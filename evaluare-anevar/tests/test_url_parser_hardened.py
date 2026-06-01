from decimal import Decimal
from pathlib import Path

from evaluare.importers.url_parser import parse_listing_html

FIXTURES = Path(__file__).parent / "fixtures"


def test_extracts_from_nextdata_and_title():
    html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://imobiliare.ro/oferta/x")
    assert parsed.pret == Decimal("249900")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("130")


def test_jsonld_still_works():
    html = (FIXTURES / "imobiliare_listing.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://imobiliare.ro/x")
    assert parsed.pret == Decimal("250000")
    assert parsed.suprafata == Decimal("180")


def test_extracts_from_real_imobiliare_structure():
    # structura reala imobiliare.ro: @graph cu Offer.priceSpecification.price si floorSize scalar
    html = (FIXTURES / "imobiliare_listing_real.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://imobiliare.ro/oferta/x")
    assert parsed.pret == Decimal("2000000")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("400")    # floorSize scalar = suprafata casei


def test_extracts_storia_area_not_terrain():
    # storia.ro: __NEXT_DATA__ cu caracteristica "area" (casa) si "terrain_area" (teren)
    html = (FIXTURES / "storia_listing_nextdata.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://storia.ro/ro/oferta/x")
    assert parsed.pret == Decimal("385000")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("220")    # "area" (casa), NU "terrain_area" (500)


def test_title_regex_fallback_for_surface():
    html = "<html><head><title>Vila 220 mp Pipera 500000 EUR</title></head><body></body></html>"
    parsed = parse_listing_html(html)
    assert parsed.suprafata == Decimal("220")
    assert parsed.pret == Decimal("500000")
