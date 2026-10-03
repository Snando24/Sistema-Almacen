"""Pruebas del branding corporativo de la aplicación."""

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QDialog

from sisalmacen.ui.theme import (
    BRAND_PALETTE,
    DARK_BRAND_PALETTE,
    THEME_DARK,
    apply_application_theme,
    apply_dialog_theme,
    get_brand_palette,
    get_brand_style_sheet,
)


def test_brand_palette_has_company_colors() -> None:
    assert BRAND_PALETTE["primary"] == "#d1121e"
    assert BRAND_PALETTE["secondary"] == "#101214"
    assert BRAND_PALETTE["accent"] == "#f2b93b"


def test_brand_palette_uses_accessible_text_tokens() -> None:
    assert BRAND_PALETTE["on_primary"] == "#ffffff"
    assert BRAND_PALETTE["on_accent"] == "#111827"
    assert BRAND_PALETTE["on_dark"] == "#f5f7fa"


def test_brand_palette_overrides_default_qt_colors_for_dialogs() -> None:
    palette = get_brand_palette()
    assert palette.color(QPalette.ColorRole.Window).name().lower() == "#f3f3f1"
    assert palette.color(QPalette.ColorRole.WindowText).name().lower() == "#111827"
    assert palette.color(QPalette.ColorRole.Text).name().lower() == "#111827"


def test_dark_theme_uses_readable_industrial_colors() -> None:
    palette = get_brand_palette(THEME_DARK)

    assert DARK_BRAND_PALETTE["background"] == "#16191d"
    assert palette.color(QPalette.ColorRole.Window).name().lower() == "#16191d"
    assert palette.color(QPalette.ColorRole.Text).name().lower() == "#f4f7fa"


def test_dialog_theme_follows_the_active_application_mode() -> None:
    app = QApplication.instance() or QApplication([])
    apply_application_theme(app, THEME_DARK)
    dialog = QDialog()

    apply_dialog_theme(dialog)

    assert dialog.autoFillBackground()
    assert dialog.palette().color(QPalette.ColorRole.Window).name().lower() == "#16191d"

    apply_application_theme(app)


def test_brand_stylesheet_contains_expected_sections_and_accessible_tokens() -> None:
    css = get_brand_style_sheet()
    assert "QMainWindow" in css
    assert "#brand-bar" in css
    assert "background-color: #d1121e" in css
    assert "color: #f5f7fa" in css
    assert "color: #111827" in css
    assert "QDialog, QMessageBox, QInputDialog" in css
    assert "background-color: #f7f8fa" in css
    assert 'QPushButton[variant="secondary"]' in css


def test_dark_stylesheet_uses_dark_dialog_and_field_surfaces() -> None:
    css = get_brand_style_sheet(THEME_DARK)

    assert "background-color: #20252b" in css
    assert "background-color: #1c2228" in css
