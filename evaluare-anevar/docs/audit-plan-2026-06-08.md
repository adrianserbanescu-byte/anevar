# Plan de audituri — proiect evaluare ANEVAR (2026-06-08)

> Cerere Adi: listă de audituri cu scop pentru stadiul actual (pre-lansare) + criticalitate +
> distribuire prioritară între sesiunile A (deploy/sistem), B (motor), C (UI). C începe cu cel critic.
> Context: app Python/FastAPI, date personale (PII/AML/GDPR), livrabile legale (rapoarte ANEVAR/SEV),
> ~566 teste, dezvoltare masivă recentă (descoperire, workspace, strat de stări, iconuri, config-API).

## P0 — BLOCANTE de lansare (risc legal / date / corectitudine produs)

| # | Audit | De ce P0 acum | Owner sugerat | Unealtă |
|---|-------|----------------|---------------|---------|
| 1 | **Securitate cod** (security-review) | App procesează PII + AML + GDPR, upload .docx/PDF, generare documente, scraping. Orice XSS/injection/path-traversal/SSRF = risc legal + breșă de date. | **C** (rulez ACUM) → A triază | `security-review` skill |
| 2 | **Vulnerabilități dependențe** (CVE) | Pre-lansare: deps cu CVE cunoscute (requests, jinja2, fastapi, python-docx, lxml). Risc direct de exploit. | **A** (deține deps + lock-uri + build) | `dependency-audit` |
| 3 | **Conformitate metodologică SEV 2025 / GEV 520/630** | Calculele de evaluare (grilă, scoring, ajustări, reconciliere) trebuie să fie corecte conform standardelor — altfel rapoartele sunt invalide juridic. NU e audit de cod pur, e validare de domeniu. | **B** (motor) + evaluator (Adi) | manual + teste motor |
| 4 | **Conformitate juridică AML/GDPR** (texte + flux) | Textele AML (HCD 58/L129), drafturile GDPR, indicatorii de suspiciune, RTS/RTN — validare jurist. Bucket C-juridic (NU foreground). | **jurist** (extern) + A coordonează | manual |

## P1 — ÎNALT (înainte de useri reali, nu blochează un build intern)

| # | Audit | De ce P1 | Owner sugerat | Unealtă |
|---|-------|----------|---------------|---------|
| 5 | **Breaking changes REST API** | API schimbat masiv recent (config-ponderi, c.axe, max_candidati 8→20, poza). Extensia de browser + orice integrare se pot rupe. | **B** (deține API motor) + C (consumatori UI) | `find-breaking-rest-api` |
| 6 | **Accesibilitate WCAG 2.1 AA** (sistematic) | Am făcut manual + audit Rams parțial. Un pass sistematic pe toate paginile (contrast, focus, tastatură, SR, target size). Conformitate + UX. | **C** (lane UI) | `design:accessibility-review` |
| 7 | **Acoperire teste** (gaps pe căi critice) | 566 teste, dar care căi critice (calcul valoare, AML decizie, generare raport, persistență dosar) sunt sub-acoperite? Pre-lansare = încredere. | **B** (motor) + C (UI/web) | `pr-test-analyzer` / manual |

## P2 — MEDIU (mentenanță / observabilitate, post-lansare OK)

| # | Audit | De ce P2 | Owner sugerat | Unealtă |
|---|-------|----------|---------------|---------|
| 8 | **Cod mort** | Post-dezvoltare masivă (5 situri descoperire, refactoring) — funcții/importuri/CSS orfane. Mentenanță, nu blocant. | **A** (sistem) sau oricine | `find-dead-code` |
| 9 | **Logging / observabilitate** | Debugging în producție: căile critice au log-uri suficiente? RotatingFileHandler există; gaps? | **A** (deține runtime/deploy) | `improve-logging` |
| 10 | **Performanță** (core web vitals) | App local (127.0.0.1) — latență mică. Relevant doar dacă apar pagini lente (descoperire scraping e deja async). | scăzut — la nevoie | `performance` |

## Recomandare de distribuire (A decide)
- **C (eu):** P0#1 securitate (ÎN CURS) → P1#6 a11y → P2#8 dead-code UI. (lane UI/.html)
- **B:** P0#3 metodologie SEV/GEV → P1#5 breaking-API → P1#7 coverage motor.
- **A:** P0#2 deps CVE → P2#9 logging → P2#8 dead-code sistem. Coordonează P0#4 (jurist) + triere findings.

**Ordinea de atac sugerată:** P0 în paralel pe cele 3 lane-uri (securitate-C, deps-A, metodologie-B) → P1 → P2.
