# Agent AI de evaluare imobiliară ANEVAR — Design MVP

**Data:** 2026-05-31
**Status:** Draft pentru review
**Autor:** Adrian Șerbănescu (cu asistență Claude Code)

---

## 1. Context și scop

Specificația tehnică sursă descrie un agent AI complet pentru generarea rapoartelor
de evaluare imobiliară conform standardelor ANEVAR/SEV. Documentul sursă acoperă cinci
subsisteme independente (ingestie documente, conectivitate date externe, motor matematic,
generator raport, validare & conformitate), fiecare reprezentând un proiect de sine stătător.

Acest document definește **doar MVP-ul** — nucleul minim util care poate fi folosit imediat
într-o evaluare reală. Celelalte subsisteme (OCR cadastral, integrare oficială ANCPI/e-Terra,
colector automat de piață) vor fi proiecte ulterioare, fiecare cu propriul ciclu spec → plan →
implementare.

### Scope MVP (decizii confirmate)

| Dimensiune | Decizie |
|---|---|
| Subsistem | Motor matematic de evaluare + generator de raport |
| Tip proprietate | Apartament rezidențial |
| Scop raport | Garantare credit ipotecar (bancar) |
| Metodă de calcul | Grila de comparație directă (SEV 105) |
| Sursă comparabile | Introducere manuală + paste URL (imobiliare.ro / storia.ro) |
| Rol AI | Generarea narativului raportului (text profesional) |
| Strategie AI | API cloud cu anonimizare înainte de trimitere |
| Format output | Word (.docx) editabil |
| Template | General SEV 103 (variante de bancă — ulterior) |
| Form factor | Aplicație web locală (browser, rulează local) |
| Livrare | Împachetat cu PyInstaller într-un singur `.exe` |
| GDPR | Toate datele rămân local; date personale anonimizate înainte de orice apel AI |

### Non-goals (explicit excluse din MVP)

- Abordarea prin cost (CIN) — apartamentele se evaluează prin comparație; modul separat ulterior
- Ingestie/OCR documente cadastrale (extras CF, releveu, CPE)
- Integrare oficială ANCPI / e-Terra API
- Colector automat de date de piață (scraping zilnic, indici BNR live)
- Alte tipuri de proprietate (casă+teren, teren, comercial)
- Alte scopuri (tranzacție, fiscal) — deși arhitectura nu le exclude ulterior
- Variante de template specifice fiecărei bănci
- Cont online / SaaS / autentificare multi-utilizator

---

## 2. Arhitectura de ansamblu

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (localhost:<port>)                                  │
│  Formular evaluare · Grilă comparabile · Preview · Download  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP (local)
┌───────────────────────────▼─────────────────────────────────┐
│  Server FastAPI (Python) — totul rulează local               │
│                                                              │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Comparable │  │  Valuation   │  │  Report Generator  │    │
│  │  Importer  │→ │   Engine     │→ │  (python-docx)     │    │
│  │(URL+manual)│  │ (grila SEV)  │  │  template SEV 103  │    │
│  └────────────┘  └──────────────┘  └─────────┬──────────┘    │
│                          │                   │               │
│                  ┌───────▼────────┐  ┌───────▼──────────┐    │
│                  │  Validation    │  │  Narrative AI    │    │
│                  │  (loops SEV)   │  │  (LLM → text)    │    │
│                  └────────────────┘  └──────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLite local — istoric evaluări, dosare, audit       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
        Împachetat cu PyInstaller → evaluare-anevar.exe
        (dublu-click → pornește serverul → deschide browserul)
