"""Config de METODOLOGIE — alegerile pe care evaluatorul (Adi) le poate seta, cu default-uri sensibile.

Vine din auditul #3 (`docs/audit-metodologie-3-2026-06-08.md`): alegeri care NU sunt univoce în
SEV 2025 / GEV 520/630 → în loc să le hardcodăm, le expunem ca OPȚIUNI cu un default bun, pe care
evaluatorul le poate schimba (exact ca ponderile D1). Motorul citește acest config; UI-ul de selecție
îl adaugă C ulterior. NU decidem metodologia în cod.

Scop confirmat de Adi: M1 (selecție teren) + M3 (pondere piață/cost) + M5 (praguri validare) + E1
(rotunjire). M2 (reconciliere top-N) și M4 (metodă depreciere) rămân pe default-ul actual.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class MetodologieConfig:
    """Parametrii de metodologie configurabili. Default = alegere sensibilă, override-abilă de evaluator."""

    # M2 — câte comparabile (cele mai similare, top-down) se MEDIAZĂ pentru valoare. Default 3 =
    # minimul legal de comparabile (decizia Adi). 1 = selecția comparabilului unic cel mai similar
    # (comportamentul istoric, validat pe grilele GBF). Se aplică la abordarea prin piață ȘI la teren.
    nr_comparabile_medie: int = 3

    # M1 — la TEREN, includem ajustările VALORICE (EUR) în criteriul de selecție (ajustarea brută)?
    # Default True = consistent cu abordarea prin piață (casa le numără). False = doar procentuale (vechi).
    teren_selectie_include_eur: bool = True

    # M3 — pondere implicită a abordării prin PIAȚĂ la reconcilierea „ponderată" (restul = cost).
    pondere_piata_default: Decimal = Decimal("0.5")

    # M5 — praguri de validare a comparabilelor.
    limita_ajustare_bruta: Decimal = Decimal("0.25")     # alertă peste această ajustare brută
    prag_outlier: Decimal = Decimal("0.50")              # alertă outlier la deviația de mediană
    min_comparabile: int = 3                              # minim comparabile (blochează sub)

    # E1 — pasul de rotunjire a valorii finale reconciliate (consistent între reconcile/reconcile_profil).
    rotunjire_valoare: Decimal = Decimal("0.01")


IMPLICIT = MetodologieConfig()

# Câmpurile expuse ca opțiuni (pt API/UI) + tipul lor — sursă unică pentru validare/serializare.
CAMPURI = {
    "nr_comparabile_medie": int,
    "teren_selectie_include_eur": bool,
    "pondere_piata_default": Decimal,
    "limita_ajustare_bruta": Decimal,
    "prag_outlier": Decimal,
    "min_comparabile": int,
    "rotunjire_valoare": Decimal,
}


# Limite acceptabile per câmp — în afara lor valoarea e RESPINSĂ (cade pe default). Apără contra
# valorilor degenerate care ar brick-ui calculul (verificare adversarială #3): `rotunjire_valoare`
# extrem → `quantize` InvalidOperation (500) sau rotunjire la 0 (garanție ZERO); `min_comparabile=0`
# → `median([])` (500); `pondere_piata` > 1 → pondere negativă / valoare nonsens.
_LIMITE: dict[str, tuple] = {
    "pondere_piata_default": (Decimal("0"), Decimal("1")),           # [0, 1]
    "limita_ajustare_bruta": (Decimal("0.0001"), Decimal("100")),    # (0, 100]
    "prag_outlier": (Decimal("0.0001"), Decimal("100")),
    "rotunjire_valoare": (Decimal("0.0001"), Decimal("1000000")),    # pas de rotunjire sanatos
    "min_comparabile": (1, 100),
    "nr_comparabile_medie": (1, 20),                                 # 1 = selectie unica; >1 = medie top-N
}


def _in_limite(camp: str, v) -> bool:
    lim = _LIMITE.get(camp)
    return lim is None or lim[0] <= v <= lim[1]


def din_override(override: dict | None) -> MetodologieConfig:
    """Construiește un config din override-ul user (doar câmpuri cunoscute, tipuri + LIMITE validate).

    Câmpurile lipsă/invalide/în afara limitelor cad pe default. Decimal acceptă int/float/str numeric
    FINIT și în interval; bool acceptă bool; int acceptă int în interval. Astfel un fișier corupt sau o
    valoare degenerată NU crapă calculul — degradează grațios la default.
    """
    if not isinstance(override, dict):
        return IMPLICIT
    valori: dict = {}
    for camp, tip in CAMPURI.items():
        if camp not in override:
            continue
        v = override[camp]
        try:
            if tip is bool:
                if isinstance(v, bool):
                    valori[camp] = v
            elif tip is int:
                if isinstance(v, int) and not isinstance(v, bool) and _in_limite(camp, v):
                    valori[camp] = v
            elif tip is Decimal:
                if isinstance(v, bool):
                    continue
                if isinstance(v, (int, float, str)):
                    d = Decimal(str(v))
                    if d.is_finite() and _in_limite(camp, d):
                        valori[camp] = d
        except (ValueError, ArithmeticError):
            continue
    return MetodologieConfig(**{**_ca_dict(IMPLICIT), **valori})


def ca_dict(cfg: MetodologieConfig) -> dict:
    """Serializare prietenoasă (Decimal → str) pentru API/persistență."""
    return {
        "nr_comparabile_medie": cfg.nr_comparabile_medie,
        "teren_selectie_include_eur": cfg.teren_selectie_include_eur,
        "pondere_piata_default": str(cfg.pondere_piata_default),
        "limita_ajustare_bruta": str(cfg.limita_ajustare_bruta),
        "prag_outlier": str(cfg.prag_outlier),
        "min_comparabile": cfg.min_comparabile,
        "rotunjire_valoare": str(cfg.rotunjire_valoare),
    }


def _ca_dict(cfg: MetodologieConfig) -> dict:
    """Câmpurile ca dict tipat (pt reconstrucția dataclass-ului)."""
    return {
        "nr_comparabile_medie": cfg.nr_comparabile_medie,
        "teren_selectie_include_eur": cfg.teren_selectie_include_eur,
        "pondere_piata_default": cfg.pondere_piata_default,
        "limita_ajustare_bruta": cfg.limita_ajustare_bruta,
        "prag_outlier": cfg.prag_outlier,
        "min_comparabile": cfg.min_comparabile,
        "rotunjire_valoare": cfg.rotunjire_valoare,
    }
