import threading
import time
from decimal import Decimal
from pathlib import Path

from evaluare.discovery.orchestrator import (
    _MAX_CONCURENTA_DESCOPERIRE,
    descopera,
    descopera_teren,
    extrage_descriere,
)
from evaluare.discovery.profiles import SubjectProfile

FIXTURES = Path(__file__).parent / "fixtures"


def test_extrage_descriere_include_text():
    html = "<html><head><title>Casa</title></head><body><p>Finisaje de lux, 4 camere.</p></body></html>"
    txt = extrage_descriere(html)
    assert "Finisaje de lux" in txt


def test_extrage_descriere_din_nextdata_storia():
    # storia: descrierea bogata (cu specs) e in __NEXT_DATA__ ad.description, NU in body randat
    desc = ("Casa in Breaza, deschidere la strada 30 m. Suprafata utila 180 mp, amprenta la sol "
            "100 mp, desfasurata 220 mp. Regim inaltime P+2E+M. Pereti tip sandwich, fundatie beton, "
            "acoperis tabla. Incalzire centrala gaz Ariston. An constructie 2010.")
    html = ('<html><head><title>Casa Breaza</title></head><body>'
            '<p>chrome si footer fara specs</p>'
            f'<script id="__NEXT_DATA__" type="application/json">'
            f'{{"props":{{"pageProps":{{"ad":{{"description":"<p>{desc}</p>"}}}}}}}}</script>'
            '</body></html>')
    txt = extrage_descriere(html)
    assert "P+2E+M" in txt
    assert "sandwich" in txt
    assert "180 mp" in txt
    assert "footer fara specs" not in txt   # NU mai luam corpul randat sarac


def test_descopera_pipeline_complet():
    search_html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    listing_html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")

    def fetcher(url):
        if "/oferta/" in url:
            return listing_html
        return search_html

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},'
                    '"stare":{"treapta":4,"text":"renovat"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":400,"text":"400"},"secundare":[]}')

    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    rez = descopera("imobiliare", judet="ilfov", localitate="otopeni", subiect=subiect,
                    atribute_secundare=[], fetcher=fetcher, client=FakeClient(),
                    max_candidati=5)
    assert len(rez) == 3
    assert all(r.breakdown.relevanta > 0 for r in rez)
    relev = [r.breakdown.relevanta for r in rez]
    assert relev == sorted(relev, reverse=True)
    assert rez[0].pret == Decimal("249900")
    assert rez[0].suprafata == Decimal("130")
    assert rez[0].teren == Decimal("400")   # terenul e propagat in rezultat (afisare)


def test_descopera_declaseaza_anunt_fara_suprafata():
    # OLX-style: preț prezent, suprafață lipsă → scor declasat + notă „completează manual"
    search = '<html><body><a href="/oferta/casa-fara-metraj-1">x</a></body></html>'
    listing = ('<html><head><title>Casă de vânzare Breaza</title>'
               '<script type="application/ld+json">'
               '{"@type":"Offer","price":"120000","priceCurrency":"EUR"}</script>'
               '</head><body>casă frumoasă, fără metraj indicat</body></html>')

    def fetcher(url):
        return listing if "/oferta/" in url else search

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},"stare":{"treapta":3,"text":"ok"},'
                    '"finisaj":{"treapta":3,"text":"ok"},"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":null,"text":""},"secundare":[]}')

    subiect = SubjectProfile(an=2010, stare=3, finisaj=3, incalzire="centrala_gaz")
    rez = descopera("imobiliare", judet="prahova", localitate="breaza", subiect=subiect,
                    atribute_secundare=[], fetcher=fetcher, client=FakeClient(), max_candidati=3)
    assert len(rez) == 1
    assert rez[0].suprafata is None
    assert "Suprafață lipsă" in rez[0].breakdown.explicatie    # marcat pentru completare manuală


def test_build_search_url_teren():
    from evaluare.discovery.portal_search import build_search_url
    u = build_search_url("imobiliare", "Prahova", "Breaza", categorie="teren")
    assert "vanzare-terenuri/judetul-prahova/breaza" in u
    s = build_search_url("storia", "Prahova", "", categorie="teren")
    assert "rezultate/vanzare/teren/prahova" in s


