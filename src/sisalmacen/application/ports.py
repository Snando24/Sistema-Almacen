"""Puertos que la capa de aplicación necesita de la infraestructura."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

from sisalmacen.domain.importing import (
    CsvContent,
    ImportDetail,
    ImportLookups,
    ImportRecord,
)
from sisalmacen.domain.inventory import (
    AuditFilter,
    AuditRow,
    MovementFilter,
    MovementRow,
    MovementType,
    Page,
    ProductData,
    ProductFilter,
    ProductRecord,
    ReportData,
)


class CatalogRepository(Protocol):
    def list_entries(self, kind: str, *, include_inactive: bool = True) -> list[dict[str, Any]]: ...

    def get(self, kind: str, entry_id: int) -> dict[str, Any] | None: ...

    def find(
        self, kind: str, field: str, value: str, *, exclude_id: int | None = None
    ) -> dict[str, Any] | None: ...

    def add(self, kind: str, data: Mapping[str, Any]) -> int: ...

    def update(self, kind: str, entry_id: int, data: Mapping[str, Any]) -> None: ...

    def set_active(self, kind: str, entry_id: int, *, active: bool) -> None: ...

    def count_active_products_using(self, kind: str, entry_id: int) -> int: ...


class ProductRepository(Protocol):
    def get(self, product_id: int) -> ProductRecord | None: ...

    def get_by_code(self, code: str) -> ProductRecord | None: ...

    def find_active_by_barcode(
        self, barcode: str, *, exclude_id: int | None = None
    ) -> ProductRecord | None: ...

    def add(self, data: ProductData, user_id: int) -> int: ...

    def update(self, product_id: int, data: ProductData, user_id: int) -> None: ...

    def apply_changes(self, product_id: int, changes: Mapping[str, Any], user_id: int) -> None: ...

    def set_active(self, product_id: int, *, active: bool, user_id: int) -> None: ...

    def search(
        self, product_filter: ProductFilter, *, page: int = 1, page_size: int = 50
    ) -> Page[ProductRecord]: ...

    def has_movements(self, product_id: int) -> bool: ...


class MovementRepository(Protocol):
    def get_type(self, code: str) -> MovementType | None: ...

    def list_types(self, *, include_inactive: bool = True) -> list[MovementType]: ...

    def add_type(self, code: str, name: str, nature: str, *, requires_reason: bool) -> int: ...

    def update_type(self, type_id: int, name: str, *, requires_reason: bool) -> None: ...

    def set_type_active(self, type_id: int, *, active: bool) -> None: ...

    def get_stock(self, product_id: int) -> Decimal: ...

    def set_stock(self, product_id: int, quantity: Decimal) -> None: ...

    def add_movement(
        self,
        *,
        type_id: int,
        movement_date: date,
        user_id: int,
        reason: str | None,
        reference: str | None,
        note: str | None,
        import_id: int | None,
        origin_id: int | None,
    ) -> int: ...

    def add_detail(
        self,
        *,
        movement_id: int,
        product_id: int,
        sign: int,
        quantity: Decimal,
        previous: Decimal,
        resulting: Decimal,
        unit_price: Decimal | None,
    ) -> None: ...

    def search(
        self, movement_filter: MovementFilter, *, page: int = 1, page_size: int = 100
    ) -> Page[MovementRow]: ...

    def has_compensation(self, movement_id: int) -> bool: ...

    def consistency_violations(self) -> list[int]: ...


class AuditRepository(Protocol):
    def add(
        self,
        *,
        user_id: int | None,
        username: str | None,
        action: str,
        entity: str,
        entity_id: str | None,
        previous: str | None,
        new: str | None,
        detail: str | None,
        station: str | None,
    ) -> None: ...

    def search(
        self, audit_filter: AuditFilter, *, page: int = 1, page_size: int = 100
    ) -> Page[AuditRow]: ...


class ImportRepository(Protocol):
    def create(
        self,
        *,
        file_name: str,
        sha256: str,
        mode: str,
        apply_stock: bool,
        user_id: int,
    ) -> int: ...

    def get(self, import_id: int) -> ImportRecord | None: ...

    def list_imports(self, *, limit: int = 200) -> list[ImportRecord]: ...

    def find_applied_by_hash(self, sha256: str) -> ImportRecord | None: ...

    def replace_details(self, import_id: int, rows: list[dict[str, Any]]) -> None: ...

    def details(
        self, import_id: int, *, only_errors: bool = False, limit: int | None = None
    ) -> list[ImportDetail]: ...

    def update_state(
        self, import_id: int, state: str, counters: Mapping[str, int], *, finished: bool
    ) -> None: ...

    def load_lookups(self) -> ImportLookups: ...


class SettingsRepository(Protocol):
    def get_all(self) -> dict[str, str]: ...

    def set_many(self, values: Mapping[str, str]) -> None: ...


class WorkUnit(Protocol):
    """Unidad de trabajo con los repositorios de una transacción."""

    catalogs: CatalogRepository
    products: ProductRepository
    movements: MovementRepository
    audit: AuditRepository
    imports: ImportRepository
    settings: SettingsRepository

    def __enter__(self) -> WorkUnit: ...

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def begin_immediate(self) -> None:
        """Inicia la transacción con bloqueo de escritura (BEGIN IMMEDIATE)."""


WorkUnitFactory = Callable[[], WorkUnit]


class CsvReaderPort(Protocol):
    def read(
        self,
        path: Path,
        *,
        encoding: str | None,
        delimiter: str | None,
        max_rows: int,
    ) -> CsvContent: ...


class ReportWriterPort(Protocol):
    """Escribe un `ReportData` en un archivo."""

    def write(self, path: Path, data: ReportData, *, company: Mapping[str, str]) -> None: ...


class BackupPort(Protocol):
    def create(self, target_dir: Path) -> tuple[Path, str]:
        """Devuelve ruta del .zip y SHA-256 de la base respaldada."""

    def restore(self, archive: Path) -> Path:
        """Restaura y devuelve la ruta del respaldo previo automático."""
