# Analiză articole metodologie piață (set 2) — abordarea prin venit, prețul terenurilor, procesul de evaluare

> **Temă:** `articole-piata-2`
> **Autor articole:** Adrian Nicolescu (4 articole de metodologie, fără dată internă — texte didactice, nedatate).
> **Surse (.txt):**
> - `Rata de capitalizare poate deforma valoarea de piata.txt`
> - `Rolul pretului in tranzactiile cu terenuri.txt`
> - `Sa intelegem procesul de evaluare imobiliara.txt`
> - `Taxarea serviciilor si Managementul cladirilor.txt`
> **Referință de prioritate:** SEV 2025 (`md files/standardele-de-evaluare-a-bunurilor-2025.md`) + analizele existente
> `docs/SEV-2025-ce-putem-folosi.md`, `docs/conformitate/B-abordari-metode.md`.
> **Cod verificat:** `src/evaluare/engine/venit.py`, `engine/chirie.py`, `engine/land.py`, `engine/validation.py`,
> `engine/metodologie.py`, `assembler.py`, `profil.py`.
> **Data analiză:** 2026-06-11.
>
> ⚠️ Document de analiză metodologică (input de produs). Decizia de conformitate rămâne a evaluatorului autorizat / ANEVAR.

Legendă status cod: ✅ implementat · 🟡 parțial · ❌ lipsă.
Severitate gap: **blocant** (afectează corectitudinea valorii / conformitatea de bază) · **important** (lipsă metodologică reală, dar evaluatorul poate compensa manual) · **minor** (rafinament / documentare).

---

## 1. CE CONȚIN articolele + CE-I UTIL pentru app

### 1.1 „Rata de capitalizare poate deforma valoarea de piață" (articol-cheie pentru `venit.py`)

**Conține:**
- Abordarea prin venit e percepută ca „precisă", dar precizia depinde de **estimarea venitului brut** (chirii comparabile) și de **rata de capitalizare**, care „deformează valoarea dacă se aplică incorect metoda".
- Definiția ratei de capitalizare: **relația castig/valoare**, un divizor prin care chiria netă → indicație de valoare. Factori care o influențează: risc, inflație așteptată, randamentul investițiilor alternative, randamentul istoric al proprietăților similare, cerere/ofertă de capital, nivelul de impozitare.
- **Sursa principală a ratei = tranzacții vânzare-închiriere** (sale-leaseback). Exemplu numeric explicit: preț 1.000.000 EUR, chirie netă 80.000 EUR/an → cap rate „aparentă" 8%.
- **Avertisment critic:** vânzările-închirierile *nu sunt automat un indicator real* — prețul din acte e distorsionat de impozite/taxe, iar chiria e parțial funcție de prețul de vânzare sau de încrederea în chiriaș. Prețul trebuie supus acelorași analize ca orice comparabilă.
- **4 metode de derivare a ratei din piață:** (1) vânzare-închiriere; (2) chirii actuale vs. prețuri de vânzare; (3) prețuri de vânzare actuale vs. chirii estimate; (4) chirii actuale vs. prețuri de vânzare estimate.
- **Metoda deductivă** (când nu există tranzacții comparabile — proprietăți unice/rar vândute): se pleacă de la rata generală a profitului investițiilor imobiliare → caz specific, prin comparație cu investiții alternative cu risc similar (build-up implicit).

**Util pentru app:** acesta este manualul de bază pentru rafinarea modulului `venit.py`. Trei idei direct implementabile:
1. **Derivarea ratei din comparabile** (cap-rate extraction): o grilă mică „preț de vânzare ↔ chirie netă" care produce o rată susținută de piață, nu un input liber.
2. **Validarea / plauzibilizarea ratei** (factorii de risc → interval acceptabil; alertă la rate aberante).
3. **Disclosure-ul sursei ratei** în raport (vânzare-închiriere vs. deductivă/build-up) — cerut și de SEV 103 A20.34.

### 1.2 „Rolul prețului în tranzacțiile cu terenuri"

