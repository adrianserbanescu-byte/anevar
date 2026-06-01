# Modul „Descoperire comparabile" (Conectivitate date externe) — Design

**Data:** 2026-05-31
**Status:** Draft pentru review
**Autor:** Adrian Șerbănescu (cu asistență Claude Code)
**Context:** Subsistemul „Conectivitate date externe" din specificația MVP. Construit peste
aplicația existentă (Planurile 1-4). Modul nou, cu spec + plan proprii.

---

## 1. Scop

Aplicația **descoperă și propune** comparabile relevante pentru casa evaluată (caută anunțuri,
extrage date verificate, le potrivește pe caracteristici, le rankează), iar **evaluatorul
selectează și confirmă**. „Asistă căutarea", NU „pilot automat" — evaluatorul rămâne responsabil
legal pentru comparabilele alese.

---

## 2. Constatări din spike (validate pe date reale, 2026-05-31)

Decizii fundamentate pe un experiment cu API Perplexity și portaluri reale (zona Otopeni):

| Test | Rezultat | Concluzie |
|---|---|---|
| Perplexity → URL-uri de anunțuri | întoarce doar pagini de **căutare/categorie** | Nu dă anunțuri individuale |
| Perplexity → date structurate (JSON) | JSON plauzibil, dar **3/4 URL-uri = 404, fabricate** | **Periculos** — fabrică date |
| Căutare directă portal (imobiliare.ro / storia.ro) | **HTTP 200**, **33 + 6** anunțuri reale extrase | **Viabil** |
| Parser pe anunț individual real | accesibil, dar prinde ~1/3 preț, 0/3 suprafață | Parserul trebuie **întărit** |

### Lecția de aur (principiu de design)

- **LLM care *caută / inventează* date → interzis.** Perplexity a fabricat anunțuri inexistente cu
  prețuri și materiale. Inacceptabil pentru un document bancar.
- **LLM care *extrage* din text pe care i-l dăm noi → permis.** Ancorat în realitate, verificabil.

Prin urmare: **descoperirea comparabilelor se face prin scraping direct** (verificabil), iar **LLM-ul
e folosit DOAR pentru extragerea atributelor din descrierea reală** a fiecărui anunț descărcat.

---

## 3. Arhitectura (pipeline)

```
Intrare de la evaluator: localitate/zonă, tip (casă+teren), suprafață construită ~,
                          + atribute secundare (text liber, vezi 5.2)
   │
   ▼
1. Construiește URL de căutare pe portal     (imobiliare.ro / storia.ro)
   ▼
2. Descarcă pagina de căutare → extrage URL-urile anunțurilor individuale   [dovedit: 33 + 6]
   ▼
3. Pentru fiecare anunț: descarcă pagina → parser ÎNTĂRIT → preț + suprafață VERIFICATE
      (JSON-LD + og:meta + titlu + __NEXT_DATA__; vezi 4)
   ▼
4. LLM extrage atributele din descrierea reală a anunțului
      (primare: an, stare, finisaj, încălzire, teren; secundare: definite de user)
   ▼
5. Scor de similaritate față de casa subiect (pe atributele primare)
   ▼
6. Listă RANKATĂ cu „match breakdown" (ce se potrivește / diferă / lipsește)
   ▼
7. Evaluatorul bifează comparabilele dorite → intră în grila de comparație existentă
```

Piesele existente reutilizate: `importers/url_parser.py` (de întărit), `models/comparable.py`,
grila din `engine/market.py`, anonimizatorul GDPR (datele trimise spre LLM sunt descrieri publice
de anunț — fără date personale ale clientului).

---

## 4. Parser întărit (extragere preț + suprafață)

Parserul actual citește doar `floorSize` schema.org → prea îngust. Se extinde cu fallback-uri,
în ordine, până găsește valoarea:
1. JSON-LD `offers.price` / `floorSize` (când există)
2. `__NEXT_DATA__` (blob JSON Next.js — imobiliare.ro/storia.ro sunt Next.js)
3. Meta Open Graph (`og:title`, `product:price:amount`)
4. Regex pe titlu/descriere (`\d+ mp`, `\d[\d.\s]* (eur|euro|€|lei)`)

Fiecare valoare extrasă păstrează **sursa** (din ce câmp a venit), pentru trasabilitate.
Dacă preț sau suprafață lipsesc după toate fallback-urile → anunțul e marcat „incomplet" și
afișat ca atare (evaluatorul completează manual sau îl ignoră).

---

## 5. Modelul de atribute

