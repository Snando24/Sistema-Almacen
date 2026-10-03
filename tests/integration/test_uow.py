"""Pruebas mínimas de la unidad de trabajo."""

from __future__ import annotations

from pathlib import Path

from sisalmacen.infrastructure.db.bootstrap import run_migrations
from sisalmacen.infrastructure.db.models import Configuracion
from sisalmacen.infrastructure.db.repositories import SqlAlchemyRepository
from sisalmacen.infrastructure.db.session import create_session_factory, create_sqlite_engine
from sisalmacen.infrastructure.db.uow import SqlAlchemyUnitOfWork


def test_sqlalchemy_uow_commit_persists_changes(tmp_path: Path, project_root: Path) -> None:
    database_path = tmp_path / "uow_commit.sqlite3"
    run_migrations(database_path=database_path, project_root=project_root)

    engine = create_sqlite_engine(database_path)
    session_factory = create_session_factory(engine)

    with SqlAlchemyUnitOfWork(session_factory) as uow:
        assert uow.session is not None
        repository = SqlAlchemyRepository(uow.session, Configuracion)
        repository.add(Configuracion(clave="demo.clave", valor="1", descripcion="Prueba"))
        uow.commit()

    with session_factory() as session:
        stored = session.get(Configuracion, "demo.clave")

    assert stored is not None
    assert stored.valor == "1"


def test_sqlalchemy_uow_rollback_discards_changes(tmp_path: Path, project_root: Path) -> None:
    database_path = tmp_path / "uow_rollback.sqlite3"
    run_migrations(database_path=database_path, project_root=project_root)

    engine = create_sqlite_engine(database_path)
    session_factory = create_session_factory(engine)

    with SqlAlchemyUnitOfWork(session_factory) as uow:
        assert uow.session is not None
        repository = SqlAlchemyRepository(uow.session, Configuracion)
        repository.add(Configuracion(clave="demo.rollback", valor="1", descripcion="Prueba"))
        uow.rollback()

    with session_factory() as session:
        stored = session.get(Configuracion, "demo.rollback")

    assert stored is None
