# Plan de accesibilitate (WCAG 2.1 AA) — aplicația de evaluare ANEVAR

**Context:** audit din 2026-06-04 pe paginile `/wizard`, `/aml`, `/grila`, `/descoperire`.
Faza 1 (fixurile prioritare) e **implementată**. Acest document urmărește ce s-a făcut și ce rămâne.

---

## ✅ Faza 1 — Fixuri aplicate (2026-06-04)

| # | Fix | Criteriu | Pagini |
|---|-----|----------|--------|
| 1 | Asociere `label`↔control (`for`/`id`) — 53 controale | 1.3.1 / 3.3.2 / 4.1.2 | wizard (31), aml (8), grila (5), descoperire (9) |
| 2 | `aria-label` pe controale fără etichetă vizibilă + pe inputurile din grila generată | 4.1.2 | toate (13) |
| 3 | Mesaje de stare anunțate: `role="status"` / `aria-live="polite"` | **4.1.3** | toate (18 regiuni) |
| 4 | Bară de progres: `role="progressbar"` + `aria-valuenow/min/max` actualizate în `arata()` | 4.1.2 / 1.3.1 | wizard |
| 5 | Mutare focus pe titlul pasului la navigare (`focusPas()`) | 2.4.3 | wizard |
| 6 | Landmark `<main>` + `<nav>` pe linkurile de pagini | 1.3.1 / 2.4.1 | toate |
| 7 | `alt` pe imaginile de previzualizare upload | 1.1.1 | wizard |
| 8 | Contrast bară progres `#2a7`→`#1c7a52` (2.56:1 → 4.58:1) | 1.4.11 | wizard |
| 9 | Tabel grilă: `<th scope="col/row">` pentru asociere antet↔celulă | 1.3.1 | grila |
| 10 | **Bug-fix colateral:** helper `$` lipsă în grila → butoanele „Indicele ANEVAR" și „Caută terenuri" erau nefuncționale | — | grila |

Acoperit de teste de regresie: `tests/test_web_a11y.py` (11 teste).

---

## 🔜 Faza 2 — Îmbunătățiri (de făcut)

Prioritizate după impact/efort. Niciuna nu blochează utilizarea curentă.

### Now (impact mare, efort mic)
1. **Înfășurare în `<form>` + submit pe Enter** (wizard, grila) — momentan butoanele sunt
   `type="button"` și Enter nu trimite. Adaugă `<form>` cu `onsubmit` și `type="submit"`. *(3.2 / UX)*
2. **`type="date"` pe câmpurile de dată** (wizard: data_evaluarii, data_raportului, data_inspectiei) —
   selector nativ + validare format. *(3.3.2)*
3. **Identificarea erorilor lângă câmp** — leagă mesajele de validare de inputuri prin
   `aria-describedby` (acum sunt doar într-o regiune live separată). *(3.3.1)*
4. **Skip-link** „Sari la conținut" la începutul fiecărei pagini, către `<main id="continut">`. *(2.4.1)*

### Next (impact mediu)
5. **`autocomplete`** pe câmpurile de identitate (evaluator, client). *(1.3.5)*
6. **Țintă tactilă ≥24px** pentru butoanele mici („șterge" upload, „➕ grilă"). *(2.5.8 — WCAG 2.2)*
7. **Stare de încărcare accesibilă** (`aria-busy="true"`) pe regiunile care fac fetch
   (descoperire, calcul, curs BNR). *(4.1.3)*
8. **`<fieldset>`/`<legend>`** pentru grupuri de câmpuri în wizard (ca în `/aml`), nu doar `<label>`-uri
   succesive. *(1.3.1)*

### Later (robustețe / proces)
9. **Testare reală cu cititor de ecran** (NVDA gratuit + VoiceOver) pe fluxul complet wizard→raport,
   plus verificare la **zoom 200%** și la lățime de 320px (reflow, 1.4.10). *(proces)*
10. **Mod contrast ridicat / `prefers-reduced-motion`** — respectă preferința de reducere a
    animației pe tranziția barei de progres. *(1.4.x / 2.3.3)*
11. **Linter CI de accesibilitate** — adaugă un pas care rulează `axe-core`/`pa11y` headless pe cele
    4 pagini la fiecare build (prinde ~30–40% automat). *(proces)*
12. **Focus vizibil întărit** — stil `:focus-visible` explicit (contur 2px) ca să nu depindă de
    inelul implicit al browserului (diferă între browsere/teme). *(2.4.7)*

---

## Principii (de păstrat la dezvoltare ulterioară)
- Orice control nou primește **etichetă asociată** (`label for` sau `aria-label`).
- Orice mesaj scris din JS merge într-o regiune cu `role="status"` / `aria-live`.
- Orice tabel de date generat folosește `<th scope>`; inputurile din tabel primesc `aria-label` cu
  numele rândului + coloanei.
- Contrast text ≥ 4.5:1, elemente non-text ≥ 3:1 — verifică la alegerea culorilor.
- `tests/test_web_a11y.py` se extinde la fiecare pagină nouă.
