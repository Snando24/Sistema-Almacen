"""Formulario genérico de catálogos."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.domain.inventory import CATALOG_KINDS
from sisalmacen.ui.dialogs.product_dialog import fill_combo
from sisalmacen.ui.theme import apply_dialog_theme
from sisalmacen.ui.widgets import show_error


class CatalogDialog(QDialog):
    def __init__(
        self,
        services: AppServices,
        kind: str,
        entry: dict[str, Any] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self._services = services
        self._kind = kind
        self._entry = entry
        spec = CATALOG_KINDS[kind]
        self.setWindowTitle(f"{'Editar' if entry else 'Nuevo'}: {spec.singular}")
        self.setMinimumWidth(440)

        self._inputs: dict[str, QWidget] = {}
        form = QFormLayout()
        for field in spec.fields:
            value = entry.get(field.name) if entry else None
            widget: QWidget
            if field.kind == "bool":
                widget = QCheckBox()
                widget.setChecked(bool(value))
            elif field.kind == "ref":
                widget = QComboBox()
                options = [
                    e
                    for e in services.catalogs.list_entries(field.ref_kind or kind)
                    if entry is None or e["id"] != entry["id"]
                ]
                fill_combo(
                    widget,
                    options,
                    label="codigo",
                    blank="(ninguna)",
                    keep_id=value,
                    selected_id=value,
                )
            else:
                widget = QLineEdit("" if value is None else str(value))
            self._inputs[field.name] = widget
            form.addRow(field.label + (" *" if field.required else ""), widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        cancel = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel.setText("Cancelar")
        cancel.setProperty("variant", "secondary")
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _save(self) -> None:
        data: dict[str, Any] = {}
        for name, widget in self._inputs.items():
            if isinstance(widget, QCheckBox):
                data[name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                data[name] = widget.currentData()
            elif isinstance(widget, QLineEdit):
                data[name] = widget.text()
        try:
            if self._entry is None:
                self._services.catalogs.create(self._kind, data)
            else:
                self._services.catalogs.update(self._kind, int(self._entry["id"]), data)
        except Exception as error:
            show_error(self, error)
            return
        self.accept()
