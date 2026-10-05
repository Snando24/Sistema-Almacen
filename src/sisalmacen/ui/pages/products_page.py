"""Listado de productos con búsqueda, filtros, paginación y acciones (S-04, S-05, S-06)."""

from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
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
    ALERT_AGOTADO,
    ALERT_BAJO_MINIMO,
    ALERT_CUALQUIERA,
    ALERT_LABELS,
    ProductData,
    ProductFilter,
    ProductRecord,
    normalize_alert_code,
)
from sisalmacen.ui.dialogs.product_dialog import ProductDetailDialog, ProductDialog, fill_combo
from sisalmacen.ui.exporting import export_report
from sisalmacen.ui.theme import current_theme_mode, THEME_DARK
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


def _get_alert_colors() -> dict[str, QColor]:
    """Devuelve colores de alerta adaptados al tema actual (claro/oscuro).
    
    Usa colores de Material Design que tienen buen contraste en ambos modos:
    - Modo claro: Colores pastel suave
    - Modo oscuro: Colores vibrantes y saturados para máximo contraste
    """
    is_dark = current_theme_mode() == THEME_DARK
    return {
        # Rojo: pastel en claro, vibrante en oscuro
        ALERT_AGOTADO: QColor("#d32f2f") if is_dark else QColor("#fde2e4"),
        # Naranja: pastel en claro, vibrante en oscuro
        ALERT_BAJO_MINIMO: QColor("#fb8c00") if is_dark else QColor("#fff3cd"),
    }


def _get_inactive_color() -> QColor:
    """Devuelve el color para productos inactivos adaptado al tema actual.
    
    - Modo claro: Gris suave
    - Modo oscuro: Gris más claro con buena legibilidad
    """
    is_dark = current_theme_mode() == THEME_DARK
    return QColor("#616161") if is_dark else QColor("#e5e5e2")


