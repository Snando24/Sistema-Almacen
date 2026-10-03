"""Repositorios SQLAlchemy de importación, configuración y resumen."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import delete, distinct, func, insert, select, text
from sqlalchemy.orm import Session

from sisalmacen.domain.auth import DashboardSnapshot
from sisalmacen.domain.importing import (
    ExistingProduct,
    ImportDetail,
    ImportLookups,
    ImportRecord,
    UnitInfo,
)
from sisalmacen.infrastructure.db.catalog_product_repositories import (
    alert_conditions,
    money_total,
    utc_now,
)
from sisalmacen.infrastructure.db.models import (
    Categoria,
    Configuracion,
    DetalleImportacion,
    DetalleMovimiento,
    Importacion,
    Inventario,
    Marca,
    Movimiento,
    Producto,
    Proveedor,
    TipoMovimiento,
    Ubicacion,
    UnidadMedida,
    Usuario,
)

_COUNTER_FIELDS = {
    "total_filas",
    "filas_nuevas",
    "filas_actualizables",
    "filas_error",
    "insertados",
    "actualizados",
    "rechazados",
}


def _to_import_record(model: Importacion) -> ImportRecord:
    return ImportRecord(
        id=model.id,
        nombre_archivo=model.nombre_archivo,
        hash_sha256=model.hash_sha256,
        modo=model.modo,
        aplicar_stock=bool(model.aplicar_stock),
        usuario_id=model.usuario_id,
        iniciado_en=model.iniciado_en,
        finalizado_en=model.finalizado_en,
        estado=model.estado,
        total_filas=model.total_filas,
        filas_nuevas=model.filas_nuevas,
        filas_actualizables=model.filas_actualizables,
        filas_error=model.filas_error,
        insertados=model.insertados,
        actualizados=model.actualizados,
        rechazados=model.rechazados,
    )


class SqlAlchemyImportRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        file_name: str,
        sha256: str,
        mode: str,
        apply_stock: bool,
        user_id: int,
    ) -> int:
        model = Importacion(
            nombre_archivo=file_name,
            hash_sha256=sha256,
            modo=mode,
            aplicar_stock=1 if apply_stock else 0,
            usuario_id=user_id,
            iniciado_en=utc_now(),
            estado="VALIDADA",
        )
        self._session.add(model)
        self._session.flush()
        return int(model.id)

    def get(self, import_id: int) -> ImportRecord | None:
        model = self._session.get(Importacion, import_id)
        return None if model is None else _to_import_record(model)

    def list_imports(self, *, limit: int = 200) -> list[ImportRecord]:
        statement = select(Importacion).order_by(Importacion.id.desc()).limit(limit)
        return [_to_import_record(m) for m in self._session.execute(statement).scalars()]

    def find_applied_by_hash(self, sha256: str) -> ImportRecord | None:
        statement = (
            select(Importacion)
            .where(Importacion.hash_sha256 == sha256, Importacion.estado == "APLICADA")
            .order_by(Importacion.id.desc())
            .limit(1)
        )
        model = self._session.execute(statement).scalar_one_or_none()
        return None if model is None else _to_import_record(model)

    def replace_details(self, import_id: int, rows: list[dict[str, Any]]) -> None:
        self._session.execute(
            delete(DetalleImportacion).where(DetalleImportacion.importacion_id == import_id)
        )
        if rows:
            self._session.execute(
                insert(DetalleImportacion),
                [{"importacion_id": import_id, **row} for row in rows],
            )
        self._session.flush()

    def details(
        self, import_id: int, *, only_errors: bool = False, limit: int | None = None
    ) -> list[ImportDetail]:
        statement = (
            select(DetalleImportacion)
            .where(DetalleImportacion.importacion_id == import_id)
            .order_by(DetalleImportacion.nro_fila)
        )
        if only_errors:
            statement = statement.where(DetalleImportacion.accion == "ERROR")
        if limit is not None:
            statement = statement.limit(limit)
        return [
            ImportDetail(
                nro_fila=row.nro_fila,
                codigo=row.codigo,
                accion=row.accion,
                datos=json.loads(row.datos_json or "{}"),
                errores=json.loads(row.errores_json or "[]"),
            )
            for row in self._session.execute(statement).scalars()
        ]

    def update_state(
        self, import_id: int, state: str, counters: Mapping[str, int], *, finished: bool
    ) -> None:
        model = self._session.get(Importacion, import_id)
        if model is None:
            raise RuntimeError("Importación inexistente.")
        model.estado = state
        for key, value in counters.items():
            if key in _COUNTER_FIELDS:
                setattr(model, key, int(value))
        if finished:
            model.finalizado_en = utc_now()
        self._session.flush()

    def load_lookups(self) -> ImportLookups:
        session = self._session

        def names(model: Any, column: Any) -> dict[str, int]:
            statement = select(column, model.id).where(model.activo == 1)
            return {str(key).lower(): int(entry_id) for key, entry_id in session.execute(statement)}

        units: dict[str, UnitInfo] = {}
        units_by_id: dict[int, UnitInfo] = {}
        for unit in session.execute(select(UnidadMedida)).scalars():
            info = UnitInfo(id=unit.id, permite_decimales=bool(unit.permite_decimales))
            units_by_id[unit.id] = info
            if unit.activo:
                units[unit.codigo.lower()] = info
                units[unit.nombre.lower()] = info

        moved = set(session.execute(select(distinct(DetalleMovimiento.producto_id))).scalars())
        products: dict[str, ExistingProduct] = {}
        barcodes: dict[str, str] = {}
        statement = (
            select(Producto, Inventario.cantidad)
            .select_from(Producto)
            .join(Inventario, Inventario.producto_id == Producto.id)
        )
        for product, quantity in session.execute(statement):
            products[product.codigo.lower()] = ExistingProduct(
                id=product.id,
                codigo=product.codigo,
                nombre=product.nombre,
                activo=bool(product.activo),
                unidad_id=product.unidad_id,
                categoria_id=product.categoria_id,
                marca_id=product.marca_id,
                proveedor_id=product.proveedor_id,
                ubicacion_id=product.ubicacion_id,
                codigo_barras=product.codigo_barras,
                descripcion=product.descripcion,
                precio_compra=product.precio_compra,
                precio_venta=product.precio_venta,
                stock_minimo=product.stock_minimo,
                stock_maximo=product.stock_maximo,
                observaciones=product.observaciones,
                cantidad=quantity,
                has_movements=product.id in moved,
            )
            if product.activo and product.codigo_barras:
                barcodes[product.codigo_barras] = product.codigo

        return ImportLookups(
            categorias=names(Categoria, Categoria.nombre),
            marcas=names(Marca, Marca.nombre),
            proveedores=names(Proveedor, Proveedor.nombre),
            ubicaciones=names(Ubicacion, Ubicacion.codigo),
            unidades=units,
            unidades_por_id=units_by_id,
            productos=products,
            barcodes=barcodes,
        )


class SqlAlchemySettingsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_all(self) -> dict[str, str]:
        rows = self._session.execute(select(Configuracion)).scalars()
        return {row.clave: row.valor for row in rows}

    def set_many(self, values: Mapping[str, str]) -> None:
        for key, value in values.items():
            row = self._session.get(Configuracion, key)
            if row is None:
                self._session.add(
                    Configuracion(clave=key, valor=value, descripcion=None, actualizado_en=utc_now())
                )
            else:
                row.valor = value
                row.actualizado_en = utc_now()
        self._session.flush()


def build_dashboard_snapshot(session: Session) -> DashboardSnapshot:
    """Indicadores de RF-080 calculados por consulta."""

    config = {
        row.clave: row.valor
        for row in session.execute(
            select(Configuracion).where(
                Configuracion.clave.in_(
                    ("empresa.nombre", "backup.carpeta", "inventario.usar_stock_maximo")
                )
            )
        ).scalars()
    }
    use_max = config.get("inventario.usar_stock_maximo", "1") == "1"
    alerts = alert_conditions(use_max)

    def count_products(*conditions: Any) -> int:
        statement = (
            select(func.count(Producto.id))
            .join(Inventario, Inventario.producto_id == Producto.id)
            .where(*conditions)
        )
        return int(session.execute(statement).scalar_one())

    def count_total(model: Any, *conditions: Any) -> int:
        statement = select(func.count()).select_from(model)
        if conditions:
            statement = statement.where(*conditions)
        return int(session.execute(statement).scalar_one())

    today = datetime.now().astimezone().date().isoformat()

    def movements_today(nature: str) -> int:
        statement = (
            select(func.count(Movimiento.id))
            .join(TipoMovimiento, TipoMovimiento.id == Movimiento.tipo_movimiento_id)
            .where(Movimiento.fecha_movimiento == today, TipoMovimiento.naturaleza == nature)
        )
        return int(session.execute(statement).scalar_one())

    raw_value = session.execute(
        text(
            "SELECT COALESCE(SUM(i.cantidad * p.precio_compra), 0) FROM producto p "
            "JOIN inventario i ON i.producto_id = p.id "
            "WHERE p.activo = 1 AND p.precio_compra IS NOT NULL"
        )
    ).scalar_one()

    return DashboardSnapshot(
        empresa_nombre=config.get("empresa.nombre", ""),
        total_usuarios=count_total(Usuario),
        total_productos=count_total(Producto),
        productos_activos=count_total(Producto, Producto.activo == 1),
        total_categorias=count_total(Categoria),
        total_movimientos=count_total(Movimiento),
        total_tipos_movimiento=count_total(TipoMovimiento),
        backup_carpeta=config.get("backup.carpeta", ""),
        productos_sin_stock=count_products(Producto.activo == 1, alerts["SIN_STOCK"]),
        productos_bajo_minimo=count_products(Producto.activo == 1, alerts["BAJO_MINIMO"]),
        productos_sobre_maximo=count_products(Producto.activo == 1, alerts["SOBRE_MAXIMO"]),
        entradas_hoy=movements_today("ENTRADA"),
        salidas_hoy=movements_today("SALIDA"),
        valor_inventario=money_total(int(raw_value)),
    )


__all__ = [
    "SqlAlchemyImportRepository",
    "SqlAlchemySettingsRepository",
    "build_dashboard_snapshot",
]
