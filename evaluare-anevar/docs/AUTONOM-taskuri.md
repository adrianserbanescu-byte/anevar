# 🤖 Listă de taskuri autonome (citită + actualizată la fiecare loop)

> **Protocol loop (instrucțiune Adi):** la fiecare job de loop → (1) actualizez ÎNTÂI lista de mai jos,
> (2) aleg și rezolv tot ce pot face singur (fără input de la Adi), (3) la următorul loop reiau.
> Ce e blocat pe Adi → [`BLOCAT-pe-Adi.md`](BLOCAT-pe-Adi.md) (NU le ating). Actualizat: 2026-06-06.

## 🚨 P0 — RECUPERARE UI NOU (prioritate maximă; precede agenda specială de mai jos)
> Owner șocat de regresiile UI nou (audit complet în `docs/audit-ui-nou/`). Backend-ul EXISTĂ — totul = frontend.
> **FĂCUT (commit-uri aab8d20→6237772):** #1 „?" ✅ · #3 afordanță sub-tab ✅ · #4 curs EUR ✅ · #5 flux identitate ✅ ·
> #6 comentariu fals ✅ · **#7 câmpuri dinamice per tip ✅** · **#8 descoperire inline ✅** · **#9 AML in-place ✅** ·
> #9 GDPR in-place ✅ · #9 Audit in-place ✅ · **#10 opțiune adnotări ✅** · **#14 Anexe sub-tab + upload ✅**.
> **73 e2e + 495 teste.** Plus (verificat VIZUAL cu Playwright): butoane finalul tab Raport ✅ · 3 butoane Generează ✅ ·
> alerte validare la calcul ✅ · import URL ✅ · atribute secundare ✅. **Inventar complet: `audit-ui-nou/5-inventar-controale-diff.md`.**
> RĂMAS din inventar (~118 controale). FĂCUTE în rularea continuă (commit-uri 8f52a70→prezent, 87 e2e + 495 teste):
1. [x] **Grile reale** inline cu ajustări pe ETAPE + alertă prudențială 25% GEV 520: **CASĂ + TEREN + CHIRII ✅**
       (+ BUG FIX: cheia `adjustments` — grilele ignorau ajustările; e2e dovedește acum aplicarea).
3. [x] **Descoperă TERENURI** (`/api/descopera-teren`) — comutator construcții/terenuri în descoperire ✅.
4. [x] **Județ/localitate = select din `/api/localitati`** (diacritice + slug + dependent + „altă") ✅ · câmp **proprietar** ✅.
6. [x] **Punte VBP grila chirii → metoda Venit** (buton „Preia VBP") ✅.
> RĂMAS:
2. [x] **Ingestie PDF** (doc-tip + `/api/ingestie`): pre-completare din extras CF/releveu/plan/CPE ✅.
5. [x] **Coadă „anunțuri din extensia browser"** ✅ (`/api/anunturi-importate`) + **Backup dosare .zip** ✅ (`/api/backup-dosare.zip`).
> 🎉 **BACKLOG-UL DE PARITATE UI = CURĂȚAT.** Toate cele ~26 controale lipsă + 30 parțiale din inventar — rezolvate
> sau acoperite. Rămâne doar muncă de finețe (a11y fină, UX-copy) + deciziile pe Adi (BLOCAT-pe-Adi.md).

## ✅ PRIMUL LOOP (SPECIAL) — RULAT (2026-06-06 ~11:36, commit b347284)
1. [x] **SCOP CORECTAT — matrice conformitate tip×scop** → `conformitate/E-matrice-tip-scop.md` (25 combinații). ✅
2. [x] **Re-analiză LEGE 129 + NORME ONPCSB** → `conformitate/F-lege-norme-aml.md` (praguri OK; 3000€ infirmat; goluri→BLOCAT §H). ✅
3. [x] **3 ADR-uri formale** → `docs/adr/ADR-002/003/004` (SQLite→foldere, lock-identitate, AI gateway). ✅
> Discrepanțele/golurile escaladate în `BLOCAT-pe-Adi.md` §G (matrice, bucket B) + §H (AML, bucket C) + §I (ADR triggers).
> De aici încolo: loops normale la 1h cu promptul normal. **Top inline rămas = grilele reale (vezi P0 sus).**


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
