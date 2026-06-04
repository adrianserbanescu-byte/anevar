# Sistem de design „Cadastru" — Evaluare ANEVAR

Estetică: **registru de carte funciară / topograf**. Hârtie-pergament caldă, cerneală
bleumarin, sienna de topograf + verde cadastral, linii de alamă. 100% offline (doar
fonturi de sistem). Sursa unică: `src/evaluare/web/templates/_design.css`, injectat în
toate paginile prin `{% include "_design.css" %}`.

> Regula de aur: **nu hardcoda valori noi** (culoare/spațiere/rază). Folosește un token
> din `:root`. Dacă nu există, adaugă-l acolo întâi.

## Design tokens (`:root`)

### Culori — hârtie & cerneală
| Token | Valoare | Rol |
|-------|---------|-----|
| `--paper` | `#f2eee2` | fundal pergament |
| `--paper-card` | `#fbf8f0` | carton card |
| `--paper-sunk` | `#e9e2d0` | casetă adâncită |
| `--ink` | `#16263d` | text principal (13:1 pe paper) |
| `--ink-2` / `--ink-faint` | `#3a4a60` / `#5a6270` | text secundar / estompat (≥4.5:1) |

### Culori — accente de marcă
| Token | Valoare | Rol |
|-------|---------|-----|
| `--sienna` / `--sienna-deep` | `#9d4a25` / `#7c3a1b` | acțiuni, accent (butoane, linkuri) |
| `--green` | `#2f6b4f` | succes / relevanță mare / risc redus |
| `--gold` / `--brass` / `--brass-hi` | `#a9822f` / `#b08d57` / `#d9c08a` | linii de alamă, sigiliu, decor |
| `--tricolor-blue/-yellow/-red` | `#27408b` `#d7a92b` `#a5301f` | bandă tricoloră (drapel) |

### Culori — semantice (stări / pastile)
| Token | Rol |
|-------|-----|
| `--danger` / `--danger-soft` / `--danger-ink` / `--danger-line` | eroare / risc sporit |
| `--warn-ink` / `--warn-soft` / `--warn-bg` / `--warn-line` | atenție / „mediu / standard" |
| `--green-soft` / `--green-line` | succes / „redus" |
| `--blue` / `--blue-deep` / `--blue-soft` / `--blue-line` | info tehnică (procente) |
| `--field-border` `#9c8a62` | bordură control (≥3:1, WCAG 1.4.11) |

### Linii / borduri
`--line` `#d7cdb4` (hairline cald) · `--line-2` `#bcae8c`

### Tipografie
| Token | Stack |
|-------|-------|
| `--serif` | Constantia, Cambria, … (titluri, valori) |
| `--sans` | Segoe UI, system-ui, … (text, UI) |
| `--mono` | Consolas, … (cod, textarea) |
| `--text-xs/-sm/-base/-lg` | `.74` / `.86` / `.95` / `1.34` rem |

> Cifre tabulare global: `font-feature-settings:"tnum"` — valorile monetare se aliniază.

### Spațiere (scală de 4px)
`--space-1..8` = `4 · 8 · 12 · 16 · 24 · 32 · 48` px.

### Borduri / raze / umbre / motion
| Token | Valoare | Rol |
|-------|---------|-----|
| `--radius` / `--radius-sm` / `--radius-pill` | `8` / `6` / `99` px | carduri / controale / pastile |
| `--shadow` | umbră de document (foarte discretă) | carduri ridicate |
| `--emboss` | inset alb+alamă | controale „gravate" |
| `--ease` | `cubic-bezier(.2,.7,.2,1)` | easing unic |
| `--grid-fine/-coarse` | `26` / `130` px | grilă cartografică (fundal) |

## Componente

| Componentă | Clase | Variante | Stări |
|------------|-------|----------|-------|
| **Buton** | `button`, `a.btn`, `a.btn.ghost` | primar (sienna), ghost | hover, active, disabled, focus-visible |
| **Input/Select/Textarea** | native | — | hover, focus (inel sienna), emboss |
| **Stepper** | `.stepper`, `.step`, `.num`, `.et` | — | `.done` (verde), `.activ` (sienna+ring), next |
| **Card pas** | `.pas` / `.pas.activ` | — | ascuns / activ |
| **Tabel-registru** | `table`, `th`, `td`, `.detalii` | — | zebra, `th[scope=row]` stub, linie alamă |
| **Pastilă/Badge** | `.badge` + tonul | vezi mai jos | — |
| **Callout / Rezumat** | `.callout`, `.rezumat` | — | — |
| **Alertă validare** | `.a-block` (eroare), `.a-warn` (atenție) | — | — |
| **Candidat** (descoperire) | `.candidat`, `.pret`, `.vezi` | — | hover |
| **Antet de pagină** | `.page-head` + `_compas.svg` + `.brass-rule` | — | — |
| **Sigiliu / decor** | `.seal-stamp`, `.cartouche`, `.tricolor-band`, `.kicker` | — | `aria-hidden` |

### Scala semantică de pastile (badge)
**O singură scală**, folosită de două domenii (relevanță descoperire + risc AML):

| Ton | Clase | Înțeles |
|-----|-------|---------|
| 🟢 verde | `.b-high`, `.redus` | relevanță mare / **risc redus** |
| 🟡 chihlimbar | `.b-mid`, `.standard` | mediu / **standard** |
| 🔴 roșu | `.b-low`, `.sporit` | relevanță mică / **risc sporit** |

> În AML clasa vine din backend: `class="badge {{ categorie }}"` (redus/standard/sporit).
> Nu reintroduce o a doua definiție pentru `.standard` (a fost un bug — vezi audit).

## Accesibilitate (built-in)
- Contrast: tot textul ≥4.5:1, componentele non-text ≥3:1 (verificat — vezi auditul WCAG).
- Focus vizibil: `:focus-visible` outline sienna 2px.
- `prefers-reduced-motion` dezactivează animațiile.
- Decorul (busolă, sigiliu, ghioșuri, riglă, bandă) e `aria-hidden` / `focusable="false"`.
- Skip-link „Sari la conținut" + landmark `<main id="continut">` pe fiecare pagină.

## Convenții
- **Nume de clase:** română pentru concepte de domeniu (`pas`, `candidat`, `rezumat`),
  engleză pentru primitive UI (`badge`, `hint`, `step`). Evită să introduci sinonime.
- **CSS local per pagină:** blocuri `<style>` scurte, doar pentru ce e specific paginii
  (ex. `.certificat` în `result.html`); restul stă în `_design.css`.
- **Fragmente reutilizabile:** `_helpers.js` (fmtRo, `$`), `_compas.svg` (busola) — incluse
  prin Jinja, un singur loc de modificat.
