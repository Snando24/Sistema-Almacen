"""Respaldo y restauración (HU-08.3 a HU-08.5)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sisalmacen.application.auditing import AuditRecorder
from sisalmacen.application.auth import AuthorizationService, CurrentSession
from sisalmacen.application.ports import BackupPort, WorkUnitFactory
from sisalmacen.application.settings import SettingsService, int_setting
from sisalmacen.domain.errors import ValidationError

_STAMP = "%Y-%m-%dT%H:%M:%SZ"


class BackupService:
    def __init__(
        self,
        uow_factory: WorkUnitFactory,
        actor: CurrentSession,
        backup: BackupPort,
        settings: SettingsService,
        authorization: AuthorizationService | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._actor = actor
        self._backup = backup
        self._settings = settings
        self._authz = authorization or AuthorizationService()
        self._audit = AuditRecorder(actor)

    def default_folder(self) -> str:
        return self._settings.read_all().get("backup.carpeta", "")

    def last_backup(self) -> str:
        return self._settings.read_all().get("backup.ultimo", "")

    def create(self, target_dir: Path | None = None) -> tuple[Path, str]:
        self._authz.require_permission(self._actor, "backup.gestionar")
        folder = target_dir or Path(self.default_folder() or "")
        if not str(folder):
            raise ValidationError("Indique la carpeta de respaldos.", code="BACKUP_CARPETA")
        archive, sha256 = self._backup.create(folder)
        self._settings.mark_backup_done()
        with self._uow_factory() as uow:
            self._audit.record(
                uow, "RESPALDAR", "backup", archive.name, new={"sha256": sha256, "ruta": str(archive)}
            )
            uow.commit()
        return archive, sha256

    def restore(self, archive: Path) -> Path:
        """Restaura el respaldo y devuelve la ruta del respaldo previo automático."""

        self._authz.require_permission(self._actor, "backup.gestionar")
        previous = self._backup.restore(archive)
        try:
            with self._uow_factory() as uow:
                self._audit.record(
                    uow,
                    "RESTAURAR",
                    "backup",
                    archive.name,
                    detail=f"Respaldo previo: {previous}",
                )
                uow.commit()
        except Exception:
            # El usuario actual puede no existir en la base restaurada.
            logging.getLogger("sisalmacen").warning("No se pudo auditar la restauración.")
        return previous

    def reminder(self) -> str | None:
        """Mensaje si el último respaldo supera `backup.recordatorio_dias` (RB-22)."""

        settings = self._settings.read_all()
        days = int_setting(settings, "backup.recordatorio_dias", 7)
        last = settings.get("backup.ultimo", "")
        if not last:
            return "Todavía no se ha creado ningún respaldo."
        try:
            moment = datetime.strptime(last, _STAMP).replace(tzinfo=UTC)
        except ValueError:
            return None
        if datetime.now(tz=UTC) - moment > timedelta(days=days):
            return f"Han pasado más de {days} días desde el último respaldo."
        return None
