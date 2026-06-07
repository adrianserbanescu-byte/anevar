# Metodologia de calcul — note factuale pentru REVIEW

> Document de referință pentru evaluatori autorizați. Conține EXACT ce calculează motorul,
> cu trimiteri la funcție/fișier. Toate căile sunt relative la `evaluare-anevar/`.
> Sursa de adevăr este codul; acest document a fost extras din cod, nu din presupuneri.
> Convenții în cod: procentele sunt fracții în `[0,1]` (0.05 = 5%); rotunjire `ROUND_HALF_UP`;
> aritmetică pe `Decimal` (nu `float`). Valorile sunt FĂRĂ TVA (`ReconciledResult.valoare_fara_tva = True`).

---

## 0. Harta motoarelor

| Abordare / pas | Fișier | Funcție-cheie |
|---|---|---|
| Cost (CIN) | `src/evaluare/engine/cost.py` | `compute_cib`, `compute_vcp`, `interpolate_depreciation`, `compute_cin`, `evaluate_cost` |
| Comparație — casă (preț total) | `src/evaluare/engine/market.py` | `_pret_baza_tranzactie`, `pret_total_corectat`, `ajustare_bruta`, `evaluate_market` |
| Comparație — teren (EUR/mp) | `src/evaluare/engine/land.py` | `_pret_baza_tranzactie`, `pret_mp_corectat`, `ajustare_bruta`, `evaluate_land` |
| Venit — grilă chirii | `src/evaluare/engine/chirie.py` | `chirie_mp_corectata`, `evalueaza_chirie`, `date_venit_din_chirie` |
| Venit — capitalizare directă + DCF | `src/evaluare/engine/venit.py` | `evalueaza_venit`, `evalueaza_dcf` |
| Reconciliere + alocare | `src/evaluare/engine/reconciliation.py` | `reconcile_profil`, `aloca_constructii` |
| Validări prudențiale | `src/evaluare/engine/validation.py` | `valideaza_proprietate`, `valideaza_comparabile`, `valideaza_depreciere` |
| Orchestrare | `src/evaluare/assembler.py` | `construieste_context`, `valideaza`, `rezolva_profil` |
| Profile | `src/evaluare/profil.py` | constantele `*_GARANTARE` etc. |

Orchestrarea în `construieste_context` (assembler.py:115–193) rulează doar abordările pentru care
există date de intrare; abordarea cerută explicit fără date ridică eroare (NU fallback tăcut —
assembler.py:161–164).

---

## 1. Cele 3 abordări

### 1.A COST — Cost de Înlocuire Net (CIN) — `cost.py`

Segregare pe elemente constructive (catalog IROVAL). Fiecare `CostElement`
(`models/property.py:9`) are `cantitate`, `cost_unitar` (lei/u.m., fără TVA), `an_pif`.

1. **CIB** (Cost de Înlocuire Brut), `compute_cib` (cost.py:10):
   `CIB = Σ cost_nou(element)`, unde `cost_nou = cantitate × cost_unitar` (property.py:19).
   — NU include TVA și NU include profitul dezvoltatorului (excluse din input; vezi checklist GEV 520).

2. **Vcp** (vârsta cronologică ponderată), `compute_vcp` (cost.py:15):
   `Vcp = Σ(vârstă_i × cost_nou_i) / Σ cost_nou_i`, unde `vârstă_i = an_referință − an_pif_i`
   (property.py:23). Dacă `Σ cost = 0` → `Vcp = 0`. Rezultatul se rotunjește la 2 zecimale
   (`evaluate_cost`, cost.py:64).

3. **Depreciere fizică Dfn**, `interpolate_depreciation` (cost.py:27): interpolare LINIARĂ în
   tabelul `depreciation_points` (vârstă→fracție), sortat după vârstă:
   `Dfn = D1 + (D2 − D1)/(V2 − V1) × (Vcp − V1)`.
   Sub primul / peste ultimul punct se face **clamp** la capete (cost.py:38–41). Tabel gol → eroare.

4. **CIN**, `compute_cin` (cost.py:50):
   `CIN = CIB × (1 − Dfn) × (1 − C_nf) × (1 − C_ex)`,
   unde `C_nf` = depreciere funcțională (`functional_depreciation`), `C_ex` = depreciere externă
   (`external_depreciation`) — fracții din `BuildingData` (property.py:44–45). Sunt aplicate
   MULTIPLICATIV (nu aditiv). Implicit 0; nenule cer justificare scrisă (vezi §4).

