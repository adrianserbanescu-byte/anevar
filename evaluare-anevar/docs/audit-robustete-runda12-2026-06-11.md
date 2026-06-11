# Audit robustețe — RUNDA 12 (2026-06-11)

Agent READ-ONLY. Continuare a hardening-ului ultracode pe app-ul FastAPI ANEVAR.
Scop: input netrusted → excepție neprinsă → HTTP 500, pe vectori NOI; concurență; DoS;
numeric extrem-dar-valid; path-safety. Probe verificate determinist cu `TestClient`
(`raise_server_exceptions=False`) pe Python 3.13 (`.venv`).

Runde anterioare ÎNCHISE (neredundate): RUNDA 9 (data ISO an-range, split data-URL,
Infinity Decimal), RUNDA 11 (nume_fisier OSError, body 50MB, DCF O(n²)), eid-overflow,
valoare-negativă→raport, concurență F-2/F-4.

## Rezumat findings

| # | Severitate | Titlu | Locație |
|---|-----------|-------|---------|
| F-12-1 | **HIGH** | `curs_valutar` extrem (dar finit/valid) → 500 pe pagina de rezultat `/evaluare/{eid}` | `web/routers/evaluare.py:206-209` + `web/format.py:9` |
| F-12-2 | **MEDIUM** | DoS O(n·m) pe screening AML: câmpuri nume nemărginite → `SequenceMatcher` blochează workerul | `aml/liste.py:48-49` via `/api/aml/evalueaza` |
| F-12-3 | **LOW** | `beneficiari_reali` listă nemărginită amplifică costul screening + construcția modelelor | `aml/models.py:97` via `/api/aml/evalueaza` |

