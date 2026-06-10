# Triaj centralizat audituri — single source of truth (menținut de A)

Scop: **nimic nu scapă.** A centralizează toate findings-urile (runde 1–2–3 + descoperire) de la A/B/C/D/E, decide owner-ul + integrează tot pe master. A = punct central, decizie + integrator unic (mandat Adi). Actualizat la fiecare buclă.

Legendă: ✅ rezolvat+comis · ▶ în lucru A · 📨 dispatched (lane, GO implementare pe branch → A integrează) · ⏸️ deferat (pre-launch — notat) · ❌ false-positive

---

## ✅ REZOLVAT de A pe master (8 fix-uri + 2 integrări)
| Finding | Commit |
|---|---|
| PyMuPDF AGPL → pypdf | `382142b` |
| SSRF redirect re-validare | `d21d6a1` |
| suprafață/preț=0 → 422 (`gt=0`) | `7f506eb` |
| Security headers CSP/nosniff/X-Frame/Referrer/Permissions | `eae9334` |
| GH-Actions v5 + `la-anexe` mort | `9634937` |
| `beneficiar`→AI anonimizat | `d5c28a0` |
| 403-logging host/CSRF | `0e14b23` |
| Audit clock UTC (jurnal, imun DST) | `dc3b8b0` |
| **Integrare B**: chirii M2 + filtru localitate diacritice (sar duplicatele suprafață/SSRF) | `cc31fbf`,`ca77f83` |
| **Integrare C**: M2 UI (alertă pe TOATE mediatele — fix integritate B) | `007c19e` |
| **Integrare docs** E (GEV520/SEV2025/PyMuPDF/SRI) + D (strategie-testare) | `8cd3715`,`bc360ae` |

## ✅ RUNDA 4 — integrat din fleet (discovery dispatch)
| Livrabil | Sursă | Commit |
|---|---|---|
| pypdf 5.9.0→6.13.1 (5 CVE prinse de gate-ul CI) + reparat `lock.py` ROOTS | D-gate/A | `e8f5f5c` |
| GEV 520 #1 — BIG condiționat ANAF/creditor | B | `427c1d6` |
| Job securitate CI (pip-audit + bandit + pre-commit) | D | `ad6ce37` |
| Build reproducible (SOURCE_DATE_EPOCH/PYTHONHASHSEED + smoke-offline) | D | `3f81971` |
| `# nosec` B404/B603 pdf.py (subprocess soffice sigur) | B+SAST | `36f1276` |
| docs E SEV2025-general (SEV 100/101/102/106/450) | E | `19bdf2d` |
| SAST profund cross-file (uid→path, URL→SSRF, scraped→AI) | A | 0 findings noi |
| D fuzz-parsere (Hypothesis pe pypdf/docx/BS4) + fix importorskip CI-safe | D+A | `24768a3`,`fe05140` |
| D a11y-axe (axe-core 12 pagini, 0 critice) | D | `61daf76` |
| B cost.py rotunjire unică (Dfn pe vcp exact, fără efect prag) | B | `adb0547` |
| B rotunjire grilă + gardă preț negativ (versiune curată, fără regresie) | B | `6e9e1b3` |
| B property-based Hypothesis pe motor (5 invarianți) + hypothesis în lock | B+A | `fbf5504` |
| D differential-review pe batch = **0 regresii** | D | verificat |

**Decizii Adi:** venit ponderat = **(b) alertă transparentă** (→B implementează); GDPR lifecycle (retenție/DSAR/ștergere completă) = **deferat pre-launch** (cere politică de retenție = decizia Adi).

**B re-audit:** lane motor CONFIRMAT curat (pip-audit 0, ruff-S 0, vulture 0). **Build bit-identic** pe Windows = imposibil (PE timestamps) → SHA256-artefact ca integritate (deferat).

