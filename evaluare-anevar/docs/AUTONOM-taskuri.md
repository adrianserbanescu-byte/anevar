# 🤖 Listă de taskuri autonome (citită + actualizată la fiecare loop)

> **Protocol loop (instrucțiune Adi):** la fiecare job de loop → (1) actualizez ÎNTÂI lista de mai jos,
> (2) aleg și rezolv tot ce pot face singur (fără input de la Adi), (3) la următorul loop reiau.
> Ce e blocat pe Adi → [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) (NU le ating). Actualizat: 2026-06-06.

## 🚨 P0 — RECUPERARE UI NOU (prioritate maximă; precede agenda specială de mai jos)
> Owner șocat de regresiile UI nou (audit complet în `docs/audit-ui-nou/`). Backend-ul EXISTĂ — totul = frontend.
> **Făcut (commit aab8d20):** #1 „?" re-adăugat · #3 sub-tab-uri cu afordanță · #4 curs EUR · #6 comentariu fals reparat.
> **De făcut (port din wizard/descoperire/grila — zero backend nou, e2e acoperă):**
1. [ ] **#7 CÂMPURI DINAMICE per tip proprietate** (cel mai critic) — port `aplicaTip` + grupurile condiționate
       (ap-fields/agr-fields/grup-teren/grup-constructie + etaj/cotă/înălțime/categorie folosință/clasă) din wizard.html.
2. [ ] **#8 MODUL DESCOPERIRE inline în Comparabile** — formular căutare (județ/localitate/atribute) → tabel rezultate
       → bifare → import în grilă + import URL/extensie (reutilizează /api/descopera, /api/import-*). „AI TĂIAT căutarea".
