# Changelog

Toate schimbările notabile sunt documentate aici.
Format generat din `git log` (381 commits, 2026-05-31 -> 2026-06-07).

---

## 2026-06-07  _(2 commits)_

### Diverse
- `5966b6e` Pachet de review: explicație exhaustivă a aplicației + ce mai e de făcut
- `908a81c` Registru livrabile finale pe criterii (destinatar/stare/poartă/format)

---

## 2026-06-06  _(99 commits)_

### Securitate
- `4e73a1f` Hardening (council temp-hygiene) + tracking: șterge .docx temporar (PII) după trimitere; sinteză+BLOCAT
- `99f1585` Hardening din auditul final + council: 8 fix-uri Bucket-A (securitate + buguri)
- `6259727` Audit final (4 fluxuri): securitate + buguri/eșecuri silențioase + datorie tehnică + acoperire teste
- `0cda6c6` Securitate: import .docx în director temporar UNIC (anti-coliziune; numele original păstrat pt parser)

### Robustețe
- `515fffd` Robustețe + acoperire: dosar.json corupt → 404 (nu 500) + 3 teste de contract
- `194664a` Robustețe „zero crash-uri pentru tester": descoperire/evaluare nu mai dau 500 + UI nu maschează eșecul
- `7f44d0a` Robustețe + e2e cap-coadă: calcul/raport/audit → 422 pe date insuficiente (nu 500); flux complet testat

### Conformitate ANEVAR/SEV/GEV
- `6e1fbe8` Conformitate (GEV 630 §28): cale de acces în descrierea proprietății (afectează valoarea) + UI + test
- `990d410` Conformitate (GEV 630 §16/§28): utilități + regim urbanistic în descrierea proprietății
- `016915c` Conformitate (GEV 630 §16): act de proprietate în raport + UI; sinteză actualizată (C-imobiliare)
- `6971cc4` Conformitate (GEV 630 §24/§44, Bucket A): detalii inspecție în raport + UI
- `501b05c` Conformitate (SEV 230, Bucket A): dreptul evaluat + sarcini CF în raport (critic la garantare)
- `c4b5f4d` Conformitate: câmp Regim teren (intravilan/extravilan) în UI nou → land.categorie (GEV 630)
- `40f142b` Conformitate #3 (Bucket A): raportul citează SURSA tipului valorii (SEV 102) + slug→denumire lizibilă
- `0981e89` UI nou: grilă de ajustări TEREN inline (port din grila.html) — 2 etape + alertă prudențială 25% GEV 520
- `d8ac934` UI nou: grilă de ajustări CASĂ inline (port din grila.html) — 2 etape + alertă prudențială 25% GEV 520
- `b347284` Loop special: matrice conformitate tip×scop + re-analiza LEGE/NORME AML + 3 ADR-uri formale
- `2633885` Audit de conformitate SEV 2025: aplicatie + planuri vs standard integral (4 fluxuri)
- `fc61d19` Validare SEV 2025: anexele foto/documente = conformitate (GEV 630 confirma council-ul)

### UI nou (workspace)
- `fb1f976` UI nou: a11y — glifele decorative ↻/↑ din butoane in <span aria-hidden> (închide auditul a11y)
- `2415c22` UI nou: a11y minor — touch target 32px, focus-offset pe tab-uri, ⚠ aria-hidden (incepe)
- `f8a47d0` UI nou: fixuri a11y auto-safe pe UI-ul crescut (din 6-a11y-actualizat.md)
- `c71387c` UI nou #5b: backup dosare .zip + backlog de paritate UI CURĂȚAT
- `f8bbd2e` UI nou #5a: coadă „anunțuri din extensia de browser" inline în Comparabile
- `bb3a51f` UI nou #2: ingestie documente PDF (CF/releveu/plan/CPE) → pre-completează câmpurile
- `ec5a8d9` UI nou: descoperă TERENURI (comutator construcții/terenuri) + actualizare task-list
- `dd5aec3` UI nou: județ/localitate = liste din /api/localitati (diacritice + slug) + câmp proprietar
- `8f52a70` UI nou: grilă CHIRII + BUG FIX cheie `ajustari`->`adjustments` (grilele ignorau ajustările!) + punte VBP
- `d0c9291` UI nou: date — blochează datele VIITOARE (max=azi) + format românesc (zz.ll.aaaa) lângă fiecare câmp
- `3128a76` UI nou #1: câmpurile-dată la crearea dosarului = calendar + legate de workspace (verificat vizual)
- `e9c5127` UI nou: 10 buguri din testarea vizuală a owner-ului (verificat cu Playwright)
- `a9b0051` UI nou: alerte de validare la calcul + import URL + atribute secundare (din inventarul de controale)
- `6cd958f` UI nou: butoane la finalul tabului Raport + mai multe la Generează (paritate wizard, verificat VIZUAL)
- `b64f153` UI nou: help data_evaluarii — daca e goala, AML foloseste data de azi (AJUTOR popover + hint inline)
- `6237772` UI nou #10: optiune adnotari la Generaza (raport de review) + fix lint e2e
- `955e3fa` UI nou #5: «Dosar nou» cere identitatea ÎNAINTE de creare (gata cu numele "?_?_?")
- `4b033d0` UI nou #9: AML in-place complet (port formular din aml.html in sub-tab; nu redirect)
- `878b2ad` UI nou #9: Audit in-place (urma de calcul pe fluxul pe foldere, nu redirect)
- `b9e891b` UI nou #9 (partial): GDPR in-place — butoane Politica + Consimtamant (.docx) in sub-tab, nu redirect
- `714efa4` UI nou #8: modulul de DESCOPERIRE re-integrat inline in Comparabile ("AI taiat cautarea" -> reparat)
- `3c6c810` UI nou #14: Anexe = sub-tab al Raportului (intre Calcul si Genereaza) + upload foto/scanuri
- `34b6050` UI nou #7: campuri DINAMICE per tip proprietate (port aplicaTip din wizard)
- `9f3ffd2` AUTONOM-taskuri: recuperarea UI nou = P0 (precede agenda speciala); imediate facute, scurt-termen listate
- `aab8d20` UI nou — fixuri IMEDIATE din review (frontend, backend deja gata)
- `ef0d9e2` Audit UI nou vs UI vechi (functional frontend+backend + a11y): regresii confirmate + plan
- `9322fc1` Council complet (Q2+Q3 + plan-UI nou): verdicte foldate + comparație cu planul meu
- `e5b8b4c` Paritate UI nou: metode Venit (capitalizare) + DCF în workspace
- `00448a5` Pregătire council adițional: brief exhaustiv UI nou + queue precis în AUTONOM-taskuri
- `16ca261` Paritate UI nou: grila de teren (land_comparables) în workspace
- `2f54ac3` UI nou: aplică fixurile auto-safe din audit (a11y + UX + design)
- `0a18297` UI nou (versiunea curentă): cont local + ÎNCEPE + workspace dosar

