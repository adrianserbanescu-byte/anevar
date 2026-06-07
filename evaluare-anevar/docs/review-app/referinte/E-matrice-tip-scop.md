# E — Matrice de conformitate tip × scop (SEV 2025)

> **Corecție de scop (Adi, 2026-06-06):** auditul precedent (`00-SINTEZA` + A–D) a fost restrâns greșit pe
> **casă+teren + garantare**. Aplicația suportă **toate tipurile** × **toate scopurile** prin `profil.py` (9 profile)
> + `assembler.rezolva_profil`. Acest document re-rulează conformitatea pe **întreaga matrice tip×scop**.
>
> **Surse:** `src/evaluare/profil.py` (profilele), `src/evaluare/assembler.py:61-74` (`rezolva_profil`),
> `tests/test_assembler_profil.py` (comportament asertat), `md files/standardele-de-evaluare-a-bunurilor-2025.md`.
> **Bucket:** **A**=cod (non-metodologie) · **B**=evaluator senior (metodologie/framing) · **C**=jurist.
> **NU s-a modificat cod.** Discrepanțele de framing sunt marcate **B** (confirmă evaluatorul).

---

## 0. Cum combină codul tip + scop (mecanica `rezolva_profil`)

`rezolva_profil(tip, scop, implicit)` (assembler.py:61-74) face, în ordine:

1. **Dacă `scop` ∈ {raportare_financiara, asigurare, impozitare, litigii}** → ia profilul **scopului**
   (`tip_valoare` + `ghid` + `abordari_aplicabile` din profilul de scop) și **suprascrie doar `tip_activ`** cu
   cel al tipului ales. ⇒ **tipul NU schimbă ghidul/abordările la scopuri speciale** — doar eticheta `tip_activ`.
2. **Dacă `scop` ∈ {garantare_credit, „garantare", absent}** → ia profilul **tipului** (casa/apartament/industrial/
   agricol/special). Aici **tipul decide totul** (ghid + abordări). Necunoscut → `implicit` (CASA_TEREN_GARANTARE).

**Consecință structurală critică pentru matrice:** pe **rândurile de scop special** (impozitare/raportare/asigurare/
litigii), celulele **industrial/agricol/special/apartament/casă au IDENTIC `ghid`, `tip_valoare`, `abordari`** —
diferă numai `tip_activ`. Deci o discrepanță pe „impozitare" (ghid greșit) e **aceeași pentru toate cele 5 tipuri**.

---

## 1. MATRICEA (5 tipuri × 5 scopuri = 25 combinații)

Legendă conformitate: ✅ = aliniat · 🟡 = parțial/framing de confirmat · ❌ = divergență confirmată față de standard.
„Abordări (noi)" = `abordari_aplicabile` din profilul rezolvat. „Profil sursă" = constanta din `profil.py`.

### 1A. Scop = GARANTARE (tipul decide; profilul = al tipului)

| Tip×Scop | Profil rezolvat | Ghid GEV (noi) | Ghid corect (standard) | Tip valoare (noi / corect) | Abordări (noi) vs cerute | Conf. | Bucket |
|---|---|---|---|---|---|---|---|
| **casă** × garantare | CASA_TEREN_GARANTARE | GEV_520 | GEV 520 (scop) + GEV 630 (metodă) | piață / piață ✅ | cost+comparație vs ≥1 adecvată; cost ≠ principal la imobil (§31) | 🟡 | B |
| **apartament** × garantare | APARTAMENT_GARANTARE | GEV_520 | GEV 520 + GEV 630 | piață / piață ✅ | comparație+cost ✅ (comparație principală) | ✅ | — |
| **industrial** × garantare | INDUSTRIAL | GEV_630 | GEV 520 (scop) + GEV 630 (metodă) | piață / piață ✅ | cost+venit+comparație vs ≥1 adecvată | 🟡 | B |
| **agricol** × garantare | AGRICOL | GEV_630 | GEV 520 (scop) + GEV 630 (metodă) | piață / piață ✅ | doar comparație vs ≥1 adecvată ✅ | 🟡 | B |
| **special** × garantare | SPECIAL | GEV_630 | GEV 520 (scop) + GEV 630 (metodă); SEV 233 dacă „în construire" | piață / piață ✅ | venit+comparație+cost; cost frecvent principal la bun special (§40.2.b SEV 103) | 🟡 | B |

