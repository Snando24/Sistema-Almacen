"""Dashboard con indicadores, alertas y accesos rápidos (S-03, RF-080/081)."""

from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.application.settings import flag
from sisalmacen.domain.inventory import ALERT_AGOTADO, ALERT_BAJO_MINIMO
from sisalmacen.ui.theme import BRAND_NAME
from sisalmacen.ui.widgets import build_page_header, fmt_money, secondary_button, show_error

_CARDS_PER_ROW = 4


class DashboardPage(QScrollArea):
    """Emite `navigate(destino, argumento)`; la ventana principal decide cómo abrirlo."""

    navigate = Signal(str, str)

    def __init__(self, services: AppServices, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dashboard-page")
        self._services = services
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.refresh()

    def refresh(self) -> None:
        try:
            snapshot = self._services.load_dashboard()
            reminder = (
                self._services.backup.reminder()
                if "backup.gestionar" in self._services.session.permisos
                else None
            )
            settings = self._services.settings.read_all()
        except Exception as error:
            show_error(self, error)
            return
        show_prices = "productos.ver_precios" in self._services.session.permisos and flag(
            settings, "inventario.usar_precios", default=True
        )

        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(16)

        company = snapshot.empresa_nombre or BRAND_NAME
        header = build_page_header("Panel de control", f"{company} · Resumen del almacén")
        refresh_button = QPushButton("Actualizar resumen")
        refresh_button.clicked.connect(lambda _c=False: QTimer.singleShot(0, self.refresh))
        header.layout().addWidget(refresh_button, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)

        if reminder:
            banner = QLabel(f"? {reminder} Vaya a Administración › Respaldos.")
            banner.setWordWrap(True)
            banner.setStyleSheet(
                "background:#f2b93b; color:#101214; font-weight:700; padding:10px; border-radius:8px;"
            )
            layout.addWidget(banner)

        cards: list[QWidget] = [
            self._card("Productos", str(snapshot.total_productos), "Registros totales"),
            self._card("Activos", str(snapshot.productos_activos), "Disponibles para operar"),
            self._card(
                "Agotados",
                str(snapshot.productos_sin_stock),
                "Productos sin stock",
                alert=ALERT_AGOTADO,
            ),
            self._card(
                "Bajo el mínimo",
                str(snapshot.productos_bajo_minimo),
                "Por debajo del stock mínimo",
                alert=ALERT_BAJO_MINIMO,
            ),
        ]
        cards.append(self._card("Entradas de hoy", str(snapshot.entradas_hoy), "Movimientos"))
        cards.append(self._card("Salidas de hoy", str(snapshot.salidas_hoy), "Movimientos"))
        if show_prices:
            cards.append(
                self._card(
                    "Valor estimado",
                    fmt_money(snapshot.valor_inventario or Decimal(0)),
                    "Stock × precio de compra",
                )
            )
        grid = QGridLayout()
        grid.setSpacing(14)
        for column in range(_CARDS_PER_ROW):
            grid.setColumnStretch(column, 1)
        for index, card in enumerate(cards):
            grid.addWidget(card, index // _CARDS_PER_ROW, index % _CARDS_PER_ROW)
        layout.addLayout(grid)

        layout.addWidget(self._quick_access())
        layout.addStretch(1)
        page.setLayout(layout)
        self.setWidget(page)

    def _card(self, title: str, value: str, subtitle: str, *, alert: str | None = None) -> QWidget:
        card = QFrame()
        card.setObjectName("stat-card")
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)
        title_label = QLabel(title)
        title_label.setObjectName("card-title")
        value_label = QLabel(value)
        value_label.setObjectName("card-value")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("card-subtitle")
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        if alert is not None:
            button = secondary_button("Ver productos")
            button.clicked.connect(lambda _c=False, a=alert: self.navigate.emit("productos", a))
            layout.addWidget(button)
        card.setLayout(layout)
        return card

    def _quick_access(self) -> QWidget:
        permisos = self._services.session.permisos
        row = QHBoxLayout()
        for label, target, argument, permission in (
            ("Nuevo producto", "producto_nuevo", "", "productos.crear"),
            ("Registrar entrada", "movimiento", "ENTRADA", "movimientos.entrada"),
            ("Registrar salida", "movimiento", "SALIDA", "movimientos.salida"),
            ("Importar CSV", "importacion", "", "importacion.ejecutar"),
            ("Reportes", "reportes", "", "reportes.ver"),
        ):
            button = QPushButton(label)
            button.setEnabled(permission in permisos)
            button.clicked.connect(lambda _c=False, t=target, a=argument: self.navigate.emit(t, a))
            row.addWidget(button)
        row.addStretch(1)
        box = QGroupBox("Accesos rápidos")
        box.setLayout(row)
        return box
