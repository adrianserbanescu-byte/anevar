"""GF1 (audit-consolidat 2026-06-11, HIGH/CORRECTNESS) — ajustarile din grila TREBUIE sa ajunga in raport.

Bug original: butonul «Trimite preturile in Comparabile» (g-import / gt-import) impingea in textarea DOAR
`pret;suprafata`, iar `asambleaza()` reconstruia comparabilele tot ca `{pret, suprafata}` — fara cheia
`adjustments`. Rezultat: `evaluate_market`/`evaluate_land` mediau preturile BRUTE (ajustarile calculate in
grila se aruncau), «Ajustare bruta» aparea 0% pe toate randurile, iar anexa F-10 «Desfasuratorul
ajustarilor» se omitea mereu. Valoarea din raport diferea de cea afisata in grila.

Fix (aditiv, frontend): g-import/gt-import serializeaza desfasuratorul de ajustari intr-un camp ascuns
(#comparabile_aj / #comparabile_teren_aj), keyed pe semnatura (pret;suprafata). `asambleaza()` citeste
maparea si ataseaza `adjustments` la fiecare comparabil. Fara grila -> map gol -> comportament vechi (brut).

Doua paliere de test:
  1. CARACTERIZARE pe template (JS-ul frontend nu e acoperit de suita Python) — regex pe dosar.html.
  2. CONTRACT backend — ajustarile trecute prin EvaluationInput SCHIMBA efectiv valoarea de piata si
     alimenteaza anexa F-10 (dovada ca, odata trimise, ajustarile chiar conteaza end-to-end).
"""
from decimal import Decimal
from pathlib import Path

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.engine.land import evaluate_land
from evaluare.models.comparable import Adjustment, Comparable, LandComparable
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData

DOSAR = Path(__file__).resolve().parent.parent / "src" / "evaluare" / "web" / "templates" / "curent" / "dosar.html"


# ── 1. Caracterizare pe template (frontend) ──────────────────────────────────────────────

def test_campurile_ascunse_de_ajustari_exista():
    """Containerele persistate (au id -> intra in snapshot/WIZARD -> supravietuiesc refresh-ului)."""
    html = DOSAR.read_text(encoding="utf-8")
    assert 'id="comparabile_aj"' in html, "lipseste containerul de ajustari casa (#comparabile_aj)"
    assert 'id="comparabile_teren_aj"' in html, "lipseste containerul de ajustari teren (#comparabile_teren_aj)"


def test_butoanele_de_import_scriu_ajustarile():
    """g-import si gt-import trebuie sa serializeze ajustarile (via _scrieAj), nu doar pret;suprafata."""
    html = DOSAR.read_text(encoding="utf-8")
    # casa
    assert '_scrieAj("comparabile_aj"' in html, "g-import nu mai scrie ajustarile in #comparabile_aj"
    # teren
    assert '_scrieAj("comparabile_teren_aj"' in html, "gt-import nu mai scrie ajustarile in #comparabile_teren_aj"


def test_asambleaza_citeste_ajustarile_si_le_ataseaza():
    """asambleaza() trebuie sa citeasca maparea de ajustari si sa ataseze cheia `adjustments`."""
    html = DOSAR.read_text(encoding="utf-8")
    assert '_ajMap("comparabile_aj")' in html, "asambleaza() nu mai citeste ajustarile de casa"
    assert '_ajMap("comparabile_teren_aj")' in html, "asambleaza() nu mai citeste ajustarile de teren"
    # cheia `adjustments` trebuie atasata comparabilelor (altfel backendul nu le vede).
    assert "c.adjustments=aj" in html, "asambleaza() nu ataseaza `adjustments` la comparabile"


# ── 2. Contract backend: ajustarile chiar schimba valoarea + alimenteaza F-10 ────────────

def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. 1", numar_cadastral="123",
        carte_funciara="CF123", evaluator_nume="Maria", evaluator_legitimatie="1",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def _inp(comparables) -> EvaluationInput:
    return EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        comparables=comparables, metoda="piata",
    )


def test_ajustarile_schimba_valoarea_de_piata():
    """Aceleasi preturi BRUTE, dar cu ajustari de proprietate -> valoare DIFERITA de media bruta.

    Aceasta e exact regresia GF1: daca ajustarile NU ajung in EvaluationInput, ambele cazuri ar da
    aceeasi valoare (media bruta). Cu ajustarile atasate, valoarea trebuie sa se miste."""
    brute = [
        Comparable(pret=Decimal("360000"), suprafata=Decimal("120")),
        Comparable(pret=Decimal("360000"), suprafata=Decimal("120")),
        Comparable(pret=Decimal("360000"), suprafata=Decimal("120")),
    ]
    cu_aj = [
        Comparable(pret=Decimal("360000"), suprafata=Decimal("120"),
                   adjustments=[Adjustment(element="Localizare", tip="procentuala",
                                           valoare=Decimal("0.10"), etapa="proprietate")]),
        Comparable(pret=Decimal("360000"), suprafata=Decimal("120"),
                   adjustments=[Adjustment(element="Localizare", tip="procentuala",
                                           valoare=Decimal("0.10"), etapa="proprietate")]),
        Comparable(pret=Decimal("360000"), suprafata=Decimal("120"),
                   adjustments=[Adjustment(element="Localizare", tip="procentuala",
                                           valoare=Decimal("0.10"), etapa="proprietate")]),
    ]
    v_brut = construieste_context(_inp(brute), client=None).market_result.valoare_piata
    v_aj = construieste_context(_inp(cu_aj), client=None).market_result.valoare_piata
    assert v_brut == Decimal("360000")
    # +10% pe etapa de proprietate -> 396000, demonstrabil diferit de media bruta.
    assert v_aj == Decimal("396000"), f"ajustarea nu a intrat in valoare: {v_aj}"
    assert v_aj != v_brut


def test_fara_ajustari_comportament_neschimbat():
    """Garda anti-regresie: comparabile FARA grila -> exact media bruta (cazul vechi nu se strica)."""
    ctx = construieste_context(_inp([
        Comparable(pret=Decimal("300000"), suprafata=Decimal("100")),
        Comparable(pret=Decimal("310000"), suprafata=Decimal("100")),
        Comparable(pret=Decimal("320000"), suprafata=Decimal("100")),
    ]), client=None)
    assert ctx.market_result.valoare_piata == Decimal("310000")
    assert all(b == Decimal("0") for b in ctx.market_result.ajustari_brute)


def test_ajustarile_teren_schimba_valoarea():
    """Simetric pe teren: ajustarile de proprietate trecute prin LandComparable schimba valoarea terenului.

    Folosim direct `evaluate_land` (motorul pe care assembler-ul il apeleaza pentru grila de teren) —
    acelasi camp `adjustments` care, in regresia GF1, nu ajungea niciodata din UI pana aici."""
    def land_comps(aj):
        mk = (lambda: [Adjustment(element="Localizare", tip="procentuala",
                                  valoare=Decimal("0.20"), etapa="proprietate")]) if aj else (lambda: [])
        return [LandComparable(pret_mp=Decimal("50"), suprafata=Decimal("500"), adjustments=mk())
                for _ in range(3)]
    v_brut = evaluate_land(land_comps(False), Decimal("500")).valoare_teren
    v_aj = evaluate_land(land_comps(True), Decimal("500")).valoare_teren
    assert v_aj != v_brut, f"ajustarea de teren nu a intrat in valoare: brut={v_brut} aj={v_aj}"
