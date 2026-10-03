"""Pruebas de equivalencia entre la migración y el SQL de referencia."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sisalmacen.infrastructure.db.bootstrap import run_migrations


def _execute_script(database_path: Path, script_path: Path) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.executescript(script_path.read_text(encoding="utf-8"))


def _schema_snapshot(database_path: Path) -> list[tuple[str, str, str, str | None]]:
    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT type, name, tbl_name, sql
            FROM sqlite_master
            WHERE name NOT LIKE 'sqlite_%'
              AND name <> 'alembic_version'
            ORDER BY type, name
            """
        ).fetchall()
    return [
        (row[0], row[1], row[2], None if row[3] is None else " ".join(row[3].split()))
        for row in rows
    ]


def test_initial_migration_matches_reference_schema(tmp_path: Path, project_root: Path) -> None:
    reference_db = tmp_path / "reference.sqlite3"
    migrated_db = tmp_path / "migrated.sqlite3"

    _execute_script(reference_db, project_root / "db" / "001_schema.sql")
    _execute_script(reference_db, project_root / "db" / "002_seed.sql")
    run_migrations(database_path=migrated_db, project_root=project_root)

    assert _schema_snapshot(migrated_db) == _schema_snapshot(reference_db)


def test_initial_migration_loads_seed_data(tmp_path: Path, project_root: Path) -> None:
    migrated_db = tmp_path / "seed.sqlite3"
    run_migrations(database_path=migrated_db, project_root=project_root)

    with sqlite3.connect(migrated_db) as connection:
        roles = connection.execute("SELECT COUNT(*) FROM rol").fetchone()[0]
        permisos = connection.execute("SELECT COUNT(*) FROM permiso").fetchone()[0]
        tipos = connection.execute("SELECT COUNT(*) FROM tipo_movimiento").fetchone()[0]
        categorias = connection.execute("SELECT COUNT(*) FROM categoria").fetchone()[0]

    assert roles == 3
    assert permisos == 19
    assert tipos == 9
    assert categorias == 17
