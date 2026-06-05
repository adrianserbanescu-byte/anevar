"""Feedback local (offline): salvare în SQLite, listare, export CSV, pagină."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path):
    s = Storage(tmp_path / "f.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


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
