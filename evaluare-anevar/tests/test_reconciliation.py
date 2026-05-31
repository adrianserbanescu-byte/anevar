from decimal import Decimal

import pytest

from evaluare.models.results import CostResult, MarketResult
from evaluare.engine.reconciliation import reconcile


def make_market(value: Decimal) -> MarketResult:
    return MarketResult(index_selectat=0, valoare_piata=value)


def make_cost(value: Decimal | None) -> CostResult:
    return CostResult(
        cib=Decimal("2000000"), vcp=Decimal("34"),
        depreciere_fizica=Decimal("0.35"), cin=Decimal("1300000"),
        valoare_cost=value,
    )


def test_reconcile_prefers_market_when_selected():
    r = reconcile(make_market(Decimal("450000")), make_cost(Decimal("460000")),
                  metoda="piata")
    assert r.metoda_selectata == "piata"
    assert r.valoare_finala == Decimal("450000")


def test_reconcile_uses_cost_when_selected():
    r = reconcile(make_market(Decimal("450000")), make_cost(Decimal("460000")),
                  metoda="cost")
    assert r.metoda_selectata == "cost"
    assert r.valoare_finala == Decimal("460000")


def test_reconcile_weighted_average():
    r = reconcile(make_market(Decimal("400000")), make_cost(Decimal("500000")),
                  metoda="ponderata", pondere_piata=Decimal("0.6"))
    # 400000*0.6 + 500000*0.4 = 440000
    assert r.metoda_selectata == "ponderata"
    assert r.valoare_finala == Decimal("440000.0")


def test_reconcile_falls_back_to_market_when_cost_unavailable():
    r = reconcile(make_market(Decimal("450000")), make_cost(None), metoda="cost")
    # cost indisponibil -> foloseste piata si noteaza
    assert r.metoda_selectata == "piata"
    assert r.valoare_finala == Decimal("450000")
    assert "indisponibil" in r.nota.lower()


def test_reconcile_raises_when_no_approach_available():
    with pytest.raises(ValueError):
        reconcile(None, make_cost(None), metoda="piata")
