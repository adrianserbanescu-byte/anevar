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
    assert data["index_selectat"] == 0                  # cel mai similar (gross 0.05 < 0.30)
    # M2 (default = media a 3, aici limitat la 2 comparabile): (105 + 84)/2 = 94.5 €/mp * 1000 = 94500
    assert Decimal(data["valoare_teren"]) == Decimal("94500.00")


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
    assert data["index_selectat"] == 1                  # cel mai similar (gross 0.05 < 0.20)
    # M2 (default = media a 3, aici limitat la 2 comparabile): media (9.60 + 10.50)/2 = 10.05 €/mp
    assert Decimal(data["chirie_mp_aleasa"]) == Decimal("10.05")
    assert Decimal(data["chirie_lunara"]) == Decimal("1005.00")    # 10.05 * 100
    assert Decimal(data["venit_brut_potential"]) == Decimal("12060.00")   # * 12


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


def test_grila_chirii_rotunjeste_toate_iesirile_monetare(tmp_path):
    # #2 (D+A): media M2 a ratei €/mp poate avea multe zecimale -> endpoint rotunjeste la bani TOATE
    # iesirile monetare (chirie_mp/lunara/vbp), ca sa nu ajunga brute in wizard via localStorage.
    client = _client(tmp_path)
    comps = [{"chirie_mp": c, "suprafata": "100"} for c in ("10", "10", "11")]   # media = 10.333...
    d = client.post("/api/grila-chirii",
                    json={"suprafata_subiect": "100", "comparabile": comps}).json()
    assert d["chirie_mp_aleasa"] == "10.33"          # rotunjit, nu 10.3333...
    for k in ("chirie_mp_aleasa", "chirie_lunara", "venit_brut_potential"):
        assert len(d[k].split(".")[-1]) <= 2         # toate <= 2 zecimale


def test_grila_teren_rotunjeste_pret_mp(tmp_path):
    # #2: pret/mp mediat (M2) rotunjit la bani in API
    client = _client(tmp_path)
    comps = [{"pret_mp": p, "suprafata": "500"} for p in ("100", "100", "101")]   # media = 100.333...
    d = client.post("/api/grila-teren",
                    json={"suprafata_subiect": "500", "comparabile": comps}).json()
    assert d["pret_mp_ales"] == "100.33" and len(d["valoare_teren"].split(".")[-1]) <= 2


def test_grila_input_degenerat_da_422_nu_500(tmp_path):
    # P0 (schemathesis/D): input numeric degenerat (valori uriase ~1e308 -> overflow la quantize, sau
    # "Infinity"/"NaN" string) -> 422 clar, NU 500. Toate 3 grilele.
    client = _client(tmp_path)
    assert client.post("/api/grila-teren", json={
        "suprafata_subiect": 1.7e308,
        "comparabile": [{"pret_mp": 1.7e308, "suprafata": 500}] * 3}).status_code == 422
    assert client.post("/api/grila-teren", json={
        "suprafata_subiect": 100,
        "comparabile": [{"pret_mp": "Infinity", "suprafata": 500}] * 3}).status_code == 422
    assert client.post("/api/grila-teren", json={
        "suprafata_subiect": 100,
        "comparabile": [{"pret_mp": "NaN", "suprafata": 500}] * 3}).status_code == 422
    assert client.post("/api/grila-casa", json={
        "suprafata_subiect": 100,
        "comparabile": [{"pret": 1.7e308, "suprafata": 500}] * 3}).status_code == 422
    assert client.post("/api/grila-chirii", json={
        "suprafata_subiect": 1.7e308,
        "comparabile": [{"chirie_mp": 100, "suprafata": 500}] * 3}).status_code == 422
