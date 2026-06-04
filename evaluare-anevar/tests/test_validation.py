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
