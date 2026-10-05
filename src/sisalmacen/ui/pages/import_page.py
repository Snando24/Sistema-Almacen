"""Importación CSV: opciones, vista previa, aplicación con progreso e historial (S-12 a S-15)."""



from __future__ import annotations



from pathlib import Path

from typing import Any



from PySide6.QtCore import Signal

from PySide6.QtGui import QColor

from PySide6.QtWidgets import (

    QCheckBox,

    QComboBox,

    QDialog,

    QFileDialog,

    QFormLayout,

    QGroupBox,

    QHBoxLayout,

    QLabel,

    QLineEdit,

    QMessageBox,

    QProgressBar,

    QPushButton,

    QSizePolicy,

    QTabWidget,

    QVBoxLayout,

    QWidget,

)



from sisalmacen.application.services import AppServices

from sisalmacen.domain.errors import DomainError

from sisalmacen.domain.importing import (

    ACTION_ERROR,

    ImportDetail,

    ImportOptions,

    ImportPreview,

    ImportRecord,

)

from sisalmacen.ui.exporting import write_csv_rows

from sisalmacen.ui.widgets import (

    TableModel,

    Worker,

    build_page_header,

    fmt_local,

    guarded,

    make_table,

    secondary_button,

    selected_payload,

    show_error,

)



MAX_PREVIEW_ROWS = 3000

_ERROR_COLOR = QColor("#fde2e4")

_ACTION_LABELS = {

    "INSERTAR": "Alta",

    "ACTUALIZAR": "Actualización",

    "SIN_CAMBIOS": "Sin cambios",

    "ERROR": "Error",

}





