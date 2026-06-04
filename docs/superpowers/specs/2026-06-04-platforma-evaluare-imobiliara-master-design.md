# Plan-master — Platformă de evaluare imobiliară (toate tipurile, toate condițiile)

**Data:** 2026-06-04. **Tip:** spec de viziune + decompoziție + spec detaliat pentru Faza 0.
**Stadiu de pornire:** aplicația acoperă o singură celulă (casă+teren · garantare credit · valoare de
piață · cost+comparație · GEV 520), validată pe dosare reale GBF; 281 teste verzi; exe offline.

> **Domeniu de aplicare al acestui spec:** definește viziunea, arhitectura fundației și roadmap-ul
> fazat. **Doar Faza 0 (Fundația)** primește plan de implementare acum; fiecare fază ulterioară va avea
> propriul ciclu spec→plan→implementare.

---

## 1. Viziune & domeniu

Platformă de evaluare **imobiliară** care acoperă o matrice cu 5 axe, configurabilă — orice „celulă"
se obține prin **date de profil**, nu cod nou de fiecare dată.

| Axă | Variante (azi ✅) |
|---|---|
| **A. Tip activ** | casă✅, teren✅ · apartament · comercial (birou/retail) · industrial (hală/depozit) · agricol · special (hotel, benzinărie) · mixt |
| **B. Scop** | garantare credit✅ · raportare financiară (IFRS) · impozitare · asigurare · vânzare · litigii · expropriere · aport în natură |
| **C. Tip valoare** (SEV 102) | valoare de piață✅ · de investiție · justă (IFRS) · de lichidare/forțată · de asigurare · chirie de piață |
| **D. Abordare** | cost✅ · comparația vânzărilor✅ · **venit (capitalizare→DCF)** |
| **E. Ghid ANEVAR** | GEV 520✅ · GEV 630 (imobiliare) · GEV 500 (raportare financiară) … |

**În scope:** toate tipurile imobiliare și toate scopurile de mai sus.
**Out of scope (YAGNI):** evaluare de echipamente/mașini, întreprinderi (business valuation), active
necorporale — alt domeniu ANEVAR, nu imobiliar.

## 2. Arhitectura fundației (Varianta 1 — aprobată)

Refactor **incremental, ghidat de teste**. Patru piese:

1. **`ProfilEvaluare`** — sursa de adevăr a unei evaluări: `tip_activ`, `scop`, `tip_valoare`,
   `abordari_aplicabile`, `ponderi` (opțional), `ghid`. Profiluri predefinite (ex.
   `CASA_TEREN_GARANTARE` = comportamentul de azi).
2. **Registru de abordări** — `cost`, `comparatie`, `venit` cu o interfață comună
   `evalueaza(...) -> RezultatAbordare`. Profilul alege care rulează. Motoarele existente (cost, market,
   land) sunt **împachetate** în această interfață *fără a le schimba logica internă* (păstrăm validarea reală).
3. **Reconciliere parametrizată** — ponderează abordările active după profil. Profilul casă+teren dă
   exact rezultatul de azi.
4. **Raport pe secțiuni** — registru de secțiuni; profil + ghid decid ce apare (GEV 520 vs 630 vs 500).
   Profilul casă+teren/garantare produce un raport **identic** cu cel actual (test de regresie pe conținut).

**Principiu de migrare:** cazul existent devine prima „celulă" în noul cadru; **cele 281 de teste rămân
plasa de siguranță**. Nicio fază nu rupe fluxul curent.

## 3. Abordarea prin venit — v1 (capabilitatea nouă)

**Capitalizare directă:**

```
NOI = Venit brut potențial − Pierderi din neocupare/neîncasare − Cheltuieli de exploatare
Valoare = NOI ÷ rată de capitalizare
```

- **Model de date (`DateVenit`):** chirii (pe unități sau €/mp × suprafață închiriabilă), grad de
  neocupare (%), cheltuieli de exploatare (sumă sau % din venit), **rata de capitalizare** (input manual,
  cu notă de sursă — om-în-buclă).
- **Tip valoare** asociat: de regulă valoare de piață; suportă și valoarea de investiție.
- **Validare:** pe standard (SEV/IVS + GEV 630) + exemple sintetice deterministe. **Validarea pe dosar
  real = sarcină marcată explicit** (motorul rămâne parametrizat ca să se calibreze ușor).
- Calcule în `Decimal`; validări (rată > 0, procente în [0,1], valori ≥ 0).

## 4. Decompoziție în sub-proiecte (roadmap fazat)

Fiecare fază = spec→plan→implementare proprie. **Acum: plan doar pentru Faza 0.**