5. **Valoare prin cost**, `evaluate_cost` (cost.py:58):
   `valoare_cost = CIN + valoare_teren`. Dacă `valoare_teren` lipsește → `valoare_cost = None`
   (CIN se calculează oricum).

### 1.B COMPARAȚIE — grila pe DOUĂ etape

Modelul de ajustare `Adjustment` (`models/comparable.py:13`) are: `tip ∈ {procentuala, valorica}`,
`etapa ∈ {tranzactie, proprietate}`, `valoare` (fracție pentru procentuală; sumă pentru valorică),
`justificare`. Câmpul listă este `adjustments`.

**Metodologia comună (teren / casă / chirie):**
- **Etapa „tranzacție"** (ofertă→tranzacție, drept, finanțare, condiții vânzare, cheltuieli,
  condițiile pieței) → aplicată **SECVENȚIAL / COMPUS** pe preț, producând „prețul de bază":
  procentuală `preț = preț × (1 + valoare)`; valorică `preț = preț + valoare`
  (`_pret_baza_tranzactie`).
- **Etapa „proprietate"** (caracteristici fizice/juridice) → aplicată **ADITIV** pe prețul de bază:
  `final = bază × (1 + Σ%_proprietate) + Σ_EUR_proprietate`.

**Regula de SELECȚIE (unică, pe toate grilele):** comparabilul cu **ajustarea brută minimă pe etapa
de PROPRIETATE** (`index = min(... key=ajustare_bruta)`). Etapa de tranzacție NU se contorizează în
selecție.

#### Grila de TEREN — `land.py`
- `pret_mp_corectat` (land.py:38): bază tranzacție (compus) + proprietate (aditiv), pe `pret_mp`.
- `ajustare_bruta` (land.py:48): **Σ |valoare|** a ajustărilor **procentuale** din etapa proprietate
  (doar procentuale).
- `evaluate_land` (land.py:60): selectează comparabilul cu brută minimă →
  **`valoare_teren = pret_mp_ales × suprafață_subiect`** (land.py:71). Aici intră suprafața.

#### Grila de CASĂ — `market.py` (pe preț TOTAL, model GBF/ANEVAR)
- `pret_total_corectat` (market.py:43): bază tranzacție (compus) + proprietate (aditiv), pe `pret`
  (preț total al comparabilei).
- Diferența de **arie utilă** se tratează ca ajustare **VALORICĂ** (EUR/mp × Δmp) introdusă în
  `adjustments` pe etapa proprietate — fiecare comparabilă e adusă la subiect. (Documentat în
  docstring-ul market.py:1–13.)
- `ajustare_bruta` (market.py:53): Σ |procentuale_proprietate| **+** Σ|valorice_proprietate| / bază
  (valoricele raportate la prețul de bază). [Diferă de teren, care numără doar procentualele.]
- `evaluate_market` (market.py:81): selectează brută minimă →
  **`valoare_piata = pret_total_corectat` al comparabilei alese**. NU este preț unitar × suprafață;
  parametrul `suprafata_subiect` e păstrat doar pentru compatibilitate și NU intră în formulă
  (market.py:89, 97).
- `pret_unitar_brut = pret / suprafata` (market.py:25) — folosit doar pentru afișare și detecția de
  outlier (§4), nu în valoarea finală.

#### Tipuri de ajustare (rezumat)
| `tip` | Aplicare în „tranzacție" | Aplicare în „proprietate" |
|---|---|---|
| `procentuala` | compus: `× (1 + v)` | aditiv: parte din `Σ%` |
| `valorica` | compus: `+ v` | aditiv: parte din `Σ_EUR` |

### 1.C VENIT — `venit.py` + `chirie.py`

**Chirie de piață** (`chirie.py`): aceeași grilă în 2 etape ca terenul, pe `chirie_mp` (lunară/mp).
`evalueaza_chirie` (chirie.py:63) selectează brută minimă (Σ |procentuale_proprietate|) →
`chirie_lunara = chirie_mp_aleasă × suprafață`; **`venit_brut_potential (VBP anual) = chirie_lunara × 12`**
(chirie.py:77, constantă `_LUNI = 12`). `date_venit_din_chirie` (chirie.py:85) împachetează VBP în `DateVenit`.

