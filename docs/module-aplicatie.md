# Modulele aplicației — mapare pe cele 5 sisteme din specificația inițială

Cele 5 sisteme discutate la început (sursă: spec NotebookLM), cu modulele care le implementează și
statutul. Modulele **planificate** au spec dedicat în `docs/superpowers/specs/`.

Legendă status: ✅ implementat · 🟡 parțial · 📋 planificat (cu spec).

---

## Sistem 1 — Ingestie documente (vision-language + OCR)
*Parsare carte funciară, releveu, plan amplasament, certificat energetic.*

| Modul | Rol | Status |
|---|---|---|
| `importers/url_parser.py` | Parsare **anunțuri** (preț, suprafețe, caracteristici structurate) | ✅ |
| upload foto + documente | Documente atașate în Anexa 2/3 a raportului (fără parsare) | ✅ |
| **`ingestie/`** | **OCR + vision-language**: extrage câmpuri din CF, releveu, plan, CPE → pre-completare | 📋 [spec](superpowers/specs/2026-06-03-modul-ingestie-documente-design.md) |

➡️ **Status sistem: 🟡 parțial** (parsăm anunțuri și atașăm documente; parsarea documentelor oficiale e planificată).

---

## Sistem 2 — Conectivitate date externe
*ANCPI/e-Terra API + scraping portaluri imobiliare + indici BNR.*

| Modul | Rol | Status |
|---|---|---|
| `discovery/` + `importers/` | Scraping portaluri (imobiliare/storia): descoperire comparabile casă **și teren** | ✅ |
| `curs_bnr.py` | Indici/curs **BNR** (feed public XML) EUR/LEI | ✅ |
| **`big/`** | **BIG** (Baza Imobiliară de Garanții) — comparabile reale de garantare + înregistrare raport (GEV 520) | 📋 [spec](superpowers/specs/2026-06-03-modul-big-design.md) |
| **`ancpi/`** | **ANCPI / e-Terra** — verificare cadastrală oficială (nr. cadastral, CF, suprafețe, sarcini) | 📋 [spec](superpowers/specs/2026-06-03-modul-ancpi-eterra-design.md) |

➡️ **Status sistem: 🟡 parțial** (portaluri + BNR gata; ANCPI/e-Terra și BIG planificate, blocate de acces).

---

## Sistem 3 — Motor matematic de evaluare
*Grila de comparație directă + cost de înlocuire net + depreciere.*

| Modul | Rol | Status |
|---|---|---|
| `engine/cost.py` | Cost de înlocuire net (CIN segregat, catalog IROVAL) + depreciere interpolată | ✅ validat |
| `engine/market.py` | Grila de **casă** pe preț total, 2 etape (tranzacție + proprietate) | ✅ validat (3 dosare) |
| `engine/land.py` | Grila de **teren** (EUR/mp), 2 etape, selecție pe ajustare brută minimă | ✅ validat (4 dosare) |
| `engine/reconciliation.py` | Reconciliere (piață/cost/ponderată) + alocarea valorii | ✅ |
| `assembler.py` | Orchestrare → `ReportContext` | ✅ |

➡️ **Status sistem: ✅ implementat și validat pe dosare reale GBF.**

---

## Sistem 4 — Generator raport SEV
*Capitolele obligatorii, formatare, anexe.*

| Modul | Rol | Status |
|---|---|---|
| `report/generator.py` | Raport `.docx`: shell GBF, 7 capitole, GEV 520 (checklist A5), alocare, anexe foto+documente, mod adnotări | ✅ conform **SEV 2025** (SEV 102/106; raportare SEV 106) |
| `ai/narrative.py` | Narativul AI per capitol (client injectabil), curățare text | ✅ |
| `models/` | ReportContext + modelele de date | ✅ |

➡️ **Status sistem: ✅ implementat, actualizat la SEV 2025 + GEV 520.**

---

## Sistem 5 — Validare & conformitate
*Loops de validare încrucișată, anonimizare GDPR, audit trail.*

| Modul | Rol | Status |
|---|---|---|
| `engine/validation.py` | Validări SEV (min comparabile, outlier, limită ajustare) | ✅ |
| `report/anonymizer.py` | Anonimizare GDPR înainte de orice apel AI | ✅ |
| **`audit/`** | **Audit trail** (jurnal append-only + hash) + snapshot + **validare încrucișată** (cablată în `/api/evaluare`) + export | ✅ schelet implementat (TDD, 9 teste) · [spec](superpowers/specs/2026-06-03-modul-audit-trail-design.md) |
| **`aml/`** | **Conformitate Legea 129/2019 (AML)** — KYC, screening sancțiuni/PEP, risc SB/FT, raport ONPCSB | 📋 [spec](superpowers/specs/2026-06-03-modul-aml-129-2019-design.md) |

➡️ **Status sistem: 🟡 parțial** (validări + GDPR + audit trail gata; AML planificat).

---

## Module-suport (transversale, implementate)

`web/` (FastAPI: API + wizard + grilă + descoperire) · `db/storage.py` (SQLite) ·
`localitati.py` (42 județe / 13.250 localități) · `zona.py` (adresă → zonă) · `config.py` ·
`money.py`.

---

## Sinteză

| Sistem | Status |
|---|---|
| 1. Ingestie documente | 🟡 parțial (parsare anunțuri ✅; OCR/VLM documente 📋) |
| 2. Conectivitate date externe | 🟡 parțial (portaluri + BNR ✅; ANCPI + BIG 📋) |
| 3. Motor matematic | ✅ |
| 4. Generator raport SEV | ✅ |
| 5. Validare & conformitate | 🟡 parțial (validări + GDPR + audit ✅; AML 📋) |

**Implementat recent:** `audit/` (schelet TDD). **Module planificate (cu spec):** `ingestie/`,
`ancpi/`, `big/`, `aml/`.
Dependențe comune: acces extern (ANCPI, BIG — membru ANEVAR), validare juridică (AML), cost model VLM
(ingestie). De clarificat înainte de implementare.

*Vezi și: [roadmap-anevar.md](roadmap-anevar.md).*
