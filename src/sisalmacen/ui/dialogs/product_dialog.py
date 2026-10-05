"""Alta/edición y detalle de productos."""

from __future__ import annotations

from html import escape
from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.application.settings import flag
from sisalmacen.domain.inventory import ALERT_LABELS, ALERT_BAJO_MINIMO, MovementFilter, ProductData, ProductRecord
from sisalmacen.ui.theme import apply_dialog_theme
from sisalmacen.ui.widgets import (
    TableModel,
    fmt_local,
    fmt_money,
    fmt_qty,
    make_table,
    parse_decimal_input,
    show_error,
)


def fill_combo(
    combo: QComboBox,
    entries: list[dict[str, Any]],
    *,
    label: str = "nombre",
    blank: str | None = None,
    keep_id: int | None = None,
    selected_id: int | None = None,
) -> None:
    """Llena un combo con ids como dato; incluye inactivos solo si es el valor actual."""

    combo.clear()
    if blank is not None:
        combo.addItem(blank, None)
    for entry in entries:
        if not entry.get("activo") and entry["id"] != keep_id:
            continue
        text = str(entry[label])
        if label == "codigo" and entry.get("nombre"):
            text = f"{entry['codigo']} - {entry['nombre']}"
        combo.addItem(text, entry["id"])
    if selected_id is not None:
        index = combo.findData(selected_id)
        if index >= 0:
            combo.setCurrentIndex(index)


