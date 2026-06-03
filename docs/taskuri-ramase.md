# Taskuri rămase — Asistent de evaluare ANEVAR

**Actualizat:** 2026-06-04. Sursă: `roadmap-anevar.md`, `plan-accesibilitate.md`, spec-urile de module,
`log.md`. Legendă efort: **S** mic · **M** mediu · **L** mare.

> Ce e DEJA făcut (nu mai apare aici): motoare cost/teren/casă (validate pe dosare reale), reconciliere,
> raport `.docx` SEV 2025 + GEV 520 + ESG, narativ AI (GDPR), descoperire comparabile (casă+teren),
> wizard 5 pași + stepper, curs BNR, Indicele ANEVAR, ingestie PDF, audit, **modul AML complet**,
> redesign vizual „Cadastru", accesibilitate Faza 1. Exe onefile funcțional, 280 teste verzi.

---

## A. Pot face AUTONOM (fără acces extern, fără decizii blocante)

### A1. Accesibilitate — Faza 2 (din `plan-accesibilitate.md`)
- [ ] **A1.1** `<form>` real + submit pe Enter în wizard/grilă/AML (acum butoanele sunt `type="button"`). **S**
- [ ] **A1.2** `type="date"` pe câmpurile de dată (data_evaluarii, data_raportului, data_inspectiei). **S**
- [ ] **A1.3** Erori legate de câmp prin `aria-describedby` (acum mesajele sunt într-o regiune separată). **S-M**
- [ ] **A1.4** Skip-link „Sari la conținut" → `<main>` pe fiecare pagină. **S**
- [ ] **A1.5** `autocomplete` pe câmpurile de identitate (evaluator, client, proprietar). **S**
- [ ] **A1.6** Țintă tactilă ≥24px pentru butoanele mici („șterge" upload, „➕ grilă"). **S**
- [ ] **A1.7** `aria-busy="true"` pe regiunile care fac fetch (descoperire, calcul, curs BNR). **S**
- [ ] **A1.8** `<fieldset>`/`<legend>` pentru grupuri de câmpuri în wizard (ca în `/aml`). **S**
- [x] `prefers-reduced-motion` + `:focus-visible` explicit — **deja făcute** la redesign.

### A2. UI / lustruire
- [ ] **A2.1** Pagina `/result` ca „**certificat**" — layout îngrijit (valoare hero, echivalent LEI, client,
      metodă, link descărcare `.docx`), nu varianta minimală de acum. **S-M**
- [ ] **A2.2** Trecere de consistență vizuală pe tabelele dinamice din `descoperire`/`grilă` (badge-uri,
      spațiere) după redesign. **S**

### A3. Metodologic / cod
- [ ] **A3.1** Verifică alinierea **IVS vs SEV 2025** în raport (IVS 103 Abordări, 105 Modele, 106 Raportare,
      400 Drepturi imobiliare) — confirmă că terminologia e la zi. **S**
- [ ] **A3.2** Testare reală cu **cititor de ecran (NVDA)** + zoom 200% / 320px (reflow). *(proces, mediu local)* **M**

---

## B. Necesită INPUT / DECIZIE de la tine

- [ ] **B1. Export PDF in-app** — vrei convertor încorporat (dependență externă: `docx2pdf`/LibreOffice,
      crește exe-ul) sau rămâne „Word → Salvează ca PDF" (documentat acum)? *(roadmap Now #6)*
- [ ] **B2. Suport multi-tip proprietate** (apartament, spațiu comercial) dincolo de casă+teren — scope mare;
      îl vrei? *(roadmap Later #16)* **L**
- [ ] **B3. Date evaluator implicite** — pre-completez peste tot „ing. Gabriela Frătilă, legitimația 14288"
      (acum doar în raport)? **S**
- [ ] **B4. AML — validarea juridică finală** a textelor generate (norme interne, decizii, RTS/RTN): cine o face?
      *(necesar înainte de uz real)*

---

## C. BLOCAT EXTERN (terți / plătit / acces ANEVAR-ANCPI)

- [ ] **C1. Catalog IROVAL** — costuri unitare €/mp pe categorii pentru CIN (acces/plată). *(roadmap #10)* **M**
- [ ] **C2. Integrare BIG** (Baza Imobiliară de Garanții) ca sursă primară de comparabile — acces membru
      ANEVAR / API → modul `big/` (spec scrisă). *(roadmap #13)* **L**
- [ ] **C3. Integrare ANCPI** (carte funciară / cadastru online) → modul `ancpi/` (spec scrisă). **L**
- [ ] **C4. Contribuție automată la BIG/BIF** din rapoartele generate — depinde de specificațiile ANEVAR.
      *(roadmap #15)* **L**
- [ ] **C5. exe semnat** (certificat code-signing) — elimină avertismentul SmartScreen. *(roadmap #12)* **M**
- [ ] **C6. AML — liste live** (sancțiuni UE/ONU consolidate, funcții PEP-ANI, țări necooperante/risc înalt CE)
      — surse oficiale, reîmprospătate manual (acum placeholder injectabil în `aml/data/liste.json`).
- [ ] **C7. AML — transmiterea electronică** la ONPCSB (rapoarte.onpcsb.ro) — o face evaluatorul; aplicația
      doar pregătește conținutul.
- [ ] **C8. Testare extracție LLM pe text real** de anunț (necesită cheie AI activă; restul descoperirii e
      validat 100% pe fixturi reale).

---

## Decizii deja luate (NU se reintroduc)
- **Wizard — navigare liberă, FĂRĂ validare între pași** (decizie user, 2026-06-04).
- **Om-în-buclă** (AI propune, evaluatorul decide) — răspundere profesională + GDPR.
- **Cheia Perplexity NU se distribuie** cu exe-ul.

---

## Recomandare de ordine (dacă mergem autonom)
1. **A1 (accesibilitate Faza 2)** — mic, sigur, lustruiește experiența. 1 trecere.
2. **A2.1 (`/result` ca certificat)** — vizibil, rapid.
3. **A3.1 (verificare IVS/SEV)** — conformitate.
4. Apoi B1/B3 (decizii mici) și, când ai acces/decizii, blocul **C**.
