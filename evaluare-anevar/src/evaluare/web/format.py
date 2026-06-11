"""Formatare numerica partajata pentru paginile web."""
from __future__ import annotations

from decimal import Decimal


def fmt_numar(v: Decimal) -> str:
    """Format ro-RO cu 2 zecimale: mii separate cu '.', zecimale cu ','. Ex: 316000 -> '316.000,00'.

    Defense-in-depth: valori extreme (ex. dintr-un curs valutar absurd) pot face `quantize` sa
    arunce decimal.InvalidOperation/Overflow (ArithmeticError) -> 500. Aici prindem si degradam
    gratios la valoarea ne-quantizata (sau '—' daca nici aceea nu se poate reprezenta), nu cracam
    pagina. Marginirea reala a inputului se face in modele (ex. EvaluationMeta.curs_valutar).
    """
    try:
        q = v.quantize(Decimal("0.01"))
        s = f"{q:,.2f}"                              # en: 316,000.00
    except (ArithmeticError, ValueError):
        try:
            s = f"{v:,.2f}"                          # fallback fara quantize
        except (ArithmeticError, ValueError):
            return "—"
    return s.replace(",", "·").replace(".", ",").replace("·", ".")
