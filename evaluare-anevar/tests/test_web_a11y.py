"""Verificari de accesibilitate (WCAG 2.1 AA) pe paginile aplicatiei — regresie pe atribute cheie."""
import pytest
from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app


@pytest.fixture
def client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None))


@pytest.mark.parametrize("ruta", ["/wizard", "/aml", "/grila", "/descoperire"])
def test_pagina_are_landmark_main(client, ruta):
    html = client.get(ruta).text
    assert "<main" in html and "</main>" in html


@pytest.mark.parametrize("ruta", ["/wizard", "/aml", "/grila"])
def test_pagina_are_nav_landmark(client, ruta):
    assert "<nav" in client.get(ruta).text


def test_wizard_labels_asociate_si_stepper(client):
    html = client.get("/wizard").text
    assert 'for="judet"' in html and 'for="client_nume"' in html
    # stepper numerotat clickabil (a inlocuit bara de progres)
    assert 'class="stepper"' in html
    assert 'data-pas="1"' in html and 'data-pas="5"' in html
    assert "Comparabile" in html and "Raport" in html   # etichetele pasilor
    assert 'role="status"' in html          # mesaje de stare anuntate


def test_aml_labels_asociate(client):
    html = client.get("/aml").text
    assert 'for="tip_entitate"' in html and 'for="nume"' in html
    assert 'aria-live="polite"' in html


def test_grila_labels_si_helper(client):
    html = client.get("/grila").text
    assert 'for="supr-teren"' in html and 'for="t-judet"' in html
    assert "const $ = id => document.getElementById(id);" in html   # bug-fix helper
    assert 'scope="col"' in html


def test_descoperire_labels(client):
    html = client.get("/descoperire").text
    assert 'for="judet"' in html and 'for="incalzire"' in html
    assert 'role="status"' in html


@pytest.mark.parametrize("ruta", ["/wizard", "/aml", "/grila", "/descoperire"])
def test_pagina_are_skip_link(client, ruta):
    html = client.get(ruta).text
    assert 'class="skip-link"' in html
    assert 'id="continut"' in html


def test_wizard_date_inputs_au_type_date(client):
    html = client.get("/wizard").text
    assert 'id="data_evaluarii"' in html
    # campul de data foloseste type="date"
    import re
    assert re.search(r'<input[^>]*id="data_evaluarii"[^>]*type="date"', html) or \
           re.search(r'<input[^>]*type="date"[^>]*id="data_evaluarii"', html)
    assert 'autocomplete="name"' in html
