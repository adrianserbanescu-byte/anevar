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


# ── Robustețe import portaluri (audit imobiliare/storia/olx) ─────────────────
_PAGINA_LISTA = """<html><head>
  <title>Apartamente de vânzare | Storia.ro</title>
  <meta property="og:title" content="Apartamente de vânzare | Storia.ro">
  <meta property="og:description" content="Vezi 84602 anunțuri de apartamente de vânzare în toată România.">
  </head><body><div>650.000 EUR · 121 mp</div></body></html>"""


def test_pagina_de_lista_e_semnalata_nu_extrage_tacut():
    # Un URL trunchiat/expirat ajunge pe o pagină de rezultate; NU trebuie să producă
    # tacit un comparabil (prețul unui anunț promovat nelegat de subiect).
    parsed = parse_listing_html(_PAGINA_LISTA, sursa_url="https://storia.ro/lista")
    assert parsed.pagina_lista is True
    with pytest.raises(ValueError, match="listă|lista|căutare"):
        to_comparable(parsed)


def test_anunt_real_nu_e_marcat_ca_lista():
    parsed = parse_listing_html(_html("imobiliare_listing.html"))
    assert parsed.pagina_lista is False


def test_mp_teren_in_titlu_nu_e_confundat_cu_suprafata_casei():
    # OLX: „Casă cu 2000mp Teren" — 2000 mp e TERENUL, nu suprafața casei.
    html = ('<html><head><title>Casă cu 2000mp Teren Gura Văii</title>'
            '<meta property="og:description" content="Casă de vânzare cu 2000 mp teren, preț 55000 EUR">'
            '</head><body></body></html>')
    parsed = parse_listing_html(html)
    assert parsed.suprafata is None                 # nu confundă terenul cu casa
    assert parsed.suprafata_teren == Decimal("2000")


def test_mp_casa_in_titlu_inca_se_extrage():
    html = ('<html><head><title>Casă 120 mp în Breaza</title>'
            '<meta property="og:description" content="Casă individuală 120 mp, preț 100000 EUR">'
            '</head><body></body></html>')
    parsed = parse_listing_html(html)
    assert parsed.suprafata == Decimal("120")
