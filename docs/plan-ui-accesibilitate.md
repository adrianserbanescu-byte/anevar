# Plan de implementare — UI + Accesibilitate (consolidat)

**Creat:** 2026-06-04. Combină: (a) findings din **critica de design** (2026-06-04) și
(b) **Accesibilitate Faza 2** rămasă din `plan-accesibilitate.md`. Ordonat pe grupuri, în ordinea
recomandată de execuție. Efort: **S** mic · **M** mediu. Sursă în paranteze: `[critică]` / `[A1.x]`.

> Decizie fermă de respectat: **wizardul rămâne cu navigare liberă, FĂRĂ validare/gating între pași.**
> „Submit" nu blochează avansarea; doar „Calculează"/„Caută" trimit date.

---

## Grup 1 — Corecturi de conformitate (rapide, impact mare)
- [x] **G1.1** ✅ Contrast `.hint` — `--ink-faint` `#6c7686` → `#5a6270` (≈3.9:1 → ≈5.3:1, WCAG AA). `[critică #1]`
- [x] **G1.2** ✅ **Skip-link** „Sari la conținut" → `<main id="continut">`, pe toate paginile. `[A1.4]` **S**
- [x] **G1.3** ✅ `type="date"` pe câmpurile de dată (wizard + form: data_evaluarii/raportului/inspectiei). `[A1.2]` **S**
- [x] **G1.4** ✅ `autocomplete` pe câmpurile de identitate (evaluator, client, proprietar). `[A1.5]` **S**
- [x] **G1.5** ✅ Țintă tactilă **≥24px** pentru butoanele mici („șterge" upload, „➕ grilă", del-up). `[A1.6 + critică]` **S**

## Grup 2 — Formulare (semantică + densitate)
- [ ] **G2.1** `<form>` real + **submit pe Enter** (wizard/grila/descoperire/aml/form). Butoanele de acțiune
      devin `type="submit"` unde e cazul; **fără gating** pe wizard (rămâne navigare liberă). `[A1.1]` **M**
- [ ] **G2.2** `aria-describedby` — leagă mesajele de stare/eroare de câmpurile corespunzătoare. `[A1.3]` **M**
- [x] **G2.3** ✅ `aria-busy="true"` pe regiunile în timpul fetch (descoperire, calcul, curs BNR, ingestie). `[A1.7]` **S**
- [ ] **G2.4** `<fieldset>`/`<legend>` pentru grupurile de câmpuri din wizard (ca în `/aml`). `[A1.8]` **S**
- [ ] **G2.5** **Densitate descoperire/grila** — labelurile inline ale mini-formularelor au devenit bloc
      (din `label{display:block}` global + `<label for>`); fă-le compacte (label inline / grid). `[critică #3]` **S-M**

## Grup 3 — Pagina de rezultat `/result` (cea mai vizibilă lacună)
- [x] **G3.1** ✅ **`/result` ca „certificat"**: valoare hero formatată + **echivalent EUR/LEI** la curs BNR +
      butoane-CTA descărcare (.docx + raport cu note), card `.rez`. `[critică #2 / A2.1]`
- [x] **G3.2** ✅ **Formatare numerică ro-RO** (helper `_fmt_numar` în `app.py`) aplicată pe `/result`.
      *(De extins ulterior pe rezultatele wizard/grilă — deocamdată doar `/result`.)* `[critică #4]`

## Grup 4 — Lustruire minoră
- [ ] **G4.1** Inel de focus pe titlul pasului — scopează-l ca să nu apară pe toată lățimea la mouse
      (păstrează pentru tastatură). `[critică 🟢]` **S**
- [ ] **G4.2** *(opțional, Later)* testare reală **NVDA** + zoom 200% / lățime 320px (reflow); linter
      a11y headless (axe-core/pa11y) în CI. `[A3.2]` **M**

## Deja făcute (NU se refac)
- `prefers-reduced-motion` + `:focus-visible` explicit (la redesign).
- Asociere label↔control, landmark-uri `<main>`/`<nav>`, mesaje de stare `role=status`/`aria-live`,
  stepper cu `aria-current`, `alt` pe upload, `<th scope>` în grilă, contrast bară progres (Faza 1).

---

## Ordine recomandată & verificare
1. **Grup 1** (corecturi rapide, una-câte-una) → rulează suita + verifică contrast (raport ≥4.5).
2. **Grup 3** (`/result` certificat) → screenshot QA (preview).
3. **Grup 2** (formulare) → suită + smoke; atenție la `FormData`/JS existent.
4. **Grup 4** la final.
- La fiecare grup: `pytest -q` + extinde `tests/test_web_a11y.py` + **rebuild exe + smoke**.
- Estimare totală: ~majoritatea **S**, două **M** (G2.1, G2.2). Fără dependențe externe — se poate face autonom.