> **Framing garantare (Bucket B, toate rândurile):** câmpul unic `ghid` nu poate ține simultan **ghidul de scop**
> (GEV 520 — obligatoriu pt. orice garantare, l.12527-12529) **și ghidul de metodă** (GEV 630 — imobile, l.5671).
> GEV 520 §19 (l.12601-12604) enumeră explicit *apartamente, spații industriale, proprietăți agricole* ca bunuri
> imobile sub garantare. Deci industrial/agricol/special pe `GEV_630` **pierd referința GEV 520** în acest câmp.
> Casă/apartament pe `GEV_520` **pierd referința GEV 630**. Ambele sunt corecte-pe-jumătate → **confirmă evaluatorul**
> care ghid se citează în raport (recomandare: raportul să **citeze ambele**: GEV 520 ca utilizare desemnată + GEV 630
> ca metodologie). Nu e bug de cod, e alegere de afișare.

### 1B. Scop = IMPOZITARE (profil IMPOZITARE; tip_activ variază, restul e fix)

| Tip×Scop | Profil rezolvat | Ghid GEV (noi) | Ghid corect (standard) | Tip valoare (noi / corect) | Abordări (noi) vs cerute | Conf. | Bucket |
|---|---|---|---|---|---|---|---|
| **casă** × impozitare | IMPOZITARE (tip=casa) | **GEV_630** | **GEV 500** (oblig., l.4041-4043) | **piață** / **valoare impozabilă** (l.4056-4061) | comparație+cost vs **cost obligatoriu** (§14 l.4111) | ❌ | B |
| **apartament** × impozitare | IMPOZITARE (tip=apart.) | **GEV_630** | **GEV 500** | **piață** / **valoare impozabilă** | comparație+cost vs cost obligatoriu | ❌ | B |
| **industrial** × impozitare | IMPOZITARE (tip=indust.) | **GEV_630** | **GEV 500** (nerezidențial, l.4039) | **piață** / **valoare impozabilă** | comparație+cost vs cost obligatoriu | ❌ | B |
| **agricol** × impozitare | IMPOZITARE (tip=agricol) | **GEV_630** | GEV 500 — dar GEV 500 evaluează **doar clădiri**, nu terenul (l.4046-4047) → teren agricol fără clădire = **gol** | **piață** / valoare impozabilă | comparație+cost | ❌ + gol | B |
| **special** × impozitare | IMPOZITARE (tip=special) | **GEV_630** | **GEV 500** | **piață** / **valoare impozabilă** | comparație+cost | ❌ | B |

### 1C. Scop = RAPORTARE FINANCIARĂ (profil RAPORTARE_FINANCIARA)

| Tip×Scop | Profil rezolvat | Ghid GEV (noi) | Ghid corect (standard) | Tip valoare (noi / corect) | Abordări (noi) vs cerute | Conf. | Bucket |
|---|---|---|---|---|---|---|---|
| **casă** × raportare | RAPORTARE_FINANCIARA | **GEV_500** | **SEV 430** (scop) + **GEV 630** (metodă imobil) | justă / justă ✅ | venit+comparație+cost vs cele adecvate ✅ | ❌ (ghid) | B |
| **apartament** × raportare | RAPORTARE_FINANCIARA | **GEV_500** | SEV 430 + GEV 630 | justă / justă ✅ | venit+comparație+cost ✅ | ❌ (ghid) | B |
| **industrial** × raportare | RAPORTARE_FINANCIARA | **GEV_500** | SEV 430 + GEV 630 | justă / justă ✅ | venit+comparație+cost ✅ | ❌ (ghid) | B |
| **agricol** × raportare | RAPORTARE_FINANCIARA | **GEV_500** | SEV 430 + GEV 630 | justă / justă ✅ | venit+comparație+cost | ❌ (ghid) | B |
| **special** × raportare | RAPORTARE_FINANCIARA | **GEV_500** | SEV 430 + GEV 630 (+ alocare §113-120) | justă / justă ✅ | venit+comparație+cost ✅ | ❌ (ghid) | B |

