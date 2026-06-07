"""Validează grid-ul editabil din workspace (audit Tier-C): textarea ascuns, grid randat,
typing→sincronizare în textarea (contractul backend), add-rând, reload→persistență.

  python scripts/_check_grid.py http://127.0.0.1:8765
"""
import sys
import time

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"

requests.post(BASE + "/api/cont", json={"nume": "Ion Evaluator", "legitimatie": "8717",
              "format_dosar": ["id_client", "tip_proprietate"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "G1", "tip_proprietate": "casa", "scop": "garantare",
    "judet": "Prahova", "localitate": "Breaza"}}, timeout=10).json()["uuid"]

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle")
    time.sleep(0.5)

    assert pg.locator("#elemente").is_hidden(), "textarea #elemente ar trebui ascuns (înlocuit de grid)"
    assert pg.locator("#grup-cost .grid-edit").count() >= 2, "așteptam grid elemente + depreciere"
    print("OK: textarea ascuns, grid-uri randate")

    grid = pg.locator("#grup-cost .grid-edit").first       # grid-ul #elemente (6 coloane)
    inps = grid.locator("tbody tr").first.locator("input")
    for i, v in enumerate(["Structura", "S", "mp", "120", "2000", "2015"]):
        inps.nth(i).fill(v)
    time.sleep(0.3)
    tav = pg.eval_on_selector("#elemente", "e=>e.value")
    assert tav == "Structura;S;mp;120;2000;2015", f"sincronizare greșită: {tav!r}"
    print("OK: typing → textarea sincronizat:", tav)

    pg.locator("#grup-cost .grid-add").first.click()       # adaugă rând
    time.sleep(0.2)
    assert grid.locator("tbody tr").count() == 2, "add-rând nu a mers"
    print("OK: add-rând")

    time.sleep(1.6)                                        # lasă autosave-ul debounce să ruleze
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle")
    time.sleep(0.5)
    tav2 = pg.eval_on_selector("#elemente", "e=>e.value")
    assert "Structura;S;mp;120;2000;2015" in tav2, f"persistență/reload eșuat: {tav2!r}"
    g2 = pg.locator("#grup-cost .grid-edit").first
    v0 = pg.eval_on_selector("#grup-cost .grid-edit tbody tr input", "e=>e.value")
    assert v0 == "Structura", f"grid nu a re-hidratat din textarea: {v0!r}"
    print("OK: persistență + reload + re-hidratare grid:", tav2)
    b.close()

print("\n=== GRID CHECK PASSED ===")
