"""Cod poștal din adresă via Poșta Română (Lot A1) — modul `cod_postal` + endpoint GET /api/cod-postal.

Rețeaua e MOCK-uită integral (fără apeluri reale): la nivel de unit injectăm un `session` fals cu
`.post`; la nivel de endpoint monkeypatch-uim `cauta_cod_postal`. Acoperă: happy-path, alegerea pe
interval de numere, ambiguitate, „not found", timeout/eroare rețea, JSON invalid, cache, robustețea
endpointului (niciodată 500).
"""
from __future__ import annotations

import json

import pytest
import requests
from fastapi.testclient import TestClient

import evaluare.cod_postal as cp
from evaluare.cod_postal import cauta_cod_postal
from evaluare.db.storage import Storage
from evaluare.web.app import create_app

# --- fixturi de răspuns (forma reală a serviciului: JSON cu `formular` = fragment HTML) -------------

def _rand(cod: str, judet: str, loc: str, strada: str) -> str:
    return (
        '<div class="col-md-12 cod-postal-line">'
        f'<div class="np"><p>{cod}</p></div>'
        f'<div class="np"><p>{judet}</p></div>'
        f'<div class="np"><p>{loc}</p></div>'
        f'<div class="np"><p>{strada}</p></div>'
        '<div class="np"><p><a href="#">Oficiu</a></p></div>'
        '</div>'
    )


def _formular_json(html: str, found: int = 1) -> str:
    return json.dumps({"formular": html, "found": found})


_NEGASIT = json.dumps({
    "formular": '<div class="cod-postal-line"><div class="np">'
                '<p>Căutarea nu a furnizat nici un rezultat!</p></div></div>',
    "found": 0,
})


class _FakeResp:
    def __init__(self, text: str, status: int = 200):
        self.text = text
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")

    def json(self):
        return json.loads(self.text)


class _FakeSession:
    """Sesiune falsă: `.post` întoarce un răspuns predefinit (sau ridică), și înregistrează apelurile."""

    def __init__(self, resp=None, exc: Exception | None = None):
        self._resp = resp
        self._exc = exc
        self.calls: list[dict] = []

    def post(self, url, data=None, headers=None, timeout=None):
        self.calls.append({"url": url, "data": data, "timeout": timeout})
        if self._exc is not None:
            raise self._exc
        return self._resp


@pytest.fixture(autouse=True)
def _curat_cache():
    cp._goleste_cache()
    yield
    cp._goleste_cache()


# --- unit: cauta_cod_postal ------------------------------------------------------------------------

def test_happy_path_un_singur_cod():
    html = _rand("515100", "Alba", "Abrud", "-")
    sess = _FakeSession(_FakeResp(_formular_json(html)))
    r = cauta_cod_postal("Alba", "Abrud", session=sess)
    assert r["cod"] == "515100"
    assert r["sursa"] == "posta-romana"
    assert r["ambiguu"] is False
    # contractul cererii: nume județ/localitate + lang ro, timeout scurt
    sent = sess.calls[0]
    assert sent["data"] == {"k_adresa": "", "k_judet": "Alba",
                            "k_localitate": "Abrud", "k_lang": "ro"}
    assert sent["timeout"] == cp._TIMEOUT


def test_alege_pe_interval_de_numere():
    # două coduri pe aceeași stradă; nr=90 cade în 85-93 -> al doilea cod, fără ambiguitate
    html = (_rand("510134", "Alba", "Alba Iulia", "Strada Calea Moților nr. 1-59; 2-68")
            + _rand("510079", "Alba", "Alba Iulia", "Strada Calea Moților nr. 85-93"))
    sess = _FakeSession(_FakeResp(_formular_json(html)))
    r = cauta_cod_postal("Alba", "Alba Iulia", "Moților", "90", session=sess)
    assert r["cod"] == "510079"
    assert r["ambiguu"] is False
    assert len(r["candidati"]) == 2


