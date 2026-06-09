from decimal import Decimal

from evaluare.audit.jurnal import JurnalAudit
from evaluare.audit.raport_audit import scrie_audit, text_audit
from evaluare.audit.snapshot import snapshot
from evaluare.audit.validare_x import valideaza_incrucisat
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, LandData
from evaluare.models.report_context import ReportContext
from evaluare.models.results import CostResult, MarketResult, ReconciledResult


def _clock():
    """Ceas determinist pentru teste (incrementeaza secundele)."""
    n = {"i": 0}

    def tick():
        n["i"] += 1
        return f"2026-06-03T10:00:{n['i']:02d}"
    return tick


# --------------------------------------------------------------------------- #
# Jurnal append-only, hash-chaining
# --------------------------------------------------------------------------- #
def test_jurnal_inlantuie_si_verifica():
    j = JurnalAudit()
    clk = _clock()
    e0 = j.inregistreaza("intrare", {"client": "X"}, clock=clk)
    e1 = j.inregistreaza("calcul", {"valoare": 100}, clock=clk)
    assert e0.index == 0 and e1.index == 1
    assert e1.hash_anterior == e0.hash          # inlantuit
    assert e0.hash and e1.hash and e0.hash != e1.hash
    assert j.verifica() is True


def test_jurnal_detecteaza_alterarea():
    j = JurnalAudit()
    clk = _clock()
    j.inregistreaza("intrare", {"a": 1}, clock=clk)
    j.inregistreaza("calcul", {"b": 2}, clock=clk)
    assert j.verifica() is True
    j.evenimente[0].detalii = '{"a": 999}'      # alterare ulterioara
    assert j.verifica() is False                # lantul se rupe


def test_jurnal_detecteaza_reordonarea():
    j = JurnalAudit()
    clk = _clock()
    j.inregistreaza("a", clock=clk)
    j.inregistreaza("b", clock=clk)
    j.evenimente.reverse()
    assert j.verifica() is False


# --------------------------------------------------------------------------- #
# Snapshot reproductibil
# --------------------------------------------------------------------------- #
def test_snapshot_hash_stabil_si_sensibil():
    a = snapshot({"x": 1, "y": 2})
    b = snapshot({"y": 2, "x": 1})              # alta ordine -> acelasi hash (sort_keys)
    assert a["hash"] == b["hash"]
    c = snapshot({"x": 1, "y": 3})
    assert c["hash"] != a["hash"]


# --------------------------------------------------------------------------- #
# Validare incrucisata
# --------------------------------------------------------------------------- #
def _ctx(valoare_piata=None, valoare_cost=None, valoare_finala="100000", alocare=None):
    meta = EvaluationMeta(client_nume="X", adresa="A", numar_cadastral="1", carte_funciara="CF1",
                          evaluator_nume="E", evaluator_legitimatie="1",
                          data_evaluarii="2026-06-03", data_raportului="2026-06-03")
    market = None
    if valoare_piata is not None:
        market = MarketResult(index_selectat=0, valoare_piata=Decimal(valoare_piata))
    cost = None
    if valoare_cost is not None:
        cost = CostResult(cib=Decimal("1"), vcp=Decimal("1"), depreciere_fizica=Decimal("0"),
                          cin=Decimal("1"), valoare_cost=Decimal(valoare_cost))
    return ReportContext(
        meta=meta, land=LandData(suprafata=Decimal("500")),
        building=BuildingData(au=Decimal("100"), acd=Decimal("120"), an_referinta=2025),
        market_result=market, cost_result=cost,
        reconciled=ReconciledResult(valoare_finala=Decimal(valoare_finala), metoda_selectata="piata"),
        alocare_constructii=Decimal(alocare) if alocare is not None else None,
    )


def test_validare_x_divergenta_piata_cost():
    ctx = _ctx(valoare_piata="100000", valoare_cost="160000")   # divergenta 37.5%
    issues = valideaza_incrucisat(ctx)
    assert any("diverg" in i.mesaj.lower() for i in issues)


def test_validare_x_fara_divergenta_cand_apropiate():
    ctx = _ctx(valoare_piata="100000", valoare_cost="110000")   # 9% < prag
    assert not any("diverg" in i.mesaj.lower() for i in valideaza_incrucisat(ctx))


def test_validare_x_alocare_negativa():
    ctx = _ctx(valoare_finala="50000", alocare="-10000")
    assert any("negativa" in i.mesaj.lower() for i in valideaza_incrucisat(ctx))


def test_validare_x_valoare_finala_zero_blocheaza():
    ctx = _ctx(valoare_finala="0")
    assert any(i.nivel == "blocheaza" for i in valideaza_incrucisat(ctx))


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #
def test_raport_audit_text_si_fisier(tmp_path):
    j = JurnalAudit()
    clk = _clock()
    j.inregistreaza("intrare", {"client": "X"}, clock=clk)
    j.inregistreaza("generare_raport", clock=clk)
    txt = text_audit(j)
    assert "URMA DE AUDIT" in txt and "integritate lant: OK" in txt
    assert "DRAFT" in txt and "răspundere" in txt        # disclaimer aplicatie -> evaluator (cerinta Adi)
    assert "intrare" in txt and "generare_raport" in txt
    out = scrie_audit(j, tmp_path / "audit.txt")
    assert out.exists() and "URMA DE AUDIT" in out.read_text(encoding="utf-8")
