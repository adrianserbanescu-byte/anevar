"""Feedback local (offline): salvare în SQLite, listare, export CSV, pagină."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    # OUTPUT_DIR=<tmp>/date -> fișierul de feedback ajunge în <tmp> („lângă exe"), nu în repo.
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    s = Storage(tmp_path / "f.db")
    s.init()
    c = TestClient(create_app(storage=s, client=None))
    c._baza = tmp_path  # pentru aserții pe fișier
    return c


def test_feedback_se_salveaza_si_se_listeaza(client):
    assert client.get("/api/feedback").json()["feedback"] == []
    r = client.post("/api/feedback", json={"mesaj": "Grila nu se actualizează",
                                           "sentiment": "👎 problemă", "pagina": "grila",
                                           "url": "http://x/grila", "tester": "ing. Popescu"})
    assert r.status_code == 200 and r.json()["total"] == 1
    lista = client.get("/api/feedback").json()["feedback"]
    assert len(lista) == 1
    assert lista[0]["mesaj"] == "Grila nu se actualizează"
    assert lista[0]["tester"] == "ing. Popescu"
    assert lista[0]["creat_la"]  # are timestamp


def test_feedback_scrie_fisier_langa_exe(client):
    from datetime import datetime
    r = client.post("/api/feedback", json={"mesaj": "în fișier", "pagina": "wizard",
                                            "tester": "Popescu", "sentiment": "👍 merge"})
    nume = r.json()["fisier"]
    assert nume.startswith("feedback-") and nume.endswith(".csv")
    f = client._baza / nume
    assert f.exists(), f
    continut = f.read_text(encoding="utf-8-sig")
    assert "în fișier" in continut and "Popescu" in continut and "data,pagina" in continut
    # a doua trimitere se adaugă în ACELAȘI fișier (per zi)
    client.post("/api/feedback", json={"mesaj": "a doua", "pagina": "grila"})
    assert datetime.now().strftime("%Y-%m-%d") in nume
    assert "a doua" in f.read_text(encoding="utf-8-sig")


def test_feedback_gol_respins(client):
    r = client.post("/api/feedback", json={"mesaj": "", "sentiment": ""})
    assert r.status_code == 422


def test_feedback_doar_reactie_acceptat(client):
    r = client.post("/api/feedback", json={"sentiment": "👍 merge", "pagina": "wizard"})
    assert r.status_code == 200


def test_feedback_csv_export(client):
    client.post("/api/feedback", json={"mesaj": "ok", "pagina": "aml", "tester": "T"})
    r = client.get("/api/feedback.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment; filename=feedback.csv" in r.headers["content-disposition"]
    text = r.text
    assert "pagina" in text and "aml" in text and "ok" in text


def test_pagina_feedback_se_randeaza(client):
    client.post("/api/feedback", json={"mesaj": "vizibil în pagină", "pagina": "wizard"})
    r = client.get("/feedback")
    assert r.status_code == 200
    assert "vizibil în pagină" in r.text


def test_feedback_persista_intre_instante(tmp_path):
    s = Storage(tmp_path / "p.db")
    s.init()
    s.adauga_feedback({"mesaj": "persist", "sentiment": "", "pagina": "x", "url": "", "tester": ""})
    # o nouă instanță Storage pe același fișier vede feedback-ul
    assert len(Storage(tmp_path / "p.db").listeaza_feedback()) == 1


# ── SEC-A-01: neutralizare formula-injection în exporturile CSV de feedback ──────
def test_feedback_fisier_neutralizeaza_formula_injection(client):
    # Câmpuri user ostile (= + - @) — în fișierul CSV de lângă exe trebuie prefixate cu apostrof,
    # ca Excel/LibreOffice să le trateze ca text, nu ca formulă LIVE (CWE-1236).
    r = client.post("/api/feedback", json={
        "mesaj": "=cmd|'/c calc'!A1", "sentiment": "@SUM(1+1)", "pagina": "-2+3",
        "url": "=HYPERLINK(\"http://evil\")", "tester": "+1"})
    nume = r.json()["fisier"]
    continut = (client._baza / nume).read_text(encoding="utf-8-sig")
    assert "'=cmd|" in continut
    assert "'@SUM(1+1)" in continut
    assert "'-2+3" in continut
    assert "'=HYPERLINK" in continut
    assert "'+1" in continut
    # nicio celulă nu mai ÎNCEPE cu un caracter de formulă neneutralizat (după virgulă)
    assert ",=cmd" not in continut and ",@SUM" not in continut and ",-2+3" not in continut


def test_feedback_fisier_control_apoi_formula_nu_scapa(client):
    # `\x01=cmd`: după curățarea caracterului de control, `=cmd` NU trebuie să rămână prefix de formulă.
    r = client.post("/api/feedback", json={"mesaj": "\x01=cmd|'/c calc'!A1", "pagina": "x"})
    continut = (client._baza / r.json()["fisier"]).read_text(encoding="utf-8-sig")
    assert "\x01" not in continut
    assert "'=cmd|" in continut


def test_feedback_csv_export_neutralizeaza_formula_injection(client):
    client.post("/api/feedback", json={
        "mesaj": "=cmd|'/c calc'!A1", "sentiment": "@SUM(1+1)", "pagina": "-2+3",
        "url": "=HYPERLINK(\"http://evil\")", "tester": "+1"})
    text = client.get("/api/feedback.csv").text
    assert "'=cmd|" in text
    assert "'@SUM(1+1)" in text
    assert "'-2+3" in text
    assert "'=HYPERLINK" in text
    assert "'+1" in text
    assert ",=cmd" not in text and ",@SUM" not in text


def test_feedback_csv_neutralizare_nu_atinge_textul_curat(client):
    # Text fără caracter de formulă la început rămâne neprefixat (fără apostrof parazit).
    client.post("/api/feedback", json={"mesaj": "merge ok", "pagina": "wizard", "tester": "Popescu"})
    text = client.get("/api/feedback.csv").text
    assert "merge ok" in text and "'merge" not in text
    assert "Popescu" in text and "'Popescu" not in text
