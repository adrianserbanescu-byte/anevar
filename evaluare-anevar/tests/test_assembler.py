from decimal import Decimal

from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.models.comparable import Adjustment, Comparable, LandComparable
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData


def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. 1", numar_cadastral="123",
        carte_funciara="CF123", evaluator_nume="Maria", evaluator_legitimatie="1",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def _building_with_elements() -> BuildingData:
    return BuildingData(
        au=Decimal("100"), acd=Decimal("120"), an_referinta=2025,
        elements=[CostElement(element="S", cod="X", um="mp",
                              cantitate=Decimal("120"), cost_unitar=Decimal("2000"),
                              an_pif=2015)],
        depreciation_points=[DepreciationPoint(varsta=5, depreciere=Decimal("0.05")),
                             DepreciationPoint(varsta=15, depreciere=Decimal("0.15"))],
    )


def test_construieste_context_cost_only():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=_building_with_elements(), comparables=[],
        valoare_teren=Decimal("100000"), metoda="cost",
    )
    ctx = construieste_context(inp, client=None)
    assert ctx.cost_result is not None
    assert ctx.market_result is None
    assert ctx.reconciled.metoda_selectata == "cost"
    # valoare prin cost = CIN + teren
    assert ctx.reconciled.valoare_finala == ctx.cost_result.valoare_cost
    # narativ fallback prezent
    assert len(ctx.narrative) > 0


def test_construieste_context_market():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        comparables=[
            Comparable(pret=Decimal("360000"), suprafata=Decimal("120"),
                       adjustments=[Adjustment(element="A", tip="procentuala",
                                               valoare=Decimal("0.05"))]),
            Comparable(pret=Decimal("372000"), suprafata=Decimal("120")),
            Comparable(pret=Decimal("366000"), suprafata=Decimal("120")),
        ],
        metoda="piata",
    )
    ctx = construieste_context(inp, client=None)
    assert ctx.market_result is not None
    assert ctx.reconciled.metoda_selectata == "piata"


def test_valideaza_piata_sub_3_comparabile_blocheaza():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        comparables=[Comparable(pret=Decimal("300000"), suprafata=Decimal("120"))],
        metoda="piata",
    )
    issues = valideaza(inp)
    assert any(i.nivel == "blocheaza" for i in issues)


def test_valoare_teren_din_grila_de_teren():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("1000")),
        building=_building_with_elements(),
        land_comparables=[
            LandComparable(pret_mp=Decimal("100"), suprafata=Decimal("450"),
                           adjustments=[Adjustment(element="A", tip="procentuala",
                                                   valoare=Decimal("0.05"))]),
        ],
        metoda="cost",
    )
    ctx = construieste_context(inp, client=None)
    # valoare teren = 105 EUR/mp * 1000 mp = 105000 (din grila, nu manual)
    assert ctx.land_result is not None
    assert ctx.land_result.valoare_teren == Decimal("105000.00")
    assert ctx.alocare_constructii is not None


def test_valideaza_cost_nu_cere_comparabile():
    inp = EvaluationInput(
        meta=_meta(), land=LandData(suprafata=Decimal("500")),
        building=_building_with_elements(), comparables=[],
        valoare_teren=Decimal("100000"), metoda="cost",
    )
    issues = valideaza(inp)
    # fara comparabile dar metoda cost -> nu blocheaza pe numarul de comparabile
    assert not any(i.nivel == "blocheaza" and "comparabile" in i.mesaj.lower() for i in issues)