### AML
- `2863973` Revert: text juridic AML (art. citare) ramane NESCHIMBAT — bucket C (jurist), nu autonom

### Audituri
- `b64e783` Audit final: igiena logurilor VERIFICAT curat (fără PII, INFO, rotating)
- `b2d22e6` AUTONOM-taskuri: 7 regresii UI majore recuperate (✅); ramas AML/Audit in-place + grile reale
- `0e5232e` Audituri (a11y/UX/design/tehnic/cod) → fixuri auto-safe + sinteze + lista BLOCAT-pe-Adi
- `00959b5` Lansare pe piata: sinteza + audit consiliu LLM + evaluare juridica RO + strategie
- `76b02db` Audit import portaluri (imobiliare/storia/olx) + 2 fixuri de corectitudine

### Council LLM
- `48d113e` Council de preluat: OLX downgrade scor (suprafață lipsă → −30 relevanță + avertisment). +test (492)
- `7eda6bb` 9 topicuri de decis (feature/module): analiza mea pe toate 9 + council Q1 (topics 1,5,7)
- `29e6487` Council #2 (stare curenta) + checkpoint de asumare in UI (blocant top-3 convergent)

### Bugfixuri
- `d2dabda` test: regresie web pentru fixul HIGH (import-url refuza pagina de lista -> 422)
- `709431a` e2e nou-UI + fix critic ($ redeclarat) + actualizare trackere

### Loop autonom
- `beaefe4` AUTONOM-taskuri: gaps din inventarul de controale (grile, ingestie PDF, terenuri, localitati select, backup)
- `43df6b3` AUTONOM-taskuri: loop special RULAT (matrice tip×scop + LEGE/NORME + 3 ADR-uri); revin la cadenta 1h
- `cc6dd98` AUTONOM-taskuri: 11/12 plangeri UI recuperate; ramane doar grilele reale (port grila.html)
- `e955286` Widget feedback pe tot UI-ul (mutat în subsolul comun) + listă taskuri autonome + polish

