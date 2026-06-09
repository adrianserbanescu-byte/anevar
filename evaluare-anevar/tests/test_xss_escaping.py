"""SEC-2 (gap UNIT flag-at de D, audit testare): gardă de REGRESIE rapidă la nivel unit ca
templatele care randează date SCRAPE (descoperire/grila) escapează prin escapeHtml + urlSafe.

Comportamentul runtime (payload `<script>`/`onerror=`/`javascript:` → text inofensiv) e acoperit
la e2e de `scripts/_check_xss.py` (Playwright, mock pe /api/descopera). Aici prindem REPEDE, fără
browser, o regresie în care cineva scoate escaparea din randarea datelor scrape.
"""
from pathlib import Path

TEMPLATES = Path(__file__).parent.parent / "src" / "evaluare" / "web" / "templates"


def _sursa(nume: str) -> str:
    return (TEMPLATES / nume).read_text(encoding="utf-8")


def test_descoperire_escapeaza_scrape_cu_escapeHtml_si_urlSafe():
    s = _sursa("descoperire.html")
    assert "escapeHtml(" in s, "descoperire: lipsește escapeHtml pe date scrape (anti-XSS SEC-2)"
    assert "urlSafe(" in s, "descoperire: lipsește urlSafe pe URL-uri scrape (anti-XSS SEC-2)"


def test_grila_escapeaza_scrape_cu_escapeHtml_si_urlSafe():
    s = _sursa("grila.html")
    assert "escapeHtml(" in s, "grila: lipsește escapeHtml pe date scrape (anti-XSS SEC-2)"
    assert "urlSafe(" in s, "grila: lipsește urlSafe pe href-uri scrape (anti-XSS SEC-2)"
