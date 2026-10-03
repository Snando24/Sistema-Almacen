"""Administración: auditoría, configuración, tipos de movimiento y respaldos (S-18 a S-20)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.application.settings import SETTING_SPECS
from sisalmacen.domain.inventory import NATURE_SIGN, AuditFilter, AuditRow, MovementType
from sisalmacen.ui.theme import apply_dialog_theme
from sisalmacen.ui.widgets import (
    TableModel,
    build_page_header,
    fmt_local,
    guarded,
    make_table,
    parse_date_input,
    secondary_button,
    selected_payload,
    show_error,
)

AUDIT_PAGE_SIZE = 100
_NATURE_LABELS = {
    "ENTRADA": "Entrada",
    "SALIDA": "Salida",
    "AJUSTE_POS": "Ajuste positivo",
    "AJUSTE_NEG": "Ajuste negativo",
}


class _AuditTab(QWidget):
    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._services = services
        self._page = 1
        self._pages = 1

        self._from = QLineEdit()
        self._from.setPlaceholderText("Desde AAAA-MM-DD")
        self._to = QLineEdit()
        self._to.setPlaceholderText("Hasta AAAA-MM-DD")
        self._user = QLineEdit()
        self._user.setPlaceholderText("Usuario")
        self._entity = QLineEdit()
        self._entity.setPlaceholderText("Entidad (producto, movimiento…)")
        self._action = QLineEdit()
        self._action.setPlaceholderText("Acción (CREAR, EDITAR…)")
        search = QPushButton("Buscar")
        search.clicked.connect(self._search)
        filters = QHBoxLayout()
        for widget in (self._from, self._to, self._user, self._entity, self._action, search):
            filters.addWidget(widget)

        self._model = TableModel(["Fecha", "Usuario", "Acción", "Entidad", "Id", "Detalle"])
        self._table = make_table(self._model)
        self._table.selectionModel().selectionChanged.connect(lambda *_a: self._show_detail())
        self._detail = QPlainTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setMaximumHeight(150)

        self._prev = secondary_button("? Anterior")
        self._prev.clicked.connect(self._previous)
        self._next = secondary_button("Siguiente ?")
        self._next.clicked.connect(self._following)
        self._status = QLabel("")
        pager = QHBoxLayout()
        pager.addWidget(self._prev)
        pager.addWidget(self._next)
        pager.addWidget(self._status, 1)

        layout = QVBoxLayout()
        layout.addLayout(filters)
        layout.addWidget(self._table, 1)
        layout.addWidget(self._detail)
        layout.addLayout(pager)
        self.setLayout(layout)

    def _build_filter(self) -> AuditFilter:
        return AuditFilter(
            fecha_desde=parse_date_input(self._from.text(), "Desde"),
            fecha_hasta=parse_date_input(self._to.text(), "Hasta"),
            username=self._user.text(),
            entidad=self._entity.text(),
            accion=self._action.text().upper(),
        )

    def refresh(self) -> None:
        try:
            result = self._services.audit.search(
                self._build_filter(), page=self._page, page_size=AUDIT_PAGE_SIZE
            )
        except Exception as error:
            show_error(self, error)
            return
        self._pages = result.pages
        self._model.set_rows(
            [
                [
                    fmt_local(r.fecha_hora),
                    r.username or "",
                    r.accion,
                    r.entidad,
                    r.entidad_id or "",
                    r.detalle or "",
                ]
                for r in result.items
            ],
            payloads=list(result.items),
        )
        self._detail.clear()
        self._status.setText(f"Página {result.page} de {self._pages} · {result.total} registro(s)")
        self._prev.setEnabled(result.page > 1)
        self._next.setEnabled(result.page < self._pages)

    def _show_detail(self) -> None:
        row: AuditRow | None = selected_payload(self._table, self._model)
        if row is None:
            self._detail.clear()
            return
        self._detail.setPlainText(
            f"Estación: {row.estacion or ''}\n\nValor anterior:\n{row.valor_anterior or '—'}\n\n"
            f"Valor nuevo:\n{row.valor_nuevo or '—'}"
        )

    @guarded
    def _search(self) -> None:
        self._build_filter()
        self._page = 1
        self.refresh()

    @guarded
    def _previous(self) -> None:
        self._page = max(1, self._page - 1)
        self.refresh()

    @guarded
    def _following(self) -> None:
        self._page = min(self._pages, self._page + 1)
        self.refresh()


class _SettingsTab(QWidget):
    saved = Signal()

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._services = services
        self._inputs: dict[str, QWidget] = {}
        values = services.settings.read_all()

        layout = QVBoxLayout()
        groups: dict[str, QFormLayout] = {}
        for spec in SETTING_SPECS:
            form = groups.get(spec.group)
            if form is None:
                form = QFormLayout()
                groups[spec.group] = form
                box = QGroupBox(spec.group)
                box.setLayout(form)
                layout.addWidget(box)
            value = values.get(spec.key, "")
            widget: QWidget
            if spec.kind == "bool":
                widget = QCheckBox()
                widget.setChecked(value == "1")
            elif spec.kind == "choice":
                widget = QComboBox()
                for option_value, option_label in spec.choices:
                    widget.addItem(option_label, option_value)
                index = widget.findData(value)
                widget.setCurrentIndex(index if index >= 0 else 0)
            elif spec.kind in ("folder", "file"):
                widget = self._path_row(spec.kind, value)
            else:
                widget = QLineEdit(value)
            self._inputs[spec.key] = widget
            form.addRow(spec.label, widget)

        save = QPushButton("Guardar configuración")
        save.clicked.connect(self._save)
        layout.addWidget(save)
        layout.addStretch(1)
        content = QWidget()
        content.setLayout(layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        self.setLayout(outer)

    def _path_row(self, kind: str, value: str) -> QWidget:
        edit = QLineEdit(value)
        browse = secondary_button("Examinar…")

        def choose() -> None:
            if kind == "folder":
                chosen = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta", edit.text())
            else:
                chosen, _ = QFileDialog.getOpenFileName(
                    self, "Seleccionar imagen", edit.text(), "Imágenes (*.png *.jpg *.jpeg)"
                )
            if chosen:
                edit.setText(chosen)

        browse.clicked.connect(lambda _c=False: choose())
        row = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(edit, 1)
        row_layout.addWidget(browse)
        row.setLayout(row_layout)
        return row

    @guarded
    def _save(self) -> None:
        values: dict[str, str] = {}
        for key, widget in self._inputs.items():
            if isinstance(widget, QCheckBox):
                values[key] = "1" if widget.isChecked() else "0"
            elif isinstance(widget, QComboBox):
                values[key] = str(widget.currentData())
            elif isinstance(widget, QLineEdit):
                values[key] = widget.text()
            else:
                edit = widget.findChild(QLineEdit)
                values[key] = edit.text() if edit is not None else ""
        self._services.settings.update(values)
        QMessageBox.information(self, "Configuración", "Configuración guardada.")
        self.saved.emit()


class _TypeDialog(QDialog):
    def __init__(
        self,
        services: AppServices,
        movement_type: MovementType | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        apply_dialog_theme(self)
        self._services = services
        self._type = movement_type
        self.setWindowTitle("Editar tipo" if movement_type else "Nuevo tipo de movimiento")
        self._code = QLineEdit(movement_type.codigo if movement_type else "")
        self._code.setEnabled(movement_type is None)
        self._name = QLineEdit(movement_type.nombre if movement_type else "")
        self._nature = QComboBox()
        for nature in NATURE_SIGN:
            self._nature.addItem(_NATURE_LABELS[nature], nature)
        if movement_type:
            self._nature.setCurrentIndex(self._nature.findData(movement_type.naturaleza))
            self._nature.setEnabled(False)
        self._reason = QCheckBox("Exige motivo")
        self._reason.setChecked(bool(movement_type and movement_type.requiere_motivo))
        form = QFormLayout()
        form.addRow("Código *", self._code)
        form.addRow("Nombre *", self._name)
        form.addRow("Naturaleza *", self._nature)
        form.addRow("", self._reason)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _save(self) -> None:
        try:
            movements = self._services.movements
            if self._type is None:
                movements.create_type(
                    self._code.text(),
                    self._name.text(),
                    self._nature.currentData(),
                    requires_reason=self._reason.isChecked(),
                )
            else:
                movements.update_type(
                    self._type.id, self._name.text(), requires_reason=self._reason.isChecked()
                )
        except Exception as error:
            show_error(self, error)
            return
        self.accept()


class _TypesTab(QWidget):
    changed = Signal()

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._services = services
        self._model = TableModel(
            ["Código", "Nombre", "Naturaleza", "Exige motivo", "Sistema", "Estado"]
        )
        self._table = make_table(self._model)
        new = QPushButton("Nuevo tipo")
        new.clicked.connect(self._new)
        edit = secondary_button("Editar")
        edit.clicked.connect(self._edit)
        toggle = secondary_button("Activar / desactivar")
        toggle.clicked.connect(self._toggle)
        bar = QHBoxLayout()
        for button in (new, edit, toggle):
            bar.addWidget(button)
        bar.addStretch(1)
        layout = QVBoxLayout()
        layout.addLayout(bar)
        layout.addWidget(self._table, 1)
        self.setLayout(layout)
        self.refresh()

    def refresh(self) -> None:
        try:
            types = self._services.movements.list_types()
        except Exception as error:
            show_error(self, error)
            return
        self._model.set_rows(
            [
                [
                    t.codigo,
                    t.nombre,
                    _NATURE_LABELS.get(t.naturaleza, t.naturaleza),
                    "Sí" if t.requiere_motivo else "No",
                    "Sí" if t.es_sistema else "No",
                    "Activo" if t.activo else "Inactivo",
                ]
                for t in types
            ],
            payloads=types,
        )

    def _selected(self) -> MovementType | None:
        selected: MovementType | None = selected_payload(self._table, self._model)
        if selected is None:
            QMessageBox.information(self, "Tipos de movimiento", "Seleccione un tipo.")
        return selected

    @guarded
    def _new(self) -> None:
        if _TypeDialog(self._services, None, self).exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            self.changed.emit()

    @guarded
    def _edit(self) -> None:
        selected = self._selected()
        if (
            selected
            and _TypeDialog(self._services, selected, self).exec() == QDialog.DialogCode.Accepted
        ):
            self.refresh()
            self.changed.emit()

    @guarded
    def _toggle(self) -> None:
        selected = self._selected()
        if selected is None:
            return
        self._services.movements.set_type_active(selected.id, active=not selected.activo)
        self.refresh()
        self.changed.emit()


class _BackupTab(QWidget):
    restored = Signal()
    created = Signal()

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._services = services
        self._folder = QLabel("")
        self._last = QLabel("")
        create = QPushButton("Crear respaldo ahora")
        create.clicked.connect(self._create_default)
        create_elsewhere = secondary_button("Crear en otra carpeta…")
        create_elsewhere.clicked.connect(self._create_elsewhere)
        restore = secondary_button("Restaurar respaldo…")
        restore.clicked.connect(self._restore)
        note = QLabel(
            "Se recomienda guardar una copia en una unidad externa. La restauración reemplaza "
            "TODA la información actual y exige reiniciar la aplicación."
        )
        note.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Carpeta de respaldos"))
        layout.addWidget(self._folder)
        layout.addWidget(QLabel("Último respaldo"))
        layout.addWidget(self._last)
        row = QHBoxLayout()
        row.addWidget(create)
        row.addWidget(create_elsewhere)
        row.addWidget(restore)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addWidget(note)
        layout.addStretch(1)
        self.setLayout(layout)
        self.refresh()

    def refresh(self) -> None:
        try:
            self._folder.setText(self._services.backup.default_folder() or "Sin definir")
            self._last.setText(fmt_local(self._services.backup.last_backup()) or "Nunca")
        except Exception as error:
            show_error(self, error)

    def _do_create(self, folder: Path | None) -> None:
        archive, sha256 = self._services.backup.create(folder)
        QMessageBox.information(
            self, "Respaldo creado", f"Archivo:\n{archive}\n\nSHA-256 de la base:\n{sha256}"
        )
        self.refresh()
        self.created.emit()

    @guarded
    def _create_default(self) -> None:
        self._do_create(None)

    @guarded
    def _create_elsewhere(self) -> None:
        chosen = QFileDialog.getExistingDirectory(self, "Carpeta de destino")
        if chosen:
            self._do_create(Path(chosen))

    @guarded
    def _restore(self) -> None:
        chosen, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar respaldo",
            self._services.backup.default_folder(),
            "Respaldos (*.zip)",
        )
        if not chosen:
            return
        answer = QMessageBox.warning(
            self,
            "Restaurar respaldo",
            "Esta operación reemplazará toda la información actual por la del respaldo.\n"
            "Antes se creará un respaldo automático de la base actual.\n\n¿Desea continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        previous = self._services.backup.restore(Path(chosen))
        QMessageBox.information(
            self,
            "Restauración completada",
            f"Se restauró el respaldo.\nRespaldo previo guardado en:\n{previous}\n\n"
            "La aplicación se cerrará; vuelva a abrirla para continuar.",
        )
        self.restored.emit()
        QApplication.quit()


class AdminPage(QWidget):
    settings_changed = Signal()
    types_changed = Signal()

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("administracion-page")
        permisos = services.session.permisos
        self._tabs = QTabWidget()
        self._audit: _AuditTab | None = None
        self._backup: _BackupTab | None = None
        if "auditoria.ver" in permisos:
            self._audit = _AuditTab(services)
            self._tabs.addTab(self._audit, "Auditoría")
        if "configuracion.gestionar" in permisos:
            settings_tab = _SettingsTab(services)
            settings_tab.saved.connect(self.settings_changed)
            self._tabs.addTab(settings_tab, "Configuración")
            types_tab = _TypesTab(services)
            types_tab.changed.connect(self.types_changed)
            self._tabs.addTab(types_tab, "Tipos de movimiento")
        if "backup.gestionar" in permisos:
            self._backup = _BackupTab(services)
            self._tabs.addTab(self._backup, "Respaldos")
        if self._tabs.count() == 0:
            self._tabs.addTab(
                QLabel("Su perfil no tiene opciones de administración."), "Administración"
            )
        self._tabs.currentChanged.connect(self._on_tab_changed)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(
            build_page_header(
                "Administración", "Auditoría, configuración, tipos de movimiento y respaldos."
            )
        )
        layout.addWidget(self._tabs, 1)
        self.setLayout(layout)

    def _on_tab_changed(self, _index: int) -> None:
        self.refresh()

    def refresh(self) -> None:
        current: Any = self._tabs.currentWidget()
        if current is self._audit and self._audit is not None:
            self._audit.refresh()
        elif current is self._backup and self._backup is not None:
            self._backup.refresh()
