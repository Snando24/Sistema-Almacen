"""Unidad de trabajo basada en SQLAlchemy."""

from __future__ import annotations

import sqlite3

from sqlalchemy.orm import Session, sessionmaker

from sisalmacen.application.uow import UnitOfWork
from sisalmacen.infrastructure.db.catalog_product_repositories import (
    SqlAlchemyCatalogRepository,
    SqlAlchemyProductRepository,
)
from sisalmacen.infrastructure.db.import_settings_repositories import (
    SqlAlchemyImportRepository,
    SqlAlchemySettingsRepository,
)
from sisalmacen.infrastructure.db.movement_audit_repositories import (
    SqlAlchemyAuditRepository,
    SqlAlchemyMovementRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Implementación concreta de la unidad de trabajo con los repositorios de negocio."""

    session: Session | None
    catalogs: SqlAlchemyCatalogRepository
    products: SqlAlchemyProductRepository
    movements: SqlAlchemyMovementRepository
    audit: SqlAlchemyAuditRepository
    imports: SqlAlchemyImportRepository
    settings: SqlAlchemySettingsRepository

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self.session = None

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        self.session = self._session_factory()
        self.catalogs = SqlAlchemyCatalogRepository(self.session)
        self.products = SqlAlchemyProductRepository(self.session)
        self.movements = SqlAlchemyMovementRepository(self.session)
        self.audit = SqlAlchemyAuditRepository(self.session)
        self.imports = SqlAlchemyImportRepository(self.session)
        self.settings = SqlAlchemySettingsRepository(self.session)
        return self

    def begin_immediate(self) -> None:
        """Abre la transacción con `BEGIN IMMEDIATE` si aún no hay una activa (ADR-17)."""

        if self.session is None:
            raise RuntimeError("La unidad de trabajo no está activa.")
        raw = self.session.connection().connection.driver_connection
        if isinstance(raw, sqlite3.Connection) and not raw.in_transaction:
            raw.execute("BEGIN IMMEDIATE")

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        try:
            if exc_type is not None:
                self.rollback()
        finally:
            if self.session is not None:
                self.session.close()
                self.session = None

    def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("La unidad de trabajo no está activa.")
        self.session.commit()

    def rollback(self) -> None:
        if self.session is None:
            return
        self.session.rollback()
