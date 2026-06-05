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


def test_extracts_olx_jsonld_si_suprafata_din_descriere():
    # olx.ro: JSON-LD Product/Offer (pret) + suprafata din textul paginii (regex "mp")
    html = (FIXTURES / "olx_listing.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://www.olx.ro/d/oferta/casa-x")
    assert parsed.pret == Decimal("165000")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("120")          # "Suprafață utilă: 120 mp"
    assert parsed.suprafata_teren == Decimal("350")    # "Suprafață teren: 350 mp"


def test_extracts_storia_area_not_terrain():
    # storia.ro: __NEXT_DATA__ cu caracteristica "area" (casa) si "terrain_area" (teren)
    html = (FIXTURES / "storia_listing_nextdata.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://storia.ro/ro/oferta/x")
    assert parsed.pret == Decimal("385000")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("220")          # "area" (casa), NU "terrain_area"
    assert parsed.suprafata_teren == Decimal("500")    # "terrain_area" = teren


def test_title_regex_fallback_for_surface():
    html = "<html><head><title>Vila 220 mp Pipera 500000 EUR</title></head><body></body></html>"
    parsed = parse_listing_html(html)
    assert parsed.suprafata == Decimal("220")
    assert parsed.pret == Decimal("500000")


def test_extrage_teren_imobiliare_format_romanesc():
    # imobiliare: terenul e in text "Sup. teren: 1.910 mp" (punctul = separator de mii)
    html = '<html><body><div>Sup. utila: 149 mp Sup. teren: 1.910 mp Tip prop.: Individuala</div></body></html>'
    p = parse_listing_html(html)
    assert p.suprafata_teren == Decimal("1910")


def test_to_decimal_ro_format_romanesc():
    from evaluare.importers.url_parser import _to_decimal_ro
    assert _to_decimal_ro("1.910") == Decimal("1910")
    assert _to_decimal_ro("351,46") == Decimal("351.46")
    assert _to_decimal_ro("149") == Decimal("149")


def test_extrage_caracteristici_structurate_storia():
    # storia.ro: dict `target` din __NEXT_DATA__ contine an, incalzire, material etc.
    html = (FIXTURES / "storia_caracteristici.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://storia.ro/ro/oferta/x")
    assert parsed.an == 2010
    assert parsed.incalzire == "centrala_gaz"
    assert parsed.material == "lemn"
    assert parsed.tip_cladire == "casa individuala"
    assert parsed.stare_text == "buna / locuibila"
    assert parsed.nr_camere == 5
    assert parsed.etaje == "un nivel"
    assert parsed.suprafata == Decimal("220")
    assert parsed.suprafata_teren == Decimal("700")


def test_caracteristici_structurate_imobiliare_din_body():
    # imobiliare e server-side: campurile apar ca text 'Eticheta: valoare' in body
    html = ("<html><head><title>Casa Breaza</title></head><body>"
            "<span>An construcție: 1996 (Finalizată)</span>"
            "<span>Structură rezistență: BCA</span>"
            "<span>Regim înălțime: D+P+1E</span>"
            "<p>Incalzire centrala termica pe gaz.</p></body></html>")
    parsed = parse_listing_html(html, sursa_url="https://imobiliare.ro/oferta/x")
    assert parsed.an == 1996
    assert parsed.material == "bca"
    assert parsed.etaje == "D+P+1E"
    assert parsed.incalzire == "centrala_gaz"