**Conține:** perspectiva dezvoltatorului asupra terenului. Cele 5 întrebari fundamentale ale dezvoltatorului: *Ce pot construi? Câte pot construi? La ce preț le pot vinde? Cât îmi va lua să le vând? Care sunt costurile?* — esența **metodei reziduale / a parcelării**. Valoarea terenului rezidențial se calculează **pe lot, nu pe mp**, și „depinde, în ultimă instanță, de ceea ce va produce terenul". Localizarea = singura caracteristică ce nu poate fi modificată (determină zonare, valori vecinătate, utilități). „Caracteristici și restricții" naturale (topografie, formă, inundabil, mlaștini) și induse de om (renivelare, contaminare sol/pânză freatică). Mesaj final: **prețul e ultimul lucru** — termenii și condițiile + adecvarea pentru dezvoltare contează mai mult.

**Util pentru app:** confirmă că **abordarea curentă pe teren (EUR/mp, comparație directă) e doar una dintre două metode SEV**. Pentru terenuri dezvoltabile (lot construibil), valoarea „pe lot" derivă din ce produce terenul = **metoda reziduală a terenului** (SEV 233 / GEV 630), pe care app-ul nu o are. De asemenea, lista de „caracteristici și restricții" e o **checklist de ajustări / due-diligence teren** (inundabil, contaminare, formă, topografie) care azi sunt doar ajustări libere fără ghidaj.

### 1.3 „Să înțelegem procesul de evaluare imobiliară"

**Conține:** procesul de evaluare în **6 pași**, scris pe scopul nostru exact — *prima ipotecă / refinanțare / credit cu garanție imobiliară*:
1. Culegere date proprietate-subiect (inspecție int/ext, foto, locație, teren, stil, mp, calitate/stare, camere/băi, garaje, vechime finisaje, facilități).
2. Verificare documente (impozite, titlu, **planuri cadastrale**) și **coroborare** cu inspecția.
3. Minim **3 comparabile**, vândute în ultimele **3–6 luni**, ideal **rază < 1 km**.
4. **Ajustări bănești = „valoare contributorie"** determinată de piață (nu costul investiției). Exemple cuantificate: baie 10.000 € → recuperare 4.000–6.000 €; bucătărie poate recupera 100%; subsol finisat 25–75%; mp extins 30–40 € din 75 €/mp; **supra-îmbunătățiri** = recuperare ~0.
5. Reconciliere → **plajă de prețuri ajustate** → valoare estimativă (nu o singură cifră mecanică).
6. Transmitere către creditor; dacă valoarea < suma cerută, se reanalizează / avans mai mare.
- Secțiune de **etică**: avertizare împotriva supraevaluării în favoarea băncii, „parteneriate" cu angajații băncii, evaluări din birou, onorarii mici → calitate slabă.

**Util pentru app:** este **harta procesului pe care app-ul îl asistă** — confirmă deciziile deja luate (min 3 comparabile, ajustare = valoare contributorie de piață, reconciliere ca plajă nu medie mecanică) și expune **garduri lipsă**: recența comparabilelor (3–6 luni), proximitatea (<1 km), conceptul de **supra-îmbunătățire** (cost ≫ valoare contributorie), și framing-ul „valoare estimativă / plajă". Validează narativ și disclaimer-ul anti-supraevaluare (etică) — relevant pentru poziționarea „asistare, nu AVM".

### 1.4 „Taxarea serviciilor și Managementul clădirilor"

**Conține:** anatomia **cheltuielilor de exploatare** pentru o clădire de birouri multi-chiriaș (service charge). Listă exhaustivă de cheltuieli deductibile (curățenie, electricitate, personal, încălzire/apă caldă/AC, asigurare, securitate/supraveghere, lift, întreținere generală, audit, **taxă de management**). Concepte: taxă prestabilită (cap fix de cheltuieli → riscul trece la proprietar), **fond de rulment** (sinking fund) pentru lucrări viitoare, variația an-la-an (întreținere programată vs. urgență), rolul managerului administrativ.

**Util pentru app:** este **defalcarea operațională a `cheltuieli_exploatare`** din `DateVenit` — azi un singur scalar. Pentru proprietăți generatoare de venit (comercial/industrial, profilurile `COMERCIAL_INCHIRIAT`/`INDUSTRIAL`/`SPECIAL`), distincția chirie **brută vs. netă** și ce intră în OPEX schimbă direct NOI și deci valoarea. Lista oferă o **checklist de cheltuieli** + atrage atenția asupra cheltuielilor de capital non-recurente (fond de rulment) care nu trebuie capitalizate ca OPEX recurent.

---

## 2. RELEVANȚĂ vs. SEV 2025 + CONTRADICȚII rezolvate