3. [ ] **#14 ANEXE = sub-tab al Raportului ÎNTRE Calcul și Generează** + upload foto/scanuri → `photos`/`documente`
       în asambleaza() (backend `_adauga_anexe` gata; textul „comercial" e fals).
4. [ ] **#9 AML / GDPR / Audit in-place** în sub-tab-uri (port formulare din aml.html; +endpoint `/api/dosar/{uid}/audit.txt`).
5. [ ] **#10 Opțiuni Generează** (adnotări/demo) + #5 flux identitate/denumire folder corect (validare la creare).
6. [ ] Grilele reale (teren/casă/chirii) cu ajustări pe etape + alerte prudențiale 25%/15% (control GEV 520 pierdut).
> La fiecare: teste + e2e + commit. Rebuild exe după un batch.

## 🌟 PRIMUL LOOP (SPECIAL, ~50 min de la 10:43) — DUPĂ recuperarea UI de mai sus; apoi loops normale la 1h
> Doar primul loop e special; după el, fiecare loop la 1h cu promptul normal (re-planific + rezolv ce pot singur).
1. [ ] **SCOP CORECTAT — re-rulez conformitatea pe ÎNTREAGA matrice tip×scop** (NU doar casă+teren+garantare).
       Toate tipurile (casă, apartament, industrial, agricol, special) × scopuri (garantare, raportare financiară,
       asigurare, impozitare, litigii) — vezi `profil.py` (9 profile) + `assembler.rezolva_profil`. Pentru fiecare
       combinație: ce ghid GEV se aplică, ce abordări sunt obligatorii, ce cere standardul vs. ce facem. Update
       `docs/conformitate/` cu o matrice tip×scop completă.
2. [ ] **Re-analiză `md files/LEGE nr.md` + `md files/NORME din 2 martie 2021de aplicare a prevederilor.md`** —
       verific diferențe de conformitate față de ce avem (probabil AML/Legea 129 + Norme ONPCSB; corelez cu modulul `aml/`).
3. [ ] **ADR-uri formale** (cerere Adi, skill `engineering:architecture`): migrarea SQLite→foldere; modelul de
       lock-identitate; AI gateway-ul. + alte decizii arhitecturale dacă le consider potrivite (ex. stocare anexe).
4. [ ] Continuă taskurile inline de mai jos (conformitate Bucket A confirmate, council „de preluat", datorie tehnică).


## ✅ COUNCIL — TOATE rulate (2026-06-06, după reconectarea MCP)
1. [x] **Council Q2** (topics 3,4,6) — foldat în `9-topicuri-decizie.md`. ✅
2. [x] **Council Q3** (topics 2,8,9) — foldat în `9-topicuri-decizie.md`. ✅
3. [x] **Council pe planul UI nou** — comparat cu al meu în `council-plan-UI-nou.md`; ce adopt notat acolo §3. ✅

## ☐ DE PREIAT din council (autonom, fără decizie de produs)
- [x] **OLX downgrade scor** (suprafață lipsă → relevanță −30 + avertisment în explicație). ✅ +test
- [ ] Hash SHA256 al folderului dosarului la asumare — **gated de declanșatorul de lock (#10, decizia ta)**.
- [ ] Fișier `.lock` per dosar + read-only la deschidere concurentă — cuplat cu fluxul de lock.
- [ ] Descoperire ca split-screen în Comparabile (caută→bifează→importă) + fallback manual — feature mai mare.

<!-- arhivat (cererea verbatim a council-ului adițional, păstrată pt referință):
3. **Council ADIȚIONAL — „planul lor pentru noul UI"** (cerere Adi, verbatim mai jos):
       „rulează încă un llm-council audit în care ceri planul lor pentru noul UI și cum ar trebui să îl
       definim. Poți să le dai contextul de până acum discutat, dar cere-le să îți facă planul lor INDIVIDUAL.
       În afară de contextul exhaustiv asupra proiectului, dă-le toate informațiile despre: **fișiere exportate**,
       **descoperire și cum funcționează + AI**, **vechiul UI**, **toate feature-urile aplicației** și **obiectivele
       setate de noi**. Cere-le planul și detalierea lor, **riscuri și dependențe**. Compară output-ul fiecăruia
       cu al meu ȘI output-ul agregat al lor vs. opinia mea. Preia ce consider potrivit în planul meu de dezvoltare."
       → `include_member_responses=true`; rezultat în `docs/council-plan-UI-nou.md` + integrare în planul de dezvoltare.
-->

## ✅ Făcut în acest loop
- [x] **Analiza mea pe toate 9 topicuri** + council Q1 → `9-topicuri-decizie.md`.
- [x] **Widget feedback** verificat: lipsea din tot UI-ul nou (era doar în `_topbar`) → mutat în `_footer` comun
      (apare pe toate paginile, vechi+nou). +test. Restul linkurilor neafectate.
- [x] **Fișier de sinteză a nopții** → `00-SINTEZA-NOAPTE-2026-06-06.md`.
- [x] Polish auto-safe: badge „recomandat" verde + aria-hidden emoji (index).
- [x] Listă autonomă creată (acest fișier) + checkpoint durabil la restart.

## ☐ Datorie tehnică autonomă (din auditul tehnic; le pot face fără decizie de produs)
- [ ] `listeaza()` — cache pe mtime via `_index.json` (evită rescanarea N fișiere la fiecare /incepe).
- [ ] Îngustez `except Exception` prea largi + logging (docx_dosar, dosare_fs.diff).
- [x] Retenție versiuni `.docx` (păstrează ultimele 10, nume cu microsecunde). ✅
- [ ] Nume fișiere temporare unice (uid+timestamp) în `gettempdir()` (evită coliziuni).
- [x] Avertisment cloud-sync — deja acoperit (DB + `date/dosare` sub același `baza`). N/A.

## ☐ Paritate UI nou (feature, additiv — wiring de capacitate existentă, nu decizie de produs)
- [x] **Grila de teren** (land_comparables) în sub-tab Comparabile. ✅
- [x] **Venit (capitalizare) + DCF** (date_venit/date_dcf, grupuri afișate la metodă). ✅
- [ ] Anexă foto / scanuri — **GATED comercial** (decizia ta; nu îl fac autonom).
> Paritate rămasă față de wizard: doar anexa foto/documente (gated comercial). Restul motorului = acoperit în UI nou.

## ☐ Securitate / temp
- [x] Import .docx în director temporar unic (anti-coliziune, păstrează numele pt parser). ✅

## ⚙ Rebuild exe — în curs (include land grid + venit/DCF + retenție + temp safety + feedback peste tot).

## ☐ Acoperire teste (țintă ≥90%, urc golurile cunoscute)
- [ ] `report/generator` (~88%) — secțiuni rare (lichidare/DCF).
- [ ] Ramuri de eroare neacoperite în `documente.py` (deja 9 teste; verific liniile lipsă).

## ☐ Polish UI auto-safe (din audituri, fără decizie de produs)
- [ ] Badge „recomandat" pe index → verde (`b-high`) în loc de chihlimbar.
- [ ] Câteva mesaje de eroare cu ghidaj (UX-copy: „Generarea a eșuat" → ce + cum repar).
- [ ] `aria-hidden` pe emoji din `index.html`/documente unde lipsește.

## ✅ Rezolvate în această sesiune de noapte (rezumat — detalii în sinteza nopții)
- Noul UI „output-first" complet (cont→ÎNCEPE→workspace) + import .docx + cont „Adi S" + 4 dosare exemplu.
- Index de alegere UI + pagină Documente (convertor MD→HTML propriu) + cross-linkuri antet/subsol.
- Audit import portaluri (live, 2 fixuri) + 5 audituri (a11y/UX/design/tehnic/cod) → 8 fixuri auto-safe.
- Checkpoint de asumare (om în buclă) în Generează. Calcul fără persistență SQLite (rând orfan reparat).
- Pachet lansare: sinteză + plan-lansare + strategie + evaluare juridică RO + 5 documente DRAFT.
- 2× LLM council (review #1 stare veche + #2 stare curentă pe decizia de lansare).
- 487 teste + 57 e2e, exe 50 MB, tot pe GitHub.
