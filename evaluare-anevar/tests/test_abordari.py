from decimal import Decimal

from evaluare.engine.abordari import RezultatAbordare, abordare_comparatie, abordare_cost
from evaluare.models.comparable import Comparable
from evaluare.models.property import BuildingData


def _building():
    return BuildingData(
        au=Decimal("100"), acd=Decimal("120"), an_referinta=2025,
        elements=[{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                   "cost_unitar": "2000", "an_pif": 2015}],
        depreciation_points=[{"varsta": 5, "depreciere": "0.05"},
                             {"varsta": 15, "depreciere": "0.15"}],
    )


def test_abordare_cost_produce_rezultat():
    r = abordare_cost(_building(), valoare_teren=Decimal("100000"))
    assert isinstance(r, RezultatAbordare)
    assert r.abordare == "cost"
    assert r.valoare is not None and r.valoare > 0
    assert "cin" in r.detalii


def test_abordare_comparatie_produce_rezultat():
    comps = [Comparable(pret=Decimal("250000"), suprafata=Decimal("120")),
             Comparable(pret=Decimal("260000"), suprafata=Decimal("125")),
             Comparable(pret=Decimal("240000"), suprafata=Decimal("118"))]
    r = abordare_comparatie(comps, suprafata_subiect=Decimal("120"))
    assert r.abordare == "comparatie"
    assert r.valoare is not None and r.valoare > 0