### Documentație
- `271c78f` log: sesiune audituri+council+hardening+pachet feedback
- `ecb8af8` log: batch conformitate descriere proprietate (GEV 630/SEV 230)
- `e700ce6` docs: sinteză conformitate actualizată — descrierea proprietății completă (GEV 630 §16/§28, SEV 230 §40/§140)
- `f7ad7b0` log: sinteză sesiune lungă — recuperare paritate UI nou + grile + a11y + conformitate
- `332e814` docs: paritate UI nou aproape completă (venit/DCF ✅) — rămâne doar anexa foto (gated)
- `26fb194` docs: planul meu (Claude) pentru noul UI (de comparat cu council la reconectare)
- `b771676` docs: actualizare listă autonomă (grila teren ✅, retenție .docx ✅, rebuild pending)
- `1d9ad45` docs: actualizare listă autonomă (loop) — council Q2/Q3 blocate de MCP offline, restul făcut
- `f419d02` docs: sinteza nopții — fișierul-umbrelă peste toate outputurile (ce am făcut, identificat, rezolvat, planificat)
- `fce96e1` log: sesiune II (pachet lansare + audit juridic RO + council #2 + checkpoint asumare)
- `0ac0dad` docs: pptx regenerat (2026-06-06, fisier datat) + note-viitoare
- `c957dee` docs: detaliere feature B (prompt generare per capitol din matrice + hints)
- `4458448` docs: fără duplicare UI (nou=unic, mapăm vechiul) + parking-lot note-viitoare + flux 5 opțiuni
- `1345be9` docs: curățare spec #2 (elimin secțiunea duplicată după implementare)
- `d427e1b` docs: #2 dosar cu identitate + dependență #1; metrare #4 pe identitate
- `55c4ae3` docs: plan de implementare #4 comercializare (MVP pe task-uri) + actualizare index
- `8a1593d` docs: index „MAJOR features pending" + spec-uri pentru cele 4 subiecte

### Diverse
- `935f0b0` Refac pptx (generator nou + QA vizual) + regenerez raportul Breaza (îmbogățit)
- `cb45edd` Polish .exe: siglă (casă albă pe albastru) + metadate de versiune Windows
- `b5aff5c` Pachet feedback: README pt tester + gitignore binare (zip/exe)
- `5162224` AML: citare sancțiuni art. 33 -> art. 43/44/49 aplicată CONSISTENT (cod + UI), pending jurist
- `33fa81f` Retenție versiuni .docx per dosar (păstrează ultimele 10) + nume cu microsecunde
- `4d9d843` Index de alegere UI (nou vs wizard) + pagina Documente + cross-linkuri peste tot
- `f679e22` Acoperire ingestie/ocr 76%->96% + plan F la zi; exe reconstruit (50 MB)
- `40feb6b` chore: gitignore .playwright-mcp/ (artefacte temporare browser MCP)
- `f571eea` Browser cross-check portaluri + scoate dosar disparut din index + coverage narativ
- `8b4f6f5` portal_search: preferă localitatea în slug (taie promovatele) + trackere la zi
- `b1f3079` build.py: forțează UTF-8 pe stdout/stderr (consola cp1252 crăpa la print cu diacritice)
- `e1b26c9` Import dosar din .docx + seed cont „Adi S" + 4 dosare exemplu
- `2a1c3d2` Noul UI — Faza 1: cont local + stocare dosare pe foldere (sursa de adevăr)
- `f45e351` master_config (opțiuni admin per cont) + captură admin/conturi/denumire în spec #4
- `957edb4` docs(#1): cadru două versiuni UI (veche/curentă) + regulă permanentă de mentenanță
- `3a409f9` #2 stocare dosare: pagină /dosare (revenire/redenumire/descărcare/ștergere) + versiuni .docx

---

## 2026-06-05  _(32 commits)_

### Robustețe
- `198e74e` feat(robustete): galata D - backup, migrare schema, versiune (D1-D4)

### Conformitate ANEVAR/SEV/GEV
- `02b9f4f` feat(raport): valoare de lichidare (B4) + anexa de certificare GEV 520 (B5)

### Council LLM
- `e3c30f8` feat(garduri): galata A post-LLM-council - alerte/disclaimere (calcule neatinse)

### Bugfixuri
- `388dfdb` Fix Pas 2: tip proprietate cablat la profil + câmpuri per tip
- `e41728c` fix(exe): exclude cryptography (corupea arhiva PKG, 'decompression -1')
- `9c5f8fb` fix(exe): portabilitate pe alt calculator - ancorare date + jurnal de eroare

### Loop autonom
- `43c0fa8` Autonom: /api/status, ștergere individuală din coadă, portal olx.ro

### Documentație
- `0f92348` docs: regenerare raport Breaza (lichidare+certificare+consistenta) + prezentare
- `ce36842` docs: materiale care deblocheaza B/C (audit AML jurist, peer-review, GDPR, banci, extensie)
- `907b641` docs: regenerare raport Breaza cu verificarea de consistenta cost<->piata (28.77%)
- `f21cd2b` docs: dosar de review pentru LLM council (autosuficient + intrebari tintite)
- `edf873f` docs: cerinta de sistem .exe - Windows 8.1/10/11 (nu Win7)

### Diverse
- `940f891` Feedback: cablare Google Forms (FORM_ID + 5 entry IDs)
- `98d204a` Build: -72% dimensiune (170→48 MB) excluzând biblioteci neimportate + script de build
- `458ded5` Ghid: conectarea widgetului de feedback la Google Forms (FORM_ID + entry IDs)
- `10deeed` Feedback: și ca fișier feedback-<data>.csv lângă exe (ușor de găsit/trimis)
- `79f0647` Feedback local-first: salvare offline în SQLite + listare/CSV (widget funcțional din prima)
- `84f95f5` Distribuție către evaluator: .env.example + ghid pas-cu-pas
- `04a8d23` Wizard: comasare câmpuri pe rânduri + comentarii „?" cu popover (densitate redusă)
- `4e550ab` Strategie de testare cap-coadă + acoperire căi HTTP rămase + prag 90%
- `d8aec53` Cablare scop→profil (simetric cu tip→profil)
- `33ddf65` Testare e2e Playwright: 30 verificări browser (wizard/grilă/descoperire/aml + fluxuri)
- `2fca521` Wizard Pas 1: câmpuri pe rânduri (layout în coloane)
- `a267d18` UX backlog review: uniformizare „Grile de ajustări" + reconciliere backlog
- `d36f128` Ierarhie CTA: acțiuni secundare ghost (primarul rămâne plin)
- `dffb6aa` Design-critique: nav curat, tab-uri la Grilă, empty states, aria-expanded
- `6e199db` A11y (WCAG 2.1 AA): stil .ghost real, rel=noopener pe linkuri _blank, backlog UX
- `e0d641c` UX-copy: mesaje de eroare după tiparul Ce+De ce+Cum repari; link descriptiv
- `96d6c57` Coadă de import persistentă (SQLite) + aliniere materiale extensie
- `a077c1a` Extensie browser completă (storia.ro/imobiliare.ro) + coadă de import end-to-end
- `3599913` feat(C5/C6): documente GDPR .docx + endpoint import-anunt + schelet extensie browser
- `f13e49a` build(D5): excludere module GUI/test din .exe (tkinter/test/lib2to3) -> 176->173 MB

---

## 2026-06-04  _(113 commits)_

### Conformitate ANEVAR/SEV/GEV
- `f397a61` report(A3.1): citeaza SEV 103/105 la aplicarea metodelor (aliniere SEV 2025)
- `b6ffaa5` feat(raport): conformitate constienta de ghid (GEV 520/630/500)

### AML
- `8f2838a` log + memorie: modul AML implementat integral (269 teste)
- `647b118` AML faza 5: verificare + bundling exe
- `44fb5c7` AML faza 4: integrare (serviciu, liste, store separat, API, pagina)

### Bugfixuri
- `b0ba984` ux(copy): standardizare - diacritice, persoana II, loading impersonal, erori cu fix
- `3ac385b` design-system: fix conflict badge + tokeni (culori/spatiere/raze/easing)
- `c6388fe` docs(log): sesiune A3 (ghid-aware, ro-RO, a11y, grila de chirii) + fix exe AVIF
- `1912572` fix(exe): exclude PIL._avif (Pillow 12) care corupea arhiva PKG
- `4568ca0` log.md: fix critic exe (dezactivare UPX)
- `dd4f98c` fix exe: dezactiveaza UPX (corupea PIL/_imagingft.pyd -> exe nu pornea)
- `b083ebf` log.md: Track B (a11y) + Track C (docs + auto-review fix corectitudine)
- `d1a7211` Track C: fix corectitudine din auto-review (C1/C2/C3/I1/M2)
- `3a6b760` a11y: fixuri WCAG 2.1 AA pe wizard/aml/grila/descoperire + plan

### Documentație
- `320b178` docs: regenerare raport Breaza + prezentare (cod la zi)
- `f678190` docs: sistem de design documentat + backlog actualizat la stare reala
- `7aca93d` docs: export OpenAPI (openapi.json) pentru concept Lovable
- `3c4284d` docs: brief pentru Lovable (concept vizual portabil in _design.css)
- `79f962c` docs: plan consolidat UI + accesibilitate (critica design + Faza 2)
- `51f5283` docs: lista completa de taskuri ramase (autonom / decizie / blocat extern)
- `fcdca68` log: intrare stepper wizard + transcript
- `15b14bc` log: intrare redesign vizual Cadastru + transcript regenerat
- `bf38927` log: intrare accesibilitate (faza 1) + transcript regenerat

### Diverse
- `89f6afe` docs(slides): redesign 'registru cadastral' + continut la zi
- `976bc33` design: scoate navigarea-text redundanta din wizard (e in bara de sus)
- `9550e6e` design: subsol de document + sageti custom select + rigla alama pe carduri
- `85979a4` design: bara de brand (sigiliu EA + nav) + panou lateral 'Date dosar' (wizard)
- `ca68430` design: cadru-cartus complet (rama + colturi ornamentate + coordonate) pe toate paginile
- `61579b1` a11y(design): bordura controale 3.18:1 (WCAG 1.4.11 non-text contrast)
- `d68ac16` design: antet unificat (busola + rigla de alama) pe toate paginile
- `6a39760` design: portare concept Lovable (pas 2) - sigiliu ANEVAR + busola/antet
- `67b7ff7` design: portare concept Lovable (pas 1) - fundal ghiosuri + grila + decor alama
- `f01aeef` chore: ignora artefacte generate (.coverage) si date sesiune (.claude)
- `4bda3b8` refactor(web): app.py -> routere pe domenii (ADR-001 Optiunea C)
- `0b54217` test(cov): masurare acoperire + prag de regresie fail_under=85
- `fe969c5` refactor(web): extrage helperele JS comune in _helpers.js (dedupe)
- `9176dfe` chore(health): tech-debt Faza 1 + logging (D1/I1/I2/Doc1/C2)
- `86d6a69` docs(log): punte VBP grila->wizard + exe final (orar)
- `4b6df4a` feat(venit): punte grila de chirii -> wizard (preluare VBP automata)
- `d782914` feat(venit): grila de chirii comparabile -> chirie de piata -> abordarea prin venit
- `bef12b0` feat(a11y): aria-describedby pe campuri + fieldset/legend pe grupuri (wizard)
- `ce33861` feat(ui): formatare numerica ro-RO pe rezultate wizard si grila
- `6839f48` log_complet.md: actualizare orara transcript verbatim
- `232206e` docs Track C: ghid evaluator + backlog actualizate la platforma completa (toate tipurile/metodele/scopurile)
- `eef35c0` plan-ui-accesibilitate: marcheaza G1.2-1.5 + G2.3 facute (skip-link, date, autocomplete, tinte, aria-busy)
- `ad718c2` Track B: type=date pe campurile de data + autocomplete pe identitate
- `e654df9` Track B: skip-link pe toate paginile + tinte tactile minime + aria-busy (WCAG)
- `6c303fb` log.md: Faza 7 + PLATFORMA COMPLETA (Fazele 0-7)
- `72b9006` Faza 7: tip proprietate special (profil SPECIAL + optiune wizard)
- `585cded` log.md: Faza 6 (DCF) cablat complet
- `93d3f13` Faza 6: wizard - metoda DCF + campuri flux/rata/rezidual
- `e2ba672` Faza 6: cablare DCF in flux (date_dcf + metoda dcf + sectiune raport)
- `5ba4eb7` log.md: Faza 6 - motor DCF implementat
- `4cbe67d` Faza 6: motor DCF (actualizarea fluxurilor + valoare reziduala)
- `8a02f80` log.md: Faza 5 (Scopuri noi) implementata
- `971812c` Faza 5: wizard - selector scop evaluare (seteaza meta.scop + tip_valoare)
- `3192cf9` Faza 5: profiluri scopuri noi (raportare financiara/asigurare/impozitare/litigii)
- `ce082be` log_complet.md: actualizare orara transcript verbatim
- `15d9617` log.md: Faza 4 (Agricol) implementata
- `4b9994d` Faza 4: wizard - optiune agricol + campuri folosinta/clasa
- `22ba0af` Faza 4: agricol - profil AGRICOL + campuri folosinta/clasa + descriptor raport
- `93366df` log.md: Faza 3 (Industrial) implementata
- `1b2f90d` Faza 3: wizard - optiune industrial + camp inaltime libera
- `e208910` Faza 3: industrial - profil INDUSTRIAL + inaltime_libera + descriptor raport
- `32655b3` log.md: Faza 2 (Comercial/venit) implementata
- `63e2950` Faza 2: wizard - metoda venit + campuri de venit
- `4d900cf` Faza 2: sectiune raport - abordarea prin venit (conditional)
- `439466a` Faza 2: date_venit in flux + venit_result pe ReportContext
- `66c601b` Faza 2: profil COMERCIAL_INCHIRIAT
- `af842c7` plan: Faza 2 comercial/venit (flux venit + raport + wizard)
- `9402eb3` log.md: Faza 1 (Apartament) implementata
- `461070c` Faza 1: wizard — selector tip proprietate + campuri apartament
- `3a79c8b` Faza 1: descriere raport adaptata apartamentului (conditional)
- `70fcf1a` plan Faza 0.5: corecteaza exemplul valideaza_profil (nivel 'alerteaza', nu 'avertisment')
- `20ec704` Faza 1: campuri apartament pe BuildingData + validare etaj<=niveluri
- `9c3cd86` Faza 1: profil APARTAMENT_GARANTARE
- `37c7633` plan: Faza 1 apartament (profil + campuri + raport + wizard)
- `5749c51` log_complet.md: actualizare orara transcript verbatim
- `1d2ef66` log.md: quick-wins UI/a11y + Faza 0.5 (cablare) — pipeline live
- `17f612e` Faza 0.5: construieste_context reconciliaza prin reconcile_profil (echivalent, pipeline live)
- `d51c3be` Faza 0.5: valideaza_profil (consistenta abordari/ponderi)
- `43e3959` plan: Faza 0.5 cablare (assembler -> reconcile_profil + valideaza_profil)
- `d1e6578` plan-ui-accesibilitate: marcheaza G1.1 + Grup 3 (G3.1, G3.2) ca facute
- `1c135a7` UI quick-wins: contrast .hint AA (G1.1) + /result ca certificat (Grup 3)
- `b995040` log_complet.md: actualizare orara transcript verbatim
- `10b9d67` log.md: Faza 0 implementata (subagent-driven) + re-spec post-faza
- `71a6bdc` re-spec post-Faza 0: interfete reale + Faza 0.5 cablare + recomandari review final
- `dd3f54b` Faza 0: reconcile_profil — ponderare degenerata cade pe selectie cu nota (consistent cu reconcile)
- `ba674aa` Faza 0: profil in ReportContext (default casa+teren) + teste de echivalenta
- `d75ab90` Faza 0: sectiuni_pentru_profil filtreaza abordarile dupa profil.abordari_aplicabile
- `6334034` Faza 0: registru de sectiuni de raport pe profil/ghid
- `79e92ee` Faza 0: reconcile_profil — type hints + lookup defensiv + test eroare
- `1cf3815` Faza 0: reconcile_profil (aditiv) + metoda_selectata extinsa cu 'venit'
- `9a4359b` Faza 0: validari intrari venit (procente [0,1], valori >=0) — acopera spec §3
- `0aab901` Faza 0: abordarea prin venit (capitalizare directa) + adaptor
- `dbd9ec4` Faza 0: RezultatAbordare + adaptoare cost/comparatie peste motoarele existente
- `add75bf` Faza 0: ProfilEvaluare + profil predefinit casa+teren
- `b8a3972` plan: proces de executie standing (subagent-driven + re-spec intre faze)
- `9c1aa96` log.md: intrare planuri implementare platforma (Faza 0 + Fazele 1-7)
- `a2df7f6` log_complet.md: actualizare orara transcript verbatim
- `1ef53cf` plan: Faza 0 (TDD detaliat) + Fazele 1-7 (planuri structurate) platforma evaluare
- `b4936c6` log.md: intrari orare (B3 evaluator persistent, critica design+plan UI, plan-master B2)
- `f629af0` log_complet.md: actualizare orara transcript verbatim
- `1eb598b` spec: plan-master platforma evaluare imobiliara (viziune + decompozitie + Faza 0)
- `dd1af9c` wizard: retine identitatea evaluatorului intre sesiuni (B3)
- `8aa6240` decizie: wizard ramane cu navigare libera, fara validare intre pasi
- `a1a775e` log.md: intrare reorganizare bara de sus wizard
- `db16872` log_complet.md: actualizare orara transcript verbatim
- `4a7290c` wizard: separa 'Instrumente' de 'Vizualizare alternativa' in bara de sus
- `f03d868` wizard: stepper numerotat clickabil (inlocuieste bara de progres)
- `0954792` log_complet.md: actualizare orara transcript verbatim
- `387fcfe` design: sistem vizual „Cadastru" pe toate paginile (offline)
- `da41d00` AML: curata import nefolosit (pyflakes clean)

---

## 2026-06-03  _(36 commits)_

### Conformitate ANEVAR/SEV/GEV
- `2f5b433` feat: termeni de referinta conform SEV 101 (16 elemente) + ESG (nou 2025) din textul complet SEV 2025
- `9da093e` feat: conformitate SEV 2025 + checklist GEV 520 in raport (din PDF oficial ANEVAR)

### AML
- `b88e3ea` AML faza 3: generatoare documente .docx
- `56abf46` AML faza 2: indicatori de suspiciune + raportare RTN/RTS
- `c7ed5b7` AML faza 1: motor de risc (scor + categorie + reguli HARD EDD)
- `33611bb` AML faza 0: constante, modele KYC/BR/PEP/risc, incadrare (PFA, audit)

### Audituri
- `b3ff1bf` feat: export urma de audit per dosar (/api/evaluare/{id}/audit.txt) + buton wizard
- `2f98bca` feat: modul audit/ (schelet TDD) - jurnal hash-chained + snapshot + validare incrucisata + export

### Bugfixuri
- `74dd88a` fix: rotunjire la 2 zecimale in raport + faptele AI (fara zecimale lungi)
- `d211d1f` fix: propaga suprafata terenului in rezultatul descoperirii (afisare + API)
- `15b1e33` fix: extrage descrierea completa din __NEXT_DATA__ (storia), nu din HTML-ul randat

### Documentație
- `b200455` docs: log_complet.md - transcript verbatim al sesiunii (generat din .jsonl) + script
- `54000cf` docs: log.md - actualizare orara doar cand exista info noi
- `ff550fe` docs: log.md - jurnal de sesiune (sinteza completa) + actualizare orara
- `36849ff` docs: plan complet modul AML ancorat in Legea 129/2019 + Norme 37/2021 + HCD 58
- `41a5035` docs: indice ANEVAR -> Done in roadmap + module
- `0a4d4cc` docs: instructiuni pentru evaluator (pornire, SmartScreen, AI optional, GDPR, ce produce)
- `c8a940e` docs: ingestie nu mai e in planificate (implementat)
- `cb2c724` docs: audit/ marcat implementat in maparea de module
- `9c191d8` docs: plan master al aplicatiei + model de sisteme actualizat (6 sisteme)
- `5389397` docs: mapare module pe cele 5 sisteme initiale + spec ingestie/ANCPI/audit
- `4ef57a3` docs: spec module AML (129/2019) + BIG + lista de module a aplicatiei
- `dabf96b` docs: roadmap produs informat de cercetarea ANEVAR (SEV 2025, GEV 520, BIG/BIF, AML 129/2019)
- `5258abe` docs: un singur raport demo (Breaza, real) cu evaluator generalizat + cifre rotunjite
- `7be0afe` docs: regenerare raport demo cu cifre rotunjite
- `11df195` docs: raport demo real pe subiect Breaza de Sus (3 comparabile reale extrase)

### Diverse
- `30bdc95` feat: Indicele imobiliar ANEVAR (date publice) - modul + endpoint + buton grila
- `e279442` feat: wiring ingestie in wizard + echivalent LEI in raport + prepopulare grila teren
- `c06c633` feat: modul ingestie/ (schelet TDD) - OCR + extractoare CF/releveu/plan/CPE + VLM injectabil
- `ad26053` feat: descoperire comparabile de TEREN (#9 Next)
- `2bda2a4` feat: Next items - Anexa 3 documente upload + hint Indicele ANEVAR
- `afcecc4` feat: Now items - curs BNR automat, disclaimer comparabile, validare casa Maneciu+Brasov
- `1b70f79` feat: buton 'Raport cu note (demo)' in wizard (Pas 5)
- `5830da1` feat: mod adnotari (note de provenienta) in raport pentru review
- `a24d90b` feat: extragere structurata caracteristici imobiliare (an, material, regim, incalzire)
- `56f2bc2` feat: parser extrage caracteristici structurate storia (an, incalzire, material, stare, camere, etaje)

---

## 2026-06-02  _(18 commits)_

### Conformitate ANEVAR/SEV/GEV
- `0a1f54f` feat: narativ AI pentru sectiunile GBF noi (ipoteze + GEV 520) + ghid per capitol

### Bugfixuri
- `2ec01d0` fix: motor teren in doua etape (tranzactie secvential + proprietate aditiv) + regresie reala
- `bf9c201` fix: eticheta curs valutar mereu EUR/LEI (nu EUR/moneda)

### Documentație
- `1b6be6b` docs: deck de prezentare pentru evaluator (.pptx, 12 slide-uri) + sursa
- `6dbc23f` docs: raport demo (.docx) cu date fictive + script generare
- `6ec5a2b` docs: prezentare pentru evaluator (review) - optimizata pentru NotebookLM

### Diverse
- `692a6a5` feat: incarcare fotografii in wizard -> Anexa foto in raport .docx
- `f1de091` feat: curatare text narativ (elimina citatii web sonar si markdown)
- `4888f7b` feat: motor casa pe pret total in doua etape (validat pe grile reale GBF)
- `1ab1cc2` feat: campuri GBF in wizard (beneficiar, proprietar, data inspectiei, moneda, curs valutar)
- `3847ad9` feat: raport shell GBF complet + grila teren/alocare in .docx + prefill grila din descoperire
- `893b6fd` feat: grila ajustari UI (pagina /grila) + cablare valoare teren in cost + alocare
- `2d11492` Add plan B: grila UI + cablare teren
- `22bc558` feat: motor evaluare teren prin comparatie (engine/land.py) + LandResult + alocare valoare
- `4b7c17b` Add plan A: motor evaluare teren
- `990d46f` Add design spec: evaluare teren prin comparatie + grila de ajustari (ancorat in grilele reale GBF)
- `1c2b246` ux: stare si finisaj afisate ca etichete (Medie/buna, Lux) in tabel, nu ca numere
- `c787e50` ux: explicatie scor ca tabel (criterii x referinta/gasit/d/pondere), formula sub tabel, secundare doar cele identificate

---

## 2026-06-01  _(52 commits)_

### Conformitate ANEVAR/SEV/GEV
- `b6a13c2` feat: validari SEV cablate in /api/evaluare (alerte in UI) + pret/mp in descoperire + rezumat exec per pas wizard

### Bugfixuri
- `631eb51` fix: deschide browserul doar dupa ce serverul e gata (evita ERR_CONNECTION_REFUSED la exe)
- `c6e26d4` fix: extractie LLM robusta - descriere reala (dupa 'Descrierea propriet') + parsare toleranta la cheile sonar (valoare_treapta, secundare la nivel superior)
- `4d70ebf` fix: extrage teren imobiliare (Sup. teren: X mp, format romanesc) + .env langa exe pentru LLM
- `23087d2` fix: parser JSON-LD recursiv (priceSpecification + floorSize scalar) - 100% extractie pe anunturi reale

### Documentație
- `c796c50` docs: tabel metodologie UI inainte de rezultate + conectarea cu modulul de calcul
- `48bda7c` docs: scoring transparent - formula/pondere/cota per atribut + formula exacta langa relevanta
- `6e723a5` docs: adauga metodologia de scoring (dissimilaritate ponderata + tratare nementionat)
- `67cdc44` docs: afiseaza valoarea regasita in anunt pentru TOATE atributele (primare+secundare)
- `b68942d` docs: atribute secundare afiseaza valoarea gasita in anunt (dovada)
- `bd5d649` docs: clarifica ferm - doar cele 5 primare in ranking, secundarele FYI

### Diverse
- `31eb1b3` feat(wizard): adauga Import din URL la Pas 3 (lipsea fata de formularul monolit)
- `cd18e5e` feat: activare Perplexity - PerplexityNarrativeClient + config foloseste PERPLEXITY_API_KEY
- `4fa79f3` ux(wizard): muta atributele de potrivire la Pas 3 (descoperire), clarifica textarea comparabile, buton explicit Genereaza raport la Pas 5
- `0d2d6c0` feat: input atribute secundare in wizard (Pas 3) + afisare rezultate secundare la candidati
- `e4237f5` feat: pret/mp afisat DOAR cand terenul e comparabil (+-40%); extrage suprafata teren (storia terrain_area)
- `e333d58` feat(ui): polish descoperire - badge-uri relevanta colorate, pret/suprafata proeminente, link clar
- `84ca8cf` feat: suport storia.ro (suprafata din __NEXT_DATA__ area) + fallback cautare pe judet
- `c263f28` docs(ui): clarifica hint zona - numele cu diacritice apar in raport, slug-ul auto
- `49e78c4` feat: wizard devine pagina principala (/); formular monolit mutat la /formular
- `45a833f` feat: suprafata construita a casei ca atribut de potrivire (pondere 5) + hint-uri câmpuri wizard
- `fad7810` feat(ui): stare+finisaj ca dropdown cu etichete text; explica normarea incalzire (_)
- `76aa346` feat: pas verificare adresa pentru raport (adauga diacritice inainte de generare)
- `162552f` docs(ui): explica regulile de normalizare slug (fara diacritice) in wizard
- `3d5b9b2` build: include data/ (liste localitati) in executabil
- `b80cddd` feat: Pas 1 wizard cu dropdown judet+localitate (slug exact) + rest adresa free-text
- `69b4119` feat: endpoint GET /api/localitati
- `95dc40c` feat: liste judete+localitati statice (slugify) + script build dataset
- `d1f2e9e` Add spec+plan: dropdown judet+localitate in wizard (slug exact portaluri)
- `30eff10` feat: pagina wizard 5 pasi (stare in browser + localStorage)
- `86724d1` feat: endpoint POST /api/zona (adresa -> judet+localitate)
- `05500bf` feat: extragere judet+localitate din adresa (LLM injectabil + fallback)
- `2f5f366` Add plan: wizard pas-cu-pas (zona din adresa + pagina 5 pasi)
- `921b29f` Add design spec: wizard pas-cu-pas pornind de la o adresa
- `e2b1815` feat: endpoint /api/descopera + pagina UI (metodologie inainte de candidati)
- `0c5b9b7` feat: orchestrator descoperire (search->scrape->parse->extract->score->rank)
- `23ae984` feat: metodologie() pentru tabelul de scoring din UI
- `2c30943` feat: extractor atribute LLM (injectabil, JSON validat, fallback)
- `f776a78` feat: modele rezultate descoperire (extractie + candidat scorat)
- `d05da30` feat: scraper cautare portal (build URL + extrage URL-uri anunturi)
- `424ee3a` feat: parser intarit (fallback __NEXT_DATA__ / og / regex titlu)
- `1b9e89f` feat: motor scoring descoperire (dissimilaritate ponderata + explicatie auto-continuta)
- `3656c60` feat: modele profil descoperire (subiect, candidat, breakdown scor)
- `f1ffdd0` Add plan: descoperire comparabile partea 2 (extractie LLM + orchestrator + UI)
- `78c6a2f` Add plan: descoperire comparabile nucleu (scoring auto-explicativ + scraping)
- `9bbac4a` Add design spec: descoperire comparabile (scraping direct + LLM extractie)
- `a740cf6` feat: text explicativ langa fiecare camp din formular (rol + logica)
- `6ee1885` feat: formular cu selector metoda + comparabile + buton Import din URL
- `122d510` feat: endpoint POST /api/import-url (parsare anunt -> campuri comparabil)
- `4b0f4bf` feat: parser anunt URL (schema.org JSON-LD) -> Comparable
- `c3aa271` chore: dependinte scraping (requests, beautifulsoup4)
- `685a38b` Add plan: import comparabile prin URL (scraping direct)

---

## 2026-05-31  _(29 commits)_

### Conformitate ANEVAR/SEV/GEV
- `7df22a9` feat: generator raport .docx SEV 103 (capitole + tabele grila/cost)

### Diverse
- `ed883b0` feat: impachetare PyInstaller (.exe cu dublu-click) + start.bat
- `8b16057` feat: pagina formular + rezultat + entry-point pornire server local
- `caacda6` feat: API FastAPI (creare evaluare, citire, download .docx)
- `aec5300` feat: assembler (input -> motoare -> ReportContext)
- `1957f36` feat: storage SQLite (save/load/list dosare)
- `f13c1fc` feat: config (.env + Settings) si activarea clientului AI
- `766293b` chore: dependinte web (fastapi/uvicorn/jinja2) + .gitignore
- `e722533` Add implementation plan 3/4: local web app (manual entry)
- `f56f70c` test: smoke end-to-end calcul -> raport .docx
- `f12cdb8` feat: narativ AI (client Claude injectabil, anonimizare, fallback)
- `99d8849` feat: anonimizare date personale (mask/unmask) pentru GDPR
- `e04c4e0` feat: ReportContext (agregat de intrare pentru raport)
- `9a85895` feat: modele meta lucrare + sectiune narativa
- `bd77a63` chore: adauga python-docx si anthropic pentru raport+AI
- `c43645e` Add implementation plan 2/3: report .docx + AI narrative
- `b4b919b` feat: loops de validare (proprietate, comparabile, depreciere)
- `4998dbd` feat: reconciliere piata vs cost (selectie + ponderare + fallback)
- `9b1eb5d` feat: Market Engine (grila de comparatie, ajustari ierarhice, selectie)
- `1ef904e` refactor: round Vcp to report convention + depreciation range guard + edge tests
- `1350dc6` feat: Cost Engine (CIB segregat, Vcp, depreciere, CIN) cu regresie GBF
- `1f2fa5c` feat: modele rezultate (cost, piata, reconciliere)
- `2e9885c` feat: modele comparabile + ajustari (piata si teren)
- `4c3dbf4` feat: modele proprietate (teren, constructie, elemente cost segregat)
- `6786735` feat: helper monetar Decimal (to_money, round_lei, pct)
- `51534fe` chore: scaffold proiect evaluare-anevar + pytest
- `656c688` Add implementation plan 1/3: core valuation engine (TDD)
- `0243ee3` Revise MVP scope: house + land with cost approach (CIN)
- `5fe68e5` Add design spec for ANEVAR valuation agent MVP

---