> **GEV_500 este definitiv GREȘIT pentru raportare financiară:** GEV 500 e ghidul de **impozitare** (titlu l.4021).
> Valoarea impozabilă „**nu reprezintă valoarea de piață, valoarea justă** sau oricare alte tipuri" (l.4059-4061).
> Pentru raportare se aplică **SEV 430** (l.11647) cu tip valoare **justă** ≈ piață (IFRS 13, G2 l.11869). `tip_valoare="justa"`
> e **corect**; **doar `ghid` e inversat** cu IMPOZITARE (vezi „inversiune încrucișată" §2.1).

### 1D. Scop = ASIGURARE (profil ASIGURARE)

| Tip×Scop | Profil rezolvat | Ghid GEV (noi) | Ghid corect (standard) | Tip valoare (noi / corect) | Abordări (noi) vs cerute | Conf. | Bucket |
|---|---|---|---|---|---|---|---|
| **casă** × asigurare | ASIGURARE | GEV_630 | **SEV 450** (scop) + GEV 630 (metodă cost) | asigurare / asigurare ✅ | doar **cost** vs cost de înlocuire/reconstruire TOTAL (§4.1 l.12427) ✅ | 🟡 | B |
| **apartament** × asigurare | ASIGURARE | GEV_630 | SEV 450 + GEV 630 | asigurare / asigurare ✅ | doar cost ✅ | 🟡 | B |
| **industrial** × asigurare | ASIGURARE | GEV_630 | SEV 450 + GEV 630 | asigurare / asigurare ✅ | doar cost ✅ | 🟡 | B |
| **agricol** × asigurare | ASIGURARE | GEV_630 | SEV 450 (clădiri agricole) | asigurare / asigurare ✅ | doar cost ✅ | 🟡 | B |
| **special** × asigurare | ASIGURARE | GEV_630 | SEV 450 + GEV 630 | asigurare / asigurare ✅ | doar cost ✅ | 🟡 | B |

> **Asigurare = în mare conform**, dar **ghidul precis e SEV 450** (l.12294), nu GEV 630. GEV 630 e acceptabil ca
> umbrelă imobiliară, însă raportul ar trebui să **citeze SEV 450** (cost de înlocuire **fără** depreciere economică,
> include demolare/moloz/onorarii §4.3-4.6, atenție la sub-asigurare §3.7). `tip_valoare="asigurare"` + `["cost"]` ✅.

### 1E. Scop = LITIGII (profil LITIGII)

| Tip×Scop | Profil rezolvat | Ghid GEV (noi) | Ghid corect (standard) | Tip valoare (noi / corect) | Abordări (noi) vs cerute | Conf. | Bucket |
|---|---|---|---|---|---|---|---|
| **casă** × litigii | LITIGII | GEV_630 | **fără GEV dedicat**; SEV 230 §20.6 (l.2736) listează litigiile; metodă = GEV 630 | piață / **depinde de speță** | comparație+cost ✅ | 🟡 | B/C |
| **apartament** × litigii | LITIGII | GEV_630 | SEV 230 + GEV 630 | piață / depinde de speță | comparație+cost ✅ | 🟡 | B/C |
| **industrial** × litigii | LITIGII | GEV_630 | SEV 230 + GEV 630 | piață / depinde | comparație+cost (venit lipsă pt. generatoare de venit) | 🟡 | B/C |
| **agricol** × litigii | LITIGII | GEV_630 | SEV 230 + GEV 630 | piață / depinde | doar comparație+cost ✅ | 🟡 | B/C |
| **special** × litigii | LITIGII | GEV_630 | SEV 230 + GEV 630 | piață / depinde | comparație+cost; cost adesea principal la special | 🟡 | B/C |

> **Litigii nu are ghid GEV dedicat** în SEV 2025 → GEV 630 (imobile) e încadrarea corectă de metodă; tipul valorii
> **depinde de obiectul disputei** (piață, justă, prejudiciu, expropriere-despăgubire). Hardcodarea `piata` e o
> presupunere rezonabilă-implicit, dar tipul ar trebui ales per speță (jurist/evaluator). Framing OK → **confirmă**.

---

## 2. Discrepanțe confirmate (cu citare linii standard)

### 2.1 🔴 INVERSIUNE ÎNCRUCIȘATĂ ghid: impozitare↔raportare (cea mai gravă)
- **Cod:** `IMPOZITARE → ghid="GEV_630"` (profil.py:62-65) și `RAPORTARE_FINANCIARA → ghid="GEV_500"` (profil.py:54-57).
- **Standard:** GEV 500 = „**Estimarea valorii impozabile a clădirilor**" — aplicare **obligatorie** pt. impozitare
  (l.4021-4022, l.4041-4043). Raportarea financiară se face pe **SEV 430** (l.11647) la **valoare justă** (l.11860).
- **Verdict:** cele două ghiduri sunt **schimbate între ele**. Impozitarea ar trebui pe **GEV 500**, raportarea **NU**
  pe GEV 500 (ci SEV 430 + GEV 630). `tip_valoare` este corect în ambele (impozitare=piață*, raportare=justă) — vezi nota*.
- **Confirmat ca intenționat-tested:** `test_assembler_profil.py:51-52` asertează explicit `impozitare→GEV_630` și
  `raportare_financiara→GEV_500`. Deci NU e regresie accidentală — e o **decizie de framing** scrisă în teste.
  → **Bucket B:** evaluatorul confirmă dacă e intenționat (improbabil, dat fiind §4-5 din GEV 500) sau de corectat.

### 2.2 🟡 Tip valoare la impozitare: `piata` vs „valoare impozabilă"
- **Cod:** `IMPOZITARE → tip_valoare="piata"`.
- **Standard:** valoarea impozabilă este un **tip distinct al valorii**, care „**nu reprezintă valoarea de piață,
  valoarea justă sau oricare alte tipuri**" (GEV 500 §4-5, l.4056-4061). `TipValoare` (profil.py:12) **nu are** o
  valoare „impozabilă" → nu poate fi exprimată. → **Bucket A** (plumbing tip) + **B** (confirmare metodologică).

### 2.3 🟡 Abordări la impozitare: cost nu e marcat obligatoriu
- **Cod:** `IMPOZITARE → ["comparatie", "cost"]` (comparație listată prima → sugerează principală).
- **Standard:** GEV 500 §14 (l.4109-4114): dacă se aplică o **singură** abordare, **trebuie să fie costul**; selecția
  finală = **minim**, fără medie ponderată (§34-35, l.4202-4215). Ordinea actuală inversează prioritatea. → **Bucket B**.

### 2.4 🟡 Garantare: ghid unic nu acoperă GEV 520 + GEV 630 simultan
- industrial/agricol/special × garantare → `GEV_630` **fără** GEV 520, deși GEV 520 e **obligatoriu** pt. orice
  garantare (l.12527-12529) și enumeră aceste tipuri (§19, l.12601-12604). Simetric, casă/apartament → `GEV_520` fără
  GEV 630. → **Bucket B** (raportul ar trebui să citeze **ambele**; un singur câmp `ghid` e insuficient).

### 2.5 🟡 Garantare: cost ca abordare (potențial) principală la imobil
- casă (`cost+comparatie`) și industrial (`cost+venit+comparatie`) listează **cost** primul. GEV 520 §31 (l.12695-12697):
  „se recomandă ca **în cazul bunurilor imobile abordarea prin cost să NU fie utilizată ca abordare principală**"
  (lichiditate). §34 (l.12709-12713): cost doar după acceptul scris al creditorului. → **Bucket B** (alertă, nu blocaj —
  deja semnalat ca #15 în `00-SINTEZA`).

### 2.6 🟡 Asigurare/Litigii: ghidul de scop nu e citat (SEV 450 / SEV 230)
- asigurare → `GEV_630` în loc de **SEV 450** (l.12294); litigii → `GEV_630` fără referința **SEV 230 §20.6** (l.2736).
  Metodologic acceptabil (cost imobil / piață imobil), dar **trasabilitatea ghidului de scop lipsește**. → **Bucket B**.

---

## 3. Goluri specifice per combinație (out-of-scope MVP, dar reale)

| Combinație | Gol specific | Bază standard | Bucket |
|---|---|---|---|
| **agricol × impozitare** | GEV 500 evaluează **doar clădiri**, nu terenul (l.4046-4047). Teren agricol fără clădire → impozitare necabilă pe acest ghid; teren impozitat pe alt regim fiscal. | GEV 500 §2 | B |
| **agricol × orice** | Profil AGRICOL = **doar comparație** (fără venit). Fermă generatoare de venit (arendă/producție) ⇒ abordarea prin venit lipsește. | SEV 103 §30.2 | B |
| **industrial × impozitare** | Industrial nerezidențial = **exact ținta GEV 500** (nerezidențial, l.4039), dar codul îl trimite pe GEV 630 + piață, nu cost-impozabil-minim. | GEV 500 §13-14, §35 | B |
| **industrial × raportare** | Venit DCF există în motor (`evalueaza_dcf`), dar profilul raportare nu forțează alocarea teren/construcție + echipamente distincte (cerută la raportare). | GEV 630 §113-120 (l.6408-6453) | A/B |
| **special × orice** | „Special" (proprietate cu piață limitată) ⇒ cost de înlocuire e adesea **principală** (SEV 103 §40.2.b, l.1421-1422) + risc de a nu exista comparabile (CMBU). Profilul listează comparație+venit ca opțiuni care pot lipsi. | SEV 103 §40.2; GEV 630 | B |
| **apartament × orice scop special** | Teren în **cotă indiviză** → alocarea/ separarea teren-construcție restricționată (GEV 630 §118.a l.6430-6435; GEV 500 §24,§28 cer teren **ne-indiviz**). La impozitare prin venit/piață ⇒ inaplicabil pe apartament. | GEV 500 §24/§28; GEV 630 §118 | B |
| **orice × litigii** | Tip valoare hardcodat `piata`; speța poate cere despăgubire/prejudiciu/valoare justă. Necesită selecție per caz. | SEV 230 §20.6; SEV 102 | B/C |
| **orice × în construire** | SEV 233 (l.3367) — niciun profil nu setează `ghid` la SEV 233 sau metoda **reziduală** (§100); proprietatea în curs de construire la garantare/raportare/impozitare/litigii nu e încadrată. | SEV 233 §20.2 (l.3413-3431) | B |

\* **Notă tip valoare impozitare:** marcat `piata` în cod, dar standardul cere tipul **distinct** „valoare impozabilă"
(§2.2). Conformitatea pe coloana „tip valoare" la impozitare e deci 🟡, nu ✅, chiar dacă numeric piața e punctul de plecare.

---

## 4. Sinteză buckets

- **Niciun bug de aritmetică** (consistent cu auditul precedent). Divergențele sunt de **încadrare (ghid/tip valoare)**.
- **Bucket B (confirmă evaluatorul) — toate discrepanțele de framing:** 2.1 (inversiune GEV 500↔630), 2.3, 2.4, 2.5, 2.6.
- **Bucket A (cod, fără metodologie):** plumbing `tip_valoare` ca să existe „valoare impozabilă" (2.2); dacă evaluatorul
  confirmă 2.1, fix-ul mapării ghidurilor e Bucket A (1 linie/profil + actualizare `test_assembler_profil.py:51-52`).
- **Bucket B/C (jurist):** tipul valorii la litigii per speță (2.x, §3).
- **Recomandare minimă fără atingerea formulei:** raportul să **citeze ambele ghiduri** la garantare (520+630) și
  **ghidul de scop** la asigurare/litigii (450/230); decuplarea „ghid de scop" vs „ghid de metodă" rezolvă 2.4+2.6 fără
  a schimba calculul.