def test_ambiguu_cand_numarul_nu_se_potriveste():
    html = (_rand("510134", "Alba", "Alba Iulia", "Strada Calea Moților nr. 1-59")
            + _rand("510079", "Alba", "Alba Iulia", "Strada Calea Moților nr. 85-93"))
    sess = _FakeSession(_FakeResp(_formular_json(html)))
    r = cauta_cod_postal("Alba", "Alba Iulia", "Moților", "1000", session=sess)
    assert r["ambiguu"] is True
    assert r["cod"] == "510134"        # primul, ca fallback
    assert "mai multe coduri" in r["mesaj"].lower()


def test_not_found_intoarce_cod_none():
    sess = _FakeSession(_FakeResp(_NEGASIT))
    r = cauta_cod_postal("Alba", "Alba Iulia", "strada-inexistenta-xyz", session=sess)
    assert r["cod"] is None
    assert r["sursa"] == "posta-romana"
    assert r["candidati"] == []


def test_judet_sau_localitate_lipsa_nu_apeleaza_reteaua():
    sess = _FakeSession(_FakeResp(_formular_json(_rand("000000", "X", "Y", "-"))))
    r = cauta_cod_postal("", "Alba Iulia", session=sess)
    assert r["cod"] is None
    assert sess.calls == []            # zero apeluri de rețea


@pytest.mark.parametrize("exc", [
    requests.Timeout("timeout"),
    requests.ConnectionError("offline"),
    requests.HTTPError("500 server"),
])
def test_eroare_retea_degradeaza_gratios(exc):
    sess = _FakeSession(exc=exc)
    r = cauta_cod_postal("Alba", "Abrud", session=sess)
    assert r["cod"] is None
    assert "manual" in r["mesaj"].lower()


def test_json_invalid_degradeaza_gratios():
    sess = _FakeSession(_FakeResp("nu-e-json <html>"))
    r = cauta_cod_postal("Alba", "Abrud", session=sess)
    assert r["cod"] is None
    assert "manual" in r["mesaj"].lower()


def test_cache_evita_al_doilea_apel():
    html = _rand("515100", "Alba", "Abrud", "-")
    sess = _FakeSession(_FakeResp(_formular_json(html)))
    r1 = cauta_cod_postal("Alba", "Abrud", session=sess)
    r2 = cauta_cod_postal("Alba", "Abrud", session=sess)
    assert r1["cod"] == r2["cod"] == "515100"
    assert len(sess.calls) == 1        # al doilea lookup servit din cache


# --- endpoint: GET /api/cod-postal -----------------------------------------------------------------

def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    return TestClient(create_app(storage=storage, client=None, fetcher=lambda u: ""))


def test_endpoint_happy(tmp_path, monkeypatch):
    def fals(judet, localitate, strada="", nr=""):
        return {"cod": "510134", "sursa": "posta-romana", "mesaj": "ok",
                "ambiguu": False, "candidati": []}
    # patch pe simbolul importat în router (descoperire importă numele direct)
    monkeypatch.setattr("evaluare.web.routers.descoperire.cauta_cod_postal", fals)
    r = _client(tmp_path).get("/api/cod-postal",
                              params={"judet": "Alba", "localitate": "Alba Iulia",
                                      "strada": "Moților", "nr": "1"})
    assert r.status_code == 200
    assert r.json()["cod"] == "510134"


def test_endpoint_nu_da_500_la_exceptie(tmp_path, monkeypatch):
    def explodeaza(*a, **k):
        raise RuntimeError("ceva neașteptat")
    monkeypatch.setattr("evaluare.web.routers.descoperire.cauta_cod_postal", explodeaza)
    r = _client(tmp_path).get("/api/cod-postal",
                              params={"judet": "Alba", "localitate": "Alba Iulia"})
    assert r.status_code == 200        # NICIODATĂ 500 — câmpul rămâne manual
    body = r.json()
    assert body["cod"] is None
    assert "manual" in body["mesaj"].lower()


def test_endpoint_params_lipsa_nu_crapa(tmp_path):
    # fără județ/localitate -> 200 cu cod None (validare în modul, fără rețea)
    r = _client(tmp_path).get("/api/cod-postal")
    assert r.status_code == 200
    assert r.json()["cod"] is None
