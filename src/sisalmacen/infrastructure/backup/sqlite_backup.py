"""Respaldo y restauración de la base SQLite (RB-20, RB-21)."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import zipfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import Engine

from sisalmacen.domain.errors import ValidationError

DB_NAME = "sisalmacen.sqlite3"
MANIFEST_NAME = "manifest.json"
APP_VERSION = "0.1.0"


class SqliteBackup:
    """Implementa `BackupPort` con la API de copia en línea de SQLite."""

    def __init__(
        self,
        database_path: Path,
        engine: Engine,
        known_revisions: Callable[[], set[str]],
        safety_dir: Path,
    ) -> None:
        self._database_path = database_path
        self._engine = engine
        self._known_revisions = known_revisions
        self._safety_dir = safety_dir

    def create(self, target_dir: Path) -> tuple[Path, str]:
        return self._create(target_dir, prefix="respaldo")

    def _create(self, target_dir: Path, *, prefix: str) -> tuple[Path, str]:
        target_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
        archive = target_dir / f"{prefix}_{stamp}.zip"
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = Path(tmp) / DB_NAME
            source = sqlite3.connect(self._database_path)
            destination = sqlite3.connect(snapshot)
            try:
                source.backup(destination)
            finally:
                destination.close()
                source.close()
            sha256 = _sha256(snapshot)
            manifest = {
                "app_version": APP_VERSION,
                "schema_version": _schema_version(snapshot),
                "created_at": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "database": DB_NAME,
                "sha256": sha256,
            }
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
                bundle.write(snapshot, DB_NAME)
                bundle.writestr(MANIFEST_NAME, json.dumps(manifest, indent=2))
        return archive, sha256

    def restore(self, archive: Path) -> Path:
        with tempfile.TemporaryDirectory() as tmp:
            candidate = self._extract_and_validate(archive, Path(tmp))
            previous, _ = self._create(self._safety_dir, prefix="prerestauracion")
            self._engine.dispose()
            for suffix in ("-wal", "-shm"):
                Path(str(self._database_path) + suffix).unlink(missing_ok=True)
            shutil.copy2(candidate, self._database_path)
        return previous

    def _extract_and_validate(self, archive: Path, workdir: Path) -> Path:
        try:
            with zipfile.ZipFile(archive) as bundle:
                names = set(bundle.namelist())
                if MANIFEST_NAME not in names or DB_NAME not in names:
                    raise _invalid()
                manifest = json.loads(bundle.read(MANIFEST_NAME))
                bundle.extract(DB_NAME, workdir)
        except (zipfile.BadZipFile, json.JSONDecodeError, OSError) as error:
            raise _invalid() from error

        candidate = workdir / DB_NAME
        if _sha256(candidate) != manifest.get("sha256"):
            raise _invalid()
        try:
            connection = sqlite3.connect(candidate)
            try:
                result = connection.execute("PRAGMA integrity_check").fetchone()
            finally:
                connection.close()
        except sqlite3.DatabaseError as error:
            raise _invalid() from error
        if not result or result[0] != "ok":
            raise _invalid()
        known = self._known_revisions()
        version = manifest.get("schema_version")
        if known and version is not None and version not in known:
            raise _invalid()
        return candidate


def _invalid() -> ValidationError:
    return ValidationError(
        "El respaldo no es válido o es de una versión incompatible.", code="BACKUP_INVALIDO"
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _schema_version(database: Path) -> str | None:
    connection = sqlite3.connect(database)
    try:
        row = connection.execute("SELECT version_num FROM alembic_version").fetchone()
        return None if row is None else str(row[0])
    except sqlite3.DatabaseError:
        return None
    finally:
        connection.close()
