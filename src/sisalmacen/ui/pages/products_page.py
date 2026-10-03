"""Listado de productos con búsqueda, filtros, paginación y acciones (S-04, S-05, S-06)."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.application.settings import flag
from sisalmacen.domain.inventory import (
    ALERT_BAJO_MINIMO,
    ALERT_CUALQUIERA,
    ALERT_LABELS,
    ALERT_SIN_STOCK,
    ALERT_SOBRE_MAXIMO,
    ProductFilter,
    ProductRecord,
)
from sisalmacen.ui.dialogs.product_dialog import ProductDetailDialog, ProductDialog, fill_combo
from sisalmacen.ui.exporting import export_report
from sisalmacen.ui.widgets import (
    TableModel,
    build_page_header,
    fmt_money,
    fmt_qty,
    guarded,
    make_table,
    parse_date_input,
    parse_decimal_input,
    secondary_button,
    selected_payload,
    show_error,
)

PAGE_SIZE = 50
_ALERT_COLORS = {
    ALERT_SIN_STOCK: QColor("#fde2e4"),
    ALERT_BAJO_MINIMO: QColor("#fff3cd"),
    ALERT_SOBRE_MAXIMO: QColor("#dbeafe"),
}
_INACTIVE_COLOR = QColor("#e5e5e2")


class ProductsPage(QWidget):
    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("productos-page")
        self._services = services
        permisos = services.session.permisos
        self._page = 1
        self._pages = 1
        self._show_prices = "productos.ver_precios" in permisos
        self._use_max = True

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar por código, nombre o código de barras")
        self._search.returnPressed.connect(self._apply_filters)
        self._state = QComboBox()
        for label, value in (("Activos", "ACTIVO"), ("Inactivos", "INACTIVO"), ("Todos", None)):
            self._state.addItem(label, value)
        self._alert = QComboBox()
        self._alert.addItem("Cualquier alerta/ninguna", None)
        self._alert.addItem("Con alguna alerta", ALERT_CUALQUIERA)
        for code, label in ALERT_LABELS.items():
            self._alert.addItem(label, code)
        self._category = QComboBox()
        self._brand = QComboBox()
        self._supplier = QComboBox()
        self._location = QComboBox()
        self._price_from = QLineEdit()
        self._price_to = QLineEdit()
        self._date_from = QLineEdit()
        self._date_to = QLineEdit()
        for edit, hint in (
            (self._price_from, "Precio venta desde"),
            (self._price_to, "Precio venta hasta"),
            (self._date_from, "Registrado desde AAAA-MM-DD"),
            (self._date_to, "Registrado hasta AAAA-MM-DD"),
        ):
            edit.setPlaceholderText(hint)

        filters = QGridLayout()
        filters.setSpacing(8)
        filters.addWidget(self._search, 0, 0, 1, 3)
        filters.addWidget(self._state, 0, 3)
        filters.addWidget(self._alert, 0, 4)
        filters.addWidget(self._category, 1, 0)
        filters.addWidget(self._brand, 1, 1)
        filters.addWidget(self._supplier, 1, 2)
        filters.addWidget(self._location, 1, 3, 1, 2)
        if self._show_prices:
            filters.addWidget(self._price_from, 2, 0)
            filters.addWidget(self._price_to, 2, 1)
        filters.addWidget(self._date_from, 2, 2)
        filters.addWidget(self._date_to, 2, 3)
        search_button = QPushButton("Buscar")
        search_button.clicked.connect(self._apply_filters)
        clear_button = secondary_button("Limpiar filtros")
        clear_button.clicked.connect(lambda _checked=False: self._clear_filters())
        filters.addWidget(search_button, 2, 4)
        filters.addWidget(clear_button, 3, 4)

        headers = ["Código", "Descripción", "Categoría", "Unidad", "Stock", "Mínimo"]
        right = {4, 5}
        if self._show_prices:
            headers.append("P. venta")
            right.add(6)
        headers += ["Estado", "Alerta"]
        self._model = TableModel(headers, right_aligned=right)
        self._table = make_table(self._model)
        self._table.doubleClicked.connect(lambda _index: self._detail())

        new_button = QPushButton("Nuevo producto")
        new_button.setEnabled("productos.crear" in permisos)
        new_button.clicked.connect(self._new)
        edit_button = QPushButton("Editar")
        edit_button.setEnabled("productos.editar" in permisos)
        edit_button.clicked.connect(self._edit)
        detail_button = secondary_button("Detalle e historial")
        detail_button.clicked.connect(self._detail)
        self._toggle_button = secondary_button("Desactivar / reactivar")
        self._toggle_button.setEnabled("productos.desactivar" in permisos)
        self._toggle_button.clicked.connect(self._toggle)

        export_button = QToolButton()
        export_button.setText("Exportar ?")
        export_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        export_menu = QMenu(export_button)
        for fmt, label in (("csv", "CSV"), ("xlsx", "Excel"), ("pdf", "PDF")):
            action = export_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, f=fmt: self._export(f))
        export_button.setMenu(export_menu)
        export_button.setEnabled("exportar.datos" in permisos)

        actions = QHBoxLayout()
        actions.addWidget(new_button)
        actions.addWidget(edit_button)
        actions.addWidget(detail_button)
        actions.addWidget(self._toggle_button)
        actions.addStretch(1)
        actions.addWidget(export_button)

        self._prev = secondary_button("? Anterior")
        self._prev.clicked.connect(self._previous_page)
        self._next = secondary_button("Siguiente ?")
        self._next.clicked.connect(self._next_page)
        self._status = QLabel("")
        pager = QHBoxLayout()
        pager.addWidget(self._prev)
        pager.addWidget(self._next)
        pager.addWidget(self._status, 1)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(
            build_page_header("Productos", "Catálogo de productos, stock y alertas de inventario.")
        )
        layout.addLayout(filters)
        layout.addLayout(actions)
        layout.addWidget(self._table, 1)
        layout.addLayout(pager)
        self.setLayout(layout)

        self.reload_catalogs()
        self.refresh()

    # ----- datos -----

    def reload_catalogs(self) -> None:
        try:
            catalogs = self._services.catalogs
            for combo, kind, label, blank in (
                (self._category, "categoria", "nombre", "Todas las categorías"),
                (self._brand, "marca", "nombre", "Todas las marcas"),
                (self._supplier, "proveedor", "nombre", "Todos los proveedores"),
                (self._location, "ubicacion", "codigo", "Todas las ubicaciones"),
            ):
                selected = combo.currentData()
                fill_combo(
                    combo,
                    catalogs.list_entries(kind),
                    label=label,
                    blank=blank,
                    selected_id=selected,
                )
            self._use_max = flag(
                self._services.settings.read_all(), "inventario.usar_stock_maximo", default=False
            )
        except Exception as error:
            show_error(self, error)

    def show_alert(self, alert: str | None) -> None:
        """Atajo desde el Dashboard (RF-073): filtra por alerta y muestra solo activos."""

        self._clear_filters(refresh=False)
        index = self._alert.findData(alert)
        if index >= 0:
            self._alert.setCurrentIndex(index)
        self._apply_filters()

    def _build_filter(self) -> ProductFilter:
        return ProductFilter(
            texto=self._search.text(),
            categoria_id=self._category.currentData(),
            marca_id=self._brand.currentData(),
            proveedor_id=self._supplier.currentData(),
            ubicacion_id=self._location.currentData(),
            estado=self._state.currentData(),
            alerta=self._alert.currentData(),
            precio_desde=parse_decimal_input(self._price_from.text(), "Precio desde"),
            precio_hasta=parse_decimal_input(self._price_to.text(), "Precio hasta"),
            registrado_desde=parse_date_input(self._date_from.text(), "Registrado desde"),
            registrado_hasta=parse_date_input(self._date_to.text(), "Registrado hasta"),
        )

    def refresh(self) -> None:
        try:
            result = self._services.products.search(
                self._build_filter(), page=self._page, page_size=PAGE_SIZE
            )
        except Exception as error:
            show_error(self, error)
            return
        self._pages = result.pages
        rows: list[list[str]] = []
        colors: list[QColor | None] = []
        for item in result.items:
            alert = item.alert(usar_stock_maximo=self._use_max)
            row = [
                item.codigo,
                item.nombre,
                item.categoria,
                item.unidad,
                fmt_qty(item.cantidad),
                fmt_qty(item.stock_minimo) if item.stock_minimo is not None else "Sin configurar",
            ]
            if self._show_prices:
                row.append(fmt_money(item.precio_venta))
            row += ["Activo" if item.activo else "Inactivo", ALERT_LABELS.get(alert or "", "")]
            rows.append(row)
            colors.append(
                _ALERT_COLORS.get(alert or "") or (None if item.activo else _INACTIVE_COLOR)
            )
        self._model.set_rows(rows, payloads=list(result.items), colors=colors)
        self._status.setText(
            f"Página {result.page} de {self._pages} · {result.total} producto(s)"
            if result.total
            else "Sin resultados"
        )
        self._prev.setEnabled(result.page > 1)
        self._next.setEnabled(result.page < self._pages)

    # ----- filtros y paginación -----

    @guarded
    def _apply_filters(self) -> None:
        self._build_filter()  # valida entradas antes de consultar
        self._page = 1
        self.refresh()

    def _clear_filters(self, *, refresh: bool = True) -> None:
        for edit in (
            self._search,
            self._price_from,
            self._price_to,
            self._date_from,
            self._date_to,
        ):
            edit.clear()
        for combo in (self._category, self._brand, self._supplier, self._location, self._alert):
            combo.setCurrentIndex(0)
        self._state.setCurrentIndex(0)
        self._page = 1
        if refresh:
            self.refresh()

    @guarded
    def _previous_page(self) -> None:
        self._page = max(1, self._page - 1)
        self.refresh()

    @guarded
    def _next_page(self) -> None:
        self._page = min(self._pages, self._page + 1)
        self.refresh()

    # ----- acciones -----

    def _selected(self) -> ProductRecord | None:
        record = selected_payload(self._table, self._model)
        if record is None:
            QMessageBox.information(self, "Productos", "Seleccione un producto.")
        return record

    @guarded
    def _new(self) -> None:
        self.reload_catalogs()
        if ProductDialog(self._services, parent=self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def start_new(self) -> None:
        """Abre el alta de producto (acceso rápido del Dashboard)."""

        self._new()

    @guarded
    def _edit(self) -> None:
        record = self._selected()
        if record is None:
            return
        full = self._services.products.get(record.id)
        if ProductDialog(self._services, full, parent=self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    @guarded
    def _detail(self) -> None:
        record = self._selected()
        if record is not None:
            ProductDetailDialog(self._services, record.id, parent=self).exec()

    @guarded
    def _toggle(self) -> None:
        record = self._selected()
        if record is None:
            return
        if record.activo:
            answer = QMessageBox.question(
                self,
                "Desactivar producto",
                f"¿Desactivar {record.codigo}? El historial se conserva.",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            self._services.products.deactivate(record.id)
        else:
            self._services.products.reactivate(record.id)
        self.refresh()

    def _export(self, fmt: str) -> None:
        try:
            data = self._services.reports.products_listing(self._build_filter())
        except Exception as error:
            show_error(self, error)
            return
        export_report(self, self._services, data, fmt)
