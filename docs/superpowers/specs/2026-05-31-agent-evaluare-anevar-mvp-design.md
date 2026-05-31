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
| Tip proprietate | **Casă individuală + teren** |
| Scop raport | Garantare credit ipotecar (bancar) — valoare de piață |
| Metode de calcul | **Două abordări:** (1) comparație directă (SEV 105) pentru proprietatea întreagă și pentru teren; (2) cost — teren prin comparație + construcție prin **cost de înlocuire net (CIN), metoda costurilor segregate** |
| Sursă comparabile | Introducere manuală + paste URL (imobiliare.ro / storia.ro) |
| Sursă costuri construcție | Cataloage IROVAL / MATRIX — costuri unitare introduse manual per element (catalog deținut de evaluator) |
| Rol AI | Generarea narativului raportului (text profesional) |
| Strategie AI | API cloud cu anonimizare înainte de trimitere |
| Format output | Word (.docx) editabil |
| Template | General SEV 103 (variante de bancă — ulterior) |
| Form factor | Aplicație web locală (browser, rulează local) |
| Livrare | Împachetat cu PyInstaller într-un singur `.exe` |
| GDPR | Toate datele rămân local; date personale anonimizate înainte de orice apel AI |
| Model de referință | `model_impozitare_Enachescu Cristian Nicolae 2026.pdf` (GBF Valuation) — folosit ca referință de structură/stil și ca sursă a formulelor de cost segregat și depreciere fizică |

### Non-goals (explicit excluse din MVP)

- Ingestie/OCR documente cadastrale (extras CF, releveu, CPE)
- Integrare oficială ANCPI / e-Terra API
- Colector automat de date de piață (scraping zilnic, indici BNR live)
- Digitizarea completă a catalogului IROVAL (costurile unitare se introduc manual din catalog)
- Alte tipuri de proprietate (apartament, teren simplu, comercial) — apartamentul devine modul ulterior
- Alte scopuri (impozitare/fiscal GEV 500, tranzacție) — deși arhitectura nu le exclude ulterior
- Abordarea prin venit (capitalizare chirie)
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
| Market Engine | Grila de comparație directă (proprietate întreagă + teren), ajustări ierarhice, indicatori de calitate | Comparable, SubjectProperty |
| Cost Engine | Cost de înlocuire net (CIN) prin metoda costurilor segregate + depreciere; valoare teren + construcție | SubjectProperty, costuri unitare, comparabile teren |
| Reconciliation | Reconciliază rezultatul abordării prin piață cu cel prin cost → valoare finală | Market Engine, Cost Engine |
| Validation | Loops de validare încrucișată (suprafețe, outliers, limite ajustare, depreciere) | Engine outputs |
| Anonymizer | Mascare date personale înainte de orice apel AI | — |
| Narrative AI | Generează textul capitolelor din datele calculate | Engine outputs, Anonymizer |
| Report Generator | Umple template SEV 103 cu numere + narativ → .docx | toate de mai sus |
| Storage (SQLite) | Persistă dosarele de evaluare pentru istoric și audit | — |

---

## 3. Modelul de date

```
Dosar evaluare (Evaluation)
├── Metadata lucrare      → client, scop (garantare credit), data evaluării,
│   (EvaluationMeta)         data raportului, evaluator, declarație independență
├── Proprietate subiect   → adresă, nr cadastral, CF, sarcini active
│   (SubjectProperty)
│   ├── Teren             → suprafață teren (mp), categorie (intravilan/extravilan),
│   │   (LandData)           deschidere, formă, utilități, restricții urbanism (PUG/RLU)
│   └── Construcție       → Ac (arie construită), Au (arie utilă),
│       (BuildingData)       Acd (arie construită desfășurată), an PIF/construcție,
│                            an modernizare, regim înălțime, structură, finisaje,
│                            clasă energetică, stare
├── Comparabile piață[]   → sursă (URL/manual), preț, suprafață, tip proprietate,
│   (Comparable)            finisaje, dată ofertă, tip (ofertă/tranzacție)
├── Comparabile teren[]   → preț/mp, suprafață, localizare, dată (pentru valoarea terenului)
│   (LandComparable)
├── Elemente cost[]       → element (infrastructură/structură/finisaje/instalații/
│   (CostElement)           învelitoare), cod IROVAL, u.m., cantitate, cost unitar
│                            (lei/u.m. din catalog), an PIF, durată viață
├── Grilă ajustări        → per comparabil × element de comparație:
│   (AdjustmentGrid)        valoarea ajustării (% sau valorică) + justificare
├── Rezultate             → valoare piață, valoare teren, CIB, depreciere, CIN,
│   (ValuationResults)      valoare prin cost, valoare finală reconciliată, TVA
└── Narativ[]             → text generat AI per capitol
    (NarrativeSection)
```

