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
