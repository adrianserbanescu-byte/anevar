# Modulele aplicației de evaluare ANEVAR

Listă a modulelor aplicației (pachetul `evaluare-anevar/src/evaluare/`), cu rolul fiecăruia și
statutul. Modulele **planificate** au spec dedicat în `docs/superpowers/specs/`.

---

## Module implementate

| Modul | Rol | Status |
|---|---|---|
| `models/` | Modelele de date: proprietate, comparabile + ajustări, rezultate, meta, narativ, ReportContext | ✅ |
| `engine/cost.py` | Abordarea prin **cost** — CIN segregat (catalog IROVAL), depreciere interpolată | ✅ validat |
| `engine/market.py` | Grila de **casă** pe preț total, 2 etape (tranzacție secvențial + proprietate aditiv) | ✅ validat (3 dosare) |
| `engine/land.py` | Grila de **teren** (EUR/mp), 2 etape, selecție pe ajustare brută minimă | ✅ validat (4 dosare) |
| `engine/reconciliation.py` | Reconcilierea (piață/cost/ponderată) + alocarea valorii (construcții = proprietate − teren) | ✅ |
| `engine/validation.py` | Validări SEV (min comparabile, outlier, limită ajustare) | ✅ |
| `assembler.py` | Orchestrare: din datele de intrare → `ReportContext` complet | ✅ |
| `discovery/` | Descoperire comparabile: căutare portal → parsare → extragere → scor → rank (casă **și teren**) | ✅ |
| `importers/url_parser.py` | Parsare anunț (preț, suprafețe, caracteristici structurate: an, încălzire, material…) | ✅ |
| `report/generator.py` | Generator raport `.docx` (shell GBF, 7 capitole, GEV 520, alocare, anexe foto+documente, mod adnotări) | ✅ conform SEV 2025 |
| `report/anonymizer.py` | Anonimizarea datelor personale înainte de orice apel AI (GDPR) | ✅ |
| `ai/narrative.py` | Narativul AI per capitol (client injectabil: Anthropic/Perplexity), curățare text | ✅ |
| `web/` | Aplicația web locală (FastAPI): API + wizard 5 pași + pagina de grilă + descoperire | ✅ |
| `db/storage.py` | Persistență SQLite a dosarelor | ✅ |
| `localitati.py` | Dataset 42 județe / 13.250 localități (dropdown-uri) | ✅ |
| `zona.py` | Derivarea zonei (județ + localitate) din adresă | ✅ |
| `curs_bnr.py` | Cursul de schimb BNR (feed public XML) — EUR/LEI | ✅ |
| `config.py` | Configurare (chei AI, căi), activarea clientului narativ | ✅ |
| `money.py` | Helper Decimal pentru bani | ✅ |

---

## Module planificate (LATER în roadmap)

| Modul | Rol | Status | Spec |
|---|---|---|---|
| `aml/` | **Conformitate Legea 129/2019 (AML)** — KYC client + beneficiar real, screening sancțiuni/PEP/jurisdicții necooperante, scor de risc SB/FT, jurnal + schiță raport ONPCSB, Anexă AML în raport | 📋 Planificat | [modul-aml-129-2019](superpowers/specs/2026-06-03-modul-aml-129-2019-design.md) |
| `big/` | **Integrare BIG (Baza Imobiliară de Garanții)** — import comparabile reale de garantare (sursă primară), înregistrarea raportului în BIG (cerință GEV 520 §7), opțional Indicele imobiliar ANEVAR | 📋 Planificat | [modul-big](superpowers/specs/2026-06-03-modul-big-design.md) |

**Dependență comună:** ambele necesită **acces/validare externă** — modulul AML necesită validare
juridică (conținut KYC, praguri, formularistică ONPCSB); modulul BIG necesită **acces de membru
ANEVAR** (API sau export). De clarificat cu ANEVAR înainte de implementare.

---

*Vezi și: [roadmap-anevar.md](roadmap-anevar.md) pentru prioritizarea Now / Next / Later.*
