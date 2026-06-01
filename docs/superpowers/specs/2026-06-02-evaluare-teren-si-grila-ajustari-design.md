# Evaluare teren prin comparație + grila de ajustări — Design

**Data:** 2026-06-02
**Status:** Draft pentru review
**Context:** Aliniere a motorului de calcul la grilele reale GBF (4 seturi de referință analizate:
Maneciu, Brașov, Bușteni, Breaza). Sursă: rapoarte + foi de calcul reale.

---

## 1. Constatări din grilele reale (ancorate în celule)

### Grila de teren (standardizată în toate 4 fișierele)
- **3 comparabile**, preț în **EUR/mp**.
- **17 elemente de ajustare, toate procentuale** (fără EUR absolut), aplicate **secvențial** pe
  prețul curent, în ordine fixă:
  1. Ofertă→Tranzacție (−5%/−10%) · 2. Drept proprietate · 3. Finanțare · 4. Condiții vânzare ·
  5. Cheltuieli post-vânzare · 6. Condițiile pieței (timp) · 7. Localizare · 8. Acces · 9. Utilități ·
  10. Suprafață · 11. Deschidere (front stradal) · 12. Înclinație · 13. Tip teren · 14. Document
  urbanistic · 15. Regim juridic (intravilan/extravilan) · 16. Regim economic (destinație) ·
  17. Indicatori urbanism (CUT/POT) · (+ Alte elemente).
