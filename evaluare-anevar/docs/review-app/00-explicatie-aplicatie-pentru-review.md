# Evaluare ANEVAR — explicație exhaustivă pentru review

> Document-umbrelă pentru cei care **revizuiesc** aplicația (evaluator senior, jurist, eventual IT/risc de
> bancă). Explică *ce este*, *cum funcționează în detaliu* și *ce mai e de făcut*. Faptele tehnice sunt extrase
> din cod (nu din presupuneri) și detaliate în 4 anexe. Actualizat: 2026-06-07.

## 0. Cum citești pachetul (harta)
- **Acest document** = explicația coerentă, cap-coadă.
- **Anexe tehnice factuale** (cu referințe la `fișier:linie`):
  - [`_metodologie.md`](_metodologie.md) — cele 3 abordări, formule, grile, reconciliere, profile, garduri.
  - [`_raport-conformitate.md`](_raport-conformitate.md) — structura raportului `.docx` + starea de conformitate SEV 2025.
  - [`_arhitectura.md`](_arhitectura.md) — tehnologie, module, rulare, securitate.
  - [`_aml-ui.md`](_aml-ui.md) — modulul AML (Legea 129), GDPR/anonimizare, fluxul de lucru UI.
- **Context de lansare:** [`../livrabile-finale.md`](../livrabile-finale.md) (ce se livrează cui), [`../BLOCAT-pe-Adi.md`](../BLOCAT-pe-Adi.md) (decizii), [`../conformitate/00-SINTEZA-conformitate.md`](../conformitate/00-SINTEZA-conformitate.md), [`../audit-final/00-sinteza-audit-final.md`](../audit-final/00-sinteza-audit-final.md).

---

## 1. Ce este aplicația (rezumat executiv)
**Un asistent software de evaluare imobiliară pentru evaluatorul autorizat ANEVAR.** Automatizează partea
repetitivă — calcule, căutarea de comparabile, redactarea raportului — dar **evaluatorul decide, verifică și
își asumă** valoarea (om în buclă).

**Trei principii care contează la review:**
1. **Avertizează, nu decide.** Validările produc *alerte* către evaluator; motorul nu refuză și nu blochează
   întocmirea (excepție: erori de date care fac calculul invalid — suprafețe ≤ 0).
2. **Numerele sunt deterministe; AI scrie doar proza.** Toate valorile (CIN, grile, reconciliere, alocare,
   lichidare) sunt calculate de motor pe `Decimal`, reproductibile. LLM-ul redactează **doar** cele 7 capitole
   narative, pe baza cifrelor, **anonimizat**, cu interdicție explicită de a inventa cifre/surse.
3. **Rulează local, offline.** Un singur `.exe` (~50 MB) care pornește un server pe `127.0.0.1` și deschide
   browserul. Datele rămân pe calculatorul evaluatorului.

**Acoperire (tip × scop):** casă+teren · apartament · comercial · industrial · agricol × garantare credit ·
raportare financiară (IFRS) · asigurare · impozitare · litigiu. Profilul ales determină *framing-ul* raportului
(tip valoare + ghid GEV declarat), nu formula numerică.

**Stadiu:** produsul tehnic e solid și testat; ce **oprește lansarea nu e cod**, ci validări umane (evaluator,
jurist AML, jurist GDPR) + câteva decizii (semnătură digitală, screening AML live, preț). Vezi §8.

---

## 2. Arhitectură & cum rulează  → detalii în [`_arhitectura.md`](_arhitectura.md)
- **Stack:** FastAPI + uvicorn + Jinja2 + Pydantic; `python-docx` (raport), `requests`/`BeautifulSoup`
  (descoperire), PyMuPDF/OCR (ingestie PDF), `anthropic`/Perplexity (narativ, opțional). Python 3.12, PyInstaller
  *onefile*. Aritmetică pe `Decimal` (nu `float`).
- **Rulare:** bind **doar** pe `127.0.0.1` (loopback), deschide browserul după ce portul e gata. Offline complet
  fără cheie AI (text-șablon). Datele stau lângă `.exe` (`OUTPUT_DIR`), cu fallback pe `%LOCALAPPDATA%` dacă e
  într-un folder de sincronizare cloud.