**Capitalizare directă**, `evalueaza_venit` (venit.py:35):
- `pierdere = VBP × grad_neocupare`; `venit_efectiv = VBP − pierdere`;
- **`NOI = venit_efectiv − cheltuieli_exploatare`** (rotunjit 2 zecimale);
- **`valoare = NOI / rata_capitalizare`** (rotunjit 2 zecimale).
- Garduri: `rata_capitalizare ≤ 0` → eroare; `NOI ≤ 0` → eroare explicită (venit.py:42–46).
- Constrângeri input (`DateVenit`, venit.py:13): `VBP ≥ 0`, `0 ≤ grad_neocupare < 1`, `cheltuieli ≥ 0`.

**DCF**, `evalueaza_dcf` (venit.py:56):
`valoare = Σ_{t=1..n} flux_t / (1+r)^t + valoare_reziduală / (1+r)^n` (rotunjit 2 zecimale).
`r` = `rata_actualizare`; valoarea reziduală/terminală e actualizată cu factorul ultimului an `(1+r)^n`.
Garduri: `r ≤ 0` → eroare; listă goală de fluxuri → eroare. Intrări în `DateDCF` (venit.py:27).

> Notă: capitalizarea directă și DCF sunt alternative — în orchestrare (assembler.py:151–158)
> DCF intră la reconciliere DOAR dacă `metoda == "dcf"`; altfel intră capitalizarea directă.
> Ambele apar ca abordare cu eticheta `"venit"`.

---

## 2. Reconcilierea și alocarea — `reconciliation.py`

Funcția folosită în orchestrare este **`reconcile_profil`** (reconciliation.py:72), apelată din
assembler.py:175. Primește lista de `RezultatAbordare` (cost / comparatie / venit) și:
- `primara` = abordarea preferată (derivată din `metoda` — vezi mai jos);
- `ponderi` = dict opțional `nume→pondere`.

Logica:
1. **Cu ponderi și ≥ 2 abordări disponibile** cu pondere > 0:
   `valoare = Σ(valoare_a × pondere_a) / Σ pondere_a` (medie ponderată normalizată, rotunjită 2 zecimale),
   `metoda_selectata = "ponderata"` (reconciliation.py:90–93).
2. **Cu ponderi dar < 2 abordări**: ponderarea NU se aplică → selectează `primara` dacă există,
   altfel prima disponibilă, cu notă explicativă (reconciliation.py:94–101).
3. **Fără ponderi**: ia `primara` dacă există; altfel prima abordare disponibilă + notă
   (reconciliation.py:103–111).

**Maparea metodă→abordare primară** (assembler.py:166–174):
| `metoda` (input) | `primara` | `ponderi` |
|---|---|---|
| `venit` / `dcf` | `venit` | — |
| `cost` | `cost` | — |
| `piata` | `comparatie` | — |
| `ponderata` | `comparatie` | `{comparatie: pondere_piata, cost: 1 − pondere_piata}` |

`pondere_piata` implicit 0.5 (assembler.py:87), constrâns `[0,1]`. Etichetele de metodă în raport:
`{cost→cost, comparatie→piata, venit→venit}` (reconciliation.py:69).

> Există și o funcție mai veche `reconcile(market, cost, metoda, pondere_piata)`
> (reconciliation.py:13) care reconciliază doar piață↔cost; NU este folosită de orchestrarea curentă
> (assembler folosește `reconcile_profil`).

**Alocarea**, `aloca_constructii` (reconciliation.py:61):
**`valoare_construcții = valoare_proprietate − valoare_teren`**.
În assembler (assembler.py:177–179) se calculează doar dacă `valoare_teren` e cunoscută;
`valoare_proprietate` = valoarea finală reconciliată.

---

## 3. Profilele — `profil.py`

`ProfilEvaluare` (profil.py:17) câmpuri: `tip_activ`, `scop`, `tip_valoare`,
`abordari_aplicabile`, `ponderi`, `ghid ∈ {GEV_520, GEV_630, GEV_500, none}`.

Profilul determină FRAMING-ul raportului (tip valoare, abordări declarate, ghid GEV) — **NU** formula
numerică, care e condusă de `metoda` la Pas 4 (assembler.py:40–42, 119).

