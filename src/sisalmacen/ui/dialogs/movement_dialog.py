"""Diálogos de entrada, salida y ajuste de inventario (CU-005, CU-006)."""

from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.domain.errors import ValidationError
from sisalmacen.domain.inventory import MovementLine, MovementRequest, ProductRecord
from sisalmacen.ui.pickers import ProductPicker
from sisalmacen.ui.theme import apply_dialog_theme
from sisalmacen.ui.widgets import (
    TableModel,
    fmt_qty,
    make_table,
    parse_decimal_input,
    selected_payload,
    show_error,
)

TITLES = {"ENTRADA": "Registrar entrada", "SALIDA": "Registrar salida"}


class MovementDialog(QDialog):
    """Cabecera + líneas producto/cantidad para entradas y salidas."""

    def __init__(self, services: AppServices, nature: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self._services = services
        self._nature = nature
        self._lines: list[tuple[ProductRecord, Decimal]] = []
        self.registered_id: int | None = None
        self.setWindowTitle(TITLES[nature])
        self.resize(780, 620)

        self._types = [
            t
            for t in services.movements.list_types(include_inactive=False)
            if t.naturaleza == nature
        ]
        self._type = QComboBox()
        for movement_type in self._types:
            self._type.addItem(movement_type.nombre, movement_type.codigo)
        self._date = QDateEdit(QDate.currentDate())
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("yyyy-MM-dd")
        self._reference = QLineEdit()
        self._reference.setPlaceholderText("Factura, guía, orden…")
        self._reason = QLineEdit()
        self._reason.setPlaceholderText("Obligatorio para algunos tipos (p. ej. Pérdida)")

        header = QFormLayout()
        header.addRow("Tipo *", self._type)
        header.addRow("Fecha *", self._date)
        header.addRow("Documento", self._reference)
        header.addRow("Motivo", self._reason)

        self._picker = ProductPicker(services)
        self._quantity = QLineEdit()
        self._quantity.setPlaceholderText("Cantidad")
        self._quantity.setMaximumWidth(140)
        self._quantity.returnPressed.connect(self._add_line)
        add_button = QPushButton("Agregar línea")
        add_button.clicked.connect(self._add_line)
        entry_row = QHBoxLayout()
        entry_row.addWidget(self._picker, 1)
        entry_row.addWidget(self._quantity)
        entry_row.addWidget(add_button)

        self._model = TableModel(
            ["Código", "Producto", "Unidad", "Stock actual", "Cantidad"], right_aligned={3, 4}
        )
        self._table = make_table(self._model)
        remove_button = QPushButton("Quitar línea")
        remove_button.clicked.connect(self._remove_line)
        confirm_button = QPushButton("Confirmar movimiento")
        confirm_button.clicked.connect(self._confirm)
        cancel_button = QPushButton("Cancelar")
        cancel_button.setProperty("variant", "secondary")
        cancel_button.clicked.connect(self.reject)
        actions = QHBoxLayout()
        actions.addWidget(remove_button)
        actions.addStretch(1)
        actions.addWidget(cancel_button)
        actions.addWidget(confirm_button)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(QLabel("Líneas del movimiento"))
        layout.addLayout(entry_row)
        layout.addWidget(self._table, 1)
        layout.addLayout(actions)
        self.setLayout(layout)
        self._picker.focus_input()

    def _add_line(self) -> None:
        try:
            product = self._picker.product
            if product is None:
                raise ValidationError("Seleccione un producto.", code="PRODUCTO_REQUERIDO")
            quantity = parse_decimal_input(self._quantity.text(), "Cantidad", required=True)
            assert quantity is not None  # noqa: S101
            if quantity <= 0:
                raise ValidationError(
                    "La cantidad debe ser mayor que cero.", code="CANTIDAD_INVALIDA"
                )
            if not product.unidad_permite_decimales and quantity != quantity.to_integral_value():
                raise ValidationError(
                    "La unidad del producto no admite decimales.", code="CANTIDAD_INVALIDA"
                )
        except Exception as error:
            show_error(self, error)
            return
        for index, (existing, total) in enumerate(self._lines):
            if existing.id == product.id:
                self._lines[index] = (existing, total + quantity)
                break
        else:
            self._lines.append((product, quantity))
        self._refresh()
        self._picker.clear()
        self._quantity.clear()
        self._picker.focus_input()

    def _remove_line(self) -> None:
        index = selected_payload(self._table, self._model)
        if index is None:
            return
        del self._lines[index]
        self._refresh()

    def _refresh(self) -> None:
        self._model.set_rows(
            [
                [p.codigo, p.nombre, p.unidad, fmt_qty(p.cantidad), fmt_qty(q)]
                for p, q in self._lines
            ],
            payloads=list(range(len(self._lines))),
        )

    def _confirm(self) -> None:
        try:
            code = self._type.currentData()
            if code is None:
                raise ValidationError(
                    "No hay tipos de movimiento activos.", code="TIPO_MOVIMIENTO_INVALIDO"
                )
            request = MovementRequest(
                tipo_codigo=code,
                fecha=self._date.date().toPython(),
                lines=tuple(MovementLine(p.id, q) for p, q in self._lines),
                motivo=self._reason.text(),
                documento_referencia=self._reference.text(),
            )
            result = self._services.movements.register(request)
        except Exception as error:
            show_error(self, error)
            return
        self.registered_id = result.movimiento_id
        by_id = {p.id: p for p, _ in self._lines}
        summary = "\n".join(
            f"{by_id[pid].codigo}: {fmt_qty(before)} ? {fmt_qty(after)}"
            for pid, before, after in result.lines
        )
        QMessageBox.information(
            self, "Movimiento registrado", f"Movimiento #{result.movimiento_id}\n\n{summary}"
        )
        self.accept()


class AdjustDialog(QDialog):
    """Ajuste al stock contado (el sistema calcula la diferencia)."""

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self._services = services
        self.setWindowTitle("Ajustar inventario")
        self.setMinimumWidth(520)

        self._picker = ProductPicker(services)
        self._picker.changed.connect(self._show_current)
        self._current = QLabel("Stock actual: —")
        self._counted = QLineEdit()
        self._counted.setPlaceholderText("Stock contado")
        self._date = QDateEdit(QDate.currentDate())
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("yyyy-MM-dd")
        self._reason = QLineEdit()
        self._reason.setPlaceholderText("Obligatorio (p. ej. conteo físico)")

        form = QFormLayout()
        form.addRow("Producto *", self._picker)
        form.addRow("", self._current)
        form.addRow("Stock contado *", self._counted)
        form.addRow("Fecha *", self._date)
        form.addRow("Motivo *", self._reason)

        confirm = QPushButton("Aplicar ajuste")
        confirm.clicked.connect(self._confirm)
        cancel = QPushButton("Cancelar")
        cancel.setProperty("variant", "secondary")
        cancel.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(confirm)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def _show_current(self) -> None:
        product = self._picker.product
        self._current.setText(
            "Stock actual: —"
            if product is None
            else f"Stock actual: {fmt_qty(product.cantidad)} {product.unidad}"
        )

    def _confirm(self) -> None:
        try:
            product = self._picker.product
            if product is None:
                raise ValidationError("Seleccione un producto.", code="PRODUCTO_REQUERIDO")
            counted = parse_decimal_input(self._counted.text(), "Stock contado", required=True)
            assert counted is not None  # noqa: S101
            result = self._services.movements.adjust_to_count(
                product.id,
                counted,
                self._reason.text(),
                movement_date=self._date.date().toPython(),
            )
        except Exception as error:
            show_error(self, error)
            return
        if result is None:
            QMessageBox.information(self, "Ajuste", "El stock contado coincide con el actual.")
        else:
            _, before, after = result.lines[0]
            QMessageBox.information(
                self,
                "Ajuste registrado",
                f"Movimiento #{result.movimiento_id}\n{fmt_qty(before)} ? {fmt_qty(after)}",
            )
        self.accept()
