"""UI nou (versiunea curentă): cont local + ÎNCEPE + workspace dosar (stocare pe foldere)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _fake_pdf(docx):
    """Convertor PDF fals (deterministic, fără LibreOffice) pentru teste."""
    from pathlib import Path
    p = Path(docx).with_suffix(".pdf")
    p.write_bytes(b"%PDF-1.4 fake\n%%EOF")
    return p


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "d.db")
    s.init()
    c = TestClient(create_app(storage=s, client=None, pdf_converter=_fake_pdf))
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


def test_genereaza_cu_adnotari(client):
    # opțiune Generează: adnotări de proveniență (raport de review)
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    r = client.post(f"/api/dosar/{uid}/raport.docx?adnotari=1", json=_payload())
    assert r.status_code == 200 and len(r.content) > 1000


def test_audit_txt_pe_flux_foldere(client):
    # Audit in-place: urma de audit pe fluxul nou (foldere), fără SQLite
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    r = client.post(f"/api/dosar/{uid}/audit.txt", json=_payload())
    assert r.status_code == 200 and "valoare_finala" in r.text
    assert client.post("/api/dosar/nope/audit.txt", json=_payload()).status_code == 404


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


def test_backup_dosare_zip(client):
    # Backup: arhivează toate dosarele într-un .zip
    import io
    import zipfile
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "Z"}}).json()["uuid"]
    r = client.get("/api/backup-dosare.zip")
    assert r.status_code == 200
    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert any(uid in n and n.endswith("dosar.json") for n in z.namelist())


# ── Hardening din auditul final (securitate + buguri) ────────────────────────
def test_grila_casa_goala_422(client):
    # bug: <3 comparabile -> ValueError din motor; trebuie 422 clar, NU 500.
    assert client.post("/api/grila-casa", json={"suprafata_subiect": "120", "comparabile": []}).status_code == 422
    assert client.post("/api/grila-teren", json={"suprafata_subiect": "500", "comparabile": []}).status_code == 422


def test_raport_date_insuficiente_422(client):
    # robustețe: cost fără puncte de depreciere -> 422 clar (din motor), NU 500 nehandelat.
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    p = _payload()
    p["building"]["depreciation_points"] = []
    assert client.post(f"/api/dosar/{uid}/raport.docx", json=p).status_code == 422
    assert client.post(f"/api/dosar/{uid}/calcul", json=p).status_code == 422


def test_import_docx_continut_invalid_nu_crapa(client):
    # robustețe: conținut care NU e .docx valid -> NU 500; degradează grațios la parsarea numelui.
    import base64
    _cont(client)
    payload = base64.b64encode(b"acesta nu este un document Word").decode()
    r = client.post("/api/dosar/import-docx",
                    json={"nume_fisier": "1_Test_casa.docx", "continut": payload})
    assert r.status_code == 200 and "uuid" in r.json()


def test_evaluare_veche_date_insuficiente_422(client):
    # endpoint-ul vechi /api/evaluare nu trebuie să dea 500 pe date incomplete.
    _cont(client)
    p = _payload()
    p["building"]["depreciation_points"] = []
    assert client.post("/api/evaluare", json=p).status_code == 422


def test_raport_format_pdf(client):
    # userul alege PDF -> conversie (fake în test) -> răspuns application/pdf.
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    r = client.post(f"/api/dosar/{uid}/raport.docx?fmt=pdf", json=_payload())
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


def test_raport_format_ambele_zip(client):
    # „amândouă" -> .zip cu .docx + .pdf.
    import io
    import zipfile
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    r = client.post(f"/api/dosar/{uid}/raport.docx?fmt=ambele", json=_payload())
    assert r.status_code == 200
    nume = zipfile.ZipFile(io.BytesIO(r.content)).namelist()
    assert any(n.endswith(".docx") for n in nume) and any(n.endswith(".pdf") for n in nume)


def test_raport_pdf_indisponibil_422(tmp_path, monkeypatch):
    # fără convertor (LibreOffice/Word) -> 422 clar; .docx-ul tot se salvează în dosar.
    from evaluare.report.pdf import PdfIndisponibil

    def _fara_convertor(_docx):
        raise PdfIndisponibil("niciun convertor")

    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "d.db")
    s.init()
    c = TestClient(create_app(storage=s, client=None, pdf_converter=_fara_convertor))
    _cont(c)
    uid = c.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    r = c.post(f"/api/dosar/{uid}/raport.docx?fmt=pdf", json=_payload())
    assert r.status_code == 422
    assert "LibreOffice" in r.json()["detail"]
    # .docx-ul rămâne salvat ca versiune (userul nu pierde munca)
    assert (tmp_path / "date" / "dosare" / uid).exists()


def test_incarca_submis_marcheaza_asumat(client):
    # ADR-003 trigger #3 (decizia Adi #10): .docx submis → versiune „submis" + identitate asumată.
    import base64
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X"}}).json()["uuid"]
    payload = base64.b64encode(b"PK raport finalizat returnat de banca").decode()
    r = client.post(f"/api/dosar/{uid}/incarca-submis",
                    json={"nume_fisier": "raport-final.docx", "continut": payload})
    assert r.status_code == 200 and r.json()["asumat_la"]
    d = client.get(f"/api/dosar/{uid}").json()
    assert any(v["tip"] == "submis" for v in d.get("versiuni", []))


def test_deblocheaza_si_cloneaza_endpoints(client):
    # ADR-003: deblocheaza (motiv obligatoriu → 422 fără) + cloneaza (dosar nou); identitate read-only după asumare.
    import base64
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X", "au": "100"}}).json()["uuid"]
    client.post(f"/api/dosar/{uid}/incarca-submis",
                json={"nume_fisier": "r.docx", "continut": base64.b64encode(b"raport").decode()})
    # identitate înghețată după asumare (salveaza nu schimbă nume_client)
    client.post(f"/api/dosar/{uid}/salveaza", json={"nume_client": "ALTUL", "au": "999"})
    assert client.get(f"/api/dosar/{uid}").json()["wizard"]["nume_client"] == "X"
    # deblocare fără motiv → 422
    assert client.post(f"/api/dosar/{uid}/deblocheaza", json={"motiv": " "}).status_code == 422
    r = client.post(f"/api/dosar/{uid}/deblocheaza", json={"motiv": "typo nume"})
    assert r.status_code == 200 and r.json()["blocat"] is False
    # clonare → dosar nou diferit
    rc = client.post(f"/api/dosar/{uid}/cloneaza")
    assert rc.status_code == 200 and rc.json()["uuid"] != uid
    assert client.post("/api/dosar/zzz/cloneaza").status_code == 404


def test_dosar_html_arata_lock_dupa_asumare(client):
    # ADR-003 UI: pagina dosarului arată bannerul de lock + butoanele DOAR după asumare.
    import base64
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X"}}).json()["uuid"]
    # neasumat: fără banner (butonul de deblocare apare DOAR în blocul {% if blocat %})
    assert 'id="btn-delock"' not in client.get(f"/dosar/{uid}").text
    assert "var BLOCAT = false" in client.get(f"/dosar/{uid}").text
    client.post(f"/api/dosar/{uid}/incarca-submis",
                json={"nume_fisier": "r.docx", "continut": base64.b64encode(b"r").decode()})
    html = client.get(f"/dosar/{uid}").text
    assert 'id="btn-delock"' in html and 'id="btn-clone"' in html   # banner de lock prezent
    assert "var BLOCAT = true" in html


def test_dosar_json_corupt_nu_crapa(client):
    # robustețe: dosar.json corupt -> 404 clar (nu 500); workspace-ul nu trebuie să crape la deschidere.
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {"nume_client": "X"}}).json()["uuid"]
    (client._baza / "date" / "dosare" / uid / "dosar.json").write_text("{ corupt", encoding="utf-8")
    assert client.get(f"/dosar/{uid}").status_code == 404
    assert client.get(f"/api/dosar/{uid}").status_code == 404


def test_calcul_alerte_sunt_expuse(client):
    # contractul „aplicația avertizează, nu decide": Au>Acd trebuie să apară în `alerte` (nu 200 mut).
    _cont(client)
    uid = client.post("/api/dosar", json={"wizard": {}}).json()["uuid"]
    p = _payload()
    p["building"]["au"] = "200"          # Au(200) > Acd(120) -> alertă de proprietate
    r = client.post(f"/api/dosar/{uid}/calcul", json=p)
    assert r.status_code == 200
    alerte = r.json()["alerte"]
    assert isinstance(alerte, list) and len(alerte) >= 1


def test_import_prea_mare_413(client):
    _cont(client)
    big = "A" * 35_000_001            # peste limita anti-DoS
    assert client.post("/api/dosar/import-docx",
                       json={"nume_fisier": "x.docx", "continut": big}).status_code == 413
    assert client.post("/api/ingestie", json={"tip": "cf", "continut": big}).status_code == 413


def test_host_nelocal_respins_403(client):
    # gardă anti DNS-rebinding: Host ne-local -> 403; default (testserver) -> OK.
    assert client.get("/incepe", headers={"host": "evil.com"}).status_code == 403
    assert client.get("/incepe").status_code == 200


def test_ssrf_url_guard():
    from evaluare.importers.url_parser import _url_public_sigur
    assert _url_public_sigur("http://127.0.0.1:5432") is False      # loopback
    assert _url_public_sigur("http://169.254.169.254/") is False    # link-local (metadata)
    assert _url_public_sigur("http://10.0.0.5/x") is False          # privat
    assert _url_public_sigur("file:///etc/passwd") is False         # schemă nepermisă


def test_cnp_redaction_prefix_9():
    from evaluare.ai import narrative
    rx = narrative._PII_REZIDUAL[0][0]
    assert rx.search("9800101123456")    # rezident străin (prefix 9) — acum prins
    assert rx.search("1800101123456")    # cetățean (prefix 1) — în continuare prins


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
