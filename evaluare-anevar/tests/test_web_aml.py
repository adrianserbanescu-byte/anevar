"""Endpoint-uri AML — evaluare relatie + generare documente + store separat (tipping-off)."""
import tempfile
from pathlib import Path

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


def test_aml_doc_temp_nu_ramane_pe_disc_si_nu_e_nume_fix(tmp_path):
    # F-SEC-2: documentele AML (CNP/nume/serie act) nu trebuie sa ramana in temp-ul partajat cu nume
    # predictibil. Dupa raspuns, copia temporara se sterge (BackgroundTask); nu exista 'aml_fisa_kyc.docx'
    # cu nume FIX in temp dupa cerere.
    client, _ = _client(tmp_path)
    fix = Path(tempfile.gettempdir()) / "aml_fisa_kyc.docx"
    fix.unlink(missing_ok=True)
    resp = client.post("/api/aml/fisa-kyc.docx", json={
        "tip_entitate": "PFA", "client_pf": {"persoana": {"nume": "Ion", "prenume": "Pop"}}})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == DOCX_MIME
    # filename-ul de descarcare ramane prietenos, dar fisierul de pe disc cu nume FIX nu e lasat in urma
    assert not fix.exists()


def test_pagina_aml_se_incarca(tmp_path):
    client, _ = _client(tmp_path)
    resp = client.get("/aml")
    assert resp.status_code == 200
    assert "AML" in resp.text


def test_aml_evalueaza_data_invalida_da_422_nu_500(tmp_path):
    # P0 (schemathesis/D): azi="" (sau format invalid) crapa date.fromisoformat downstream -> 500.
    # Acum validator pe AmlEvaluareRequest.azi -> 422 clar (input hardening, NU textul juridic AML).
    client, _ = _client(tmp_path)
    assert client.post("/api/aml/evalueaza",
                       json={"azi": "", "semnale_indicatori": None}).status_code == 422
    assert client.post("/api/aml/evalueaza", json={"azi": "nu-e-data"}).status_code == 422
    # data valida ramane 200 (fara regresie)
    assert client.post("/api/aml/evalueaza", json={"azi": "2026-06-03"}).status_code == 200
    # documentul AML: azi None -> fallback (200), dar non-gol invalid -> 422
    assert client.post("/api/aml/evaluare-risc.docx", json={"azi": "xxx"}).status_code == 422


def test_aml_model_din_dict_user_invalid_da_422_nu_500(tmp_path):
    # Audit proactiv lane B: tiparul Model(**req.X) (ClientPF/PJ, Semnale, SemnaleIndicatori, RaportRTN/RTS)
    # arunca ValidationError/TypeError pe chei/tipuri gresite -> era 500. Acum _construieste -> 422.
    client, _ = _client(tmp_path)
    assert client.post("/api/aml/evalueaza", json={
        "azi": "2026-01-01", "client_pf": {"persoana": "nu-e-dict"}}).status_code == 422
    assert client.post("/api/aml/evalueaza", json={
        "azi": "2026-01-01", "semnale_indicatori": {"camp_inexistent": 1}}).status_code == 422
    assert client.post("/api/aml/rtn.docx", json={
        "azi": "2026-01-01", "rtn": {"cheie_gresita": 1}}).status_code == 422
    assert client.post("/api/aml/rts.docx", json={
        "azi": "2026-01-01", "rts": {"cheie_gresita": 1}}).status_code == 422
    # valid ramane 200
    assert client.post("/api/aml/evalueaza", json={
        "azi": "2026-06-03", "client_pf": {"persoana": {"nume": "Ion", "prenume": "Pop"}}}
    ).status_code == 200


def test_aml_date_invalide_pe_campuri_nested_dau_422_nu_500(tmp_path):
    # Re-audit A (lane B): campuri de tip data 'str' fara validator (RaportRTN.data_tranzactie,
    # RaportRTS.data_inregistrare, StatutPEP.data_incetare_functie) ajungeau la date.fromisoformat
    # downstream -> 500. Acum validator ISO pe ele -> 422 (data_incetare '' -> None, PEP curent).
    client, _ = _client(tmp_path)
    P = {"nume": "Ion", "prenume": "Pop"}
    assert client.post("/api/aml/rtn.docx", json={
        "azi": "2026-01-01", "rtn": {"suma_eur": "15000", "data_tranzactie": ""}}).status_code == 422
    assert client.post("/api/aml/rts.docx", json={
        "azi": "2026-01-01", "rts": {"motiv": "x", "data_inregistrare": "nope"}}).status_code == 422
    assert client.post("/api/aml/evalueaza", json={
        "azi": "2026-01-01",
        "client_pf": {"persoana": P, "pep": {"este_pep": True, "data_incetare_functie": "garbage"}}}
    ).status_code == 422
    # data_incetare '' -> tratat ca PEP curent (fara data), NU crash
    assert client.post("/api/aml/evalueaza", json={
        "azi": "2026-01-01",
        "client_pf": {"persoana": P, "pep": {"este_pep": True, "data_incetare_functie": ""}}}
    ).status_code == 200
    # valide -> 200
    assert client.post("/api/aml/rtn.docx", json={
        "azi": "2026-01-01", "rtn": {"suma_eur": "15000", "data_tranzactie": "2026-01-10"}}
    ).status_code == 200