## 🔴 RUNDA 5 — re-audit ADVERSARIAL pe master integrat (Adi sceptic: „e un cacat")
**B (motor/numeric):** integrarea SOLIDĂ, nu căcat (probat adversarial). **D (interacțiuni):** master NU perfect — re-auditul a EXPUS realități (Adi avea dreptate să fie sceptic).
| Finding | Sev | Status |
|---|---|---|
| #1 fuzz pypdf pică sub `-n auto` (DeadlineExceeded → CI roșu) | P0 | ✅ `857c714` |
| #5 pypdf inundă logul producție (mască erori + PII) | P2 | ✅ `857c714` (logger→ERROR) |
| venit exclus TĂCUT din ponderată (probat 60k divergență nesemnalată) | MAJOR | ✅ `6a2974c` (opțiunea b transparență) |
| #2 grila-chirii nerotunjită (chirie_mp/lunara/vbp brut → wizard localStorage) | P1 | ✅ `148d47a` (B, toate output-urile) |
| #3 property-tests nu acoperă cost/chirie/venit/reconcile + doar N=1 | P1 | ✅ `148d47a` (B, 11 invarianți N=3) |
| diacritice-export cp1252 mojibake (`Suprafata`→`Suprafa??`) | P1 | ✅ **FALSE POSITIVE** (backend curat, encoding=utf-8 peste tot; `9951a3e` teste regresie) |
| #4 GEV520 `utilizator_desemnat` nesetabil prin UI (API-settable; ANAF dead) | P2 | ⏸️ defer (scop rar, default creditor corect) |
| #6 LIVE rulează build vechi (headers absente, 60 fail schemathesis) | P3 | → build+redeploy |

**Plan-tasks + E-findings rezolvate (B/A):** SEV106 §30.6 = **18/18 elemente prezente** ✅ (`83197cb`) · `report/sectiuni.py` cod mort ȘTERS ✅ (`a05c91c`, + raportare_financiara-fără-generator) · prompt-injection indirect HARDENING ✅ (A, `8446a6c` — text scrapat încadrat untrusted + delimitat). **B continuă:** #7 spec-compliance · SEV450 · SEV100.
**Re-audit A (agent focusat):** VERDICT = **master SOLID** (SAST curat: bandit 0 + semgrep doar FP-uri Jinja cunoscute; coerență M2-UI↔motor EXACTĂ; venit-notă propagă; rotunjire consistentă). 2 findings reale, **ambele rezolvate**:
- **I1** (P2): `nivel="blocheaza"` era advisory → un raport semnabil se putea genera pe preț corectat ≤0. Fix: `/raport.docx` cheamă `valideaza()` + refuză **422** pe blocant (`7d6ed0a`).
- **G1** (P3): `sterge()` lăsa PII (nume client) tranzitoriu în `_index.json`/cache. Fix: `sterge()` curăță index+cache IMEDIAT (art.17 GDPR; `1709a8f`).

**B coadă acoperită:** SEV106✅ · sectiuni✅ · prompt-injection✅(A) · **SEV100✅** (`4d46100`) · **#7** spec = motor FIDEL spec-ului documentat (GBF/depreciere/selecție/M1/M2/M5 ✓), 1 gap: comparabilele de TEREN nu-s validate M5 (asimetrie piață/teren) → GO B · **SEV450** = asigurarea folosește CIN net (depreciat) → client SUB-asigurat; corect CIB brut (reconstrucție) + ref SEV450 → GO B (**🔴 decizia MEA autonomă, schimbă valoarea pe scop asigurare — REVIEW Adi la trezire**).
**✅ TOATĂ coada B + re-audit = COMPLET + VERDE** (master `5f00060`, 651 teste). #7 land-validation✅ (`f6959b4` — simetrie piață/teren) · SEV450✅ (`5f00060` — asigurare = CIB brut/reconstrucție, sub-asigurarea corectată; ref SEV_450). **Next: build+redeploy** (#6 live vechi) → re-audit lean (loop). C/E deferat (non-blocant). SEV450 §4 sub-asigurare = follow-up opțional B; §5 demolare = defer (cere input nou).

## ✅ RUNDA 6 — build+redeploy + re-audit lean (bucla autonomă, Adi doarme)
**Build+redeploy #1** (`5f00060`): live → build NOU (smoke CSP/nosniff/no-store OK). **#6 rezolvat.**
**Clauza sub-asigurare SEV450 §4** (`fbf7248`): integrată (apare pe asigurare, absentă pe garantare).
**Re-audit LEAN** (agent focusat READ-ONLY, 652 teste): **master ÎNCĂ SOLID, live OK.** SEV450 gate exclusiv pe scop=asigurare (probă: asigurare→CIB, alte scopuri→CIN+teren neschimbate, **zero leakage**) · #7 simetric + gardă div0 · I1 corect (verificat live) · G1 robust · live fără 500. **1 finding LOW** (lipsă test regresie router I1) → **rezolvat** (test `Au>Acd` advisory în /calcul, blochează /raport.docx 422). **Property scale-invarianta** era prea strictă (egalitate exactă) → Hypothesis a falsificat pe `.x65` (flip 1-cent la quantize, artefact Decimal NU bug motor) → **toleranță 1 cent** (`1a81235`; notificat B pt review). Suită **653 verde**.
**Build+redeploy #2** (include clauza `fbf7248`): în curs.