```

### Principiul central: separarea calcul / AI

- **Calculele sunt deterministe** — Python pur, fără AI, fără internet. Rezultate reproductibile
  și auditabile, exact ce cere garantarea bancară.
- **AI-ul atinge doar textul narativ**, niciodată numerele. Primește cifrele deja calculate
  ca date de intrare și produce text; nu inventează și nu modifică valori.

### Componente izolate (o singură responsabilitate fiecare)

| Componentă | Responsabilitate | Depinde de |
|---|---|---|
| Comparable Importer | Aduce comparabilele (manual + parsare URL), normalizează la schemă unică | — |
| Valuation Engine | Grila de comparație directă, ajustări ierarhice, indicatori de calitate | Comparable, SubjectProperty |
| Validation | Loops de validare încrucișată (suprafețe, outliers, limite ajustare) | Valuation output |
| Anonymizer | Mascare date personale înainte de orice apel AI | — |
| Narrative AI | Generează textul capitolelor din datele calculate | Valuation output, Anonymizer |
| Report Generator | Umple template SEV 103 cu numere + narativ → .docx | toate de mai sus |
| Storage (SQLite) | Persistă dosarele de evaluare pentru istoric și audit | — |

---

## 3. Modelul de date

```
Dosar evaluare (Evaluation)
├── Metadata lucrare      → client, scop (garantare credit), data evaluării,
│   (EvaluationMeta)         data raportului, evaluator, declarație independență
├── Proprietate subiect   → adresă, nr cadastral, CF, suprafață utilă,
│   (SubjectProperty)        nr camere, etaj/total etaje, an construcție,
│                            finisaje, clasă energetică, sarcini active
├── Comparabile[]         → sursă (URL/manual), preț, suprafață, etaj,
│   (Comparable)            finisaje, dată ofertă, tip (ofertă/tranzacție)
├── Grilă ajustări        → per comparabil × element de comparație:
│   (AdjustmentGrid)        valoarea ajustării (% sau valorică) + justificare
├── Rezultat              → preț unitar corectat/comp, valoare selectată,
│   (ValuationResult)       indicatori calitate, valoare finală rotunjită
└── Narativ[]             → text generat AI per capitol
    (NarrativeSection)