| # | Constantă | `tip_activ` | `scop` | `tip_valoare` | `abordari_aplicabile` | `ghid` |
|---|---|---|---|---|---|---|
| 1 | `CASA_TEREN_GARANTARE` | casa | garantare_credit | piata | cost, comparatie | **GEV_520** |
| 2 | `APARTAMENT_GARANTARE` | apartament | garantare_credit | piata | comparatie, cost | **GEV_520** |
| 3 | `COMERCIAL_INCHIRIAT` | comercial | garantare_credit | piata | venit, comparatie | GEV_630 |
| 4 | `INDUSTRIAL` | industrial | garantare_credit | piata | cost, venit, comparatie | GEV_630 |
| 5 | `AGRICOL` | agricol | garantare_credit | piata | comparatie | GEV_630 |
| 6 | `RAPORTARE_FINANCIARA` | comercial | raportare_financiara | **justa** | venit, comparatie, cost | **GEV_500** |
| 7 | `ASIGURARE` | casa | asigurare | **asigurare** | cost | GEV_630 |
| 8 | `IMPOZITARE` | casa | impozitare | piata | comparatie, cost | GEV_630 |
| 9 | `LITIGII` | casa | litigii | piata | comparatie, cost | GEV_630 |
| 10 | `SPECIAL` | special | garantare_credit | piata | venit, comparatie, cost | GEV_630 |

> Sunt definite 10 constante de profil; tabelul listează toate. Maparea „9 profile (tip × scop)" din
> brief corespunde celor cablate în orchestrare prin `rezolva_profil`: 5 după TIP
> (`PROFIL_DUPA_TIP` — casa, apartament, industrial, agricol, special; assembler.py:43–49) + 4 după
> SCOP special (`PROFIL_DUPA_SCOP` — raportare_financiara, asigurare, impozitare, litigii;
> assembler.py:53–58). `COMERCIAL_INCHIRIAT` este definit dar NU e cablat în cele două dicționare.

**`rezolva_profil`** (assembler.py:61):
- Scop special (≠ garantare) → profilul scopului (impune `tip_valoare` + `ghid`), păstrând
  `tip_activ` din tipul ales (assembler.py:68–73).
- Scop garantare/absent → profilul după tip; necunoscut → `implicit` (CASA_TEREN_GARANTARE).

> OBSERVAȚIE de verificat la review (semnalată în jurnalul proiectului, nu corectată în cod):
> `IMPOZITARE` are `ghid = GEV_630`, dar GEV 500 este ghidul pentru valoarea impozabilă a clădirilor;
> `RAPORTARE_FINANCIARA` are `GEV_500`. Posibilă inversare ghid impozitare↔raportare. Codul curent
> este cel din tabel; de validat de evaluator.

Secțiunile de raport sunt filtrate după ghid (`report/sectiuni.py:1–21`): de ex. `abordare_venit`
doar la GEV_630, `gev_520` doar la GEV_520, `raportare_financiara` doar la GEV_500.

---

## 4. Garduri / alerte prudențiale

> PRINCIPIU: validările produc liste de `Issue` cu `nivel ∈ {blocheaza, alerteaza}`
> (`validation.py:14, 21`). În practica UI curente (router `web/routers/curent.py:146`) ele sunt
> expuse ca **„alerte"** spre evaluator; motorul NU oprește generarea — evaluatorul decide. „blocheaza"
> marchează erori de date care fac calculul nevalid (ex. suprafețe ≤ 0), nu un refuz al aplicației.

Orchestratorul rulează (`valideaza`, assembler.py:101):
- `valideaza_proprietate` + `valideaza_depreciere` — **întotdeauna**;
- `valideaza_comparabile` — **doar** dacă `metoda ∈ {piata, ponderata}` (assembler.py:110–111).
- `valideaza_profil` există (validation.py:90) dar NU e apelat din `valideaza`.

**Praguri (constante, validation.py:16–18):**
| Constantă | Valoare | Unde se aplică |
|---|---|---|
| `LIMITA_AJUSTARE_BRUTA` | **0.25 (25%)** | ajustarea **BRUTĂ** a unei comparabile de casă (`ajustare_bruta`, etapa proprietate) |
| `PRAG_OUTLIER` | **0.50 (50%)** | deviația relativă a prețului unitar brut față de **mediana** comparabilelor |
| `MIN_COMPARABILE` | **3** | număr minim de comparabile |

**`valideaza_proprietate`** (validation.py:28) → toate `blocheaza`:
`suprafata teren > 0`; `Au > 0`; `Acd > 0`; **`Au ≤ Acd`**; (apartament) `etaj ≤ nr_niveluri_bloc`.

**`valideaza_comparabile`** (validation.py:46):
- `< 3 comparabile` → **blocheaza** (și se oprește);
- pentru fiecare, dacă `|pret_unitar − mediană| / mediană > 0.50` → **alerteaza** „outlier";
- pentru fiecare, dacă `ajustare_bruta(c) > 0.25` → **alerteaza** „depășește limita".

