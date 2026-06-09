"""#7 coverage (cod nou): cauta_anunturi_multi (multi-localitate prin virgula) + filtrul STRICT
pe fallback-ul de judet (extract_listing_urls strict=True -> [] cand nicio localitate nu se potriveste)."""
from evaluare.discovery.portal_search import (
    BAZE,
    cauta_anunturi,
    cauta_anunturi_multi,
    extract_listing_urls,
)


def test_extract_strict_taie_leak_judet():
    html = '<a href="/oferta/casa-pipera-9">x</a>'              # anunt din ALTA localitate
    # prefer „otopeni", nimic nu se potriveste:
    assert extract_listing_urls(html, BAZE["imobiliare"], prefer="otopeni", strict=True) == []
    nonstrict = extract_listing_urls(html, BAZE["imobiliare"], prefer="otopeni", strict=False)
    assert len(nonstrict) == 1                                  # localitate -> toate (mai bine ceva)


def test_cauta_anunturi_multi_combina_doua_localitati():
    def fetcher(url):
        if "otopeni" in url:
            return '<a href="/oferta/casa-otopeni-1">a</a><a href="/oferta/casa-otopeni-2">b</a>'
        if "buftea" in url:
            return '<a href="/oferta/casa-buftea-1">c</a>'
        return ""                                              # pagina de judet (fallback) goala
    urls = cauta_anunturi_multi("imobiliare", "ilfov", "otopeni, buftea", fetcher=fetcher)
    assert len(urls) == 3
    assert sum("otopeni" in u for u in urls) == 2 and any("buftea-1" in u for u in urls)


def test_cauta_anunturi_multi_dedup_aceeasi_localitate():
    def fetcher(url):
        return '<a href="/oferta/casa-otopeni-1">a</a>' if "otopeni" in url else ""
    # aceeasi localitate de 2 ori -> dedup -> un singur URL
    assert cauta_anunturi_multi("imobiliare", "ilfov", "otopeni, otopeni", fetcher=fetcher) == \
        ["https://www.imobiliare.ro/oferta/casa-otopeni-1"]


def test_cauta_anunturi_multi_o_localitate_delegheaza():
    def fetcher(url):
        return '<a href="/oferta/casa-otopeni-1">a</a>' if "otopeni" in url else ""
    # 0/1 localitate -> identic cu cauta_anunturi
    assert cauta_anunturi_multi("imobiliare", "ilfov", "otopeni", fetcher=fetcher) == \
        cauta_anunturi("imobiliare", "ilfov", "otopeni", fetcher=fetcher)
