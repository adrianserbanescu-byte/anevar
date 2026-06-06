# Sinteză conformitate SEV 2025 — aplicația + planuri vs. standardul integral

> Audit de conformitate în 4 fluxuri pe `md files/standardele-de-evaluare-a-bunurilor-2025.md` (14.034 linii)
> vs. tot codul dezvoltat + planurile viitoare. Rapoarte detaliate: [`A-cadru-raportare.md`](A-cadru-raportare.md),
> [`B-abordari-metode.md`](B-abordari-metode.md), [`C-imobiliare-anexe.md`](C-imobiliare-anexe.md),
> [`D-garantare-adiacente.md`](D-garantare-adiacente.md). Bucket: **A**=îl pot face eu (cod, non-metodologie) ·
> **B**=evaluator senior (metodologie/praguri) · **C**=jurist. Actualizat: 2026-06-06.

## ✅ Scop extins (corecție Adi 2026-06-06, rulat în loop-ul special)
Auditul A-D a fost rulat (greșit) restrâns pe casă+teren+garantare. Aplicația suportă **toate tipurile × scopuri** (9 profile).
Re-rularea pe ÎNTREAGA matrice e acum livrată: **[`E-matrice-tip-scop.md`](E-matrice-tip-scop.md)** (5 tipuri × 5 scopuri).
Plus re-analiza juridică AML: **[`F-lege-norme-aml.md`](F-lege-norme-aml.md)** (Legea 129 + Norme ONPCSB).
- **E (matrice):** discrepanțele sunt de FRAMING (ghid GEV citat), toate **bucket B** — vârf: inversiunea
  `IMPOZITARE↔RAPORTARE_FINANCIARA` pe GEV_630/GEV_500 (asertată în teste → confirmi). Escaladat în `BLOCAT §G`.
- **F (AML):** toate pragurile corecte; „3.000 €" din auditul vechi **INFIRMAT**; eroare de citare disclaimer
  (art. 33 → art. 43/44/49) + 3 goluri GDPR — toate **bucket C** (jurist). Escaladat în `BLOCAT §H`.

## Verdict general
Aplicația e **solidă și în mare conformă**: raportul `.docx` urmează fidel scheletul SEV 106 + GEV 520, motorul
implementează corect cele 3 abordări, are anonimizare GDPR, alocare valoare, garduri prudențiale + urmă de audit.
**Niciun audit nu a găsit erori de aritmetică.** Golurile sunt de (a) **completitudine a raportului**, (b)
**metodologie de calibrat de un evaluator**, (c) **un blocaj de UI** pe anexe. Mai jos, lista unică prioritizată.

