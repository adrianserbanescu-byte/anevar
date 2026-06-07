"""Verifica propagarea judet/localitate: Proprietate (#judet/#localitate) -> Descoperire (#d-judet/#d-localitate)."""
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
loc = requests.get(BASE + "/api/localitati", timeout=10).json()
jud = loc["judete"][0]
jslug = jud["slug"]
lslug = loc["localitati"][jslug][0]["slug"]
print("test judet slug:", jslug, "| localitate slug:", lslug)

requests.post(BASE + "/api/cont", json={"nume": "X", "legitimatie": "1", "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "P", "tip_proprietate": "casa", "scop": "garantare",
    "judet": jslug, "localitate": lslug}}, timeout=10).json()["uuid"]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto(f"{BASE}/dosar/{uid}", wait_until="networkidle")
    pg.wait_for_timeout(1300)
    vals = pg.evaluate("""()=>({
      judet: document.getElementById('judet') ? document.getElementById('judet').value : '?',
      djudet: document.getElementById('d-judet') ? document.getElementById('d-judet').value : '?',
      localitate: document.getElementById('localitate') ? document.getElementById('localitate').value : '?',
      dlocalitate: document.getElementById('d-localitate') ? document.getElementById('d-localitate').value : '?'
    })""")
    print("VALORI dupa load:", vals)
    propagat = vals["djudet"] == vals["judet"] and vals["djudet"] != ""
    print("PROPAGARE judet OK:" if propagat else "PROPAGARE judet ESUATA:", vals["djudet"], "vs", vals["judet"])
    b.close()
