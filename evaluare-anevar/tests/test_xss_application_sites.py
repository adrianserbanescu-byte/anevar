"""SEC-2 — gardă XSS mai puternică decât prezența funcțiilor (complement la test_xss_escaping.py).

Două niveluri peste presence-check-ul existent:
  1. INVARIANT pe site-urile de aplicare (pur Python, portabil): ORICE `href="${...}"` dinamic din
     templatele care randează date scrape folosește urlSafe/urlSig — prinde regresia în care cineva
     adaugă un `href="${c.url}"` BRUT (vector javascript:), chiar dacă funcția există altundeva.
  2. BEHAVIOR real al funcțiilor escapeHtml/urlSafe (rulate cu Node pe payload-uri XSS) — verifică
     că NEUTRALIZEAZĂ efectiv `<script>`/`onerror=`/`javascript:`, nu doar că sunt referite.
     Se SARE grațios dacă Node lipsește (suita rămâne portabilă; e2e _check_xss.py acoperă oricum).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).parent.parent / "src" / "evaluare" / "web" / "templates"
HREF_DINAMIC = re.compile(r'href="\$\{([^}]*)\}"')
SANITIZER = re.compile(r'urlSafe\(|urlSig\(')
# templatele care randează date scrape în href dinamic
CU_HREF_SCRAPE = ["descoperire.html", "grila.html", "wizard.html"]


def _sursa(nume: str) -> str:
    return (TEMPLATES / nume).read_text(encoding="utf-8")


@pytest.mark.parametrize("nume", CU_HREF_SCRAPE)
def test_href_dinamic_intotdeauna_sanitizat(nume):
    """Fiecare href dinamic din JS folosește urlSafe/urlSig (blochează href=javascript: din scrape)."""
    s = _sursa(nume)
    brute = [m.group(0) for m in HREF_DINAMIC.finditer(s) if not SANITIZER.search(m.group(1))]
    assert not brute, f"{nume}: href dinamic NESANITIZAT (vector javascript: SEC-2): {brute}"


def _extrage_functie(sursa: str, nume: str) -> str:
    """Extrage `function <nume>(...){ ... }` prin potrivirea acoladelor (funcțiile pot fi multi-linie)."""
    start = sursa.index(f"function {nume}(")
    i = sursa.index("{", start)
    adanc = 0
    for j in range(i, len(sursa)):
        if sursa[j] == "{":
            adanc += 1
        elif sursa[j] == "}":
            adanc -= 1
            if adanc == 0:
                return sursa[start:j + 1]
    raise AssertionError(f"acolade neechilibrate pentru {nume}")


@pytest.mark.skipif(shutil.which("node") is None, reason="Node absent — behavior acoperit e2e (_check_xss.py)")
def test_behavior_escapeHtml_si_urlSafe_neutralizeaza_xss(tmp_path):
    """Rulează escapeHtml/urlSafe (din descoperire.html) pe payload-uri XSS și verifică neutralizarea."""
    s = _sursa("descoperire.html")
    harness = tmp_path / "xss_check.js"
    harness.write_text(
        _extrage_functie(s, "escapeHtml") + "\n" +
        _extrage_functie(s, "urlSafe") + "\n" +
        "var location = { origin: 'http://127.0.0.1:8000' };\n"
        "var r = {\n"
        "  script_escapat: !escapeHtml('<script>alert(1)</script>').includes('<script'),\n"
        "  onerror_escapat: !escapeHtml('<img src=x onerror=alert(1)>').includes('<img'),\n"
        "  amp_corect: escapeHtml('a & b') === 'a &amp; b',\n"
        "  ghilimele: escapeHtml('\\\"x\\\"') === '&quot;x&quot;',\n"
        "  js_blocat: urlSafe('javascript:alert(1)') === '#',\n"
        "  data_blocat: urlSafe('data:text/html,<script>') === '#',\n"
        "  http_permis: urlSafe('https://imobiliare.ro/x').indexOf('http') === 0,\n"
        "  titlu_real_intact: escapeHtml('Casă cu 3 camere & garaj') === 'Casă cu 3 camere &amp; garaj',\n"
        "};\n"
        "console.log(JSON.stringify(r));\n",
        encoding="utf-8",
    )
    out = subprocess.run(["node", str(harness)], capture_output=True, text=True, timeout=30, encoding="utf-8")
    assert out.returncode == 0, f"node a eșuat: {out.stderr}"
    r = json.loads(out.stdout.strip())
    esuate = [k for k, v in r.items() if not v]
    assert not esuate, f"escapeHtml/urlSafe NU neutralizează: {esuate} (rezultat: {r})"
