"""Fixtures compartidas de pruebas."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def project_root() -> Path:
    return ROOT


@pytest.fixture
def app_context(tmp_path: Path, project_root: Path):  # type: ignore[no-untyped-def]
    from sisalmacen.bootstrap import AppContext
    from sisalmacen.infrastructure.config import AppPaths
    from sisalmacen.infrastructure.db.bootstrap import run_migrations
    from sisalmacen.infrastructure.db.session import create_session_factory, create_sqlite_engine

    data_dir = tmp_path / "var"
    database_path = data_dir / "sisalmacen.sqlite3"
    paths = AppPaths(
        project_root=project_root,
        data_dir=data_dir,
        logs_dir=tmp_path / "logs",
        database_path=database_path,
    )
    run_migrations(database_path=database_path, project_root=project_root)
    engine = create_sqlite_engine(database_path)
    context = AppContext(paths=paths, engine=engine, session_factory=create_session_factory(engine))
    yield context
    engine.dispose()


@pytest.fixture
def services(app_context, tmp_path: Path):  # type: ignore[no-untyped-def]
    from sisalmacen.composition import build_services, start_local_session

    current = start_local_session(app_context.session_factory, str(tmp_path / "respaldos"))
    return build_services(app_context, current)


@pytest.fixture
def make_product(services) -> Callable[..., int]:  # type: ignore[no-untyped-def]
    """Crea un producto con categoría y unidad por defecto; devuelve su id."""

    from sisalmacen.domain.inventory import ProductData

    def factory(code: str = "P-1", unit: str = "UND", **extra: object) -> int:
        categories = services.catalogs.list_entries("categoria")
        general = next((category for category in categories if category["nombre"] == "General"), None)
        if general is not None:
            category_id = int(general["id"])
        elif categories:
            category_id = int(max(categories, key=lambda category: int(category["id"]))["id"])
        else:
            category_id = services.catalogs.create("categoria", {"nombre": "General"})
        unit_id = next(
            u["id"] for u in services.catalogs.list_entries("unidad_medida") if u["codigo"] == unit
        )
        data = ProductData(
            codigo=code,
            nombre=f"Producto {code}",
            categoria_id=category_id,
            unidad_id=unit_id,
            **extra,  # type: ignore[arg-type]
        )
        return services.products.create(data)

    return factory
