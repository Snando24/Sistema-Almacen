"""Historial de movimientos y registro de entradas, salidas y ajustes (S-08 a S-11)."""



from __future__ import annotations



from pathlib import Path

from PySide6.QtCore import Signal

from PySide6.QtWidgets import (

    QComboBox,

    QDialog,

    QGridLayout,

    QHBoxLayout,

    QInputDialog,

    QLabel,

    QLineEdit,

    QMessageBox,

    QPushButton,

    QVBoxLayout,

    QWidget,

)



from sisalmacen.application.services import AppServices

from sisalmacen.domain.errors import DomainError

from sisalmacen.domain.inventory import MovementFilter, MovementRow

from sisalmacen.ui.dialogs.movement_dialog import AdjustDialog, MovementDialog

from sisalmacen.ui.pickers import ProductPicker

from sisalmacen.ui.widgets import (

    TableModel,

    build_page_header,

    fmt_qty,

    guarded,

    make_table,

    parse_date_input,

    Worker,

    secondary_button,

    selected_payload,

    show_error,

)



PAGE_SIZE = 100





class MovementsPage(QWidget):

    changed = Signal()



    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:

        super().__init__(parent)

        self.setObjectName("movimientos-page")

        self._services = services

        permisos = services.session.permisos

        self._page = 1

        self._pages = 1

        self._worker: Worker | None = None



        self._picker = ProductPicker(services, only_active=False)

        self._type = QComboBox()

        self._date_from = QLineEdit()

        self._date_from.setPlaceholderText("Desde AAAA-MM-DD")

        self._date_to = QLineEdit()

        self._date_to.setPlaceholderText("Hasta AAAA-MM-DD")



        search_button = QPushButton("Buscar")

        search_button.clicked.connect(self._apply_filters)

        clear_button = secondary_button("Limpiar")

        clear_button.clicked.connect(self._clear_filters)

        filters = QGridLayout()

        filters.setSpacing(8)

        filters.addWidget(QLabel("Producto"), 0, 0)

        filters.addWidget(self._picker, 0, 1, 1, 3)

        filters.addWidget(self._type, 1, 0, 1, 2)

        filters.addWidget(self._date_from, 1, 2)

        filters.addWidget(self._date_to, 1, 3)

        filters.addWidget(search_button, 1, 4)

        filters.addWidget(clear_button, 1, 5)



        entry_button = QPushButton("Registrar entrada")

        entry_button.setEnabled("movimientos.entrada" in permisos)

        entry_button.clicked.connect(lambda _c=False: self._register("ENTRADA"))

        exit_button = QPushButton("Registrar salida")

        exit_button.setEnabled("movimientos.salida" in permisos)

        exit_button.clicked.connect(lambda _c=False: self._register("SALIDA"))

        adjust_button = QPushButton("Ajustar inventario")

        adjust_button.setEnabled("movimientos.ajuste" in permisos)

        adjust_button.clicked.connect(self._adjust)

        import_button = secondary_button("Importar CSV")

        import_button.setEnabled(
            any(
                permiso in permisos
                for permiso in ("movimientos.entrada", "movimientos.salida", "movimientos.ajuste")
            )
        )

        import_button.clicked.connect(self._import_csv)

        download_template = secondary_button("Descargar plantilla")

        download_template.setEnabled("inventario.ver" in permisos)

        download_template.clicked.connect(self._download_template)

        correct_button = secondary_button("Corregir movimiento")

        correct_button.setEnabled(

            "movimientos.ajuste" in permisos and services.session.rol_codigo == "ADMIN"

        )

        correct_button.clicked.connect(self._correct)

        actions = QHBoxLayout()

        for button in (entry_button, exit_button, adjust_button):

            actions.addWidget(button)

        actions.addWidget(import_button)

        actions.addWidget(download_template)

        actions.addStretch(1)

        actions.addWidget(correct_button)



        self._model = TableModel(

            [

                "N.º",

                "Fecha",

                "Tipo",

                "Código",

                "Producto",

                "Cantidad",

                "Stock anterior",

                "Stock resultante",

                "Usuario",

                "Motivo / documento",

                "Corrige a",

            ],

            right_aligned={5, 6, 7},

        )

        self._table = make_table(self._model)



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

            build_page_header("Movimientos", "Entradas, salidas y ajustes; historial completo.")

        )

        layout.addLayout(filters)

        layout.addLayout(actions)

        layout.addWidget(self._table, 1)

        layout.addLayout(pager)

        self.setLayout(layout)



        self._load_types()

        self.refresh()



    def _load_types(self) -> None:

        self._type.clear()

        self._type.addItem("Todos los tipos", None)

        try:

            for movement_type in self._services.movements.list_types():

                self._type.addItem(movement_type.nombre, movement_type.codigo)

        except Exception as error:

            show_error(self, error)



    def reload_types(self) -> None:

        selected = self._type.currentData()

        self._load_types()

        index = self._type.findData(selected)

        if index >= 0:

            self._type.setCurrentIndex(index)



    def _build_filter(self) -> MovementFilter:

        product = self._picker.product

        return MovementFilter(

            producto_id=product.id if product else None,

            tipo_codigo=self._type.currentData(),

            fecha_desde=parse_date_input(self._date_from.text(), "Desde"),

            fecha_hasta=parse_date_input(self._date_to.text(), "Hasta"),

        )



    def refresh(self) -> None:

        try:

            result = self._services.movements.history(

                self._build_filter(), page=self._page, page_size=PAGE_SIZE

            )

        except Exception as error:

            show_error(self, error)

            return

        self._pages = result.pages

        self._model.set_rows(

            [

                [

                    str(r.movimiento_id),

                    r.fecha_movimiento,

                    r.tipo_nombre,

                    r.producto_codigo,

                    r.producto_nombre,

                    fmt_qty(r.signo * r.cantidad),

                    fmt_qty(r.stock_anterior),

                    fmt_qty(r.stock_resultante),

                    r.usuario,

                    r.motivo or r.documento_referencia or "",

                    "" if r.movimiento_origen_id is None else f"#{r.movimiento_origen_id}",

                ]

                for r in result.items

            ],

            payloads=list(result.items),

        )

        self._status.setText(

            f"Página {result.page} de {self._pages} · {result.total} línea(s)"

            if result.total

            else "Sin movimientos"

        )

        self._prev.setEnabled(result.page > 1)

        self._next.setEnabled(result.page < self._pages)



    @guarded

    def _apply_filters(self) -> None:

        self._build_filter()

        self._page = 1

        self.refresh()



    @guarded

    def _clear_filters(self) -> None:

        self._picker.clear()

        self._type.setCurrentIndex(0)

        self._date_from.clear()

        self._date_to.clear()

        self._page = 1

        self.refresh()



    @guarded

    def _previous_page(self) -> None:

        self._page = max(1, self._page - 1)

        self.refresh()



    @guarded

    def _next_page(self) -> None:

        self._page = min(self._pages, self._page + 1)

        self.refresh()



    def start_register(self, nature: str) -> None:

        """Abre el registro de entrada/salida (acceso rápido del Dashboard)."""



        self._register(nature)



    def _register(self, nature: str) -> None:

        try:

            dialog = MovementDialog(self._services, nature, parent=self)

        except Exception as error:

            show_error(self, error)

            return

        if dialog.exec() == QDialog.DialogCode.Accepted:

            self.refresh()

            self.changed.emit()



    @guarded

    def _adjust(self) -> None:

        if AdjustDialog(self._services, parent=self).exec() == QDialog.DialogCode.Accepted:

            self.refresh()

            self.changed.emit()

    def _import_csv(self) -> None:
        """Abre diálogo para importar movimientos desde CSV."""

        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getOpenFileName(self, "Importar movimientos", "", "CSV (*.csv)")
        if not filename:
            return
        self._run_worker(
            lambda progress: self._services.movements.import_csv_file(
                Path(filename), progress=progress
            ),
            self._on_import_finished,
        )

    def _download_template(self) -> None:
        """Descarga plantilla CSV para movimientos."""

        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Descargar plantilla", "", "CSV (*.csv)")
        if not filename:
            return
        try:
            csv_content = self._services.movements.get_csv_template()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(csv_content)
            QMessageBox.information(self, "Plantilla descargada", f"Plantilla guardada en {filename}")
        except Exception as error:
            show_error(self, error)

    def _run_worker(self, task, on_success) -> None:  # type: ignore[no-untyped-def]
        if self._worker is not None:
            QMessageBox.information(self, "Movimientos", "Ya hay una operación en curso.")
            return
        self._worker = Worker(task)
        self._worker.succeeded.connect(on_success)
        self._worker.failed.connect(self._on_worker_failed)
        self._worker.finished.connect(self._release_worker)
        self.setEnabled(False)
        self._worker.start()

    def _release_worker(self) -> None:
        self.setEnabled(True)
        if self._worker is not None:
            self._worker.deleteLater()
        self._worker = None

    def _on_worker_failed(self, error: object) -> None:
        if isinstance(error, BaseException):
            if isinstance(error, DomainError):
                show_error(self, error)
                return
            show_error(self, error)

    def _on_import_finished(self, result: object) -> None:
        if not isinstance(result, dict):
            return
        QMessageBox.information(
            self,
            "Importación completada",
            f"Movimientos creados: {result.get('created', 0)}\nErrores: {result.get('errors', 0)}",
        )
        self.refresh()
        self.changed.emit()

    @guarded

    def _correct(self) -> None:

        row: MovementRow | None = selected_payload(self._table, self._model)

        if row is None:

            QMessageBox.information(self, "Corregir", "Seleccione una línea del movimiento.")

            return

        reason, accepted = QInputDialog.getText(

            self,

            "Corregir movimiento",

            f"Motivo de la corrección del movimiento #{row.movimiento_id}:",

        )

        if not accepted:

            return

        result = self._services.movements.correct(row.movimiento_id, reason)

        QMessageBox.information(

            self,

            "Corrección registrada",

            f"Se creó el movimiento compensatorio #{result.movimiento_id}.",

        )

        self.refresh()

        self.changed.emit()

