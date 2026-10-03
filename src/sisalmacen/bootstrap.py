"""Bootstrap principal de la aplicación."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from sisalmacen.infrastructure.config import AppPaths, resolve_app_paths
from sisalmacen.infrastructure.db.bootstrap import run_migrations
from sisalmacen.infrastructure.db.session import create_session_factory, create_sqlite_engine
from sisalmacen.infrastructure.logging import configure_logging


@dataclass(frozen=True)
class AppContext:
    """Dependencias principales de ejecución."""

    paths: AppPaths
    engine: Engine
    session_factory: sessionmaker[Session]


def bootstrap_application() -> AppContext:
    """Prepara rutas, logging, migraciones y conexión a la BD."""

    paths = resolve_app_paths()
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.logs_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(paths.logs_dir)
    run_migrations(database_path=paths.database_path, project_root=paths.project_root)
    engine = create_sqlite_engine(paths.database_path)
    session_factory = create_session_factory(engine)
    return AppContext(paths=paths, engine=engine, session_factory=session_factory)
