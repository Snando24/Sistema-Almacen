"""Raíz de composición: conecta aplicación, infraestructura y sesión local."""

from __future__ import annotations

from sqlalchemy.orm import Session, sessionmaker

from sisalmacen.application.audit_log import AuditService
from sisalmacen.application.auth import (
    CurrentSession,
    DashboardService,
    LocalSessionService,
)
from sisalmacen.application.backup import BackupService
from sisalmacen.application.catalogs import CatalogService
from sisalmacen.application.importing import ImportService
from sisalmacen.application.movements import MovementService
from sisalmacen.application.products import ProductService
from sisalmacen.application.reports import ReportService
from sisalmacen.application.services import AppServices
from sisalmacen.application.settings import SettingsService
from sisalmacen.bootstrap import AppContext
from sisalmacen.domain.auth import DashboardSnapshot
from sisalmacen.infrastructure.backup.sqlite_backup import SqliteBackup
from sisalmacen.infrastructure.csv.reader import CsvFileReader
from sisalmacen.infrastructure.db.auth_repositories import (
    SqlAlchemyConfigurationRepository,
    SqlAlchemyDashboardRepository,
    SqlAlchemyUserRepository,
)
from sisalmacen.infrastructure.db.bootstrap import known_revisions
from sisalmacen.infrastructure.db.uow import SqlAlchemyUnitOfWork
from sisalmacen.infrastructure.export.csv_export import CsvReportWriter
from sisalmacen.infrastructure.export.excel_export import ExcelReportWriter
from sisalmacen.infrastructure.export.pdf_export import PdfReportWriter
from sisalmacen.infrastructure.security.passwords import Argon2PasswordHasher
from sisalmacen.ui.theme import BRAND_NAME


def start_local_session(
    session_factory: sessionmaker[Session], backup_folder: str
) -> CurrentSession:
    """Crea o reutiliza el usuario local y completa la configuración mínima."""

    with session_factory() as session:
        try:
            service = LocalSessionService(
                user_repository=SqlAlchemyUserRepository(session),
                configuration_repository=SqlAlchemyConfigurationRepository(session),
                password_hasher=Argon2PasswordHasher(),
            )
            current = service.start(company_name=BRAND_NAME, backup_folder=backup_folder)
            session.commit()
            return current
        except Exception:
            session.rollback()
            raise


def build_services(context: AppContext, current: CurrentSession) -> AppServices:
    """Construye todos los casos de uso con sus dependencias concretas."""

    session_factory = context.session_factory

    def uow_factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    def load_dashboard() -> DashboardSnapshot:
        with session_factory() as session:
            return DashboardService(SqlAlchemyDashboardRepository(session)).get_snapshot()

    settings = SettingsService(uow_factory, current)  # type: ignore[arg-type]
    movements = MovementService(uow_factory, current)  # type: ignore[arg-type]
    backup_port = SqliteBackup(
        database_path=context.paths.database_path,
        engine=context.engine,
        known_revisions=lambda: known_revisions(context.paths.project_root),
        safety_dir=context.paths.data_dir / "respaldos" / "automaticos",
    )
    writers = {"csv": CsvReportWriter(), "xlsx": ExcelReportWriter(), "pdf": PdfReportWriter()}
    return AppServices(
        session=current,
        catalogs=CatalogService(uow_factory, current),  # type: ignore[arg-type]
        products=ProductService(uow_factory, current),  # type: ignore[arg-type]
        movements=movements,
        imports=ImportService(uow_factory, current, CsvFileReader(), movements),  # type: ignore[arg-type]
        reports=ReportService(uow_factory, current, writers),  # type: ignore[arg-type]
        audit=AuditService(uow_factory, current),  # type: ignore[arg-type]
        settings=settings,
        backup=BackupService(uow_factory, current, backup_port, settings),  # type: ignore[arg-type]
        load_dashboard=load_dashboard,
    )
