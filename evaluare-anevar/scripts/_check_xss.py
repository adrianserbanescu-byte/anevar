"""SEC-2: verifica ca date scrape-uite malitioase (titlu/url/explicatie) sunt ESCAPATE la randarea
rezultatelor de descoperire in dosar.html (anti-XSS). Mock pe /api/descopera cu payload malitios.
"""
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
requests.post(BASE + "/api/cont", json={"nume": "X", "legitimatie": "1", "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "X", "tip_proprietate": "casa", "scop": "garantare"}}, timeout=10).json()["uuid"]

MAL = {"candidati": [{"relevanta": 90, "pret": "100000", "moneda": "EUR",
                      "suprafata": "<img src=x onerror=alert(1)>",
                      "url": "javascript:alert(1)",
                      "explicatie": "<script>alert(document.cookie)</script>"}],
       "metodologie": []}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.route("**/api/descopera", lambda r: r.fulfill(json=MAL))
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle")
    pg.wait_for_timeout(900)
    pg.click("#s-comparabile")
    pg.wait_for_timeout(300)
    pg.click("#d-cauta")
    pg.wait_for_timeout(1500)
    html = pg.inner_html("#d-rezultate")
    # tag-urile RAW NU trebuie sa existe (escapate -> &lt;...&gt; = text inofensiv)
    assert "<script>alert" not in html, "XSS: <script> NEescapat (tag real)!"
    assert "<img src=x" not in html, "XSS: <img> NEescapat (tag real)!"
    assert "javascript:alert" not in html, "XSS: url javascript: ne-sanitizat!"
    assert "&lt;script&gt;" in html and "&lt;img" in html, "payload ar trebui sa apara ca TEXT escapat"
    print("=== SEC-2 XSS escapat OK (payload apare ca text, nu executat) ===")
    b.close()
