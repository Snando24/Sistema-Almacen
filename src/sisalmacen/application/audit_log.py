"""Consulta de auditoría (HU-08.1): solo lectura."""

from __future__ import annotations

from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.ports import WorkUnitFactory
from sisalmacen.domain.inventory import AuditFilter, AuditRow, Page


class AuditService:
    def __init__(
        self,
        uow_factory: WorkUnitFactory,
        actor: CurrentSession,
        authorization: AuthorizationService | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._actor = actor
        self._authz = authorization or AuthorizationService()

    def search(
        self, audit_filter: AuditFilter, *, page: int = 1, page_size: int = 100
    ) -> Page[AuditRow]:
        self._authz.require_permission(self._actor, "auditoria.ver")
        with self._uow_factory() as uow:
            return uow.audit.search(audit_filter, page=page, page_size=page_size)
