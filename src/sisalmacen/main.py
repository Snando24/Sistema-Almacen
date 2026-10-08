"""Punto de entrada de SisAlmacen."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from sisalmacen.bootstrap import bootstrap_application
from sisalmacen.composition import build_services, start_local_session
from sisalmacen.infrastructure.config import AppPaths
from sisalmacen.ui.main_window import MainWindow
from sisalmacen.ui.theme import (
    BRAND_NAME,
    THEME_LIGHT,
    THEME_SETTING_KEY,
    apply_application_theme,
    get_app_icon,
)


def _build_runtime_label(path: Path, paths: AppPaths) -> str:
    """Genera una etiqueta amigable para rutas locales mostradas en la UI."""

    storage_root = paths.data_dir.parent
    try:
        relative = path.relative_to(storage_root)
        return f"datos locales/{relative.as_posix()}"
    except ValueError:
        return str(path)


def main() -> int:
    """Inicia la aplicación de escritorio."""

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(BRAND_NAME)
    app.setApplicationDisplayName(BRAND_NAME)
    app.setWindowIcon(get_app_icon())
    apply_application_theme(app, THEME_LIGHT)

    try:
        context = bootstrap_application()
        backup_dir = context.paths.data_dir / "respaldos"
        backup_dir.mkdir(parents=True, exist_ok=True)
        current = start_local_session(context.session_factory, str(backup_dir))
        services = build_services(context, current)
        apply_application_theme(
            app, services.settings.read_all().get(THEME_SETTING_KEY, THEME_LIGHT)
        )
        window = MainWindow(
            services=services,
            database_label=_build_runtime_label(context.paths.database_path, context.paths),
            logs_label=_build_runtime_label(context.paths.logs_dir / "sisalmacen.log", context.paths),
        )
    except Exception:  # pragma: no cover - manejo defensivo de arranque
        logging.getLogger("sisalmacen").exception("Fallo técnico al iniciar la aplicación.")
        QMessageBox.critical(
            None,
            "Error de inicio",
            "No se pudo inicializar la aplicación. Revise el log para más detalle técnico.",
        )
        return 1

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