- **Model de date „folder = adevăr":** fiecare dosar = un folder cu `dosar.json` + versiuni `raport-*.docx`
  (retenție 10). Pozițio­nează produsul pentru versionare/predare la peer-review/istoric. (Există și o cale veche
  pe SQLite, în retragere.)
- **Module (7 routere):** cont/dosar (UI nou), evaluare (UI vechi), grile, descoperire, piață/ingestie, AML, pagini.
- **Date externe:** descoperire pe portaluri (caută→citește→punctează→explică); **extensie de browser** prin care
  evaluatorul trimite MANUAL o pagină de anunț (fără scraping automat); import `.docx`; ingestie PDF (CF/releveu/CPE).
- **Securitate (întărită recent + audit):** anti-SSRF la fetch, gardă `Host` anti DNS-rebinding, erori de input →
  422 (nu 500), limită 25 MB la import, igienă PII pe `.docx` temporar, anonimizare CNP, dosar corupt → 404.
  Pozitive: SQL parametrizat, bind loopback, fără `eval/exec`, path-traversal mitigat.

---

## 3. Metodologia de calcul — **partea cea mai importantă de revizuit**  → [`_metodologie.md`](_metodologie.md)

### 3.1 Cele 3 abordări (formule exacte)
- **COST (CIN):** segregare pe elemente (catalog IROVAL). `CIB = Σ(cantitate × cost_unitar)` (fără TVA, fără
  profit dezvoltator). Depreciere fizică prin **interpolare liniară** în tabelul vârstă→fracție (clamp la capete).
  **`CIN = CIB × (1 − D_fizică) × (1 − D_funcțională) × (1 − D_externă)`** (multiplicativ). `valoare = CIN + teren`.
- **COMPARAȚIE — grilă în 2 etape:**
  - Etapa **„tranzacție"** (ofertă→tranzacție, drept, finanțare, condiții) → aplicată **secvențial/compus** → „preț de bază".
  - Etapa **„proprietate"** (caracteristici fizice/juridice) → aplicată **aditiv** pe prețul de bază.
  - **Selecție:** comparabilul cu **ajustarea brută minimă pe etapa de proprietate** (tranzacția nu se contorizează).
  - **Teren:** `valoare = preț/mp corectat al comparabilei alese × suprafața subiectului`.
  - **Casă:** pe **preț TOTAL** (model GBF/ANEVAR); diferența de mărime = **ajustare valorică de arie utilă**
    (preț unitar × Δmp). Valoarea = prețul total corectat al comparabilei alese (NU preț unitar × suprafață).
- **VENIT:** capitalizare directă `valoare = NOI / rată` (NOI = VBP − neocupare − cheltuieli; VBP = chirie/mp ales
  × suprafață × 12) **sau** DCF `valoare = Σ flux_t/(1+r)^t + rezidual/(1+r)^n`.

### 3.2 Reconciliere & alocare
- `reconcile_profil`: dacă există ponderi pe ≥2 abordări → **medie ponderată normalizată**; altfel selectează abordarea
  primară (derivată din `metoda`: cost/piata/venit/ponderata/dcf). **Alocare: `construcții = proprietate − teren`.**

### 3.3 Profile (tip × scop → ghid GEV)
10 constante de profil; orchestrarea cablează 5 după tip (casă/apartament/industrial/agricol/special) + 4 după scop
(raportare financiară/asigurare/impozitare/litigii). Profilul impune tip valoare + ghid GEV + secțiunile de raport.

### 3.4 Garduri / alerte prudențiale (toate produc *alerte*, nu blocaje)
| Prag | Valoare | Unde |
|---|---|---|
| Ajustare brută | **25%** (`LIMITA_AJUSTARE_BRUTA`) | brută pe etapa proprietate (casă) → alertă |
| Outlier | **50%** față de mediană | preț unitar brut al comparabilei → alertă |
| Minim comparabile | **3** | sub 3 → blochează calculul de piață |
| Au ≤ Acd, suprafețe > 0 | — | erori de date (blochează) |
| Consistență cost↔piață | **20%** | în raport: dacă deprecierea implicită > 20% → text de avertizare GEV 520 |

