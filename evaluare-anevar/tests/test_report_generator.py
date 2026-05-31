from decimal import Decimal

from docx import Document

from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.models.results import CostResult, ReconciledResult
from evaluare.models.report_context import ReportContext
from evaluare.models.narrative import NarrativeSection
from evaluare.report.generator import genereaza_raport


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1, Bucuresti",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta,
        land=LandData(suprafata=Decimal("500"), categorie="intravilan"),
        building=BuildingData(
            au=Decimal("322.75"), acd=Decimal("351.46"), an_referinta=2025,
            elements=[
                CostElement(element="Structura", cod="X", um="mp",
                            cantitate=Decimal("100"), cost_unitar=Decimal("2000"),
                            an_pif=2015),
            ],
            depreciation_points=[DepreciationPoint(varsta=10, depreciere=Decimal("0.1"))],
        ),
        cost_result=CostResult(cib=Decimal("200000"), vcp=Decimal("10"),
                               depreciere_fizica=Decimal("0.10"), cin=Decimal("180000"),
                               valoare_cost=Decimal("280000")),
        reconciled=ReconciledResult(valoare_finala=Decimal("280000"),
                                    metoda_selectata="cost"),
        narrative=[NarrativeSection(capitol="Analiza celei mai bune utilizari (CMBU)",
                                    text="Cea mai buna utilizare este cea rezidentiala.")],
    )


def _all_text(path) -> str:
    doc = Document(str(path))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def test_genereaza_raport_creeaza_fisier(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    assert out.exists()
    # se deschide ca document Word valid
    Document(str(out))


def test_raportul_contine_datele_cheie(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    text = _all_text(out)
    assert "Ion Popescu" in text
    assert "Garantarea creditului ipotecar" in text
    assert "280000" in text                       # valoarea finala
    assert "CIN" in text or "180000" in text       # tabel cost
    assert "Cea mai buna utilizare" in text        # narativ inserat


def test_raportul_are_cele_sapte_capitole(tmp_path):
    out = tmp_path / "raport.docx"
    genereaza_raport(_ctx(), out)
    doc = Document(str(out))
    headings = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    titlu = "\n".join(headings)
    for nr in ["1.", "2.", "3.", "4.", "5.", "6.", "7."]:
        assert nr in titlu
