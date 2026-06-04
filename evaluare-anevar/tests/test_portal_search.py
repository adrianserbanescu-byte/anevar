from pathlib import Path

from evaluare.discovery.portal_search import (
    build_search_url,
    cauta_anunturi,
    extract_listing_urls,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_search_url_imobiliare():
    url = build_search_url("imobiliare", judet="ilfov", localitate="otopeni")
    assert "imobiliare.ro" in url
    assert "ilfov" in url and "otopeni" in url


def test_extract_listing_urls_keeps_only_oferta_pages():
    html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    urls = extract_listing_urls(html, baza="https://www.imobiliare.ro")
    # doar cele 3 /oferta/, absolutizate, fara paginare/agentii
    assert len(urls) == 3
    assert all("/oferta/" in u for u in urls)
    assert all(u.startswith("https://www.imobiliare.ro/oferta/") for u in urls)


def test_build_search_url_judet_only():
    url = build_search_url("storia", judet="cluj")
    assert url.endswith("/casa/cluj")
    assert "/casa/cluj/" not in url


def test_cauta_anunturi_uses_injected_fetcher():
    html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    urls = cauta_anunturi("imobiliare", judet="ilfov", localitate="otopeni",
                          fetcher=lambda u: html)
    assert len(urls) == 3


def test_cauta_anunturi_cade_pe_judet_la_404_localitate():
    html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")

    def fetcher(u):
        # localitatea da 404; judetul (fara localitate) merge
        if u.rstrip("/").endswith("/cluj-napoca"):
            raise RuntimeError("404")
        return html

    urls = cauta_anunturi("storia", judet="cluj", localitate="cluj-napoca", fetcher=fetcher)
    assert len(urls) == 3