### 3.5 ⚠️ Puncte care necesită confirmarea evaluatorului (semnalate de analiză)
Acestea sunt **decizii de metodologie** (Bucket B) — nu le-am atins; le supun reviewului:
1. **Selecția pe „ajustare brută minimă (proprietate)"** ca regulă unică — risc de alunecare spre AVM; SEV 105 cere
   raționament, nu doar minim mecanic. **Corect?**
2. **Ajustarea de suprafață liniară** (Δmp × preț) — economic, mp-ul marginal e degresiv la diferențe mari. **OK?**
3. **Valoarea de lichidare = factor fix 0,85** (orientativ, 0,80–0,90 de stabilit de evaluator) — lipsesc cele 2
   premise (vânzare ordonată/forțată) + declararea premisei (def. A60 schimbată în 2025). **De calibrat.**
4. **Nu există prag de 15% în cod** și **ajustarea netă nu e gardată** (e calculată/afișată, dar fără alertă).
   Engine folosește 25% (brut) + 20% (consistență). **Dorești o gardă pe ajustarea netă?**
5. **Declarația de conformitate e necondiționată** — raportul afirmă „conform SEV" chiar dacă validările cad.
   Fixul tehnic (gardă) e ușor, dar **formularea o confirmă evaluatorul**.
6. **Posibilă inversiune de ghid GEV:** `IMPOZITARE→GEV_630` vs `RAPORTARE_FINANCIARA→GEV_500` (GEV 500 e ghidul de
   impozitare). Asertat în teste ca framing intenționat → **de confirmat că nu e inversat.**
7. La garantare pe industrial/agricol/special raportul citează GEV 630, nu GEV 520 (și invers la casă/apartament) —
   recomandare: să **citeze ambele** (utilizare desemnată + metodă).
8. `COMERCIAL_INCHIRIAT` e definit dar **necablat** în orchestrare (comercialul închiriat cade pe alt profil).

---

## 4. Fluxul de lucru (cum folosește evaluatorul)  → [`_aml-ui.md §3-4`](_aml-ui.md)
**UI nou „output-first":** `cont` (o singură dată: nume + legitimație + formatul numelui de dosar) → **ÎNCEPE**
(dosar nou cu identitate / încarcă salvat / importă `.docx`) → **workspace** per dosar, cu **salvare automată în
folder** (debounce 700 ms). Patru tab-uri:
- **Raport** (5 sub-tab-uri): *Proprietate* (identitate + pre-completare din PDF/CF; câmpuri fizice dinamice pe tip;
  utilități/acces/urbanism; elemente de cost) · *Comparabile* (**descoperire inline** pe portaluri + import URL +
  coadă din extensie; **3 grile de ajustări** pe 2 etape, cu alertă > 25%) · *Calcul* (metodă, monedă, curs BNR auto,
  alerte de validare) · *Anexe* (fotografii + scanuri → în `.docx`) · *Generează*.
- **AML**, **GDPR**, **Audit** (urmă de audit hash-înlănțuită + validare încrucișată).

**Checkpoint de asumare la «Generează» (om-în-buclă):** butonul e blocat până când evaluatorul bifează că *a
verificat și își asumă profesional* valoarea (semnătura îi aparține; aplicația doar asistă). Convergență a auditului
juridic și a consiliului LLM — răspunderea trăiește în UI, cu urmă în dosar. Fiecare generare = **versiune
persistentă** în folder; copia temporară (PII) se șterge după trimitere.

> **Notă de stare:** UI-ul nou a fost **recuperat la paritate** cu wizardul vechi în această sesiune (anexe
> dez-blocate, AML/GDPR/Audit reconstruite *in-place*, descoperire re-integrată, câmpuri dinamice pe tip, curs EUR).
> Documentul istoric [`../audit-ui-nou/`](../audit-ui-nou/) descrie *starea-problemă de dinainte* — nu cea curentă.
> Wizardul vechi (5 pași) încă coexistă; o re-verificare cap-coadă a fiecărui endpoint din UI-ul nou rămâne în QA.

---

