"""Check e2e: beneficiarul se adaptează la SCOP în workspace-ul dosarului (#5, cerere Adi).

Verifică: hint-ul „Beneficiar" se schimbă cu scopul (garantare→bancă, impozitare→proprietar) și
la impozitare se auto-completează clientul ca beneficiar; plus ZERO erori în consolă.
Rulează pe un server de test (PYTHONPATH=src scripts/_serve_test.py), implicit 8765.
"""
import sys

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765"

requests.post(BASE + "/api/cont", json={"nume": "E", "legitimatie": "1",
              "format_dosar": ["id_client"]}, timeout=10)
uid = requests.post(BASE + "/api/dosar", json={"wizard": {"id_client": "D1"}},
                    timeout=10).json()["uuid"]

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    erori = []
    pg.on("console", lambda m: erori.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.goto(BASE + f"/dosar/{uid}", wait_until="networkidle", timeout=15000)

    h0 = (pg.text_content("#beneficiar-hint") or "").lower()
    assert "banc" in h0, f"hint implicit (garantare) greșit: {h0!r}"

    pg.fill("#nume_client", "Ionescu")
    pg.select_option("#scop", "impozitare")
    h1 = (pg.text_content("#beneficiar-hint") or "").lower()
    assert "proprietar" in h1, f"hint impozitare greșit: {h1!r}"
    benef = pg.input_value("#beneficiar")
    assert benef == "Ionescu", f"auto-fill beneficiar la impozitare greșit: {benef!r}"
    b.close()

if erori:
    print("EROARE — mesaje în consolă:", erori)
    sys.exit(1)
print("OK: #5 beneficiar/scop (hint dinamic + auto-fill la impozitare) + ZERO erori console")
