"""Importación de productos desde CSV (doc 06): validar, previsualizar, confirmar y aplicar."""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Callable
from dataclasses import replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.movements import MovementService, today_local
from sisalmacen.application.ports import CsvReaderPort, WorkUnit, WorkUnitFactory
from sisalmacen.application.settings import int_setting
from sisalmacen.domain.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDenied,
    ValidationError,
)
from sisalmacen.domain.importing import (
    ACTION_ERROR,
    ACTION_INSERT,
    ACTION_NO_CHANGE,
    ACTION_UPDATE,
    CLEAR_TOKEN,
    COLUMNS,
    MODES,
    REQUIRED_FOR_INSERT,
    ImportDetail,
    ImportLookups,
    ImportOptions,
    ImportPreview,
    ImportRecord,
    ImportResult,
    PendingCatalog,
    RowError,
    RowResult,
)
from sisalmacen.domain.inventory import (
    MONEY_PLACES,
    QUANTITY_PLACES,
    ZERO,
    MovementLine,
    MovementRequest,
    ProductData,
    decimal_places,
    is_whole,
)

ProgressCallback = Callable[[int, int], None]

_MAX_STOCK = Decimal("999999999")
_QUANTITY_COLUMNS = ("stock_minimo", "stock")
_MONEY_COLUMNS = ("precio_compra", "precio_venta")
_CATALOG_COLUMNS = (
    ("categoria", "categoria_id", "categorias", True),
    ("marca", "marca_id", "marcas", False),
    ("proveedor", "proveedor_id", "proveedores", False),
    ("ubicacion", "ubicacion_id", "ubicaciones", False),
)


