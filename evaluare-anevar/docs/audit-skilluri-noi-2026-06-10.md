# Audituri cu skill-uri noi (2026-06-10) — read-only, GO de la Adi

Trei audituri noi peste cele anterioare, rulate de sesiunea C. Findings only.

## 1. differential-review (trailofbits) — diff M2 UI (sesiune-c 49de090)
Vezi docs/audit-differential-review-M2-2026-06-10.md.
- Securitate (XSS): CURAT — innerHTML randează doar valori numerice/computate.
- F1 [LOW] grila.html fallback `[d.index_selectat]` fără guard `||0` (inconsistență vs _indMed).
- F2 [MEDIUM-test] logica M2 UI fără test commis (fallback + alertă-pe-toate-mediate, prudențial-critic).

## 2. site-audit (Lighthouse engine) — UI live
| Pagină | Performance | Accessibility | Best Practices |
|--------|-------------|---------------|----------------|
| /incepe | 99/100 | **100/100** | **100/100** |
| /descoperire | 74/100 | **100/100** | **100/100** |
- A11y 100 + Best-Practices 100 pe ambele = confirmă auditul manual a11y + zero console-errors/API deprecate.
- Perf 74 pe /descoperire = MapLibre CDN render-blocking → **reîntărește recomandarea bundle MapLibre local**
  (bundling rezolvă simultan: perf descoperire + SRI/supply-chain + offline). Pe /incepe (fără CDN) = 99.
- Metricile perf sub 100 (Speed Index 3.6s, FID 240ms) = artefact al throttling-ului Lighthouse; app local real e instant.

## 3. semgrep 1.165.0 (golul flagat — acum rulat)
- web/ (OWASP + JS): **0 findings** (5 PartialParsing pe Jinja = limitare parser, non-finding).
- src/ python (security-audit + python): **6 WARNING**, TOATE `template-unescaped-with-safe` (filtrul `|safe`):
  _cartus.html:5-8 (ornament colț), _icon.html:37 (dict SVG iconuri), document.html:12 (docs build-time).
  = EXACT cele triate SIGURE în security-review-ul inițial (conținut de dezvoltator, nu user/scrape).
  **0 findings noi reale.** Recomandare opțională: `{# nosemgrep #}` + comentariu de ce-s safe (reduce zgomot la audituri viitoare) → candidat fp-check.

## Verdict cumulat
Zero vulnerabilitate nouă. 2 items minore actionabile (F1 nit + F2 test M2). Perf descoperire = încă un argument pt bundle MapLibre local.
