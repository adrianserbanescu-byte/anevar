from decimal import Decimal

from evaluare.engine.abordari import abordare_cost, abordare_comparatie
from evaluare.engine.reconciliation import reconcile, reconcile_profil
from evaluare.models.comparable import Comparable
from evaluare.models.property import BuildingData
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.market import evaluate_market
from evaluare.models.report_context import ReportContext
from evaluare.profil import CASA_TEREN_GARANTARE


def _building():
    return BuildingData(
        au=Decimal("100"), acd=Decimal("120"), an_referinta=2025,
        elements=[{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                   "cost_unitar": "2000", "an_pif": 2015}],
        depreciation_points=[{"varsta": 5, "depreciere": "0.05"},
                             {"varsta": 15, "depreciere": "0.15"}],
    )


def test_reconcile_profil_echivalent_cu_reconcile_pe_cost():
    b = _building()
    cost = evaluate_cost(b, valoare_teren=Decimal("100000"))
    vechi = reconcile(market=None, cost=cost, metoda="cost")
    nou = reconcile_profil([abordare_cost(b, valoare_teren=Decimal("100000"))], primara="cost")
    assert nou.valoare_finala == vechi.valoare_finala
    assert nou.metoda_selectata == vechi.metoda_selectata == "cost"


def test_reconcile_profil_echivalent_pe_piata():
    comps = [Comparable(pret=Decimal("250000"), suprafata=Decimal("120")),
             Comparable(pret=Decimal("260000"), suprafata=Decimal("125")),
             Comparable(pret=Decimal("240000"), suprafata=Decimal("118"))]
    market = evaluate_market(comps, suprafata_subiect=Decimal("120"))
    vechi = reconcile(market=market, cost=None, metoda="piata")
    nou = reconcile_profil([abordare_comparatie(comps, suprafata_subiect=Decimal("120"))],
                           primara="comparatie")
    assert nou.valoare_finala == vechi.valoare_finala
    assert nou.metoda_selectata == "piata"


def test_report_context_are_profil_default():
    assert "profil" in ReportContext.model_fields