| Fază | Conținut | Deblochează |
|---|---|---|
| **0. Fundația** ⬅ acum | Profil + registru abordări + **venit (capitalizare directă)** + raport pe secțiuni; casă+teren remapat în cadru | cadrul + venit |
| 1. Apartament | profil rezidențial-apartament (etaj, an bloc, cotă teren, regim înălțime) | rezidențial garantare |
| 2. Comercial/închiriat | venitul devine abordare primară; GEV 630; chirii | birou/retail |
| 3. Industrial | cost + venit; specific hală/depozit/logistică | industrial |
| 4. Agricol/teren | comparație specifică; eventual venit agricol | agricol |
| 5. Scopuri noi | IFRS (valoare justă, GEV 500), asigurare (valoare de asigurare), impozitare, litigii | toate scopurile |
| 6. DCF + grilă chirii | adâncirea venitului (flux multi-anual + chirii comparabile) | venituri variabile |
| 7. Special | hotel, benzinărie (cazuri complexe, metode specifice) | nișă |

## 5. Faza 0 — Fundația (spec detaliat, plan-ready)

### 5.1 Componente noi / modificate
- `src/evaluare/profil.py` — `ProfilEvaluare` (Pydantic) + enumuri (tip_activ, scop, tip_valoare, ghid) +
  profiluri predefinite (`CASA_TEREN_GARANTARE`).
- `src/evaluare/engine/abordari.py` — protocolul `Abordare` + `RezultatAbordare` + adaptoare care
  împachetează `cost`, `market`+`land` (comparație) **fără** a schimba motoarele existente.
- `src/evaluare/engine/venit.py` — `DateVenit` + `evalueaza_venit()` (capitalizare directă).
- `src/evaluare/engine/reconciliation.py` — extins: selecție/ponderare după profil (backwards compatible).
- `src/evaluare/report/sectiuni.py` — registru de secțiuni + builder pe profil; `report/generator.py`
  refactorizat să-l folosească, păstrând ieșirea identică pentru profilul casă+teren/garantare.
- `assembler.py` / `models/report_context.py` — primesc `profil` (default `CASA_TEREN_GARANTARE`).

### 5.2 Flux de date
`ProfilEvaluare` → registrul rulează abordările `abordari_aplicabile` → `RezultatAbordare[]` →
reconciliere parametrizată → valoare finală → builder de raport pe secțiuni (filtrate de profil+ghid).

### 5.3 Tratarea erorilor
- Abordare cerută dar fără date suficiente → mesaj clar de validare (nu rezultat tăcut).
- Rată de capitalizare ≤ 0 sau lipsă → eroare explicită.
- Profil inconsistent (ex. abordare neaplicabilă tipului) → avertisment de validare.

### 5.4 Testare (TDD)
- **Regresie:** toate cele 281 de teste rămân verzi; profilul casă+teren reproduce exact valorile și
  conținutul raportului actual.
- **Nou:** `test_profil`, `test_abordari` (registru + adaptoare), `test_venit` (capitalizare pe exemple
  sintetice deterministe), `test_reconciliere_profil`, `test_report_sectiuni`.
- La final: rebuild exe + smoke.

### 5.5 În afara Fazei 0 (explicit)
- DCF și grila de chirii (Faza 6).
- Tipurile de proprietate noi efectiv și UI-ul lor (Fazele 1+) — Faza 0 livrează **cadrul + motorul de
  venit + teste** (backend), fără wizard/endpoint nou pe tip. Generalizarea wizardului și un eventual
  endpoint pentru venit vin cu primul tip nou (Faza 1/2).
- Scopuri/ghiduri noi de raport (Faza 5).

## 6. Principii & constrângeri (se păstrează)
Validat pe dovezi · om-în-buclă (AI propune, evaluatorul decide) · GDPR-first · **offline** ·
TDD + rebuild + smoke · ancorat în SEV 2025/IVS + GEV · compatibilitate înapoi la fiecare pas ·
wizardul rămâne navigare liberă (decizie anterioară).

## 7. Riscuri & întrebări deschise
- **Validare reală venit:** lipsește un dosar real la pornire (de obținut) — calibrare ulterioară.
- **Refactor raport:** trecerea la secțiuni trebuie să păstreze 1:1 ieșirea GEV 520 — test de regresie pe
  conținut obligatoriu.
- **Rata de capitalizare:** sursă externă (piață) — rămâne input manual cu notă, până la o eventuală bază.
- **Granularitatea profilelor:** riscul de over-engineering — Faza 0 livrează doar enumurile/profilele
  folosite acum + venit; restul se adaugă pe fază.
