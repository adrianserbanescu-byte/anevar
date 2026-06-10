from decimal import Decimal

from evaluare.engine.validation import (
    valideaza_comparabile,
    valideaza_depreciere,
    valideaza_proprietate,
)
from evaluare.models.comparable import Adjustment, Comparable
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData


def _building(au="322.75", acd="351.46", c_nf="0", justif_nf="") -> BuildingData:
    return BuildingData(
        au=Decimal(au), acd=Decimal(acd), an_referinta=2025,
        functional_depreciation=Decimal(c_nf),
        elements=[CostElement(element="S", cod="X", um="mp",
                              cantitate=Decimal("10"), cost_unitar=Decimal("100"),
                              an_pif=2015)],
        depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        justificare_depreciere=justif_nf,
    )


def test_blocheaza_cand_au_mai_mare_decat_acd():
    land = LandData(suprafata=Decimal("500"))
    building = _building(au="400", acd="351.46")
    issues = valideaza_proprietate(land, building)
    assert any(i.nivel == "blocheaza" and "Au" in i.mesaj for i in issues)


def test_blocheaza_cand_suprafata_teren_zero():
    land = LandData(suprafata=Decimal("0"))
    building = _building()
    issues = valideaza_proprietate(land, building)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_proprietate_valida_fara_probleme():
    land = LandData(suprafata=Decimal("500"))
    building = _building()
    issues = valideaza_proprietate(land, building)
    assert all(i.nivel != "blocheaza" for i in issues)


def test_blocheaza_sub_3_comparabile():
    comps = [Comparable(pret=Decimal("1"), suprafata=Decimal("1"))]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_alerteaza_ajustare_bruta_peste_25_la_suta():
    comps = [
        Comparable(pret=Decimal("1"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("1"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("1"), suprafata=Decimal("1"),
                   adjustments=[Adjustment(element="A", tip="procentuala",
                                           valoare=Decimal("0.30"))]),
    ]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "alerteaza" and "ajustare" in i.mesaj.lower() for i in issues)


def test_alerteaza_outlier_dupa_mediana():
    comps = [
        Comparable(pret=Decimal("500"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("510"), suprafata=Decimal("1")),
        Comparable(pret=Decimal("2000"), suprafata=Decimal("1")),  # outlier
    ]
    issues = valideaza_comparabile(comps)
    assert any(i.nivel == "alerteaza" and "outlier" in i.mesaj.lower() for i in issues)


def test_blocheaza_depreciere_functionala_fara_justificare():
    building = _building(c_nf="0.10", justif_nf="")
    issues = valideaza_depreciere(building)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_depreciere_functionala_cu_justificare_ok():
    building = _building(c_nf="0.10", justif_nf="uzura interioara avansata")
    issues = valideaza_depreciere(building)
    assert all(i.nivel != "blocheaza" for i in issues)


def test_valideaza_comparabile_teren_m5_simetric_cu_piata():
    # #7: gardile M5 (min 3, outlier, limita ajustare, pret<=0) aplicate si la comparabilele de TEREN.
    from decimal import Decimal

    from evaluare.engine.validation import valideaza_comparabile_teren
    from evaluare.models.comparable import Adjustment, LandComparable

    def _t(pret_mp, adj=None):
        return LandComparable(pret_mp=Decimal(pret_mp), suprafata=Decimal("500"),
                              adjustments=adj or [])

    # <3 comparabile de teren -> blocheaza
    iss = valideaza_comparabile_teren([_t("100")])
    assert any(i.nivel == "blocheaza" and "teren" in i.mesaj for i in iss)
    # 3 comparabile: unul outlier (300 vs mediana 100) + unul cu ajustare bruta 40% (> 25%)
    comps = [_t("100"), _t("300"),
             _t("100", [Adjustment(element="x", tip="procentuala",
                                   valoare=Decimal("0.40"), etapa="proprietate")])]
    iss2 = valideaza_comparabile_teren(comps)
    assert any("outlier" in i.mesaj and "teren" in i.mesaj for i in iss2)        # 300 e outlier
    assert any("ajustare bruta" in i.mesaj and "teren" in i.mesaj for i in iss2)  # 0.40 > 0.25


def test_assembler_valideaza_aplica_garda_pe_comparabile_teren():
    # #7: assembler.valideaza ruleaza acum gardile si pe land_comparables (nu doar piata).
    from decimal import Decimal

    from evaluare.assembler import EvaluationInput, valideaza
    from evaluare.models.comparable import LandComparable
    inp = EvaluationInput(
        meta={"client_nume": "X", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
              "evaluator_nume": "E", "evaluator_legitimatie": "1", "data_evaluarii": "2026-01-01",
              "data_raportului": "2026-01-01"},
        land={"suprafata": "500"}, building={"au": "100", "acd": "120", "an_referinta": 2025},
        land_comparables=[LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("500"))],  # doar 1 -> <3
        metoda="cost",
    )
    issues = valideaza(inp)
    assert any("comparabile de teren" in i.mesaj for i in issues)   # garda M5 pe teren a rulat
