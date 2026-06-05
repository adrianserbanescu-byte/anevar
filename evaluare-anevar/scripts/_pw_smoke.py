"""Testare end-to-end Playwright a aplicației Evaluare ANEVAR (headless).

Verifică: încărcare pagini fără erori de consolă, cablarea câmpurilor și a butoanelor,
fluxurile între pagini (localStorage), comutarea tab-urilor și a tipului de proprietate.
"""
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
rezultate = []
erori_consola = []


def check(nume, cond, detaliu=""):
    rezultate.append((nume, bool(cond), detaliu))
    print(("  OK  " if cond else " FAIL ") + nume + (f"  [{detaliu}]" if detaliu and not cond else ""))


def pagina(ctx, url):
    p = ctx.new_page()
    errs = []
    p.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(url)
    p.wait_for_load_state("networkidle")
    return p, errs


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context()

    # ---------- WIZARD ----------
    p, errs = pagina(ctx, BASE + "/wizard")
    check("wizard: fără erori consolă", not errs, "; ".join(errs[:3]))
    # localitati populate (judet are opțiuni dincolo de placeholder)
    n_judete = p.eval_on_selector("#judet", "el => el.options.length")
    check("wizard: dropdown județ populat", n_judete > 5, f"{n_judete} opțiuni")
    # recap live: completez client_nume -> apare în panoul recap
    p.fill("#client_nume", "Ion Testescu")
    p.dispatch_event("#client_nume", "input")
    recap = p.inner_text("#r_client_nume")
    check("wizard: recap live (client)", "Testescu" in recap, recap)

    # Pas 2: comutare tip proprietate -> vizibilitate grupuri
    p.click('#stepper .step[data-pas="2"]')
    def vizibil(sel):
        return p.eval_on_selector(sel, "el => getComputedStyle(el).display !== 'none'")
    p.select_option("#tip_proprietate", "agricol")
    check("Pas2 agricol: grup-construcție ascuns", not vizibil("#grup-constructie"))
    check("Pas2 agricol: grup-teren vizibil", vizibil("#grup-teren"))
    check("Pas2 agricol: câmpuri agricol vizibile", vizibil("#agr-fields"))
    p.select_option("#tip_proprietate", "apartament")
    check("Pas2 apartament: grup-teren ascuns", not vizibil("#grup-teren"))
    check("Pas2 apartament: câmpuri apartament vizibile", vizibil("#ap-fields"))
    check("Pas2 apartament: grup-construcție vizibil", vizibil("#grup-constructie"))
    p.select_option("#tip_proprietate", "casa")
    check("Pas2 casă: ambele grupuri vizibile",
          vizibil("#grup-teren") and vizibil("#grup-constructie"))

    # Pas 4: calcul (metoda cost, valori implicite) -> apare o valoare
    p.click('#stepper .step[data-pas="4"]')
    p.click("#btn-calc")
    p.wait_for_selector("#rezultat-calc:has-text('Valoare')", timeout=8000)
    rez = p.inner_text("#rezultat-calc")
    check("wizard: calcul produce valoare", "Valoare" in rez, rez[:60])

    # Pas 5: butonul de raport e activ după calcul (link generat, fără eroare)
    p.click('#stepper .step[data-pas="5"]')
    check("wizard: buton raport prezent", p.is_visible("#btn-raport"))
    p.close()

    # ---------- GRILĂ: tab-uri ----------
    p, errs = pagina(ctx, BASE + "/grila")
    check("grilă: fără erori consolă", not errs, "; ".join(errs[:3]))
    check("grilă: panou teren vizibil inițial",
          p.eval_on_selector("#panel-teren", "el => !el.hidden"))
    check("grilă: panou casă ascuns inițial",
          p.eval_on_selector("#panel-casa", "el => el.hidden"))
    p.click("#tab-casa")
    check("grilă: după click Casă -> panou casă vizibil",
          p.eval_on_selector("#panel-casa", "el => !el.hidden"))
    check("grilă: după click Casă -> panou teren ascuns",
          p.eval_on_selector("#panel-teren", "el => el.hidden"))
    # tastatură: ArrowRight pe tab mută la chirii
    p.focus("#tab-casa")
    p.keyboard.press("ArrowRight")
    check("grilă: ArrowRight -> tab chirii selectat",
          p.eval_on_selector("#tab-chirii", "el => el.getAttribute('aria-selected') === 'true'"))
    p.close()

    # ---------- DESCOPERIRE: empty state ----------
    p, errs = pagina(ctx, BASE + "/descoperire")
    check("descoperire: fără erori consolă", not errs, "; ".join(errs[:3]))
    check("descoperire: empty state prezent",
          "Niciun rezultat încă" in p.inner_text("#rezultate"))
    p.close()

    # ---------- FLUX: grila_prefill_casa (descoperire -> grilă) ----------
    p = ctx.new_page()
    p.goto(BASE + "/grila")
    p.evaluate("localStorage.setItem('grila_prefill_casa', JSON.stringify([{pret:'250000',suprafata:'120'}]))")
    p.goto(BASE + "/grila")
    p.wait_for_load_state("networkidle")
    consumat = p.evaluate("localStorage.getItem('grila_prefill_casa')")
    check("flux: grila consumă prefill-ul (șters după citire)", consumat is None, str(consumat))
    p.close()

    # ---------- FLUX: vbp_din_grila (grilă -> wizard) ----------
    p = ctx.new_page()
    p.goto(BASE + "/wizard")
    p.evaluate("localStorage.setItem('vbp_din_grila','12345')")
    p.goto(BASE + "/wizard")
    p.wait_for_load_state("networkidle")
    vbp_val = p.eval_on_selector("#vbp", "el => el.value")
    consumat2 = p.evaluate("localStorage.getItem('vbp_din_grila')")
    check("flux: wizard preia VBP din grilă", vbp_val == "12345", f"vbp={vbp_val}")
    check("flux: vbp_din_grila șters după preluare", consumat2 is None, str(consumat2))
    p.close()

    # ---------- IMPORT: extensie -> coadă -> panou Descoperire -> grilă ----------
    _H = ('<html><head><script type="application/ld+json">'
          '{"@type":"Offer","price":"150000","priceCurrency":"EUR",'
          '"floorSize":{"value":"120"}}</script></head><body>casă</body></html>')
    r = ctx.request.post(BASE + "/api/import-anunt",
                         data={"html": _H, "url": "https://storia.ro/ro/oferta/pw-test"})
    jd = r.json()
    check("import-anunt: parsează preț+suprafață", jd.get("pret") == "150000" and jd.get("suprafata") == "120",
          str(jd.get("pret")) + "/" + str(jd.get("suprafata")))
    check("import-anunt: intră în coadă", jd.get("in_coada", 0) >= 1, str(jd.get("in_coada")))
    p = ctx.new_page()
    p.goto(BASE + "/descoperire")
    p.wait_for_load_state("networkidle")
    check("descoperire: secțiune importate vizibilă",
          p.eval_on_selector("#sectiune-importate", "el => getComputedStyle(el).display !== 'none'"))
    lista = p.inner_text("#lista-importate")
    check("descoperire: anunțul importat afișat (preț)", "150000" in lista, lista[:60])
    # trimite bifatele la grila casă -> setează grila_prefill_casa + redirect /grila
    p.click("#laGrilaImport")
    p.wait_for_url("**/grila", timeout=8000)
    check("import -> grilă: redirect la /grila", p.url.endswith("/grila"), p.url)
    p.close()
    # golesc coada pentru a nu lăsa reziduuri
    ctx.request.post(BASE + "/api/anunturi-importate/sterge")

    # ---------- AML ----------
    p, errs = pagina(ctx, BASE + "/aml")
    check("aml: fără erori consolă", not errs, "; ".join(errs[:3]))
    check("aml: banner legal prezent", "NU verifică automat" in p.inner_text("body"))
    p.close()

    b.close()

# ---------- SUMAR ----------
total = len(rezultate)
trecute = sum(1 for _, ok, _ in rezultate if ok)
print(f"\n=== {trecute}/{total} verificări trecute ===")
if trecute != total:
    print("ESEC:")
    for nume, ok, det in rezultate:
        if not ok:
            print(f"  - {nume}  [{det}]")
    raise SystemExit(1)
print("TOATE VERIFICĂRILE AU TRECUT")
