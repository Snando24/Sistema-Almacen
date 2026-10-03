"""Inicialización de la base de datos y migraciones."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config


def _resolve_runtime_path(project_root: Path, relative_path: Path) -> Path:
    """Resuelve la ruta real de archivos de recursos tanto en desarrollo como empaquetados."""

    candidates: list[Path] = [project_root / relative_path]

    if getattr(sys, "_MEIPASS", None):
        candidates.append(Path(sys._MEIPASS) / relative_path)

    executable_dir = Path(sys.executable).resolve().parent
    candidates.append(executable_dir / relative_path)
    candidates.append(executable_dir / "_internal" / relative_path)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return project_root / relative_path


def build_alembic_config(database_path: Path, project_root: Path) -> Config:
    """Construye la configuración de Alembic para una base destino."""

    alembic_ini = _resolve_runtime_path(project_root, Path("alembic.ini"))
    migrations_dir = _resolve_runtime_path(
        project_root,
        Path("src") / "sisalmacen" / "infrastructure" / "migrations",
    )

    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(migrations_dir))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    return config


def known_revisions(project_root: Path) -> set[str]:
    """Revisiones Alembic conocidas por esta versión del código (vacío si no se pueden leer)."""

    try:
        from alembic.script import ScriptDirectory

        config = build_alembic_config(database_path=Path("unused.sqlite3"), project_root=project_root)
        script = ScriptDirectory.from_config(config)
        return {revision.revision for revision in script.walk_revisions()}
    except Exception:
        return set()


def _database_has_tables(database_path: Path) -> bool:
    """Comprueba si la base ya contiene tablas creadas."""

    if not database_path.exists():
        return False

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        return bool(rows)


def _bootstrap_sql_files(database_path: Path, project_root: Path) -> None:
    """Crea la Base de Datos desde los SQL de referencia cuando no hay migración disponible."""

    schema_path = _resolve_runtime_path(project_root, Path("db") / "001_schema.sql")
    seed_path = _resolve_runtime_path(project_root, Path("db") / "002_seed.sql")

    if not schema_path.exists() or not seed_path.exists():
        raise FileNotFoundError("No se encontraron los SQL de esquema y seed para la inicialización.")

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 5000")

        if not _database_has_tables(database_path):
            connection.executescript(schema_path.read_text(encoding="utf-8"))
            connection.executescript(seed_path.read_text(encoding="utf-8"))
            connection.commit()


def run_migrations(database_path: Path, project_root: Path) -> None:
    """Aplica todas las migraciones pendientes a la base indicada."""

    database_path.parent.mkdir(parents=True, exist_ok=True)

    alembic_ini = _resolve_runtime_path(project_root, Path("alembic.ini"))
    migrations_dir = _resolve_runtime_path(
        project_root,
        Path("src") / "sisalmacen" / "infrastructure" / "migrations",
    )

    if alembic_ini.exists() and migrations_dir.exists():
        try:
            config = build_alembic_config(database_path=database_path, project_root=project_root)
            command.upgrade(config, "head")
            return
        except Exception:
            if _database_has_tables(database_path):
                return

    _bootstrap_sql_files(database_path=database_path, project_root=project_root)
