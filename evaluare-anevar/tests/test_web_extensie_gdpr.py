"""Endpointuri noi: documente GDPR + import-anunt (pregătit pentru extensia de browser)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path):
    s = Storage(tmp_path / "e.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


def test_gdpr_politica_si_consimtamant_se_genereaza(client):
    for url in ("/api/gdpr/politica.docx", "/api/gdpr/consimtamant.docx"):
        r = client.post(url, json={})
        assert r.status_code == 200
        assert "wordprocessingml" in r.headers["content-type"]
        assert len(r.content) > 1000  # docx real


def test_import_anunt_extrage_si_avertizeaza_oferta(client):
    html = "<html><body><h1>Casă de vânzare</h1><div>120.000 EUR · 100 mp</div></body></html>"
    r = client.post("/api/import-anunt", json={"html": html, "url": "https://exemplu.ro/anunt"})
    assert r.status_code == 200
    d = r.json()
    assert "_nota" in d and "ofert" in d["_nota"].lower()
    assert d["sursa_url"] == "https://exemplu.ro/anunt"
