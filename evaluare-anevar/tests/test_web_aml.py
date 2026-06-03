"""Endpoint-uri AML — evaluare relatie + generare documente + store separat (tipping-off)."""
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None)), storage


def test_aml_evalueaza_pf_standard(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/api/aml/evalueaza", json={
        "tip_entitate": "PFA", "azi": "2026-06-03",
        "client_pf": {"persoana": {"nume": "Ion", "prenume": "Popescu"}},
    })
    assert resp.status_code == 200
    d = resp.json()
    assert d["categorie"] == "standard"
    assert d["necesita_persoana_desemnata"] is False
    assert "decizie_desemnare" not in d["documente_necesare"]


def test_aml_evalueaza_pep_sporit_si_rts(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/api/aml/evalueaza", json={
        "tip_entitate": "PJ", "azi": "2026-06-03",
        "client_pf": {"persoana": {"nume": "Ion", "prenume": "Popescu"},
                      "pep": {"este_pep": True}},
        "semnale_indicatori": {"presiune_valoare_predeterminata": True},
    })
    d = resp.json()
    assert d["categorie"] == "sporit"
    assert d["propune_rts"] is True
    assert "decizie_desemnare" in d["documente_necesare"]   # societate
    assert "rts" in d["documente_necesare"]


def test_aml_norme_interne_docx(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/api/aml/norme-interne.docx", json={"tip_entitate": "PFA"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == DOCX_MIME
    assert len(resp.content) > 0


def test_aml_decizie_refuzata_pentru_pfa(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/api/aml/decizie.docx", json={
        "tip_entitate": "PFA", "persoana_desemnata": {"nume": "X", "prenume": "Y"}})
    assert resp.status_code == 400


def test_aml_decizie_ok_pentru_societate(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.post("/api/aml/decizie.docx", json={
        "tip_entitate": "PJ", "persoana_desemnata": {"nume": "Ana", "prenume": "Ionescu"}})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == DOCX_MIME


def test_aml_rts_se_stocheaza_separat(tmp_path):
    client, storage = _client(tmp_path)
    resp = client.post("/api/aml/rts.docx", json={
        "tip_entitate": "PFA",
        "rts": {"motiv": "presiune valoare", "data_inregistrare": "2026-06-05",
                "indicatori": ["presiune_valoare_predeterminata"]}})
    assert resp.status_code == 200
    # fisierul RTS persistat in directorul confidential, separat de baza de date
    conf = storage.db_path.parent / "aml_confidential"
    assert conf.is_dir()
    assert any(p.name.startswith("rts_") for p in conf.iterdir())


def test_aml_rtn_docx_si_store(tmp_path):
    client, storage = _client(tmp_path)
    resp = client.post("/api/aml/rtn.docx", json={
        "rtn": {"suma_eur": "12000", "data_tranzactie": "2026-06-03"}})
    assert resp.status_code == 200
    conf = storage.db_path.parent / "aml_confidential"
    assert any(p.name.startswith("rtn_") for p in conf.iterdir())


def test_pagina_aml_se_incarca(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.get("/aml")
    assert resp.status_code == 200
    assert "AML" in resp.text
