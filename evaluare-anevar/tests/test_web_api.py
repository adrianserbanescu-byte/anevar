from decimal import Decimal

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _payload() -> dict:
    return {
        "meta": {
            "client_nume": "Ion Popescu", "adresa": "Str. 1",
            "numar_cadastral": "123", "carte_funciara": "CF123",
            "evaluator_nume": "Maria", "evaluator_legitimatie": "1",
            "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16",
        },
        "land": {"suprafata": "500"},
        "building": {
            "au": "100", "acd": "120", "an_referinta": 2025,
            "elements": [{"element": "S", "cod": "X", "um": "mp",
                          "cantitate": "120", "cost_unitar": "2000", "an_pif": 2015}],
            "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                    {"varsta": 15, "depreciere": "0.15"}],
        },
        "valoare_teren": "100000",
        "metoda": "cost",
    }


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    app = create_app(storage=storage, client=None)
    return TestClient(app)


def test_post_evaluare_returns_id_and_value(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/evaluare", json=_payload())
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["metoda"] == "cost"
    assert Decimal(data["valoare_finala"]) > 0


def test_get_evaluare_returns_summary(tmp_path):
    client = _client(tmp_path)
    eid = client.post("/api/evaluare", json=_payload()).json()["id"]
    resp = client.get(f"/api/evaluare/{eid}")
    assert resp.status_code == 200
    assert resp.json()["client_nume"] == "Ion Popescu"


def test_download_raport_docx(tmp_path):
    client = _client(tmp_path)
    eid = client.post("/api/evaluare", json=_payload()).json()["id"]
    resp = client.get(f"/api/evaluare/{eid}/raport.docx")
    assert resp.status_code == 200
    ct = resp.headers["content-type"]
    assert "officedocument.wordprocessingml.document" in ct
    # un .docx este un fisier zip -> incepe cu "PK"
    assert resp.content[:2] == b"PK"


def test_get_missing_evaluare_404(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/api/evaluare/9999")
    assert resp.status_code == 404


def test_evaluare_returneaza_alerte(tmp_path):
    client = _client(tmp_path)
    data = client.post("/api/evaluare", json=_payload()).json()
    assert "alerte" in data
    assert isinstance(data["alerte"], list)
