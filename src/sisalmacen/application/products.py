"""Casos de uso de productos (HU-03.1 a HU-03.4)."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from uuid import uuid4

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.ports import WorkUnit, WorkUnitFactory
from sisalmacen.application.settings import flag
from sisalmacen.domain.errors import (
    BusinessRuleViolation,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from sisalmacen.domain.inventory import (
    MONEY_PLACES,
    QUANTITY_PLACES,
    ZERO,
    Page,
    ProductData,
    ProductFilter,
    ProductRecord,
    decimal_places,
    is_whole,
)


class ProductService:
    """Alta, edición, baja lógica y consulta de productos."""

    def __init__(
        self,
        uow_factory: WorkUnitFactory,
        actor: CurrentSession,
        authorization: AuthorizationService | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._actor = actor
        self._authz = authorization or AuthorizationService()
        self._audit = AuditRecorder(actor)

    # ----- consultas -----

    def search(
        self, product_filter: ProductFilter, *, page: int = 1, page_size: int = 50
    ) -> Page[ProductRecord]:
        self._authz.require_permission(self._actor, "productos.ver")
        with self._uow_factory() as uow:
            result = uow.products.search(product_filter, page=page, page_size=page_size)
        if self._hide_prices(settings):
            return Page(
                items=[_mask_prices(item) for item in result.items],
                total=result.total,
                page=result.page,
                page_size=result.page_size,
            )
        return result

    def get(self, product_id: int) -> ProductRecord:
        self._authz.require_permission(self._actor, "productos.ver")
        with self._uow_factory() as uow:
            record = uow.products.get(product_id)
            settings = uow.settings.get_all()
        if record is None:
            raise NotFoundError("No se encontró el producto.", code="PRODUCTO_NO_ENCONTRADO")
        return _mask_prices(record) if self._hide_prices(settings) else record

    # ----- escritura -----

    def create(self, data: ProductData) -> int:
        self._authz.require_permission(self._actor, "productos.crear")
        with self._uow_factory() as uow:
            clean = self._validate(uow, data, current=None)
            if not clean.codigo:
                clean = replace(clean, codigo=self._new_legacy_code())
            if uow.products.get_by_code(clean.codigo) is not None:
                raise ConflictError(
                    f"Ya existe un producto con el código {clean.codigo}.",
                    code="PRODUCTO_CODIGO_DUPLICADO",
                )
            self._ensure_barcode_free(uow, clean.codigo_barras, exclude_id=None)
            product_id = uow.products.add(clean, self._actor.user_id)
            self._audit.record(uow, "CREAR", "producto", product_id, new=clean)
            uow.commit()
        return product_id

    def update(self, product_id: int, data: ProductData) -> None:
        self._authz.require_permission(self._actor, "productos.editar")
        with self._uow_factory() as uow:
            current = uow.products.get(product_id)
            if current is None:
                raise NotFoundError("No se encontró el producto.", code="PRODUCTO_NO_ENCONTRADO")
            clean = self._validate(uow, replace(data, activo=current.activo), current=current)
            if self._hide_prices(uow.settings.get_all()):
                clean = replace(
                    clean,
                    precio_compra=current.precio_compra,
                    precio_venta=current.precio_venta,
                )
            duplicate = uow.products.get_by_code(clean.codigo)
            if duplicate is not None and duplicate.id != product_id:
                raise ConflictError(
                    f"Ya existe un producto con el código {clean.codigo}.",
                    code="PRODUCTO_CODIGO_DUPLICADO",
                )
            if current.unidad_id != clean.unidad_id and uow.products.has_movements(product_id):
                raise BusinessRuleViolation(
                    "No puede cambiar la unidad de un producto con movimientos.",
                    code="UNIDAD_CON_MOVIMIENTOS",
                )
            if current.activo:
                self._ensure_barcode_free(uow, clean.codigo_barras, exclude_id=product_id)
            uow.products.update(product_id, clean, self._actor.user_id)
            self._audit.record(
                uow,
                "EDITAR",
                "producto",
                product_id,
                previous=current.as_data(),
                new=clean,
                detail=f"row_version {current.row_version} -> {current.row_version + 1}",
            )
            uow.commit()

    def deactivate(self, product_id: int) -> None:
        self._authz.require_permission(self._actor, "productos.desactivar")
        self._set_active(product_id, active=False)

    def reactivate(self, product_id: int) -> None:
        self._authz.require_permission(self._actor, "productos.desactivar")
        self._set_active(product_id, active=True)

    def _set_active(self, product_id: int, *, active: bool) -> None:
        with self._uow_factory() as uow:
            current = uow.products.get(product_id)
            if current is None:
                raise NotFoundError("No se encontró el producto.", code="PRODUCTO_NO_ENCONTRADO")
            if current.activo == active:
                return
            if active:
                self._ensure_barcode_free(uow, current.codigo_barras, exclude_id=product_id)
            uow.products.set_active(product_id, active=active, user_id=self._actor.user_id)
            self._audit.record(
                uow,
                "REACTIVAR" if active else "DESACTIVAR",
                "producto",
                product_id,
                previous={"activo": current.activo},
                new={"activo": active},
            )
            uow.commit()

    # ----- exportación CSV -----

    def export_csv(self, product_filter: ProductFilter, *, page: int = 1) -> str:
        """Exporta productos a CSV con filtros aplicados."""

        from sisalmacen.application.csv_export import export_to_csv, PRODUCTOS_CSV_HEADERS

        self._authz.require_permission(self._actor, "productos.ver")
        with self._uow_factory() as uow:
            result = uow.products.search(product_filter, page=page, page_size=0)

        rows = []
        for item in result.items:
            # Calcular totales desde movimientos
            entradas_total = 0  # Esto se calcularía desde movimientos
            salidas_total = 0
            stock_inicial = item.cantidad - entradas_total + salidas_total

            rows.append({
                "codigo_producto": item.codigo,
                "descripcion": item.nombre,
                "descripcion_adicional": "",
                "marca": item.marca or "",
                "categoria": item.categoria,
                "precio_compra": item.precio_compra,
                "precio_venta": item.precio_venta,
                "stock_minimo": item.stock_minimo,
                "stock_inicial": stock_inicial,
                "entradas": entradas_total,
                "salidas": salidas_total,
                "stock_actual": item.cantidad,
                "almacen": "",
                "ubicacion": item.ubicacion or "",
                "proveedor": item.proveedor or "",
                "fecha_registro": item.creado_en[:10],
                "estado": "ACTIVO" if item.activo else "INACTIVO",
                "observacion": item.observaciones or "",
            })

        return export_to_csv(PRODUCTOS_CSV_HEADERS, rows)

    def get_csv_template(self) -> str:
        """Descarga plantilla CSV vacía para importación de productos."""

        from sisalmacen.application.csv_export import export_to_csv, PRODUCTOS_CSV_HEADERS

        self._authz.require_permission(self._actor, "productos.crear")
        
        template_row = {header: "" for header in PRODUCTOS_CSV_HEADERS}
        return export_to_csv(PRODUCTOS_CSV_HEADERS, [template_row])

    def import_csv(self, csv_content: str) -> dict[str, int]:
        """Importa productos desde contenido CSV.
        
        Args:
            csv_content: Contenido del archivo CSV como string
            
        Returns:
            dict con 'created' y 'errors' counts
        """
        from csv import DictReader
        from io import StringIO
        from sisalmacen.application.csv_export import PRODUCTOS_CSV_HEADERS
        
        self._authz.require_permission(self._actor, "productos.crear")
        
        # Parse CSV content
        content = csv_content.lstrip("\ufeff")
        reader = DictReader(StringIO(content))
        
        created = 0
        errors = 0
        
        for row in reader:
            try:
                # Validate required fields
                if not row.get("codigo_producto") or not row.get("descripcion"):
                    errors += 1
                    continue
                
                # Create product data
                product_data = ProductData(
                    codigo=row.get("codigo_producto", "").strip(),
                    nombre=row.get("descripcion", "").strip(),
                    stock_minimo=int(row.get("stock_minimo", 0)) if row.get("stock_minimo") else 0,
                )
                
                # Create product
                self.create(product_data)
                created += 1
            except Exception:
                errors += 1
                continue
        
        return {"created": created, "errors": errors}

    # ----- validaciones -----

    def _hide_prices(self, settings: dict[str, str]) -> bool:
        return "productos.ver_precios" not in self._actor.permisos or not flag(
            settings, "inventario.usar_precios", default=True
        )

    @staticmethod
    def _ensure_barcode_free(uow: WorkUnit, barcode: str | None, *, exclude_id: int | None) -> None:
        if not barcode:
            return
        other = uow.products.find_active_by_barcode(barcode, exclude_id=exclude_id)
        if other is not None:
            raise ConflictError(
                f"El código de barras ya está en uso por {other.codigo}.",
                code="PRODUCTO_BARRAS_DUPLICADO",
            )

    @staticmethod
    def _new_legacy_code() -> str:
        """Crea el identificador interno para altas o migraciones sin código externo."""

        return f"LEGACY-{uuid4().hex[:12].upper()}"

    def _validate(
        self, uow: WorkUnit, data: ProductData, *, current: ProductRecord | None
    ) -> ProductData:
        codigo = data.codigo.strip()
        nombre = data.nombre.strip()
        if not codigo and current is not None:
            codigo = current.codigo
        if codigo and len(codigo) > 50:
            raise ValidationError("El código excede 50 caracteres.", code="PRODUCTO_CODIGO_LARGO")
        if not nombre:
            raise ValidationError("Debe indicar el nombre.", code="PRODUCTO_NOMBRE_REQUERIDO")
        if len(nombre) > 200:
            raise ValidationError("El nombre excede 200 caracteres.", code="PRODUCTO_NOMBRE_LARGO")

        barcode = (data.codigo_barras or "").strip() or None
        if barcode is not None and len(barcode) > 50:
            raise ValidationError(
                "El código de barras excede 50 caracteres.", code="PRODUCTO_BARRAS_LARGO"
            )

        _require_ref(
            uow, "categoria", data.categoria_id, "categoría", current and current.categoria_id
        )
        unit = _require_ref(
            uow, "unidad_medida", data.unidad_id, "unidad", current and current.unidad_id
        )
        for kind, value, label, previous in (
            ("marca", data.marca_id, "marca", current and current.marca_id),
            ("proveedor", data.proveedor_id, "proveedor", current and current.proveedor_id),
            ("ubicacion", data.ubicacion_id, "ubicación", current and current.ubicacion_id),
        ):
            if value is not None:
                _require_ref(uow, kind, value, label, previous)

        allow_decimals = bool(unit.get("permite_decimales"))
        for label, price in (
            ("precio de compra", data.precio_compra),
            ("precio de venta", data.precio_venta),
        ):
            _check_non_negative(price, label, MONEY_PLACES)
        for label, qty in (
            ("stock mínimo", data.stock_minimo),
        ):
            _check_non_negative(qty, label, QUANTITY_PLACES)
            if qty is not None and not allow_decimals and not is_whole(qty):
                raise ValidationError(
                    f"El {label} debe ser entero para la unidad {unit.get('codigo')}.",
                    code="CANTIDAD_INVALIDA",
                )

        return replace(
            data,
            codigo=codigo,
            nombre=nombre,
            codigo_barras=barcode,
            descripcion=(data.descripcion or "").strip() or None,
            observaciones=(data.observaciones or "").strip() or None,
        )


def _mask_prices(record: ProductRecord) -> ProductRecord:
    return replace(record, precio_compra=None, precio_venta=None)


def _check_non_negative(value: Decimal | None, label: str, places: int) -> None:
    if value is None:
        return
    if value < ZERO:
        raise ValidationError(f"El {label} no puede ser negativo.", code="VALOR_NEGATIVO")
    if decimal_places(value) > places:
        raise ValidationError(
            f"El {label} admite hasta {places} decimales.", code="CANTIDAD_INVALIDA"
        )


def _require_ref(
    uow: WorkUnit, kind: str, entry_id: int, label: str, previous_id: int | None
) -> dict[str, object]:
    entry = uow.catalogs.get(kind, entry_id)
    if entry is None:
        raise ValidationError(f"La {label} seleccionada no existe.", code="CATALOGO_NO_ENCONTRADO")
    if not entry.get("activo") and entry_id != previous_id:
        raise ValidationError(f"La {label} seleccionada está inactiva.", code="CATALOGO_INACTIVO")
    return entry
