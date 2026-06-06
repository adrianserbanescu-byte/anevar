# Audit accesibilitate (WCAG 2.1 AA) + UX — UI NOU curent

Domeniu: `templates/curent/*` (dosar, incepe, cont), `index.html`, `documente.html`, parțialele comune (`_design.css`, `_nav_cross.html`, `_cartus.html`, `_footer.html`).
Referință de contrast pentru „butoane la sub-tab-uri”: `grila.html` (`.tabs`).
Data: 2026-06-06. Metodă: inspecție statică a fișierelor (cod, nu randare live). NU s-a modificat cod.

## Tabel probleme

| # | Severitate | Fișier | Problemă | Fix concret (1 linie) | Auto-safe? |
|---|-----------|--------|----------|-----------------------|------------|
| 1 | Înalt | `_design.css` (309-319) | `.subtabs` inactive: fill `--paper-sunk` pe pagina `--paper` + bordură `--line` (~1.1:1 față de pagină) → nu au afordanță de buton (vezi secțiunea dedicată). | Bordură `--field-border` + `box-shadow:var(--emboss)` pe `.subtabs [role=tab]`. | Da |
| 2 | Înalt | `curent/dosar.html` (195-213) | Lipsește popover-ul „?” (ajutor pe câmp); există doar „!” (mapare UI vechi, marcat „temporar/dev”). Câmpurile fără context = utilizabilitate slabă. | Portează injectorul „?” din `wizard.html` (729) cu `aria-label="Detalii câmp"` și text de ajutor real. | Nu |
| 3 | Înalt | `index.html` (8-13), `documente.html` (8,16) | Salt de nivel titluri: după `h1` (din `_cartus`) urmează direct `h2`, fără probleme; DAR în `dosar.html` panourile sub-tab folosesc `h3` (35,67) fără `h2` părinte → ordine ruptă (SC 1.3.1). | Adaugă un `h2` per tabpanel (ex. „Raport evaluare”) înainte de `h3`, sau ridică `h3`→`h2`. | Da |
| 4 | Înalt | `documente.html` (18-21) | `.doc-card` e `<a>` cu `<br>` și două `<span>`; numele accesibil = „titlu descriere” concatenat, fără rol de heading/listă → navigare grea la SR. | Înfășoară titlul în heading și grupează cardurile într-o listă (`<ul><li>`). | Nu |
| 5 | Mediu | `_nav_cross.html` (2-7) | `.cross-ui a`: text `--ink-2` (#3a4a60) pe `--paper-sunk` (#e9e2d0) ≈ 7:1 OK, dar link-urile NU sunt subliniate și se disting de text doar prin greutate → SC 1.4.1 (culoare singura) marginal; emoji „⇄/📄” fără text alt. | Adaugă `text-decoration:underline` la `.cross-ui a` + `aria-hidden` pe emoji. | Da |
| 6 | Mediu | `curent/dosar.html` (18-33) | Cele două `role="tablist"` (tabs + subtabs) nu au relație ierarhică expusă; sub-tab-urile sunt un al doilea tablist „orfan” vizual când tab-ul părinte nu e evident selectat. | Lasă `aria-label` distinct (deja există) + crește contrastul subtab (vezi #1) ca să se citească ierarhia. | Da |
| 7 | Mediu | `curent/dosar.html` (136-137) | Butonul „Generează” pornește `disabled`; starea „de ce e blocat” e doar vizuală (checkbox de asumare). `aria-describedby` trimite la caseta info, dar nu anunță tranziția activ/inactiv. | La `sincronAsumare()` setează și `aria-disabled` + un `role="status"` „Confirmă asumarea pentru a genera”. | Da |
| 8 | Mediu | `curent/incepe.html` (25-26) | Butoane „comercial” `disabled` cu `aria-disabled="true"` redundant pe element nativ disabled → SR nu le anunță deloc (disabled le scoate din focus); utilizatorul nu află că există funcția. | Folosește `aria-disabled="true"` FĂRĂ `disabled` nativ + handler care explică, sau marchează clar „indisponibil”. | Nu |
| 9 | Mediu | `curent/incepe.html` (77,86) | La import, `impBtn.textContent='📥 Se importă…'` înlocuiește conținutul → emoji devine text citit literal („telefon mobil cu săgeată”) la SR. | Pune statusul în `#import-status` (există, `aria-live`) și lasă textul butonului stabil. | Da |
| 10 | Mediu | `curent/dosar.html` (19-23) | Tab-urile au emoji decorativ în `<span aria-hidden>` (OK), dar eticheta vizibilă depinde de emoji pentru sens rapid; fără emoji unele titluri („AML”,„GDPR”) sunt acronime neexplicate. | Adaugă `title`/`abbr` sau text complet la prima apariție (ex. „AML (spălare bani)”). | Da |
| 11 | Mediu | `_design.css` (610) | Țintă tactilă: `button{min-height:24px}` și `.subtabs` au `padding:6px 14px` → înălțime efectivă ~30px, sub recomandarea 44px (SC 2.5.5 AAA; AA 2.5.8 cere 24px — trece la limită). | Crește `min-height:32px` global și padding subtab la `8px 16px`. | Da |
| 12 | Mediu | `curent/dosar.html` (84-91) | Câmpurile `comparabile`/`depreciere`/`elemente` sunt `<textarea>` cu sintaxă „;”/linie explicată doar în `<small class=hint>` neasociat prin `aria-describedby` (doar `elemente` are h-elemente). | Adaugă `aria-describedby` pe fiecare textarea către hint-ul său. | Da |
| 13 | Scăzut | `curent/cont.html` (26-28) | Checkbox-urile de format (`.fmt`) nu sunt grupate într-un `fieldset`/`legend` → relația „alege min 3 câmpuri” nu e expusă programatic. | Înfășoară `#campuri` în `<fieldset><legend>Format nume dosar</legend>`. | Da |
| 14 | Scăzut | `curent/dosar.html` (131-135) | Checkbox-ul de asumare (critic juridic) e doar `<label class=chk><input>`; fără `aria-describedby` spre consecință și fără indicare de obligativitate. | Adaugă `aria-required` vizual + leagă de `#gen-status`/explicație. | Da |
| 15 | Scăzut | `_design.css` (192,283) | `.chk` (#3a4a60 pe card) și `.cross-ui` text mic `.82rem`/`.84rem` → lizibilitate marginală; `.hint` `--ink-faint` (#5a6270) pe pastile colorate (badge) poate scădea sub 4.5:1. | Verifică `.hint`/`.chk` la ≥4.5:1; crește talie minimă text la `.875rem`. | Da |
| 16 | Scăzut | `curent/incepe.html` (49,52) | `<h3>⚠ Dosare dispărute</h3>` folosește emoji ca semnal de stare (SC 1.4.1) și butonul „scoate” are stil inline `font-size:.8rem` sub talie. | Adaugă text „Avertisment:” + scoate stilul inline, folosește `.ghost`. | Da |
| 17 | Scăzut | `_footer.html` (6-8) | Cifra demo „316.000,00 RON” și „v—” apar pe toate paginile ca text static fără context → zgomot pentru SR în `contentinfo`. | Marchează ca `aria-hidden` sau mută în comentariu dacă e doar decor. | Da |
| 18 | Scăzut | `index.html` (13,20) | Emoji „🆕/🧭” în `<h2>` cu `aria-hidden` (OK), dar `.badge b-high` „recomandat” e doar vizual; SR aud „recomandat” lipit de titlu fără separare. | Adaugă `<span class="sr-only">etichetă:</span>` sau virgulă. | Da |
| 19 | Scăzut | `_design.css` (321,277) | `:focus-visible` global OK (2px sienna), dar pe `.subtabs`/`.tabs` inelul de focus se poate suprapune cu bordura pală → vizibilitate slabă pe pastilele plate. | Adaugă `outline-offset:3px` explicit pe `[role=tab]:focus-visible`. | Da |
| 20 | Scăzut | `curent/dosar.html` (15,222-225) | Indicatorul „● salvat” folosește simbol „●/⚠/…” ca singur semnal de stare în `role=status` → SR citește caractere, nu sens clar. | Prefixează text: „Stare: salvat în folder”. | Da |

## Sub-tab-uri fără afordanță de buton — diagnostic + fix

**Diagnostic (owner are dreptate).** În `_design.css`:

- `.tabs [role=tab]` (264-275) stau pe un container cu `border-bottom:2px solid var(--brass)` și au bordură proprie + colțuri rotunjite sus → citesc clar ca file de dosar („folder tabs”). Activul are fill `--paper-card` care „taie” rigla de alamă. Afordanță bună.
- `.subtabs [role=tab]` (309-319) sunt pastile cu `background:var(--paper-sunk)` (#e9e2d0) așezate pe pagina `--paper` (#f2eee2). Diferența fill↔pagină e ~ΔL imperceptibil; `border:1px solid var(--line)` (#d7cdb4) are contrast < 3:1 față de pagină (sub pragul WCAG 1.4.11 pentru componente non-text). `box-shadow:none; transform:none` explicit → fără relief. Rezultat: inactivele arată ca **text simplu**, nu butoane; doar activul (fill sienna + text alb) pare control. De aici percepția „nu au butoane ca în UI-ul vechi”.

**Cauză.** Intenția din comentariul CSS („pastile discrete ca să nu concureze cu tab-urile”) a împins contrastul prea jos: bordura și fill-ul aleg tokeni aproape egali cu fundalul paginii.

**Fix concret (1 schimbare CSS, fără a atinge HTML/JS — auto-safe):**
```css
.subtabs [role=tab]{
  background:var(--paper-card);            /* card, nu sunk */
  border:1px solid var(--field-border);    /* ≥3:1 pe pagină (WCAG 1.4.11) */
  box-shadow:var(--emboss);                /* relief de control */
  min-height:32px; padding:8px 16px;       /* țintă tactilă */
}
.subtabs [role=tab]:hover{ box-shadow:var(--shadow); }
.subtabs [role=tab][aria-selected="true"]{ /* păstrează fill sienna existent */ }
```
Aceasta dă afordanță de buton inactivelor, păstrează ierarhia (tab > subtab) și nu schimbă comportamentul (pattern-ul ARIA tab/keyboard din `dosar.html` rămâne valid).

## Rezumat (top 5)

Owner are dreptate pe ambele puncte. (1) **Sub-tab-urile `.subtabs` nu au afordanță de buton**: fill `--paper-sunk` și bordura `--line` sunt cvasi-identice cu pagina (`--paper`), fără relief — inactivele par text simplu, spre deosebire de `.tabs` din `grila.html` care au cadru de „folder” pe rigla de alamă. Fix CSS pur, auto-safe. (2) **Popover-ul „?” (ajutor pe câmp) lipsește din UI-ul nou** — există doar marcatorul „!” de mapare UI-vechi, declarat temporar; câmpurile rămân fără context. (3) **Ordine titluri ruptă** în `dosar.html`: panourile sub-tab sar la `h3` fără `h2` părinte (SC 1.3.1). (4) **`.doc-card` din `documente.html`** e link-bloc cu `<br>`, fără heading/listă — navigare slabă la cititoare de ecran. (5) **Stări comunicate doar prin emoji/simbol** („●/⚠”, butoane comerciale `disabled`, emoji injectat ca text la import) — încalcă SC 1.4.1 și ascunde funcții. Majoritatea fix-urilor (14/20) sunt auto-safe (CSS/atribute).
