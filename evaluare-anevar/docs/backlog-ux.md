# Backlog UX / accesibilitate / design

Status consolidat din auditurile `/design:ux-copy`, `/design:accessibility-review`,
`/design:design-critique`. Actualizat după implementări.

## ✅ Rezolvate

| # | Item | Unde |
|---|------|------|
| U1 | „Wizard" → „Evaluare" în navigare | `_topbar.html` |
| U2 | „Grile/Grilă" uniformizat (pagina are 3 grile → plural „Grile de ajustări") | `grila.html` |
| U3 | Empty state Descoperire + caz „0 rezultate" + try/catch pe căutare | `descoperire.html` |
| UX | Mesaje de eroare *Ce + Cum repari* (wizard/grilă/aml/form) | toate |
| UX | Link descriptiv „Vezi anunțul ↗" în loc de „link" | wizard, grilă, descoperire |
| UX | Consecvență stări de încărcare („Se caută…") | grilă |
| UX | Fără expunerea excepției JS brute în UI | grilă, form, descoperire |
| A11y | Stil real `.ghost` (buton secundar) + `rel="noopener"` pe linkuri `_blank` | `_design.css`, toate |
| A11y | `aria-expanded`/`aria-controls` pe selecturile care dezvăluie câmpuri | `wizard.html` |
| Design | „Formular" scos din nav primar (rămâne link în wizard) | `_topbar.html`, `wizard.html` |
| Design | Tab-uri la Grilă (WAI-ARIA: săgeți, Home/End) în loc de 3 grile stivuite | `grila.html`, `_design.css` |
| Design | Ierarhie CTA: acțiuni secundare `ghost`, primarul plin | wizard, aml, result |

## ✅ Rezolvate — UI nou „curent" (audit a11y+UX+design, 2026-06-06)

| # | Item | Unde |
|---|------|------|
| N1 | `dosar.html` refăcut pe sistemul de design: `_cartus`+`_footer`+`<nav>` (în loc de chrome hand-rolled) | `curent/dosar.html` |
| N2 | Tab-uri/sub-tab-uri = componenta `.tabs` + noua `.subtabs` (WAI-ARIA: role=tab/tabpanel, aria-controls/labelledby, săgeți/Home/End) | `dosar.html`, `_design.css` |
| N3 | Popover „!" accesibil: `.hint-toggle.is-map` (albastru info, contrast AA), aria-expanded/controls/label, închidere Escape | `dosar.html`, `_design.css` |
| N4 | Valori demo → `placeholder` (fără risc de raport cu date-exemplu) | `dosar.html` |
| N5 | Indicator de salvare real (… / salvat / eșuat), buton Generează cu `aria-busy` | `dosar.html` |
| N6 | `incepe`/`cont`: `<nav>` landmark, file-input `aria-label`, `th scope=col`+„Acțiuni", empty-state `.callout`, badge „comercial" vizibil, import cu status inline (nu `alert`), `autocomplete=name` | `incepe.html`, `cont.html` |
| N7 | Nume dosar recalculat la salvare (gol nu mai rămâne „?_?_?") | `dosare_fs.py` |

## ✅ Rezolvate — v1.5 „Flux livrabile" (audit a11y, 2026-06-07)

Audit WCAG 2 A/AA cu **axe-core (live, Playwright)** → **0 violări** (22 reguli trecute). Fixuri aplicate în `flux_livrabile.html`:

| # | Item | Severitate |
|---|------|-----------|
| F1 | Checkpoint asumare: `<div>` clicabil → `role=checkbox` + `tabindex` + tastatură (Space/Enter) + `aria-checked` | 🔴 blocant (2.1.1, 4.1.2) |
| F2 | Status „condiționat"/„în așteptare": contrast sub AA (`--gold`/`--line-2`) → `--warn-ink`/`--ink-faint` | 🔴 serios (1.4.3) |
| F3 | Switch-uri RTN/RTS: `aria-pressed` → `role=switch` + `aria-checked` + etichete descriptive | 🟡 |
| F4 | Stepper: `aria-controls` → panouri (`role=group`, id-uri) | 🟡 |
| F5 | Bară progres: `role=progressbar` + `aria-valuenow/min/max` (actualizat în JS) | 🟡 |
| F6 | Contor livrabile: `aria-live=polite` (anunț la schimbare) | 🟡 |
| F7 | Comutator PFA/PJ: `role=group` + `aria-pressed` | 🟡 |

**Sweep a11y pe TOATĂ aplicația (axe-core live, 2026-06-07):** `/`, `/incepe`, `/wizard`, `/grila`,
`/aml`, `/descoperire`, `/dosar/{uid}` (workspace + tab-urile AML/GDPR/Audit/Raport), `/flux-livrabile`
(7 pași + PFA + RTN/RTS + asumat + responsive 360/414/768px) → **0 violări** peste tot. Singurele
probleme erau pe v1.5 (reparate, F1–F7). Restul aplicației era deja curat.

> Rămas (NU făcut — risc pe build-ul de feedback / efort): ținte tactile 44×44px (AAA, doar `@media
> (pointer:coarse)`); `listeaza()` cache pe mtime (caching = risc de stale). De reluat post-feedback.

## 📌 De planificat — sesiuni de explorare

- **Modul de DESCOPERIRE — brainstorming / grill-me** (cerut de Adi, 2026-06-07).
  Sesiune dedicată (`superpowers:brainstorming` sau `grill-me`) pe modulul de descoperire de
  comparabile (scraping portaluri imobiliare/storia/olx, extracție atribute, scor de relevanță,
  coadă din extensia de browser). De clarificat: scop/UX-ul ideal, ce surse, cum se prezintă
  candidații, cum se leagă de grile/calcul, limitări legale de scraping. **Nu s-a făcut încă** —
  de programat cu Adi (nu autonom).

## 🟡 Deschise — decizii de produs din auditul UI nou (vezi `plan-maine-2026-06-06.md` §B)
- Ordine creare dosar (gol-apoi-completezi vs. modal de identitate) — **B1**.
- Blocare identitate după prima generare (read-only + override) — **B2**.
- „Importă dosarul tău" = `.docx` vs. folder (`importa_folder`) — **B3**.
- Reconciliere format-nume vs. câmpuri-identitate — **B4**.
- 5 opțiuni home cu 2 dezactivate — **B5**.
- Calcul→Generează o singură sursă de adevăr — **B6**.
- Moneda implicită EUR la garantare — **B7**.

## 🟡 Deschise (de confirmat / efort mai mare)

1. **Ținte tactile 44×44px** (WCAG 2.5.5 — nivel AAA, nu cerut de AA).
   - Acum butoanele au `min-height:24px` (trece AA 2.2 / 2.5.8). Pentru ecrane touch s-ar
     putea mări la 44px. Impact: `_design.css` (button, a.btn, file-selector-button).
   - Risc mic; estetic poate îngroșa butoanele pe desktop.

2. **Densitate „hints" (progressive disclosure).**
   - Fiecare câmp din wizard are un paragraf `.hint` permanent → încărcare cognitivă +
     formular lung. Variante: hints colapsabile („?" tooltip), sau câmpuri avansate în
     `<details>`. Conflictă parțial cu a11y (hints sunt `aria-describedby`) → necesită grijă.
   - Efort mediu, risc mediu (atinge toată structura wizardului).

3. **Form clasic (`/formular`) — paritate de copy.**
   - Acum e pagina secundară; nu a primit aceeași trecere de UX-copy ca wizardul. De aliniat
     dacă rămâne folosit.

## Neatins intenționat (guvernanță proiect)
- Copy juridic (banner AML, confirmare RTS/RTN — Legea 129/2019) = **bucket C (jurist)**.
- Copy/praguri metodologice (SEV/GEV, ajustări prudențiale, factor lichidare) = **bucket B (evaluator)**.
