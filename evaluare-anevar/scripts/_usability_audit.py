"""Audit de usability/interactiune (Playwright) — gaseste sistematic probleme de interactiune+layout.
Output: JSON cu probleme + screenshots desktop/mobil per pagina pt review euristic.
  python scripts/_usability_audit.py http://127.0.0.1:8765
"""
import json
import re
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"
OUT = "docs/design-audit"

# setup: cont cu format care expune tokeni (ca in screenshot Adi) + un dosar casa
requests.post(BASE + "/api/cont", json={"nume": "Adrian Serbanescu", "legitimatie": "126",
              "format_dosar": ["scop", "data_raport", "nume_evaluator"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {
    "scop": "garantare", "tip_proprietate": "casa", "judet": "Prahova", "localitate": "Breaza",
    "nume_client": "Pop", "au": "100", "acd": "120"}}, timeout=10).json().get("uuid", "")

PAGES = [("incepe", "/incepe"), ("dosar", "/dosar/" + uid), ("descoperire", "/descoperire"),
         ("cont", "/cont"), ("aml", "/aml"), ("grila", "/grila")]

issues = []
def add(pg_name, sev, cat, msg):
    issues.append({"pagina": pg_name, "sev": sev, "cat": cat, "msg": msg})

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for name, path in PAGES:
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        errs = []
        pg.on("console", lambda m, e=errs: e.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda ex, e=errs: e.append(str(ex)))
        try:
            pg.goto(BASE + path, wait_until="networkidle", timeout=15000)
        except Exception as ex:  # noqa: BLE001
            add(name, "HIGH", "load", f"pagina nu s-a incarcat: {ex}")
            pg.close()
            continue
        pg.wait_for_timeout(700)

        for e in errs[:5]:
            add(name, "HIGH", "consola", e[:150])

        ndate = pg.locator("input[type=date]").count()
        if ndate:
            add(name, "MED", "interactiune",
                f"{ndate} input(uri) type=date: pickerul se deschide DOAR pe iconita (native), nu pe tot field-ul; format = locale OS (poate mm/dd/yyyy)")

        body_txt = pg.locator("body").inner_text()
        toks = {t for t in re.findall(r"\b[a-z][a-z]+_[a-z_]+\b", body_txt) if len(t) > 8}
        if toks:
            add(name, "MED", "copy", f"tokeni interni expusi in text: {', '.join(sorted(toks)[:6])}")

        unlabeled = pg.evaluate("""() => {
          const els=[...document.querySelectorAll('input:not([type=hidden]):not([type=radio]):not([type=checkbox]):not([type=date]),select,textarea')];
          return els.filter(e=>!e.getAttribute('aria-label')&&!e.closest('label')&&!(e.id&&document.querySelector('label[for=\"'+e.id+'\"]'))).length;
        }""")
        if unlabeled:
            add(name, "MED", "a11y", f"{unlabeled} camp(uri) fara label asociat / aria-label")

        small = pg.evaluate("""() => [...document.querySelectorAll('button,.btn,a.btn')]
          .filter(e=>{const r=e.getBoundingClientRect();return r.height>0&&r.height<30;}).length""")
        if small:
            add(name, "LOW", "hit-target", f"{small} buton/link cu inaltime <30px (greu de apasat)")

        pg.screenshot(path=f"{OUT}/ux-{name}-1280.png", full_page=True)
        for w in (768, 390):
            pg.set_viewport_size({"width": w, "height": 900})
            pg.wait_for_timeout(350)
            ov = pg.evaluate("() => ({d: document.documentElement.scrollWidth, w: window.innerWidth})")
            if ov["d"] > ov["w"] + 2:
                add(name, "MED", "responsive", f"overflow orizontal la {w}px (continut {ov['d']}px > ecran {ov['w']}px) -> scroll lateral")
        pg.screenshot(path=f"{OUT}/ux-{name}-390.png", full_page=True)
        pg.close()
    b.close()

print(json.dumps(issues, ensure_ascii=False, indent=1))
print(f"\n--- {len(issues)} probleme; screenshots in {OUT}/ux-*.png ---")