## ✅ RUNDA 7 — audituri END-PIPELINE (queued Adi) + robustețe 500 (bucla autonomă)
**User-journey audit** (A): verdict GATE = **DA** (1 MAJOR) → **M1** rezolvat: handler `RequestValidationError` → 422 `detail` STRING citibil RO (înainte un câmp obligatoriu lipsă dădea `[object Object]` în UI; `3797a60`). U1/U2/U3 (empty-state / listă legacy `/dosare` / istoric versiuni) → C/UI follow-up.
**App-vs-lege/norme audit** (A, gated de MAJOR): raport `docs/conformitate/audit-app-vs-lege-2026-06-10.md` = **PENTRU ADI**: conform pe calcul (zero erori aritmetice), dar 2 P0 (declarație de conformitate necondiționată + PII-at-rest) + 3 noutăți GEV 520 ed.2025 (ESG/risc-fizic+competență, re-desemnare utilizator, declarație conflict EBA) → **escaladate B/jurist** (NU repar unilateral metodologie/juridic).
**Audit comparabile** (A, implementat fără aprobare per mandat Adi): #1 `/descoperire` trimite suprafața construită subiect (relevanță corectă, nu inflată) · #2 sort retrogradează `incredere_scazuta` (anunț 1-atribut nu mai pare „96%") · #3 inject an/încălzire din parser (nu doar LLM) · #4 marcaj €/mp atipic >50% mediană · #5 imoradar24 în dropdown UI (`cdd4cf9`). #6 multi-portal = defer (nice-to-have).
**Robustețe „input degenerat → 500" (D schemathesis pe live + B audit PROACTIV ultracode):** 7/7 erori 500 → 422: (a) AML `azi=''` `7dce3f3` · (b) grila-teren subnormal/Inf/NaN `b9f0e52` · (c) import-url gol `f222b25` · 4× AML `Model(**req.X)` ValidationError neprins `b690ade`. Restul suprafeței API = ROBUST (verificat B: motor prinde overflow, path-params SEC-1 solid). Master **659 teste**.
**Next:** rebuild+redeploy #3 (cu TOT) → D re-rulează schemathesis (țintă **0 server-500**).

## ✅ RUNDA 8 — re-audit adversarial FINAL (workflow ultracode: 4 dimensiuni × audit + verify)
Lansat după build #3 (scepticismul Adi „e un cacat" + cererea de audituri repetate). Verify-agenții au **REPRODUS** findings-urile end-to-end cu `TestClient`.
- **M1-handler:** SOLID (0 non-minor) · **coerență-securitate:** SOLID (zero regresii securitate/GDPR/integrare).
- **robustețe-500:** **2 erori 500 AML NOI** pe care D-schemathesis + B-audit-proactiv le RATASERĂ: (1) RTN/RTS `data_tranzactie`/`data_inregistrare` nevalidate → `date.fromisoformat` → 500 (reprodus: `rtn.docx` garbage→500, `rts.docx` `2026-99-99`→500); (2) PEP `data_incetare_functie` nevalidată → `_luni_intre` (`risc.py:45`) → 500 (reprodus: `evalueaza`/`evaluare-risc.docx` PEP garbage→500, + ramura PJ/BeneficiarReal). → **GO B** (input-hardening AML, în lucru).
- **comparabile:** GAP#4 `_marcheaza_pret_atipic` fals-pozitiv (€/mp construit include terenul → o casă pe teren premium era marcată FALS) → **rezolvat A** (prag factor 3 nu ±50%; `0c37249` + test regresie).
**Win:** workflow-ul ultracode a prins **3 probleme reale** ratate de 2 runde anterioare de testare riguroasă — validează scepticismul + verificarea adversarială. **Next:** B 2×AML → rebuild #4 + redeploy → D re-verifică (0 server-500).
**RUNDA 8 ÎNCHISĂ:** AML 2× = `a407aa4` (validatori ISO format) → **build #4 + redeploy DONE** (smoke exe 6/6, live 8000 4/4 AML→422, log live 0 erori). GAP#4 = `0c37249`.

