"""Acoperire pentru căile HTTP rămase: curs-BNR, indice ANEVAR, ingestie (erori),
dosar inexistent (404), backup, și cablarea tip/scop prin /api/evaluare."""
from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path):
    s = Storage(tmp_path / "g.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


def _evaluare_payload(**extra):
    p = {
        "meta": {"client_nume": "X", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF",
                 "evaluator_nume": "E", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                                   "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                             {"varsta": 15, "depreciere": "0.15"}]},
        "comparables": [{"pret": "250000", "suprafata": "120"},
                        {"pret": "260000", "suprafata": "125"},
                        {"pret": "240000", "suprafata": "118"}],
        "valoare_teren": "100000", "metoda": "cost",
    }
    p.update(extra)
    return p


# ---------- curs BNR ----------
def test_curs_bnr_ok(client, monkeypatch):
    monkeypatch.setattr("evaluare.curs_bnr.curs_bnr",
                        lambda m: {"moneda": "EUR", "curs": Decimal("4.9750"), "data": "2026-06-05"})
    r = client.get("/api/curs-bnr?moneda=EUR")
    assert r.status_code == 200
    assert r.json() == {"moneda": "EUR", "curs": "4.9750", "data": "2026-06-05"}


def test_curs_bnr_valuta_inexistenta_404(client, monkeypatch):
    monkeypatch.setattr("evaluare.curs_bnr.curs_bnr", lambda m: None)
    r = client.get("/api/curs-bnr?moneda=ZZZ")
    assert r.status_code == 404


def test_curs_bnr_retea_cazuta_502(client, monkeypatch):
    def cade(m):
        raise OSError("fără rețea")
    monkeypatch.setattr("evaluare.curs_bnr.curs_bnr", cade)
    r = client.get("/api/curs-bnr")
    assert r.status_code == 502
    assert "BNR" in r.json()["detail"]


# ---------- indice ANEVAR ----------
def test_indice_anevar_taie_la_ultimele(client, monkeypatch):
    date = {"orase": ["București"],
            "perioade": [{"perioada": f"T{i}", "valori": {"București": i}} for i in range(1, 9)]}
    monkeypatch.setattr("evaluare.indice_anevar.indice_anevar", lambda fetcher=None: dict(date))
    r = client.get("/api/indice-anevar?ultimele=3")
    assert r.status_code == 200
    assert len(r.json()["perioade"]) == 3
    assert r.json()["perioade"][-1]["perioada"] == "T8"


def test_indice_anevar_retea_cazuta_502(client, monkeypatch):
    def cade(fetcher=None):
        raise OSError("fără rețea")
    monkeypatch.setattr("evaluare.indice_anevar.indice_anevar", cade)
    r = client.get("/api/indice-anevar")
    assert r.status_code == 502


# ---------- ingestie: căi de eroare ----------
def test_ingestie_tip_necunoscut_400(client):
    r = client.post("/api/ingestie", json={"tip": "habarnam", "continut": "x"})
    assert r.status_code == 400


def test_ingestie_base64_invalid_400(client):
    r = client.post("/api/ingestie", json={"tip": "cf", "continut": "data:application/pdf;base64,!!nu-e-base64!!"})
    assert r.status_code == 400


# ---------- dosar inexistent: 404 pe toate rutele ----------
def test_dosar_inexistent_404(client):
    for url in ("/api/evaluare/9999", "/api/evaluare/9999/raport.docx", "/api/evaluare/9999/audit.txt"):
        assert client.get(url).status_code == 404


def test_backup_descarca_copie(client):
    # Baza există (init) -> backup-ul reușește și întoarce un fișier binar.
    r = client.get("/api/backup.db")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/octet-stream"
    assert len(r.content) > 0


# ---------- /api/evaluare end-to-end: tip + scop -> profil ----------
def test_evaluare_cu_tip_si_scop(client):
    r = client.post("/api/evaluare", json=_evaluare_payload(tip_proprietate="apartament",
                                                            scop="raportare_financiara"))
    assert r.status_code == 200
    d = r.json()
    assert "id" in d and Decimal(d["valoare_finala"]) > 0
    # raportul reflectă profilul (apartament + raportare) — se generează fără eroare
    assert client.get(f"/api/evaluare/{d['id']}/raport.docx").status_code == 200


def test_evaluare_agricol_fara_cost(client):
    # Agricol fără elemente de cost -> valoarea vine din comparație (nu cost).
    r = client.post("/api/evaluare", json=_evaluare_payload(
        tip_proprietate="agricol", metoda="piata",
        building={"au": "100", "acd": "120", "an_referinta": 2025,
                  "elements": [], "depreciation_points": []}))
    assert r.status_code == 200
    assert r.json()["metoda"] == "piata"
