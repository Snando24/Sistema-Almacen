"""Exportación e impresión de reportes desde la interfaz."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from sisalmacen.application.services import AppServices
from sisalmacen.domain.inventory import ReportData
from sisalmacen.ui.widgets import show_error

_FILTERS = {
    "csv": ("CSV (*.csv)", ".csv"),
    "xlsx": ("Excel (*.xlsx)", ".xlsx"),
    "pdf": ("PDF (*.pdf)", ".pdf"),
}


def write_csv_rows(path: Path, rows: list[list[str]]) -> None:
    """Escribe filas simples en CSV UTF-8 con BOM (informe de errores de importación)."""

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)


def export_report(
    parent: QWidget, services: AppServices, data: ReportData, fmt: str
) -> Path | None:
    """Pide destino, exporta y avisa. Devuelve la ruta o `None` si se canceló o falló."""

    file_filter, suffix = _FILTERS[fmt]
    chosen, _ = QFileDialog.getSaveFileName(
        parent, "Exportar", f"{data.key}{suffix}", file_filter
    )
    if not chosen:
        return None
    path = Path(chosen)
    if path.suffix.lower() != suffix:
        path = path.with_suffix(suffix)
    try:
        services.reports.export(data, fmt, path)
    except Exception as error:
        show_error(parent, error)
        return None
    QMessageBox.information(parent, "Exportación", f"Archivo generado:\n{path}")
    return path


def preview_report(parent: QWidget, services: AppServices, data: ReportData) -> None:
    """Genera un PDF temporal y lo abre en el visor del sistema (vista previa/impresión)."""

    handle = tempfile.NamedTemporaryFile(prefix="sisalmacen_", suffix=".pdf", delete=False)
    handle.close()
    path = Path(handle.name)
    try:
        services.reports.export(data, "pdf", path)
    except Exception as error:
        show_error(parent, error)
        return
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
