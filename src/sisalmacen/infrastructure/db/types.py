"""TypeDecorators para cantidades y dinero escalados."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy.types import Integer, TypeDecorator


class ScaledDecimal(TypeDecorator[int]):
    """Persiste decimales como enteros escalados."""

    impl = Integer
    cache_ok = True

    def __init__(self, scale: int) -> None:
        super().__init__()
        self.scale = scale
        self.multiplier = Decimal(10) ** scale
        self.quantizer = Decimal(1) / self.multiplier

    def process_bind_param(self, value: Decimal | None, dialect: Any) -> int | None:
        if value is None:
            return None
        quantized = value.quantize(self.quantizer, rounding=ROUND_HALF_UP)
        return int(quantized * self.multiplier)

    def process_result_value(self, value: int | None, dialect: Any) -> Decimal | None:
        if value is None:
            return None
        return (Decimal(value) / self.multiplier).quantize(self.quantizer)


class ScaledQuantity(ScaledDecimal):
    """Cantidad con precisión de 3 decimales."""

    cache_ok = True

    def __init__(self) -> None:
        super().__init__(scale=3)


class ScaledMoney(ScaledDecimal):
    """Dinero con precisión de 4 decimales."""

    cache_ok = True

    def __init__(self) -> None:
        super().__init__(scale=4)
