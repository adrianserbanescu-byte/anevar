"""Check e2e: căutarea INLINE «Descoperă comparabile» — localități vecine + buton „tot județul" (#3).

Verifică (mock pe /api/descopera, capturează payload-ul):
- input #d-vecine + buton #d-cauta-judet există;
- „Caută" trimite localitatea aleasă + cele vecine (virgulă) în payload.localitate;
- „Caută în tot județul" trimite localitate='' (caută pe tot județul);
- zero erori în consolă.
Rulează pe un server de test (PYTHONPATH=src scripts/_serve_test.py), implicit 8765.
"""
import json
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
MOCK = {"metodologie": [], "candidati": [
    {"url": "https://x.ro/oferta/1", "titlu": "Test", "pret": "100000", "moneda": "EUR",
     "suprafata": "100", "teren": "400", "pret_mp": None, "relevanta": 80, "explicatie": "t"}]}

requests.post(BASE + "/api/cont", json={"nume": "E", "legitimatie": "1",
              "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar",
                    json={"wizard": {"id_client": "D9", "judet": "prahova", "localitate": "ploiesti"}},
                    timeout=10).json()["uuid"]
payloads = []

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    erori = []
    pg.on("console", lambda m: erori.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erori.append(str(e)))

    def mock(r):
        try:
            payloads.append(json.loads(r.request.post_data or "{}"))
        except Exception:
            pass
        r.fulfill(json=MOCK)
    pg.route("**/api/descopera", mock)
    pg.goto(BASE + f"/dosar/{uid}", wait_until="networkidle", timeout=15000)
    pg.wait_for_timeout(1300)  # cascada async judet -> localitate
    pg.evaluate("document.getElementById('sp-comparabile').hidden = false")

    assert pg.query_selector("#d-vecine"), "input localități vecine lipsește"
    assert pg.query_selector("#d-cauta-judet"), "buton „tot județul” lipsește"

    pg.fill("#d-vecine", "baicoi, blejoi")
    pg.click("#d-cauta")
    pg.wait_for_function("document.querySelectorAll('#d-rezultate .callout').length > 0", timeout=8000)
    loc1 = (payloads[-1].get("localitate") or "").replace(" ", "")
    assert "baicoi,blejoi" in loc1, f"vecinele nu ajung în payload: {loc1!r}"

    pg.click("#d-cauta-judet")
    pg.wait_for_timeout(1500)
    loc2 = payloads[-1].get("localitate")
    assert loc2 == "", f"„tot județul” ar trebui localitate='', e: {loc2!r}"
    b.close()

if erori:
    print("EROARE console:", erori)
    sys.exit(1)
print(f"OK: vecine -> localitate='{loc1}'; tot județul -> localitate=''; zero erori console")
