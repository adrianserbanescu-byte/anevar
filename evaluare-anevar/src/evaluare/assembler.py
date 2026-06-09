"""Orchestrarea motoarelor: din datele de intrare -> ReportContext complet."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from evaluare.ai.narrative import NarrativeClient, generate_narrative
from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.land import evaluate_land
from evaluare.engine.market import evaluate_market
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.engine.reconciliation import aloca_constructii, reconcile_profil
from evaluare.engine.validation import (
    Issue,
    valideaza_comparabile,
    valideaza_depreciere,
    valideaza_proprietate,
)
from evaluare.engine.venit import DateDCF, DateVenit, evalueaza_dcf, evalueaza_venit
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.report_context import ReportContext
from evaluare.profil import (
    AGRICOL,
    APARTAMENT_GARANTARE,
    ASIGURARE,
    CASA_TEREN_GARANTARE,
    IMPOZITARE,
    INDUSTRIAL,
    LITIGII,
    RAPORTARE_FINANCIARA,
    SPECIAL,
    ProfilEvaluare,
)
from evaluare.report.anonymizer import build_anonymizer

# Maparea tipului ales în wizard (Pas 2) la profilul de evaluare. Profilul determină
# framing-ul raportului (tip activ, abordări declarate, ghid GEV), NU formula numerică
# (aceea e condusă de „Metodă" la Pas 4). Tipurile fără intrare rămân pe profilul implicit.
PROFIL_DUPA_TIP: dict[str, ProfilEvaluare] = {
    "casa": CASA_TEREN_GARANTARE,
    "apartament": APARTAMENT_GARANTARE,
    "industrial": INDUSTRIAL,
    "agricol": AGRICOL,
    "special": SPECIAL,
}

# Scopuri speciale (≠ garantare): determină tipul valorii + ghidul GEV (raportare → valoare
# justă/GEV 500, asigurare → valoare de asigurare, etc.). La „garantare" decide TIPUL.
PROFIL_DUPA_SCOP: dict[str, ProfilEvaluare] = {
    "raportare_financiara": RAPORTARE_FINANCIARA,
    "asigurare": ASIGURARE,
    "impozitare": IMPOZITARE,
    "litigii": LITIGII,
}


def rezolva_profil(tip: str | None, scop: str | None,
                   implicit: ProfilEvaluare) -> ProfilEvaluare:
    """Profilul efectiv din tip (Pas 2) + scop (Pas 1).

    Scop special -> profilul scopului (tip valoare + ghid), păstrând tipul de activ ales.
    Scop garantare/absent -> profilul tipului ales. Necunoscut -> implicit.
    """
    pe_scop = PROFIL_DUPA_SCOP.get(scop or "")
    if pe_scop is not None:
        pe_tip = PROFIL_DUPA_TIP.get(tip or "")
        if pe_tip is not None:
            return pe_scop.model_copy(update={"tip_activ": pe_tip.tip_activ})
        return pe_scop
    return PROFIL_DUPA_TIP.get(tip or "", implicit)


class EvaluationInput(BaseModel):
    """Datele de intrare ale unei evaluari (corpul cererii web)."""

    meta: EvaluationMeta
    land: LandData
    building: BuildingData
    comparables: list[Comparable] = Field(default_factory=list)
    land_comparables: list[LandComparable] = Field(default_factory=list)
    valoare_teren: Decimal | None = None
    metoda: Literal["piata", "cost", "ponderata", "venit", "dcf"] = "cost"
    pondere_piata: Decimal = Field(default=Decimal("0.5"), ge=0, le=1)
    # Tipul ales în wizard (Pas 2): casa/apartament/industrial/agricol/special. Dacă e dat,
    # determină profilul (suprascrie `profil`). Lipsă -> se folosește `profil` (implicit casă).
    tip_proprietate: str | None = None
    # Scopul ales (Pas 1): garantare/raportare_financiara/asigurare/impozitare/litigii.
    # Scopurile speciale determină profilul (tip valoare + ghid GEV). Vezi rezolva_profil.
    scop: str | None = None
    profil: ProfilEvaluare = CASA_TEREN_GARANTARE
    date_venit: DateVenit | None = None
    date_dcf: DateDCF | None = None
    photos: list[str] = Field(default_factory=list)   # data-URL base64 pentru anexa foto
    documente: list[str] = Field(default_factory=list)  # data-URL base64 (scanuri CF/cadastral) -> Anexa 3


def valideaza(inp: EvaluationInput, cfg: MetodologieConfig = IMPLICIT) -> list[Issue]:
    """Ruleaza validarile SEV relevante pentru metoda aleasa.

    - proprietate (suprafete, Au<=Acd) si depreciere: mereu;
    - comparabile (min 3, outlier, limita ajustare): doar la metodele care folosesc piata.
    `cfg` = praguri de metodologie configurabile (M5).
    """
    issues: list[Issue] = []
    issues += valideaza_proprietate(inp.land, inp.building)
    issues += valideaza_depreciere(inp.building)
    if inp.metoda in ("piata", "ponderata"):
        issues += valideaza_comparabile(inp.comparables, cfg)
    return issues


def construieste_context(
    inp: EvaluationInput, client: NarrativeClient | None,
    cfg: MetodologieConfig = IMPLICIT,
) -> ReportContext:
    """Ruleaza motoarele si asambleaza ReportContext (inclusiv narativul).

    `cfg` = config de metodologie (M1 selectie teren, M3 pondere, E1 rotunjire); default = IMPLICIT.
    """
    # Profil efectiv din tip (Pas 2) + scop (Pas 1) — framing raport, nu formula numerică.
    profil = rezolva_profil(inp.tip_proprietate, inp.scop, inp.profil)
    # Teren: daca exista comparabile de teren, valoarea se calculeaza prin grila;
    # altfel se foloseste valoarea introdusa manual.
    land_result = None
    valoare_teren = inp.valoare_teren
    if inp.land_comparables:
        land_result = evaluate_land(inp.land_comparables, inp.land.suprafata, cfg)
        valoare_teren = land_result.valoare_teren

    cost_result = None
    if inp.building.elements:
        cost_result = evaluate_cost(inp.building, valoare_teren=valoare_teren)

    market_result = None
    if inp.comparables:
        market_result = evaluate_market(inp.comparables, suprafata_subiect=inp.building.acd, cfg=cfg)

    venit_result = None
    if inp.date_venit is not None:
        venit_result = evalueaza_venit(inp.date_venit)

    dcf_valoare = None
    if inp.date_dcf is not None:
        dcf_valoare = evalueaza_dcf(inp.date_dcf.fluxuri, inp.date_dcf.rata_actualizare,
                                    inp.date_dcf.valoare_reziduala)

    rezultate = []
    if cost_result is not None:
        rezultate.append(RezultatAbordare(abordare="cost", valoare=cost_result.valoare_cost))
    if market_result is not None:
        rezultate.append(RezultatAbordare(abordare="comparatie", valoare=market_result.valoare_piata))
    # Abordarea prin venit: capitalizare directa SAU DCF (nu ambele) — DCF doar daca metoda e "dcf".
    venit_pt_reconciliere = None
    if inp.metoda == "dcf":
        venit_pt_reconciliere = dcf_valoare
    elif venit_result is not None:
        venit_pt_reconciliere = venit_result.valoare
    if venit_pt_reconciliere is not None:
        rezultate.append(RezultatAbordare(abordare="venit", valoare=venit_pt_reconciliere))

    # Metoda ceruta explicit trebuie sa aiba date — altfel eroare clara, nu fallback tacut.
    if inp.metoda == "venit" and venit_result is None:
        raise ValueError("Metoda 'venit' ceruta, dar lipsesc datele de venit (date_venit).")
    if inp.metoda == "dcf" and dcf_valoare is None:
        raise ValueError("Metoda 'dcf' ceruta, dar lipsesc fluxurile DCF (date_dcf).")

    if inp.metoda in ("venit", "dcf"):
        primara, ponderi = "venit", None
    elif inp.metoda == "cost":
        primara, ponderi = "cost", None
    elif inp.metoda == "piata":
        primara, ponderi = "comparatie", None
    else:
        primara = "comparatie"
        ponderi = {"comparatie": inp.pondere_piata, "cost": Decimal("1") - inp.pondere_piata}
    reconciled = reconcile_profil(rezultate, primara=primara, ponderi=ponderi, cfg=cfg)

    alocare = None
    if valoare_teren is not None:
        alocare = aloca_constructii(reconciled.valoare_finala, valoare_teren)

    ctx = ReportContext(
        meta=inp.meta, land=inp.land, building=inp.building,
        comparables=inp.comparables, land_comparables=inp.land_comparables,
        cost_result=cost_result, market_result=market_result, reconciled=reconciled,
        land_result=land_result, alocare_constructii=alocare, photos=inp.photos,
        documente=inp.documente, profil=profil,
        venit_result=venit_result, date_venit=inp.date_venit,
        dcf_valoare=dcf_valoare,
    )

    anonymizer = build_anonymizer(inp.meta)
    ctx.narrative = generate_narrative(ctx, client=client, anonymizer=anonymizer)
    return ctx
