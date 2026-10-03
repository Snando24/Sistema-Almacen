"""Resolución de rutas y configuración base de la aplicación."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Rutas utilizadas por la aplicación local."""

    project_root: Path
    data_dir: Path
    logs_dir: Path
    database_path: Path


def resolve_project_root() -> Path:
    """Obtiene la raíz del proyecto en modo desarrollo."""

    return Path(__file__).resolve().parents[3]


def resolve_app_paths(project_root: Path | None = None) -> AppPaths:
    """Construye las rutas persistentes principales."""

    root = project_root or resolve_project_root()
    data_dir = root / "var"
    logs_dir = root / "logs"
    database_path = data_dir / "sisalmacen.sqlite3"
    return AppPaths(
        project_root=root,
        data_dir=data_dir,
        logs_dir=logs_dir,
        database_path=database_path,
    )
