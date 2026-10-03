"""Reportes y exportaciones (HU-07.x)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.movements import today_local
from sisalmacen.application.ports import ReportWriterPort, WorkUnit, WorkUnitFactory
from sisalmacen.application.settings import flag
from sisalmacen.domain.errors import PermissionDenied, ValidationError
from sisalmacen.domain.inventory import (
    ALERT_AGOTADO,
    ALERT_BAJO_MINIMO,
    ALERT_LABELS,
    ZERO,
    MovementFilter,
    ProductFilter,
    ProductRecord,
    ReportData,
)

REPORTS: tuple[tuple[str, str], ...] = (
    ("inventario_general", "Inventario general"),
    ("stock_bajo", "Stock bajo"),
    ("sin_stock", "Productos sin stock"),
    ("por_categoria", "Inventario por categoría"),
    ("movimientos_periodo", "Movimientos por período"),
    ("historial_producto", "Historial de producto"),
    ("valorizado", "Inventario valorizado"),
)


@dataclass
class ReportParams:
    categoria_id: int | None = None
    producto_id: int | None = None
    tipo_codigo: str | None = None
    fecha_desde: date | None = None
    fecha_hasta: date | None = None
    incluir_inactivos: bool = False


class ReportService:
    """Genera tablas de reporte a partir de los datos vigentes y las exporta."""

    def __init__(
        self,
        uow_factory: WorkUnitFactory,
        actor: CurrentSession,
        writers: Mapping[str, ReportWriterPort],
        authorization: AuthorizationService | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._actor = actor
        self._writers = dict(writers)
        self._authz = authorization or AuthorizationService()
        self._audit = AuditRecorder(actor)

    @property
    def formats(self) -> tuple[str, ...]:
        return tuple(self._writers)

    def build(self, key: str, params: ReportParams) -> ReportData:
        self._authz.require_permission(self._actor, "reportes.ver")
        builders = {
            "inventario_general": self._inventory_general,
            "stock_bajo": self._low_stock,
            "sin_stock": self._out_of_stock,
            "por_categoria": self._by_category,
            "movimientos_periodo": self._movements_period,
            "historial_producto": self._product_history,
            "valorizado": self._valued,
        }
        builder = builders.get(key)
        if builder is None:
            raise ValidationError("Reporte desconocido.", code="REPORTE_DESCONOCIDO")
        with self._uow_factory() as uow:
            return builder(uow, params)

    def products_listing(self, product_filter: ProductFilter) -> ReportData:
        """Listado de productos (completo o filtrado) para exportar (RF-090/091)."""

        self._authz.require_permission(self._actor, "exportar.datos")
        with self._uow_factory() as uow:
            return self._product_table(
                uow, "listado_productos", "Listado de productos", product_filter
            )

    def company_info(self) -> dict[str, str]:
        with self._uow_factory() as uow:
            settings = uow.settings.get_all()
        return {k: v for k, v in settings.items() if k.startswith("empresa.")}

    def export(self, data: ReportData, fmt: str, path: Path) -> None:
        self._authz.require_permission(self._actor, "exportar.datos")
        writer = self._writers.get(fmt)
        if writer is None:
            raise ValidationError("Formato de exportación no soportado.", code="EXPORT_FORMATO")
        company = self.company_info()
        writer.write(path, data, company=company)
        with self._uow_factory() as uow:
            self._audit.record(
                uow,
                "EXPORTAR",
                "reporte",
                data.key,
                new={"formato": fmt, "filtros": data.filters, "filas": len(data.rows)},
                detail=path.name,
            )
            uow.commit()

    # ----- reportes -----

    def _show_prices(self, uow: WorkUnit) -> bool:
        return "productos.ver_precios" in self._actor.permisos and flag(
            uow.settings.get_all(), "inventario.usar_precios", default=True
        )

    def _product_table(
        self, uow: WorkUnit, key: str, title: str, product_filter: ProductFilter
    ) -> ReportData:
        items = uow.products.search(product_filter, page=1, page_size=0).items
        prices = self._show_prices(uow)
        headers = ["Código", "Descripción", "Categoría", "Unidad", "Stock", "Mínimo"]
        types = ["text", "text", "text", "text", "qty", "qty"]
        if prices:
            headers += ["P. compra", "P. venta"]
            types += ["money", "money"]
        headers += ["Estado", "Alerta"]
        types += ["text", "text"]
        rows: list[list[object]] = []
        for item in items:
            row: list[object] = [
                item.codigo,
                item.nombre,
                item.categoria,
                item.unidad,
                item.cantidad,
                item.stock_minimo,
            ]
            if prices:
                row += [item.precio_compra, item.precio_venta]
            alert = item.alert()
            row += ["Activo" if item.activo else "Inactivo", ALERT_LABELS.get(alert or "", "")]
            rows.append(row)
        return ReportData(
            key=key,
            title=title,
            headers=headers,
            column_types=types,
            rows=rows,
            filters=product_filter.describe(),
        )

    def _inventory_general(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        product_filter = ProductFilter(
            categoria_id=params.categoria_id,
            estado=None if params.incluir_inactivos else "ACTIVO",
        )
        return self._product_table(uow, "inventario_general", "Inventario general", product_filter)

    def _low_stock(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        product_filter = ProductFilter(
            categoria_id=params.categoria_id, estado="ACTIVO", alerta=ALERT_BAJO_MINIMO
        )
        return self._product_table(uow, "stock_bajo", "Stock bajo", product_filter)

    def _out_of_stock(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        product_filter = ProductFilter(
            categoria_id=params.categoria_id, estado="ACTIVO", alerta=ALERT_AGOTADO
        )
        return self._product_table(uow, "sin_stock", "Productos sin stock", product_filter)

    def _by_category(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        prices = self._show_prices(uow)
        items = uow.products.search(ProductFilter(estado="ACTIVO"), page=1, page_size=0).items
        groups: dict[str, list[ProductRecord]] = {}
        for item in items:
            groups.setdefault(item.categoria, []).append(item)
        headers = ["Categoría", "Productos", "Con stock"]
        types = ["text", "int", "int"]
        if prices:
            headers.append("Valor de inventario")
            types.append("money")
        rows: list[list[object]] = []
        for name in sorted(groups, key=str.lower):
            members = groups[name]
            row: list[object] = [
                name,
                len(members),
                sum(1 for m in members if m.cantidad > ZERO),
            ]
            if prices:
                row.append(_value(members))
            rows.append(row)
        return ReportData(
            key="por_categoria",
            title="Inventario por categoría",
            headers=headers,
            column_types=types,
            rows=rows,
            filters=["Estado: ACTIVO"],
        )

    def _valued(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        if not self._show_prices(uow):
            raise PermissionDenied(
                "No tiene permiso para ver precios o la valorización está desactivada.",
                code="SIN_PERMISO",
            )
        items = uow.products.search(
            ProductFilter(categoria_id=params.categoria_id, estado="ACTIVO"), page=1, page_size=0
        ).items
        rows: list[list[object]] = []
        total = ZERO
        for item in items:
            if item.precio_compra is None:
                continue
            value = item.cantidad * item.precio_compra
            total += value
            rows.append(
                [item.codigo, item.nombre, item.unidad, item.cantidad, item.precio_compra, value]
            )
        return ReportData(
            key="valorizado",
            title="Inventario valorizado",
            headers=["Código", "Nombre", "Unidad", "Stock", "P. compra", "Valor"],
            column_types=["text", "text", "text", "qty", "money", "money"],
            rows=rows,
            filters=["Estado: ACTIVO", "Solo productos con precio de compra"],
            totals=["TOTAL", "", "", None, None, total],
        )

    def _movement_table(
        self,
        uow: WorkUnit,
        key: str,
        title: str,
        movement_filter: MovementFilter,
        filters: list[str],
    ) -> ReportData:
        rows_src = uow.movements.search(movement_filter, page=1, page_size=0).items
        rows: list[list[object]] = [
            [
                row.fecha_movimiento,
                row.tipo_nombre,
                row.producto_codigo,
                row.producto_nombre,
                row.signo * row.cantidad,
                row.stock_anterior,
                row.stock_resultante,
                row.usuario,
                row.documento_referencia or row.motivo or "",
            ]
            for row in rows_src
        ]
        return ReportData(
            key=key,
            title=title,
            headers=[
                "Fecha",
                "Tipo",
                "Código",
                "Producto",
                "Cantidad",
                "Stock anterior",
                "Stock resultante",
                "Usuario",
                "Motivo / documento",
            ],
            column_types=["date", "text", "text", "text", "qty", "qty", "qty", "text", "text"],
            rows=rows,
            filters=filters,
        )

    def _movements_period(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        today = today_local()
        since = params.fecha_desde or today.replace(day=1)
        until = params.fecha_hasta or today
        if since > until:
            raise ValidationError(
                "La fecha inicial es posterior a la final.", code="FECHAS_INVALIDAS"
            )
        return self._movement_table(
            uow,
            "movimientos_periodo",
            "Movimientos por período",
            MovementFilter(tipo_codigo=params.tipo_codigo, fecha_desde=since, fecha_hasta=until),
            [f"Desde: {since.isoformat()}", f"Hasta: {until.isoformat()}"]
            + ([f"Tipo: {params.tipo_codigo}"] if params.tipo_codigo else []),
        )

    def _product_history(self, uow: WorkUnit, params: ReportParams) -> ReportData:
        if params.producto_id is None:
            raise ValidationError("Seleccione un producto.", code="PRODUCTO_REQUERIDO")
        product = uow.products.get(params.producto_id)
        label = f"{product.codigo} - {product.nombre}" if product else str(params.producto_id)
        return self._movement_table(
            uow,
            "historial_producto",
            "Historial de producto",
            MovementFilter(
                producto_id=params.producto_id,
                fecha_desde=params.fecha_desde,
                fecha_hasta=params.fecha_hasta,
            ),
            [f"Producto: {label}"],
        )


def _value(members: list[ProductRecord]) -> Decimal:
    return sum((m.cantidad * m.precio_compra for m in members if m.precio_compra is not None), ZERO)