Restul suprafeței auditate a rezultat CURAT (vezi „Vectori verificați negativ").

---

## F-12-1 — HIGH — `curs_valutar` extrem → HTTP 500 pe `/evaluare/{eid}`

### Descriere
`EvaluationMeta.curs_valutar: Decimal | None` (`models/meta.py:39`) e validat de Pydantic
DOAR ca număr **finit** (respinge NaN/Inf), dar **fără limită de magnitudine**. Valoarea se
persistă în SQLite la `POST /api/evaluare`. La randarea paginii de rezultat,
`pagina_rezultat` calculează echivalentul valutar **fără try/except**:

```python
# web/routers/evaluare.py:205-209
if curs:
    if moneda == "LEI":
        echiv = fmt_numar(val / curs) + " EUR"      # val / curs ENORM
    elif moneda == "EUR":
        echiv = fmt_numar(val * curs) + " LEI"       # val * curs ENORM
```

`fmt_numar` rulează `v.quantize(Decimal("0.01"))` (`web/format.py:9`). Când raportul
`val/curs` (sau produsul `val*curs`) depășește ~10²⁶, rezultatul cere mai multe cifre
semnificative decât precizia contextului Decimal (28) → **`decimal.InvalidOperation`**.
Excepția NU e prinsă (handler-ul global tratează doar `RequestValidationError`/422) →
**HTTP 500**.

Notă: garda `if curs:` exclude doar `0`/`None`; un `curs` minuscul (`1E-30`) e „truthy".
Garda de `valoare_imposibila` și `construieste_context` NU acoperă acest caz — `curs_valutar`
nu intră în calculul motorului, doar în randarea paginii.

### Linia-sursă unde crapă
`web/format.py:9` → `q = v.quantize(Decimal("0.01"))` → `decimal.InvalidOperation`,
declanșat din `web/routers/evaluare.py:207` (LEI) sau `:209` (EUR).

### Probă (verificată — 500 confirmat)
```
POST /api/evaluare
{
  "meta": {"client_nume":"X","adresa":"a","numar_cadastral":"1","carte_funciara":"1",
           "data_evaluarii":"2026-01-01","data_raportului":"2026-01-01",
           "evaluator_nume":"E","evaluator_legitimatie":"L",
           "moneda":"LEI","curs_valutar":"1E-30"},
  "land": {"suprafata":"500"},
  "building": {"au":"100","acd":"120","an_referinta":2026,
    "elements":[{"element":"S","cod":"C","um":"mp","cantitate":"100","cost_unitar":"1000","an_pif":2010}],
    "depreciation_points":[{"varsta":0,"depreciere":"0"},{"varsta":50,"depreciere":"0.5"}]},
  "metoda":"cost","valoare_teren":"50000"
}
# -> 200 {"id": N, ...}

GET /evaluare/{N}
# -> 500 Internal Server Error   (decimal.InvalidOperation in fmt_numar)
```
Variantă EUR: aceeași structură cu `"moneda":"EUR","curs_valutar":"1E+9000"` → tot 500.
Cross-check: `GET /api/evaluare/{N}` (JSON, NU cheamă `fmt_numar`) rămâne **200** — confirmă
că exact conversia de afișare e vinovată.

### Fix recomandat
Două straturi (oricare oprește 500-ul; ideal ambele):
1. **La marginea API** — mărginește magnitudinea cursului în `EvaluationMeta.curs_valutar`
   (ex. `Field(gt=0, le=Decimal("1e6"))` sau un validator care respinge cursuri implauzibile;
   un curs EUR/LEI real e ~5). Transformă inputul absurd în 422 grațios.
2. **La randare** — fă `fmt_numar` robust: prinde `decimal.InvalidOperation`/`Overflow` și
   întoarce un fallback (ex. `str(v)` sau „—"), SAU înconjoară blocul de conversie din
   `pagina_rezultat` cu `try/except (ArithmeticError)` și omite `echiv` la eșec (pagina nu
   trebuie să cadă pentru o simplă afișare auxiliară). `fmt_numar` e folosit și pe alte
   pagini → fix-ul în `fmt_numar` are cel mai mare blast-radius pozitiv.

---

## F-12-2 — MEDIUM — DoS O(n·m) pe screening AML (nume nemărginite)

### Descriere
`/api/aml/evalueaza` → `evalueaza_relatie` → `screening(nume, liste)`
(`aml/serviciu.py:48-49`). Pentru fiecare nume din client se rulează
`_similar(nume, intrare)` = `SequenceMatcher(None, _norm(a), _norm(b)).ratio()`
(`aml/liste.py:48-49`) pentru FIECARE intrare din listele de screening. `SequenceMatcher`
e **O(n·m)** în lungimea șirurilor.

Câmpurile de nume (`PersoanaFizica.nume`/`prenume`, `ClientPJ.denumire` — `aml/models.py`)
sunt `str` **fără cap de lungime**. Plafonul global de corp e 50MB (`web/app.py:86`), deci
un singur nume poate avea ~zeci de MB. Listele implicite conțin deja `pep_functii` (9 intrări),
deci `_similar` chiar rulează pe input default — nu necesită `liste.json` populat.

Aplicația rulează local, mono-instanță → un request care macină CPU minute întregi blochează
tot UI-ul evaluatorului (DoS de disponibilitate).

### Linia-sursă
`aml/liste.py:49` → `SequenceMatcher(None, _norm(a), _norm(b)).ratio()` cu `b` = nume
user-controlat nemărginit; apelat în buclă din `aml/liste.py:66-70` (`screening`).

### Probă (verificată — timp măsurat)
```
POST /api/aml/evalueaza
{"tip_entitate":"PFA","azi":"2026-01-01",
 "client_pf":{"persoana":{"nume":"AAAA…(500.000 caractere)…A"}}}
# -> 200, dar ELAPSED ~10.7s  (doar 500k chars × 9 intrări PEP)
```
La ~50MB (limita de corp), timpul crește pătratic → ordin de minute, workerul e blocat.

### Fix recomandat
1. Cap de lungime pe câmpurile de nume KYC (ex. `nume`/`prenume` `Field(max_length=200)`,
   `denumire` `max_length=300`) în `aml/models.py` — un nume legal nu depășește câteva zeci
   de caractere. (Aliniat cu existentul `SemnaleIndicatori` care e deja strict.)
2. Defensiv în `screening`/`_similar`: trunchiază/skip pe șiruri peste un prag (ex. >256 char)
   înainte de `SequenceMatcher` (potrivirea unui nume real nu are nevoie de mai mult).

---

## F-12-3 — LOW — `beneficiari_reali` listă nemărginită

### Descriere
`ClientPJ.beneficiari_reali: list[BeneficiarReal]` (`aml/models.py:97`) nu are `max_length`.
La `/api/aml/evalueaza`, fiecare beneficiar generează un nume de screening
(`aml/serviciu.py:25-26`) + un model Pydantic complet (cu `StatutPEP` imbricat). Combinat cu
F-12-2, amplifică costul. Sub plafonul de 50MB încap mii de beneficiari.

### Probă (verificată)
```
POST /api/aml/evalueaza
{"tip_entitate":"PFA","azi":"2026-01-01",
 "client_pj":{"denumire":"Co","beneficiari_reali":[{"nume":"N…","prenume":"P"}, … ×5000]}}
# -> 200 în ~1.4s (construcție + screening pe 5000 BR)
```

### Fix recomandat
`Field(max_length=...)` rezonabil pe `beneficiari_reali` (ex. 1000) — un BR real are puține
persoane; protejează contra listelor abuzive fără a afecta cazurile legitime.

---

## Vectori verificați NEGATIV (curați — fără 500 pe input nou)

- **`/api/aml/decizie.docx`** cu kwargs extra (`persoana_desemnata` cu câmp necunoscut) →
  Pydantic ignoră extra (default), enum invalid → `ValidationError` (ValueError) → 400 prins.
  NU 500. (Spre deosebire de obs. vechi — `_construieste` prinde și `TypeError`.)
- **`/api/aml/evalueaza`** cu `client_pf.persoana` conținând câmp necunoscut → ignorat → 200.
- **`curs_valutar = "NaN"`** → respins de validatorul `finite_number` → 422 grațios.
- **Valoare finală enormă** (cost_unitar `1E+200`/`1E+9000`) → `construieste_context` prinde
  `decimal.InvalidOperation` (subclasă `ArithmeticError`) → 422 (`evaluare.py:51-52`). Calea
  de calcul e protejată; doar afișarea cursului (F-12-1) scapă, pentru că `curs_valutar` NU
  intră în motor.
- **`/api/indice-anevar?ultimele=-5` / `=0`** → `dd["perioade"][-max(1, ultimele):]`
  (`piata.py:104`); `max(1, ...)` neutralizează negativul/zero → 200.
- **Grile** (`/api/grila-casa|teren|chirii`) cu `suprafata_subiect` ≤ 0 / Decimal degenerat →
  toate trei sunt înfășurate în `try/except (ValueError, ArithmeticError)` → 422
  (`grile.py:47-48,63-64,84-85`). `chirie` are și gardă explicită `<=0`. `Comparable.suprafata`
  și `pret` au deja `Field(gt=0)`.
- **`/api/metodologie-config`** (body dict brut) → `din_override` clampează la `_LIMITE`
  (inclusiv `rotunjire_valoare ∈ [0.0001, 1e6]`, `min_comparabile ≥ 1`), respinge non-finit;
  `salveaza_override` normalizează înainte de persistare → fără quantize-InvalidOperation, fără
  `median([])`. Vector ÎNCHIS la sursă.
- **`/api/descopera/config-ponderi`** → validează categorie/atribut cunoscute, finit, întreg,
  ≥0, sumă efectivă >0 → 422 pe orice abatere.
- **Path-safety** `uid` (`/api/dosar/{uid}/...`) → `dosare_fs._cale` validează `uuid.UUID`,
  non-UUID → `KeyError` → 404 (anti path-traversal). `nume_fisier` import .docx → sanitizat
  (`_nume_fisier_sigur`, RUNDA 11). `eid` → `Annotated[int, ge=1, le=2**63-1]`.
- **Concurență storage pe foldere** → `_scrie` prinde `FileNotFoundError`→`KeyError` (F-2);
  lock-uri cu `contextlib.suppress(OSError)`; scriere atomică `os.replace`. Cache/index
  degradează grațios la fișier corupt. Nu am găsit race nou neacoperit.
- **SSRF** (`import_from_url`) → `_url_public_sigur` re-validat per-redirect, cap redirecturi.
- **Date AML** → `verifica_an_plauzibil` [1900, 2200] închide overflow-ul aritmetic de date
  (`_adauga_luni`, `suspendare_pana_la`, `termen_rtn`); `data_incetare_functie` în viitor →
  `_luni_intre` întoarce negativ, `< 12` adevărat, fără crash.

## Metodologie
Probe rulate cu `TestClient(app, raise_server_exceptions=False)` pe `.venv` (Python 3.13,
fastapi 0.136.3), `OUTPUT_DIR` temporar izolat, `client=None`, `fetcher` stub. Status 500
citit direct din răspuns; traceback-ul F-12-1 confirmat prin reproducerea
`fmt_numar(val/curs)` în afara rutei.
