from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_post_zona_fallback(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/zona", json={"adresa": "Str. X 10, Otopeni, Ilfov"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["judet"] == "ilfov"
    assert data["localitate"] == "otopeni"