> **REGULĂ FERMĂ:** DOAR cele 5 atribute primare intră în ranking. Toate atributele secundare
> sunt strict **FYI (informative)** și **NU influențează în niciun fel scorul sau ordinea**
> candidaților. Ranking-ul = funcție exclusiv de cele 5 primare.
>
> **TRANSPARENȚĂ (toate atributele):** pentru **fiecare** atribut — primar SAU secundar — se
> afișează **valoarea exactă regăsită în anunț** (dovada). La primare, valoarea găsită alimentează
> scorul ȘI se afișează; la secundare doar se afișează. Ce nu apare în text → „nementionat".

### 5.1 Atribute primare (scorate, determină ranking-ul)

Ordinea de prioritate (cât mută prețul), **confirmată de evaluator — de revizuit ulterior dacă e cazul**:

1. **Suprafață construită** (suprafața casei, ex. Acd — driver major de comparabilitate; pondere 5, alimentată din suprafața reală a anunțului prin parser, nu LLM)
2. **An construcție** (pondere 5)
3. **Stare construcție** (separată de an: o casă veche renovată ≠ una nouă neîntreținută)
4. **Nivel finisaj**
5. **Tip încălzire**
6. **Suprafață teren**

(Notă: modelul a fost extins de la 5 la 6 atribute primare — s-a adăugat suprafața construită a casei.
Total ponderi = 20. Pragurile/ponderile rămân „de revizuit ulterior".)

Pentru fiecare atribut primar, LLM-ul întoarce **valoarea regăsită în anunț** (ex. an=2008,
stare=„renovată 2021", finisaj=„lux", încălzire=„centrală pe gaz", teren=450 mp), sau
„nementionat" dacă lipsește. Această valoare **se afișează** în match breakdown (dovada) **și**
intră în scorul de similaritate. Un atribut primar „nementionat" e tratat ca necunoscut (nu ca
nepotrivire) și semnalat evaluatorului spre completare manuală.

Plus filtrul de bază (must-have, nu se scorează — definesc setul de candidați): localitate/zonă,
tip (casă+teren), suprafață construită aproximativă.

### 5.2 Atribute secundare (definite de user, informative)

Evaluatorul scrie într-un text box, **câte unul pe linie**, în format `atribut: valoare_dorită`
(ex. `tamplarie: termopan`, `garaj: da`, `panouri solare`). Valoarea dorită e opțională.

Pentru fiecare candidat, LLM-ul caută atributul în descrierea reală și raportează **trei stări**.
Pentru „potrivit" și „diferit", afișează și **valoarea exactă găsită în anunț** (dovada), ca
evaluatorul să vadă pe ce se bazează verdictul:

| Stare | Sens | Ce se afișează |
|---|---|---|
| ✅ Potrivit | atributul e menționat și valoarea corespunde celei dorite | valoarea găsită (ex. „termopan PVC") |
| ⚠️ Diferit | atributul e menționat, dar cu altă valoare | valoarea găsită (ex. „tâmplărie lemn") |
| ➖ Nementionat | descrierea nu pomenește atributul | — (nimic) |

Exemplu pentru `tamplarie: termopan` pe un candidat: `⚠️ Diferit — găsit în anunț: „tâmplărie lemn stratificat"`.

**Decizie (fermă):** atributele secundare sunt **exclusiv FYI** — semnalizatoare afișate în „match
breakdown" pentru informarea evaluatorului. Ele **NU intră în scor și NU influențează ranking-ul**
sub nicio formă. Ranking-ul este determinat **doar de cele 5 atribute primare**. Motiv: secundarele
sunt variabile și des „nementionate"; scorarea lor ar reintroduce zgomot. (Ajustabil ulterior doar
dacă evaluatorul cere explicit influență pe ranking.)

### 5.3 Scoringul și ranking-ul

**Scopul scorului:** o euristică de *proximitate* care propune candidații, NU un model de evaluare.
Valoarea reală se face în grila de comparație (corecțiile), cu evaluatorul ca decident final. Scorul
trebuie doar să fie rezonabil și explicabil.

**Pas 1 — dissimilaritate per atribut** `d ∈ [0,1]` (0 = identic, 1 = complet diferit). Fiecare
atribut are o **pondere** și o **cotă** (cât cântărește din formula finală când toate 5 sunt cunoscute;
cotă = pondere / 15):

| # | Atribut | Pondere | Cotă (din total) | Formula `d` (pe valoarea găsită) | Exemplu |
|---|---|---|---|---|---|
| 1 | An construcție | **5** | **33%** | `d = min(\|an_subiect − an_anunț\| / 25, 1)` | \|2013−2008\|/25 → 0.20 |
| 2 | Stare | **4** | **27%** | `d = \|treaptă_subiect − treaptă_anunț\| / 4` (5 trepte: 1=degradată…5=nouă) | \|3−4\|/4 → 0.25 |
| 3 | Nivel finisaj | **3** | **20%** | `d = \|treaptă_subiect − treaptă_anunț\| / 3` (4 trepte: 1=modest…4=lux) | standard vs lux → 0.67 |
| 4 | Tip încălzire | **2** | **13%** | `d = 0` aceeași / `0.5` înrudită / `1` fundamental diferită | centrală gaz vs pompă → 0.5 |
| 5 | Suprafață teren | **1** | **7%** | `d = min(\|teren_subiect − teren_anunț\| / teren_subiect, 1)` | \|500−450\|/500 → 0.10 |

**Pas 2 — combinare ponderată**, **doar peste atributele CUNOSCUTE** (cele „nementionat" se exclud
și ponderile rămase se renormalizează automat):
```
dissimilaritate = Σ(pondere_i × d_i) / Σ(pondere_i)     // i parcurge doar atributele cunoscute
Relevanță (%)    = round( 100 × (1 − dissimilaritate) )
```
Ranking: descrescător după Relevanță (cel mai mare = cel mai similar = sus).

**Pas 3 — tratarea atributelor primare „nementionat":**
- Un atribut primar necunoscut **NU se penalizează** (necunoscut ≠ nepotrivire). Se **exclude** din
  sumă, iar ponderile se renormalizează peste atributele cunoscute.
- Candidatul afișează explicit **„scor bazat pe X/5 atribute"**, ca evaluatorul să știe pe ce date stă scorul.
- **Prag de încredere:** dacă **≥3 din 5 primare sunt „nementionat"**, candidatul e marcat
  **„date insuficiente — verifică manual"** și nu concurează la vârf pe baza unui scor slab fundamentat.

**Exemplu de afișare (un candidat) — fiecare atribut cu valoarea găsită, `d`, ponderea și
contribuția (pondere × d); lângă relevanța finală, formula exactă cu numerele:**
```
RELEVANȚĂ 86%  (bazat pe 4/5 atribute — Teren nementionat)
Formula: 100 × (1 − (5×0.20 + 4×0.25 + 3×0.00 + 2×0.00) / (5+4+3+2))
       = 100 × (1 − 2.00/14) = 100 × (1 − 0.143) = 86%

  Atribut    Valoare găsită     d      pondere  contribuție(pondere×d)
  An         2008 (subiect 2013) 0.20   5        1.00
  Stare      "renovat 2021"      0.25   4        1.00
  Finisaj    "lux"               0.00   3        0.00
  Încălzire  "centrală gaz"      0.00   2        0.00
  Teren      ➖ nementionat       —      (exclus) —
  ────────────────────────────────────────────────────
  Σ contribuții = 2.00 ;  Σ ponderi cunoscute = 14 ;  dissim = 0.143
```
Notă: când un atribut e „nementionat", ponderea lui iese din numitor (aici 14 = 5+4+3+2, fără
ponderea 1 a terenului), deci formula afișată conține mereu exact ponderile atributelor cunoscute.

**Calibrare:** toate pragurile și ponderile (cei 25 de ani la „an", treptele de stare/finisaj,
ponderile, pragul de 3/5) sunt **valori implicite, de calibrat de evaluator — de revizuit ulterior**.
Mapările ordinale (text liber „stare"/„finisaj" → treaptă) se fac tot prin LLM, pe baza descrierii.

### 5.4 Cerință UI: tabel de metodologie ÎNAINTE de rezultate

În pagina de descoperire, **înainte de lista candidaților individuali**, se afișează o singură dată
un **tabel de metodologie** care explică cum se scorează — fiecare atribut primar cu **formula
exactă pe valoarea găsită, ponderea și cota din total**:

| # | Atribut | Pondere | Cotă | Formula `d` |
|---|---|---|---|---|
| 1 | An | 5 | 33% | `min(\|an_subiect − an_anunț\| / 25, 1)` |
| 2 | Stare | 4 | 27% | `\|treaptă_subiect − treaptă_anunț\| / 4` |
| 3 | Finisaj | 3 | 20% | `\|treaptă_subiect − treaptă_anunț\| / 3` |
| 4 | Încălzire | 2 | 13% | `0 / 0.5 / 1` |
| 5 | Teren | 1 | 7% | `min(\|teren_subiect − teren_anunț\| / teren_subiect, 1)` |

Sub tabel: nota „Relevanță = 100 × (1 − Σ(pondere×d)/Σ(ponderi cunoscute)); atributele «nementionat»
sunt excluse din calcul." Apoi urmează candidații, fiecare cu propriul breakdown și câmpul
`explicatie`. Astfel cititorul înțelege metodologia **o dată sus**, apoi fiecare rezultat individual.

---

## 6. Rolul LLM-ului

- **Doar extracție din text furnizat** (descrierea reală a anunțului descărcat). Niciodată căutare
  sau generare de date despre proprietăți.
- Prompt: „din acest text de anunț, extrage {atribute}; pentru ce nu apare, întoarce «nementionat»".
- Întoarce date structurate (JSON validat) cu `valoare_gasita` (textul exact din anunț) pentru
  **fiecare atribut, primar și secundar**; `null` când nu apare. La cele secundare se adaugă și
  `stare` (potrivit/diferit/nementionat, prin comparație cu valoarea dorită de evaluator).
- Toate valorile regăsite sunt afișate evaluatorului ca dovadă — trasabilitate completă.
- Provider: configurabil prin clientul injectabil existent. Pentru această sarcină (extracție
  ancorată) orice LLM e potrivit, inclusiv Perplexity sonar. Pentru **narativ** se păstrează Claude
  ca implicit (tendința de halucinare a Perplexity e un steag galben pentru proză liberă).

---

## 7. Riscuri asumate

- **Anti-bot / rate-limiting:** azi paginile s-au descărcat cu un User-Agent simplu (HTTP 200), dar
  la volum portalurile pot bloca; posibil să fie nevoie de Playwright (headless) și throttling.
- **Fragilitatea parserului:** layout-ul portalurilor se schimbă; fallback-urile multiple reduc
  riscul, dar întreținerea e necesară.
- **Termeni și Condiții / legal:** scraping-ul direct poate încălca ToS-ul site-urilor. Folosit pe
  răspunderea evaluatorului (decizie asumată explicit).
- **Acoperire variabilă:** unele zone/anunțuri au descrieri sărace → atribute „nementionate" multe.

---

## 7.5 Conectarea cu modulul de calcul deja dezvoltat

Modulul de descoperire **nu modifică** motorul de calcul existent — îl alimentează. Punctul de
cuplare este modelul `Comparable` (Planul 1) și funcția `to_comparable()` (Planul 4):

```
Descoperire (search → parse → score → rank)
   → evaluatorul bifează candidații doriți
   → fiecare candidat → to_comparable()  [funcție existentă]  → pret + suprafață
   → lista `comparables` din EvaluationInput  [existent]
   → evaluate_market / grila de comparație  [existent, neatins]
   → reconciliere → raport .docx  [existent]
```

Trei punți:
1. **Date (preț/suprafață):** `ParsedListing → to_comparable()` produce un `Comparable` standard.
   Descoperirea reutilizează exact acest seam → **zero schimbare** în motorul de piață/grilă.
2. **Profilul subiectului fără re-introducere:** `SubjectProfile` se derivă din datele deja
   introduse (an din `BuildingData.an_pif`/an construcție, teren din `LandData.suprafata`); doar
   atributele noi (stare, treaptă finisaj, categorie încălzire) se cer suplimentar.
3. **Breakdown-ul ghidează corecțiile din grilă:** unde `d > 0` (ex. finisaj diferit) → semnal că
   acolo se aplică o corecție în grilă (elementul „caracteristici fizice"/„finisaje"). **Valoarea
   corecției o pune evaluatorul** — scorul NU generează ajustări automat.

**Principiu:** scorul de descoperire e pentru **selecție**; valoarea finală vine din grilă (corecții)
+ reconciliere, **neschimbate**. Descoperirea înlocuiește doar pasul „caut manual comparabile".

---

## 8. Non-goals (excluse din acest modul)

- **Pilot automat** (selecție de comparabile fără confirmarea evaluatorului)
- **Perplexity ca sursă de comparabile** (respins pe dovezi — fabrică date)
- **ANCPI / e-Terra** (date de tranzacție reale — valoroase, dar acces instituțional; modul separat, amânat)
- **Indici BNR (RPPI)** — câștig ușor, dar e o sarcină separată (alimentează corecția „timp" din grilă)
- Scorare pe atribute secundare (rămân informative)

---

## 9. Decizii înregistrate (pentru pagina web a modulului)

- **Doar cele 5 atribute primare intră în ranking** (an · stare · finisaj · încălzire · teren) — *de revizuit ulterior*.
- Atribute secundare: text liber, definite de user, raportate în 3 stări — **strict FYI, fără influență asupra ranking-ului**.
- Provider LLM extracție: configurabil; narativ implicit Claude.

---

## 10. Pasul următor

Spec → plan de implementare (writing-plans). Primul nucleu de construit (dovedit viabil):
scraper-ul de căutare pe portal + parserul întărit; apoi stratul de extracție LLM + scoring;
apoi UI-ul de descoperire (listă candidați cu bife și match breakdown).
