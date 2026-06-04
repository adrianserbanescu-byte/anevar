"""Formatare numerica partajata pentru paginile web."""
from __future__ import annotations

from decimal import Decimal


def fmt_numar(v: Decimal) -> str:
    """Format ro-RO cu 2 zecimale: mii separate cu '.', zecimale cu ','. Ex: 316000 -> '316.000,00'."""
    q = v.quantize(Decimal("0.01"))
    s = f"{q:,.2f}"                                  # en: 316,000.00
    return s.replace(",", "·").replace(".", ",").replace("·", ".")
