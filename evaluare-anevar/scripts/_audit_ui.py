"""Audit UI (cerere Adi):
  (1) ALINIERE: screenshot-uri full-page ale formularelor -> inspectie vizuala.
  (2) LINKURI + INTOARCERE LA UI VECHI: flag linkuri /wizard//formular din UI NOU;
      verifica daca paginile vechi (wizard/form/result) au cale inapoi la UI nou.
"""
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."

requests.post(BASE + "/api/cont", json={"nume": "Audit", "legitimatie": "1",
              "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "id_client": "AUD", "tip_proprietate": "casa", "scop": "garantare",
    "nume_client": "Test Client", "judet": "", "localitate": ""}}, timeout=10).json()["uuid"]

OLD = ("/wizard", "/formular")
NOU = ("/incepe", "/alege", "/flux-livrabile")
pagini_nou = ["/alege", "/incepe", f"/dosar/{uid}", "/descoperire", "/grila",
              "/documente", "/cont", "/dosare", "/flux-livrabile"]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()

    print("=== AUDIT 2: linkuri catre UI VECHI gasite in UI NOU ===")
    gasit = []
    for url in pagini_nou:
        try:
            pg.goto(BASE + url, wait_until="networkidle", timeout=15000)
        except Exception as e:
            print(f"  (nu am putut incarca {url}: {e})")
            continue
        hrefs = pg.eval_on_selector_all("a[href]", "els => els.map(a => a.getAttribute('href'))")
        for h in hrefs:
            if h and (h in OLD or h.rstrip("/").endswith(("/wizard", "/formular"))):
                gasit.append((url, h))
    if gasit:
        for u, h in sorted(set(gasit)):
            print(f"  ⚠ LINK UI-VECHI: pe {u}  ->  {h}")
    else:
        print("  OK: niciun link /wizard sau /formular in UI nou")

    print("=== AUDIT 2b: paginile vechi au cale INAPOI la UI nou? (sa nu te 'prinda') ===")
    for url in OLD:
        try:
            pg.goto(BASE + url, wait_until="networkidle", timeout=15000)
        except Exception:
            print(f"  {url}: (eroare incarcare)")
            continue
        hrefs = pg.eval_on_selector_all("a[href]", "els => els.map(a => a.getAttribute('href'))")
        back = sorted({h for h in hrefs if h and h.rstrip("/").endswith(NOU)})
        print(f"  {url}: inapoi la UI nou = {'DA ' + str(back) if back else '⚠ NU — te prinde in UI vechi!'}")

    print("=== AUDIT 1: screenshot-uri pt aliniere ===")
    shots = [(f"/dosar/{uid}", "dosar-workspace"), ("/incepe", "incepe"), ("/grila", "grila")]
    for url, nume in shots:
        try:
            pg.goto(BASE + url, wait_until="networkidle", timeout=15000)
            pg.wait_for_timeout(700)
            cale = f"{OUT}/audit-{nume}.png"
            pg.screenshot(path=cale, full_page=True)
            print(f"  screenshot: {cale}")
        except Exception as e:
            print(f"  (screenshot {nume} esuat: {e})")
    b.close()
print("=== AUDIT DONE ===")
