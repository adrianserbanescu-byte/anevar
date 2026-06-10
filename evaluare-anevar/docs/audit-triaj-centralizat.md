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
| #2 grila-chirii nerotunjită (chirie_mp/lunara/vbp brut → wizard localStorage) | P1 | 📨 B |
| #3 property-tests nu acoperă cost/chirie/venit/reconcile + doar N=1 | P1 | 📨 B |
| diacritice-export cp1252 mojibake (`Suprafata`→`Suprafa??`) | P1 | 📨 D (reassign de la C silent) |
| #4 GEV520 `utilizator_desemnat` nesetabil prin UI (API-settable; ANAF dead) | P2 | ⏸️ defer (scop rar, default creditor corect) |
| #6 LIVE rulează build vechi (headers absente, 60 fail schemathesis) | P3 | → build+redeploy |

**Pending:** workflow A 8-dim (verify) + C/E re-audit → centralizez + verdict final + re-audit loop.

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