```

Schemele se implementează cu Pydantic. Persistate ca rânduri în SQLite (un dosar = o evaluare).

---

## 4. Motorul de calcul — grila de comparație directă (SEV 105)

Reproduce exact logica din specificația sursă. Pași deterministi:

### 4.1 Preț unitar brut

Pentru fiecare comparabil: `preț / suprafață utilă` (€/mp sau lei/mp, unitate configurabilă).

### 4.2 Ajustări ierarhice

Aplicate **secvențial** pe prețul curent, în ordinea din specificație:

| Ordine | Element de comparație | Tip ajustare | Logică |
|---|---|---|---|
| 1 | Drepturi de proprietate transmise | Procentuală | Diferențe proprietate deplină vs dezmembrăminte |
| 2 | Condiții de finanțare | Valorică | Elimină impactul creditelor subvenționate |
| 3 | Condiții de vânzare (ofertă→tranzacție) | Procentuală | Corecție negativă pentru oferte active |
| 4 | Evoluția pieței (timp) | Procentuală | Ajustare la condiții curente (indice/dată) |
| 5 | Localizare | Procentuală | Poziționare spațială |
| 6 | Caracteristici fizice | Procentuală | Etaj, finisaje, suprafață, stare construcție |
| 7 | Utilități / economice | Valorică / Procentuală | Aducere la paritate pe bază de costuri |

### 4.3 Indicatori de calitate (calculați automat)

- **Ajustare brută** = Σ |corecții| per comparabil (suma absolută)
- **Ajustare netă** = Σ algebrică a corecțiilor aplicate

### 4.4 Selecția valorii finale

- Se preferă comparabilul cu **ajustare brută minimă** (cel mai similar = cel mai credibil)
- Valoare finală = preț unitar corectat al acelui comparabil × suprafața subiectului
- Rotunjire conform practicii profesionale
- Specificare situație TVA (valoarea exprimată nu conține TVA)

Motorul este 100% izolat și testabil cu valori cunoscute dintr-un raport de referință.

---

## 5. Validări (loops de control)

Rulate înainte de generarea raportului. Deterministe, separate de AI. Fiecare alertă apare
în UI cu mesaj clar și se loghează în audit trail.

| Verificare | Regulă | Acțiune |
|---|---|---|
| Date cadastrale | suprafață utilă > 0; etaj ≤ total etaje; an construcție valid | **Blochează** dacă lipsesc câmpuri obligatorii |
| Număr minim comparabile | minimum 3 (cerință SEV) | **Blochează** sub 3 |
| Outliers | preț unitar brut deviază peste prag de la mediană | **Alertează** (marchează comparabilul) |
| Limită ajustare brută | ajustare brută per comparabil > 25% | **Alertează** (comparabil slab credibil) |
| Coerență valoare finală | €/mp final în intervalul comparabilelor | **Alertează** dacă în afara intervalului |

Pragurile (% outlier, % limită) sunt configurabile, cu valori implicite din practica ANEVAR.

---

## 6. AI narativ

### 6.1 Rol

LLM-ul primește **datele deja calculate** și produce textul profesional pentru capitolele analitice:

- Analiza pieței / dinamica pieței locale
- Descrierea proprietății (juridică + fizică)
- Analiza CMBU (cea mai bună utilizare)
- Justificarea/fundamentarea ajustărilor aplicate
- Reconcilierea rezultatelor și concluzia valorii

### 6.2 Garanții (trasabilitate deplină)

- AI primește numerele ca date de intrare; nu le inventează, nu le modifică
- Fiecare secțiune narativă citează datele sursă (ex. „ajustare −5% pentru etaj, comparabil 2")
- Promptul include reguli SEV relevante, pentru terminologie conformă
- Output editabil de utilizator în .docx înainte de livrare

### 6.3 Strategie: API cloud cu anonimizare

- Înainte ca orice text să plece spre API, stratul **Anonymizer** înlocuiește datele personale
  (nume client, adresă exactă, nr cadastral, CF) cu marcaje (`[CLIENT]`, `[ADRESA]`, `[CADASTRAL]`)
- AI-ul primește doar cifrele și caracteristicile tehnice
- După primirea textului, datele reale se reintroduc local în .docx
- Cheia API se citește dintr-un `.env` local lângă executabil (nu hardcodată)
- **Fallback fără AI:** dacă lipsește cheia, raportul se generează cu placeholdere de text
  (numerele rămân complete). Aplicația rămâne utilizabilă offline.

---

## 7. Generarea raportului (.docx)

`python-docx` umple un template SEV 103 cu cele 7 capitole obligatorii din specificație:

1. **Sinteza evaluării și certificare** — identificare proprietate, client, scop, tip valoare
   (Valoarea de Piață, SEV 104), date evaluare/raport/valabilitate, declarație independență
2. **Ipoteze generale și speciale** — limitative privind structura, solul; ipoteze speciale
3. **Prezentarea datelor de piață** — analiză macro + dinamică piață locală
4. **Descrierea juridică și fizică** — situație juridică (cadastral, CF, sarcini); caracteristici fizice
5. **Analiza CMBU** — permisibilitate legală, posibilitate fizică, fezabilitate financiară
6. **Aplicarea metodelor de calcul** — tabelul detaliat al grilei de comparație + justificări
7. **Reconcilierea și concluzia valorii** — analiză critică, selecția valorii, situație TVA

Tabelul grilei se inserează cu toate ajustările și indicatorii de calitate. Anonimizare la
cerere pentru versiunea de arhivă.

---

## 8. Structura proiectului

```
evaluare-anevar/
├── app/
│   ├── main.py                  # FastAPI — pornește serverul + deschide browserul
│   ├── models/                  # scheme Pydantic
│   │   ├── evaluation.py
│   │   ├── property.py
│   │   └── comparable.py
│   ├── engine/
│   │   ├── valuation.py         # grila de comparație (determinist)
│   │   ├── adjustments.py       # ajustări ierarhice
│   │   └── validation.py        # loops de validare
│   ├── importers/
│   │   ├── manual.py
│   │   └── url_parser.py        # imobiliare.ro / storia.ro
│   ├── ai/
│   │   ├── anonymizer.py        # mascare date personale
│   │   └── narrative.py         # apel API + prompturi SEV
│   ├── report/
│   │   ├── generator.py         # python-docx
│   │   └── templates/
│   │       └── sev103.docx      # template raport
│   ├── db/
│   │   └── storage.py           # SQLite local
│   └── web/                     # frontend (HTMX + formulare)
├── tests/
│   ├── test_valuation.py        # grilă de referință cu valori cunoscute
│   ├── test_adjustments.py
│   ├── test_validation.py
│   └── test_anonymizer.py
├── build/
│   ├── evaluare-anevar.spec     # config PyInstaller
│   └── start.bat                # fallback rulare din sursă
├── requirements.txt
└── README.md
```

---

## 9. Împachetare PyInstaller

- `pyinstaller evaluare-anevar.spec` → produce **`evaluare-anevar.exe`** (un singur fișier)
- La dublu-click: pornește serverul FastAPI pe un port liber, apoi deschide automat browserul
- Include: interpretorul Python, librăriile, template-ul .docx, frontend-ul
- **Playwright** (parsare URL) necesită atenție la împachetare. Dacă devine prea greu, fallback
  pe `requests + BeautifulSoup` pentru site-urile care permit; Playwright rămâne opțional
- Cheia API se citește dintr-un `.env` local lângă executabil
- SQLite + rapoartele generate se salvează într-un folder lângă executabil (`./date/`)

---

## 10. Strategia de testare

| Suită | Ce verifică | Prioritate |
|---|---|---|
| Motor de calcul | Grilă de referință dintr-un raport ANEVAR real → valoare reprodusă la leu | **Critică** |
| Ajustări | Fiecare tip de ajustare aplicat corect, în ordinea ierarhică | Înaltă |
| Validări | Fiecare regulă (sub 3 comp → blocat, outlier → alertă etc.) | Înaltă |
| Anonymizer | Niciun nume/CF/adresă nu scapă în textul trimis spre API | **Critică** (GDPR) |
| URL parser | Fixturi HTML salvate (nu live, teste stabile) | Medie |
| Generare raport | Smoke: dosar complet → .docx valid cu cele 7 capitole | Medie |

Cea mai importantă suită este motorul de calcul — calculele trebuie să fie corecte la leu pentru
a fi acceptabile în context bancar.

---

## 11. Stack tehnologic

- **Backend:** Python 3.11+, FastAPI, Pydantic
- **Frontend:** HTMX + HTML/CSS (formulare, grilă, preview); fără framework JS greu
- **Calcul:** Python pur (eventual `decimal` pentru precizie monetară)
- **Parsare URL:** requests + BeautifulSoup (+ Playwright opțional)
- **Raport:** python-docx
- **AI:** SDK Anthropic (Claude) sau OpenAI, prin API
- **Persistență:** SQLite (stdlib `sqlite3` sau SQLModel)
- **Împachetare:** PyInstaller
- **Testare:** pytest

---

## 12. Etape ulterioare (post-MVP, fiecare cu propriul spec)

1. Abordarea prin cost (CIN) — pentru case + teren
2. Ingestie/OCR documente cadastrale (extras CF, releveu, CPE)
3. Integrare oficială ANCPI / e-Terra API
4. Colector automat de date de piață (indici BNR/ANCPI, scraping programat)
5. Variante de template pe bănci (BCR, BRD etc.)
6. Tipuri suplimentare de proprietate și scopuri (fiscal, asigurare)
7. Opțiune LLM local (Ollama) pentru GDPR total offline
