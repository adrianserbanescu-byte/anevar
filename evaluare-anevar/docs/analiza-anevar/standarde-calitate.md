# Standarde de calitate, studii de piață și glosar — analiză vs. SEV 2025

> **Temă:** asigurarea calității în evaluare + recomandări studii de piață (art. 111 Cod fiscal) +
> glosarul oficial ANEVAR de termeni + (control) HCD 55/2017. Scop: ce recomandări de
> **calitate / studii de piață / terminologie** ar trebui aplicația să respecte față de SEV 2025, și
> ce e deja implementat în cod.
>
> **Surse analizate:**
> - `asigurarea-calitatii-in-activitatea-de-evaluare-recomandari.txt` (recomandări ANEVAR privind un
>   sistem de asigurare și control al calității — text complet)
> - `anexa-hcd-74-recomandari-studii-de-piata.txt` (Anexa la HCD nr. 74/2022 — studiile de piață
>   notariale prevăzute la art. 111 din Codul fiscal)
> - `glosar.pdf` (Glosarul oficial ANEVAR de termeni — citit vizual; aliniat la IVS/SEV 2025)
> - `hcd_55_din_2017.pdf` (Îndrumar de evaluare — **evaluarea bunurilor culturale mobile**, citit vizual)
>
> **Referință de prioritate:** SEV 2025 (`standardele-de-evaluare-a-bunurilor-2025.md`) +
> `docs/SEV-2025-ce-putem-folosi.md` / `SEV-2025-gap-implementare.md`. **Regula contradicțiilor:** SEV 2025
> primează; în rest documentul mai nou. (Glosarul de pe site-ul ANEVAR e cel mai recent — © 2026 — și
> conține deja definiția „Evaluare" din ediția 2025, deci e perfect concordant cu SEV 2025.)
>
> ⚠️ Document de analiză metodologică. Decizia de conformitate revine evaluatorului autorizat / ANEVAR,
> nu aplicației.

---

## 0. Verdict de relevanță per document (citește întâi)

| Document | Relevanță pentru app (casă+teren / garantare credit) | De ce |
|---|---|---|
| **Glosar ANEVAR** | 🟢 **FOARTE MARE** | Vocabularul obligatoriu: termenii de folosit **consecvent** în UI și raport. Aliniat la SEV 2025. |
| **Asigurarea calității** | 🟢 **MARE** | Definește sistemul de QC intern (verificare înainte de emitere) + structura **dosarului de lucru** — temă transversală pe toată misiunea, parțial neimplementată ca feature. |
| **Anexa HCD 74 (studii de piață art. 111)** | 🟡 **MICĂ / INDIRECTĂ** | Studiile notariale **NU sunt rapoarte de evaluare** și **NU pot fi sursă** pentru rapoarte (§28). Nu e fluxul nostru. Util doar ca: (a) sursă oficială de prețuri-ancoră (grile notariale), (b) o terminologie de **ne-confundat** cu valoarea de piață. |
| **HCD 55/2017 (bunuri culturale mobile)** | 🔴 **ZERO** | Îndrumar pentru specializarea **EBM** (tablouri, icoane, monede). Alt domeniu; aplicabil doar de evaluatori EBM. Exclus din app. Reținem doar 1 idee transversală (vezi 1.C). |

---

## 1. CE CONȚINE + CE-I UTIL pentru aplicație

### A. Asigurarea calității în activitatea de evaluare (recomandări ANEVAR)

Document de tip „politici și proceduri de QC", structurat pe 5 elemente ale unui sistem de asigurare și
control al calității + un capitol despre **dosarul de lucru**:

1. **Responsabilitățile privind calitatea** — o cultură internă bazată pe calitate; o persoană cu atribuții
   de QC la nivel operațional.
2. **Cerințe de etică / independență** — comunicarea cerințelor de independență, identificarea
   amenințărilor, **confirmare scrisă anuală** a respectării independenței.
3. **Acceptarea / continuarea relațiilor cu clienții** — competență + capacitate (timp/resurse) + integritatea
   clientului; **termeni de referință agreați în scris la începere**; ce faci dacă afli ulterior date care ar
   fi dus la refuz.
4. **Resurse umane** — coordonator de misiune; personal cu competența necesară.
5. **Realizarea evaluării** — consecvență, **supervizare și verificare internă a calității ÎNAINTE de
   emiterea raportului**, de către o persoană calificată care **idealmente NU e din echipa care a evaluat**;
   pașii verificării (a–e): discuție cu coordonatorul, citirea raportului + anexelor, revizuirea dosarului de
   lucru, analiza adecvării concluziilor la scop, **documentarea verificării** (cu autorizarea emiterii doar
   după corecții).
6. **Dosarul de lucru** (recomandat în format electronic) cu structură fixă: **(1) Contractare** (ofertă,
   contract, termeni de referință, PV predare-primire, comenzi, facturi); **(2) Informații de la client**
   (cererea de informații + documentele în original); **(3) Prelucrări evaluator** (inspecție: foto/fișe;
   informații de piață: printscreen-uri, link-uri, date; fișiere de lucru/calcule); **(4) Raport** (variantă
   preliminară + finală). Confidențialitate + integritate + accesibilitate + **păstrare** pe durata cerută.

**Util pentru app:** acesta e **modelul-țintă pentru bucla de „flux livrabile" + dosar** și pentru un
**checklist de QC pre-emitere** (vezi gap-uri G-Q1…G-Q4). Aplicația organizează deja un „dosar" și
generează raport — dar nu materializează **pasul de verificare internă** și nici structura formală a
dosarului de lucru cerută aici.

### B. Anexa HCD 74/2022 — studii de piață (art. 111 Cod fiscal)

Recomandări pentru **studiile de piață notariale** (valorile minime pe piața imobiliară din anul precedent,
folosite de notari pentru calculul impozitului la transferul proprietății). Conține: definiții
(„valoarea minimă prevăzută de Codul fiscal" = **tip de valoare distinct**, exclusiv pentru aceste studii),
responsabilități, surse de informații, metodologie (termeni de referință → zonarea localității → prezentarea
datelor → analiza datelor → selectarea valorilor minime → anexe).

**Puncte de reținut (nu de implementat, ci de respectat ca graniță conceptuală):**
- §4–5: studiile de piață **NU sunt rapoarte de evaluare**, nu estimează valori individuale, nu aplică
  metodologii/ajustări/indexări; tipul valorii **NU poate fi asimilat cu „valoarea de piață"** din SEV.
- §28: aceste studii **NU pot fi folosite ca sursă de valori de referință** pentru elaborarea sau
  verificarea rapoartelor de evaluare, în nicio circumstanță.

**Util pentru app:** practic doar terminologic și ca avertizare — dacă vreodată cineva ar vrea să „tragă"
valori din grile notariale ca input de comparabile, aplicația **trebuie să le respingă/eticheteze** ca
ne-eligibile (sunt valori minime, nu valori de piață). Nu e nevoie de niciun motor nou.

### C. HCD 55/2017 — bunuri culturale mobile (control)

Îndrumar pentru specializarea **EBM** (descoperiri arheologice, opere de artă, icoane, monede, mobilier
etnografic etc.). Explicit **nu** se aplică mașinilor/echipamentelor/imobilelor. **Zero suprapunere** cu
fluxul nostru. Singura idee transversală reutilizabilă: distincția **macroidentificare** (categoria
activului) vs. **microidentificare** (caracteristicile specifice) — un principiu general de identificare,
deja acoperit de fapt la noi prin `tip_activ` + descrierea proprietății.

### D. Glosarul ANEVAR (cel mai important livrabil al temei)

Glosar oficial, aliniat la **IVS / SEV 2025** (conține definiția „Evaluare" marcată explicit „ediția 2025"
și termeni-novație 2025: **ESG, specialist, scepticism profesional, model automat de evaluare (AVM), riscul
evaluării, utilizare desemnată / utilizator desemnat**). Rol declarat: **utilizarea unitară a limbajului**,
eliminarea ambiguităților, corelarea cu standardele în vigoare. Termeni-cheie pentru noi (RO → EN):

| Termen RO (de folosit) | Definiție pe scurt | EN | Notă pentru app |
|---|---|---|---|
| **Valoare de piață** | suma estimată la data evaluării, cumpărător/vânzător hotărâți, tranzacție nepărtinitoare | market value | tip valoare default — OK |
| **Utilizare desemnată** | motivul pentru care se estimează valoarea (fostul „scop") | intended use | ⚠️ UI folosește încă „Scop" |
| **Utilizator desemnat** | terțul căruia i se acordă dreptul de a utiliza raportul (ex. banca) | intended user | OK în model (`utilizator_desemnat`) |
| **Tipul (tipurile) valorii** | ipotezele fundamentale ale valorii raportate (SEV 102) | basis(es) of value | OK |
| **Abordare în evaluare** | cost / venit / piață | valuation approach | ⚠️ UI scrie „comparatie", glosar „abordarea prin piață" |
| **Proprietate comparabilă** | proprietate vândută/ofertată recent, similară, ajustabilă credibil | — | OK conceptual |
| **Elemente de comparație** | caracteristicile tranzacției/bunului care explică diferențele de preț | — | grila de ajustări |
| **Scepticism profesional** | judecată analitică + analiză critică a informațiilor | professional scepticism | ✅ în declarație |
| **Raționament profesional** | folosirea cunoștințelor/experienței pentru o decizie informată | professional judgement | — |
| **Riscul evaluării** | posibilitatea ca valoarea să nu fie adecvată utilizării desemnate | valuation risk | concept nou 2025 |
| **Factori ESG** | mediu, social, guvernanță | ESG | 🔴 lipsă secțiune (vezi gap SEV-2025 G1) |
| **Specialist** | expert tehnic care asistă evaluarea/verificarea | specialist | termen 2025 |
| **Model automat de evaluare (AVM)** | calcul automat fără raționament profesional pe model | AVM | ⚠️ relevant pt. disclaimer app |
| **Dosar de lucru** | date/documente care susțin analizele și **demonstrează conformitatea cu SEV** | — | 🟡 vezi G-Q2 |
| **Verificarea evaluării / a procesului / a valorii** | tipuri de verificare (review) | valuation review | leagă de SEV 400 + QC |
| **Evaluarea pentru garantarea împrumutului** | raport în scopul garantării unui credit acordat de o instituție de credit | — | fluxul nostru #1 |
| **Evaluare globală** | evaluarea sistematică a unor grupuri de bunuri, fără inspecție, pe parcursul creditului | — | de NU confundat cu evaluarea individuală |
| **Cost de nou / Cost net (cost depreciat)** | cost de înlocuire/reconstrucție de nou, resp. minus deprecierea | — | OK în motorul de cost |
| **Vârsta efectivă** | vârsta aparentă în funcție de stare (≠ cronologică) | — | input depreciere |
| **Alocarea valorii** | separarea valorii în construcție + teren | — | ✅ avem secțiune alocare |
| **Zonare** | condiții permisive/restrictive din legislația de utilizare a terenului | — | leagă de certificat urbanism |
| **Amplasament / Teren viran / Teren în exces / în surplus** | tipuri/stări de teren | — | util la motor teren |

**Util pentru app:** glosarul = **dicționarul de referință pentru un audit terminologic** al UI + raport +
texte generate. Două câștiguri concrete: (1) consecvență (un singur termen pentru un concept), (2) un
**glosar in-app** (tooltips / pagină de ghid) care explică termenii pentru beneficiari/bănci — exact rolul
educativ pe care glosarul și-l asumă.

---

## 2. RELEVANȚA vs. SEV 2025 + CONTRADICȚII rezolvate

### 2.1 Concordanță (cine câștigă + de ce)

- **Glosarul ↔ SEV 2025: concordanță deplină.** Glosarul e versiunea-dicționar a aceluiași corp normativ
  (IVS 2025 → SEV 2025). Acolo unde apare o nuanță, **SEV 2025 primează** (regula temei), dar nu există
  contradicție reală — glosarul citează explicit SEV 102, GEV 500/520/630, ediția 2025.
- **Asigurarea calității ↔ SEV 100/101 + SEV 400:** complementare. Recomandările de QC sunt „cum"-ul
  operațional al cerinței SEV 100 par. 20 („procedură de verificare a calității procesului") și al SEV 400
  (verificarea evaluării). Nicio contradicție; recomandările sunt **mai detaliate** decât textul SEV, deci
  le folosim ca ghid de implementare a cerinței SEV.
- **HCD 74 ↔ SEV 2025:** **fără conflict, prin construcție.** HCD 74 spune chiar el (§5, §28) că valoarea
  din studiile notariale **nu e** valoare de piață SEV și **nu** alimentează rapoarte. Deci, departe de a
  contrazice SEV, trasează granița. Implicație de produs: **nu amesteca cele două surse**.

### 2.2 Contradicție terminologică internă rezolvată (SEV 2025 câștigă)

| Concept | Termen vechi (în cod/UI azi) | Termen SEV 2025 / glosar (de adoptat) | Cine câștigă & de ce |
|---|---|---|---|
| Motivul evaluării | **„Scop" / „Scopul evaluării"** (UI `dosar.html`, model `scop`) | **„Utilizare desemnată"** (fostul „scop" → redenumit în SEV 102, 2025) | **SEV 2025.** E o renumire explicită din ediția 2025 (vezi `SEV-2025-ce-putem-folosi.md` N3). De afișat „Utilizare desemnată", cu „(scop)" în paranteză pentru tranziție. |
| A treia abordare | **„comparatie"** (enum `Abordare`, UI) | **„abordarea prin piață"** (glosar: *Abordare în evaluare*) | **Glosar/SEV.** „piață" e termenul canonic; „comparația vânzărilor" e *metoda* din cadrul abordării prin piață. UI ar trebui să spună „abordarea prin piață". |
| Valoarea pentru asigurare | corect: cost de reconstrucție brut | „Cost de nou" / SEV 450 | concordant — fără schimbare |

> Notă: aceste sunt ajustări **de etichetă/limbaj**, nu de motor. Riscul e doar de percepție de
> ne-conformitate la o verificare ANEVAR/bancă, nu de calcul greșit.

---

## 3. GAP-URI de implementare (ce ar trebui app-ul să facă/adauge)

> Severitate: **blocant** (raport ne-conform / respins) · **important** (slăbește conformitatea, nu blochează
> un dosar rezidențial simplu) · **minor** (cosmetic / nișă). Verificat în cod la data analizei.

### Calitate (din recomandările de asigurare a calității)

| # | Gap | Cerință | Stare în cod | Severitate |
|---|---|---|---|---|
| **G-Q1** | **Pas de verificare internă a calității înainte de emitere** — checklist QC live (coerență date intrare + calcule + adecvare la scop), bifat din datele dosarului, cu „autorizare emitere doar după corecții" | Asig. calității §5 (a–e) + SEV 100 par. 20 | Doar **afirmație** în declarația de conformitate (`report/generator.py:264–265`) — **nu există** o procedură/checklist efectivă în UI | **important** |
| **G-Q2** | **Structura formală a dosarului de lucru** (4 secțiuni: Contractare / Info client / Prelucrări evaluator / Raport) + retenție + integritate | Asig. calității, cap. „Dosarul de lucru" | App are „dosar" + versionare/audit (storage.py), dar **nu** structurat pe cele 4 secțiuni cerute; lipsesc explicit: ofertă/contract, termeni de referință ca artefact, PV predare-primire | **important** |
| **G-Q3** | **Termeni de referință agreați în scris la începere** ca artefact distinct (nu doar capitol în raport) | Asig. calității §3; SEV 101 | Termenii apar **în raport** (`_termeni_referinta`), dar nu ca document semnat la start | **minor** |
| **G-Q4** | **Confirmare independență / acceptarea misiunii** (verificare conflict de interese + integritate client + competență/capacitate la acceptare) | Asig. calității §2, §3 | Declarația de independență e în raport; **nu** există pas de „acceptare/continuare" la deschiderea dosarului (se leagă și de gap-ul EBA din `SEV-2025-gap-implementare.md` G4) | **important** |

### Terminologie (din glosar)

| # | Gap | Cerință | Stare în cod | Severitate |
|---|---|---|---|---|
| **G-T1** | **Audit terminologic UI+raport** și redenumire „Scop"→„Utilizare desemnată", „comparatie"→„abordarea prin piață" | Glosar + SEV 102 (2025) | UI `dosar.html:122` „Scop"; enum `Abordare="comparatie"` (`profil.py:13`) | **minor** (percepție conformitate) |
| **G-T2** | **Glosar in-app** (pagină/tooltips) cu termenii-cheie RO(+EN) pentru beneficiari/bănci | rolul educativ declarat al glosarului | Inexistent (există doar ghid FAQ în `data/documente/ghid`) | **minor** |
| **G-T3** | **Disclaimer „NU este AVM"** — glosarul definește AVM ca model fără raționament profesional; app-ul produce **draft** asistat, verificat de evaluator | Glosar (AVM) + poziționare legală | Disclaimerul existent spune „draft + evaluatorul verifică" (task #12/#13) — **de întărit** cu mențiunea explicită „nu este model automat de evaluare în sensul SEV" | **minor** |
| **G-T4** | **Termen valoare ESG / riscul evaluării** în raport | Glosar (ESG, riscul evaluării) — novație 2025 | 🔴 lipsă (suprapunere cu `SEV-2025-gap-implementare.md` **G1** — secțiune ESG) | **blocant** *(deja urmărit ca G1 ESG)* |

### Studii de piață (din HCD 74)

| # | Gap | Cerință | Stare în cod | Severitate |
|---|---|---|---|---|
| **G-S1** | **Gardă anti-contaminare**: dacă un comparabil provine dintr-o grilă/studiu notarial (art. 111), aplicația trebuie să-l **respingă sau eticheteze** ca ne-eligibil (e valoare minimă, nu valoare de piață) | HCD 74 §5, §28 | Nicio verificare; sursele de comparabile nu poartă metadată de proveniență (se leagă de ierarhia datelor SEV 104 — `SEV-2025-gap-implementare.md` G12) | **minor** |
| **G-S2** | (Non-gap) Grilele notariale 2026 ca **ancoră oficială de sanity-check**, marcate clar ca „valoare minimă, nu valoare de piață" | — (idee de feature) | — | **minor / opțional** |

> **Notă de delimitare:** aplicația **NU trebuie** să implementeze un motor de studii de piață notariale
> (art. 111) — e o activitate separată, cu tip de valoare diferit, interzisă ca sursă de raport. HCD 55
> (bunuri culturale) e complet în afara scopului.

---

## 4. Prioritizare

**Important (de făcut pentru maturitatea de QC):**
1. **G-Q1** — checklist live de verificare a calității pre-emitere (transformă afirmația din declarație
   într-o procedură reală; cel mai mare câștig de conformitate pe tema „calitate").
2. **G-Q4** — pas de acceptare a misiunii (conflict de interese + competență) la deschiderea dosarului.
3. **G-Q2** — structurarea dosarului de lucru pe cele 4 secțiuni ANEVAR + retenție/integritate.

**Minor (curățenie terminologică & UX, ieftine):**
4. **G-T1/G-T2/G-T3** — audit terminologic + glosar in-app + întărirea disclaimer-ului AVM.
5. **G-S1** — etichetarea provenienței comparabilelor (anti-contaminare notarială).

**Deja urmărit în alt livrabil:**
- **G-T4 (ESG / riscul evaluării)** = **G1** din `docs/SEV-2025-gap-implementare.md` (blocant) — nu se
  dublează aici; doar se confirmă că glosarul îl validează ca terminologie obligatorie 2025.

---

**Documente conexe:** `docs/SEV-2025-ce-putem-folosi.md`, `docs/SEV-2025-gap-implementare.md`,
`docs/SEV-2025-cerinte-per-tip-imobil.md`, `docs/GEV520-2025-crosscheck.md`.