## 5. Raportul generat + conformitate SEV 2025  → [`_raport-conformitate.md`](_raport-conformitate.md)
**Structura `.docx`** (shell GBF + 7 capitole SEV 106): copertă → scrisoare de transmitere → **declarație de
conformitate & certificare** → **termeni de referință** (SEV 101) → **cap. 1-7** (sinteză; ipoteze; piață; descriere
juridică+fizică; CMBU; **aplicarea metodelor + grilele de calcul**; reconciliere) → **alocarea valorii** (+ verificare
consistență GEV 520) → **riscul garanției GEV 520** (doar la profil de garantare; + valoarea de lichidare + checklist
16 puncte) → **anexe** (comparabile + foto + documente) → casetă de semnătură.

**Split AI/determinist:** AI scrie doar cele 7 capitole narative (anonimizat, `temperature=0.2`, fără cifre/surse
inventate); **toate numerele sunt deterministe**. Modul `adnotari` (demo) marchează proveniența fiecărei secțiuni
([CALCULAT]/[AI]/[EXTRAS]/[ȘABLON]/[EXEMPLU]) — notele **nu** apar în raportul real. **Niciun audit nu a găsit erori
de aritmetică.**

**Câmpuri de conformitate** (cu sursă SEV/GEV): tip valoare + sursă (SEV 102), drept evaluat + sarcini CF (SEV 230),
act, inspecție (amploare/însoțitor/observații — GEV 630), regim teren, utilități, regim urbanistic POT/CUT, acces.
*Tipar:* câmpurile **critice la garantare** (sarcini CF, inspecție) **avertizează vizibil** când lipsesc; cele
descriptive opționale (act, utilități, POT/CUT, acces) sunt **omise tăcut** — limită cunoscută.

**Stare de conformitate:** ✅ rezolvat (Bucket A): tip valoare+sursă, descriere completă, inspecție, anexe (backend).
🟡 rămâne **Bucket B** (evaluator): punctele din §3.5. 🔵 **Bucket C** (jurist): SEV 400 (verificarea evaluării, absent),
ESG real, AML/GDPR.

---

## 6. AML + GDPR + juridic  → [`_aml-ui.md §1-2`](_aml-ui.md)
**AML (Legea 129/2019 + Norme ONPCSB + HCD 58/2023 ANEVAR):** KYC (PF/PJ, beneficiar real **> 25%**, PEP 8 categorii);
**evaluare de risc** pe 4 factori ponderați → praguri (≤1,4 redus / ≥2,2 sporit) + 5 reguli care forțează „sporit"
(art. 17); **10 indicatori** de suspiciune → orice bifă propune **RTS**; praguri legale în cod (RTN **10.000 €**,
ocazional/anti-fragmentare **15.000 €**, post-PEP 12 luni, retenție 5 ani); **6 documente `.docx`**; RTS/RTN **stocate
separat** de dosar (tipping-off, art. 38). **Screening PEP/sancțiuni e INJECTABIL, NU live** — `liste.json` e
placeholder explicit; UI avertizează „aplicația NU verifică automat" + linkuri către surse oficiale. **Toate
documentele AML poartă antet DRAFT „neverificat juridic"** — citările de articole (inclusiv art. 43/44/49) sunt
**pending validare jurist**.

**GDPR / anonimizare:** lanț *date reale → mascare ([CLIENT]/[ADRESA]/[CADASTRAL]/[CF]/[EVALUATOR]) → plasă regex
(CNP/telefon/email) → la AI pleacă DOAR text anonimizat → demascare locală*. **Datele AML/KYC nu ajung NICIODATĂ la
AI.** Operatorul de date = evaluatorul (nu aplicația); AI = sub-procesator pe text anonimizat. Modele GDPR + 5 drafturi
legale (T&C, confidențialitate, EULA, **DPA art. 28**, disclaimer) — toate **DRAFT, necesită avocat RO**.

---

## 7. Calitate & verificare
- **Teste:** ~513 teste unitare/integrare (prin FastAPI TestClient) + smoke e2e Playwright cap-coadă; **coverage ~94%**
  (prag impus 90). Aritmetica de evaluare e acoperită; gardurile prudențiale au teste.
