"""Conversie si rotunjire monetara consistenta (Decimal)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def to_money(value: float | int | str | Decimal) -> Decimal:
    """Converteste orice numeric la Decimal fara erori de virgula mobila."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def round_lei(value: Decimal) -> Decimal:
    """Rotunjeste la leu intreg (jumatate in sus)."""
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def pct(value: float | int | str | Decimal) -> Decimal:
    """Converteste un procent (ex. 35) la fractie (0.35)."""
    return to_money(value) / Decimal("100")
