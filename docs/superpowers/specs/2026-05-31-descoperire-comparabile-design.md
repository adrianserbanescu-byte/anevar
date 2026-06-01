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

### 5.1 Atribute primare (scorate, determină ranking-ul)

Ordinea de prioritate (cât mută prețul), **confirmată de evaluator — de revizuit ulterior dacă e cazul**:

1. **An construcție**
2. **Stare construcție** (separată de an: o casă veche renovată ≠ una nouă neîntreținută)
3. **Nivel finisaj**
4. **Tip încălzire**
5. **Suprafață teren**

Plus filtrul de bază (must-have, nu se scorează — definesc setul de candidați): localitate/zonă,
tip (casă+teren), suprafață construită aproximativă.

### 5.2 Atribute secundare (definite de user, informative)

Evaluatorul scrie într-un text box, **câte unul pe linie**, în format `atribut: valoare_dorită`
(ex. `tamplarie: termopan`, `garaj: da`, `panouri solare`). Valoarea dorită e opțională.

Pentru fiecare candidat, LLM-ul caută atributul în descrierea reală și raportează **trei stări**:

| Stare | Sens |
|---|---|
| ✅ Potrivit | atributul e menționat și valoarea corespunde celei dorite |
| ⚠️ Diferit | atributul e menționat, dar cu altă valoare |
| ➖ Nementionat | descrierea nu pomenește atributul |

**Decizie (fermă):** atributele secundare sunt **exclusiv FYI** — semnalizatoare afișate în „match
breakdown" pentru informarea evaluatorului. Ele **NU intră în scor și NU influențează ranking-ul**
sub nicio formă. Ranking-ul este determinat **doar de cele 5 atribute primare**. Motiv: secundarele
sunt variabile și des „nementionate"; scorarea lor ar reintroduce zgomot. (Ajustabil ulterior doar
dacă evaluatorul cere explicit influență pe ranking.)

---

## 6. Rolul LLM-ului

- **Doar extracție din text furnizat** (descrierea reală a anunțului descărcat). Niciodată căutare
  sau generare de date despre proprietăți.
- Prompt: „din acest text de anunț, extrage {atribute}; pentru ce nu apare, întoarce «nementionat»".
- Întoarce date structurate (JSON validat) cu atributele + starea fiecărui atribut secundar.
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
