"""Web: Registrul rapoartelor (pagina + export CSV/XLSX), numarul de lucrare pe coperta,
si pachetul de inspectie per dosar (/api/dosar/{uid}/export.zip) — Procedura §6/§11/§12."""
from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _fake_pdf(docx):
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


def _cont(client):
    return client.post("/api/cont", json={"nume": "Adi S", "legitimatie": "8717",
                                          "format_dosar": ["nume_client"]})


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


def _dosar(client, **wizard):
    _cont(client)
    w = {"nume_client": "Pop Ion", "scop": "garantare", "numar_cadastral": "12345"}
    w.update(wizard)
    return client.post("/api/dosar", json={"wizard": w}).json()["uuid"]


# ── Numar de lucrare alocat la creare ─────────────────────────────────────────
def test_dosar_nou_primeste_nr_lucrare(client):
    uid = _dosar(client)
    d = client.get(f"/api/dosar/{uid}").json()
    assert "/" in (d.get("nr_lucrare") or "")
    assert d["nr_lucrare"].endswith("/0001")


# ── Pagina + JSON ─────────────────────────────────────────────────────────────
def test_pagina_registru(client):
    _dosar(client, nume_client="Vasilescu")
    r = client.get("/registru")
    assert r.status_code == 200
    assert "Registrul rapoartelor" in r.text and "Vasilescu" in r.text


def test_api_registru_json(client):
    _dosar(client, nume_client="Unu")
    _dosar(client, nume_client="Doi")
    j = client.get("/api/registru").json()
    assert len(j["randuri"]) == 2
    chei = {c["cheie"] for c in j["coloane"]}
    assert {"nr_lucrare", "onorariu", "verificator", "risc_aml"}.issubset(chei)


