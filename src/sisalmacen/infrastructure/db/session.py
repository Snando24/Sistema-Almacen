"""Creación de engine y sesiones SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def create_sqlite_engine(database_path: Path) -> Engine:
    """Crea un engine SQLite con las pragmas obligatorias."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite+pysqlite:///{database_path.as_posix()}",
        future=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection: object, connection_record: object) -> None:
        del connection_record
        if not isinstance(dbapi_connection, sqlite3.Connection):
            return
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute("PRAGMA journal_mode = WAL")
        cursor.execute("PRAGMA busy_timeout = 5000")
        cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Construye la factoría de sesiones usada por la aplicación."""

    return sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
        class_=Session,
    )
