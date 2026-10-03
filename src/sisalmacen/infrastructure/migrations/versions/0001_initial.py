"""Migración inicial equivalente al SQL de referencia."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Final

from alembic import op

revision: Final[str] = "0001_initial"
down_revision: Final[str | None] = None
branch_labels: Final[tuple[str, ...] | None] = None
depends_on: Final[tuple[str, ...] | None] = None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _sqlite_connection() -> sqlite3.Connection:
    proxied_connection = op.get_bind().connection
    driver_connection = getattr(proxied_connection, "driver_connection", None)
    if driver_connection is None:
        driver_connection = getattr(proxied_connection, "dbapi_connection", None)
    if isinstance(driver_connection, sqlite3.Connection):
        return driver_connection
    if isinstance(proxied_connection, sqlite3.Connection):
        return proxied_connection
    raise TypeError("La migración inicial requiere una conexión SQLite.")


def _run_script(path: Path) -> None:
    connection = _sqlite_connection()
    sql = path.read_text(encoding="utf-8")
    connection.executescript(sql)


def upgrade() -> None:
    root = _repo_root()
    _run_script(root / "db" / "001_schema.sql")
    _run_script(root / "db" / "002_seed.sql")


def downgrade() -> None:
    tables = [
        "auditoria",
        "detalle_movimiento",
        "movimiento",
        "detalle_importacion",
        "importacion",
        "tipo_movimiento",
        "inventario",
        "producto",
        "ubicacion",
        "proveedor",
        "unidad_medida",
        "marca",
        "categoria",
        "usuario",
        "rol_permiso",
        "permiso",
        "rol",
        "configuracion",
    ]
    for table_name in tables:
        op.execute(f"DROP TABLE IF EXISTS {table_name}")
