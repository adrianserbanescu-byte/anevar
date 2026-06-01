from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_index_is_wizard(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    # pagina principala este acum wizard-ul
    assert 'id="pas-1"' in resp.text
    assert "pas cu pas" in resp.text


def test_formular_monolit_la_ruta_noua(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/formular")
    assert resp.status_code == 200
    assert "<form" in resp.text
    assert 'name="metoda"' in resp.text          # selector de metoda
    assert "Import din URL" in resp.text          # buton import
    assert 'name="comparabile"' in resp.text      # sectiune comparabile


def test_result_page_loads(tmp_path):
    client = _client(tmp_path)
    payload = {
        "meta": {"client_nume": "Ion Popescu", "adresa": "Str. 1",
                 "numar_cadastral": "123", "carte_funciara": "CF123",
                 "evaluator_nume": "Maria", "evaluator_legitimatie": "1",
                 "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16"},
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp",
                                   "cantitate": "120", "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"},
                                             {"varsta": 15, "depreciere": "0.15"}]},
        "valoare_teren": "100000", "metoda": "cost",
    }
    eid = client.post("/api/evaluare", json=payload).json()["id"]
    resp = client.get(f"/evaluare/{eid}")
    assert resp.status_code == 200
    assert "Ion Popescu" in resp.text
    assert "raport.docx" in resp.text   # link de descarcare
