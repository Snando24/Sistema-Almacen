"""Página de catálogos (S-07)."""

from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.domain.inventory import CATALOG_KINDS
from sisalmacen.ui.dialogs.catalog_dialog import CatalogDialog
from sisalmacen.ui.widgets import (
    TableModel,
    build_page_header,
    guarded,
    make_table,
    selected_payload,
    show_error,
)


class _CatalogTab(QWidget):
    def __init__(self, services: AppServices, kind: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._services = services
        self._kind = kind
        self._spec = CATALOG_KINDS[kind]
        self._can_manage = "catalogos.gestionar" in services.session.permisos

        headers = [f.label for f in self._spec.fields if f.kind != "bool"] + ["Estado"]
        self._columns = [f for f in self._spec.fields if f.kind != "bool"]
        bools = [f for f in self._spec.fields if f.kind == "bool"]
        self._bool_fields = bools
        headers = [f.label for f in self._columns] + [f.label for f in bools] + ["Estado"]
        self._model = TableModel(headers)
        self._table: QTableView = make_table(self._model)
        self._table.doubleClicked.connect(lambda _index: self._edit())

        self._inactive = QCheckBox("Mostrar inactivos")
        self._inactive.toggled.connect(lambda _checked: self.refresh())
        new_button = QPushButton("Nuevo")
        new_button.clicked.connect(self._new)
        edit_button = QPushButton("Editar")
        edit_button.clicked.connect(self._edit)
        toggle_button = QPushButton("Activar / desactivar")
        toggle_button.clicked.connect(self._toggle)
        for button in (new_button, edit_button, toggle_button):
            button.setEnabled(self._can_manage)

        bar = QHBoxLayout()
        bar.addWidget(new_button)
        bar.addWidget(edit_button)
        bar.addWidget(toggle_button)
        bar.addStretch(1)
        bar.addWidget(self._inactive)
        layout = QVBoxLayout()
        layout.addLayout(bar)
        layout.addWidget(self._table, 1)
        self.setLayout(layout)
        self.refresh()

    def refresh(self) -> None:
        try:
            entries = self._services.catalogs.list_entries(
                self._kind, include_inactive=self._inactive.isChecked()
            )
            names = {e["id"]: e for e in entries}
        except Exception as error:
            show_error(self, error)
            return
        rows: list[list[str]] = []
        for entry in entries:
            row = []
            for field in self._columns:
                value = entry.get(field.name)
                if field.kind == "ref":
                    parent = names.get(value)
                    value = parent["codigo"] if parent else ""
                row.append("" if value is None else str(value))
            row += ["Sí" if entry.get(f.name) else "No" for f in self._bool_fields]
            row.append("Activo" if entry.get("activo") else "Inactivo")
            rows.append(row)
        self._model.set_rows(rows, payloads=entries)

    def _selected(self) -> dict[str, Any] | None:
        entry = selected_payload(self._table, self._model)
        if entry is None:
            QMessageBox.information(self, "Catálogos", "Seleccione un registro.")
        return entry

    @guarded
    def _new(self) -> None:
        if CatalogDialog(self._services, self._kind, parent=self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    @guarded
    def _edit(self) -> None:
        if not self._can_manage:
            return
        entry = self._selected()
        if entry is None:
            return
        dialog = CatalogDialog(self._services, self._kind, entry, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    @guarded
    def _toggle(self) -> None:
        entry = self._selected()
        if entry is None:
            return
        self._services.catalogs.set_active(
            self._kind, int(entry["id"]), active=not bool(entry.get("activo"))
        )
        self.refresh()


class CatalogsPage(QWidget):
    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("catalogos-page")
        self._tabs = QTabWidget()
        self._tab_widgets: list[_CatalogTab] = []
        for kind, spec in CATALOG_KINDS.items():
            tab = _CatalogTab(services, kind)
            self._tab_widgets.append(tab)
            self._tabs.addTab(tab, spec.label)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(
            build_page_header(
                "Catálogos", "Categorías, marcas, unidades, proveedores y ubicaciones."
            )
        )
        layout.addWidget(self._tabs, 1)
        self.setLayout(layout)

    def refresh(self) -> None:
        for tab in self._tab_widgets:
            tab.refresh()