class ImportPage(QWidget):

    changed = Signal()



    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:

        super().__init__(parent)

        self.setObjectName("csv-page")

        self._services = services

        self._permisos = services.session.permisos

        self._preview: ImportPreview | None = None

        self._import_id: int | None = None

        self._options: ImportOptions | None = None

        self._has_errors = False

        self._worker: Worker | None = None

        self._on_success: Any = None



        tabs = QTabWidget()

        tabs.addTab(self._build_import_tab(), "Importar")

        self._history_tab = self._build_history_tab()

        tabs.addTab(self._history_tab, "Historial")

        tabs.currentChanged.connect(lambda index: self._refresh_history() if index == 1 else None)



        layout = QVBoxLayout()

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(10)

        layout.addWidget(

            build_page_header(

                "Importación CSV",

                "Validar, previsualizar, confirmar y aplicar en una sola transacción.",

            )

        )

        layout.addWidget(tabs, 1)

        self.setLayout(layout)

        self._update_buttons()



    # ----- construcción -----



    def _build_import_tab(self) -> QWidget:

        self._path = QLineEdit()

        self._path.setReadOnly(True)

        self._path.setPlaceholderText("Seleccione un archivo .csv")

        browse = secondary_button("Examinar…")

        browse.clicked.connect(self._browse)

        file_row = QHBoxLayout()

        file_row.addWidget(self._path, 1)

        file_row.addWidget(browse)



        self._encoding = QComboBox()

        for label, value in (("Automática", None), ("UTF-8", "utf-8"), ("Windows-1252", "cp1252")):

            self._encoding.addItem(label, value)

        self._delimiter = QComboBox()

        for label, value in (

            ("Automático", None),

            ("Coma ( , )", ","),

            ("Punto y coma ( ; )", ";"),

            ("Tabulador", "\t"),

            ("Barra ( | )", "|"),

        ):

            self._delimiter.addItem(label, value)

        self._decimal = QComboBox()

        self._decimal.addItem("Punto ( . )", ".")

        self._decimal.addItem("Coma ( , )", ",")

        self._mode = QComboBox()

        for label, value in (

            ("Insertar y actualizar", "INSERTAR_ACTUALIZAR"),

            ("Solo insertar", "INSERTAR"),

            ("Solo actualizar", "ACTUALIZAR"),

        ):

            self._mode.addItem(label, value)



        self._create_missing = QCheckBox("Crear catálogos faltantes (categoría, marca, proveedor, ubicación)")

        self._create_missing.setEnabled("catalogos.gestionar" in self._permisos)

        self._apply_stock = QCheckBox("Aplicar stock de la columna «stock» (genera movimientos)")

        self._apply_stock.setEnabled("movimientos.ajuste" in self._permisos)

        self._skip_errors = QCheckBox("Omitir filas con error y aplicar las válidas (solo administrador)")

        self._skip_errors.setEnabled(self._services.session.rol_codigo == "ADMIN")



        form = QFormLayout()

        form.addRow("Archivo", file_row)

        form.addRow("Codificación", self._encoding)

        form.addRow("Separador", self._delimiter)

        form.addRow("Decimal", self._decimal)

        form.addRow("Modo", self._mode)

        options_box = QGroupBox("Opciones")

        options_layout = QVBoxLayout()

        options_layout.addLayout(form)

        options_layout.addWidget(self._create_missing)

        options_layout.addWidget(self._apply_stock)

        options_layout.addWidget(self._skip_errors)

        options_box.setLayout(options_layout)



        self._validate_button = QPushButton("Validar archivo")

        self._validate_button.clicked.connect(self._validate)

        self._errors_button = secondary_button("Exportar errores")

        self._errors_button.clicked.connect(self._export_errors)

        self._apply_button = QPushButton("Aplicar importación")

        self._apply_button.clicked.connect(self._apply)

        self._discard_button = secondary_button("Descartar")

        self._discard_button.clicked.connect(self._discard)

        buttons = QHBoxLayout()

        buttons.addWidget(self._validate_button)

        buttons.addWidget(self._errors_button)

        buttons.addStretch(1)

        buttons.addWidget(self._discard_button)

        buttons.addWidget(self._apply_button)



        self._progress = QProgressBar()

        self._progress.setVisible(False)

        self._summary = QLabel("Seleccione un archivo y pulse «Validar archivo».")

        self._summary.setWordWrap(True)

        self._warnings = QLabel("")

        self._warnings.setWordWrap(True)

        self._warnings.setStyleSheet("color: #9e0f18; font-weight: 600;")

        self._model = TableModel(["Fila", "Código", "Acción", "Detalle"])

        self._table = make_table(self._model)
        
        # Configurar tamaño y política de la tabla para soporte de contenido variable
        self._table.setMinimumHeight(200)
        self._table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Crear un contenedor para la previsualización con bordes claros
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self._summary)
        preview_layout.addWidget(self._warnings)
        preview_layout.addWidget(self._table, 1)  # La tabla se expande para llenar espacio disponible

        preview_box = QGroupBox("Previsualización de validación")
        preview_box.setLayout(preview_layout)
        preview_box.setMinimumHeight(250)  # Asegurar altura mínima para el grupo

        widget = QWidget()

        layout = QVBoxLayout()

        layout.addWidget(options_box)

        layout.addLayout(buttons)

        layout.addWidget(self._progress)

        layout.addWidget(preview_box, 1)  # preview_box se expande para llenar espacio disponible

        widget.setLayout(layout)

        return widget



    def _build_history_tab(self) -> QWidget:

        self._history_model = TableModel(

            [

                "N.º",

                "Archivo",

                "Inicio",

                "Modo",

                "Estado",

                "Filas",

                "Con error",

                "Insertados",

                "Actualizados",

                "Rechazados",

            ],

            right_aligned={5, 6, 7, 8, 9},

        )

        self._history_table = make_table(self._history_model)

        errors_button = secondary_button("Ver errores")

        errors_button.clicked.connect(self._show_history_errors)

        refresh_button = secondary_button("Actualizar")

        refresh_button.clicked.connect(self._refresh_history)

        bar = QHBoxLayout()

        bar.addWidget(errors_button)

        bar.addWidget(refresh_button)

        bar.addStretch(1)

        widget = QWidget()

        layout = QVBoxLayout()

        layout.addLayout(bar)

        layout.addWidget(self._history_table, 1)

        widget.setLayout(layout)

        return widget



    # ----- estado -----



    def _update_buttons(self) -> None:

        busy = self._worker is not None

        can_run = "importacion.ejecutar" in self._permisos

        has_preview = self._import_id is not None

        self._validate_button.setEnabled(can_run and not busy)

        self._errors_button.setEnabled(has_preview and self._has_errors and not busy)

        self._apply_button.setEnabled(has_preview and can_run and not busy)

        self._discard_button.setEnabled(has_preview and not busy)


    def prepare_product_import(self, path: str | None = None) -> None:
        """Prepara la pantalla para importar productos desde otras vistas."""

        self._reset_preview()
        self._summary.setText("Seleccione un archivo y pulse «Validar archivo».")
        if path:
            self._path.setText(path)


    def _read_options(self) -> ImportOptions:

        return ImportOptions(

            mode=self._mode.currentData(),

            encoding=self._encoding.currentData(),

            delimiter=self._delimiter.currentData(),

            decimal_separator=self._decimal.currentData(),

            create_missing_catalogs=self._create_missing.isChecked(),

            apply_stock=self._apply_stock.isChecked(),

            skip_error_rows=self._skip_errors.isChecked(),

        )



    def _run(self, task: Any, on_success: Any) -> None:

        worker = Worker(task)

        self._worker = worker

        self._on_success = on_success

        self._progress.setRange(0, 0)

        self._progress.setVisible(True)

        worker.progressed.connect(self._on_progress)

        worker.succeeded.connect(self._on_worker_succeeded)

        worker.failed.connect(self._on_failure)

        self._update_buttons()

        worker.start()



    def _on_progress(self, done: int, total: int) -> None:

        self._progress.setRange(0, max(total, 1))

        self._progress.setValue(done)



    def _release_worker(self) -> None:

        if self._worker is not None:

            self._worker.wait()

            self._worker.deleteLater()

        self._worker = None

        self._progress.setVisible(False)



    def _on_worker_succeeded(self, result: object) -> None:

        self._release_worker()

        self._update_buttons()

        try:

            self._on_success(result)

        except Exception as error:

            show_error(self, error)



    def _on_failure(self, error: object) -> None:

        self._release_worker()

        self._update_buttons()

        if isinstance(error, DomainError) and error.code == "IMPORT_DESACTUALIZADA":

            QMessageBox.warning(self, "Vista previa desactualizada", error.message)

            self._show_stored()

            return

        if isinstance(error, BaseException):

            show_error(self, error)



    # ----- acciones -----



    @guarded

    def _browse(self) -> None:

        chosen, _ = QFileDialog.getOpenFileName(

            self, "Seleccionar CSV", "", "Archivos CSV (*.csv *.txt);;Todos (*.*)"

        )

        if chosen:

            self._path.setText(chosen)



    @guarded

    def _validate(self) -> None:

        if not self._path.text():

            QMessageBox.information(self, "Importación", "Seleccione un archivo CSV.")

            return

        path = Path(self._path.text())

        options = self._read_options()

        self._options = options

        self._summary.setText("Validando archivo…")

        self._run(

            lambda _progress: self._services.imports.validate(path, options), self._on_validated

        )



    def _on_validated(self, preview: ImportPreview) -> None:

        self._preview = preview

        self._import_id = preview.importacion_id

        self._has_errors = preview.errores > 0

        self._summary.setText(

            f"Archivo: {preview.archivo} · Total: {preview.total} · Altas: {preview.nuevas} · "

            f"Actualizaciones: {preview.actualizables} · Sin cambios: {preview.sin_cambios} · "

            f"Con error: {preview.errores}"

        )

        notes = list(preview.warnings)

        if preview.repetido is not None:

            notes.append(

                f"Este archivo ya fue aplicado el {fmt_local(preview.repetido.finalizado_en)} "

                f"(importación #{preview.repetido.id})."

            )

        if preview.total > MAX_PREVIEW_ROWS:

            notes.append(f"Se muestran las primeras {MAX_PREVIEW_ROWS} filas.")

        self._warnings.setText("\n".join(notes))

        rows: list[list[str]] = []

        colors: list[QColor | None] = []

        for result in preview.rows[:MAX_PREVIEW_ROWS]:

            rows.append(

                [

                    str(result.nro_fila),

                    result.codigo,

                    _ACTION_LABELS.get(result.accion, result.accion),

                    "; ".join(f"{e.code} {e.column}: {e.message}" for e in result.errors),

                ]

            )

            colors.append(_ERROR_COLOR if result.accion == ACTION_ERROR else None)

        self._model.set_rows(rows, colors=colors)

        self._update_buttons()



    def _show_stored(self) -> None:

        """Reconstruye la vista previa desde lo guardado (tras una re-validación)."""



        if self._import_id is None:

            return

        try:

            record = next(

                r for r in self._services.imports.history() if r.id == self._import_id

            )

            details = self._services.imports.details(self._import_id)

        except Exception as error:

            show_error(self, error)

            return

        self._has_errors = record.filas_error > 0

        self._summary.setText(

            f"Total: {record.total_filas} · Altas: {record.filas_nuevas} · "

            f"Actualizaciones: {record.filas_actualizables} · Con error: {record.filas_error}"

        )

        self._warnings.setText("")

        self._model.set_rows(

            [_detail_row(d) for d in details[:MAX_PREVIEW_ROWS]],

            colors=[_ERROR_COLOR if d.accion == ACTION_ERROR else None for d in details[:MAX_PREVIEW_ROWS]],

        )

        self._update_buttons()



    @guarded

    def _export_errors(self) -> None:

        if self._import_id is None:

            return

        report = self._services.imports.error_report(self._import_id)

        chosen, _ = QFileDialog.getSaveFileName(

            self, "Guardar informe de errores", "errores_importacion.csv", "CSV (*.csv)"

        )

        if not chosen:

            return

        write_csv_rows(Path(chosen), report)

        QMessageBox.information(self, "Informe de errores", f"Archivo generado:\n{chosen}")



    @guarded

    def _apply(self) -> None:

        if self._preview is None or self._options is None or self._import_id is None:

            return

        preview = self._preview

        options = self._read_options()

        if self._has_errors and not options.skip_error_rows:

            QMessageBox.warning(

                self,

                "Archivo con errores",

                "El archivo tiene filas con error. Corrija el archivo, exporte el informe "

                "o (administrador) marque «Omitir filas con error».",

            )

            return

        question = (

            f"Se aplicarán {preview.nuevas} altas y {preview.actualizables} actualizaciones.\n"

        )

        if preview.repetido is not None:

            question += "\nATENCIÓN: este archivo ya fue aplicado anteriormente.\n"

        answer = QMessageBox.question(self, "Confirmar importación", question + "\n¿Continuar?")

        if answer != QMessageBox.StandardButton.Yes:

            return

        import_id = self._import_id

        self._summary.setText("Aplicando importación…")

        self._run(

            lambda progress: self._services.imports.apply(import_id, options, progress=progress),

            self._on_applied,

        )



    def _on_applied(self, result: Any) -> None:

        QMessageBox.information(

            self,

            "Importación aplicada",

            f"Altas: {result.insertados}\nActualizaciones: {result.actualizados}\n"

            f"Sin cambios: {result.sin_cambios}\nRechazadas: {result.rechazados}\n"

            f"Movimientos de stock: {result.movimientos}",

        )

        self._reset_preview()

        self._summary.setText("Importación aplicada correctamente.")

        self.changed.emit()



    @guarded

    def _discard(self) -> None:

        if self._import_id is not None:

            self._services.imports.cancel(self._import_id)

        self._reset_preview()

        self._summary.setText("Importación descartada.")



    def _reset_preview(self) -> None:

        self._preview = None

        self._import_id = None

        self._options = None
        self._has_errors = False

        self._warnings.setText("")

        self._model.set_rows([])

        self._update_buttons()



    # ----- historial -----



    def _refresh_history(self) -> None:

        if "importacion.historial" not in self._permisos:

            return

        try:

            records = self._services.imports.history()

        except Exception as error:

            show_error(self, error)

            return

        self._history_model.set_rows(

            [

                [

                    str(r.id),

                    r.nombre_archivo,

                    fmt_local(r.iniciado_en),

                    r.modo,

                    r.estado,

                    str(r.total_filas),

                    str(r.filas_error),

                    str(r.insertados),

                    str(r.actualizados),

                    str(r.rechazados),

                ]

                for r in records

            ],

            payloads=list(records),

        )



    @guarded

    def _show_history_errors(self) -> None:

        record: ImportRecord | None = selected_payload(self._history_table, self._history_model)

        if record is None:

            QMessageBox.information(self, "Historial", "Seleccione una importación.")

            return

        details = self._services.imports.details(record.id, only_errors=True)

        dialog = QDialog(self)

        dialog.setWindowTitle(f"Errores de la importación #{record.id}")

        dialog.resize(820, 480)

        model = TableModel(["Fila", "Código", "Acción", "Detalle"])

        model.set_rows([_detail_row(d) for d in details])

        layout = QVBoxLayout()

        layout.addWidget(make_table(model))

        dialog.setLayout(layout)

        dialog.exec()





def _detail_row(detail: ImportDetail) -> list[str]:

    return [

        str(detail.nro_fila),

        detail.codigo or "",

        _ACTION_LABELS.get(detail.accion, detail.accion),

        "; ".join(

            f"{e.get('code', '')} {e.get('column', '')}: {e.get('message', '')}"

            for e in detail.errores

        ),

    ]

