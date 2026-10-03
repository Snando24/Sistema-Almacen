"""Reportes con filtros previos, vista previa y exportación (S-16)."""

from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.reports import REPORTS, ReportParams
from sisalmacen.application.services import AppServices
from sisalmacen.domain.inventory import ReportData
from sisalmacen.ui.dialogs.product_dialog import fill_combo
from sisalmacen.ui.exporting import export_report, preview_report
from sisalmacen.ui.pickers import ProductPicker
from sisalmacen.ui.widgets import (
    TableModel,
    build_page_header,
    fmt_money,
    fmt_qty,
    guarded,
    make_table,
    secondary_button,
    show_error,
)


def _format_cell(value: object, kind: str) -> str:
    from decimal import Decimal

    if value is None:
        return ""
    if isinstance(value, Decimal):
        return fmt_money(value) if kind == "money" else fmt_qty(value)
    return str(value)


class ReportsPage(QWidget):
    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportes-page")
        self._services = services
        self._data: ReportData | None = None
        permisos = services.session.permisos

        self._report = QComboBox()
        for key, title in REPORTS:
            self._report.addItem(title, key)
        self._category = QComboBox()
        self._picker = ProductPicker(services, only_active=False)
        self._type = QComboBox()
        self._from = QDateEdit(QDate.currentDate().addDays(-30))
        self._to = QDateEdit(QDate.currentDate())
        for edit in (self._from, self._to):
            edit.setCalendarPopup(True)
            edit.setDisplayFormat("yyyy-MM-dd")
        self._inactive = QCheckBox("Incluir productos inactivos")

        form = QFormLayout()
        form.addRow("Reporte", self._report)
        form.addRow("Categoría", self._category)
        form.addRow("Producto", self._picker)
        form.addRow("Tipo de movimiento", self._type)
        form.addRow("Desde", self._from)
        form.addRow("Hasta", self._to)
        form.addRow("", self._inactive)
        box = QGroupBox("Criterios")
        box.setLayout(form)

        generate = QPushButton("Generar")
        generate.clicked.connect(self._generate)
        self._buttons: list[QPushButton] = []
        actions = QHBoxLayout()
        actions.addWidget(generate)
        actions.addStretch(1)
        can_export = "exportar.datos" in permisos
        for label, handler in (
            ("Vista previa / imprimir", self._preview),
            ("CSV", lambda: self._export("csv")),
            ("Excel", lambda: self._export("xlsx")),
            ("PDF", lambda: self._export("pdf")),
        ):
            button = secondary_button(label)
            button.setEnabled(False)
            button.clicked.connect(lambda _c=False, h=handler: self._run_guarded(h))
            self._buttons.append(button)
            actions.addWidget(button)
        self._can_export = can_export

        self._info = QLabel("Elija un reporte, ajuste los criterios y pulse «Generar».")
        self._info.setWordWrap(True)
        self._model = TableModel([])
        self._table = make_table(self._model)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(
            build_page_header("Reportes", "Inventario, movimientos y valorización del almacén.")
        )
        layout.addWidget(box)
        layout.addLayout(actions)
        layout.addWidget(self._info)
        layout.addWidget(self._table, 1)
        self.setLayout(layout)
        self.reload_catalogs()

    def reload_catalogs(self) -> None:
        try:
            selected = self._category.currentData()
            fill_combo(
                self._category,
                self._services.catalogs.list_entries("categoria"),
                blank="Todas",
                selected_id=selected,
            )
            self._type.clear()
            self._type.addItem("Todos", None)
            for movement_type in self._services.movements.list_types():
                self._type.addItem(movement_type.nombre, movement_type.codigo)
        except Exception as error:
            show_error(self, error)

    def _run_guarded(self, handler: object) -> None:
        try:
            handler()  # type: ignore[operator]
        except Exception as error:
            show_error(self, error)

    @guarded
    def _generate(self) -> None:
        product = self._picker.product
        params = ReportParams(
            categoria_id=self._category.currentData(),
            producto_id=product.id if product else None,
            tipo_codigo=self._type.currentData(),
            fecha_desde=self._from.date().toPython(),
            fecha_hasta=self._to.date().toPython(),
            incluir_inactivos=self._inactive.isChecked(),
        )
        data = self._services.reports.build(self._report.currentData(), params)
        self._data = data
        right = {i for i, kind in enumerate(data.column_types) if kind in ("qty", "money", "int")}
        self._model = TableModel(data.headers, right_aligned=right)
        self._table.setModel(self._model)
        rows = [
            [_format_cell(v, k) for v, k in zip(row, data.column_types, strict=False)]
            for row in data.rows
        ]
        if data.totals is not None:
            rows.append(
                [_format_cell(v, k) for v, k in zip(data.totals, data.column_types, strict=False)]
            )
        self._model.set_rows(rows)
        self._info.setText(
            f"{data.title}: {len(data.rows)} fila(s)."
            + (f" Filtros: {' | '.join(data.filters)}" if data.filters else "")
        )
        for button in self._buttons:
            button.setEnabled(self._can_export)

    def _preview(self) -> None:
        if self._data is not None:
            preview_report(self, self._services, self._data)

    def _export(self, fmt: str) -> None:
        if self._data is not None:
            export_report(self, self._services, self._data, fmt)
