"""Selector de producto por código, nombre o código de barras."""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.domain.inventory import ProductFilter, ProductRecord
from sisalmacen.ui.theme import apply_dialog_theme
from sisalmacen.ui.widgets import (
    TableModel,
    fmt_qty,
    guarded,
    make_table,
    selected_payload,
    show_error,
)


class ProductSearchDialog(QDialog):
    """Lista de coincidencias para elegir un producto."""

    def __init__(
        self,
        services: AppServices,
        text: str,
        *,
        only_active: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self._services = services
        self._only_active = only_active
        self.selected: ProductRecord | None = None
        self.setWindowTitle("Buscar producto")
        self.resize(760, 460)

        self._query = QLineEdit(text)
        self._query.setPlaceholderText("Código, nombre o código de barras")
        self._query.returnPressed.connect(self._search)
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self._search)
        self._model = TableModel(["Código", "Nombre", "Unidad", "Stock"], right_aligned={3})
        self._table = make_table(self._model)
        self._table.doubleClicked.connect(self._choose_index)
        choose_button = QPushButton("Seleccionar")
        choose_button.clicked.connect(self._choose)
        self._hint = QLabel("")

        top = QHBoxLayout()
        top.addWidget(self._query, 1)
        top.addWidget(search_button)
        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._hint)
        layout.addWidget(choose_button)
        self.setLayout(layout)
        self._search()

    @guarded
    def _search(self) -> None:
        result = self._services.products.search(
            ProductFilter(texto=self._query.text(), estado="ACTIVO" if self._only_active else None),
            page=1,
            page_size=50,
        )
        self._model.set_rows(
            [[p.codigo, p.nombre, p.unidad, fmt_qty(p.cantidad)] for p in result.items],
            payloads=list(result.items),
        )
        self._hint.setText(
            f"Mostrando {len(result.items)} de {result.total}. Refine la búsqueda si no aparece."
        )

    def _choose_index(self, _index: QModelIndex) -> None:
        self._choose()

    def _choose(self) -> None:
        record = selected_payload(self._table, self._model)
        if record is None:
            return
        self.selected = record
        self.accept()


class ProductPicker(QWidget):
    """Campo de texto + botón que resuelve un único producto."""

    changed = Signal()

    def __init__(
        self,
        services: AppServices,
        *,
        only_active: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._services = services
        self._only_active = only_active
        self.product: ProductRecord | None = None

        self._edit = QLineEdit()
        self._edit.setPlaceholderText("Código, nombre o código de barras + Enter")
        self._edit.returnPressed.connect(self._lookup)
        button = QPushButton("Buscar")
        button.clicked.connect(self._lookup)
        self._label = QLabel("Ningún producto seleccionado")
        self._label.setObjectName("info-label")

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self._edit, 1)
        row.addWidget(button)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addLayout(row)
        layout.addWidget(self._label)
        self.setLayout(layout)

    def clear(self) -> None:
        self.product = None
        self._edit.clear()
        self._label.setText("Ningún producto seleccionado")
        self.changed.emit()

    def focus_input(self) -> None:
        self._edit.setFocus()

    def set_product(self, record: ProductRecord | None) -> None:
        self.product = record
        if record is None:
            self._label.setText("Ningún producto seleccionado")
        else:
            self._edit.setText(record.codigo)
            self._label.setText(
                f"{record.codigo} · {record.nombre} · "
                f"Stock: {fmt_qty(record.cantidad)} {record.unidad}"
            )
        self.changed.emit()

    def _lookup(self) -> None:
        text = self._edit.text().strip()
        try:
            result = self._services.products.search(
                ProductFilter(texto=text, estado="ACTIVO" if self._only_active else None),
                page=1,
                page_size=30,
            )
        except Exception as error:
            show_error(self, error)
            return
        lowered = text.lower()
        exact = [
            p
            for p in result.items
            if p.codigo.lower() == lowered or (p.codigo_barras or "").lower() == lowered
        ]
        if len(exact) == 1:
            self.set_product(exact[0])
            return
        if len(result.items) == 1:
            self.set_product(result.items[0])
            return
        if not result.items and text:
            QMessageBox.information(self, "Buscar producto", "No se encontraron productos.")
            return
        dialog = ProductSearchDialog(
            self._services, text, only_active=self._only_active, parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected is not None:
            self.set_product(dialog.selected)
