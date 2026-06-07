"""Verifica grid-ul comparabile/comparabile_teren (#6): ascuns, grid, typing->sync, import->refresh."""
import sys
import time

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
requests.post(BASE + "/api/cont", json={"nume": "X", "legitimatie": "1", "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "C", "tip_proprietate": "casa", "scop": "garantare"}}, timeout=10).json()["uuid"]

errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("console", lambda m, e=errs: e.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda ex, e=errs: e.append(str(ex)))
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle")
    pg.wait_for_timeout(900)
    pg.click("#s-comparabile")   # grid-ul comparabile e in sub-tabul Comparabile (ascuns by default)
    pg.wait_for_timeout(350)

    assert pg.locator("#comparabile").is_hidden(), "comparabile textarea trebuie ascuns"
    assert pg.locator("#comparabile_teren").is_hidden(), "comparabile_teren textarea trebuie ascuns"
    assert pg.locator("#comparabile + .grid-edit").count() == 1, "lipsește grid comparabile"
    print("OK: textarea-uri ascunse, grid-uri prezente")

    pg.fill("input[aria-label='Preț']", "250000")
    pg.fill("input[aria-label='Suprafață (mp)']", "120")
    time.sleep(0.3)
    v = pg.eval_on_selector("#comparabile", "e=>e.value")
    assert v == "250000;120", f"sync manual greșit: {v!r}"
    print("OK: typing -> textarea:", v)

    n0 = pg.locator("#comparabile + .grid-edit tbody tr").count()
    pg.evaluate("()=>{var t=document.getElementById('comparabile'); t.value=t.value+'\\n300000;150'; t._grid.refresh();}")
    time.sleep(0.25)
    n1 = pg.locator("#comparabile + .grid-edit tbody tr").count()
    assert n1 == n0 + 1, f"import->refresh nu a adăugat rând: {n0}->{n1}"
    vfin = pg.eval_on_selector("#comparabile", "e=>e.value")
    print(f"OK: import->refresh {n0}->{n1} rânduri; textarea={vfin!r}")
    b.close()

assert not errs, f"erori consolă: {errs[:5]}"
print("erori consolă:", errs[:5] or "NICIUNA")
print("=== #6 COMPARABILE GRID OK ===")
