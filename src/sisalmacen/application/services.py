"""Contenedor de servicios que recibe la interfaz."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sisalmacen.application.audit_log import AuditService
from sisalmacen.application.auth import CurrentSession
from sisalmacen.application.backup import BackupService
from sisalmacen.application.catalogs import CatalogService
from sisalmacen.application.importing import ImportService
from sisalmacen.application.movements import MovementService
from sisalmacen.application.products import ProductService
from sisalmacen.application.reports import ReportService
from sisalmacen.application.settings import SettingsService
from sisalmacen.domain.auth import DashboardSnapshot


@dataclass(frozen=True)
class AppServices:
    session: CurrentSession
    catalogs: CatalogService
    products: ProductService
    movements: MovementService
    imports: ImportService
    reports: ReportService
    audit: AuditService
    settings: SettingsService
    backup: BackupService
    load_dashboard: Callable[[], DashboardSnapshot]
