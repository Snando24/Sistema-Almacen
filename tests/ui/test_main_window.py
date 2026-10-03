"""Pruebas de la ventana principal con servicios reales sobre una BD temporal."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from sisalmacen.domain.inventory import MovementLine, MovementRequest
from sisalmacen.ui.main_window import SECTION_LABELS, MainWindow
from sisalmacen.ui.theme import THEME_DARK, THEME_LIGHT, THEME_SETTING_KEY, get_brand_style_sheet


@pytest.fixture
def window(services):  # type: ignore[no-untyped-def]
    QApplication.instance() or QApplication([])
    win = MainWindow(
        services=services, database_label="var/sisalmacen.sqlite3", logs_label="logs/sisalmacen.log"
    )
    yield win
    win.close()


def test_navigation_has_every_section(window) -> None:  # type: ignore[no-untyped-def]
    assert window._navigation.count() == window._stacked_pages.count() == len(SECTION_LABELS) == 7
    assert window._navigation.currentRow() == 0
    expected = {
        1: "productos-page",
        2: "movimientos-page",
        3: "csv-page",
        4: "reportes-page",
        5: "catalogos-page",
        6: "administracion-page",
    }
    for row, name in expected.items():
        window._navigation.setCurrentRow(row)
        assert window._stacked_pages.currentIndex() == row
        assert window._stacked_pages.currentWidget().objectName() == name


def test_window_is_local_without_login(window) -> None:  # type: ignore[no-untyped-def]
    texts = [label.text() for label in window.findChildren(QLabel)]
    assert any("MODO LOCAL" in text for text in texts)
    assert not any("contraseña" in text.lower() for text in texts)


def test_theme_toggle_persists_and_applies_dark_mode(window, services) -> None:  # type: ignore[no-untyped-def]
    assert window._theme_toggle is not None
    assert window._theme_mode == THEME_LIGHT

    window._toggle_theme()

    assert window._theme_mode == THEME_DARK
    assert services.settings.read_all()[THEME_SETTING_KEY] == THEME_DARK
    assert "Modo claro" in window._theme_toggle.text()

    window._toggle_theme()


def test_products_page_lists_and_filters_by_alert(window, services, make_product) -> None:  # type: ignore[no-untyped-def]
    product_id = make_product("P-1", stock_minimo=Decimal(5))
    services.movements.register(
        MovementRequest("ENT_COMPRA", date(2026, 1, 1), (MovementLine(product_id, Decimal(3)),))
    )
    page = window._products
    page.refresh()
    assert page._model.rowCount() == 1

    page.show_alert("BAJO_MINIMO")
    assert page._model.rowCount() == 1
    page.show_alert("SIN_STOCK")
    assert page._model.rowCount() == 0


def test_dashboard_navigation_opens_products_with_alert(window) -> None:  # type: ignore[no-untyped-def]
    window._dashboard.navigate.emit("productos", "SIN_STOCK")
    assert window._stacked_pages.currentIndex() == 1


def test_refresh_reloads_dashboard_values(window, make_product) -> None:  # type: ignore[no-untyped-def]
    make_product("P-1")
    window._navigation.setCurrentRow(0)
    window._refresh_current()
    texts = {label.text() for label in window._dashboard.findChildren(QLabel)}
    assert "1" in texts


def test_stylesheet_uses_logo_colors() -> None:
    css = get_brand_style_sheet()
    for token in ("#navigation::item:selected", "#stat-card", "#f2b93b", "#d1121e", "#101214"):
        assert token in css