class ProductDialog(QDialog):
    """Formulario de producto con validación en el caso de uso."""

    def __init__(
        self,
        services: AppServices,
        product: ProductRecord | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self._services = services
        self._product = product
        self.saved_id: int | None = None
        self.setWindowTitle("Editar producto" if product else "Nuevo producto")
        self.setMinimumWidth(520)

        catalogs = services.catalogs
        categories = catalogs.list_entries("categoria")
        units = catalogs.list_entries("unidad_medida")
        self._code = QLineEdit(product.codigo if product else "")
        self._code.setPlaceholderText("Opcional: se generará un ID interno si se deja vacío")
        self._name = QLineEdit(product.nombre if product else "")
        self._barcode = QLineEdit(product.codigo_barras or "" if product else "")
        self._category = QComboBox()
        fill_combo(
            self._category,
            categories,
            keep_id=product.categoria_id if product else None,
            selected_id=product.categoria_id if product else None,
        )
        self._unit = QComboBox()
        fill_combo(
            self._unit,
            units,
            label="codigo",
            keep_id=product.unidad_id if product else None,
            selected_id=product.unidad_id if product else None,
        )
        self._brand = QComboBox()
        fill_combo(
            self._brand,
            catalogs.list_entries("marca"),
            blank="(sin marca)",
            keep_id=product.marca_id if product else None,
            selected_id=product.marca_id if product else None,
        )
        self._supplier = QComboBox()
        fill_combo(
            self._supplier,
            catalogs.list_entries("proveedor"),
            blank="(sin proveedor)",
            keep_id=product.proveedor_id if product else None,
            selected_id=product.proveedor_id if product else None,
        )
        self._location = QComboBox()
        fill_combo(
            self._location,
            catalogs.list_entries("ubicacion"),
            label="codigo",
            blank="(sin ubicación)",
            keep_id=product.ubicacion_id if product else None,
            selected_id=product.ubicacion_id if product else None,
        )
        self._cost = QLineEdit(fmt_plain(product.precio_compra) if product else "")
        self._price = QLineEdit(fmt_plain(product.precio_venta) if product else "")
        self._minimum = QLineEdit(fmt_plain(product.stock_minimo) if product else "")
        self._description = QLineEdit(product.descripcion or "" if product else "")
        self._notes = QLineEdit(product.observaciones or "" if product else "")

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form.addRow("Código (opcional)", self._code)
        form.addRow("Descripción principal *", self._name)
        form.addRow("Categoría *", self._category)
        form.addRow("Unidad *", self._unit)
        form.addRow("Código de barras", self._barcode)
        form.addRow("Marca", self._brand)
        form.addRow("Proveedor", self._supplier)
        form.addRow("Ubicación", self._location)
        self._show_prices = "productos.ver_precios" in services.session.permisos and flag(
            services.settings.read_all(), "inventario.usar_precios", default=True
        )
        if self._show_prices:
            form.addRow("Precio de compra", self._cost)
            form.addRow("Precio de venta", self._price)
        form.addRow("Stock mínimo", self._minimum)
        form.addRow("Descripción adicional", self._description)
        form.addRow("Observaciones", self._notes)

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
        try:
            if self._category.currentData() is None or self._unit.currentData() is None:
                QMessageBox.information(
                    self,
                    "Datos incompletos",
                    "Cree al menos una categoría y una unidad en Catálogos antes de guardar.",
                )
                return
            data = ProductData(
                codigo=self._code.text(),
                nombre=self._name.text(),
                categoria_id=int(self._category.currentData()),
                unidad_id=int(self._unit.currentData()),
                codigo_barras=self._barcode.text(),
                descripcion=self._description.text(),
                marca_id=self._brand.currentData(),
                proveedor_id=self._supplier.currentData(),
                ubicacion_id=self._location.currentData(),
                precio_compra=parse_decimal_input(self._cost.text(), "Precio de compra"),
                precio_venta=parse_decimal_input(self._price.text(), "Precio de venta"),
                stock_minimo=parse_decimal_input(self._minimum.text(), "Stock mínimo"),
                observaciones=self._notes.text(),
            )
            if self._product is None:
                self.saved_id = self._services.products.create(data)
            else:
                self._services.products.update(self._product.id, data)
                self.saved_id = self._product.id
            
            # Verificar si el producto está bajo mínimo después de guardar
            saved_product = self._services.products.get(self.saved_id)
            alert = saved_product.alert()
            if alert == ALERT_BAJO_MINIMO:
                QMessageBox.warning(
                    self,
                    "⚠️ Stock bajo mínimo",
                    f"Producto: {saved_product.codigo}\n"
                    f"Stock actual: {saved_product.cantidad}\n"
                    f"Stock mínimo: {saved_product.stock_minimo}\n\n"
                    f"Este producto está por debajo del stock mínimo configurado.",
                )
        except Exception as error:
            show_error(self, error)
            return
        self.accept()


def fmt_plain(value: Any) -> str:
    return "" if value is None else format(value.normalize(), "f")


class ProductDetailDialog(QDialog):
    """Ficha del producto con su historial de movimientos (RF-033)."""

    def __init__(
        self, services: AppServices, product_id: int, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self.setWindowTitle("Detalle de producto")
        self.resize(900, 600)
        record = services.products.get(product_id)
        alert = record.alert()

        summary = QTextBrowser()
        summary.setMaximumHeight(210)
        rows = [
            ("Código", record.codigo),
            ("Descripción principal", record.nombre),
            ("Estado", "Activo" if record.activo else "Inactivo"),
            ("Categoría", record.categoria),
            ("Unidad", record.unidad),
            ("Código de barras", record.codigo_barras or ""),
            ("Marca", record.marca or ""),
            ("Proveedor", record.proveedor or ""),
            ("Ubicación", record.ubicacion or ""),
            ("Stock actual", f"{fmt_qty(record.cantidad)} {record.unidad}"),
            (
                "Stock mínimo",
                fmt_qty(record.stock_minimo)
                if record.stock_minimo is not None
                else "Sin configurar",
            ),
            ("Alerta", ALERT_LABELS.get(alert or "", "Sin alerta")),
            (
                "Precio compra / venta",
                f"{fmt_money(record.precio_compra)} / {fmt_money(record.precio_venta)}",
            ),
            ("Registrado", fmt_local(record.creado_en)),
            ("Actualizado", fmt_local(record.actualizado_en)),
        ]
        summary.setHtml(
            "<table cellpadding='3'>"
            + "".join(f"<tr><td><b>{escape(k)}</b></td><td>{escape(v)}</td></tr>" for k, v in rows)
            + "</table>"
        )

        model = TableModel(
            [
                "Fecha",
                "Tipo",
                "Cantidad",
                "Stock anterior",
                "Stock resultante",
                "Usuario",
                "Motivo",
            ],
            right_aligned={2, 3, 4},
        )
        history = services.movements.history(
            MovementFilter(producto_id=product_id), page=1, page_size=200
        )
        model.set_rows(
            [
                [
                    r.fecha_movimiento,
                    r.tipo_nombre,
                    fmt_qty(r.signo * r.cantidad),
                    fmt_qty(r.stock_anterior),
                    fmt_qty(r.stock_resultante),
                    r.usuario,
                    r.motivo or r.documento_referencia or "",
                ]
                for r in history.items
            ]
        )
        layout = QVBoxLayout()
        layout.addWidget(summary)
        layout.addWidget(QLabel(f"Historial de movimientos ({history.total})"))
        layout.addWidget(make_table(model), 1)
        self.setLayout(layout)
