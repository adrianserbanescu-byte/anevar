"""Reconcilierea valorilor din abordarea prin piata si prin cost."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Literal

from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.results import CostResult, MarketResult, ReconciledResult

Metoda = Literal["piata", "cost", "ponderata"]

# ── Reguli GEV 630 la reconcilierea valorilor (SEV 2025) ──────────────────────────────────────────
# Avertismente NON-BLOCANTE (aditive): nu schimba valoarea finala si nu rup compatibilitatea — doar
# se anexeaza la `ReconciledResult.nota` (afisat in raport la generator.py). Evaluatorul autorizat
# decide; aplicatia nu poarta raspundere normativa.
#
#   §107 — INTERZISA stabilirea valorii finale prin media aritmetica SAU ponderata a doua/mai multe
#          valori obtinute din abordari DIFERITE (modul "ponderata" produce exact asta).
#   §108 — Nu se aplica o A DOUA abordare doar FORMAL (ca simpla verificare) cand o singura abordare
#          e adecvata si bazata pe date suficiente — daca a doua abordare e calculata dar nu intra in
#          concluzie, raportul trebuie sa justifice de ce a fost realizata.
#   §109 — Diferenta <=20% intre evaluari nu e a priori neconformitate; >20% intre abordari diferite
#          cere ANALIZA / JUSTIFICARE in raport.

# Pragul §109 — peste aceasta diferenta relativa intre abordari se cere justificare in raport.
_PRAG_DIFERENTA_GEV630 = Decimal("0.20")

_AVERT_107 = (
    "GEV 630 §107: valoarea finala a fost stabilita prin medie ponderata a abordarilor — ghidul "
    "INTERZICE concluzia prin media aritmetica/ponderata a valorilor din abordari diferite; "
    "selectati o singura valoare cu rationament sau justificati incadrarea in exceptia legala."
)


def _eticheta_pereche(a: str, b: str) -> str:
    """Numele prietenoase ale unei perechi de abordari, pentru textul avertismentului §109."""
    return f"{_METODA.get(a, a)} si {_METODA.get(b, b)}"


def _diferenta_relativa(v1: Decimal, v2: Decimal) -> Decimal | None:
    """Diferenta relativa intre doua indicatii (raportata la cea mai mica, pozitiva, non-zero)."""
    baza = min(v1, v2)
    if baza <= 0:
        return None
    return abs(v1 - v2) / baza


def _avert_diferenta_mare(valori: dict[str, Decimal]) -> list[str]:
    """§109 — avertizeaza pentru fiecare pereche de abordari care difera cu > 20% (fara justificare).

    Non-blocant: nu impune nimic, doar semnaleaza ca raportul trebuie sa contina analiza diferentei.
    """
    avertismente: list[str] = []
    nume = list(valori)
    for i in range(len(nume)):
        for j in range(i + 1, len(nume)):
            a, b = nume[i], nume[j]
            dif = _diferenta_relativa(valori[a], valori[b])
            if dif is not None and dif > _PRAG_DIFERENTA_GEV630:
                avertismente.append(
                    f"GEV 630 §109: abordarile {_eticheta_pereche(a, b)} difera cu {dif:.0%} "
                    f"(> 20%) — analizati si justificati diferenta in raport."
                )
    return avertismente


def _avert_a_doua_formala(valori: dict[str, Decimal], metoda_selectata: str) -> list[str]:
    """§108 — cand o singura abordare intra in concluzie dar exista alte abordari CALCULATE, acelea

    pot fi „a doua abordare doar formala" (simpla verificare). Non-blocant: noteaza ca raportul
    trebuie sa justifice de ce au fost realizate (nu se aplica la "ponderata", unde toate contribuie).
    """
    if metoda_selectata == "ponderata" or len(valori) < 2:
        return []
    return [
        "GEV 630 §108: o singura abordare a stabilit valoarea, dar exista si alte abordari calculate "
        "ca indicatie — justificati in raport rolul lor (nu doar verificare formala) sau de ce nu au "
        "fost utilizate."
    ]


def _compune_nota(*parti: str) -> str:
    """Concateneaza notele/avertismentele non-goale intr-un singur text (separator ' ')."""
    return " ".join(p for p in parti if p)


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

    # Abordarile cu valoare (chei consistente cu reconcile_profil: "comparatie" = piata) — baza pentru
    # avertismentele GEV 630 §108/§109 (non-blocante, doar anexate la nota).
    valori: dict[str, Decimal] = {}
    if market_value is not None:
        valori["comparatie"] = market_value
    if cost_value is not None:
        valori["cost"] = cost_value
    avert_dif = _avert_diferenta_mare(valori)        # §109: diferenta > 20% intre abordari

    if metoda == "piata":
        if market_value is not None:
            return ReconciledResult(
                valoare_finala=market_value, metoda_selectata="piata",
                nota=_compune_nota(*_avert_a_doua_formala(valori, "piata"), *avert_dif),
            )
        assert cost_value is not None  # garantat de verificarea both-None de mai sus
        return ReconciledResult(
            valoare_finala=cost_value, metoda_selectata="cost",
            nota="Abordarea prin piata indisponibila; s-a folosit abordarea prin cost.",
        )

    if metoda == "cost":
        if cost_value is not None:
            return ReconciledResult(
                valoare_finala=cost_value, metoda_selectata="cost",
                nota=_compune_nota(*_avert_a_doua_formala(valori, "cost"), *avert_dif),
            )
        assert market_value is not None  # garantat de verificarea both-None de mai sus
        return ReconciledResult(
            valoare_finala=market_value, metoda_selectata="piata",
            nota="Abordarea prin cost indisponibila; s-a folosit abordarea prin piata.",
        )

    # ponderata
    if market_value is None or cost_value is None:
        disponibila = market_value if market_value is not None else cost_value
        metoda_disp: Literal["piata", "cost"] = "piata" if market_value is not None else "cost"
        assert disponibila is not None  # cel putin una e non-None (both-None deja exclus)
        return ReconciledResult(
            valoare_finala=disponibila, metoda_selectata=metoda_disp,
            nota="O abordare indisponibila; ponderarea nu s-a putut aplica.",
        )
    pondere_cost = Decimal("1") - pondere_piata
    valoare = (market_value * pondere_piata + cost_value * pondere_cost).quantize(
        cfg.rotunjire_valoare, rounding=ROUND_HALF_UP)            # E1: rotunjire consistenta
    # §107 (media ponderata interzisa ca CONCLUZIE) + §109 (diferenta > 20%) — non-blocante.
    return ReconciledResult(
        valoare_finala=valoare, metoda_selectata="ponderata",
        nota=_compune_nota(_AVERT_107, *avert_dif),
    )


def aloca_constructii(
    valoare_proprietate: Decimal, valoare_teren: Decimal
) -> Decimal:
    """Alocarea valorii (din rapoarte): valoarea constructiilor = proprietate - teren."""
    return valoare_proprietate - valoare_teren


# Eticheta de metodă întoarsă în ReconciledResult.metoda_selectata.
MetodaSelectata = Literal["piata", "cost", "ponderata", "venit"]

# Maparea numelui de abordare (cost/comparatie/venit) la eticheta de metodă din raport.
_METODA: dict[str, MetodaSelectata] = {"cost": "cost", "comparatie": "piata", "venit": "venit"}


def _eticheta_metoda(abordare: str) -> MetodaSelectata:
    """Maparea sigură nume-abordare -> etichetă de metodă din literal.

    `_METODA` acoperă toate valorile NumeAbordare (cost/comparatie/venit); fallback-ul "piata"
    împiedică o etichetă în afara literalului să ajungă în API/raport pentru un nume neașteptat.
    """
    return _METODA.get(abordare, "piata")


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

    # §109 (non-blocant) — diferenta > 20% intre orice pereche de abordari calculate cere justificare.
    avert_dif = _avert_diferenta_mare(valori)

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
            nota_excl = ""
            if excluse:
                nume_excl = ", ".join(_METODA.get(a, a) for a in excluse)
                nume_pond = ", ".join(_METODA.get(a, a) for a in disponibile)
                nota_excl = (f"Abordarea prin {nume_excl} a fost calculata ca indicatie de valoare, dar NU este "
                             f"inclusa in valoarea ponderata (ponderarea aplicata foloseste {nume_pond}).")
            # §107 (non-blocant) — media ponderata INTERZISA ca valoare de concluzie (vezi _AVERT_107).
            nota = _compune_nota(_AVERT_107, nota_excl, *avert_dif)
            return ReconciledResult(valoare_finala=valoare, metoda_selectata="ponderata", nota=nota)
        # sub doua abordari disponibile -> ponderarea nu se aplica; selectie cu nota
        nota = "Ponderarea nu s-a putut aplica (sub doua abordari disponibile)."
        if primara in valori:
            return ReconciledResult(
                valoare_finala=valori[primara], metoda_selectata=_eticheta_metoda(primara),
                nota=_compune_nota(nota, *_avert_a_doua_formala(valori, "selectie"), *avert_dif),
            )
        abordare_disp = next(iter(valori))
        return ReconciledResult(
            valoare_finala=valori[abordare_disp], metoda_selectata=_eticheta_metoda(abordare_disp),
            nota=_compune_nota(nota, *_avert_a_doua_formala(valori, "selectie"), *avert_dif),
        )

    if primara in valori:
        # §108 (a doua abordare doar formala) + §109 — non-blocante, anexate la nota.
        return ReconciledResult(
            valoare_finala=valori[primara], metoda_selectata=_eticheta_metoda(primara),
            nota=_compune_nota(*_avert_a_doua_formala(valori, "selectie"), *avert_dif),
        )
    # fallback fara ponderi
    abordare_disp = next(iter(valori))
    return ReconciledResult(
        valoare_finala=valori[abordare_disp], metoda_selectata=_eticheta_metoda(abordare_disp),
        nota=_compune_nota(
            f'Abordarea "{primara}" indisponibila; s-a folosit "{abordare_disp}".',
            *_avert_a_doua_formala(valori, "selectie"), *avert_dif),
    )