**Regula aplicată:** SEV 2025 are prioritate; în rest documentul mai nou câștigă. Articolele lui Nicolescu sunt **didactice, nedatate** și descriu practica clasică internațională (Appraisal/RICS) — SEV 2025 este mai nou și normativ, deci **prevalează în orice divergență**. Nu am găsit contradicții de fond: articolele sunt **subset / fundamentare** a cerințelor SEV, nu în conflict cu ele.

| Temă articol | Relevanță SEV 2025 | Verdict |
|---|---|---|
| Rata de capitalizare derivată din vânzare-închiriere + metoda deductivă | SEV 103 **A20.31–A20.34** (rata de actualizare/capitalizare cu **dovezi documentate**); GEV 630 §64 (corelare tip venit ↔ tip rată) | **Aliniat, SEV mai exigent.** Articolul dă *cum* derivi rata; SEV *cere documentarea metodei*. Ambele converg → app trebuie să facă ambele. SEV câștigă pe forma (documentare obligatorie). |
| „Prețul din acte e distorsionat de impozite/taxe" la sale-leaseback | SEV 103 A10.3 (ofertele nu pot fi singura indicație) + scepticism profesional SEV 100 §10.4 | **Aliniat.** Articolul = aplicație concretă a scepticismului profesional pe care SEV îl impune transversal. |
| Teren „pe lot, valoarea = ce produce terenul" (rezidual/parcelare) | GEV 630 (evaluarea terenului — comparație **și** metode reziduale); SEV 233 (proprietate în curs de construire, metoda reziduală a terenului) | **Aliniat.** SEV admite explicit metoda reziduală. App-ul folosește doar comparația directă → gap, nu contradicție. |
| Proces în 6 pași (inspecție → comparabile → ajustări → reconciliere → creditor) | GEV 630 §16–112 (proces pas-cu-pas) + GEV 520 (garantare) | **Aliniat, SEV mai detaliat.** Articolul e versiunea „de buzunar" a procesului GEV 630. |
| Min 3 comparabile, **3–6 luni**, **<1 km** | GEV 630 §51/§57 (min 3, oferte critic analizate); SEV 103 A10.7 (preferință recență/proximitate, dar **fără praguri numerice fixe**) | **SEV câștigă pe principiu; articolul oferă praguri practice.** SEV nu fixează „3–6 luni / 1 km" → aceste cifre rămân **euristici de alertă**, nu blocaje normative. |
| Ajustare = **valoare contributorie de piață** (≠ cost investiție); supra-îmbunătățiri | SEV 103 A10.8 + §20.5 (ajustări argumentate, cuantificate); CMBU GEV 630 §35–39 | **Aliniat.** „Valoare contributorie" = exact ce face grila aditivă din `market.py`. Supra-îmbunătățirea = caz de CMBU / depreciere funcțională (capital excedentar A30.20). |
| OPEX / service charge defalcat; chirie brută vs. netă | SEV 103 A20 (NOI = venit efectiv − cheltuieli de exploatare); GEV 630 §64 (consecvența tip flux ↔ tip rată) | **Aliniat, SEV mai exigent.** SEV cere consecvență flux↔rată (chirie netă ↔ cap rate pe NOI). Articolul dă conținutul OPEX. |
| Etica (anti-supraevaluare în favoarea băncii) | GEV 520 A3/§79/§81 (independență, conflict de interese, cerințe EBA) | **Aliniat.** Articolul susține narativ disclaimerul de independență deja prezent. |

**Concluzie secțiune 2:** zero contradicții de rezolvat. Articolele **fundamentează și operaționalizează** cerințele SEV 2025 din zona abordării prin venit și a terenului. Acolo unde articolul dă praguri numerice (3–6 luni, 1 km, procente de recuperare) pe care SEV nu le fixează, acestea se implementează ca **alerte/euristici**, nu ca garduri blocante — pentru a respecta primatul raționamentului profesional (SEV 105 §10.5).

---

## 3. GAP-URI de implementare (vs. cod verificat)

### Abordarea prin venit (`engine/venit.py`, `engine/chirie.py`)

