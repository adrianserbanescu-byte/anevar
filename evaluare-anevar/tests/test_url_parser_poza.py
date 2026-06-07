"""Poza (og:image) extrasa de parser pentru cardurile UI + default-ul max_candidati ridicat."""
from evaluare.importers.url_parser import parse_listing_html
from evaluare.web.schemas import DescoperaRequest, DescoperaTerenRequest


def test_poza_din_og_image():
    html = ('<html><head><title>Casă</title>'
            '<meta property="og:image" content="https://img.example/casa.jpg"></head>'
            '<body>120 mp</body></html>')
    assert parse_listing_html(html).poza == "https://img.example/casa.jpg"


def test_poza_fallback_twitter_image():
    html = ('<html><head><title>Casă</title>'
            '<meta name="twitter:image" content="https://img.example/t.jpg"></head>'
            '<body></body></html>')
    assert parse_listing_html(html).poza == "https://img.example/t.jpg"


def test_poza_lipsa_e_none():
    html = '<html><head><title>Casă</title></head><body>120 mp</body></html>'
    assert parse_listing_html(html).poza is None


def test_max_candidati_default_ridicat():
    # BUG max-8 reparat: default-ul nu mai e 8 (trage mai multe fara override de UI)
    assert DescoperaRequest(judet="ilfov", localitate="otopeni", subiect={}).max_candidati == 20
    assert DescoperaTerenRequest(judet="ilfov").max_candidati == 20
    # ramane configurabil din request
    assert DescoperaRequest(judet="x", localitate="y", subiect={}, max_candidati=35).max_candidati == 35