def test_descopera_teren_pipeline():
    from decimal import Decimal

    from evaluare.discovery.orchestrator import descopera_teren
    search = '<html><body><a href="/oferta/teren-breaza-1">t1</a></body></html>'
    listing = ('<html><head><title>Teren Breaza 1000 mp</title>'
               '<script type="application/ld+json">'
               '{"@type":"Offer","price":"50000","priceCurrency":"EUR",'
               '"floorSize":{"value":"1000"}}</script></head><body>x</body></html>')

    def fetcher(url):
        return listing if "/oferta/" in url else search

    rez = descopera_teren("imobiliare", "prahova", "breaza",
                          suprafata_subiect=Decimal("1000"), fetcher=fetcher)
    assert len(rez) == 1
    assert rez[0].pret == Decimal("50000")
    assert rez[0].suprafata == Decimal("1000")
    assert rez[0].pret_mp == Decimal("50")     # 50000 / 1000
    assert rez[0].relevanta == 100             # suprafata identica cu subiectul


def test_descopera_gap2_incredere_la_coada_gap4_pret_atipic():
    # GAP #2 + #4 (audit comparabile), prin pipeline-ul real:
    #  #2: un anunt din care NU se extrag atribute (LLM null) -> incredere_scazuta -> COADA, chiar daca
    #      suprafata lui bate exact subiectul (relevanta bruta mare = inselatoare, „96%" pe 1 atribut).
    #  #4: un anunt cu €/mp absurd (mult sub mediana) -> MARCAT „atipic", NU exclus (evaluatorul decide).
    def _listing(supr, pret, marker):
        return (f'<html><head><title>Casa {marker} Breaza</title>'
                f'<script type="application/ld+json">{{"@type":"Offer","price":"{pret}",'
                f'"priceCurrency":"EUR","floorSize":{{"value":"{supr}"}}}}</script>'
                f'</head><body>{marker} text</body></html>')
    listings = {"bogat": _listing(130, 250000, "BOGAT"),
                "sarac": _listing(120, 260000, "SARAC"),     # suprafata EXACT subiect, dar atribute lipsa
                "ieftin": _listing(125, 1000, "BOGAT")}       # pret absurd, dar atribute complete (confident)
    search = ('<html><body><a href="/oferta/bogat-1">a</a>'
              '<a href="/oferta/sarac-1">b</a><a href="/oferta/ieftin-1">c</a></body></html>')

    def fetcher(url):
        for k, v in listings.items():
            if k in url:
                return v
        return search

    class FakeClient:
        def complete(self, system, user):
            if "BOGAT" in user:
                return ('{"an":{"valoare":2013,"text":"2013"},"stare":{"treapta":3,"text":"ok"},'
                        '"finisaj":{"treapta":4,"text":"lux"},'
                        '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                        '"teren":{"valoare":500,"text":"500"},"secundare":[]}')
            return ('{"an":{"valoare":null,"text":""},"stare":{"treapta":null,"text":""},'
                    '"finisaj":{"treapta":null,"text":""},"incalzire":{"categorie":null,"text":""},'
                    '"teren":{"valoare":null,"text":""},"secundare":[]}')

    subiect = SubjectProfile(suprafata_construita=Decimal("120"), an=2013, stare=3, finisaj=4,
                             incalzire="centrala_gaz", teren=Decimal("500"))
    rez = descopera("imobiliare", "prahova", "breaza", subiect=subiect, atribute_secundare=[],
                    fetcher=fetcher, client=FakeClient(), max_candidati=5)
    assert len(rez) == 3
    # GAP #2: „sarac" (suprafata 120 = exact subiect -> relevanta bruta mare) e ULTIMUL fiindca incredere_scazuta
    assert rez[-1].suprafata == Decimal("120")
    assert rez[-1].breakdown.incredere_scazuta is True
    # GAP #4: „ieftin" (1000€ / 125mp = 8 €/mp << mediana) e MARCAT atipic
    ieftin = next(r for r in rez if r.pret == Decimal("1000"))
    assert "atipic" in ieftin.breakdown.explicatie


