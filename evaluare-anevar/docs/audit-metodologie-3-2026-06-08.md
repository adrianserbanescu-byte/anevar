# Audit #3 — Conformitate metodologică + corectitudine calcule (motor evaluare)

Data: 2026-06-08 | sesiunea B | read-only (audit de inginerie; validarea metodologiei = Adi/evaluator)
Module auditate: `engine/market.py`, `land.py`, `cost.py`, `reconciliation.py`, `validation.py`,
`abordari.py` (+ modele + teste existente: test_market/test_cost/test_reconciliation/test_chirie).

## Verdict general
Motorul e **structural sănătos** și aliniat la metodologia GBF/ANEVAR în 2 etape (tranzacție secvențial
→ proprietate aditiv), depreciere multiplicativă la cost, selecție pe ajustare brută minimă. **Formulele
de bază sunt corecte** (validate de testele existente). Nu am găsit bug-uri critice de calcul. Dar există
**inconsistențe + alegeri de metodologie** care trebuie validate de evaluator (Adi) înainte de lansare,
fiindcă afectează ce comparabil se selectează și valoarea finală.

---

## A. Întrebări de METODOLOGIE pentru Adi (NU le decid eu — bucket evaluator)

### M1 [MAJOR] — Selecția la TEREN ignoră ajustările valorice (EUR)
`land.ajustare_bruta` (criteriul de selecție) însumează **doar** ajustările **procentuale** de proprietate
și **ignoră** cele **valorice (EUR)**. La PIAȚĂ (`market.ajustare_bruta`) se numără **ambele** (pct + EUR/bază).
Efect: un comparabil de teren cu o ajustare EUR mare îi e *aplicată* la preț (`pret_mp_corectat` o include),
dar **NU e penalizat la selecție** → poate fi ales drept „cel mai puțin ajustat" deși nu este.
**Întrebare:** la teren, criteriul de selecție trebuie să includă și ajustările valorice (EUR), ca la piață,
sau e intenționat doar pe procentuale? (`land.py:48` vs `market.py:60`)

### M2 — Selecție pe UN singur comparabil (min ajustare brută)
Ambele grile aleg **un singur** comparabil (cel cu ajustarea brută minimă) și iau valoarea lui corectată,
NU o medie/reconciliere a primelor N. **Întrebare:** e regula GBF/ANEVAR intenționată (un comparabil), sau
vrei reconciliere a top-2/3? (`market.py:96`, `land.py:69`)

### M3 — Ponderea implicită piață/cost la reconciliere = 50/50
`reconcile(pondere_piata=0.5)` — la metoda „ponderată", 50% piață + 50% cost. Pentru **garantarea creditelor
(GEV 520)** abordarea prin piață e de regulă dominantă. **Întrebare:** ce pondere implicită vrei (ex. 70/30
piață/cost), sau rămâne alegere per-dosar? (`reconciliation.py:17`)

### M4 — Depreciere la cost: multiplicativă
`CIN = CIB·(1−Dfn)·(1−C_nf)·(1−C_ex)` (deduceri multiplicative/secvențiale). **Întrebare:** confirmi
multiplicativ (nu aditiv)? + sursa tabelului de depreciere fizică e cea agreată (GEV 630)? (`cost.py:53`)

### M5 — Praguri de validare
`validation.py`: limită ajustare brută **25%**, outlier la **50%** deviație de mediană, **min 3** comparabile.
**Întrebare:** sunt pragurile conforme cu SEV 2025/GEV 520 (în special 25% și 50%)? (`validation.py:16-18`)

---

## B. Constatări de INGINERIE (le pot repara după ce confirmi că nu schimbă metodologia)

### E1 [minor] — Rotunjire inconsistentă la reconciliere
`reconcile()` ramura „ponderată" **NU rotunjește** valoarea finală, dar `reconcile_profil()` rotunjește la
`0.01`. Cele două funcții ar trebui să fie consistente. Dar *politica de rotunjire* a valorii finale (la cent?
la 100/1000 EUR, cum cer rapoartele?) = decizie de metodologie — confirmă pragul. (`reconciliation.py:57` vs `:92`)

### E2 [minor] — Comparabilele de TEREN nu sunt validate
`valideaza_comparabile` (outlier 50% + limită 25% + min 3) rulează **doar pe comparabilele de casă**
(`Comparable`), nu și pe cele de teren (`LandComparable`). Terenul n-are check de outlier/limită.
Recomand un `valideaza_comparabile_teren` echivalent (folosind pragurile confirmate la M5).

### E3 [nit] — Parametru mort
`evaluate_market(suprafata_subiect=...)` nu mai e folosit în formulă (păstrat „pt compatibilitate"), dar e
threadat prin `abordare_comparatie`. Curățenie minoră. (`market.py:89`)

---

## Recomandare
- **M1–M5 = pe Adi** (validare metodologică). După răspunsuri, implementez fix-urile validate (M1 e cel mai
  important — afectează selecția comparabilului de teren).
- **E1–E3** le repar după ce M1/M5 sunt confirmate (E1 depinde de politica de rotunjire, E2 de praguri).
- Niciun bug critic de calcul; lansarea nu e blocată tehnic, dar M1 + pragurile (M5) merită confirmate
  înainte ca rapoartele să fie folosite la garantare.
