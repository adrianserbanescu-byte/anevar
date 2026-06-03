from decimal import Decimal

from evaluare.curs_bnr import curs_bnr

_XML = ('<?xml version="1.0"?><DataSet xmlns="http://www.bnr.ro/xsd"><Body>'
        '<Cube date="2026-06-03">'
        '<Rate currency="EUR">5.2592</Rate>'
        '<Rate currency="USD">4.6100</Rate>'
        '<Rate currency="HUF" multiplier="100">1.3200</Rate>'
        '</Cube></Body></DataSet>')


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
