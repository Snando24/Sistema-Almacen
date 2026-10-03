"""Componentes de interfaz compartidos."""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.domain.errors import DomainError, ValidationError

LOGGER = logging.getLogger("sisalmacen")

ROLE_PAYLOAD = Qt.ItemDataRole.UserRole


# ---------- formato ----------


def fmt_qty(value: Decimal | None) -> str:
    if value is None:
        return ""
    text = format(value.normalize(), ",f")
    return text


def fmt_money(value: Decimal | None) -> str:
    if value is None:
        return ""
    two = value.quantize(Decimal("0.01"))
    shown = two if two == value else value.quantize(Decimal("0.0001"))
    return format(shown, ",f")


def fmt_local(utc_text: str | None) -> str:
    """Convierte fecha UTC ISO-8601 a hora local legible (ADR-11)."""

    if not utc_text:
        return ""
    try:
        moment = datetime.strptime(utc_text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        return utc_text
    return f"{moment.astimezone():%Y-%m-%d %H:%M}"


def parse_decimal_input(text: str, label: str, *, required: bool = False) -> Decimal | None:
    """Convierte el texto de un campo; acepta coma o punto decimal."""

    cleaned = text.strip().replace(",", ".")
    if not cleaned:
        if required:
            raise ValidationError(f"Debe indicar {label}.", code="CAMPO_REQUERIDO")
        return None
    try:
        value = Decimal(cleaned)
    except InvalidOperation as error:
        raise ValidationError(f"{label}: valor numérico inválido.", code="NUMERO_INVALIDO") from error
    if not value.is_finite():
        raise ValidationError(f"{label}: valor numérico inválido.", code="NUMERO_INVALIDO")
    return value


def parse_date_input(text: str, label: str) -> date | None:
    cleaned = text.strip()
    if not cleaned:
        return None
    try:
        return date.fromisoformat(cleaned)
    except ValueError as error:
        raise ValidationError(f"{label}: use el formato AAAA-MM-DD.", code="FECHA_INVALIDA") from error


# ---------- errores ----------


def show_error(parent: QWidget | None, error: BaseException) -> None:
    """Muestra el mensaje funcional; el detalle técnico solo va al log."""

    if isinstance(error, DomainError):
        QMessageBox.warning(parent, "No se pudo completar la acción", error.message)
        return
    LOGGER.error("Error inesperado en la interfaz", exc_info=error)
    QMessageBox.critical(
        parent,
        "Error inesperado",
        "Ocurrió un error técnico. Revise el archivo de log para más detalle.",
    )


def guarded(method: Callable[[Any], None]) -> Callable[..., None]:
    """Slot sin argumentos que captura errores y los muestra al usuario."""

    @functools.wraps(method)
    def wrapper(self: Any, *_args: object) -> None:
        try:
            method(self)
        except Exception as error:
            show_error(self, error)

    return wrapper


# ---------- tablas ----------


class TableModel(QAbstractTableModel):
    """Modelo de solo lectura con cadenas, alineación por columna y color por fila."""

    def __init__(
        self,
        headers: list[str],
        right_aligned: set[int] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._headers = headers
        self._right = right_aligned or set()
        self._rows: list[list[str]] = []
        self._payloads: list[Any] = []
        self._colors: list[QColor | None] = []

    def set_rows(
        self,
        rows: list[list[str]],
        payloads: list[Any] | None = None,
        colors: list[QColor | None] | None = None,
    ) -> None:
        self.beginResetModel()
        self._rows = rows
        self._payloads = payloads if payloads is not None else [None] * len(rows)
        self._colors = colors if colors is not None else [None] * len(rows)
        self.endResetModel()

    def payload(self, row: int) -> Any:
        return self._payloads[row] if 0 <= row < len(self._payloads) else None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self._headers)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._rows[index.row()][index.column()]
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() in self._right:
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if role == Qt.ItemDataRole.BackgroundRole:
            return self._colors[index.row()]
        if role == ROLE_PAYLOAD:
            return self._payloads[index.row()]
        return None


def make_table(model: QAbstractTableModel) -> QTableView:
    table = QTableView()
    table.setModel(model)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(28)
    table.horizontalHeader().setStretchLastSection(True)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    return table


def selected_payload(table: QTableView, model: TableModel) -> Any:
    indexes = table.selectionModel().selectedRows()
    return model.payload(indexes[0].row()) if indexes else None


# ---------- piezas visuales ----------


def build_page_header(title: str, subtitle: str) -> QFrame:
    header = QFrame()
    header.setObjectName("page-header")
    title_label = QLabel(title)
    title_label.setObjectName("page-title")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("page-subtitle")
    subtitle_label.setWordWrap(True)
    layout = QVBoxLayout()
    layout.setContentsMargins(20, 14, 20, 14)
    layout.setSpacing(4)
    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    header.setLayout(layout)
    return header


def secondary_button(text: str) -> QPushButton:
    button = QPushButton(text)
    button.setProperty("variant", "secondary")
    return button


# ---------- hilos ----------


class Worker(QThread):
    """Ejecuta una tarea larga fuera del hilo de la interfaz (RNF-004)."""

    succeeded = Signal(object)
    failed = Signal(object)
    progressed = Signal(int, int)

    def __init__(self, task: Callable[[Callable[[int, int], None]], Any]) -> None:
        super().__init__()
        self._task = task

    def run(self) -> None:
        try:
            result = self._task(lambda done, total: self.progressed.emit(done, total))
        except Exception as error:
            self.failed.emit(error)
            return
        self.succeeded.emit(result)
