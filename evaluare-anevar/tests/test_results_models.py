from decimal import Decimal

from evaluare.models.results import CostResult, MarketResult, ReconciledResult


def test_cost_result_fields():
    r = CostResult(
        valoare_teren=Decimal("36000"),
        cib=Decimal("2012343"),
        vcp=Decimal("34.02"),
        depreciere_fizica=Decimal("0.3502"),
        cin=Decimal("1307558"),
        valoare_cost=Decimal("1343558"),
    )
    assert r.cin == Decimal("1307558")
    assert r.valoare_cost == Decimal("1343558")


def test_market_result_fields():
    r = MarketResult(
        preturi_unitare_corectate=[Decimal("4500"), Decimal("4600")],
        ajustari_brute=[Decimal("0.10"), Decimal("0.18")],
        index_selectat=0,
        valoare_piata=Decimal("450000"),
    )
    assert r.index_selectat == 0
    assert r.valoare_piata == Decimal("450000")


def test_reconciled_result_fields():
    r = ReconciledResult(
        valoare_finala=Decimal("450000"),
        metoda_selectata="piata",
        valoare_fara_tva=True,
    )
    assert r.metoda_selectata == "piata"