# ── Export CSV / XLSX ─────────────────────────────────────────────────────────
def test_export_csv(client):
    _dosar(client, nume_client="Popescu", onorariu="1500")
    r = client.get("/api/registru.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "registru-rapoarte.csv" in r.headers["content-disposition"]
    assert "Popescu" in r.text and "1500" in r.text


def test_export_xlsx(client):
    _dosar(client, nume_client="Ionescu")
    r = client.get("/api/registru.xlsx")
    assert r.status_code == 200
    assert "spreadsheetml" in r.headers["content-type"]
    assert r.content[:2] == b"PK"
    z = zipfile.ZipFile(io.BytesIO(r.content))
    assert "Ionescu" in z.read("xl/worksheets/sheet1.xml").decode("utf-8")


# ── Coperta raportului poarta numarul de identificare ─────────────────────────
def test_coperta_contine_nr_lucrare(client):
    from docx import Document
    uid = _dosar(client)
    nr = client.get(f"/api/dosar/{uid}").json()["nr_lucrare"]
    r = client.post(f"/api/dosar/{uid}/raport.docx", json=_payload())
    assert r.status_code == 200
    doc = Document(io.BytesIO(r.content))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Nr. de identificare raport" in text
    assert nr in text


# ── Pachet de inspectie per dosar ─────────────────────────────────────────────
def test_export_dosar_zip(client):
    uid = _dosar(client)
    client.post(f"/api/dosar/{uid}/raport.docx", json=_payload())   # asuma o versiune .docx
    r = client.get(f"/api/dosar/{uid}/export.zip")
    assert r.status_code == 200
    assert "application/zip" in r.headers["content-type"]
    z = zipfile.ZipFile(io.BytesIO(r.content))
    nume = z.namelist()
    assert "dosar.json" in nume
    assert "verifica_integritate.txt" in nume
    assert any(n.startswith("raport-") and n.endswith(".docx") for n in nume)
    integ = z.read("verifica_integritate.txt").decode("utf-8")
    assert "INTEGRU" in integ                                # versiunea asumata e integra


def test_export_dosar_zip_fara_lock(client):
    # .lock (stare tranzitorie de deschidere) NU intra in pachetul de arhiva.
    uid = _dosar(client)
    client.post(f"/api/dosar/{uid}/lock", json={"token": "t1"})
    z = zipfile.ZipFile(io.BytesIO(client.get(f"/api/dosar/{uid}/export.zip").content))
    assert ".lock" not in z.namelist()


def test_export_dosar_uid_invalid_404(client):
    assert client.get("/api/dosar/nope/export.zip").status_code == 404
    assert client.get("/api/dosar/../export.zip").status_code in (404, 400)


# ── Pregatire BIG per dosar (GEV 520 §7) ──────────────────────────────────────
def test_big_dosar_incomplet_listeaza_lipsuri(client):
    # Dosar minimal (doar identitate) -> multe campuri minime BIG lipsa, dar nu pica.
    uid = _dosar(client, nume_client="Pop", tip_proprietate="casa")
    r = client.get(f"/api/dosar/{uid}/big")
    assert r.status_code == 200
    j = r.json()
    assert j["uid"] == uid
    assert j["gata"] is False
    assert isinstance(j["lipsuri"], list) and j["lipsuri"]
    # Evaluatorul (creatorul contului) + nr de lucrare sunt completate automat -> NU apar ca lipsa.
    assert "Numele evaluatorului" not in j["lipsuri"]
    assert "Numărul de identificare a raportului" not in j["lipsuri"]
    # Banca/valoarea/codul postal nu sunt completate -> apar ca lipsa.
    assert "Banca / utilizatorul desemnat (creditorul)" in j["lipsuri"]
    assert "Valoarea de piață (concluzia evaluatorului)" in j["lipsuri"]


def test_big_dosar_complet_e_gata(client):
    uid = _dosar(client,
                 nume_client="Ionescu", tip_proprietate="teren",
                 beneficiar="Banca Transilvania", cod_postal="400001",
                 judet="Cluj", localitate="Cluj-Napoca",
                 suprafata_teren="500", moneda="RON",
                 data_evaluarii="2026-01-16", valoare_finala="123000")
    j = client.get(f"/api/dosar/{uid}/big").json()
    assert j["gata"] is True, j["lipsuri"]
    assert j["lipsuri"] == []
    # Payload-ul reflecta datele introduse (mapate la campurile BIG).
    p = j["payload"]
    assert p["banca"] == "Banca Transilvania"
    assert p["tip_proprietate"] == "teren"
    assert p["cod_postal"] == "400001"
    assert str(p["valoare_piata"]) == "123000"


def test_big_uid_invalid_404(client):
    assert client.get("/api/dosar/nope/big").status_code == 404


# ── H14-1: suprafata/valoare <=0 -> checklist „lipsa", NU 500 ──────────────────
@pytest.mark.parametrize("camp,valoare", [
    ("suprafata_teren", "0"),
    ("suprafata_teren", "-5"),
    ("suprafata_teren", "0.0"),
    ("valoare_finala", "0"),
    ("valoare_finala", "-100"),
])
def test_big_suprafata_valoare_nepozitiva_nu_da_500(client, camp, valoare):
    uid = _dosar(client, nume_client="Pop", tip_proprietate="teren", **{camp: valoare})
    r = client.get(f"/api/dosar/{uid}/big")
    assert r.status_code == 200, r.text          # NU mai e 500 (ValidationError prinsa)
    j = r.json()
    assert j["gata"] is False
    # valoarea ne-pozitiva e tratata ca LIPSA -> apare in checklist
    if camp == "suprafata_teren":
        assert "Suprafața" in j["lipsuri"]
    else:
        assert "Valoarea de piață (concluzia evaluatorului)" in j["lipsuri"]


def test_registru_nu_cade_din_dosar_otravit(client):
    # Un dosar cu suprafata=0 nu trebuie sa darame pagina /registru pentru toti.
    _dosar(client, nume_client="Bun", tip_proprietate="teren", suprafata_teren="500")
    _dosar(client, nume_client="Otravit", tip_proprietate="teren", suprafata_teren="0",
           valoare_finala="-1")
    r = client.get("/registru")
    assert r.status_code == 200                   # pagina intreaga supravietuieste
    assert "Bun" in r.text and "Otravit" in r.text


def test_registru_arata_pregatirea_big(client):
    _dosar(client, nume_client="Vasilescu", tip_proprietate="casa")
    r = client.get("/registru")
    assert r.status_code == 200
    assert "Pregătire BIG" in r.text
    # Dosar incomplet -> pastila „lipsă" pe pagina.
    assert "lipsă" in r.text
