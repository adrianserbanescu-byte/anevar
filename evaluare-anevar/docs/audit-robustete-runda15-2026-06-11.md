# Audit robustețe — RUNDA 15 (2026-06-11)

**Scop:** input netrusted → 500 / DoS pe codul AML și câmpurile noi adăugate recent:
`aml/risc.py` (factor scop, BR-lipsă), `aml/models.py` (EDD/RBR opționale), `aml/indicatori.py`
(15 indicatori noi), `aml/serviciu.py`, endpoint-urile `/api/aml/evalueaza` + `/api/aml/decizie.docx`;
plus câmpurile noi pe `meta` (`cod_postal`, `riscuri_fizice`, `certificat_energetic`) și wiring-ul
ESG în generator.

**Metodă:** citire cod + execuție de probe (pydantic direct + `TestClient` pe `create_app`). READ-ONLY
— niciun fișier de cod modificat.

**Concluzie de ansamblu:** suprafața AML este **bine întărită** după rundele 9–14. Toate payload-urile
ostile pe `/api/aml/evalueaza` și `/api/aml/decizie.docx` întorc **422/400, nu 500** (verificat
end-to-end). Singurele findings noi sunt **două vectori de DoS prin liste nemărginite** pe câmpurile
adăugate recent (unul nou pe `meta.riscuri_fizice`, unul rezidual pe `beneficiari_reali` cu plafon încă prea
mare) și două câmpuri-string nemărginite. NU repet findings-urile rezolvate F-12-2/F-12-3 (truncare 256 +
`max_length=1000` aplicate) și nici cele din R9–R11/R13/R14.

| ID | Severitate | Rezumat | Locație |
|----|-----------|---------|---------|
| F-15-1 | **MEDIUM** | `meta.riscuri_fizice` listă nemărginită → N paragrafe docx (memorie/CPU) la generarea raportului | `models/meta.py:62` via `POST /api/dosar/{uid}/genereaza` |
| F-15-2 | **MEDIUM** | Plafon `beneficiari_reali=1000` încă prea mare: 1000 BR × listă oficială mare = minute de CPU pe un singur request (DoS rezidual) | `aml/models.py:109` via `/api/aml/evalueaza` |
| F-15-3 | **LOW** | `cod_postal` / `certificat_energetic` string-uri nemărginite → balonare payload + docx | `models/meta.py:57,65` via raport |
| F-15-4 | **LOW** | `SemnaleIndicatori.observatii` + `RiscIdentificat.observatie` string-uri nemărginite (intră în docx ca atare) | `aml/indicatori.py:165`, `esg.py:132` |

---

## F-15-1 (MEDIUM) — `meta.riscuri_fizice` listă nemărginită → DoS la generarea raportului

**Locație:** `src/evaluare/models/meta.py:62`
```python
riscuri_fizice: list[str] = Field(default_factory=list)   # FĂRĂ max_length
```
Câmpul nou (ESG / GEV 520 §86–88) nu are plafon de lungime. Fluxul:
`POST /api/dosar/{uid}/genereaza` (body `EvaluationInput`, attacker-controlled) →
`genereaza_raport(ctx, …)` → `report/generator.py:705 _adauga_esg` →
`identificate = [esg.RiscIdentificat(cheie=r.strip()) for r in riscuri]` →
`esg.genereaza_sectiune_esg(identificate)` → `for paragraf in …split("\n\n"): doc.add_paragraph(paragraf)`.

Fiecare etichetă devine un paragraf separat în docx. `python-docx` serializează fiecare paragraf în XML
(alocare DOM + escapare), mult mai scump decât string-join.

**Probă (unitar, confirmată):**
```python
from evaluare import esg
identificate = [esg.RiscIdentificat(cheie="risc"+str(i)) for i in range(200_000)]
out = esg.genereaza_sectiune_esg(identificate)   # 0.16s, 24 MB string
out.count("\n\n")+1   # 200002 paragrafe trimise în docx
```
**Probă (HTTP, schiță):**
```
POST /api/dosar/{uid}/genereaza
{"meta": {..., "riscuri_fizice": ["x","x", … ×200000]}, ...}
```
200k × `add_paragraph` în python-docx = sute de MB RAM + secunde–minute CPU per request, cu fișier `.docx`
balonat scris pe disc (`fs.adauga_versiune_docx`). Câteva request-uri concurente epuizează workerul.

**Notă de delimitare:** R14 a marcat acest wiring „Robust", dar a verificat doar **sanitizarea per-etichetă**
(`if r and r.strip()`, fallback pe cheie necunoscută). Nu a acoperit **lungimea listei**. Acesta este unghiul nou.