**`valideaza_depreciere`** (validation.py:76): dacă `C_nf > 0` sau `C_ex > 0` și
`justificare_depreciere` e goală → **blocheaza** (cere justificare scrisă).

**Verificare de consistență cost↔piață (raport, NU validare de input)** — `report/generator.py:438–450`,
`_adauga_alocare`: dacă `|(CIN − valoare_construcții_alocată)/CIN| > 0.20 (20%)` → text bold
„VERIFICARE DE CONSISTENȚĂ (GEV 520)" care cere justificarea diferenței. Este o alertă în corpul
raportului, generată determinist; nu blochează.

> Despre pragul „15%" din brief: în COD, constanta engine pentru ajustarea brută este **25%**
> (`LIMITA_AJUSTARE_BRUTA = 0.25`), iar verificarea de consistență din raport folosește **20%**.
> Nu există constantă `0.15`/15% în motor. Pragul de 15% (dacă apare în referințele GEV 520 pentru
> ajustarea NETĂ) NU este implementat ca gardă în cod — `ajustare_neta` este calculată și afișată
> (market.py:69, land.py:54, chirie.py:57) dar nu generează alertă. De confirmat la review dacă se
> dorește o gardă pe ajustarea netă.

---

## 5. Determinist (motor) vs. input/evaluator

**DETERMINIST — calculat de motor** (din intrări → ieșire reproductibilă, `Decimal`):
- Cost: CIB, Vcp, Dfn (interpolare+clamp), CIN, valoare_cost (cost.py).
- Comparație: prețuri corectate pe etape, ajustări brute/nete, **selecția comparabilei (brută minimă)**,
  valoare piață / valoare teren (market.py, land.py).
- Venit: chirie corectată + selecție, VBP, NOI, valoare prin capitalizare, valoare DCF (chirie.py, venit.py).
- Reconciliere (selecție sau medie ponderată normalizată) + alocare construcții (reconciliation.py).
- Rezolvarea profilului din tip+scop și filtrarea secțiunilor după ghid (assembler.py, sectiuni.py).
- Toate validările/pragurile prudențiale și verificarea de consistență 20% (validation.py, generator.py).

**INPUT / DECIZIA EVALUATORULUI** (motorul NU le inventează):
- Segregarea pe elemente: `element, cod, um, cantitate, cost_unitar, an_pif` (din catalog IROVAL).
- Tabelul de depreciere fizică `depreciation_points` (perechile vârstă→fracție).
- Deprecierile funcțională/externă `C_nf`, `C_ex` + justificarea scrisă.
- **Toate ajustările din grile** (`Adjustment`: tip, etapă, valoare, justificare) — inclusiv ajustarea
  de arie utilă (valorică) și clasificarea tranzacție vs. proprietate. (Docstring market.py:40:
  „de stabilit de evaluator la inspecție".)
- Comparabilele și sursele lor; suprafețele subiectului (Au, Acd, AC, suprafață teren).
- `metoda` (cost/piata/ponderata/venit/dcf) și `pondere_piata`.
- Parametri de venit: `rata_capitalizare`, `grad_neocupare`, `cheltuieli_exploatare`, fluxuri DCF,
  `rata_actualizare`, `valoare_reziduala`.
- `valoare_teren` manuală (dacă nu există comparabile de teren — assembler.py:124–127).
- Profilul (tip activ + scop) și toate metadatele lucrării (`EvaluationMeta`).
- Factorul de garanție/lichiditate (raport: 0,80–0,90 „se stabilește de evaluator" — generator.py:492–494).
- Narativul AI (generat de LLM, marcat `[AI]`; restul valorilor sunt `[CALCULAT]`).

---

### Anexă: rotunjiri și unități
- Rotunjiri la 2 zecimale (`ROUND_HALF_UP`): Vcp (cost.py:64), NOI și valoare venit (venit.py:41,47),
  DCF (venit.py:72), chirie lunară și VBP (chirie.py:76–77), medie ponderată reconciliere
  (reconciliation.py:92). CIB/CIN/valoare_piata/valoare_teren NU sunt rotunjite explicit în engine
  (rămân `Decimal` la precizie completă; rotunjirea de afișare se face în stratul de raport).
- Costuri unitare = lei/u.m. FĂRĂ TVA (property.py:16). VBP = chirie lunară × 12 (anual).
- Procente = fracții `[0,1]`. Valoarea finală e fără TVA (`results.py:36`).