def test_gap4_calibrat_nu_marcheaza_casa_pe_teren_premium():
    # Re-audit final: pragul ±50% marca FALS o casă genuină pe teren premium (€/mp CONSTRUIT include
    # terenul -> mai mare legitim). Acum (factor 3) doar outlierii EXTREMI (preț tastat greșit) sunt marcați.
    def _l(supr, pret, m):
        return (f'<html><head><title>Casa {m}</title><script type="application/ld+json">'
                f'{{"@type":"Offer","price":"{pret}","priceCurrency":"EUR","floorSize":{{"value":"{supr}"}}}}'
                f'</script></head><body>{m}</body></html>')
    # 3 case ~2000 €/mp + 1 pe teren premium la 3600 €/mp (1.8x, legitim) + 1 cu preț tastat greșit (40 €/mp)
    L = {"casa1": _l(100, 200000, "A"), "casa2": _l(100, 210000, "B"), "casa3": _l(100, 195000, "C"),
         "premium": _l(100, 360000, "D"), "gresit": _l(100, 4000, "E")}
    search = '<html><body>' + ''.join(f'<a href="/oferta/{k}-1">{k}</a>' for k in L) + '</body></html>'

    def fetcher(url):
        for k, v in L.items():
            if "/" + k + "-" in url:        # match pe segmentul de cale (evită coliziuni cu „oferta")
                return v
        return search

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":""},"stare":{"treapta":3,"text":""},'
                    '"finisaj":{"treapta":3,"text":""},"incalzire":{"categorie":"centrala_gaz","text":""},'
                    '"teren":{"valoare":500,"text":""},"secundare":[]}')

    subiect = SubjectProfile(suprafata_construita=Decimal("100"), an=2010, stare=3, finisaj=3,
                             incalzire="centrala_gaz", teren=Decimal("500"))
    rez = descopera("imobiliare", "prahova", "breaza", subiect=subiect, atribute_secundare=[],
                    fetcher=fetcher, client=FakeClient(), max_candidati=10)
    by_pret = {r.pret: r for r in rez}
    # mediană €/mp ~2000; casa premium 3600 (1.8x) e în [mediană/3, mediană*3] -> NU marcată (era FALS la ±50%)
    assert "atipic" not in by_pret[Decimal("360000")].breakdown.explicatie
    # prețul tastat greșit (40 €/mp = factor ~50 sub mediană) -> marcat
    assert "atipic" in by_pret[Decimal("4000")].breakdown.explicatie


# ─────────────────────────── PERF-1: paralelizare prudentă ───────────────────────────

def _listing_supr(supr, pret, titlu):
    return (f'<html><head><title>{titlu}</title>'
            f'<script type="application/ld+json">{{"@type":"Offer","price":"{pret}",'
            f'"priceCurrency":"EUR","floorSize":{{"value":"{supr}"}}}}</script>'
            f'</head><body>{titlu}</body></html>')


def test_perf1_pastreaza_ordinea_url_urilor():
    # Ordinea rezultatelor (înainte de sortarea finală) trebuie să fie cea a URL-urilor, indiferent
    # de ordinea în care thread-urile termină. Anunțurile au TOATE aceeași relevanță (subiect identic)
    # -> sortarea stabilă nu le reordonează, deci verificăm direct ordinea de URL.
    n = 12
    listings = {f"l{i}": _listing_supr(100, 200000, f"CASA-{i}") for i in range(n)}
    search = ('<html><body>'
              + ''.join(f'<a href="/oferta/l{i}-1">a</a>' for i in range(n))
              + '</body></html>')

    def fetcher(url):
        for k, v in listings.items():
            if "/" + k + "-" in url:
                return v
        return search

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":""},"stare":{"treapta":3,"text":""},'
                    '"finisaj":{"treapta":3,"text":""},"incalzire":{"categorie":"centrala_gaz","text":""},'
                    '"teren":{"valoare":500,"text":""},"secundare":[]}')

    subiect = SubjectProfile(suprafata_construita=Decimal("100"), an=2010, stare=3, finisaj=3,
                             incalzire="centrala_gaz", teren=Decimal("500"))
    rez = descopera("imobiliare", "prahova", "breaza", subiect=subiect, atribute_secundare=[],
                    fetcher=fetcher, client=FakeClient(), max_candidati=n)
    assert len(rez) == n
    titluri = [r.titlu for r in rez]
    assert titluri == [f"CASA-{i}" for i in range(n)]   # ordinea URL-urilor, păstrată