**G1 — Rata de capitalizare e input liber, fără derivare din piață și fără validare [important]**
`DateVenit.rata_capitalizare: Decimal` (venit.py:19) acceptă orice valoare > 0 (singura gardă: `evalueaza_venit` ridică `ValueError` la rată ≤ 0, venit.py:39). Nu există:
- niciun mecanism de **extracție a ratei din tranzacții vânzare-închiriere** (cele 4 metode din articol);
- nicio **validare de plauzibilitate** (ex. rată în afara unui interval rezonabil 2%–15% → alertă);
- nicio **documentare a sursei/metodei** ratei (vânzare-închiriere vs. deductivă/build-up) — cerută de SEV 103 A20.34.
Acesta e exact riscul din titlul articolului: „rata poate deforma valoarea de piață". O eroare de input pe rată (ex. 0,8 în loc de 0,08) trece nedetectată și deformează valoarea cu un ordin de mărime.
*Recomandare:* (a) helper `rata_din_vanzare_inchiriere(pret, chirie_neta)` + grilă mică de derivare; (b) gardă de plauzibilitate (alertă în afara unui interval configurabil, analog M5); (c) câmp obligatoriu „metodă + sursă rată" în `DateVenit`, propagat în raport.

**G2 — Cheltuielile de exploatare = scalar unic, fără defalcare OPEX și fără distincția chirie brută/netă [important]**
`DateVenit.cheltuieli_exploatare: Decimal` (venit.py:18) e o singură sumă. Articolul „service charge" arată că OPEX-ul are 15+ poziții și că **fondul de rulment (capital) nu trebuie capitalizat ca OPEX recurent**. Nu există nicio structură care să distingă: chirie brută vs. netă, OPEX recurent vs. capital, sau procentul tipic de cheltuieli. La proprietăți cu venit (`COMERCIAL_INCHIRIAT`, `INDUSTRIAL`, `SPECIAL`), un OPEX greșit clasificat → NOI greșit → valoare greșită.
*Recomandare:* model opțional `CheltuieliExploatare` cu poziții (checklist din articol) care însumează în `cheltuieli_exploatare`, + flag „chirie netă/brută" și avertisment de consecvență flux↔rată (GEV 630 §64). Minim: o notă/validare „confirmați că rata de cap se aplică pe NOI net, nu pe venit brut".

**G3 — Gradul de neocupare neexplicat și fără pragul de suficiență a datelor [minor]**
`grad_neocupare` (venit.py:17) e un input liber [0,1). Nu există ghidaj/sursă (piață locală — cum cere articolul „reflectă atitudinea pieței specifice locale"). Minor pentru garantarea casă+teren (unde venitul e rar primara), important la profilurile de venit.
*Recomandare:* notă de documentare a sursei gradului de neocupare; opțional alertă la valori extreme.

**G4 — Valoarea terminală DCF e sumă manuală; lipsesc metodele standard [important]** *(confirmă B-abordari §3)*
`evalueaza_dcf` (venit.py:58–74) acceptă o `valoare_reziduala` manuală. Lipsesc **Gordon** (NOI×(1+g)/(r−g)) și **exit-cap**, cu validarea r>g. Articolul de cap-rate explică exact relația castig/valoare care stă la baza ambelor.
*Recomandare:* implementează Gordon + exit-cap cu validare r>g; reutilizează logica de cap-rate din G1.

### Prețul terenurilor (`engine/land.py`)

**G5 — Lipsește metoda reziduală / a parcelării terenului [important]**
`land.py` implementează **doar comparația directă EUR/mp**. Articolul „rolul prețului" descrie metoda reziduală (valoarea „pe lot" = ce produce terenul: preț produs finit − costuri dezvoltare − profit dezvoltator), recunoscută de SEV 233 / GEV 630 pentru terenuri dezvoltabile. Pentru un teren construibil mare, comparația EUR/mp poate denatura (articolul: „se calculează pe lot, nu pe mp"; „o parte se pierde").
*Recomandare:* modul opțional `teren_rezidual` (nr. loturi × preț lot − costuri − profit); util și pentru CMBU. Bucket B (evaluatorul decide când se aplică), dar motorul lipsește complet.

**G6 — Lipsește checklist-ul „caracteristici și restricții" teren [minor]**
Ajustările de teren sunt libere. Articolul oferă o taxonomie utilă (inundabil, contaminare sol/pânză freatică, topografie, formă, mlaștini, utilități, zonare) care ar trebui să **declanșeze ajustări / due-diligence** și apare deja ca cerință ESG (riscuri fizice) în SEV 104 Anexă / GEV 520 §86–88.
*Recomandare:* checklist de caracteristici teren (inundabilitate, contaminare, formă, topografie) → sugerează ajustări + alimentează blocul ESG (gol normativ 2025 deja semnalat).

