from pathlib import Path

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

FIXTURES = Path(__file__).parent / "fixtures"


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    html = (FIXTURES / "imobiliare_listing.html").read_text(encoding="utf-8")
    app = create_app(storage=storage, client=None, fetcher=lambda url: html)
    return TestClient(app)


def test_import_url_returns_parsed_fields(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/import-url", json={"url": "https://imobiliare.ro/x"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["pret"] == "250000"
    assert data["suprafata"] == "180"
    assert data["moneda"] == "EUR"


def test_import_url_empty_when_nothing_found(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    app = create_app(storage=storage, client=None,
                     fetcher=lambda url: "<html><body>nimic</body></html>")
    client = TestClient(app)
    resp = client.post("/api/import-url", json={"url": "https://x"})
    assert resp.status_code == 200
    assert resp.json()["pret"] is None
