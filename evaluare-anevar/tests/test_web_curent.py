"""UI nou (versiunea curentă): cont local + ÎNCEPE + workspace dosar (stocare pe foldere)."""
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


def _payload():
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
    return client.post("/api/cont", json={
        "nume": "Adi S", "legitimatie": "8717",
        "format_dosar": ["id_client", "nume_client", "tip_proprietate"]})


# ── Cont ─────────────────────────────────────────────────────────────────────
def test_pagina_cont_fara_cont(client):
    r = client.get("/cont")
    assert r.status_code == 200 and "Nume evaluator" in r.text


def test_creeaza_cont_si_reincarca(client):
    assert _cont(client).status_code == 200
    r = client.get("/cont")
    assert "Adi S" in r.text and "8717" in r.text


def test_cont_invalid_422(client):
    assert client.post("/api/cont", json={"nume": "", "legitimatie": "x"}).status_code == 422


# ── ÎNCEPE ───────────────────────────────────────────────────────────────────
def test_incepe_fara_cont_cere_cont(client):
    r = client.get("/incepe")
    assert r.status_code == 200 and "Creează cont" in r.text


def test_incepe_cu_cont_arata_optiuni(client):
    _cont(client)
    r = client.get("/incepe")
    assert "Dosar nou" in r.text and "Adi S" in r.text


# ── Dosar (workspace) ────────────────────────────────────────────────────────
def test_dosar_nou_necesita_cont(client):
    assert client.post("/api/dosar", json={"wizard": {}}).status_code == 403


def test_creeaza_deschide_salveaza_dosar(client):
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "Ana"}}).json()["uuid"]
    assert client.get(f"/dosar/{uid}").status_code == 200
    # salvează snapshot
    client.post(f"/api/dosar/{uid}/salveaza", json={"nume_client": "Ana", "au": "90"})
    d = client.get(f"/api/dosar/{uid}").json()
    assert d["wizard"]["au"] == "90"


def test_dosar_apare_in_incepe(client):
    _cont(client)
    client.post("/api/dosar", json={"wizard": {"nume_client": "Vasile"}})
    client.get("/incepe")                                   # prima vedere -> intră în index
    assert "/dosar/" in client.get("/incepe").text


def test_calcul_fara_persistenta_sqlite(client):
    # «Calculează» din UI-ul nou NU trebuie să scrie rânduri orfane în SQLite (folder=adevăr)
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    n_inainte = len(client.get("/dosare").text.split("Deschide"))
    r = client.post(f"/api/dosar/{uid}/calcul", json=_payload())
    assert r.status_code == 200
    d = r.json()
    assert d["valoare_finala"] and d["metoda"] == "cost"
    assert "id" not in d                                    # calc-only: nu persistă în SQLite
    assert len(client.get("/dosare").text.split("Deschide")) == n_inainte   # zero dosare noi
    assert client.post("/api/dosar/nope/calcul", json=_payload()).status_code == 404


def test_calcul_metoda_venit(client):
    # paritate UI nou: metoda venit (capitalizare directă) cu date_venit
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    p = _payload()
    p["metoda"] = "venit"
    p["date_venit"] = {"venit_brut_potential": "24000", "grad_neocupare": "0.1",
                       "cheltuieli_exploatare": "3000", "rata_capitalizare": "0.08"}
    r = client.post(f"/api/dosar/{uid}/calcul", json=p)
    assert r.status_code == 200 and r.json()["metoda"] == "venit"


def test_calcul_cu_grila_teren(client):
    # paritate UI nou: comparabile de teren → valoarea terenului se calculează din grilă
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    p = _payload()
    p["land_comparables"] = [{"pret_mp": "50", "suprafata": "700"},
                             {"pret_mp": "55", "suprafata": "650"},
                             {"pret_mp": "48", "suprafata": "720"}]
    r = client.post(f"/api/dosar/{uid}/calcul", json=p)
    assert r.status_code == 200 and r.json()["valoare_finala"]


def test_genereaza_raport_salveaza_versiune(client):
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    r = client.post(f"/api/dosar/{uid}/raport.docx", json=_payload())
    assert r.status_code == 200 and len(r.content) > 1000
    folder = client._baza / "date" / "dosare" / uid
    assert len(list(folder.glob("raport-*.docx"))) == 1


def test_genereaza_raport_cu_anexa_foto(client):
    # Anexe: o fotografie (data-URL) ajunge în raport prin photos (Anexa 2)
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    png = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAA"
           "C0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==")
    p = _payload()
    p["photos"] = [png]
    r = client.post(f"/api/dosar/{uid}/raport.docx", json=p)
    assert r.status_code == 200 and len(r.content) > 1000


def test_dosar_inexistent_404(client):
    assert client.get("/dosar/nope").status_code == 404
    assert client.get("/api/dosar/nope").status_code == 404


def test_sterge_dosar(client):
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    client.post(f"/api/dosar/{uid}/sterge")
    assert client.get(f"/api/dosar/{uid}").status_code == 404


def test_scoate_dosar_disparut_din_index(client):
    import shutil

    from evaluare import dosare_fs as fs
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X"}}).json()["uuid"]
    client.get("/incepe")                                  # intră în index „ultima vedere"
    shutil.rmtree(client._baza / "date" / "dosare" / uid)  # folderul dispare de pe disc
    assert uid in fs._citeste_index()                      # încă în index (dispărut)
    assert client.post(f"/api/dosar/{uid}/scoate-din-index").json()["ok"] is True
    assert uid not in fs._citeste_index()                  # scos din index


# ── Import .docx ─────────────────────────────────────────────────────────────
def _docx_b64(tmp_path, nume):
    import base64

    import docx
    doc = docx.Document()
    doc.add_paragraph("Utilizarea desemnata a evaluării este garantarea împrumutului.")
    f = tmp_path / nume
    doc.save(str(f))
    return "data:application/octet-stream;base64," + base64.b64encode(f.read_bytes()).decode()


def test_import_docx_creeaza_dosar_precompletat(client, tmp_path):
    _cont(client)
    b64 = _docx_b64(tmp_path, "555 Maria Ionescu casa Sinaia.docx")
    r = client.post("/api/dosar/import-docx",
                    json={"nume_fisier": "555 Maria Ionescu casa Sinaia.docx", "continut": b64})
    assert r.status_code == 200
    d = r.json()
    assert d["wizard"]["id_client"] == "555"
    assert d["wizard"]["nume_client"] == "Maria Ionescu"
    assert d["wizard"]["judet"] == "Prahova"
    # raportul sursă e atașat ca versiune
    folder = client._baza / "date" / "dosare" / d["uuid"]
    assert len(list(folder.glob("raport-*.docx"))) == 1


def test_import_docx_necesita_cont(client, tmp_path):
    b64 = _docx_b64(tmp_path, "1 X casa Cluj.docx")
    r = client.post("/api/dosar/import-docx", json={"nume_fisier": "1 X casa Cluj.docx", "continut": b64})
    assert r.status_code == 403


def test_import_docx_continut_invalid_400(client):
    _cont(client)
    r = client.post("/api/dosar/import-docx",
                    json={"nume_fisier": "x.docx", "continut": "@@@nu e base64@@@"})
    assert r.status_code == 400
