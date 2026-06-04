"""Helperele JS comune (_helpers.js) sunt injectate o singura data in paginile care le folosesc."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path):
    s = Storage(tmp_path / "h.db")
    s.init()
    return TestClient(create_app(storage=s, client=None))


@pytest.mark.parametrize("ruta", ["/wizard", "/grila"])
def test_helpere_injectate_o_singura_data(client, ruta):
    html = client.get(ruta).text
    # helperele exista (injectate din _helpers.js)
    assert "function fmtRo" in html
    assert "document.getElementById(id)" in html
    # dar fara dubla declarare (const $ nu poate fi redeclarat -> ar rupe pagina)
    assert html.count("const $ = id => document.getElementById(id)") == 1
    assert html.count("function fmtRo") == 1
