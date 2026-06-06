# Sinteză audituri — UI nou + refresh (2026-06-06)

5 audituri rulate pe starea curentă (rapoarte individuale alături): a11y, UX-copy, design-critique,
tehnic-refresh, calitate-cod. Mai jos: **ce am reparat deja** (auto-safe) și **ce rămâne** (parcat
pentru decizie sau ca datorie tehnică). Lucrurile care depind de tine → [`BLOCAT-pe-Adi.md`](../BLOCAT-pe-Adi.md).

## ✅ Reparat în această iterație (auto-safe, testat — 487 teste)
| # | Din audit | Fix |
|---|-----------|-----|
| 1 | **calitate-cod (Înalt, securitate)** | `md_to_html`: XSS prin `href` — acum URL-urile sunt filtrate (`javascript:`/`data:` blocate, ghilimele escapate). +test |
| 2 | **a11y + design (Înalt)** | `md_to_html` cobora titlurile +1 nivel → corpul documentului nu mai are `<h1>` (gata cu dublul h1 și cu kicker-ul de brand „GBF…" injectat în mijlocul textului). +test |
| 3 | **calitate-cod (Mediu)** | `md_to_html` suportă blocuri de cod ` ``` ` (apăreau literal într-un document livrat). +test |
| 4 | **tehnic (Înalt)** | rând orfan în SQLite: «Calculează» din UI nou chema `/api/evaluare` (care `storage.save` la fiecare clic). Acum `/api/dosar/{uid}/calcul` = calcul fără persistență. +test |
| 5 | **tehnic (Mediu)** | scriere atomică (`os.replace`) pentru `dosar.json` + `_index.json` (anti-coruptie la crash) |
| 6 | **design (Înalt)** | `.alegere .card` nedefinit + `article.document` nestilizat → adăugate stiluri (carduri cu fundal/bordură, scope document fără ornamentele globale, blockquote sienna, `<pre>`) |
| 7 | **a11y (Înalt)** | landmark duplicat: nav-ul din subsol are acum nume distinct („Comută interfața (subsol)") |
| 8 | **a11y (Înalt)** | butonul «Generează» blocat → `aria-describedby` spre motivul asumării |

## 🟡 Rămas — datorie tehnică (auto-safe, dar mai mare; le fac în iterații viitoare)
- `listeaza()` scanează N fișiere `dosar.json` la fiecare `/incepe` → cache pe mtime (folosește `_index.json` ca să eviți rescanarea). *Scalabilitate la sute de dosare.*
- `asambleaza()` (JS) dublează `EvaluationInput` și **omite** `land_comparables`, `pondere_piata`, `date_venit`, `date_dcf`, `photos`, `documente` → metodele venit/DCF + anexele foto/doc nu-s accesibile din UI nou (vezi paritatea wizard, mai jos).
- `except Exception` prea largi în câteva locuri (înghit erori) → îngustare + logging.
- Retenție versiuni `.docx` în folderul dosarului (acum cresc nelimitat).
- Fișiere temporare cu nume controlat de uid/client în `gettempdir()` → coliziuni posibile.

## 🟠 Rămas — UX/design (impact mic, dar cer o decizie minoră)
- `.cross-ui` apare de 2× pe pagină (antet dreapta + subsol centrat) — **cerut explicit de tine** (linkuri în header+footer). Design-ul recomandă în antet doar „⇄ Schimbă interfața" + instanța „tare" în subsol. *Decizie: păstrăm ambele complete sau simplificăm antetul?*
- Emoji (🆕🧭📄) ca iconografie primară vs. SVG topograf — de înlocuit pe termen mediu.
- Badge „recomandat" e chihlimbar (`b-mid` = „atenție" în scala proprie) → ar trebui verde (`b-high`).
- Jargon de dev expus userului (popover „!", „folder/disc", „output-first", „DRAFT", CIN/CIB/IROVAL) — popover-ul „!" e oricum temporar (B8).

## Paritate wizard (recheck) — ce NU acoperă încă UI-ul nou
UI-ul nou acoperă: identitate, date fizice (teren/Au/Acd/an), elemente cost, depreciere, comparabile
(preț;supr), metodă cost/piață/ponderată, generare `.docx`. **Lipsesc față de wizard:** grila de
**teren** (land_comparables), **chirii→venit/DCF**, **ponderea piață** explicită, **anexa foto** și
**scanuri documente** (ingestie PDF). Acestea există în motor + în wizard, dar `asambleaza()` nu le
trimite. → de adăugat în UI nou (datorie de paritate, nu pierdere de funcționalitate).
