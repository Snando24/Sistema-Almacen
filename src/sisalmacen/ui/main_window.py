"""Ventana principal: navegación lateral y páginas funcionales."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from sisalmacen.application.services import AppServices
from sisalmacen.ui.pages.admin_page import AdminPage
from sisalmacen.ui.pages.catalogs_page import CatalogsPage
from sisalmacen.ui.pages.dashboard_page import DashboardPage
from sisalmacen.ui.pages.import_page import ImportPage
from sisalmacen.ui.pages.movements_page import MovementsPage
from sisalmacen.ui.pages.products_page import ProductsPage
from sisalmacen.ui.pages.reports_page import ReportsPage
from sisalmacen.ui.theme import (
    BRAND_NAME,
    BRAND_TAGLINE,
    THEME_DARK,
    THEME_LIGHT,
    THEME_SETTING_KEY,
    apply_application_theme,
    get_brand_logo_html,
    normalize_theme_mode,
)
from sisalmacen.ui.widgets import show_error

SECTION_LABELS = (
    "Dashboard",
    "Productos",
    "Movimientos",
    "Importación CSV",
    "Reportes",
    "Catálogos",
    "Administración",
)
(
    IDX_DASHBOARD,
    IDX_PRODUCTS,
    IDX_MOVEMENTS,
    IDX_IMPORT,
    IDX_REPORTS,
    IDX_CATALOGS,
    IDX_ADMIN,
) = range(7)


class MainWindow(QMainWindow):
    """Ventana de operación local (sin inicio de sesión)."""

    def __init__(self, *, services: AppServices, database_label: str, logs_label: str) -> None:
        super().__init__()
        self._services = services
        self._database_label = database_label
        self._logs_label = logs_label
        self._theme_mode = normalize_theme_mode(
            services.settings.read_all().get(THEME_SETTING_KEY, THEME_LIGHT)
        )
        self._theme_toggle: QToolButton | None = None
        self.setWindowTitle(BRAND_NAME)
        self.setMinimumSize(1000, 660)
        self.resize(1240, 780)
        self._setup_ui()

    # ----- construcción -----

    def _setup_ui(self) -> None:
        self._build_menu()
        self._build_pages()

        root = QWidget()
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self._build_brand_bar())
        body = QHBoxLayout()
        body.setContentsMargins(18, 18, 18, 18)
        body.setSpacing(18)
        body.addWidget(self._build_sidebar(), 0)
        body.addWidget(self._stacked_pages, 1)
        root_layout.addLayout(body, 1)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        self._navigation.setCurrentRow(IDX_DASHBOARD)
        status_bar = QStatusBar()
        status_bar.showMessage(f"Modo local · Base de datos: {self._database_label}")
        self.setStatusBar(status_bar)

    def _build_pages(self) -> None:
        services = self._services
        self._dashboard = DashboardPage(services)
        self._products = ProductsPage(services)
        self._movements = MovementsPage(services)
        self._import = ImportPage(services)
        self._reports = ReportsPage(services)
        self._catalogs = CatalogsPage(services)
        self._admin = AdminPage(services)

        self._stacked_pages = QStackedWidget()
        for page in (
            self._dashboard,
            self._products,
            self._movements,
            self._import,
            self._reports,
            self._catalogs,
            self._admin,
        ):
            self._stacked_pages.addWidget(page)

        self._dashboard.navigate.connect(self._on_dashboard_navigate)
        self._movements.changed.connect(self._after_data_change)
        self._import.changed.connect(self._after_data_change)
        self._admin.settings_changed.connect(self._after_settings_change)
        self._admin.types_changed.connect(self._movements.reload_types)

    def _build_brand_bar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("brand-bar")

        logo = QLabel(get_brand_logo_html())
        logo.setObjectName("brand-logo")
        logo.setTextFormat(Qt.TextFormat.RichText)
        name = QLabel(BRAND_NAME.replace("R&R ", "").upper())
        name.setObjectName("brand-name")
        tagline = QLabel(BRAND_TAGLINE)
        tagline.setObjectName("brand-tagline")
        texts = QVBoxLayout()
        texts.setSpacing(2)
        texts.addWidget(name)
        texts.addWidget(tagline)
        badge = QLabel("MODO LOCAL")
        badge.setObjectName("brand-badge")

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 10, 24, 10)
        layout.setSpacing(16)
        layout.addWidget(logo)
        layout.addLayout(texts)
        layout.addStretch(1)
        if "configuracion.gestionar" in self._services.session.permisos:
            self._theme_toggle = QToolButton()
            self._theme_toggle.setObjectName("theme-toggle")
            self._theme_toggle.clicked.connect(self._toggle_theme)
            self._update_theme_toggle()
            layout.addWidget(self._theme_toggle, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        bar.setLayout(layout)
        return bar

    def _build_sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("sidebar")
        panel.setFixedWidth(240)

        caption = QLabel("NAVEGACIÓN")
        caption.setObjectName("sidebar-caption")
        self._navigation = QListWidget()
        self._navigation.setObjectName("navigation")
        for label in SECTION_LABELS:
            self._navigation.addItem(QListWidgetItem(label))
        self._navigation.currentRowChanged.connect(self._show_section)

        hint = QLabel(
            f"Uso local en este equipo: no requiere inicio de sesión.\nLogs: {self._logs_label}"
        )
        hint.setObjectName("sidebar-hint")
        hint.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(10)
        layout.addWidget(caption)
        layout.addWidget(self._navigation, 1)
        layout.addWidget(hint)
        panel.setLayout(layout)
        return panel

    def _build_menu(self) -> None:
        system_menu = self.menuBar().addMenu("Sistema")
        refresh_action = QAction("Actualizar pantalla", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(lambda _c=False: self._refresh_current())
        system_menu.addAction(refresh_action)
        exit_action = QAction("Salir", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)

        go_menu = self.menuBar().addMenu("Ir a")
        for index, label in enumerate(SECTION_LABELS):
            action = QAction(label, self)
            action.setShortcut(QKeySequence(f"Ctrl+{index + 1}"))
            action.triggered.connect(lambda _c=False, row=index: self._go_to(row))
            go_menu.addAction(action)

    # ----- navegación -----

    def _go_to(self, row: int) -> None:
        self._navigation.setCurrentRow(row)

    def _show_section(self, index: int) -> None:
        if 0 <= index < self._stacked_pages.count():
            self._stacked_pages.setCurrentIndex(index)
            self._refresh_page(index)

    def _refresh_current(self) -> None:
        self._refresh_page(self._stacked_pages.currentIndex())
        self.statusBar().showMessage("Pantalla actualizada.", 4000)

    def _refresh_page(self, index: int) -> None:
        """Recarga la página al entrar; cada página muestra sus propios errores."""

        if index == IDX_DASHBOARD:
            self._dashboard.refresh()
        elif index == IDX_PRODUCTS:
            self._products.reload_catalogs()
            self._products.refresh()
        elif index == IDX_MOVEMENTS:
            self._movements.refresh()
        elif index == IDX_REPORTS:
            self._reports.reload_catalogs()
        elif index == IDX_CATALOGS:
            self._catalogs.refresh()
        elif index == IDX_ADMIN:
            self._admin.refresh()

    def _after_data_change(self) -> None:
        self._products.reload_catalogs()
        self._products.refresh()
        self._movements.refresh()
        self._dashboard.refresh()

    def _after_settings_change(self) -> None:
        mode = self._services.settings.read_all().get(THEME_SETTING_KEY, THEME_LIGHT)
        self._apply_theme(mode)
        self._after_data_change()

    def _toggle_theme(self) -> None:
        mode = THEME_DARK if self._theme_mode == THEME_LIGHT else THEME_LIGHT
        try:
            self._services.settings.update({THEME_SETTING_KEY: mode})
        except Exception as error:
            show_error(self, error)
            return
        self._apply_theme(mode)
        self.statusBar().showMessage(
            "Modo oscuro activado." if self._theme_mode == THEME_DARK else "Modo claro activado.",
            4000,
        )

    def _apply_theme(self, mode: str | None) -> None:
        app = QApplication.instance()
        if app is None:
            return
        self._theme_mode = apply_application_theme(app, mode)
        self._update_theme_toggle()

    def _update_theme_toggle(self) -> None:
        if self._theme_toggle is None:
            return
        if self._theme_mode == THEME_DARK:
            self._theme_toggle.setText("☀ Modo claro")
            self._theme_toggle.setToolTip("Cambiar al modo claro")
        else:
            self._theme_toggle.setText("☾ Modo oscuro")
            self._theme_toggle.setToolTip("Cambiar al modo oscuro")

    def _on_dashboard_navigate(self, target: str, argument: str) -> None:
        if target == "productos":
            self._go_to(IDX_PRODUCTS)
            self._products.show_alert(argument or None)
        elif target == "producto_nuevo":
            self._go_to(IDX_PRODUCTS)
            self._products.start_new()
        elif target == "movimiento":
            self._go_to(IDX_MOVEMENTS)
            self._movements.start_register(argument)
        elif target == "importacion":
            self._go_to(IDX_IMPORT)
        elif target == "reportes":
            self._go_to(IDX_REPORTS)
