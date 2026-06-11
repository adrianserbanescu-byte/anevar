"""Verificarea interna a calitatii (QC) live + gardarea emiterii raportului — gap G-Q1.

Acopera atat fluxul NOU (foldere, /api/dosar/...) cat si cel VECHI (SQLite, /api/evaluare/...).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "d.db")
    s.init()
    c = TestClient(create_app(storage=s, client=None))
    c._baza = tmp_path
    return c


def _payload() -> dict:
    return {
        "meta": {"client_nume": "Ion Pop", "adresa": "A", "numar_cadastral": "777",
                 "carte_funciara": "CF", "evaluator_nume": "Adi S", "evaluator_legitimatie": "8717",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                                   "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"}]},
        "valoare_teren": "100000", "metoda": "cost",
    }


def _cont(client):
    return client.post("/api/cont", json={"nume": "Adi S", "legitimatie": "8717"})


def _dosar(client) -> str:
    _cont(client)
    return client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]


# ── Endpoint live (flux nou, foldere) ─────────────────────────────────────────
def test_calitate_live_dosar_valid_emisibil(client):
    uid = _dosar(client)
    r = client.post(f"/api/dosar/{uid}/calitate", json=_payload())
    assert r.status_code == 200
    body = r.json()
    assert body["emisibil"] is True
    chei = {e["cheie"] for e in body["checklist"]}
    assert "comparabile_minime" in chei and "cmbu_concluzionat" in chei
    # fiecare element are starea bifata automat + nivel
    assert all("trecut" in e and e["nivel"] in ("blocheaza", "alerteaza") for e in body["checklist"])


def test_calitate_live_reflecta_esecul(client):
    uid = _dosar(client)
    p = _payload()
    p["meta"]["tip_valoare"] = ""                  # blocaj QC: tip valoare nedeclarat
    r = client.post(f"/api/dosar/{uid}/calitate", json=p)
    assert r.status_code == 200
    body = r.json()
    assert body["emisibil"] is False and body["blocaje"] >= 1
    tv = next(e for e in body["checklist"] if e["cheie"] == "tip_valoare_sursa")
    assert tv["trecut"] is False and tv["nivel"] == "blocheaza"


def test_calitate_live_dosar_inexistent_404(client):
    _cont(client)
    assert client.post("/api/dosar/nope/calitate", json=_payload()).status_code == 404


# ── Gardarea emiterii (flux nou) ──────────────────────────────────────────────
def test_raport_blocat_pe_qc_tip_valoare_gol(client):
    uid = _dosar(client)
    p = _payload()
    p["meta"]["tip_valoare"] = ""                  # blocaj QC (NU e prins de validatorii vechi)
    r = client.post(f"/api/dosar/{uid}/raport.docx", json=p)
    assert r.status_code == 422 and "calitat" in r.json()["detail"].lower()


def test_raport_blocat_pe_qc_data_inversa(client):
    uid = _dosar(client)
    p = _payload()
    p["meta"]["data_evaluarii"] = "2026-02-10"
    p["meta"]["data_raportului"] = "2026-01-01"     # raport inainte de evaluare -> blocaj QC
    r = client.post(f"/api/dosar/{uid}/raport.docx", json=p)
    assert r.status_code == 422 and "calitat" in r.json()["detail"].lower()


def test_raport_valid_trece_de_qc(client):
    # regresie: garda QC NU blocheaza un dosar altfel valid (CMBU placeholder + documente lipsa =
    # doar avertismente, nu blocaje).
    uid = _dosar(client)
    r = client.post(f"/api/dosar/{uid}/raport.docx", json=_payload())
    assert r.status_code == 200 and r.content[:2] == b"PK"


# ── Documentarea verificarii in urma de audit (recomandarea §5.e) ─────────────
def test_audit_documenteaza_verificarea_calitatii(client):
    uid = _dosar(client)
    r = client.post(f"/api/dosar/{uid}/audit.txt", json=_payload())
    assert r.status_code == 200 and "verificare_calitate" in r.text


# ── UI: panoul de verificare a calitatii in pagina dosarului ──────────────────
def test_dosar_html_contine_panoul_de_calitate(client):
    uid = _dosar(client)
    html = client.get(f"/dosar/{uid}").text
    assert 'id="qc-box"' in html                         # panoul QC din sub-tabul Generează
    assert 'id="qc-lista"' in html and 'id="qc-verifica"' in html
    assert "Verificare internă a calității" in html
    assert "refreshQC" in html                           # logica live (fetch /calitate)


# ── Paritate flux vechi (SQLite, /api/evaluare) ───────────────────────────────
def test_calitate_live_flux_vechi(client):
    eid = client.post("/api/evaluare", json=_payload()).json()["id"]
    r = client.get(f"/api/evaluare/{eid}/calitate")
    assert r.status_code == 200 and r.json()["emisibil"] is True
    assert client.get("/api/evaluare/999999/calitate").status_code == 404


def test_raport_vechi_blocat_pe_qc(client):
    # dosar persistat cu tip valoare gol (validatorii vechi nu-l prind) -> raportul oficial e blocat de QC
    p = _payload()
    p["meta"]["tip_valoare"] = ""
    eid = client.post("/api/evaluare", json=p).json()["id"]
    r = client.get(f"/api/evaluare/{eid}/raport.docx")
    assert r.status_code == 422 and "calitat" in r.json()["detail"].lower()
