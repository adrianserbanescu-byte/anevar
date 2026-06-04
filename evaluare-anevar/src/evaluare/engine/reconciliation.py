"""Reconcilierea valorilor din abordarea prin piata si prin cost."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, Optional

from evaluare.models.results import CostResult, MarketResult, ReconciledResult
from evaluare.engine.abordari import RezultatAbordare

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


def aloca_constructii(
    valoare_proprietate: Decimal, valoare_teren: Decimal
) -> Decimal:
    """Alocarea valorii (din rapoarte): valoarea constructiilor = proprietate - teren."""
    return valoare_proprietate - valoare_teren


# Maparea numelui de abordare la eticheta de metodă din raport.
_METODA = {"cost": "cost", "comparatie": "piata", "venit": "venit"}


def reconcile_profil(
    rezultate: list[RezultatAbordare],
    primara: str,
    ponderi: Optional[dict[str, Decimal]] = None,
) -> ReconciledResult:
    """Reconciliază o listă de RezultatAbordare după profil.

    - `primara`: numele abordării preferate (cost/comparatie/venit).
    - `ponderi`: dacă e dat (dict nume->Decimal), face medie ponderată pe abordările cu valoare.
    Dacă primara lipsește, cade pe prima abordare disponibilă și notează motivul.
    """
    valori = {r.abordare: r.valoare for r in rezultate if r.valoare is not None}
    if not valori:
        raise ValueError("Nicio abordare nu produce o valoare utilizabilă.")

    if ponderi:
        disponibile = [a for a in ponderi if a in valori]
        total_pondere = sum(ponderi[a] for a in disponibile)
        if len(disponibile) >= 2 and total_pondere > 0:
            valoare = (sum(valori[a] * ponderi[a] for a in disponibile) / total_pondere
                       ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return ReconciledResult(valoare_finala=valoare, metoda_selectata="ponderata")
        # sub doua abordari disponibile -> ponderarea nu se aplica; selectie cu nota
        nota = "Ponderarea nu s-a putut aplica (sub doua abordari disponibile)."
        if primara in valori:
            return ReconciledResult(valoare_finala=valori[primara],
                                    metoda_selectata=_METODA.get(primara, primara), nota=nota)
        abordare_disp = next(iter(valori))
        return ReconciledResult(valoare_finala=valori[abordare_disp],
                                metoda_selectata=_METODA.get(abordare_disp, abordare_disp), nota=nota)

    if primara in valori:
        return ReconciledResult(valoare_finala=valori[primara],
                                metoda_selectata=_METODA.get(primara, primara))
    # fallback fara ponderi
    abordare_disp = next(iter(valori))
    return ReconciledResult(
        valoare_finala=valori[abordare_disp], metoda_selectata=_METODA.get(abordare_disp, abordare_disp),
        nota=f'Abordarea "{primara}" indisponibila; s-a folosit "{abordare_disp}".',
    )
