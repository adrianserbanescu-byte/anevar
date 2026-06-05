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


_HTML_ANUNT = ('<html><head><script type="application/ld+json">'
               '{"@type":"Offer","price":"150000","priceCurrency":"EUR",'
               '"floorSize":{"value":"120"}}</script></head><body>casă</body></html>')


def test_coada_import_aduna_si_deduplica(client):
    # gol la inceput
    assert client.get("/api/anunturi-importate").json()["anunturi"] == []
    # un anunt cu pret+suprafata -> intra in coada
    r = client.post("/api/import-anunt", json={"html": _HTML_ANUNT, "url": "https://x.ro/1"})
    assert r.json()["in_coada"] == 1
    # acelasi URL -> nu se dubleaza
    client.post("/api/import-anunt", json={"html": _HTML_ANUNT, "url": "https://x.ro/1"})
    assert len(client.get("/api/anunturi-importate").json()["anunturi"]) == 1
    # alt URL -> se adauga
    client.post("/api/import-anunt", json={"html": _HTML_ANUNT, "url": "https://x.ro/2"})
    lista = client.get("/api/anunturi-importate").json()["anunturi"]
    assert len(lista) == 2
    assert lista[0]["pret"] == "150000" and lista[0]["suprafata"] == "120"


def test_coada_import_ignora_anunt_fara_pret_si_se_goleste(client):
    # pagina fara pret/suprafata -> nu intra in coada
    client.post("/api/import-anunt", json={"html": "<html><body>nimic</body></html>", "url": "https://x.ro/gol"})
    assert client.get("/api/anunturi-importate").json()["anunturi"] == []
    # adauga unul valid, apoi goleste
    client.post("/api/import-anunt", json={"html": _HTML_ANUNT, "url": "https://x.ro/3"})
    assert len(client.get("/api/anunturi-importate").json()["anunturi"]) == 1
    r = client.post("/api/anunturi-importate/sterge")
    assert r.json()["anunturi"] == []
    assert client.get("/api/anunturi-importate").json()["anunturi"] == []
