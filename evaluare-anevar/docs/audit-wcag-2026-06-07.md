# Audit accesibilitate WCAG 2.1 AA — paginile principale (2026-06-07)

> Rulat cu skill-ul `design:accessibility-review` (sesiune C) pe **incepe.html, cont.html,
> dosare.html, result.html, index.html, feedback_list.html**. Verdict: **stare foarte bună** după
> cele 5 valuri de polish anterioare. O singură lacună reală găsită (caption tabele) — **fix-uită**.
>
> NU acoperite (alte bucket-uri): `dosar.html` (A — ADR-003), `descoperire.html`/`grila.html` (B),
> text juridic AML/`aml.py` (jurist).

**Standard:** WCAG 2.1 AA · **Data:** 2026-06-07 · **Auditor:** sesiune C (`design:accessibility-review`)

---

## Sumar

| Severitate | Count | Stare |
|---|---|---|
| 🔴 Critical | 0 | — |
| 🟡 Major | 0 | — |
| 🟢 Minor | 1 | ✅ FIXED (caption tabele) |
| ℹ Recomandare (peste AA) | 1 | Documentat (touch target 44px = AAA) |

**Issues found: 1 real (rezolvat) + 1 recomandare opțională.** Restul = PASS.

---

## Findings

### Perceivable

| # | Issue | WCAG | Severitate | Recomandare | Stare |
|---|---|---|---|---|---|
| 1 | Tabelele de date (dosare, feedback) fără `<caption>` — screen readers nu primesc descriere de ansamblu | 1.3.1 Info & Relationships | 🟢 Minor | `<caption class="sr-only">` cu descrierea coloanelor | ✅ FIXED (commit e89bbe2) |

**Verificate, PASS:**
- 1.1.1 Non-text content — zero `<img>` fără alt; emoji decorative au `aria-hidden="true"` (valurile 1-5); SVG-uri sigiliu/compas au `aria-hidden` + `focusable="false"`
- 1.3.1 — `scope="col"` pe toate `<th>` (val 5); `<dl>` semantic pe result.html; landmark `<main id="continut">` pe toate
- 1.4.3 Contrast text — vezi tabelul de mai jos, toate ≥4.97:1
- 1.4.11 Non-text contrast — `--field-border #9c8a62` ≥3:1 pe card (comentat în CSS)

### Operable

| Verificat | Stare |
|---|---|
| 2.1.1 Keyboard | PASS — toate controalele sunt `<button>`/`<a>`/`<input>` native (keyboard by default); zero `<div onclick>` |
| 2.4.1 Skip link | PASS — `.skip-link` „Sari la conținut" pe toate paginile (CSS L626) |
| 2.4.3 Focus order | PASS — DOM order logic; form-ul de creare dosar focus pe primul câmp la deschidere |
| 2.4.7 Focus visible | PASS — `:focus-visible{ outline:2px solid sienna; offset:2px }` global (L341); inputurile au `outline:none` DAR alternativă validă: `border-color:sienna` + `box-shadow:0 0 0 3px ring` |
| 2.5.8 Target Size Minimum (WCAG 2.2 AA) | PASS — `min-height:32px` global pe button/a.btn (>24px minim) |

### Understandable

| Verificat | Stare |
|---|---|
| 3.1.1 Language | PASS — `<html lang="ro">` pe toate paginile |
| 3.2.1 On focus | PASS — niciun context-change neașteptat la focus |
| 3.3.1 Error identification | PASS — mesaje de eroare cu „cod 404 + verifică Y" (valurile 1-2); `role="status" aria-live="polite"` pe zonele de status |
| 3.3.2 Labels | PASS — `<label for>` pe toate inputurile; `cont.html` are `required` + `aria-required` + `aria-describedby` (val 3) |

### Robust

| Verificat | Stare |
|---|---|
| 4.1.2 Name/role/value | PASS — `role="alert"` pe disclaimer AML; `role="status" aria-live` pe status zones; `aria-describedby` pe butoane↔status; `aria-disabled` pe butoane comerciale |
| 2.4.2 Page titled | PASS — titluri unice descriptive pe fiecare pagină |

---