_ALERT_COLORS = _get_alert_colors()
_INACTIVE_COLOR = _get_inactive_color()


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

        # Columnas simplificadas: solo información esencial en la tabla
        # Categoría, Unidad, Precio, etc. se ven en el detalle del producto
        headers = ["Código", "Descripción", "Stock", "Mínimo", "Estado", "Alerta"]
        right = {2, 3}  # Stock y Mínimo alineados a la derecha
        self._model = TableModel(headers, right_aligned=right)
        self._table = make_table(self._model)
        self._table.doubleClicked.connect(lambda _index: self._detail())

        new_button = QPushButton("Nuevo producto")
        new_button.setEnabled("productos.crear" in permisos)
        new_button.clicked.connect(self._new)
        import_button = secondary_button("Importar CSV")
        import_button.setEnabled("importacion.ejecutar" in permisos)
        import_button.clicked.connect(self._import_csv)
        download_template = secondary_button("Descargar plantilla")
        download_template.setEnabled("productos.ver" in permisos)
        download_template.clicked.connect(self._download_template)
        set_minimum_button = secondary_button("Establecer stock mínimo")
        set_minimum_button.setEnabled("productos.editar" in permisos)
        set_minimum_button.clicked.connect(self._set_bulk_minimum)
        edit_button = QPushButton("Editar")
        edit_button.setEnabled("productos.editar" in permisos)
        edit_button.clicked.connect(self._edit)
        detail_button = secondary_button("Detalle e historial")
        detail_button.clicked.connect(self._detail)
        self._toggle_button = secondary_button("Desactivar / reactivar")
        self._toggle_button.setEnabled("productos.desactivar" in permisos)
        self._toggle_button.clicked.connect(self._toggle)

        export_button = QToolButton()
        export_button.setText("Exportar…")
        export_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        export_menu = QMenu(export_button)
        for fmt, label in (("csv", "CSV"), ("xlsx", "Excel"), ("pdf", "PDF")):
            action = export_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, f=fmt: self._export(f))
        export_button.setMenu(export_menu)
        export_button.setEnabled("exportar.datos" in permisos)

        actions = QHBoxLayout()
        actions.addWidget(new_button)
        actions.addWidget(import_button)
        actions.addWidget(download_template)
        actions.addWidget(set_minimum_button)
        actions.addWidget(edit_button)
        actions.addWidget(detail_button)
        actions.addWidget(self._toggle_button)
        actions.addStretch(1)
        actions.addWidget(export_button)

        self._prev = secondary_button("← Anterior")
        self._prev.clicked.connect(self._previous_page)
        self._next = secondary_button("Siguiente →")
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
        except Exception as error:
            show_error(self, error)

    def show_alert(self, alert: str | None) -> None:
        """Atajo desde el Dashboard (RF-073): filtra por alerta y muestra solo activos."""

        normalized = normalize_alert_code(alert)
        self._clear_filters(refresh=False)
        index = self._alert.findData(normalized)
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
            alerta=normalize_alert_code(self._alert.currentData()),
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
        # Recalcular colores según el tema actual
        alert_colors = _get_alert_colors()
        inactive_color = _get_inactive_color()
        for item in result.items:
            alert = item.alert()
            # Columnas simplificadas: Código, Descripción, Stock, Mínimo, Estado, Alerta
            row = [
                item.codigo,
                item.nombre,
                fmt_qty(item.cantidad),
                fmt_qty(item.stock_minimo) if item.stock_minimo is not None else "Sin configurar",
                "Activo" if item.activo else "Inactivo",
                ALERT_LABELS.get(alert or "", ""),
            ]
            rows.append(row)
            colors.append(
                alert_colors.get(alert or "") or (None if item.activo else inactive_color)
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

    def _import_csv(self) -> None:
        """Redirige al flujo oficial de importación CSV de productos."""

        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(self, "Importar productos", "", "CSV (*.csv)")
        if not filename:
            return
        main_window = self.window()
        if hasattr(main_window, "open_product_import"):
            main_window.open_product_import(filename)
            return
        QMessageBox.information(
            self,
            "Importar productos",
            "Abra la sección «Importación CSV» para validar y aplicar el archivo.",
        )

    def _download_template(self) -> None:
        """Descarga plantilla CSV para productos."""

        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Descargar plantilla", "", "CSV (*.csv)")
        if not filename:
            return
        try:
            csv_content = self._services.products.get_csv_template()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(csv_content)
            QMessageBox.information(self, "Plantilla descargada", f"Plantilla guardada en {filename}")
        except Exception as error:
            show_error(self, error)

    def _export(self, fmt: str) -> None:
        try:
            data = self._services.reports.products_listing(self._build_filter())
        except Exception as error:
            show_error(self, error)
            return
        export_report(self, self._services, data, fmt)

    @guarded
    def _set_bulk_minimum(self) -> None:
        """Abre diálogo para establecer stock mínimo de forma masiva."""
        dialog = BulkMinimumDialog(self._services, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()


class BulkMinimumDialog(QDialog):
    """Diálogo para establecer stock mínimo de forma masiva/general para productos."""

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Establecer stock mínimo")
        self.setMinimumWidth(400)
        self._services = services
        self._minimum_value = QLineEdit()

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        form.addRow(
            "Stock mínimo para TODOS los productos",
            self._minimum_value
        )
        
        info_label = QLabel(
            "Esta acción establecerá el stock mínimo indicado para TODOS los productos activos.\n"
            "Los productos inactivos no serán modificados."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 11px;")
        form.addRow(info_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Aplicar")
        ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.clicked.connect(self._apply)
        cancel = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel.setText("Cancelar")
        cancel.setProperty("variant", "secondary")
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _apply(self) -> None:
        try:
            minimum_text = self._minimum_value.text().strip()
            if not minimum_text:
                QMessageBox.warning(
                    self,
                    "Valor requerido",
                    "Por favor ingrese un valor para el stock mínimo.",
                )
                return
            
            minimum_value = parse_decimal_input(minimum_text, "Stock mínimo")
            
            # Confirmar antes de aplicar
            answer = QMessageBox.question(
                self,
                "Confirmar",
                f"¿Establecer el stock mínimo en {minimum_value} para TODOS los productos activos?\n\n"
                f"Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            if answer != QMessageBox.StandardButton.Ok:
                return
            
            # Obtener todos los productos activos
            result = self._services.products.search(
                ProductFilter(estado="ACTIVO"),
                page=1,
                page_size=50000,
            )
            
            # Actualizar cada producto
            updated_count = 0
            for product in result.items:
                data = ProductData(
                    codigo=product.codigo,
                    nombre=product.nombre,
                    categoria_id=product.categoria_id,
                    unidad_id=product.unidad_id,
                    codigo_barras=product.codigo_barras,
                    descripcion=product.descripcion,
                    marca_id=product.marca_id,
                    proveedor_id=product.proveedor_id,
                    ubicacion_id=product.ubicacion_id,
                    precio_compra=product.precio_compra,
                    precio_venta=product.precio_venta,
                    stock_minimo=minimum_value,
                    observaciones=product.observaciones,
                )
                self._services.products.update(product.id, data)
                updated_count += 1
            
            QMessageBox.information(
                self,
                "Stock mínimo actualizado",
                f"Se actualizó el stock mínimo para {updated_count} producto(s).",
            )
            self.accept()
        except Exception as error:
            show_error(self, error)
