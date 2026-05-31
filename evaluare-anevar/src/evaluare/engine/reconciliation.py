"""Reconcilierea valorilor din abordarea prin piata si prin cost."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from evaluare.models.results import CostResult, MarketResult, ReconciledResult

Metoda = Literal["piata", "cost", "ponderata"]


def reconcile(
    market: Optional[MarketResult],
    cost: Optional[CostResult],
    metoda: Metoda = "piata",
    pondere_piata: Decimal = Decimal("0.5"),
) -> ReconciledResult:
    """Selecteaza valoarea finala din cele doua abordari.

    - "piata": foloseste valoarea de piata
    - "cost": foloseste valoarea prin cost (teren + CIN)
    - "ponderata": medie ponderata (pondere_piata pentru piata)
    Daca abordarea ceruta nu e disponibila, cade pe cealalta si noteaza motivul.
    """
    market_value = market.valoare_piata if market is not None else None
    cost_value = cost.valoare_cost if cost is not None else None

    if market_value is None and cost_value is None:
        raise ValueError("Nicio abordare nu produce o valoare utilizabila.")

    if metoda == "piata":
        if market_value is not None:
            return ReconciledResult(valoare_finala=market_value, metoda_selectata="piata")
        return ReconciledResult(
            valoare_finala=cost_value, metoda_selectata="cost",
            nota="Abordarea prin piata indisponibila; s-a folosit abordarea prin cost.",
        )

    if metoda == "cost":
        if cost_value is not None:
            return ReconciledResult(valoare_finala=cost_value, metoda_selectata="cost")
        return ReconciledResult(
            valoare_finala=market_value, metoda_selectata="piata",
            nota="Abordarea prin cost indisponibila; s-a folosit abordarea prin piata.",
        )

    # ponderata
    if market_value is None or cost_value is None:
        disponibila = market_value if market_value is not None else cost_value
        metoda_disp = "piata" if market_value is not None else "cost"
        return ReconciledResult(
            valoare_finala=disponibila, metoda_selectata=metoda_disp,
            nota="O abordare indisponibila; ponderarea nu s-a putut aplica.",
        )
    pondere_cost = Decimal("1") - pondere_piata
    valoare = market_value * pondere_piata + cost_value * pondere_cost
    return ReconciledResult(valoare_finala=valoare, metoda_selectata="ponderata")
