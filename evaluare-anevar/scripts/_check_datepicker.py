"""Verifica fix-ul date-picker din _helpers.js: handler legat + zero erori consola pe paginile shared."""
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
requests.post(BASE + "/api/cont", json={"nume": "X", "legitimatie": "1", "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "D", "tip_proprietate": "casa", "scop": "garantare"}}, timeout=10).json()["uuid"]

errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle"); pg.wait_for_timeout(600)
    bound = pg.eval_on_selector("input[type=date]", "e=>!!e._pick")
    print("date-picker handler legat pe dosar:", bound)
    pg.goto(f"{BASE}/grila", wait_until="networkidle"); pg.wait_for_timeout(400)  # _helpers.js fara date -> nu crapa
    b.close()
print("erori consola:", errs[:5] or "NICIUNA")
assert bound is True, "handler-ul nu s-a legat"
assert not errs, f"erori consola: {errs}"
print("OK")