Schemele se implementează cu Pydantic. Persistate ca rânduri în SQLite (un dosar = o evaluare).

---

## 4. Motorul de calcul (casă + teren, garantare credit)

Pentru casă individuală + teren se aplică **două abordări**, apoi se reconciliază. Toate
calculele sunt deterministe (Python pur, precizie `Decimal`).

### 4.A Abordarea prin piață — grila de comparație directă (SEV 105)

Se aplică pe proprietatea întreagă (casă+teren) când există comparabile vândute/oferite de
proprietăți similare.

**4.A.1 Preț unitar brut** — pentru fiecare comparabil: `preț / suprafață` (€/mp sau lei/mp,
unitate configurabilă; pentru case raportat de regulă la Acd sau Au).

**4.A.2 Ajustări ierarhice** — aplicate secvențial pe prețul curent, în ordinea din specificație:

| Ordine | Element de comparație | Tip ajustare | Logică |
|---|---|---|---|
| 1 | Drepturi de proprietate transmise | Procentuală | Diferențe proprietate deplină vs dezmembrăminte |
| 2 | Condiții de finanțare | Valorică | Elimină impactul creditelor subvenționate |
| 3 | Condiții de vânzare (ofertă→tranzacție) | Procentuală | Corecție negativă pentru oferte active |
| 4 | Evoluția pieței (timp) | Procentuală | Ajustare la condiții curente (indice/dată) |
| 5 | Localizare | Procentuală | Poziționare spațială |
| 6 | Caracteristici fizice | Procentuală | Suprafață teren, suprafață construită, finisaje, stare, regim înălțime |
| 7 | Utilități / economice | Valorică / Procentuală | Aducere la paritate pe bază de costuri |

**4.A.3 Indicatori de calitate** (automat):
- **Ajustare brută** = Σ |corecții| per comparabil
- **Ajustare netă** = Σ algebrică a corecțiilor

**4.A.4 Selecția** — se preferă comparabilul cu ajustare brută minimă; valoarea = preț unitar
corectat × suprafața subiectului.

### 4.B Abordarea prin cost (teren prin comparație + construcție prin CIN)

Reproduce metoda din modelul de referință (GBF / IROVAL).

**4.B.1 Valoarea terenului** — prin comparația comparabilelor de teren (€/mp ajustat × suprafață
teren). Dacă nu există comparabile de teren în zonă, se semnalează și se documentează (ca în model).

**4.B.2 Costul de înlocuire brut (CIB) — metoda costurilor segregate:**

```
CIB = Σ (cantitate_element × cost_unitar_element)      [pe elemente: infrastructură,
                                                          structură, finisaje, instalații
                                                          electrice/sanitare/încălzire, învelitoare]
```
Costurile unitare provin din cataloagele IROVAL/MATRIX (introduse manual de evaluator).

**4.B.3 Vârsta cronologică ponderată (Vcp)** — media ponderată a vârstelor elementelor,
ponderată cu costul fiecărui element (elementele cu an PIF/modernizare diferit au vârste diferite).

**4.B.4 Deprecierea fizică (Dfn)** — prin interpolare conform GEV 500 / model de referință:

```
Dfn = D1 + (D2 − D1) / (V2 − V1) × (Vcp − V1)
```
unde `(V1, D1)` și `(V2, D2)` sunt punctele din tabelul de depreciere care încadrează Vcp.

**4.B.5 Depreciere funcțională (C_nf) și externă (C_ex)** — la **garantare credit** pot fi
nenule (spre deosebire de scopul fiscal, unde sunt 0). Configurabile per dosar, cu valori
implicite 0 și justificare obligatorie când sunt nenule.

**4.B.6 Costul de înlocuire net (CIN):**

```
CIN = CIB × (1 − Dfn) × (1 − C_nf) × (1 − C_ex)
```

**4.B.7 Valoarea prin cost** = Valoare teren + CIN. Tratament TVA documentat separat.

### 4.C Reconcilierea (SEV — concluzia valorii)

- Se compară valoarea din abordarea prin piață cu cea prin cost
- Evaluatorul selectează valoarea finală (cu ponderare/justificare), conform practicii profesionale
- Rotunjire; specificarea situației TVA (valoarea exprimată nu conține TVA)
- Dacă o abordare nu e aplicabilă (ex. lipsă comparabile teren), se documentează motivul și se
  folosește abordarea disponibilă (exact ca în modelul de referință)

Ambele motoare sunt 100% izolate și testabile cu valori cunoscute. Modelul de referință GBF
(CIN = 1.307.557,6 lei pentru Acd 351,46 mp) servește drept test de regresie pentru Cost Engine.

---

## 5. Validări (loops de control)

Rulate înainte de generarea raportului. Deterministe, separate de AI. Fiecare alertă apare
în UI cu mesaj clar și se loghează în audit trail.

