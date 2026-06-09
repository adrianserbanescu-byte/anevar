"""Check e2e: selectorul „Tip" din /descoperire (casă/apartament/teren) — cerere Adi.

Verifică: selectorul există, toggle-ul de câmpuri funcționează (teren ascunde câmpurile de
clădire; apartament arată nr. camere) și NU apar erori în consolă (prinde greșeli JS de sintaxă).
Rulează pe un server de test (PYTHONPATH=src scripts/_serve_test.py), implicit 8765.
"""
import sys

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    erori = []
    pg.on("console", lambda m: erori.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.goto(BASE + "/descoperire", wait_until="networkidle", timeout=15000)

    assert pg.query_selector("#tip"), "selectorul Tip lipsește"
    optiuni = pg.eval_on_selector_all("#tip option", "els => els.map(o => o.value)")
    assert set(optiuni) == {"casa", "apartament", "teren"}, f"opțiuni greșite: {optiuni}"

    pg.select_option("#tip", "teren")
    assert pg.query_selector("#camp-cladire").is_hidden(), "la teren, câmpurile de clădire ar trebui ascunse"

    pg.select_option("#tip", "apartament")
    assert not pg.query_selector("#camp-apartament").is_hidden(), "la apartament, nr. camere ar trebui vizibil"
    assert not pg.query_selector("#camp-cladire").is_hidden(), "la apartament, câmpurile de clădire rămân vizibile"

    pg.select_option("#tip", "casa")
    assert pg.query_selector("#camp-apartament").is_hidden(), "la casă, nr. camere ar trebui ascuns"
    b.close()

if erori:
    print("EROARE — mesaje de eroare în consolă:", erori)
    sys.exit(1)
print("OK: selector Tip (casa/apartament/teren) + toggle câmpuri + ZERO erori console")