- **Indicatori:** ajustare brută %, ajustare netă %, nr. ajustări.
- **Selecție: comparabilul cu ajustare brută minimă** (marcat „x").
- **Valoare teren** = preț_unitar_ales (EUR/mp) × suprafață_subiect (mp); + echivalent Lei la curs BNR.

### Grila de casă — ce e mai bogat decât motorul nostru actual
Pe lângă ajustările ierarhice procentuale, are și **ajustări valorice (EUR absolut)** și elemente
suplimentare:
- **Ajustare negociere** (−5%/−10%) ca **prim pas** separat.
- **Componente non-imobiliare** (mobilier: −2.000…−10.000 EUR) — valorică.
- **Suprafață teren**: ajustare valorică = `EUR/mp × Δmp` (nu procentual).
- **Arie utilă**: ajustare valorică = `preț_unitar_comparabilă × Δmp_utili`.
- **PIF/vechime** — element separat procentual.
- **Curte**, **Sistem încălzire** — elemente separate procentuale.
- **Alte elemente** (garaj, anexe) — valorice.

### Concluzia cheie
Motorul nostru actual e prea simplu: comparabilele se introduc doar ca `preț;suprafață` și se compară
**brut**. Grila reală aplică **multe ajustări per comparabil**. Trebuie să expunem **grila de ajustări**.
Și mecanica grilei de teren = mecanica grilei de casă → **reutilizăm același motor**.

---

## 2. Scop (acest spec)

1. **Modul nou: evaluare teren prin comparație** — grilă proprie de teren (3 comparabile, ajustări %),
   care înlocuiește `valoare_teren` introdus manual.
2. **Îmbogățirea grilei de comparație** (casă + teren) cu **ajustări per element** (procentuale și
   valorice), aplicate secvențial, cu selecția pe ajustare brută minimă (deja implementată).

Aliniere la structura reală GBF. NU schimbăm abordarea prin cost (CIN) și nici reconcilierea.

---

## 3. Arhitectură (reutilizare maximă)

Motorul `engine/market.py` deja: calculează preț unitar, aplică `adjustments` (procentuale ȘI
valorice) secvențial, calculează ajustare brută/netă, selectează comparabilul cu ajustare brută
minimă. **Această mecanică e exact grila reală.** Deci:

- **`engine/land.py`** (NOU) — `evaluate_land(comparabile_teren, suprafata_subiect) -> GridResult`:
  identic cu `evaluate_market`, dar prețul de pornire e **EUR/mp direct** (nu preț/suprafață), iar
  valoarea = preț_unitar_corectat × suprafață_subiect. Reutilizează aplicarea ajustărilor și selecția.
- **Model `LandComparable`** (extindere): preț_mp, suprafață, + `adjustments: list[Adjustment]`
  (toate procentuale pentru teren). Modelul `Adjustment` (procentuală/valorică) există deja.
- **Grila de casă**: `Comparable` are deja `adjustments`; le folosim efectiv (acum sunt goale).
  Definim un set standard de **elemente de ajustare** (catalogul de mai sus) pe care UI-ul le expune.

---

## 4. Catalogul de elemente de ajustare (standard, editabil)

Pentru consistență cu rapoartele, definim seturile standard de elemente:

**Teren (toate procentuale):** ofertă→tranzacție, drept proprietate, finanțare, condiții vânzare,
cheltuieli post-vânzare, condițiile pieței, localizare, acces, utilități, suprafață, deschidere,
înclinație, tip teren, document urbanistic, regim juridic, regim economic, CUT/POT.

**Casă:** negociere (%), componente non-imobiliare (EUR), drept proprietate (%), finanțare (%),
condiții vânzare (%), condițiile pieței (%), localizare (%), suprafață teren (EUR/mp×Δ),
arie utilă (EUR), destinație (%), PIF/vechime (%), acces (%), curte (%), finisaje (%),
sistem încălzire (%), alte elemente (EUR).

Evaluatorul completează valoarea fiecărui element per comparabil (gol = 0, neaplicat).

---

## 5. UI — grila de ajustări

Provocarea: introducerea unei grile complete e mai complexă decât `preț;suprafață`. Propunere
pragmatică, în 2 niveluri:

- **Nivel simplu (rapid, ca acum):** doar `preț;suprafață` → comparație brută (fără ajustări).
  Util pentru o estimare rapidă. Rămâne disponibil.
- **Nivel grilă (nou):** un tabel editabil — rânduri = elementele de ajustare standard, coloane =
  comparabilele (3). Evaluatorul introduce procentul/valoarea per celulă. Aplicația calculează prețul
  corectat, ajustarea brută, și marchează comparabilul ales. Separat pentru **teren** și **casă**.

În wizard: un buton „Grilă detaliată" deschide tabelul; comparabilele descoperite pre-populează
prețul/suprafața, evaluatorul adaugă ajustările.

---

## 6. Integrarea cu ce există

- **Valoarea terenului** (din grila de teren) → înlocuiește `valoare_teren` manual în abordarea prin
  cost (`valoare_cost = CIN + valoare_teren`) și apare în raport.
- **Reconcilierea** rămâne: proprietate prin comparație vs prin cost.
- **Alocarea valorii** (din rapoarte): V_construcții = V_proprietate − V_teren — o adăugăm la
  rezultate (utilă în raport).
- Descoperirea de comparabile (existentă) poate pre-popula AMBELE grile (teren și casă) cu
  preț/suprafață; ajustările le pune evaluatorul.

---

## 7. Non-goals

- Nu schimbăm abordarea prin cost (CIN segregat) — rămâne.
- Nu automatizăm valorile ajustărilor (evaluatorul le introduce; eventual sugestii ulterior din
  breakdown-ul de descoperire).
- Template-ul de raport .docx (shell GBF) — spec separat, ulterior.
- Curs BNR live — momentan introdus manual (ulterior, modul de indici).

---

## 8. Pași de implementare (rezumat)
1. `LandComparable` cu adjustments + `engine/land.py` (`evaluate_land`) — TDD, regresie pe grila
   reală (ex. Maneciu: 15.77 EUR/mp × 2776 = 44.000 EUR).
2. Catalog elemente standard (teren + casă) ca date.
3. Wire valoare_teren_calculată în cost + alocare în rezultate.
4. UI grilă detaliată (tabel ajustări) — teren și casă.
5. Regresie pe cele 4 seturi reale (valori reproduse).

---

## 9. Test de regresie (din grilele reale)
| Set | Teren ales | Preț/mp | Supr. | Valoare teren |
|---|---|---|---|---|
| Maneciu | Comp A (14%) | 15.77 | 2776 | 44.000 EUR |
| Brașov | Comp B (15%) | 96.68 | 808 | 78.000 EUR |
| Bușteni | Comp A (8%) | 111.72 | 305 | 34.000 EUR |
| Breaza | Comp C (5%) | 74.81 | 900 | 67.000 EUR |

Motorul de teren trebuie să reproducă aceste valori din ajustările reale.