## 🔴 P0 — Conformitate care BLOCHEAZĂ acceptarea la bancă
| # | Gol | Bază standard | Stare | Bucket |
|---|-----|---------------|-------|--------|
| 1 | **Anexele foto/documente blocate în UI nou** (dosar.html „comercial"). **Backend-ul EXISTĂ** (`generator._adauga_anexe` l.505-542; wizardul le atașează funcțional) → deblocarea = **portare wizard→dosar**, nu dezvoltare. | GEV 630 §111.a.(1) l.6371 + l.5645; SEV 230 §120 | backend ✅ / UI nou ❌ | **A** (cod) + volum=**B/C** (tu) |
| 2 | **Declarația de conformitate e necondiționată** — raportul afirmă „conform SEV" chiar dacă validările cad. | SEV 106 §30.8 (l.2576) | 🟡 | **A** (gardă) — *dar wording = confirmă evaluator* |

## 🟠 P1 — Completitudine raport (Bucket A, le pot face; non-metodologie)
| # | Gol | Bază | Bucket |
|---|-----|------|--------|
| 3 | ✅ **REZOLVAT** — raportul citează acum tipul valorii + sursa (SEV 102/IVS 104) și transformă slug-ul „piata" în denumire lizibilă (`generator._tip_valoare_txt`) | SEV 102 §20.4 (l.754) + 106 §30.6(i) | A ✅ |
| 4 | **`tip_valoare` hardcodat + `TipValoare="lichidare"` cod mort** → nu se poate cere efectiv un tip ≠ piață | profil.py:12, meta.tip_valoare | A (plumbing) |
| 5 | **Profil IMPOZITARE → GEV_630 (vs GEV_500) și RAPORTARE_FINANCIARA → GEV_500** — pare inversat (GEV 500 = „valoarea impozabilă"), DAR e **asertat în teste** (`test_assembler_profil.py:51-52`) → intenționat/tested, NU bug accidental | profil.py:54-65 | **B** (confirmă evaluatorul: e intenționat sau de corectat?) |
| 6 | Date fizice imobiliare lipsă din UI nou (acces, utilități-distanțe, urbanism POT/CUT, act proprietate, tip drept + sarcini CF) | GEV 630 §16/§24/§28; SEV 230 §40/§140 | A (câmpuri) |
| 7 | Inspecția: amploare + neconcordanțe scriptic↔faptic + nume însoțitor + listă documente lipsă | GEV 630 §24/§44/§111.a.3 | A (câmpuri) |
| 8 | Recipisa BIG doar narativă (cerută ca element formal) | GEV 520 §83-84 | A (câmp) + extern |

## 🟡 P2 — Metodologie (Bucket B — alertăm, decide evaluatorul; NU atingem formula)
| # | Gol | Bază |
|---|-----|------|
| 9 | Neaplicarea unei abordări nu cere justificare + divergența/media mecanică între abordări nu e gardată | SEV 103 §40.3/§10.7/§10.9 |
| 10 | Selecția comparabilei = regulă unică „brută minimă" (alunecă spre AVM) | SEV 105 l.2388; A10.6(f) |
| 11 | Ajustări liniare (inclusiv suprafață) fără justificare obligatorie + lipsă gardă pe ajustarea NETĂ | SEV 103 §20.5, A10.8 |
| 12 | DCF: valoare terminală = sumă manuală, fără Gordon/exit; rată nedocumentată | A20.22-A20.34 |
| 13 | Cost: ignoră indirectele + profitul promotorului; depreciere pe vârstă cronologică liniară | A30.11-A30.19 |
| 14 | **Valoarea de lichidare: factor fix 0.85 auto-generat**; lipsesc cele 2 premise (ordonată/forțată) + declararea premisei (def. A60 schimbată 2025) | GEV 520 A120; SEV 102 A60 |
| 15 | Cost ca abordare PRINCIPALĂ la imobil fără gardă | GEV 520 §31/§34 |
> Pe acestea pot adăuga **ALERTE** (Bucket A, în spiritul „avertizăm, nu blocăm") fără să ating calculul: gardă de
> justificare ajustări nenule, prag de divergență la reconciliere, gardă pe ajustarea netă, alertă cost-primar-la-imobil.

## 🔵 P3 — Module adiacente / juridic (Bucket B/C — viitor, out-of-scope MVP)
| # | Gol | Bază | Bucket |
|---|-----|------|--------|
| 16 | **SEV 400 „Verificarea evaluării"** — absent integral (GEV 520 §18 îl invocă) | SEV 400 | modul viitor |
| 17 | Acord scris pe termenii de referință + disclaimer „asistare, nu AVM" + ESG real (nu hardcodat) | SEV 101 §20.2; SEV 105; SEV 104 ESG | C / B |

## Ce fac EU autonom acum (Bucket A, non-metodologie, cu teste)
1. **Fix bug framing IMPOZITARE → GEV 500** (#5) — clar greșit, scop non-MVP dar corectitudine.
2. **Citez sursa tipului valorii** în raport (#3) — aditiv.
3. **Plumbing tip_valoare** (#4) — permit selectarea tipului (piață/lichidare/etc.) fără a atinge factorul de lichidare (B).
4. **Alerte noi** (Bucket A) pentru #9/#11/#15 (avertizăm, nu blocăm) — după ce confirmi că vrei alerte noi.
5. Anexele (#1): backend gata; **aștept OK-ul tău pe re-încadrare** (era „comercial") înainte să portez UI-ul.

## Ce ESCALADEZ la tine (BLOCAT-pe-Adi)
- **#1 anexe** (re-încadrare P0 vs. comercial-pe-volum) · **#2 wording declarație conformitate** + #9-#15 metodologie
  (evaluator senior) · #16 SEV 400 + #17 acord scris/ESG (jurist/evaluator). Vezi `BLOCAT-pe-Adi.md`.
