"""Pruebas de rutas para desarrollo y ejecutable empaquetado."""

from __future__ import annotations

from pathlib import Path

from sisalmacen.infrastructure.config import resolve_app_paths


def test_resolve_app_paths_uses_project_folders_in_development(tmp_path: Path) -> None:
    paths = resolve_app_paths(project_root=tmp_path)

    assert paths.project_root == tmp_path
    assert paths.data_dir == tmp_path / "var"
    assert paths.logs_dir == tmp_path / "logs"
    assert paths.database_path == tmp_path / "var" / "sisalmacen.sqlite3"


def test_resolve_app_paths_uses_localappdata_when_frozen(
    monkeypatch, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    local_appdata = tmp_path / "LocalAppData"
    monkeypatch.setenv("LOCALAPPDATA", str(local_appdata))
    monkeypatch.setattr("sisalmacen.infrastructure.config.sys.frozen", True, raising=False)

    paths = resolve_app_paths(project_root=tmp_path / "_internal")

    assert paths.project_root == tmp_path / "_internal"
    assert paths.data_dir == local_appdata / "SisAlmacen" / "var"
    assert paths.logs_dir == local_appdata / "SisAlmacen" / "logs"
    assert paths.database_path == local_appdata / "SisAlmacen" / "var" / "sisalmacen.sqlite3"
