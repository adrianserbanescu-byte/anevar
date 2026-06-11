"""Extractia ETAJULUI apartamentului din anunt (gap profiles.py: etaj driver major).

Acopera: regex pe text liber („etaj 3", „parter", „demisol", „etaj 3/5", „3/5"), cheia
structurata storia `Floor_no`, si firul end-to-end prin `parse_listing_html`. Aditiv si robust:
None cand nu apare, fara exceptie; 0 = parter/demisol (conventia profilului).
"""
import pytest

from evaluare.importers.url_parser import (
    _etaj_din_floor_no,
    _etaj_din_text,
    parse_listing_html,
)


# ── _etaj_din_text: regex pe descriere/titlu ────────────────────────────────
@pytest.mark.parametrize(
    "text, asteptat",
    [
        ("Apartament 3 camere, etaj 3, zona centrala", 3),
        ("Garsoniera la etajul 5 din 10", 5),
        ("Apartament et. 2, bloc nou", 2),
        ("Apartament confort 1, et.4/8", 4),
        ("Apartament etaj 3/5, decomandat", 3),
        ("Apartament 2 camere 4/10, renovat", 4),         # forma „etaj/total" fara cuvantul „etaj"
        ("Apartament la parter, acces facil", 0),
        ("Apartament demisol, pret bun", 0),
        ("Apartament la mansarda, luminos", 0),
        ("Spatiu la subsol", 0),
        ("Apartament 2 camere, decomandat, renovat", None),  # niciun indiciu de etaj
        ("", None),
        ("Casa P+1+M, teren 300 mp", None),                  # „P+1" nu e etaj apartament
    ],
)
def test_etaj_din_text(text, asteptat):
    assert _etaj_din_text(text) == asteptat


def test_etaj_din_text_verbal_are_prioritate_fata_de_forma_slash():
    # „etaj 7" e explicit; „3/5" e ambiguu -> verbalul castiga.
    assert _etaj_din_text("Apartament etaj 7, vedere superba 3/5 stele") == 7


def test_etaj_din_text_parter_doar_daca_nu_e_etaj_numeric():
    # daca exista etaj numeric, nu se intoarce 0 doar pt ca apare „parter" undeva.
    assert _etaj_din_text("etaj 4, deasupra unui spatiu comercial la parter") == 4


def test_etaj_din_text_robust_la_numere_aberante():
    # numar implauzibil de mare -> ignorat (None), fara exceptie.
    assert _etaj_din_text("etaj 999") is None


# ── _etaj_din_floor_no: cheia structurata storia ────────────────────────────
@pytest.mark.parametrize(
    "valoare, asteptat",
    [
        ("floor_3", 3),
        ("floor_10", 10),
        ("ground_floor", 0),
        ("cellar", 0),
        ("3", 3),
        (3, 3),
        (None, None),
        ("penthouse", None),     # nerecunoscut, fara numar -> None
        ("floor_99", None),      # peste interval plauzibil -> None
    ],
)
def test_etaj_din_floor_no(valoare, asteptat):
    assert _etaj_din_floor_no(valoare) == asteptat


# ── end-to-end prin parse_listing_html ──────────────────────────────────────
def test_parse_listing_extrage_etaj_din_titlu():
    html = ('<html><head><title>Apartament 3 camere etaj 3/5 Cluj</title>'
            '<meta property="og:description" content="Apartament decomandat, etaj 3, renovat">'
            '</head><body></body></html>')
    parsed = parse_listing_html(html)
    assert parsed.etaj == 3


def test_parse_listing_extrage_parter():
    html = ('<html><head><title>Apartament 2 camere parter Bucuresti</title>'
            '</head><body>Apartament la parter, acces facil pentru persoane cu dizabilitati</body></html>')
    parsed = parse_listing_html(html)
    assert parsed.etaj == 0


def test_parse_listing_etaj_none_pentru_casa():
    # Anunt de casa fara mentiune de etaj apartament -> None (nu blocheaza, nu arunca).
    html = ('<html><head><title>Casa individuala 120 mp Breaza</title>'
            '<meta property="og:description" content="Casa individuala 120 mp, teren 300 mp">'
            '</head><body></body></html>')
    parsed = parse_listing_html(html)
    assert parsed.etaj is None


def test_parse_listing_floor_no_structurat_are_prioritate():
    # storia: Floor_no structurat (floor_4) bate orice forma din text.
    nextdata = (
        '<html><head><title>Apartament Cluj</title></head><body>'
        '<script id="__NEXT_DATA__" type="application/json">'
        '{"props":{"target":{"Floor_no":["floor_4"]}}}'
        '</script>'
        '<p>etaj 2 mentionat gresit in descriere</p>'
        '</body></html>'
    )
    parsed = parse_listing_html(nextdata)
    assert parsed.etaj == 4


def test_parse_listing_etaj_nu_arunca_pe_html_gol():
    parsed = parse_listing_html("<html><body></body></html>")
    assert parsed.etaj is None
