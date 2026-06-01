from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


def test_wizard_page_loads_with_5_steps(tmp_path):
    client = _client(tmp_path)
    resp = client.get("/wizard")
    assert resp.status_code == 200
    body = resp.text
    for i in range(1, 6):
        assert f'id="pas-{i}"' in body
    # referinta catre endpoint-urile reutilizate
    assert "/api/zona" in body
    assert "/api/descopera" in body
    assert "/api/evaluare" in body
    assert "localStorage" in body
