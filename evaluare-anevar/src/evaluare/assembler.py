"""Orchestrarea motoarelor: din datele de intrare -> ReportContext complet."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from evaluare.audit.validare_x import valideaza_incrucisat
from evaluare.ai.narrative import NarrativeClient, generate_narrative
from evaluare.engine.abordari import RezultatAbordare
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.land import evaluate_land, pret_mp_corectat
from evaluare.engine.market import evaluate_market, pret_total_corectat
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.engine.reconciliation import aloca_constructii, reconcile_profil
from evaluare.engine.validation import (
    Issue,
    valideaza_comparabile,
    valideaza_comparabile_teren,
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
    if inp.land_comparables:   # grila de teren -> valoarea terenului: aceleasi garzi M5 ca piata
        issues += valideaza_comparabile_teren(inp.land_comparables, cfg)
    return issues


def valideaza_din_context(ctx: ReportContext, cfg: MetodologieConfig = IMPLICIT) -> list[Issue]:
    """Ca `valideaza`, dar reconstruita din ReportContext (nu din inputul brut).

    Endpointul vechi `/api/evaluare/{eid}/raport.docx` incarca dosarul din storage si NU mai are
    `EvaluationInput`-ul; ca sa blocheze documentul oficial pe ACELEASI probleme blocante ca
    endpointul nou, ruleaza aceiasi validatori pe campurile din context. Piata conteaza doar cand
    a contribuit efectiv la valoare (`metoda_selectata` = piata/ponderata); terenul intra mereu.
    """
    issues: list[Issue] = []
    issues += valideaza_proprietate(ctx.land, ctx.building)
    issues += valideaza_depreciere(ctx.building)
    if ctx.reconciled.metoda_selectata in ("piata", "ponderata"):
        issues += valideaza_comparabile(ctx.comparables, cfg)
    if ctx.land_comparables:
        issues += valideaza_comparabile_teren(ctx.land_comparables, cfg)
    return issues


def valoare_imposibila(ctx: ReportContext) -> list[Issue]:
    """Blocaje de VALOARE imposibila matematic — subsetul de `blocheaza` care NU poate fi emis nici
    macar provizoriu (un pret negativ/zero nu e o estimare utila), spre deosebire de blocajele de DATE
    (Au>Acd, depreciere fara justificare) care raman advisory in /calcul (decizia re-audit I1).

    Sursa unica de adevar pentru garda «nu produce/persista o valoare imposibila», aplicata la /calcul,
    persistenta si raportul oficial. Lucreaza DOAR pe context (nu pe inputul brut), ca sa fie folosibila
    si de endpointul vechi care incarca dosarul din storage. Decizia owner (2026-06-10): «blocheaza doar
    valorile invalide» — valoarea finala <=0 SAU un pret corectat (comparabil/teren care contribuie la
    valoare) <=0.
    """
    invalide: list[Issue] = [i for i in valideaza_incrucisat(ctx) if i.nivel == "blocheaza"]
    # Pretul corectat <=0 polueaza valoarea DOAR cand piata a contribuit efectiv (piata/ponderata).
    if ctx.reconciled.metoda_selectata in ("piata", "ponderata"):
        for idx, comp in enumerate(ctx.comparables):
            if pret_total_corectat(comp) <= 0:
                invalide.append(Issue(
                    nivel="blocheaza",
                    mesaj=f"Comparabilul {idx}: pretul corectat este <= 0 — valoarea de piata e nonsens.",
                ))
    # Terenul intra MEREU in valoare (prin valoare_teren) cand exista grila de teren.
    for idx, comp in enumerate(ctx.land_comparables):
        if pret_mp_corectat(comp) <= 0:
            invalide.append(Issue(
                nivel="blocheaza",
                mesaj=f"Comparabilul de teren {idx}: pretul/mp corectat este <= 0 — valoarea terenului e nonsens.",
            ))
    return invalide


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
        # SEV 450 (asigurare): valoarea = costul de RECONSTRUCTIE = cost de inlocuire BRUT (CIB),
        # NEdeprecat si fara teren (terenul nu se asigura) — altfel clientul ar fi SUB-ASIGURAT. Pentru
        # restul scopurilor (garantare etc.) ramane valoare_cost (CIN deprecat + teren).
        valoare_cost_abordare = (cost_result.cib if inp.scop == "asigurare"
                                 else cost_result.valoare_cost)
        rezultate.append(RezultatAbordare(abordare="cost", valoare=valoare_cost_abordare))
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
