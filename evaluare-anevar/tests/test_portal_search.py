from pathlib import Path

from evaluare.discovery.portal_search import (
    build_search_url,
    cauta_anunturi,
    cauta_anunturi_multi,
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


def test_extract_listing_urls_prefera_localitatea_taie_promovate():
    # un anunț promovat din altă localitate (Pipera) afișat pe căutarea Breaza
    html = ('<a href="/oferta/casa-breaza-1">x</a>'
            '<a href="/oferta/duplex-pipera-promovat-2">y</a>'
            '<a href="/oferta/vila-breaza-3">z</a>')
    urls = extract_listing_urls(html, baza="https://www.imobiliare.ro", prefer="breaza")
    assert len(urls) == 2 and all("breaza" in u for u in urls)


def test_extract_listing_urls_prefer_fara_potrivire_intoarce_toate():
    html = '<a href="/oferta/casa-sinaia-1">x</a><a href="/oferta/vila-azuga-2">y</a>'
    urls = extract_listing_urls(html, baza="https://www.imobiliare.ro", prefer="breaza")
    assert len(urls) == 2                       # niciuna nu se potrivește -> toate


def test_cauta_anunturi_uses_injected_fetcher():
    html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    urls = cauta_anunturi("imobiliare", judet="ilfov", localitate="otopeni",
                          fetcher=lambda u: html)
    assert len(urls) == 3


def test_cauta_anunturi_judet_fallback_filtreaza_strict_pe_localitate():
    # localitatea da 404 -> cade pe pagina judetului, DAR ia doar anunturile din localitate (nu tot judetul)
    judet_html = ('<a href="/oferta/casa-cluj-napoca-1">x</a>'
                  '<a href="/oferta/vila-floresti-2">y</a>'          # alta localitate -> taiat
                  '<a href="/oferta/duplex-cluj-napoca-3">z</a>')

    def fetcher(u):
        if u.rstrip("/").endswith("/cluj-napoca"):
            raise RuntimeError("404")          # localitatea n-are pagina proprie
        return judet_html                       # pagina judetului

    urls = cauta_anunturi("storia", judet="cluj", localitate="cluj-napoca", fetcher=fetcher)
    assert len(urls) == 2 and all("cluj-napoca" in u for u in urls)   # floresti taiat (fara leak)


def test_cauta_anunturi_judet_fallback_fara_match_empty():
    # localitatea 404 + niciun anunt din localitate pe pagina judetului -> [] (NU tot judetul = bugul Adi)
    judet_html = '<a href="/oferta/casa-floresti-1">x</a><a href="/oferta/vila-turda-2">y</a>'

    def fetcher(u):
        if u.rstrip("/").endswith("/cluj-napoca"):
            raise RuntimeError("404")
        return judet_html

    urls = cauta_anunturi("storia", judet="cluj", localitate="cluj-napoca", fetcher=fetcher)
    assert urls == []          # fara leak pe tot judetul


def test_cauta_anunturi_pe_judet_explicit_intoarce_tot():
    # fara localitate (cautare pe judet ceruta EXPLICIT) -> toate anunturile, fara filtru
    html = '<a href="/oferta/casa-a-1">x</a><a href="/oferta/vila-b-2">y</a>'
    urls = cauta_anunturi("storia", judet="cluj", localitate="", fetcher=lambda u: html)
    assert len(urls) == 2


def test_cauta_anunturi_multi_combina_localitati_vecine():
    # userul adauga localitati vecine (separate prin virgula) -> rezultate combinate, dedup
    paginile = {
        "/otopeni": '<a href="/oferta/casa-otopeni-1">a</a>',
        "/tunari": '<a href="/oferta/casa-tunari-2">b</a><a href="/oferta/casa-otopeni-1">a</a>',
    }

    def fetcher(u):
        for sufix, html in paginile.items():
            if u.rstrip("/").endswith(sufix):
                return html
        return ""              # pagina de judet -> goala

    urls = cauta_anunturi_multi("imobiliare", judet="ilfov", localitati="otopeni, tunari",
                                fetcher=fetcher)
    assert len(urls) == 2                                  # otopeni-1 + tunari-2 (dedup otopeni-1)
    assert any("otopeni-1" in u for u in urls) and any("tunari-2" in u for u in urls)
