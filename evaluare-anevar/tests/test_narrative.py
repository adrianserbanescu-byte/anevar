from decimal import Decimal

from evaluare.ai.narrative import CAPITOLE_NARATIVE, generate_narrative
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.report_context import ReportContext
from evaluare.models.results import CostResult, ReconciledResult
from evaluare.report.anonymizer import build_anonymizer


def _ctx() -> ReportContext:
    meta = EvaluationMeta(
        client_nume="Ion Popescu", adresa="Str. Exemplu 1",
        numar_cadastral="123456", carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu", evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16", data_raportului="2026-01-16",
    )
    return ReportContext(
        meta=meta,
        land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("322.75"), acd=Decimal("351.46"),
                              an_referinta=2025),
        cost_result=CostResult(cib=Decimal("2000000"), vcp=Decimal("34"),
                               depreciere_fizica=Decimal("0.35"), cin=Decimal("1300000"),
                               valoare_cost=Decimal("1400000")),
        reconciled=ReconciledResult(valoare_finala=Decimal("1400000"),
                                    metoda_selectata="cost"),
    )


class FakeClient:
    """Client de test: intoarce un text si retine ce a primit."""

    def __init__(self):
        self.calls = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        # raspuns care contine un token, ca sa verificam demascarea
        return "Proprietatea [CLIENT] are valoarea estimata."


def test_generate_narrative_produces_one_section_per_chapter():
    ctx = _ctx()
    client = FakeClient()
    anon = build_anonymizer(ctx.meta)
    sections = generate_narrative(ctx, client=client, anonymizer=anon)
    assert len(sections) == len(CAPITOLE_NARATIVE)
    assert {s.capitol for s in sections} == set(CAPITOLE_NARATIVE)


def test_generate_narrative_unmasks_client_data():
    ctx = _ctx()
    client = FakeClient()
    anon = build_anonymizer(ctx.meta)
    sections = generate_narrative(ctx, client=client, anonymizer=anon)
    # textul demascat trebuie sa contina numele real, nu token-ul
    assert all("Ion Popescu" in s.text for s in sections)
    assert all("[CLIENT]" not in s.text for s in sections)


def test_generate_narrative_never_sends_real_client_name_to_client():
    ctx = _ctx()
    client = FakeClient()
    anon = build_anonymizer(ctx.meta)
    generate_narrative(ctx, client=client, anonymizer=anon)
    # niciun prompt trimis catre client nu contine numele real
    for system, user in client.calls:
        assert "Ion Popescu" not in system
        assert "Ion Popescu" not in user


def test_narrative_acopera_capitolele_gbf_noi():
    ctx = _ctx()
    sections = generate_narrative(ctx, client=FakeClient(), anonymizer=build_anonymizer(ctx.meta))
    capitole = {s.capitol for s in sections}
    assert "Ipoteze generale si speciale" in capitole
    assert "Riscul asociat garantiei (GEV 520)" in capitole


def test_narrative_trimite_ghid_gev520():
    ctx = _ctx()
    client = FakeClient()
    generate_narrative(ctx, client=client, anonymizer=build_anonymizer(ctx.meta))
    promptul_gev = next(u for _, u in client.calls if "GEV 520" in u)
    assert "lichiditatea" in promptul_gev.lower()
    assert "garantarea creditului" in promptul_gev.lower()


def test_curata_narativ_elimina_citatii_si_markdown():
    from evaluare.ai.narrative import _curata_narativ
    t = _curata_narativ("Riscul **este** moderat[2][6].\n## Concluzie\nValoare buna[1].")
    assert "[2]" not in t and "[6]" not in t and "[1]" not in t
    assert "**" not in t
    assert "##" not in t
    assert "este" in t and "Concluzie" in t


def test_curata_narativ_pastreaza_tokeni_anonimizator():
    from evaluare.ai.narrative import _curata_narativ
    # tokenii alfabetici ai anonimizatorului NU trebuie atinsi
    t = _curata_narativ("Proprietatea [CLIENT] de la [ADRESA] are [CADASTRAL].")
    assert "[CLIENT]" in t and "[ADRESA]" in t and "[CADASTRAL]" in t


def test_fallback_without_client_returns_placeholders():
    ctx = _ctx()
    sections = generate_narrative(ctx, client=None, anonymizer=None)
    assert len(sections) == len(CAPITOLE_NARATIVE)
    assert all(s.text.strip() for s in sections)   # placeholder ne-gol
    assert any("[de completat" in s.text.lower() for s in sections)
