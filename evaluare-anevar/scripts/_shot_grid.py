"""Screenshot al data-entry-ului workspace cu grid-ul nou populat (pt review)."""
import sys
import time
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = Path("docs/design-audit/screens")
OUT.mkdir(parents=True, exist_ok=True)

requests.post(BASE + "/api/cont", json={"nume": "Ion Evaluator", "legitimatie": "8717",
              "format_dosar": ["id_client", "tip_proprietate"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "G1", "tip_proprietate": "casa", "scop": "garantare",
    "judet": "Prahova", "localitate": "Breaza", "au": "100", "acd": "120"}}, timeout=10).json()["uuid"]

rows = [["Structură de rezistență", "S", "mp", "120", "2200", "2008"],
        ["Finisaje", "F", "mp", "120", "800", "2015"],
        ["Instalații", "I", "buc", "1", "45000", "2008"]]

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1000})
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle")
    time.sleep(0.6)
    grid = pg.locator("#grup-cost .grid-edit").first
    for ri, row in enumerate(rows):
        if ri > 0:
            pg.locator("#grup-cost .grid-add").first.click()
            time.sleep(0.15)
        inps = grid.locator("tbody tr").nth(ri).locator("input")
        for i, v in enumerate(row):
            inps.nth(i).fill(v)
    dg = pg.locator("#grup-cost .grid-edit").nth(1)
    di = dg.locator("tbody tr").first.locator("input")
    di.nth(0).fill("17")
    di.nth(1).fill("0.20")
    time.sleep(0.4)
    pg.locator("#grup-constructie").screenshot(path=str(OUT / "WORKSPACE-grid-NOU.png"))
    print("shot ->", OUT / "WORKSPACE-grid-NOU.png")
    b.close()
