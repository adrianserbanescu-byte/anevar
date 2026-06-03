from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_audit_txt_pentru_dosar(tmp_path):
    client = _client(tmp_path)
    payload = {
        "meta": {"client_nume": "X", "adresa": "A", "numar_cadastral": "1", "carte_funciara": "CF1",
                 "evaluator_nume": "E", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-06-03", "data_raportului": "2026-06-03"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp",
                                   "cantitate": "120", "cost_unitar": "1500", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                             {"varsta": 15, "depreciere": "0.15"}]},
        "valoare_teren": "40000", "metoda": "cost",
    }
    eid = client.post("/api/evaluare", json=payload).json()["id"]
    resp = client.get(f"/api/evaluare/{eid}/audit.txt")
    assert resp.status_code == 200
    text = resp.text
    assert "URMA DE AUDIT" in text
    assert "integritate lant: OK" in text
    assert "valoare_finala" in text
    assert "identificare" in text


def test_audit_txt_dosar_inexistent(tmp_path):
    client = _client(tmp_path)
    assert client.get("/api/evaluare/999/audit.txt").status_code == 404