def test_perf1_un_candidat_care_esueaza_nu_pica_tot():
    # Robustețe: un fetch care aruncă excepție trebuie sărit, restul candidaților rămân.
    listings = {f"l{i}": _listing_supr(100, 200000, f"CASA-{i}") for i in range(5)}
    search = ('<html><body>'
              + ''.join(f'<a href="/oferta/l{i}-1">a</a>' for i in range(5))
              + '</body></html>')

    def fetcher(url):
        if "/oferta/l2-" in url:
            raise RuntimeError("rețea picată pe candidatul 2")
        for k, v in listings.items():
            if "/" + k + "-" in url:
                return v
        return search

    class FakeClient:
        def complete(self, system, user):
            return '{"secundare":[]}'

    subiect = SubjectProfile(suprafata_construita=Decimal("100"))
    rez = descopera("imobiliare", "prahova", "breaza", subiect=subiect, atribute_secundare=[],
                    fetcher=fetcher, client=FakeClient(), max_candidati=5)
    titluri = {r.titlu for r in rez}
    assert titluri == {"CASA-0", "CASA-1", "CASA-3", "CASA-4"}   # 2 a fost sărit, restul intacte


def test_perf1_fetch_urile_ruleaza_in_paralel():
    # Dovada de concurență: dacă fetch-urile ar rula serial, N candidați la `delay` secunde fiecare ar
    # dura ~N*delay. În paralel (plafon >1), durata e ~ceil(N/plafon)*delay. Folosim un fetcher lent și
    # numărăm câte thread-uri sunt active simultan (>1 => paralelism real).
    n = _MAX_CONCURENTA_DESCOPERIRE
    delay = 0.05
    activi = 0
    maxim_simultan = 0
    lock = threading.Lock()
    listing = _listing_supr(100, 200000, "CASA")
    search = ('<html><body>'
              + ''.join(f'<a href="/oferta/l{i}-1">a</a>' for i in range(n))
              + '</body></html>')

    def fetcher(url):
        nonlocal activi, maxim_simultan
        if "/oferta/" not in url:
            return search
        with lock:
            activi += 1
            maxim_simultan = max(maxim_simultan, activi)
        try:
            time.sleep(delay)
            return listing
        finally:
            with lock:
                activi -= 1

    class FakeClient:
        def complete(self, system, user):
            return '{"secundare":[]}'

    subiect = SubjectProfile(suprafata_construita=Decimal("100"))
    t0 = time.perf_counter()
    rez = descopera("imobiliare", "prahova", "breaza", subiect=subiect, atribute_secundare=[],
                    fetcher=fetcher, client=FakeClient(), max_candidati=n)
    durata = time.perf_counter() - t0
    assert len(rez) == n
    assert maxim_simultan > 1                       # fetch-uri suprapuse (nu serial)
    assert durata < n * delay                       # mai rapid decât suma seriilor


def test_perf1_descopera_teren_paralel_si_ordonat():
    # Aceeași garanție pentru descopera_teren: paralelism + un fetch picat nu oprește restul.
    n = 6
    listings = {f"t{i}": _listing_supr(1000, 50000, f"TEREN-{i}") for i in range(n)}
    search = ('<html><body>'
              + ''.join(f'<a href="/oferta/t{i}-1">a</a>' for i in range(n))
              + '</body></html>')
    activi = 0
    maxim_simultan = 0
    lock = threading.Lock()

    def fetcher(url):
        nonlocal activi, maxim_simultan
        if "/oferta/" not in url:
            return search
        if "/oferta/t3-" in url:
            raise RuntimeError("picat")
        with lock:
            activi += 1
            maxim_simultan = max(maxim_simultan, activi)
        try:
            time.sleep(0.05)
            for k, v in listings.items():
                if "/" + k + "-" in url:
                    return v
            return search
        finally:
            with lock:
                activi -= 1

    rez = descopera_teren("imobiliare", "prahova", "breaza",
                          suprafata_subiect=Decimal("1000"), fetcher=fetcher, max_candidati=n)
    titluri = {r.titlu for r in rez}
    assert titluri == {f"TEREN-{i}" for i in range(n) if i != 3}   # 3 sărit, restul intacte
    assert maxim_simultan > 1                                       # fetch-uri suprapuse
