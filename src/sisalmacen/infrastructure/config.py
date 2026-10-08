"""Resolución de rutas y configuración base de la aplicación."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Rutas utilizadas por la aplicación local."""

    project_root: Path
    data_dir: Path
    logs_dir: Path
    database_path: Path


APP_FOLDER_NAME = "SisAlmacen"


def resolve_project_root() -> Path:
    """Obtiene la raíz del proyecto en modo desarrollo."""

    return Path(__file__).resolve().parents[3]


def _is_frozen_runtime() -> bool:
    """Indica si la app corre desde un ejecutable empaquetado."""

    return bool(getattr(sys, "frozen", False))


def _resolve_persistent_root() -> Path:
    """Obtiene la carpeta persistente para datos del usuario en Windows."""

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / APP_FOLDER_NAME
    return Path.home() / "AppData" / "Local" / APP_FOLDER_NAME


def resolve_app_paths(project_root: Path | None = None) -> AppPaths:
    """Construye las rutas persistentes principales."""

    root = project_root or resolve_project_root()
    storage_root = _resolve_persistent_root() if _is_frozen_runtime() else root
    data_dir = storage_root / "var"
    logs_dir = storage_root / "logs"
    database_path = data_dir / "sisalmacen.sqlite3"
    return AppPaths(
        project_root=root,
        data_dir=data_dir,
        logs_dir=logs_dir,
        database_path=database_path,
    )