def normalize_header(value: str) -> str:
    """Minúsculas, sin acentos, sin espacios laterales y con guion bajo."""

    text = unicodedata.normalize("NFD", value.strip().lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[\s\-]+", "_", text)


def parse_decimal(text: str, separator: str) -> Decimal:
    cleaned = text.strip()
    if separator == ",":
        cleaned = cleaned.replace(",", ".")
    value = Decimal(cleaned)
    if not value.is_finite():
        raise InvalidOperation
    return value


# ---------- clasificación de filas (sin BD) ----------


def classify_rows(
    rows: list[tuple[int, dict[str, str]]],
    options: ImportOptions,
    lookups: ImportLookups,
) -> list[RowResult]:
    seen_codes: set[str] = set()
    seen_barcodes: dict[str, str] = {}
    return [
        classify_row(number, raw, options, lookups, seen_codes, seen_barcodes)
        for number, raw in rows
    ]


def classify_row(  # noqa: C901, PLR0912, PLR0915
    number: int,
    raw: dict[str, str],
    options: ImportOptions,
    lookups: ImportLookups,
    seen_codes: set[str],
    seen_barcodes: dict[str, str],
) -> RowResult:
    code = raw.get("codigo", "").strip()
    result = RowResult(nro_fila=number, codigo=code, accion=ACTION_ERROR, raw=raw)
    errors = result.errors

    def fail(error_code: str, column: str, message: str) -> None:
        errors.append(RowError(error_code, column, message, raw.get(column, "")))

    if not code and options.mode == "ACTUALIZAR":
        fail("E01", "codigo", "El código está vacío.")
        return result
    key = code.lower()
    if key and key in seen_codes:
        fail("E02", "codigo", "El código está duplicado dentro del archivo.")
        return result
    if key:
        seen_codes.add(key)
    if code and len(code) > 50:
        fail("E10", "codigo", "El código excede 50 caracteres.")

    existing = lookups.productos.get(key) if key else None
    result.existing_id = existing.id if existing else None
    if existing and options.mode == "INSERTAR":
        fail("E20", "codigo", "El producto ya existe y el modo es INSERTAR.")
    if not existing and options.mode == "ACTUALIZAR":
        fail("E21", "codigo", "El producto no existe y el modo es ACTUALIZAR.")
    is_insert = existing is None
    values: dict[str, Any] = {}

    def cell(column: str) -> str:
        return raw.get(column, "").strip()

    # texto libre
    for column, limit, required in (
        ("nombre", 200, True),
        ("descripcion", None, False),
        ("observaciones", None, False),
    ):
        text = cell(column)
        if not text:
            if required and is_insert:
                fail("E03", column, f"El campo {column} es obligatorio en el alta.")
            continue
        if text == CLEAR_TOKEN:
            if required:
                fail("E03", column, f"El campo {column} no puede borrarse.")
            elif not is_insert:
                values[column] = None
            continue
        if limit is not None and len(text) > limit:
            fail("E10", column, f"El campo {column} excede {limit} caracteres.")
            continue
        values[column] = text

    # catálogos
    for column, id_column, table_name, required in _CATALOG_COLUMNS:
        text = cell(column)
        if not text:
            if required and is_insert:
                fail("E03", column, f"El campo {column} es obligatorio en el alta.")
            continue
        if text == CLEAR_TOKEN:
            if required:
                fail("E03", column, f"El campo {column} no puede borrarse.")
            elif not is_insert:
                values[id_column] = None
            continue
        table = getattr(lookups, table_name)
        found = table.get(text.lower())
        if found is not None:
            values[id_column] = found
        elif options.create_missing_catalogs:
            values[id_column] = PendingCatalog(column, text)
        else:
            fail("E04", column, f"No existe {column} '{text}' en el catálogo.")

    unit_text = cell("unidad")
    if not unit_text:
        if is_insert:
            fail("E03", "unidad", "El campo unidad es obligatorio en el alta.")
    elif unit_text == CLEAR_TOKEN:
        fail("E03", "unidad", "El campo unidad no puede borrarse.")
    else:
        unit = lookups.unidades.get(unit_text.lower())
        if unit is None:
            fail("E04", "unidad", f"No existe la unidad '{unit_text}'.")
        else:
            values["unidad_id"] = unit.id
    unit_id = values.get("unidad_id", existing.unidad_id if existing else None)
    unit_info = lookups.unidades_por_id.get(unit_id) if unit_id is not None else None

    # números
    numbers: dict[str, Decimal | None] = {}
    for column in (*_MONEY_COLUMNS, *_QUANTITY_COLUMNS):
        text = cell(column)
        if not text:
            continue
        if text == CLEAR_TOKEN and column != "stock":
            if not is_insert:
                numbers[column] = None
            continue
        try:
            number = parse_decimal(text, options.decimal_separator)
        except InvalidOperation:
            fail("E05", column, f"Valor numérico inválido: '{text}'.")
            continue
        if number < ZERO:
            fail("E08", column, "No se permiten valores negativos.")
            continue
        places = MONEY_PLACES if column in _MONEY_COLUMNS else QUANTITY_PLACES
        if decimal_places(number) > places:
            fail("E05", column, f"Se permiten hasta {places} decimales.")
            continue
        if (
            column in _QUANTITY_COLUMNS
            and unit_info is not None
            and not unit_info.permite_decimales
            and not is_whole(number)
        ):
            fail("E07", column, "La unidad no admite decimales.")
            continue
        numbers[column] = number
    if numbers.get("stock") is not None and numbers["stock"] > _MAX_STOCK:  # type: ignore[operator]
        fail("E24", "stock", "El stock está fuera del rango permitido.")
    for column in ("precio_compra", "precio_venta", "stock_minimo"):
        if column in numbers:
            values[column] = numbers[column]

    # estado
    state = cell("estado").upper()
    if state in ("ACTIVO", "INACTIVO"):
        values["activo"] = state == "ACTIVO"
    elif state:
        fail("E09", "estado", "El estado debe ser ACTIVO o INACTIVO.")
    elif is_insert:
        values["activo"] = True
    effective_active = values.get("activo", existing.activo if existing else True)

    # código de barras
    barcode = cell("codigo_barras")
    if barcode == CLEAR_TOKEN:
        if not is_insert:
            values["codigo_barras"] = None
    elif barcode:
        if len(barcode) > 50:
            fail("E10", "codigo_barras", "El código de barras excede 50 caracteres.")
        else:
            values["codigo_barras"] = barcode
    final_barcode = values.get("codigo_barras", existing.codigo_barras if existing else None)
    barcode_changes = "codigo_barras" in values or (
        existing is not None and not existing.activo and effective_active
    )
    if final_barcode and effective_active and barcode_changes:
        row_identity = key or f"fila-{number}"
        owner = lookups.barcodes.get(final_barcode)
        if (owner is not None and owner.lower() != row_identity) or (
            final_barcode in seen_barcodes and seen_barcodes[final_barcode].lower() != row_identity
        ):
            fail("E11", "codigo_barras", "El código de barras ya lo usa otro producto activo.")
        else:
            seen_barcodes[final_barcode] = row_identity

    if existing and "unidad_id" in values and values["unidad_id"] != existing.unidad_id:
        if existing.has_movements:
            fail("E22", "unidad", "No se puede cambiar la unidad de un producto con movimientos.")

    stock = numbers.get("stock")
    if options.apply_stock and stock is not None and not effective_active:
        fail("E23", "stock", "El producto está inactivo y no admite aplicar stock.")

    if errors:
        return result

    result.stock = stock if options.apply_stock else None
    if is_insert:
        result.accion = ACTION_INSERT
        result.values = values
        return result

    assert existing is not None  # noqa: S101
    changes = {k: v for k, v in values.items() if _differs(existing, k, v)}
    stock_changes = result.stock is not None and result.stock != existing.cantidad
    if changes or stock_changes:
        result.accion = ACTION_UPDATE
        result.values = changes
    else:
        result.accion = ACTION_NO_CHANGE
        result.stock = None
    return result


def _differs(existing: Any, column: str, value: Any) -> bool:
    if isinstance(value, PendingCatalog):
        return True
    return bool(getattr(existing, column) != value)


# ---------- servicio ----------


class ImportService:
    """Orquesta las dos fases de importación (RI-01)."""

    def __init__(
        self,
        uow_factory: WorkUnitFactory,
        actor: CurrentSession,
        reader: CsvReaderPort,
        movements: MovementService,
        authorization: AuthorizationService | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._actor = actor
        self._reader = reader
        self._movements = movements
        self._authz = authorization or AuthorizationService()
        self._audit = AuditRecorder(actor)

    def _require_permissions(self, options: ImportOptions) -> None:
        self._authz.require_permission(self._actor, "importacion.ejecutar")
        if options.apply_stock:
            self._authz.require_permission(self._actor, "movimientos.ajuste")
        if options.create_missing_catalogs:
            self._authz.require_permission(self._actor, "catalogos.gestionar")
        if options.skip_error_rows and self._actor.rol_codigo != "ADMIN":
            raise PermissionDenied(
                "Solo un administrador puede omitir filas con error.", code="SIN_PERMISO"
            )

    # ----- fase 1: validar -----

    def validate(self, path: Path, options: ImportOptions) -> ImportPreview:
        self._require_permissions(options)
        if options.mode not in MODES:
            raise ValidationError("Modo de importación no válido.", code="CSV_MODO")
        with self._uow_factory() as uow:
            max_rows = int_setting(uow.settings.get_all(), "importacion.max_filas", 50000)
        content = self._reader.read(
            path,
            encoding=options.encoding,
            delimiter=options.delimiter,
            max_rows=max_rows,
        )

        header_map = {normalize_header(h): h for h in content.headers}
        required = ("codigo",) if options.mode == "ACTUALIZAR" else REQUIRED_FOR_INSERT
        missing = [column for column in required if column not in header_map]
        if missing:
            raise ValidationError(
                f"Faltan columnas obligatorias: {', '.join(missing)}.", code="CSV_ESTRUCTURA"
            )
        warnings = [
            f"Columna ignorada: {original}"
            for normalized, original in header_map.items()
            if normalized not in COLUMNS
        ]
        rows = [
            (
                number,
                {
                    column: row.get(header_map[column], "")
                    for column in COLUMNS
                    if column in header_map
                },
            )
            for number, row in content.rows
        ]

        with self._uow_factory() as uow:
            lookups = uow.imports.load_lookups()
            results = classify_rows(rows, options, lookups)
            repeated = uow.imports.find_applied_by_hash(content.sha256)
            import_id = uow.imports.create(
                file_name=path.name,
                sha256=content.sha256,
                mode=options.mode,
                apply_stock=options.apply_stock,
                user_id=self._actor.user_id,
            )
            uow.imports.replace_details(import_id, [_detail_row(r) for r in results])
            counters = _counters(results)
            uow.imports.update_state(import_id, "VALIDADA", counters, finished=False)
            uow.commit()

        return ImportPreview(
            importacion_id=import_id,
            archivo=path.name,
            sha256=content.sha256,
            total=len(results),
            nuevas=counters["filas_nuevas"],
            actualizables=counters["filas_actualizables"],
            sin_cambios=sum(1 for r in results if r.accion == ACTION_NO_CHANGE),
            errores=counters["filas_error"],
            rows=results,
            warnings=warnings,
            repetido=repeated,
        )

    def cancel(self, import_id: int) -> None:
        self._authz.require_permission(self._actor, "importacion.ejecutar")
        with self._uow_factory() as uow:
            record = uow.imports.get(import_id)
            if record is not None and record.estado == "VALIDADA":
                uow.imports.update_state(import_id, "CANCELADA", {}, finished=True)
                uow.commit()

    # ----- fase 2: aplicar -----

    def apply(
        self,
        import_id: int,
        options: ImportOptions,
        *,
        progress: ProgressCallback | None = None,
    ) -> ImportResult:
        self._require_permissions(options)
        try:
            return self._apply(import_id, options, progress)
        except DomainError:
            raise
        except Exception:
            self._mark_failed(import_id)
            raise

    def _apply(
        self, import_id: int, options: ImportOptions, progress: ProgressCallback | None
    ) -> ImportResult:
        with self._uow_factory() as uow:
            uow.begin_immediate()
            record = uow.imports.get(import_id)
            if record is None:
                raise NotFoundError("No se encontró la importación.", code="IMPORT_NO_ENCONTRADA")
            if record.estado != "VALIDADA":
                raise ConflictError(
                    "La importación ya fue procesada o cancelada.", code="IMPORT_ESTADO"
                )
            effective = replace(options, mode=record.modo, apply_stock=record.aplicar_stock)
            rows = [(d.nro_fila, d.datos) for d in uow.imports.details(import_id)]
            lookups = uow.imports.load_lookups()
            results = classify_rows(rows, effective, lookups)

            current = _counters(results)
            if (
                current["filas_nuevas"] != record.filas_nuevas
                or current["filas_actualizables"] != record.filas_actualizables
                or current["filas_error"] != record.filas_error
            ):
                uow.imports.replace_details(import_id, [_detail_row(r) for r in results])
                uow.imports.update_state(import_id, "VALIDADA", current, finished=False)
                uow.commit()
                raise ConflictError(
                    "Los datos cambiaron desde la vista previa. Revise la nueva vista previa.",
                    code="IMPORT_DESACTUALIZADA",
                )

            error_rows = [r for r in results if r.accion == ACTION_ERROR]
            if error_rows and not options.skip_error_rows:
                raise ValidationError(
                    f"El archivo tiene {len(error_rows)} filas con error. "
                    "Revise o exporte el informe.",
                    code="CSV_CON_ERRORES",
                )

            outcome = self._write_rows(uow, import_id, results, progress)
            counters = {
                "filas_nuevas": current["filas_nuevas"],
                "filas_actualizables": current["filas_actualizables"],
                "filas_error": current["filas_error"],
                "insertados": outcome.insertados,
                "actualizados": outcome.actualizados,
                "rechazados": outcome.rechazados,
            }
            uow.imports.update_state(import_id, "APLICADA", counters, finished=True)
            self._audit.record(
                uow,
                "IMPORTAR",
                "importacion",
                import_id,
                new={
                    "archivo": record.nombre_archivo,
                    "modo": record.modo,
                    "insertados": outcome.insertados,
                    "actualizados": outcome.actualizados,
                    "rechazados": outcome.rechazados,
                },
            )
            uow.commit()
            return outcome

    def _write_rows(
        self,
        uow: WorkUnit,
        import_id: int,
        results: list[RowResult],
        progress: ProgressCallback | None,
    ) -> ImportResult:
        created: dict[tuple[str, str], int] = {}
        initial: list[MovementLine] = []
        positive: list[MovementLine] = []
        negative: list[MovementLine] = []
        inserted = updated = unchanged = rejected = 0
        total = len(results)

        def resolve(value: Any) -> Any:
            if isinstance(value, PendingCatalog):
                return self._ensure_catalog(uow, value, created, import_id)
            return value

        for index, row in enumerate(results, start=1):
            if row.accion == ACTION_ERROR:
                rejected += 1
            elif row.accion == ACTION_INSERT:
                data = _product_data(row, resolve)
                product_id = uow.products.add(data, self._actor.user_id)
                self._audit.record(
                    uow,
                    "CREAR",
                    "producto",
                    product_id,
                    new=data,
                    detail=f"Importación #{import_id}",
                )
                if row.stock is not None and row.stock > ZERO:
                    initial.append(MovementLine(product_id, row.stock))
                inserted += 1
            elif row.accion == ACTION_UPDATE and row.existing_id is not None:
                changes = {k: resolve(v) for k, v in row.values.items()}
                if changes:
                    uow.products.apply_changes(row.existing_id, changes, self._actor.user_id)
                    self._audit.record(
                        uow,
                        "EDITAR",
                        "producto",
                        row.existing_id,
                        new=changes,
                        detail=f"Importación #{import_id}",
                    )
                if row.stock is not None:
                    difference = row.stock - uow.movements.get_stock(row.existing_id)
                    if difference > ZERO:
                        positive.append(MovementLine(row.existing_id, difference))
                    elif difference < ZERO:
                        negative.append(MovementLine(row.existing_id, -difference))
                updated += 1
            else:
                unchanged += 1
            if progress is not None and (index % 200 == 0 or index == total):
                progress(index, total)

        movements = 0
        for type_code, lines in (
            ("ENT_INICIAL", initial),
            ("AJ_POSITIVO", positive),
            ("AJ_NEGATIVO", negative),
        ):
            if not lines:
                continue
            self._movements.register_in(
                uow,
                MovementRequest(
                    tipo_codigo=type_code,
                    fecha=today_local(),
                    lines=tuple(lines),
                    motivo=f"Importación CSV #{import_id}",
                    importacion_id=import_id,
                ),
                check_permission=False,
            )
            movements += 1
        return ImportResult(
            importacion_id=import_id,
            insertados=inserted,
            actualizados=updated,
            sin_cambios=unchanged,
            rechazados=rejected,
            movimientos=movements,
        )

    def _ensure_catalog(
        self,
        uow: WorkUnit,
        pending: PendingCatalog,
        created: dict[tuple[str, str], int],
        import_id: int,
    ) -> int:
        cache_key = (pending.kind, pending.name.lower())
        if cache_key in created:
            return created[cache_key]
        field = "codigo" if pending.kind == "ubicacion" else "nombre"
        existing = uow.catalogs.find(pending.kind, field, pending.name)
        if existing is not None:
            created[cache_key] = int(existing["id"])
            return created[cache_key]
        data: dict[str, Any] = {"nombre": pending.name}
        if pending.kind == "ubicacion":
            data = {"codigo": pending.name, "nombre": pending.name, "padre_id": None}
        entry_id = uow.catalogs.add(pending.kind, data)
        self._audit.record(
            uow,
            "CREAR",
            pending.kind,
            entry_id,
            new=data,
            detail=f"Importación #{import_id}",
        )
        created[cache_key] = entry_id
        return entry_id

    def _mark_failed(self, import_id: int) -> None:
        try:
            with self._uow_factory() as uow:
                uow.imports.update_state(import_id, "FALLIDA", {}, finished=True)
                uow.commit()
        except Exception:  # noqa: S110
            pass

    # ----- consultas -----

    def history(self) -> list[ImportRecord]:
        self._authz.require_permission(self._actor, "importacion.historial")
        with self._uow_factory() as uow:
            return uow.imports.list_imports()

    def details(self, import_id: int, *, only_errors: bool = False) -> list[ImportDetail]:
        self._authz.require_permission(self._actor, "importacion.historial")
        with self._uow_factory() as uow:
            return uow.imports.details(import_id, only_errors=only_errors)

    def error_report(self, import_id: int) -> list[list[str]]:
        """Filas del informe de errores (doc 06 §5), con encabezado."""

        report: list[list[str]] = [
            ["fila", "codigo", "columna", "error_codigo", "mensaje", "valor_original"]
        ]
        for detail in self.details(import_id, only_errors=True):
            for error in detail.errores:
                report.append(
                    [
                        str(detail.nro_fila),
                        detail.codigo or "",
                        error.get("column", ""),
                        error.get("code", ""),
                        error.get("message", ""),
                        error.get("original", ""),
                    ]
                )
        return report


def _counters(results: list[RowResult]) -> dict[str, int]:
    return {
        "total_filas": len(results),
        "filas_nuevas": sum(1 for r in results if r.accion == ACTION_INSERT),
        "filas_actualizables": sum(1 for r in results if r.accion == ACTION_UPDATE),
        "filas_error": sum(1 for r in results if r.accion == ACTION_ERROR),
    }


def _detail_row(result: RowResult) -> dict[str, Any]:
    return {
        "nro_fila": result.nro_fila,
        "codigo": result.codigo or None,
        "accion": result.accion,
        "datos_json": json.dumps(result.raw, ensure_ascii=False),
        "errores_json": json.dumps(
            [
                {"code": e.code, "column": e.column, "message": e.message, "original": e.original}
                for e in result.errors
            ],
            ensure_ascii=False,
        )
        if result.errors
        else None,
    }


def _product_data(row: RowResult, resolve: Callable[[Any], Any]) -> ProductData:
    values = {key: resolve(value) for key, value in row.values.items()}
    return ProductData(
        codigo=row.codigo,
        nombre=values["nombre"],
        categoria_id=values["categoria_id"],
        unidad_id=values["unidad_id"],
        codigo_barras=values.get("codigo_barras"),
        descripcion=values.get("descripcion"),
        marca_id=values.get("marca_id"),
        proveedor_id=values.get("proveedor_id"),
        ubicacion_id=values.get("ubicacion_id"),
        precio_compra=values.get("precio_compra"),
        precio_venta=values.get("precio_venta"),
        stock_minimo=values.get("stock_minimo"),
        observaciones=values.get("observaciones"),
        activo=values.get("activo", True),
    )