### Procesul de evaluare (transversal — `engine/validation.py`, `assembler.py`)

**G7 — Fără gardă pe recența și proximitatea comparabilelor [important]**
`valideaza_comparabile` (validation.py:50–84) verifică număr, outlier, ajustare brută, dar **nu** recența (articol: 3–6 luni) și **nu** proximitatea (<1 km). Câmpurile de dată/sursă există pe model dar nu sunt validate (vezi B-abordari §5). Pentru garantare, o comparabilă veche de 2 ani e un risc real de supraevaluare.
*Recomandare:* alertă pe vechimea comparabilei (prag configurabil, default ~6 luni) și, dacă există coordonate/zonă, pe distanță. Euristică (alertă), nu blocaj — SEV nu fixează pragul.

**G8 — Lipsește conceptul de „supra-îmbunătățire" (cost ≫ valoare contributorie) [minor]**
Articolul (proces, pas 4) și CMBU (GEV 630 §35–39) descriu cazul în care o îmbunătățire costisitoare recuperează ~0 (capital excedentar — depreciere funcțională A30.20). Motorul de cost (`cost.py`) tratează deprecierea funcțională ca scalar unic, fără sub-categoria „capital excedentar". O ajustare de piață care contrazice puternic costul nu e semnalată ca posibilă supra-îmbunătățire.
*Recomandare:* alertă când valoarea contributorie de piață a unei caracteristici e mult sub costul ei (semnal de supra-îmbunătățire) — leagă de garda de divergență piață↔cost deja recomandată în B-abordari §1.

**G9 — Reconcilierea ca „plajă de valori", nu doar o cifră [minor]** *(rafinament de raport)*
Articolul subliniază (pas 5) că rezultatul e **o plajă de prețuri ajustate** și o **valoare estimativă**, nu o cifră mecanică. `reconcile_profil` produce o singură `valoare_finala`. Aliniat cu SEV 103 §10.7 (fără medie mecanică). Gap de **framing/raport**: expunerea plajei (min–max al indicațiilor) ar întări mesajul „asistare, nu AVM".
*Recomandare:* afișează în raport intervalul indicațiilor de abordare/comparabile alături de valoarea reconciliată.

---

## Top 3 acțiuni recomandate (prioritate)

1. **G1 — rata de capitalizare: derivare din piață + validare + documentare sursă** (important). Este nucleul articolului-cheie și un risc direct de deformare a valorii. Atinge și SEV 103 A20.34 (dovezi documentate).
2. **G5 — metoda reziduală a terenului** (important). Singurul motor de teren e comparația EUR/mp; pentru terenuri dezvoltabile lipsește metoda recunoscută de SEV 233 / GEV 630.
3. **G7 — garda de recență/proximitate a comparabilelor** (important). Praguri practice (3–6 luni, <1 km) ca alerte; risc concret de supraevaluare la garantare, cu efort mic (câmpurile există deja pe model).

---

### Rezumat (≤180 cuvinte)

Cele 4 articole (Adrian Nicolescu, didactice/nedatate) operaționalizează zona **venit + teren + proces** a SEV 2025 — fără contradicții de fond; SEV rămâne prioritar și mai exigent (documentare obligatorie a ratei, consecvență flux↔rată). Articolul-cheie („rata de capitalizare poate deforma valoarea") corespunde direct `engine/venit.py`: app-ul are capitalizare directă + DCF de bază corecte, dar **rata de capitalizare e un input liber** — fără derivare din vânzare-închiriere (cele 4 metode din articol), fără validare de plauzibilitate, fără documentarea sursei (G1, A20.34). **Cheltuielile de exploatare** sunt un scalar unic, fără defalcarea OPEX din articolul „service charge" și fără distincția chirie brută/netă (G2). **Terenul** are doar comparație EUR/mp; lipsește **metoda reziduală/parcelare** pe care articolul o descrie și pe care SEV 233/GEV 630 o admit (G5). Procesul în 6 pași confirmă deciziile existente (min 3 comparabile, valoare contributorie, reconciliere ca plajă), dar expune garduri lipsă: **recență/proximitate comparabile** (G7), **supra-îmbunătățiri** (G8), **valoare terminală DCF** (G4). Nicio eroare de aritmetică; golurile sunt de completitudine metodologică și de garduri de plauzibilitate.
