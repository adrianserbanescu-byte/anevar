from decimal import Decimal

from docx import Document

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.report_context import ReportContext
from evaluare.engine.cost import evaluate_cost
from evaluare.engine.reconciliation import reconcile
from evaluare.ai.narrative import generate_narrative
from evaluare.report.generator import genereaza_raport, _fmt


def test_full_pipeline_cost_only(tmp_path):
    # date casa + teren, doar abordarea prin cost (fara comparabile)
    building = BuildingData(
        au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
        elements=[
            CostElement(element="Structura", cod="X", um="mp",
                        cantitate=Decimal("351.46"), cost_unitar=Decimal("5725.67"),
                        an_pif=2015),
        ],
        depreciation_points=[
            DepreciationPoint(varsta=5, depreciere=Decimal("0.05")),
            DepreciationPoint(varsta=15, depreciere=Decimal("0.15")),
        ],
    )
    cost = evaluate_cost(building, valoare_teren=Decimal("100000"))
    reconciled = reconcile(market=None, cost=cost, metoda="cost")

    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1, Bucuresti",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    ctx = ReportContext(meta=meta, land=LandData(suprafata=Decimal("500")),
                        building=building, cost_result=cost, market_result=None,
                        reconciled=reconciled)
    # fara client AI -> placeholdere
    ctx.narrative = generate_narrative(ctx, client=None, anonymizer=None)

    out = tmp_path / "raport_complet.docx"
    genereaza_raport(ctx, out)
    assert out.exists()
    doc = Document(str(out))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Ion Popescu" in text
    assert _fmt(reconciled.valoare_finala) in text
