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
- [x] ✅ **Hash de integritate la asumare** — implementat per versiune `.docx` (`verifica_integritate`, tamper-evidence în audit). Declanșator #10 decis (hibrid+upload).
- [x] ✅ **Fișier `.lock` per dosar** — concurență (token + TTL 90s, avertisment soft) + curățare orfane la pornire. **ADR-003 ÎNCHIS** (rămâne doar #12, decizia ta de produs).
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
- [x] `listeaza()` — **cache pe `mtime_ns`** (`_cache_antete.json`) — dosar neschimbat nu se recitește/reparsează la fiecare /incepe; cache derivat, reconstruire transparentă. ✅ +test (commit 18bbe16).
- [x] Îngustez `except Exception` prea largi + logging — VERIFICAT (2026-06-07): `dosare_fs.py` deja
      înguste (ValueError/OSError/KeyError), `docx_dosar.py` fără except; cele din `curent.py` traduc curat
      în HTTP 4xx (nu eșec silențios). N/A — deja rezolvat. ✅
- [x] Retenție versiuni `.docx` (păstrează ultimele 10, nume cu microsecunde). ✅
- [x] Nume fișiere temporare unice (token uuid) la generarea raportului (`curent.py`: `raport_{uid}_{tok}.docx/.zip`)
      — evită coliziuni la generări concurente; curățarea PII (background task) păstrată. ✅ (2026-06-07)
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

## 🔧 Audit skill-uri (2026-06-07) — recomandări de la 6 skill-uri rulate
> Detalii complete în [`audit-skills-2026-06-07.md`](audit-skills-2026-06-07.md).
> Skill-uri rulate: dependency-audit, find-dead-code, improve-logging, changelog,
> security-review, find-breaking-rest-api. Două decizii pe Adi → `BLOCAT-pe-Adi.md` §J.

### 🚨 P0 — Securitate (vulnerabilități cu CVE active)
- [ ] **Upgrade `urllib3 2.6.3 → 2.7.0`** în `evaluare-anevar/requirements.lock` (PYSEC-2026-141 + PYSEC-2026-142, High).
- [ ] **Upgrade `idna 3.13 → 3.15+`** (CVE-2026-45409 — bypass al fix-ului CVE-2024-3651, Moderate).
- [ ] Rulează `pytest` + smoke-test exe după upgrade ca să prinzi regresii (atenție la Pillow-style packaging breakage).

### P1 — Logging coverage (8% acum, țintă: ≥50% pe `engine/` + `web/routers/`)
- [ ] **Adaugă `log = logging.getLogger(__name__)` la 5 routere mute:** `web/routers/{aml,curent,evaluare,descoperire,grile}.py`.
      Loghează: startup, fiecare endpoint pe entry/exit (debug), erorile 4xx/5xx (warning/error).
- [ ] **Adaugă logging la modulul `engine/`** (`abordari`, `chirie`, `reconciliation`, `validation`, `venit`) —
      flux: input → coeficienți → rezultat. Critic pentru audit ANEVAR + reproducibilitate.
- [ ] **Adaugă logging la `audit/raport_audit.py`** — ironic: modulul de audit nu emite log.
- [x] **Adaugă logging la `report/generator.py`** — DONE pe `sesiune-b` (commit-uri ba3f14e/7a19213, Sesiunea B):
      logger dedicat + `log.warning` la inserarea Anexa 2/3 (foto/scanuri care dispăreau TĂCUT din raport) +
      `log.debug` pe formatări (`_fmt/_b2/_pct`) + `log.info` la generare (fără PII). +test caplog. ⏳ pending merge de A.
- [ ] **Fix silent failures (40 except blocks fără log+raise):**
  - `importers/url_parser.py` liniile 55, 69, 98, 140, 158, 304, 396, 402 — toate `return None`/`False` la 8 except. Adaugă `log.warning("parse failed for %s: %s", url, e)`.
  - `discovery/extractor.py` liniile 48, 65, 168 — `return None` la fetch eșuat.
  - `dosare_fs.py` liniile 79, 138, 158 — `dosar.json` corupt în tăcere.
  - `indice_anevar.py:33` — `return {}` în tăcere.
  - **`zona.py:47` — `pass` în except (anti-pattern declarat) → `log.debug("zona necunoscută: %s", e)`.**
  - `cont.py:28`, `ai/narrative.py:102+110` — fallback silent → `log.debug(...)`.

### P2 — Cod mort (verifică și șterge după confirmare)
- [ ] `engine/reconciliation.py:13 reconcile` — verifică în tot src/ și teste; dacă orfan, șterge.
- [ ] `engine/validation.py:90 valideaza_profil` — idem.
- [ ] `engine/chirie.py:85 date_venit_din_chirie` — idem.
- [ ] `money.py:14 round_lei`, `money.py:19 pct` — utilități neapelate (poate erau pentru raport vechi).
- [ ] `localitati.py:13 slugify` — verifică (s-ar putea să fie folosit la generarea slug-urilor).
- [ ] `report/sectiuni.py:35 sectiuni_pentru_profil` — router-by-profile mort?
- [ ] `dosare_fs.py:190 importa_folder` — endpoint legacy import folder (înainte de UI nou).
- [ ] `importers/url_parser.py:372 to_comparable` — verifică (poate apelat via getattr).

### P2 — Securitate defensivă (low risk, fără downside)
- [ ] Adaugă regex Pydantic pe `{uid}` path params: `uid: str = Field(..., regex=r"^[a-f0-9-]{36}$")` în
      toate handlers din `web/routers/curent.py` și `evaluare.py`. Defense-in-depth: zero downside.
- [ ] **Audit defensiv `requests` direct:** verifică dacă `curs_bnr.py:18` și `ai/narrative.py:230` ar putea
      cândva primi URL din input utilizator. Acum sunt statice (BNR XML + endpoint Anthropic). Documentează în cod.

### P3 — Dependențe outdated fără CVE (programat, după pachet de teste verde)
- [ ] Upgrade lot mic la sfârșit de iterație: `anthropic 0.105→0.107`, `uvicorn 0.48→0.49`,
      `pydantic-core 2.46→2.47`, `click`, `pytest-cov`, `requests` (sincronizat cu urllib3), `lxml`,
      `ruff`, `soupsieve`, `certifi`.

### P3 — Changelog
- [x] **`CHANGELOG.md` generat** la rădăcina proiectului (33 KB, 499 linii) — vezi commit pending.
- [ ] Commit-ează `CHANGELOG.md`: `git add CHANGELOG.md && git commit -m "docs: changelog generat din git history (skill changelog@easier-life-skills)"`.

### P3 — Deprecation telemetry (pregătire pentru retragere UI vechi)
- [ ] **Când Adi confirmă §D.18** (retragerea UI vechi): adaugă header `Deprecation: true` + `Sunset: <data>`
      (RFC 8594) pe toate endpoint-urile `/api/evaluare/...` și paginile vechi. Telemetria ușoară: log fiecare hit.

## ✅ Rezolvate în această sesiune de noapte (rezumat — detalii în sinteza nopții)
- Noul UI „output-first" complet (cont→ÎNCEPE→workspace) + import .docx + cont „Adi S" + 4 dosare exemplu.
- Index de alegere UI + pagină Documente (convertor MD→HTML propriu) + cross-linkuri antet/subsol.
- Audit import portaluri (live, 2 fixuri) + 5 audituri (a11y/UX/design/tehnic/cod) → 8 fixuri auto-safe.
- Checkpoint de asumare (om în buclă) în Generează. Calcul fără persistență SQLite (rând orfan reparat).
- Pachet lansare: sinteză + plan-lansare + strategie + evaluare juridică RO + 5 documente DRAFT.
- 2× LLM council (review #1 stare veche + #2 stare curentă pe decizia de lansare).
- 487 teste + 57 e2e, exe 50 MB, tot pe GitHub.