**Fix:** `Field(default_factory=list, max_length=64)` pe `riscuri_fizice` (8 riscuri în catalog + etichete
libere; 64 e generos). Opțional, cap și pe lungimea fiecărei etichete (`max_length` pe element nu e direct în
pydantic pentru `list[str]` — folosește un `field_validator` care taie la ~200 caractere / element, paritate cu
`_MAX_NUME` din AML).

---

## F-15-2 (MEDIUM) — Plafon `beneficiari_reali=1000` rezidual prea mare → DoS screening

**Locație:** `src/evaluare/aml/models.py:109`
```python
beneficiari_reali: list[BeneficiarReal] = Field(default_factory=list, max_length=1000)
```
F-12-3 (R12) a fost remediat parțial: există acum `max_length=1000` (înainte era nemărginit) și `_similar`
truncă la 256 caractere (`aml/liste.py:26,57`). DAR plafonul **1000** rămâne prea mare. `serviciu._nume_screening`
emite ~1 nume per BR (+ reprezentant + denumire), iar `screening` rulează `SequenceMatcher` (O(n·m)) pe FIECARE
nume × FIECARE intrare din listele oficiale. Listele oficiale reale (ex. lista consolidată UE de sancțiuni) au
**mii** de intrări → produsul `1000 BR × mii intrări × ~250 µs/comparație` = minute de CPU blocant per request.

Listele nu sunt attacker-controlled (se încarcă din `data/liste.json`), dar **numărul de BR este** — și el
multiplică direct costul. Plafonul de nume (256) limitează costul *per comparație*, nu **produsul**.

**Probă (confirmată):**
```python
# 1000 BR × 1000 intrări listă, nume de 200 caractere:
evalueaza_relatie('PFA', ClientPJ(beneficiari_reali=[BeneficiarReal(nume='A'*200,prenume='B'*200)]*... ), …)
# → 285.13 s CPU pe un singur apel (1M comparații SequenceMatcher)
# calibrare: ~250 µs / comparație pe stringuri de 200 char
```
```
POST /api/aml/evalueaza
{"azi":"2026-06-11","client_pj":{"beneficiari_reali":[{"nume":"A…","prenume":"B…"}, … ×1000]}}
```

**Fix:** coboară plafonul la o valoare realistă (ex. `max_length=50` — un BR real al unei PJ are puține persoane;
chiar și structuri complexe rar depășesc câteva zeci). Alternativ/suplimentar: deduplică numele înainte de
screening și/sau limitează numărul total de comparații (cap pe `len(nume) × len(intrari)`), returnând un
avertisment „screening trunchiat" peste prag (om-în-buclă, fără 500).

---

## F-15-3 (LOW) — `cod_postal` / `certificat_energetic` string-uri nemărginite

**Locație:** `src/evaluare/models/meta.py:57,65`
```python
cod_postal: str | None = None              # fără max_length
certificat_energetic: str | None = None    # fără max_length
```
Câmpuri noi (gap S-4 BIG / G7 CPE). R14 a verificat doar că sunt **interpolate ca text** (fără conversie
numerică) → corect, nu produc 500. Dar nu au plafon de lungime: un `cod_postal` de câțiva MB intră în payload-ul
BIG / pe copertă și în docx, balonând documentul oficial și răspunsul. Severitate mică (nu e 500, nu e
amplificare O(n·m)), dar inconsistent cu restul câmpurilor KYC care au `_MAX_NUME=200`.

**Probă:** `EvaluationMeta(..., cod_postal="9"*10_000_000)` acceptat fără eroare; ajunge în recipisa BIG și docx.

**Fix:** `cod_postal: str | None = Field(default=None, max_length=12)` (cod poștal RO = 6 cifre);
`certificat_energetic: str | None = Field(default=None, max_length=120)` (clasă energetică / referință scurtă).

---

## F-15-4 (LOW) — Câmpuri `observatii` / `observatie` nemărginite

**Locație:** `src/evaluare/aml/indicatori.py:165` (`SemnaleIndicatori.observatii: str = ""`),
`src/evaluare/esg.py:132` (`RiscIdentificat.observatie: str = ""`).
Ambele sunt text liber fără `max_length`. `observatii` ajunge în răspunsul `/api/aml/evalueaza`
(nu e încă redat în docx, dar e reflectat înapoi); `observatie` intră în `genereaza_sectiune_esg` și de acolo în
docx ca atare. Nu produc 500 (sunt doar concatenate), dar permit balonarea răspunsului/documentului. Inconsistent
cu `_MAX_NUME` aplicat pe restul câmpurilor text AML.

**Fix:** `Field(default="", max_length=2000)` pe ambele (o observație legitimă de evaluator e scurtă).

---

## Suprafețe verificate FĂRĂ finding (rezultate negative, pentru trasabilitate)

