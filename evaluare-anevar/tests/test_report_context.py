from decimal import Decimal

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.report_context import ReportContext
from evaluare.models.results import CostResult, ReconciledResult


def _meta() -> EvaluationMeta:
    return EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )


def test_report_context_holds_everything():
    ctx = ReportContext(
        meta=_meta(),
        land=LandData(suprafata=Decimal("500")),
        building=BuildingData(
            au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
            elements=[CostElement(element="S", cod="X", um="mp",
                                  cantitate=Decimal("10"), cost_unitar=Decimal("100"),
                                  an_pif=2015)],
            depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        ),
        comparables=[],
        cost_result=CostResult(cib=Decimal("1000"), vcp=Decimal("10"),
                               depreciere_fizica=Decimal("0.1"), cin=Decimal("900"),
                               valoare_cost=Decimal("1400")),
        market_result=None,
        reconciled=ReconciledResult(valoare_finala=Decimal("1400"),
                                    metoda_selectata="cost"),
    )
    assert ctx.meta.client_nume == "Ion Popescu"
    assert ctx.reconciled.valoare_finala == Decimal("1400")
    assert ctx.market_result is None
