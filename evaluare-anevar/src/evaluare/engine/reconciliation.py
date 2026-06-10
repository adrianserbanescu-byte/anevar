"""Reconcilierea valorilor din abordarea prin piata si prin cost."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.results import CostResult, MarketResult, ReconciledResult

Metoda = Literal["piata", "cost", "ponderata"]


def reconcile(
    market: MarketResult | None,
    cost: CostResult | None,
    metoda: Metoda = "piata",
    pondere_piata: Decimal | None = None,
    cfg: MetodologieConfig = IMPLICIT,
) -> ReconciledResult:
    """Selecteaza valoarea finala din cele doua abordari.

    - "piata": foloseste valoarea de piata
    - "cost": foloseste valoarea prin cost (teren + CIN)
    - "ponderata": medie ponderata (pondere_piata pentru piata)
    Daca abordarea ceruta nu e disponibila, cade pe cealalta si noteaza motivul.
    `pondere_piata` None -> default din config (M3). Valoarea ponderata se rotunjeste la pasul din config (E1).
    """
    if pondere_piata is None:
        pondere_piata = cfg.pondere_piata_default
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
    valoare = (market_value * pondere_piata + cost_value * pondere_cost).quantize(
        cfg.rotunjire_valoare, rounding=ROUND_HALF_UP)            # E1: rotunjire consistenta
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
    ponderi: dict[str, Decimal] | None = None,
    cfg: MetodologieConfig = IMPLICIT,
) -> ReconciledResult:
    """Reconciliază o listă de RezultatAbordare după profil.

    - `primara`: numele abordării preferate (cost/comparatie/venit).
    - `ponderi`: dacă e dat (dict nume->Decimal), face medie ponderată pe abordările cu valoare.
    Dacă primara lipsește, cade pe prima abordare disponibilă și notează motivul.
    """
    # Rotunjim valoarea fiecarei abordari la pasul din config (E1) -> valoarea finala e rotunjita
    # consistent pe TOATE ramurile (piata/cost/ponderata), nu doar la ponderare. M2: media top-N poate
    # avea multe zecimale; fara asta, valoarea bruta (ex. 28 cifre) ar ajunge in API + jurnalul de audit.
    valori = {r.abordare: r.valoare.quantize(cfg.rotunjire_valoare, rounding=ROUND_HALF_UP)
              for r in rezultate if r.valoare is not None}
    if not valori:
        raise ValueError("Nicio abordare nu produce o valoare utilizabilă.")

    if ponderi:
        disponibile = [a for a in ponderi if a in valori]
        total_pondere = sum(ponderi[a] for a in disponibile)
        if len(disponibile) >= 2 and total_pondere > 0:
            valoare = (sum(valori[a] * ponderi[a] for a in disponibile) / total_pondere
                       ).quantize(cfg.rotunjire_valoare, rounding=ROUND_HALF_UP)   # E1
            # Transparenta (decizia Adi, optiunea b): daca o abordare a fost CALCULATA ca indicatie dar
            # nu intra in ponderare (ex. venitul la o ponderare piata/cost), o declaram EXPLICIT in nota,
            # ca valoarea finala sa nu diverga TACUT de indicatiile aratate in raport.
            excluse = [a for a in valori if a not in ponderi]
            nota = ""
            if excluse:
                nume_excl = ", ".join(_METODA.get(a, a) for a in excluse)
                nume_pond = ", ".join(_METODA.get(a, a) for a in disponibile)
                nota = (f"Abordarea prin {nume_excl} a fost calculata ca indicatie de valoare, dar NU este "
                        f"inclusa in valoarea ponderata (ponderarea aplicata foloseste {nume_pond}).")
            return ReconciledResult(valoare_finala=valoare, metoda_selectata="ponderata", nota=nota)
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
