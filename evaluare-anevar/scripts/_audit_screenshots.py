"""Capturează screenshot-uri full-page la toate paginile, pentru auditul de design.

Rulează contra unui server pornit (test 8765 sau live 8000). Creează un cont + un dosar
ca paginile cu conținut (workspace, listă) să arate realist.

  python scripts/_audit_screenshots.py http://127.0.0.1:8765 docs/design-audit/screens
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/design-audit/screens")
OUT.mkdir(parents=True, exist_ok=True)

# --- setup minim de date (cont + dosar) ca paginile sa nu fie goale ---
requests.post(BASE + "/api/cont", json={"nume": "Ion Evaluator", "legitimatie": "8717",
              "format_dosar": ["id_client", "nume_client", "tip_proprietate"]}, timeout=10)
uid = ""
try:
    uid = requests.post(BASE + "/api/dosar", json={"wizard": {
        "nume_client": "Pop", "id_client": "D001", "tip_proprietate": "casa", "scop": "garantare",
        "judet": "Prahova", "localitate": "Breaza", "au": "322", "acd": "351"}}, timeout=10).json().get("uuid", "")
except Exception as e:  # noqa: BLE001
    print("setup dosar:", e)

PAGES = [
    ("01-index", "/"),
    ("02-flux-livrabile-v1.5", "/flux-livrabile"),
    ("03-incepe-v1", "/incepe"),
    ("04-dosar-workspace", f"/dosar/{uid}"),
    ("05-dosare-lista", "/dosare"),
    ("06-descoperire", "/descoperire"),
    ("07-aml", "/aml"),
    ("08-grila", "/grila"),
    ("09-documente", "/documente"),
    ("10-cont", "/cont"),
    ("11-wizard-VECHI", "/wizard"),
    ("12-formular-VECHI", "/formular"),
]

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    for name, path in PAGES:
        try:
            page.goto(BASE + path, wait_until="networkidle", timeout=15000)
            time.sleep(1.2)
            page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
            print(f"OK  {name}  ({path})")
        except Exception as e:  # noqa: BLE001
            print(f"FAIL {name} ({path}): {e}")
    browser.close()
print(f"\nScreenshot-uri in {OUT}")
