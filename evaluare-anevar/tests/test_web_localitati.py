from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_get_localitati(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/api/localitati")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["judete"]) == 42
    assert any(j["slug"] == "ilfov" for j in data["judete"])
    assert any(loc["slug"] == "otopeni" for loc in data["localitati"]["ilfov"])
