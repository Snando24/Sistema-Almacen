"""Pruebas de contraste y jerarquía visual en formularios modales."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication, QDialogButtonBox

from sisalmacen.ui.dialogs.product_dialog import ProductDialog


def test_product_dialog_uses_light_surface_and_neutral_cancel_action(services) -> None:  # type: ignore[no-untyped-def]
    QApplication.instance() or QApplication([])
    dialog = ProductDialog(services)

    buttons = dialog.findChild(QDialogButtonBox)
    assert buttons is not None
    cancel = buttons.button(QDialogButtonBox.StandardButton.Cancel)

    assert dialog.autoFillBackground()
    assert cancel.property("variant") == "secondary"
