from decimal import Decimal

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_grila_teren(tmp_path):
    client = _client(tmp_path)
    payload = {
        "suprafata_subiect": "1000",
        "comparabile": [
            {"pret_mp": "100", "suprafata": "450",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "0.05"}]},
            {"pret_mp": "120", "suprafata": "500",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "-0.30"}]},
        ],
    }
    resp = client.post("/api/grila-teren", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["index_selectat"] == 0
    assert Decimal(data["valoare_teren"]) == Decimal("105000.00")


def test_grila_casa(tmp_path):
    client = _client(tmp_path)
    payload = {
        "suprafata_subiect": "100",
        "comparabile": [
            {"pret": "500000", "suprafata": "100",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "0.05"}]},
            {"pret": "520000", "suprafata": "100",
             "adjustments": [{"element": "A", "tip": "procentuala", "valoare": "-0.20"}]},
            {"pret": "510000", "suprafata": "100", "adjustments": []},
        ],
    }
    resp = client.post("/api/grila-casa", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "valoare_piata" in data
    assert "index_selectat" in data


def test_grila_chirii(tmp_path):
    client = _client(tmp_path)
    payload = {
        "suprafata_subiect": "100",
        "comparabile": [
            {"chirie_mp": "12", "suprafata": "120",
             "adjustments": [{"element": "stare", "tip": "procentuala", "valoare": "-0.20",
                              "etapa": "proprietate"}]},   # bruta 0.20
            {"chirie_mp": "10", "suprafata": "100",
             "adjustments": [{"element": "finisaj", "tip": "procentuala", "valoare": "0.05",
                              "etapa": "proprietate"}]},   # bruta 0.05 -> ales
        ],
    }
    resp = client.post("/api/grila-chirii", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["index_selectat"] == 1
    assert Decimal(data["chirie_mp_aleasa"]) == Decimal("10.50")
    assert Decimal(data["chirie_lunara"]) == Decimal("1050.00")
    assert Decimal(data["venit_brut_potential"]) == Decimal("12600.00")


def test_grila_chirii_fara_comparabile_422(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/grila-chirii",
                       json={"suprafata_subiect": "100", "comparabile": []})
    assert resp.status_code == 422


def test_pagina_grila_se_incarca(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/grila")
    assert resp.status_code == 200
    assert "Grilă teren" in resp.text
    assert "Grilă casă" in resp.text
    assert "Grilă chirii" in resp.text
    assert "/api/grila-teren" in resp.text
    assert "/api/grila-casa" in resp.text
    assert "/api/grila-chirii" in resp.text
    assert "trimiteVbpWizard" in resp.text          # punte VBP grila -> wizard


def test_wizard_preia_vbp_din_grila(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/wizard")
    assert resp.status_code == 200
    assert "preiaVbpGrila" in resp.text
    assert "vbp_din_grila" in resp.text
