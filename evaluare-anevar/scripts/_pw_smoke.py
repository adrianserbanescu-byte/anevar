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

    # Pas 3: An/Stare/Finisaj pe același rând + iconiță „?" cu popover la click
    p.click('#stepper .step[data-pas="3"]')
    tops = p.eval_on_selector_all("#attr_an,#attr_stare,#attr_finisaj",
                                  'els => els.map(e => e.closest(".field").offsetTop)')
    check("Pas3: an/stare/finisaj pe același rând", len(set(tops)) == 1, str(tops))
    check("hints: iconite ? injectate", p.eval_on_selector_all(".hint-toggle", "e=>e.length") > 10)
    tog = p.query_selector('#pas-3 .hint-toggle')
    tog.click()
    check("icon ?: click deschide popover-ul", p.query_selector("#pas-3 .hint.hint-open") is not None)
    tog.click()
    check("icon ?: click din nou inchide", p.query_selector("#pas-3 .hint.hint-open") is None)

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

    # ---------- START (/" redirect dupa cont) + ALEGERE UI (/alege) + DOCUMENTE ----------
    # „/" redirectioneaza (decizie Adi 2026-06-08): fara cont -> /cont; cu cont -> /incepe.
    p, errs = pagina(ctx, BASE + "/")
    check("/ redirect la cont/incepe", p.url.rstrip("/").endswith(("/cont", "/incepe")), p.url)
    p.close()
    # Alegerea de interfata mutata pe /alege (UI nou: flux + incepe); wizard vechi ASCUNS.
    p, errs = pagina(ctx, BASE + "/alege")
    check("alege: fără erori consolă", not errs, "; ".join(errs[:3]))
    _idx = p.content()
    check("alege: UI nou (incepe + flux), wizard ascuns",
          "/incepe" in _idx and "/flux-livrabile" in _idx and "/wizard" not in _idx)
    check("alege: cross-nav prezent", p.eval_on_selector(".cross-ui", "e=>!!e") is True)
    p.close()
    p, errs = pagina(ctx, BASE + "/documente")
    check("documente: index încarcă", "Documente" in p.inner_text("body"))
    check("documente: card disclaimer", p.eval_on_selector('a[href="/documente/disclaimer-profesional"]', "e=>!!e") is True)
    p.goto(BASE + "/documente/disclaimer-profesional")
    p.wait_for_load_state("networkidle")
    check("documente: document randat", p.eval_on_selector("article.document", "e=>e.innerText.length>200") is True)
    p.close()

    # ---------- UI NOU „curent": cont -> ÎNCEPE -> dosar ----------
    # serverul e2e are OUTPUT_DIR izolat în temp -> nu atinge contul/dosarele reale
    ctx.request.post(BASE + "/api/cont", data={"nume": "Tester E2E", "legitimatie": "9999",
                     "format_dosar": ["id_client", "nume_client", "tip_proprietate", "data_raport"]})
    p, errs = pagina(ctx, BASE + "/cont")
    check("cont: fără erori consolă", not errs, "; ".join(errs[:3]))
    check("cont: nume precompletat din cont", "Tester E2E" in p.eval_on_selector("#nume", "e=>e.value"))
    p.close()

    p, errs = pagina(ctx, BASE + "/incepe")
    check("incepe: fără erori consolă", not errs, "; ".join(errs[:3]))
    check("incepe: buton Dosar nou prezent", "Dosar nou" in p.inner_text("body"))
    check("incepe: nav landmark", p.eval_on_selector("nav", "e=>!!e") is True)
    # Dosar nou cere identitatea ÎNAINTE (nu mai creează „?_?_?")
    p.click("#nou")
    check("incepe: «Dosar nou» dezvăluie formularul de identitate", not p.eval_on_selector("#form-nou", "e=>e.hidden"))
    # câmpul-dată din numele dosarului = calendar (nu free text)
    check("incepe: câmp dată în formular = calendar (type=date)",
          p.eval_on_selector("#n-data_raport", "e=>e.type") == "date")
    p.fill("#n-id_client", "777")
    p.fill("#n-nume_client", "Test Client")
    p.fill("#n-data_raport", "2026-01-15")
    p.click("#creeaza-nou")
    p.wait_for_url("**/dosar/**", timeout=8000)
    check("incepe: creare cu identitate -> workspace", "/dosar/" in p.url)
    # linkajul: data introdusă la creare pre-completează câmpul din workspace (#1)
    check("incepe: data de la creare → pre-completată în workspace (data_raportului)",
          p.eval_on_selector("#data_raportului", "e=>e.value") == "2026-01-15")
    p.close()

    uid = ctx.request.post(BASE + "/api/dosar",
                           data={"wizard": {"nume_client": "Ana E2E", "tip_proprietate": "casa"}}).json()["uuid"]
    p, errs = pagina(ctx, BASE + "/dosar/" + uid)
    check("dosar: fără erori consolă", not errs, "; ".join(errs[:3]))
    check("dosar: nume precompletat (Ana)", "Ana" in p.eval_on_selector("#nume_client", "e=>e.value"))
    # câmpurile-dată: max=azi + nu se pot alege date viitoare
    check("dosar: câmp dată are max=azi", p.eval_on_selector("#data_evaluarii", "e=>e.max===new Date().toISOString().slice(0,10)") is True)
    p.eval_on_selector("#data_evaluarii", "e=>{e.value='2099-12-31'; e.dispatchEvent(new Event('change'));}")
    check("dosar: dată viitoare blocată (clamp la azi)",
          p.eval_on_selector("#data_evaluarii", "e=>e.value<=new Date().toISOString().slice(0,10)") is True)
    # Popover-ul „!" de mapare a fost ELIMINAT (decizia #16, commit b03decc) — rămâne doar ajutorul „?".
    check("dosar: ajutor (?) prezent", p.eval_on_selector(".hint-toggle", "e=>e.textContent==='?'") is True)
    # județ/localitate = liste din /api/localitati (diacritice), cu localitate dependentă
    p.wait_for_function("document.querySelector('#judet') && document.querySelector('#judet').options.length>1", timeout=8000)
    check("dosar: județ = listă din /api/localitati", p.eval_on_selector("#judet", "e=>e.options.length>1") is True)
    p.select_option("#judet", index=1)
    check("dosar: localitate dependentă se populează la județ", p.eval_on_selector("#localitate", "e=>e.options.length>1") is True)
    check("dosar: pre-completare din documente (ingestie PDF)",
          p.eval_on_selector("#ing-fisier", "e=>!!e") is True and p.eval_on_selector("#ing-tip option[value='cf']", "e=>!!e") is True)
    # tip + scop stabilite la creare -> blocate (read-only) în workspace
    check("dosar: tip proprietate blocat după creare", p.eval_on_selector("#tip_proprietate", "e=>e.disabled") is True)

    # logica aplicaTip per tip (setăm valoarea + dispatch change, ocolind blocarea selectului)
    def _set_tip(v):
        p.eval_on_selector("#tip_proprietate",
                           "e=>{e.disabled=false; e.value='" + v + "'; e.dispatchEvent(new Event('change'));}")
    _set_tip("apartament")
    check("dosar: tip apartament -> ap-fields vizibil + teren ascuns",
          (not p.eval_on_selector("#ap-fields", "e=>e.hidden")) and p.eval_on_selector("#grup-teren", "e=>e.hidden"))
    check("dosar: apartament -> elemente cost ascunse + metoda cost dezactivată",
          p.eval_on_selector("#grup-cost", "e=>e.hidden") is True
          and p.eval_on_selector("#metoda option[value='cost']", "e=>e.disabled") is True)
    _set_tip("agricol")
    check("dosar: tip agricol -> agr-fields vizibil + construcție ascunsă",
          (not p.eval_on_selector("#agr-fields", "e=>e.hidden")) and p.eval_on_selector("#grup-constructie", "e=>e.hidden"))
    _set_tip("casa")
    check("dosar: tip casă -> teren + construcție + cost vizibile",
          (not p.eval_on_selector("#grup-teren", "e=>e.hidden")) and (not p.eval_on_selector("#grup-cost", "e=>e.hidden")))
    # Anexe ca sub-tab al Raportului (înainte de Generează) + upload foto
    p.click("#s-anexe")
    check("dosar: sub-tab Anexe + upload foto",
          (not p.eval_on_selector("#sp-anexe", "e=>e.hidden")) and p.eval_on_selector("#up-foto", "e=>!!e") is True)
    # modulul de DESCOPERIRE re-integrat inline în Comparabile (formular + buton Caută)
    p.click("#s-comparabile")
    check("dosar: căutare comparabile inline (re-integrată)",
          p.eval_on_selector("#d-cauta", "e=>!!e") is True and p.eval_on_selector("#d-judet", "e=>!!e") is True)
    check("dosar: import URL + atribute secundare (paritate descoperire)",
          p.eval_on_selector("#d-url-btn", "e=>!!e") is True and p.eval_on_selector("#d-secundare", "e=>!!e") is True)
    check("dosar: comutator căutare construcții/terenuri",
          p.eval_on_selector("#d-tip option[value='terenuri']", "e=>!!e") is True)
    check("dosar: coadă anunțuri din extensia de browser",
          p.eval_on_selector("#coada-ext", "e=>!!e") is True and p.eval_on_selector("#ext-reload", "e=>!!e") is True)
    # grilă de ajustări casă inline (port din grila.html) → /api/grila-casa
    p.eval_on_selector_all("details.grila-det", "els=>els.forEach(e=>{e.open=true;})")
    p.fill("#g-supr", "120")
    for gi in range(3):
        p.fill(f".g-pret[data-i='{gi}']", str(250000 + gi * 6000))
        p.fill(f".g-sup[data-i='{gi}']", str(120 + gi * 4))
    # ajustare de 30% pe Comp 1 (etapa proprietate, ELEM_CASA index 6 = Localizare): TREBUIE să declanșeze
    # alerta prudențială > 25% — dovedește că ajustările (cheia `adjustments`) chiar ajung la motor.
    p.fill(".g-aj[data-e='6'][data-i='0']", "0.30")
    p.click("#g-calc")
    p.wait_for_selector("#g-rezultat:has-text('Valoare de piață')", timeout=8000)
    check("dosar: grilă ajustări casă inline → valoare de piață", "Valoare de piață" in p.inner_text("#g-rezultat"))
    check("dosar: ajustările grilei chiar se aplică (alertă 25% la ajustare 30%)",
          "ajustare brută" in p.inner_text("#g-rezultat"))
    check("dosar: grila are <th scope> (a11y tabel)",
          p.eval_on_selector(".grid-aj th[scope='row']", "e=>!!e") is True
          and p.eval_on_selector(".grid-aj th[scope='col']", "e=>!!e") is True)
    # grilă de ajustări teren inline → /api/grila-teren
    p.eval_on_selector_all("details.grila-det", "els=>els.forEach(e=>{e.open=true;})")
    p.fill("#gt-supr", "500")
    for gi in range(3):
        p.fill(f".gt-pret[data-i='{gi}']", str(50 + gi * 3))
        p.fill(f".gt-sup[data-i='{gi}']", str(700 + gi * 20))
    p.click("#gt-calc")
    p.wait_for_selector("#gt-rezultat:has-text('Valoare teren')", timeout=8000)
    check("dosar: grilă ajustări teren inline → valoare teren", "Valoare teren" in p.inner_text("#gt-rezultat"))
    # grilă de chirii inline → /api/grila-chirii → VBP + punte la metoda Venit
    p.fill("#gc-supr", "100")
    for gi in range(3):
        p.fill(f".gc-pret[data-i='{gi}']", str(8 + gi))
        p.fill(f".gc-sup[data-i='{gi}']", str(90 + gi * 5))
    p.click("#gc-calc")
    p.wait_for_selector("#gc-rezultat:has-text('Venit brut')", timeout=8000)
    check("dosar: grilă chirii inline → VBP", "Venit brut" in p.inner_text("#gc-rezultat"))
    p.click("#gc-vbp")
    check("dosar: «Preia VBP» → metoda Venit + câmpul VBP completat",
          p.eval_on_selector("#vbp", "e=>e.value") != "" and p.eval_on_selector("#metoda", "e=>e.value") == "venit")
    p.click("#s-proprietate")
    p.click("#t-aml")
    check("dosar: tab AML comută panoul",
          (not p.eval_on_selector("#p-aml", "e=>e.hidden")) and p.eval_on_selector("#p-raport", "e=>e.hidden"))
    # AML in-place: formular + Evaluează (calcul local, fără redirect)
    check("dosar: AML in-place (formular + buton Evaluează)",
          p.eval_on_selector("#aml-eval", "e=>!!e") is True and p.eval_on_selector("#aml_tip_client", "e=>!!e") is True)
    p.fill("#aml_nume", "Test")
    p.click("#aml-eval")
    p.wait_for_selector("#aml-rez:has-text('Categorie risc')", timeout=8000)
    check("dosar: AML evaluare in-place -> rezultat", "Categorie risc" in p.inner_text("#aml-rez"))
    p.click("#t-raport")
    p.click("#s-calcul")
    check("dosar: sub-tab Calcul vizibil", not p.eval_on_selector("#sp-calcul", "e=>e.hidden"))
    # venit/DCF: câmpurile apar doar la metoda corespunzătoare
    p.select_option("#metoda", "cost")
    check("dosar: grup venit ascuns la cost", p.eval_on_selector("#grup-venit", "e=>e.hidden"))
    p.select_option("#metoda", "venit")
    check("dosar: grup venit vizibil la metoda venit", not p.eval_on_selector("#grup-venit", "e=>e.hidden"))
    p.select_option("#metoda", "cost")
    # butoane la finalul tabului Raport (paritate wizard): bară de jos + 3 butoane la Generează
    p.click("#s-genereaza")
    check("dosar: 3 butoane la Generează (raport + demo + audit)",
          p.eval_on_selector("#genereaza-demo", "e=>!!e") is True and p.eval_on_selector("#gen-audit", "e=>!!e") is True)
    check("dosar: bară de jos (Înapoi/Înainte/Reset/Documente)",
          p.eval_on_selector("#nav-inainte", "e=>!!e") is True and p.eval_on_selector("#reset-dosar", "e=>!!e") is True)
    p.click("#s-proprietate")
    p.click("#nav-inainte")   # Proprietate -> Comparabile
    check("dosar: «Înainte ▶» navighează la sub-tabul următor", not p.eval_on_selector("#sp-comparabile", "e=>e.hidden"))
    # checkpoint de asumare: «Generează» blocat până confirmă evaluatorul
    p.click("#s-genereaza")
    check("dosar: Generează blocat fără asumare", p.eval_on_selector("#genereaza", "e=>e.disabled"))
    p.check("#asumare")
    check("dosar: Generează activ după asumare", not p.eval_on_selector("#genereaza", "e=>e.disabled"))
    # PDF→DOCX: selectorul de format a fost SCOS — raportul e mereu .docx; verific absența + nota de export PDF
    check("dosar: fără selector format (PDF→DOCX) + notă „salvează ca PDF local”",
          p.eval_on_selector_all("input[name='gen-fmt']", "e=>e.length") == 0
          and "salvează-l ca PDF local" in p.inner_text("body"))
    p.click("#s-proprietate")
    p.fill("#au", "111")
    p.dispatch_event("#au", "input")
    p.wait_for_selector("#save-ind:has-text('salvat')", timeout=5000)
    check("dosar: autosave -> indicator „salvat”", "salvat" in p.inner_text("#save-ind"), p.inner_text("#save-ind"))
    # flux COMPLET cap-coadă: completează minim valid + generează + DESCARCĂ .docx (gol acoperire cov #2)
    p.fill("#acd", "120")
    p.fill("#an_referinta", "2025")
    # #elemente + #depreciere sunt acum grid-uri editabile (textarea CSV ascuns) -> umplem celulele după aria-label
    p.fill("input[aria-label='Element']", "Structura")
    p.fill("input[aria-label='Cod']", "X")
    p.fill("input[aria-label='U.M.']", "mp")
    p.fill("input[aria-label='Cant.']", "120")
    p.fill("input[aria-label='Cost unitar']", "2000")
    p.fill("input[aria-label='An PIF']", "2015")
    p.fill("input[aria-label^='Vârstă']", "5")   # grid depreciere (textarea ascuns)
    p.fill("input[aria-label^='Fracție']", "0.05")
    p.fill("#suprafata_teren", "500")
    p.fill("#valoare_teren", "100000")
    p.fill("#data_evaluarii", "2026-01-16")     # setate ca să NU apară confirm-ul de dată lipsă
    p.fill("#data_raportului", "2026-01-16")
    p.click("#s-genereaza")
    p.click("#genereaza")
    # blob-download via a.click() nu e prins fiabil de expect_download; verificăm statusul de succes „✓ … salvat".
    p.wait_for_selector("#gen-status:has-text('salvat')", timeout=15000)
    check("dosar: flux complet → raport generat + salvat ca versiune",
          "salvat" in p.inner_text("#gen-status"))
    p.close()

    # ---------- FEEDBACK: widget -> salvare locală -> pagina /feedback ----------
    p = ctx.new_page()
    p.goto(BASE + "/wizard")
    p.wait_for_load_state("networkidle")
    p.click("#fb-open")
    check("feedback: panoul se deschide", not p.eval_on_selector("#fb-panel", "e=>e.hidden"))
    p.fill("#fb-msg", "Test automat e2e - merge")
    p.click("#fb-send")
    p.wait_for_selector("#fb-status:has-text('Mulțumim')", timeout=8000)
    salvat = ctx.request.get(BASE + "/api/feedback").json()["feedback"]
    check("feedback: salvat local prin widget",
          any("Test automat e2e" in (f.get("mesaj") or "") for f in salvat), str(len(salvat)))
    p.goto(BASE + "/feedback")
    check("feedback: apare în pagina /feedback", "Test automat e2e" in p.inner_text("body"))
    csv = ctx.request.get(BASE + "/api/feedback.csv")
    check("feedback: export CSV", csv.ok and "Test automat e2e" in csv.text())
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
