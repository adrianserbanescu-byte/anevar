from decimal import Decimal

import pytest

import evaluare.curs_bnr as cb
from evaluare.curs_bnr import curs_bnr

_XML = ('<?xml version="1.0"?><DataSet xmlns="http://www.bnr.ro/xsd"><Body>'
        '<Cube date="2026-06-03">'
        '<Rate currency="EUR">5.2592</Rate>'
        '<Rate currency="USD">4.6100</Rate>'
        '<Rate currency="HUF" multiplier="100">1.3200</Rate>'
        '</Cube></Body></DataSet>')


@pytest.fixture(autouse=True)
def _curs_cache_curat():
    """Izoleaza cache-ul feed-ului BNR intre teste."""
    cb._goleste_cache()
    yield
    cb._goleste_cache()


def test_curs_bnr_eur():
    r = curs_bnr("EUR", fetcher=lambda u: _XML)
    assert r["curs"] == Decimal("5.2592")
    assert r["data"] == "2026-06-03"
    assert r["moneda"] == "EUR"


def test_curs_bnr_multiplicator_huf():
    r = curs_bnr("HUF", fetcher=lambda u: _XML)
    assert r["curs"] == Decimal("0.013200")   # 1.32 / 100


def test_curs_bnr_valuta_inexistenta():
    assert curs_bnr("XXX", fetcher=lambda u: _XML) is None


# --- PERF-3: cache TTL pe calea de retea reala -------------------------------------------------

def test_curs_bnr_cacheaza_calea_reala(monkeypatch):
    # fetcher implicit (None) -> calea de retea reala e cacheata: o singura descarcare pentru
    # doua apeluri, chiar si pe valute diferite (acelasi feed XML serveste toate valutele).
    apeluri = {"n": 0}

    def fals_fetch(url):
        apeluri["n"] += 1
        return _XML

    monkeypatch.setattr(cb, "_fetch", fals_fetch)
    r1 = curs_bnr("EUR")
    r2 = curs_bnr("HUF")
    assert r1["curs"] == Decimal("5.2592")
    assert r2["curs"] == Decimal("0.013200")
    assert apeluri["n"] == 1   # a doua valuta vine din cache, fara re-descarcare


def test_curs_bnr_cache_expira_dupa_ttl(monkeypatch):
    # dupa expirarea TTL-ului, feed-ul se re-descarca.
    apeluri = {"n": 0}

    def fals_fetch(url):
        apeluri["n"] += 1
        return _XML

    ceas = {"t": 1000.0}
    monkeypatch.setattr(cb, "_fetch", fals_fetch)
    monkeypatch.setattr(cb.time, "monotonic", lambda: ceas["t"])
    curs_bnr("EUR")
    assert apeluri["n"] == 1
    ceas["t"] += cb._TTL_CURS_SEC + 1   # depaseste TTL-ul
    curs_bnr("EUR")
    assert apeluri["n"] == 2


def test_curs_bnr_goleste_cache(monkeypatch):
    apeluri = {"n": 0}

    def fals_fetch(url):
        apeluri["n"] += 1
        return _XML

    monkeypatch.setattr(cb, "_fetch", fals_fetch)
    curs_bnr("EUR")
    cb._goleste_cache()
    curs_bnr("EUR")
    assert apeluri["n"] == 2   # dupa golire, se re-descarca


def test_curs_bnr_fetcher_injectat_ocoleste_cache():
    # un fetcher injectat NU populeaza si nu citeste cache-ul: fiecare apel il foloseste.
    apeluri = {"n": 0}

    def fetcher(_url):
        apeluri["n"] += 1
        return _XML

    curs_bnr("EUR", fetcher=fetcher)
    curs_bnr("EUR", fetcher=fetcher)
    assert apeluri["n"] == 2
