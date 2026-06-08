"""P1.1 — Imoradar24 ca portal de descoperire (acoperire noua).

Imoradar24 are slug curat (/{cat}-de-vanzare/judetul-{j}/{localitate}) + anunturi /oferta/...;
paginile sunt self-hosted, deci parserul generic (JSON-LD + og:meta) extrage pret/supr/poza.
Astfel integrarea = doar segment de search; parserul existent face restul."""
from decimal import Decimal
from pathlib import Path

import pytest

from evaluare.discovery.portal_search import (
    BAZE,
    build_search_url,
    cauta_anunturi,
    extract_listing_urls,
)
from evaluare.importers.url_parser import parse_listing_html

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_search_url_imoradar_casa_si_teren():
    assert (build_search_url("imoradar", "Ilfov", "Otopeni", "casa")
            == "https://www.imoradar24.ro/case-de-vanzare/judetul-ilfov/otopeni")
    assert (build_search_url("imoradar", "ilfov", "", "teren")
            == "https://www.imoradar24.ro/terenuri-de-vanzare/judetul-ilfov")


def test_build_search_url_slugify_diacritice_si_spatii():
    # diacriticele se pliaza la ASCII; altfel portalul da 404 -> zero comparabile (toate portalurile)
    assert (build_search_url("imoradar", "Bistrița-Năsăud", "Năsăud", "casa")
            == "https://www.imoradar24.ro/case-de-vanzare/judetul-bistrita-nasaud/nasaud")
    # spatii in localitate -> '-'
    assert (build_search_url("imobiliare", "Cluj", "Florești Centru", "casa")
            == "https://www.imobiliare.ro/vanzare-case-vile/judetul-cluj/floresti-centru")


def test_build_search_url_portal_si_categorie_necunoscute_raises():
    with pytest.raises(ValueError):
        build_search_url("portal-inexistent", "ilfov", "", "casa")
    with pytest.raises(ValueError):       # apartament nu e segment de search (doar casa/teren)
        build_search_url("imoradar", "ilfov", "", "apartament")


def test_extract_listing_urls_imoradar_oferta_si_prefer():
    html = (FIXTURES / "imoradar_search.html").read_text(encoding="utf-8")
    toate = extract_listing_urls(html, baza=BAZE["imoradar"])
    assert len(toate) >= 3 and all("/oferta/" in u for u in toate)
    assert all(u.startswith("https://www.imoradar24.ro/oferta/") for u in toate)
    # prefer = localitate -> taie promovatele din alta zona (Pipera), pastreaza Otopeni
    otopeni = extract_listing_urls(html, baza=BAZE["imoradar"], prefer="otopeni")
    assert otopeni and all("otopeni" in u.lower() for u in otopeni)
    assert not any("pipera" in u.lower() for u in otopeni)


def test_parse_imoradar_listing_extrage_pret_supr_poza():
    html = (FIXTURES / "imoradar_listing.html").read_text(encoding="utf-8")
    p = parse_listing_html(html, sursa_url="https://www.imoradar24.ro/oferta/casa-otopeni-1699081")
    assert p.pret == Decimal("319000") and p.moneda == "EUR"
    assert p.suprafata == Decimal("173")
    assert p.poza and p.poza.endswith(".jpg")
    assert p.pagina_lista is False


def test_cauta_anunturi_imoradar_cu_fetcher_injectat():
    search = (FIXTURES / "imoradar_search.html").read_text(encoding="utf-8")

    def fetcher(url):
        return search

    urls = cauta_anunturi("imoradar", "ilfov", "otopeni", fetcher=fetcher)
    assert urls and all("/oferta/" in u for u in urls)
    assert all("otopeni" in u.lower() for u in urls)   # prefer localitate filtreaza promovatele