- **`/api/aml/evalueaza` — toate payload-urile ostile → 422, nu 500** (verificat end-to-end cu `TestClient`):
  `procent` text/`NaN` → 422 (pydantic `finite_number`); `scop` invalid (Literal) → 422; cheie de indicator
  necunoscută → 422 (`model_config extra="forbid"`); `beneficiari_reali` > 1000 → 422 (`max_length`);
  `data_incetare_functie="9999-01-01"` → 422 (`verifica_an_plauzibil`, AN_MAX=2200); `azi` ne-ISO → 422.
- **`risc.py` — factor scop:** `_SCOP_FACTOR.get(semnale.scop)` folosește `.get()` + `scop` e `Literal` validat →
  niciun `KeyError` pe scop necunoscut. `_factor_produs(scop=None)` → 2 (neutru). Robust.
- **`risc.py` — `nivel_masuri` / `_LUNI_REEVALUARE[categorie]`:** indexare cu `CategorieRisc` (Literal calculat
  intern, mereu ∈ {redus,standard,sporit}) → fără `KeyError`. Robust.
- **`risc.py` — BR-lipsă (`_beneficiar_real_lipsa`):** doar `any(... for br in client.beneficiari_reali)` pe listă
  mărginită (1000); aditiv, nu forțează categoria. Fără conversii negardate. Robust.
- **`pep_efectiv` / `_luni_intre` / `_adauga_luni`:** `data_incetare_functie` validată ISO + an plauzibil în
  `StatutPEP._valideaza_data_incetare`; `azi` validat la schema. Aritmetica de date nu mai poate da
  `OverflowError` (AN_MAX=2200 + 5 ani « 9999). Robust.
- **`models.py` — `procent: Decimal`:** pydantic respinge `NaN`/`Inf` (`finite_number`); valori extreme
  (`1E+999`) acceptate dar NU folosite în aritmetică nicăieri (doar stocate/serializate). Fără 500. Robust.
- **`models.py` — `data_extras_rbr` / `nr_extras_rbr` / `consultat_rbr`:** câmpuri RBR noi; `data_extras_rbr`
  acceptă string ne-ISO, dar NU e folosit în aritmetică de date și NU e încă redat în `documente.py`
  (grep gol) → fără 500. *Recomandare preventivă:* dacă va fi cândva folosit în calcul de termen, adaugă
  același validator ISO ca pe `data_incetare_functie`.
- **`models.py` — EDD (`sursa_fonduri`, `sursa_avere`, `aprobare_…`, `monitorizare_sporita`):** câmpuri opționale
  pe `DosarAML`, neexpuse direct pe `/api/aml/evalueaza` (care construiește `ClientPF/PJ`, nu `DosarAML`); fără
  wiring docx pentru `sursa_*` (grep gol). Fără suprafață de 500.
- **`indicatori.py` — 15 indicatori noi:** `SemnaleIndicatori` cu `extra="forbid"`; `evalueaza_indicatori` /
  `propune_rts` iterează `_CHEI` (chei statice din catalog) cu `getattr` pe câmpuri bool declarate → fără
  `getattr` pe input arbitrar, fără `KeyError`. Robust.
- **`esg.genereaza_sectiune_esg` — chei/surse necunoscute:** `risc(cheie)` și `descriere_sursa(sursa)` folosesc
  `.get()` cu fallback pe cheia brută → cheie/sursă inexistentă redată ca atare, fără excepție (verificat cu
  `cheie='cheie_inexistenta_xyz'`, `sursa='SURSA_NECUNOSCUTA'`, `observatie` de 100k caractere). Robust pe
  conținut; vulnerabil doar pe **lungimea listei** (F-15-1) și a observației (F-15-4).
- **`checklist_riscuri_fizice`:** `by_cheie` dict-comprehension peste `identificate` (chei duplicate →
  suprascriere benignă); iterează catalogul fix de 8 riscuri. Robust.
- **`/api/aml/decizie.docx`:** `PersoanaFizica(**…)` + `genereaza_decizie_desemnare` prinse de
  `except ValueError` (ValidationError ⊂ ValueError) → 400, nu 500 (verificat: `tip_act` invalid → 400,
  `tip_entitate` necunoscut → 200 benign, PFA fără persoană → 400).
- **`serviciu.evalueaza_relatie`:** `_nume_screening` filtrează numele goale; `screening`/`avertisment_liste`
  gardate (try/except pe `date.fromisoformat`). Fără 500.

---

*Notă:* findings-urile reflectă starea worktree-ului principal `evaluare-anevar/src/evaluare/` la `HEAD` de pe
`master` în 2026-06-11 (commit `6c66e92`). Probe rulate cu `uv run python` / `PYTHONUTF8=1` pe Python 3.13.13.
F-15-1..4 sunt toate **fail-safe-able prin `max_length`** la nivel de schemă pydantic — fix de o linie/câmp,
fără atingerea logicii de business.