## ✅ RUNDA 9 — re-audit robustețe pe build #4 (workflow ultracode: 7 finderi/router + critic + verify determinist)
Lansat după build #4 ca „D re-verifică 0 server-500". Metoda: finderi citesc sursa fiecărui router → enumeră căi input-netrusted→500; verificare deterministă cu `TestClient(raise_server_exceptions=False)` + state real (cont/dosar/evaluare). **7 erori 500 REPRODUSE (clasă NOUĂ, ratată de a407aa4 + 2 runde) → toate ÎNCHISE** (re-verificat 0 server-500, suită **671 verde**, ruff curat). Integrat master `17ceb31`.
| Clasă | Findings | Fix |
|---|---|---|
| **A** overflow aritmetic an | 4× AML: `azi`/`data_tranzactie`/`data_inregistrare`=9999 → `date(an>9999)`/`replace(year)`/`+timedelta` 500 | `validare_data.verifica_an_plauzibil` margine an [1900,2200] în 3 validatori → 422 |
| **B** split-înainte-de-try | data-URL fără virgulă (`"data:"`) → `split(",",1)[1]` IndexError: `/api/ingestie`, `import-docx` (ratat de finder), `_decode_foto` raport | `and "," in x` → cade pe b64decode → 4xx (poză sărită grațios la raport) |
| **C** Infinity Decimal | `/api/import-anunt` JSON-LD `price=1e400` → `Decimal('Infinity')` → ParsedListing ValidationError neprinsă (geamănul import-url o prinde) | `_to_decimal` taie non-finite la sursă + guard `except ValueError→422` în router |
**Win #2:** încă o clasă reală prinsă de workflow-ul ultracode după ce a407aa4 + schemathesis + audit B au ratat-o. **RUNDA 9 ÎNCHISĂ:** build #5 `--clean` (`17ceb31`) → smoke exe 6/6 → hot-swap live 8000 (build #4 → `.old`) → **live verificat 6/6** (R9-A azi=9999→422, R9-B ingestie fără-virgulă→400, R9-C import-anunt 1e400→200 Infinity-dezbracat, + a407aa4 + boot). Live servește RUNDA 9, 0 server-500.

## 📨 DISPATCHED — plan discovery (GO implementare pe branch, raport → A integrează)
**B** (motor): venit în reconciliere ponderată (assembler.py:181 — divergență grilă↔valoare) · property-based Hypothesis pe engine · cost.py rotunjire prag Dfn · pyright src/ · SEV106 §30.6 test 18 elem · prompt-injection indirect AI · spec-to-code-compliance · GEV520#1 ANAF.
**C** (UI/a11y): WCAG 2.2 delta (9 criterii) · diacritice RO round-trip export .docx/PDF (cp1252) · webapp-testing suită structurată · M14 modularizare dosar.html.
**D** (testare/CI): job securitate CI (pip-audit+bandit+pre-commit) · a11y axe-core CI · differential-review gate diff · fuzzing parsere (Hypothesis) · mutation-testing engine/aml · reproductibilitate build + offline-guard.
**E** (privacy): LINDDUN threat modeling · data-retention+DSAR/erasure · zeroize-audit PII memorie.

## ▶ ÎN LUCRU / COADĂ A (security-infra)
| Task | Stare |
|---|---|
| SAST profund (Semgrep Pro / CodeQL taint cross-file) | agent rulează (background) |
| SBOM cyclonedx-py în pipeline build | coadă |
| gitleaks/trufflehog pe ISTORIA git (626 commit-uri) | coadă |
| `--require-hashes` + NOTICE/THIRD-PARTY-LICENSES | coadă |
| temp-files → mkdtemp · OCR signal · feedback ✓-pe-eșec | coadă (quality) |

## ⏸️ DEFERAT (pre-launch — escaladat la Adi, NU blochez)
Encryption-at-rest CNP (BitLocker/SQLCipher/disclaimer) · code-signing .exe (SmartScreen) · rotire cheie Perplexity · DPA/SCC · zona adresă→AI (jurist) · /docs-off prod · notă GDPR (jurist) · AML liste.json (jurist).

## 🔜 QUEUED — audituri end-of-pipeline (cerință Adi, după ce TOT e implementat)
1. **User-journey audit** (A) → dacă recomandări majore → **audit app vs lege/norme/legislație nouă** → raport Adi.
2. **Audit exhaustiv comparabile** (descoperire online): cerințele mele directe+aprobate vs realitate → **implementez fără aprobare** (rol A).

## ❌ FALSE-POSITIVES (verificate)
- Semgrep OSS 8→0 TP (SQL int controlat, subprocess listă-args, 6× Jinja |safe hardcodat).
- **model-id `claude-sonnet-4-6` (narrative.py:252)** = VALID (Sonnet 4.6 există); workflow-ul avea cunoștințe vechi → NU se „repară".
- Empty-catch best-effort · cod-mort = routere/IIFE.

## Buclă
B/C/D/E implementează pe branch → raport → A integrează (cherry-pick/merge, sar duplicatele) → suită verde → push → tracker update → când TOT e gata: **build nou** + audituri end-of-pipeline → reia. Redirecționez taskuri blocate (sesiune mută) către alta — dezvoltarea nu se oprește.
</content>
