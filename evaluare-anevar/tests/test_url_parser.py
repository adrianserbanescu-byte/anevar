from decimal import Decimal
from pathlib import Path

import pytest

from evaluare.importers.url_parser import (
    ParsedListing,
    import_from_url,
    parse_listing_html,
    to_comparable,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_imobiliare_extracts_price_and_surface():
    parsed = parse_listing_html(_html("imobiliare_listing.html"),
                                sursa_url="https://imobiliare.ro/x")
    assert parsed.pret == Decimal("250000")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("180")
    assert parsed.sursa_url == "https://imobiliare.ro/x"


def test_parse_storia_handles_graph():
    parsed = parse_listing_html(_html("storia_listing.html"),
                                sursa_url="https://storia.ro/y")
    assert parsed.pret == Decimal("1350000")
    assert parsed.moneda == "RON"
    assert parsed.suprafata == Decimal("220")


def test_parse_returns_none_fields_when_absent():
    parsed = parse_listing_html("<html><body>nimic</body></html>")
    assert parsed.pret is None
    assert parsed.suprafata is None


def test_to_comparable_builds_from_parsed():
    parsed = ParsedListing(pret=Decimal("250000"), moneda="EUR",
                           suprafata=Decimal("180"), titlu="Casa",
                           sursa_url="https://imobiliare.ro/x")
    comp = to_comparable(parsed)
    assert comp.pret == Decimal("250000")
    assert comp.suprafata == Decimal("180")
    assert comp.sursa == "https://imobiliare.ro/x"
    assert comp.tip_oferta == "oferta"


def test_to_comparable_requires_price_and_surface():
    parsed = ParsedListing(pret=None, moneda=None, suprafata=Decimal("180"),
                           titlu="", sursa_url="")
    with pytest.raises(ValueError):
        to_comparable(parsed)


def test_import_from_url_uses_injected_fetcher():
    html = _html("imobiliare_listing.html")
    parsed = import_from_url("https://imobiliare.ro/x", fetcher=lambda url: html)
    assert parsed.pret == Decimal("250000")
    assert parsed.suprafata == Decimal("180")
