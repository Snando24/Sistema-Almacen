"""Tema visual corporativo para la aplicación de Grupo Corporación.

Colores tomados del logo: rojo del "&", negro de las "R", gris del engranaje,
amarillo de la excavadora y blanco.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import QApplication, QDialog

BRAND_NAME = "R&R Grupo Corporación"
BRAND_TAGLINE = "MECÁNICA DE MAQUINARIAS PESADAS Y SOLDADURA EN GENERAL"

THEME_SETTING_KEY = "ui.tema"
THEME_LIGHT = "claro"
THEME_DARK = "oscuro"


def _contrast_color(bg_hex: str, *, light: str = "#ffffff", dark: str = "#111827") -> str:
    """Elige el color de texto con mayor contraste contra un fondo dado."""

    def _hex_to_rgb(value: str) -> tuple[int, int, int]:
        h = value.lstrip("#")
        if len(h) == 3:
            h = "".join(char * 2 for char in h)
        return tuple(int(h[index : index + 2], 16) for index in (0, 2, 4))

    def _srgb_to_linear(channel: int) -> float:
        c = channel / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def _relative_luminance(value: str) -> float:
        r, g, b = _hex_to_rgb(value)
        r_lin = _srgb_to_linear(r)
        g_lin = _srgb_to_linear(g)
        b_lin = _srgb_to_linear(b)
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    bg_luma = _relative_luminance(bg_hex)
    dark_luma = _relative_luminance(dark)
    light_luma = _relative_luminance(light)

    if (max(bg_luma, dark_luma) + 0.05) / (min(bg_luma, dark_luma) + 0.05) > (
        max(bg_luma, light_luma) + 0.05
    ) / (min(bg_luma, light_luma) + 0.05):
        return dark
    return light


BRAND_PALETTE = {
    "primary": "#d1121e",
    "primary_dark": "#9e0f18",
    "secondary": "#101214",
    "secondary_light": "#2f3438",
    "steel": "#dfe3e8",
    "accent": "#f2b93b",
    "background": "#f3f3f1",
    "dialog": "#f7f8fa",
    "panel": "#ffffff",
    "field": "#ffffff",
    "border": "#d9d9d4",
    "border_strong": "#98a2b3",
    "muted": "#4b5563",
    "text": "#111827",
    "on_primary": _contrast_color("#d1121e"),
    "on_accent": _contrast_color("#f2b93b"),
    "on_dark": "#f5f7fa",
    "button_secondary": "#ffffff",
    "button_secondary_text": "#101214",
    "disabled": "#eaecf0",
    "disabled_text": "#667085",
    "shadow": "rgba(16, 18, 20, 0.18)",
}

DARK_BRAND_PALETTE = {
    "primary": "#c8102e",
    "primary_dark": "#970f22",
    "secondary": "#111315",
    "secondary_light": "#2c3136",
    "steel": "#3d454e",
    "accent": "#f2b93b",
    "background": "#16191d",
    "dialog": "#20252b",
    "panel": "#282e36",
    "field": "#1c2228",
    "border": "#4d5966",
    "border_strong": "#9aa4b2",
    "muted": "#c0c7d1",
    "text": "#f4f7fa",
    "on_primary": "#ffffff",
    "on_accent": "#111827",
    "on_dark": "#f5f7fa",
    "button_secondary": "#303842",
    "button_secondary_text": "#f4f7fa",
    "disabled": "#3a424d",
    "disabled_text": "#aab3bf",
    "shadow": "rgba(0, 0, 0, 0.35)",
}


def normalize_theme_mode(mode: str | None) -> str:
    """Normaliza la preferencia visual y mantiene el modo claro por defecto."""

    return THEME_DARK if mode == THEME_DARK else THEME_LIGHT


def get_theme_palette(mode: str | None = None) -> dict[str, str]:
    """Devuelve los tokens de color del modo solicitado."""

    return DARK_BRAND_PALETTE if normalize_theme_mode(mode) == THEME_DARK else BRAND_PALETTE


def current_theme_mode() -> str:
    """Lee el modo activo de la aplicación Qt, si ya fue inicializada."""

    app = QApplication.instance()
    if app is None:
        return THEME_LIGHT
    return normalize_theme_mode(app.property(THEME_SETTING_KEY))


def get_brand_palette(mode: str | None = None) -> QPalette:
    """Devuelve una paleta explícita para asegurar legibilidad en todas las ventanas."""

    p = get_theme_palette(mode)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(p["background"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(p["text"]))
    palette.setColor(QPalette.ColorRole.Base, QColor(p["field"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(p["panel"]))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(p["dialog"]))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(p["text"]))
    palette.setColor(QPalette.ColorRole.Text, QColor(p["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(p["panel"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(p["text"]))
    palette.setColor(QPalette.ColorRole.Light, QColor(p["steel"]))
    palette.setColor(QPalette.ColorRole.Midlight, QColor(p["steel"]))
    palette.setColor(QPalette.ColorRole.Mid, QColor(p["border"]))
    palette.setColor(QPalette.ColorRole.Dark, QColor(p["secondary_light"]))
    palette.setColor(QPalette.ColorRole.Shadow, QColor(p["secondary"]))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(p["primary"]))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(p["on_primary"]))
    palette.setColor(QPalette.ColorRole.Link, QColor(p["primary"]))
    palette.setColor(QPalette.ColorRole.LinkVisited, QColor(p["primary_dark"]))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(p["muted"]))
    return palette


def apply_application_theme(application: QApplication, mode: str | None = None) -> str:
    """Aplica y registra el modo visual actual a toda la aplicación Qt."""

    normalized = normalize_theme_mode(mode)
    application.setProperty(THEME_SETTING_KEY, normalized)
    application.setPalette(get_brand_palette(normalized))
    application.setStyleSheet(get_brand_style_sheet(normalized))
    return normalized


def apply_dialog_theme(dialog: QDialog) -> None:
    """Aplica el modo activo a diálogos secundarios del sistema."""

    dialog.setPalette(get_brand_palette(current_theme_mode()))
    dialog.setAutoFillBackground(True)
    dialog.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)


def _get_assets_dir() -> Path:
    """Resuelve la carpeta de recursos visuales en desarrollo y en ejecutable."""

    if getattr(sys, "frozen", False):
        bundle_dir = Path(getattr(sys, "_MEIPASS"))
        return bundle_dir / "src" / "sisalmacen" / "ui" / "assets"
    return Path(__file__).resolve().parent / "assets"


def get_brand_logo_path() -> Path:
    """Devuelve la ruta del logo corporativo principal."""

    return _get_assets_dir() / "brand_logo.png"


def get_app_icon_path() -> Path:
    """Devuelve la ruta del icono principal de la aplicación."""

    return _get_assets_dir() / "app_icon.ico"


def get_app_icon() -> QIcon:
    """Carga el icono principal de la aplicación."""

    icon_path = get_app_icon_path()
    return QIcon(str(icon_path)) if icon_path.exists() else QIcon()


def get_brand_logo_pixmap(*, max_width: int = 220, max_height: int = 88) -> QPixmap:
    """Carga el logo corporativo listo para usarse en la interfaz."""

    logo_path = get_brand_logo_path()
    pixmap = QPixmap(str(logo_path))
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(
        max_width,
        max_height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def get_brand_logo_html(*, size_px: int = 44) -> str:
    """Devuelve el isotipo "R&R" con los colores del logo."""

    black = BRAND_PALETTE["secondary"]
    red = BRAND_PALETTE["primary"]
    return (
        f'<span style="font-size:{size_px}px; font-weight:900; color:{black};">R</span>'
        f'<span style="font-size:{size_px}px; font-weight:900; color:{red};">&amp;</span>'
        f'<span style="font-size:{size_px}px; font-weight:900; color:{black};">R</span>'
    )


def get_brand_style_sheet(mode: str | None = None) -> str:
    """Devuelve la hoja de estilo con identidad industrial del logo de la empresa."""

    p = get_theme_palette(mode)
    return f"""
        QMainWindow {{
            background-color: {p["background"]};
            color: {p["text"]};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }}

        QDialog, QMessageBox, QInputDialog {{
            background-color: {p["dialog"]};
            color: {p["text"]};
        }}

        QDialog QLabel,
        QDialog QCheckBox,
        QDialog QRadioButton,
        QDialog QGroupBox,
        QDialog QFormLayout QLabel,
        QFormLayout QLabel {{
            color: {p["text"]};
            background: transparent;
            font-weight: 600;
        }}

        QWidget {{
            color: {p["text"]};
        }}

        QScrollArea {{
            background: transparent;
            border: none;
        }}

        QScrollArea > QWidget > QWidget {{
            background: transparent;
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 12px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical {{
            background: {p["steel"]};
            border-radius: 5px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {p["primary"]};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        QLabel {{
            color: {p["text"]};
            background: transparent;
        }}

        QDialogButtonBox {{
            background: transparent;
        }}

        QPushButton {{
            background-color: {p["primary"]};
            color: {p["on_primary"]};
            border: 2px solid {p["primary_dark"]};
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 700;
        }}

        QPushButton:hover {{
            background-color: {p["primary_dark"]};
        }}

        QPushButton:focus {{
            border-color: {p["accent"]};
        }}

        QPushButton:!enabled {{
            background-color: #a1a1aa;
            border-color: #71717a;
        }}

        QLineEdit, QTextEdit, QComboBox {{
            background-color: {p["field"]};
            color: {p["text"]};
            border: 1px solid {p["border"]};
            border-radius: 8px;
            padding: 7px 10px;
        }}

        QDialog QLineEdit,
        QDialog QTextEdit,
        QDialog QComboBox,
        QDialog QPlainTextEdit,
        QDialog QDateEdit {{
            background-color: {p["field"]};
            color: {p["text"]};
            border: 1px solid {p["border"]};
            border-radius: 8px;
            padding: 7px 10px;
        }}

        QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
        QDialog QLineEdit:focus, QDialog QTextEdit:focus, QDialog QComboBox:focus,
        QDialog QPlainTextEdit:focus, QDialog QDateEdit:focus {{
            border: 2px solid {p["primary"]};
        }}

        QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled,
        QDateEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {p["disabled"]};
            color: {p["disabled_text"]};
            border-color: {p["border"]};
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left: 1px solid {p["border"]};
        }}

        QGroupBox {{
            background: {p["panel"]};
            border: 1px solid {p["border"]};
            border-top: 4px solid {p["accent"]};
            border-radius: 10px;
            margin-top: 14px;
            padding: 14px 10px 10px 10px;
            font-weight: 700;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 8px;
            color: {p["secondary"]};
        }}

        /* Barra superior de marca */
        #brand-bar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {p["secondary"]},
                stop:1 {p["secondary_light"]});
            border-bottom: 4px solid {p["primary"]};
        }}

        #brand-logo {{
            background-color: {p["panel"]};
            border: 2px solid {p["accent"]};
            border-radius: 10px;
            padding: 0 8px;
        }}

        #brand-name {{
            font-size: 20px;
            font-weight: 800;
            color: {p["on_dark"]};
        }}

        #brand-tagline {{
            font-size: 11px;
            font-weight: 700;
            color: {p["on_dark"]};
        }}

        #brand-badge {{
            background: {p["accent"]};
            color: {p["on_accent"]};
            border-radius: 10px;
            padding: 4px 12px;
            font-weight: 800;
        }}

        /* Navegación lateral */
        #sidebar {{
            background: {p["secondary"]};
            border-radius: 12px;
            border-bottom: 4px solid {p["accent"]};
        }}

        #sidebar-caption {{
            color: {p["on_dark"]};
            font-size: 11px;
            font-weight: 700;
        }}

        #sidebar-hint {{
            color: {p["on_dark"]};
            font-size: 12px;
        }}

        #navigation {{
            background: transparent;
            border: none;
            outline: none;
            color: {p["on_dark"]};
            font-size: 14px;
        }}

        #navigation::item {{
            padding: 11px 12px;
            margin: 2px 0;
            border-radius: 8px;
            border-left: 4px solid transparent;
            color: {p["on_dark"]};
        }}

        #navigation::item:hover {{
            background: {p["secondary_light"]};
        }}

        #navigation::item:selected {{
            background: {p["primary"]};
            border-left: 4px solid {p["accent"]};
            color: {p["on_primary"]};
            font-weight: 700;
        }}

        /* Encabezado de cada página */
        #page-header {{
            background: {p["secondary"]};
            border-radius: 12px;
            border-bottom: 4px solid {p["accent"]};
        }}

        #page-title {{
            font-size: 24px;
            font-weight: 800;
            color: {p["on_dark"]};
        }}

        #page-subtitle {{
            font-size: 13px;
            color: {p["on_dark"]};
        }}

        /* Tarjetas */
        #stat-card {{
            background: {p["panel"]};
            border: 1px solid {p["border"]};
            border-top: 4px solid {p["primary"]};
            border-radius: 10px;
        }}

        #card-title {{
            font-size: 12px;
            font-weight: 700;
            color: {p["muted"]};
        }}

        #card-value {{
            font-size: 26px;
            font-weight: 800;
            color: {p["secondary"]};
        }}

        #card-subtitle {{
            font-size: 12px;
            color: {p["muted"]};
        }}

        #info-label {{
            font-size: 12px;
            color: {p["muted"]};
        }}

        #info-value {{
            font-size: 13px;
            color: {p["text"]};
        }}

        #bullet {{
            color: {p["secondary_light"]};
        }}

        QStatusBar {{
            background: {p["secondary"]};
            color: {p["on_dark"]};
            border-top: 3px solid {p["primary"]};
        }}

        QStatusBar QLabel {{
            color: {p["on_dark"]};
        }}

        QMenuBar {{
            background: {p["secondary"]};
            color: {p["on_dark"]};
        }}

        QMenuBar::item {{
            padding: 6px 12px;
            background: transparent;
        }}

        QMenuBar::item:selected {{
            background: {p["primary"]};
        }}

        QMenu {{
            background: {p["field"]};
            color: {p["text"]};
            border: 1px solid {p["border"]};
        }}

        QMenu::item {{
            padding: 6px 24px;
        }}

        QMenu::item:selected {{
            background: {p["primary"]};
            color: {p["on_primary"]};
        }}

        QPushButton[variant="secondary"] {{
            background-color: {p["button_secondary"]};
            color: {p["button_secondary_text"]};
            border-color: {p["border_strong"]};
        }}

        QPushButton[variant="secondary"]:hover {{
            background-color: {p["steel"]};
            border-color: {p["secondary_light"]};
        }}

        QPushButton[variant="secondary"]:!enabled, QPushButton:!enabled {{
            background-color: #a1a1aa;
            border-color: #71717a;
        }}

        QToolButton {{
            background-color: {p["secondary_light"]};
            color: white;
            border: 2px solid {p["secondary"]};
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 700;
        }}

        QToolButton:hover {{
            background-color: {p["secondary"]};
        }}

        QToolButton::menu-indicator {{
            image: none;
        }}

        QDateEdit, QPlainTextEdit, QTextBrowser {{
            background: {p["field"]};
            color: {p["text"]};
            border: 1px solid {p["border"]};
            border-radius: 8px;
            padding: 6px 8px;
        }}

        QComboBox QAbstractItemView {{
            background: {p["field"]};
            color: {p["text"]};
            selection-background-color: {p["primary"]};
            selection-color: #ffffff;
            border: 1px solid {p["border"]};
        }}

        QCheckBox {{
            spacing: 8px;
        }}

        QTableView {{
            background: {p["field"]};
            alternate-background-color: {p["panel"]};
            color: {p["text"]};
            gridline-color: {p["border"]};
            border: 1px solid {p["border"]};
            border-radius: 8px;
            selection-background-color: {p["primary"]};
            selection-color: #ffffff;
        }}

        QHeaderView::section {{
            background: {p["secondary"]};
            color: #ffffff;
            padding: 6px 8px;
            border: none;
            border-right: 1px solid {p["secondary_light"]};
            font-weight: 700;
        }}

        QTabWidget::pane {{
            border: 1px solid {p["border"]};
            border-radius: 8px;
            background: transparent;
            top: -1px;
        }}

        QTabBar::tab {{
            background: {p["secondary_light"]};
            color: {p["on_dark"]};
            padding: 8px 18px;
            margin-right: 3px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 700;
        }}

        QTabBar::tab:selected {{
            background: {p["primary"]};
            border-bottom: 3px solid {p["accent"]};
        }}

        QTabBar::tab:hover:!selected {{
            background: {p["secondary"]};
        }}

        QProgressBar {{
            border: 1px solid {p["border"]};
            border-radius: 6px;
            background: {p["field"]};
            text-align: center;
            height: 16px;
        }}

        QProgressBar::chunk {{
            background: {p["primary"]};
            border-radius: 5px;
        }}

        QToolTip {{
            background: {p["secondary"]};
            color: white;
            border: 1px solid {p["accent"]};
        }}
    """
