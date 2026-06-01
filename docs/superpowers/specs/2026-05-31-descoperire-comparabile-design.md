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

1. **An construcție**
2. **Stare construcție** (separată de an: o casă veche renovată ≠ una nouă neîntreținută)
3. **Nivel finisaj**
4. **Tip încălzire**
5. **Suprafață teren**

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

**Pas 1 — dissimilaritate per atribut** `d ∈ [0,1]` (0 = identic, 1 = complet diferit):

| Atribut | Tip | Formula | Exemplu |
|---|---|---|---|
| An construcție | numeric | `d = min(\|Δani\| / 25, 1)` | Δ=5 ani → 0.20 |
| Stare | ordinal, 5 trepte (1=degradată … 5=nouă) | `d = \|Δtrepte\| / 4` | „bună"(3) vs „renovat"(4) → 0.25 |
| Nivel finisaj | ordinal, 4 trepte (1=modest … 4=lux) | `d = \|Δtrepte\| / 3` | standard vs lux → 0.67 |
| Tip încălzire | categorial | `0` aceeași / `0.5` înrudită / `1` fundamental diferită | centrală gaz vs pompă → 0.5 |
| Suprafață teren | numeric | `d = min(\|Δmp\| / teren_subiect, 1)` | 500 vs 450 → 0.10 |

**Pas 2 — combinare ponderată** (ponderi implicite după prioritate: an=5, stare=4, finisaj=3,
încălzire=2, teren=1), **doar peste atributele CUNOSCUTE**:
```
dissimilaritate = Σ(pondere_i × d_i) / Σ(pondere_i)     // i parcurge doar atributele cunoscute
scor_afișat      = round(100 × (1 − dissimilaritate))    // ex. „similaritate 84%"
```
Ranking: descrescător după scor (cel mai mare scor = cel mai similar = sus).

**Pas 3 — tratarea atributelor primare „nementionat":**
- Un atribut primar necunoscut **NU se penalizează** (necunoscut ≠ nepotrivire). Se **exclude** din
  sumă, iar ponderile se renormalizează peste atributele cunoscute.
- Candidatul afișează explicit **„scor bazat pe X/5 atribute"**, ca evaluatorul să știe pe ce date stă scorul.
- **Prag de încredere:** dacă **≥3 din 5 primare sunt „nementionat"**, candidatul e marcat
  **„date insuficiente — verifică manual"** și nu concurează la vârf pe baza unui scor slab fundamentat.

**Exemplu de afișare (un candidat):**
```
Similaritate 84% (bazat pe 4/5 atribute)
  An:        2008          → d 0.20  (subiect 2013)
  Stare:     "renovat 2021"→ d 0.25
  Finisaj:   "lux"         → d 0.00
  Încălzire: "centrală gaz"→ d 0.00
  Teren:     ➖ nementionat (exclus din scor)
```

**Calibrare:** toate pragurile și ponderile (cei 25 de ani la „an", treptele de stare/finisaj,
ponderile, pragul de 3/5) sunt **valori implicite, de calibrat de evaluator — de revizuit ulterior**.
Mapările ordinale (text liber „stare"/„finisaj" → treaptă) se fac tot prin LLM, pe baza descrierii.

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
