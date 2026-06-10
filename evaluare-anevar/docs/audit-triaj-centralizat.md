# Triaj centralizat audituri — single source of truth (menținut de A)

Scop: **nimic nu scapă.** A centralizează toate findings-urile (runde 1–2–3 + descoperire) de la toate sesiunile (A/B/C/D/E), decide owner-ul, urmărește statusul până la REZOLVAT/DISPATCHED/DEFERAT/FALSE-POSITIVE. Actualizat la fiecare buclă.

Legendă status: ✅ rezolvat+comis · ▶ în lucru (A) · 📨 dispatched (lane) · ⏸️ deferat (pre-launch/comercial/jurist — doar notat) · ❌ false-positive (verificat)

---

## RUNDA 1–2 — findings & status

### ✅ Rezolvate de A (comise pe master)
| Finding | Sursă | Commit |
|---|---|---|
| PyMuPDF AGPL → pypdf (BSD) — deblochează distribuția | D r2 (licențe) | `382142b` |
| SSRF prin redirect — re-validare fiecare Location | B r1 + SAST | `d21d6a1` |
| suprafață=0/preț=0 → 500 — `Field(gt=0)` + valideaza în gardă | B r1 | `7f506eb` |
| Security headers (CSP/nosniff/X-Frame/Referrer/Permissions) + Server | C r2 + D r2 | `eae9334` |
| GitHub Actions checkout v5 + handler mort `la-anexe` | D r1 + C r1 | `9634937` |
| `beneficiar`→AI anonimizat | GDPR r2 + SAST | `d5c28a0` |

### 📨 Dispatched pe lane
| Finding | Lane | Stare |
|---|---|---|
| Chirii M2 (mediere top-N ca piață/teren) | B | GO dat (sesiune-b) |
| GEV 520 ed.2025 (BIG/ANAF + secțiuni noi) | B | forwardat (branch GEV_520) |
| Rotunjire valori grilă (28 zecimale în API/snapshot) | B | de dispatchat |
| Gardă valori negative (ajustări extreme/DCF/alocare) | B | de dispatchat |
| ruff `_e2e.py`/`_usability_audit.py` | D | dispatchat (tooling D) |
| Race LibreOffice xdist (UserInstallation profil partajat) | D | dispatchat (P1) |
| Perf settings/narrative 31s (mock anthropic) | D | dispatchat (P2) |
| Starlette httpx2 deprecation | D | dispatchat (P3) |

### ▶ În coadă la A (current-state, voi rezolva)
| Finding | Notă |
|---|---|
| 403-logging pe respingeri host/CSRF | NIT — app.py n-are logger, mic |
| temp-files nume predictibile → `mkdtemp` | SAST L1 — hardening multi-user |
| OCR niciodată invocat → PDF scanat = text gol silențios | quality — semnal UI |
| feedback widget arată „✓" pe save local eșuat | quality — simbol avertizare |

### ⏸️ Deferate (pre-launch/comercial/jurist — doar NOTATE, NU blochez)
| Finding | De ce deferat |
|---|---|
| Rotire cheie Perplexity (`.env`) | comercial/pre-launch (app în development) |
| Semnare cod Windows (SmartScreen) | comercial (abonament) — pre-launch |
| DPA/SCC transfer AI | juridic — jurist |
| CNP/KYC criptat at-rest | pre-launch hardening |
| Adresă brută→AI la `zona.py` (extragere județ/loc) | adresa E input-ul funcției; offline=fallback; jurist notează în GDPR |
| `/docs`/`/redoc`/`openapi` off pe build prod | pre-launch (utile în dev acum) |
| Nota GDPR „DOAR anonimizat" (onestitate) | bucket C — jurist (doc e MODEL/DRAFT) |
| Anexe AML `liste.json` placeholder sancțiuni/PEP | bucket C — jurist/loop |

### ❌ False-positives (verificate, fără acțiune)
- **D Semgrep SAST (8 raw → 0 TP):** SQL f-string pe int controlat (`db/storage.py:80`); subprocess listă-args shell=False (`report/pdf.py:37`); 6× Jinja `|safe` cu source hardcodat (escape complet în `md_to_html`). Cod matur.
- Empty-catch-uri best-effort (showPicker/localStorage/sendBeacon/lock-ping) — corecte.
- Cod mort „detectat" = routere FastAPI via include_router / IIFE-uri numite — false-positives.

---

## RUNDA 3 — research A (online project-help) → dispatch pe lane
| # | Acțiune | Lane |
|---|---|---|
| H1 | SEV 2025 (SEV 100/105/106 + declarație conformitate IVS + ESG) | B |
| H2 | Factori ESG/eficiență energetică (CPE) în garanție (EBA+IVS) | B |
| H3 | Semnare cod Windows | A (⏸️ comercial) |
| H4 | Schemathesis (contract/fuzz pe openapi.json) | D |
| M5 | Atheris fuzz pe parsere (pypdf/url/extractor) | D |
| M6 | mutmut mutation testing pe `engine/` | D |
| M7 | Hypothesis property-based pe invarianți | D |
| M8 | Logging structurat JSON + correlation-id | A |
| M9 | Raport diagnostic local opt-in | A |
| M10 | Update offline semnat (tufup) | A |
| M11 | ANAF webservice (validare CUI beneficiar) | A/B (coord AML) |
| M12 | INS TEMPO-Online (date piață reale) | B |
| M13 | Parser BNR regex→XML real (defusedxml) | B/A |
| M14 | Modularizare dosar.html (1224 linii) + generator.py | C/A/B |
| L15–L19 | exe-size, profiling, ANCPI deep-link, a11y polish, onboarding | A/C |

---

## PENDING (în zbor)
- **Workflow descoperire A** (`w8fkqwo3m`): tipuri audit online + skills + plugins + re-run-tool-mai-bun + verificări proiect → plan dispatch + listă instalat.
- **B/C/D/E:** re-run TOATE auditurile + tool-uri noi → raport la A.
- Când aterizează: instalez utilul · dispatch consolidat pe lane · integrez · **build nou** · reiau bucla.
</content>