| Verificare | Regulă | Acțiune |
|---|---|---|
| Date cadastrale/fizice | suprafață teren > 0; Au/Acd > 0; Au ≤ Acd; an PIF valid | **Blochează** dacă lipsesc câmpuri obligatorii |
| Număr minim comparabile | minimum 3 pentru abordarea aplicată (cerință SEV) | **Blochează** sub 3 dacă abordarea e folosită |
| Outliers | preț unitar brut deviază peste prag de la mediană | **Alertează** (marchează comparabilul) |
| Limită ajustare brută | ajustare brută per comparabil > 25% | **Alertează** (comparabil slab credibil) |
| Depreciere fizică | Dfn în interval plauzibil (0–100%); Vcp ≤ durata de viață | **Alertează** dacă Vcp > durata de viață sau Dfn în afara intervalului tabelului |
| Justificare depreciere C_nf/C_ex | dacă nenule, justificare text obligatorie | **Blochează** generarea fără justificare |
| Coerență valoare finală | valoarea reconciliată în intervalul celor două abordări | **Alertează** dacă în afara intervalului |
| Cel puțin o abordare | minim o abordare aplicabilă și documentată | **Blochează** dacă nicio abordare nu produce valoare |

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

1. **Sinteza evaluării și certificare** — identificare proprietate (teren + construcție), client,
   scop, tip valoare (Valoarea de Piață, SEV 104), date evaluare/raport/valabilitate, declarație independență
2. **Ipoteze generale și speciale** — limitative privind structura, solul; ipoteze speciale
3. **Prezentarea datelor de piață** — analiză macro + dinamică piață locală
4. **Descrierea juridică și fizică** — situație juridică (cadastral, CF, sarcini); descrierea
   terenului (suprafață, categorie, utilități) și a construcției (Ac/Au/Acd, structură, finisaje, stare)
5. **Analiza CMBU** — permisibilitate legală (PUG/RLU), posibilitate fizică, fezabilitate financiară
6. **Aplicarea metodelor de calcul** — (a) tabelul grilei de comparație + justificări;
   (b) tabelul costurilor segregate (CIB), calculul deprecierii și CIN; valoarea terenului
7. **Reconcilierea și concluzia valorii** — analiză critică a celor două abordări, selecția
   valorii finale, situație TVA

Tabelele (grila de comparație + tabelul costurilor segregate cu depreciere/CIN) se inserează cu
toate valorile și indicatorii. Anonimizare la cerere pentru versiunea de arhivă.

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
│   │   ├── market.py            # grila de comparație (determinist)
│   │   ├── adjustments.py       # ajustări ierarhice
│   │   ├── cost.py             # CIB segregat, depreciere, CIN, valoare teren
│   │   ├── reconciliation.py    # reconciliere piață vs cost
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
│   ├── test_market.py           # grilă de referință cu valori cunoscute
│   ├── test_adjustments.py
│   ├── test_cost.py            # CIN segregat vs model GBF (1.307.557,6 lei)
│   ├── test_reconciliation.py
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
| Cost Engine (CIN) | Reproduce modelul de referință GBF: CIB segregat, Vcp, Dfn, CIN = 1.307.557,6 lei | **Critică** |
| Market Engine | Grilă de comparație de referință → valoare reprodusă la leu | **Critică** |
| Ajustări | Fiecare tip de ajustare aplicat corect, în ordinea ierarhică | Înaltă |
| Reconciliere | Selecția corectă între cele două abordări; cazul „o abordare lipsă" | Înaltă |
| Validări | Fiecare regulă (sub 3 comp → blocat, outlier → alertă, depreciere etc.) | Înaltă |
| Anonymizer | Niciun nume/CF/adresă nu scapă în textul trimis spre API | **Critică** (GDPR) |
| URL parser | Fixturi HTML salvate (nu live, teste stabile) | Medie |
| Generare raport | Smoke: dosar complet → .docx valid cu cele 7 capitole | Medie |

Cele mai importante suite sunt motoarele de calcul — valorile trebuie reproduse la leu pentru a fi
acceptabile în context bancar. Modelul de referință GBF (`model_impozitare...2026.pdf`) este testul
de regresie principal pentru Cost Engine.

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

1. Modul apartament rezidențial (grila de comparație, fără cost)
2. Scop fiscal / impozitare (GEV 500) — reutilizează Cost Engine cu C_nf = C_ex = 0
3. Digitizarea catalogului IROVAL (selecție coduri + costuri unitare automate)
4. Ingestie/OCR documente cadastrale (extras CF, releveu, CPE)
5. Integrare oficială ANCPI / e-Terra API
6. Colector automat de date de piață (indici BNR/ANCPI, scraping programat)
7. Variante de template pe bănci (BCR, BRD etc.)
8. Tipuri suplimentare (teren simplu, comercial) și abordarea prin venit
9. Opțiune LLM local (Ollama) pentru GDPR total offline
