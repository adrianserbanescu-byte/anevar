"""Check e2e: la calcul eșuat, UI afișează mesajul REAL de la server (nu cel generic).

Înainte: `if(!r.ok) throw new Error()` arunca eroarea goală → mesaj vag „verifică valorile".
Acum: frontend-ul citește `detail`-ul (422) → utilizatorul vede cauza reală (ex. „Sunt necesare
comparabile pentru abordarea prin piață"). Rulează pe un server de test, implicit 8765.
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
    # 422 „Failed to load resource” e log-ul benign al browserului pt răspunsul de eroare al calcului
    # (așteptat când calculul eșuează legitim), NU o eroare JS reală → îl ignorăm.
    pg.on("console", lambda m: erori.append(m.text)
          if (m.type == "error" and "Failed to load resource" not in m.text) else None)
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.goto(BASE + f"/dosar/{uid}", wait_until="networkidle", timeout=15000)
    # Calcul pe un dosar gol (fără comparabile/suprafețe) → server-ul întoarce 422 cu detaliu.
    pg.evaluate("document.getElementById('calc').click()")
    pg.wait_for_function(
        "(document.getElementById('rezultat').textContent||'').indexOf('Se calculează')<0 "
        "&& (document.getElementById('rezultat').textContent||'').length>0", timeout=10000)
    msg = pg.text_content("#rezultat") or ""
    b.close()

assert "eșu" in msg, f"calculul ar fi trebuit să eșueze pe un dosar gol: {msg!r}"
# Detaliul REAL de la server (422) începe cu „Date insuficiente…"; mesajul generic NU-l conține.
assert "Date insuficiente" in msg, f"mesajul NU arată cauza reală (încă generic?): {msg!r}"
if erori:
    print("EROARE console:", erori)
    sys.exit(1)
print(f"OK: eroarea de calcul arată cauza reală -> {msg[:130]!r}")
