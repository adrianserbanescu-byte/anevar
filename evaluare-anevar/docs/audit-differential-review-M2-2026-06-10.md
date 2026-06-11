# Differential Review — M2 UI (sesiune-c vs master, commit 49de090)

> Skill: differential-review (trailofbits). Read-only. Diff: dosar.html + grila.html (M2 media top-N).
> Risc clasificat: MEDIUM (innerHTML cu valori + logică de valoare afișată; fără auth/crypto/transfer).

## Sumar
| Dimensiune | Verdict |
|------------|---------|
| Securitate (XSS) | ✅ CURAT — fără regresie |
| Corectitudine fallback indici_mediati | ✅ Solid (1 nit minor) |
| Acoperire teste | ⚠️ GAP — fără test commis pe logica M2 UeI |

## Findings

### F1 [INFO/LOW] grila.html — fallback `[d.index_selectat]` fără guard `||0`
`const mediati = (...) ? d.indici_mediati : [d.index_selectat];` (grila.html afiseaza).
`_indMed` din dosar.html are guard: `[d.index_selectat||0]`. Inconsistență minoră: dacă
`index_selectat` ar fi `undefined` (nu se întâmplă — motorul îl setează mereu), grila ar
produce `[undefined]` (fără highlight, fără crash). Defensiv. Recomandare: aliniere la `||0`.

### F2 [MEDIUM — test coverage] Logica M2 UI nu are test de regresie commis
Comportamentul critic „alertă prudențială pe TOATE comparabilele mediate" (concern B: pre-M2
comp 2/3 mai ajustate intrau în valoare dar scăpau de alertă) e verificat DOAR manual (Node).
Per metodologie, lipsa testului pe cod prudențial-critic = severitate elevată.
Recomandare: test e2e/unit care asertează (a) fallback !indici_mediati→[index_selectat],
(b) alerta listează TOȚI indicii mediati peste prag (nu doar index_selectat).

## Non-findings (verificat explicit)
- innerHTML din diff randează DOAR valori numerice/computate (indici int, parseFloat/Math.round,
  fmtRo) — niciun string scrape. escapeHtml/urlSafe pe descoperire/grila NEATINSE de diff.
- Alerta pe toate `indici_mediati` = corect implementată (rezolvă concern B).
- Calculul valorii e în motor (B); diff-ul atinge DOAR stratul de afișare.

## Blast radius
`afiseaza()` (grila.html) — toate 3 grilele (teren/casă/chirii). Cele 3 handlere dosar.html.
Contained la stratul de display (zero schimbare de calcul).

## Recomandare dispatch
F1 (nit) + F2 (test) = lane C (al meu, le pot face). Decizie A: cine repară + cine integrează.
