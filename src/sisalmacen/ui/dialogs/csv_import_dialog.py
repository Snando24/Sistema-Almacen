"""Diálogo para importar datos desde CSV."""

from __future__ import annotations

from csv import DictReader
from io import StringIO
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QMessageBox,
)

from sisalmacen.ui.theme import apply_dialog_theme
from sisalmacen.ui.widgets import TableModel, make_table

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget


class CSVImportDialog(QDialog):
    """Diálogo para importar datos desde CSV con preview."""

    def __init__(self, csv_content: str, headers: list[str], parent: QWidget | None = None) -> None:
        """
        Args:
            csv_content: Contenido del archivo CSV como string
            headers: Lista de columnas esperadas
            parent: Widget padre
        """
        super().__init__(parent)
        self.setWindowTitle("Vista previa de importación")
        self.setMinimumSize(800, 400)
        self.csv_content = csv_content
        self.headers = headers
        self.rows = []

        # Parse CSV content
        self._parse_csv()

        # Build UI
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Se importarán {len(self.rows)} registros:"))

        # Table with preview
        model = TableModel(headers)
        for row in self.rows:
            model.append([row.get(h, "") for h in headers])

        table = make_table(model)
        layout.addWidget(table)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        apply_dialog_theme(self)

    def _parse_csv(self) -> None:
        """Parse CSV content and extract rows."""
        try:
            # Remove BOM if present
            content = self.csv_content.lstrip("\ufeff")
            reader = DictReader(StringIO(content))
            self.rows = list(reader)
        except Exception as e:
            raise ValueError(f"Error parsing CSV: {e}")

    def get_rows(self) -> list[dict[str, str]]:
        """Get parsed rows."""
        return self.rows