- **Audituri rulate:** conformitate SEV 2025 pe întreaga matrice tip×scop; 4 audituri (securitate, buguri/eșecuri
  silențioase, datorie tehnică, acoperire) + un panel LLM Council pe constatări. Constatările Bucket-A au fost reparate;
  restul e escaladat (Bucket B/C/decizii).

---

## 8. CE MAI E DE FĂCUT (consolidat)
> Detaliu + owner în [`../livrabile-finale.md`](../livrabile-finale.md) și [`../BLOCAT-pe-Adi.md`](../BLOCAT-pe-Adi.md).

**A. Validări externe (drumul critic — Poarta 0, în paralel):**
- **Evaluator senior** — confirmă metodologia (punctele §3.5). *Validează premisa produsului.*
- **Jurist AML** — auditează modulul + citările (art.). **Blocant absolut.**
- **Jurist GDPR** — confirmă DPA (art. 28), transferul LLM extra-UE/SCC, AI Act.
- **Bănci (Risc/IT)** — validează **forma** raportului; ideal pilot pe 20-30 dosare *după* finalizarea metodologiei.
- **Asigurătorul de răspundere ANEVAR** — aviz că rapoartele asistate AI sunt acoperite (altfel risc comercial).

**B. Metodologie de calibrat (evaluator → o implementez eu):** selecție comparabilă, ajustare degresivă de suprafață,
factor de lichidare + premise, gardă pe ajustarea netă, declarație de conformitate condiționată, framing/inversiune ghid GEV.

**C. Jurist:** finalizare texte AML/GDPR + citări; decizie screening **live** (OpenSanctions) vs. dezactivat; SEV 400.

**D. Decizii / cumpărări (Adi):** certificat **code-signing** (SmartScreen), lock de identitate la finalizare,
criptare-la-repaus (BitLocker/disclaimer), **preț**, ordinea comercială (validare înainte de gateway).

**E. De creat (lipsesc, recomandate):** **manual de utilizare** · **SLA suport** · **plan de incident/breach** ·
**cerere de aviz** către asigurător · **etichetarea „AI (proză) vs determinist (toate numerele)"** în raport (mitigare
percepție bănci) · conversia pachetelor pentru jurist/bancă în **PDF**.

---

## 9. Limitări declarate (onestitate — le spunem deschis)
- **Baza de „piață" nu e o bază de date de tranzacții reale** — analiza de piață e descriptivă (AI), comparabilele le
  introduce/validează evaluatorul.
- **Surse oficiale** (catalog IROVAL pentru costuri, BIG, ANCPI) — necesită acces/membru ANEVAR; nu sunt integrate live.
- **Liste AML (sancțiuni/PEP)** — injectabile, de reîmprospătat manual din surse oficiale; fără screening automat.
- **Profitul dezvoltatorului + costurile indirecte** nu sunt incluse în cost; deprecierea fizică e liniară pe vârstă.
- **`.exe` nesemnat digital** → Windows SmartScreen avertizează la prima rulare.
- **Textele juridice/AML sunt DRAFT** — nu se folosesc în producție fără jurist.

---

## 10. Întrebări țintite pentru reviewer (checklist)
**Pentru evaluator (metodologie):** punctele 1-8 din §3.5 — în special selecția comparabilei, ajustarea de suprafață,
factorul de lichidare, gardă pe ajustarea netă, inversiunea de ghid GEV. Plus: raportul `.docx` (structură, grile,
declarații, GEV 520, anexe) — **complet și acceptabil pentru bănci?** Ce ar duce la respingere?

**Pentru jurist:** modulul AML (KYC/risc/indicatori/RTS-RTN/tipping-off, citările de articole) + GDPR (anonimizare,
DPA, transfer LLM, AI Act) + drafturile legale — corecte și suficiente?

**Pentru IT/risc de bancă (dacă e cazul):** rulare locală/offline, modelul de date pe foldere + urma de audit,
întărirea de securitate, faptul că **toate numerele sunt deterministe** (LLM scrie doar proza).

> **Regula de aur:** aplicația **avertizează, nu decide**; metodologia și pragurile legale **nu se modifică** fără
> semnătura unui evaluator senior / jurist.
