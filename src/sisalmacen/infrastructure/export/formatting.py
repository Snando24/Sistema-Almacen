"""Formato común de celdas para CSV y PDF."""

from __future__ import annotations

from datetime import date
from decimal import Decimal


def plain_decimal(value: Decimal) -> str:
    """Decimal sin exponente ni ceros finales."""

    text = format(value.normalize(), "f")
    return text


def money_text(value: Decimal) -> str:
    two = value.quantize(Decimal("0.01"))
    if two == value:
        return format(two, "f")
    return format(value.quantize(Decimal("0.0001")), "f")


def cell_text(value: object, kind: str) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return money_text(value) if kind == "money" else plain_decimal(value)
    if isinstance(value, date):
        return value.isoformat()
    return str(value)