## Color Contrast Check (calculat manual, formula WCAG)

| Element | Foreground | Background | Ratio | Cerut | Pass? |
|---|---|---|---|---|---|
| Body text | `--ink #16263d` | `--paper #f2eee2` | ~13:1 | 4.5:1 | ✅ |
| Hint text | `--ink-faint #5a6270` | `--paper` | 5.41:1 | 4.5:1 | ✅ |
| Linkuri | `--sienna #9d4a25` | `--paper` | 5.26:1 | 4.5:1 | ✅ |
| Buton primar | `#fdf8ef` | `--sienna #9d4a25` | 5.70:1 | 4.5:1 | ✅ |
| Badge verde | `--green #2f6b4f` | `--green-soft #e2ece2` | 5.21:1 | 4.5:1 | ✅ |
| Badge amber | `--warn-ink #7a5c14` | `--warn-bg #ece4d2` | 4.97:1 | 4.5:1 | ✅ (marginal) |
| Badge roșu | `--danger #9c2c1b` | `--danger-soft #f4e0d9` | 5.91:1 | 4.5:1 | ✅ |

**Toate trec AA.** Cel mai strâns: badge amber 4.97:1 (marjă +0.47 față de prag) — recomand monitorizare dacă cândva se deschide fundalul.

---

## Keyboard Navigation

| Pagină | Tab order | Enter/Space | Escape | Observație |
|---|---|---|---|---|
| incepe.html | logic: nav → butoane acțiune → form → tabel | activează butoane native | — | form focus pe primul câmp la deschidere ✅ |
| cont.html | nume → legitimație → checkbox-uri format → salvează | salvează prin buton | — | `aria-describedby` leagă butonul de status ✅ |
| dosare.html | tabel → butoane per rând (open/ren/docx/del) | acțiuni native | — | toate `<button>` native ✅ |
| result.html | nav → butoane descărcare | linkuri native | — | H1 în `<main>` (val 3) ✅ |

Zero focus traps. Zero `tabindex > 0`.

---

## Screen Reader

| Element | Announced as | Issue |
|---|---|---|
| Tabele dosare/feedback | „tabel, N rânduri" + acum `<caption>` descriptiv | ✅ FIXED (era fără caption) |
| Emoji decorative | (tăcut — `aria-hidden`) | ✅ |
| Status zones | citite live la schimbare (`aria-live="polite"`) | ✅ |
| Disclaimer AML | „alertă: Aplicația NU verifică automat..." (`role="alert"`) | ✅ |
| Butoane comerciale (build comercial) | „indisponibil" (`aria-disabled`) | ✅ |

---

## Priority Fixes

1. ✅ **[FIXED] Caption tabele** (1.3.1) — afecta utilizatorii de screen reader pe `/dosare` și `/feedback`. Rezolvat în commit e89bbe2.

## Recomandări opționale (peste AA, NU obligatorii)

1. **Touch target 44×44px** (WCAG 2.5.5 — nivel **AAA**, nu AA): butoanele au `min-height:32px`. Pe AA 2.1 nu e cerință (2.5.5 e AAA; 2.5.8 AA-2.2 cere doar 24px). Dacă vizezi AAA sau mobile-heavy usage, crește la 44px — **dar atinge CSS global** (`_design.css` L630), care afectează și paginile A/B → necesită coordonare cross-sesiune, NU fix unilateral.

2. **Badge amber 4.97:1** — trece AA cu marjă mică. Dacă se ajustează vreodată paleta, păstrează `--warn-ink` suficient de închis.

---

## Concluzie

**Paginile principale ale aplicației sunt conforme WCAG 2.1 AA.** Munca de polish din cele 6 valuri
(emoji aria-hidden, scope=col, form a11y, heading hierarchy, error UX-copy, captions) + paleta de
culori gândită din start cu contrast (comentariile din `_design.css` dovedesc intenție) au produs un
UI accesibil. Singura recomandare rămasă (touch 44px) e AAA și cere decizie de design global.

---

*Generat în sesiunea C (worktree `anevar-c`, ramura `sesiune-c`). Fix-ul aplicat: commit e89bbe2.*
