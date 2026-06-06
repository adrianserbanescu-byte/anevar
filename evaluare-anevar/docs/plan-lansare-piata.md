# Plan de lansare pe piață + meta-analiză a consiliului LLM

> **Autor:** Claude (analiză independentă, agentică). **Data:** 2026-06-06.
> **Scop:** un singur document pe care Adi îl poate aproba cu „da". Auditez opiniile
> consiliului LLM, adaug opinia mea critică, agreg totul într-o secvență de lansare pe
> **piața liberă** (fără partea de marketing — nu e scopul).
> **Surse citite:** `review-llm-council-RESULT.md` (1056 linii), `review-llm-council.md`,
> `plan-post-council.md`, `plan-maine-2026-06-06.md`, `features-majore-pending.md`,
> `specs/4-comercializare*.md`, `backlog-ux.md`, `strategie-testare.md`, plus materialele
> de execuție deja pregătite (`audit-aml-pentru-jurist.md`, `protocol-peer-review-evaluator.md`,
> `pachet-validare-banci.md`, `gdpr/*-MODEL.md`, `distributie-evaluator.md`,
> `spec-extensie-browser.md`) și **verificare în cod** a gardurilor de protecție.

---

## Nota metodologică (cum am auditat)

Nu m-am bazat doar pe ce *spun* documentele de plan că s-a făcut. Am verificat **în cod**
fiecare gard de protecție pretins în `plan-post-council.md §A`. Rezultatul: toate cele 8
sunt reale și cablate, nu schițe. Asta contează, fiindcă diferența dintre „am scris în plan
că alertăm la ajustare >25%" și „`LIMITA_AJUSTARE_BRUTA = Decimal('0.25')` produce un `Issue`
de nivel «alerteaza»" e diferența dintre un produs și un PowerPoint. Citez fișierul și linia
unde e relevant.

**O constatare care schimbă tonul întregului audit:** consiliul a evaluat un dosar care
descria un `.exe` de **176 MB nesemnat**. Realitatea de azi (`dist/evaluare-anevar.exe`) e
**50 MB** (confirmat pe disc, build 2026-06-06). Deci o parte din critica de distribuție a
consiliului (mărime „coșmar pentru antivirus") e **deja parțial caducă** — problema rămasă e
strict **semnătura digitală**, nu mărimea. Voi marca peste tot unde consiliul a citit o stare
mai veche decât cea reală.

---

# 1. Audit al consiliului LLM (temă cu temă)

Pentru fiecare temă majoră: **(a)** ce a spus consiliul, **(b)** ce e deja rezolvat,
**(c)** ce rămâne, **(d)** opinia mea critică — inclusiv unde consiliul a greșit sau a exagerat.

## 1.1. Grila casă/apartament: preț total vs. EUR/mp

**(a) Ce a spus consiliul.** Cea mai dură critică a panelului, etichetată „Red Flag Critic"
de chairman (Gemini) și „probabil cel mai mare red flag din dosar" (Gemini, membru). Teza:
în România, rezidențialul pentru garantare GEV 520 se evaluează **aproape exclusiv pe EUR/mp**;
lucrul pe preț total cu ajustarea de suprafață ca Δmp×preț-unitar „distorsionează procentele
de ajustare pe care băncile le monitorizează strict" și forțează respingerea automată.

**(b) Ce e rezolvat.** Parțial, la nivel de **garduri**: motorul afișează deja ajustarea brută
și are praguri prudențiale (`validation.py:16`, `LIMITA_AJUSTARE_BRUTA=0.25`). Triajul a
încadrat corect conversia la €/mp ca **strat de prezentare** (`plan-post-council.md B1`) și a
trimis-o la peer-review (`protocol-peer-review-evaluator.md`, întrebarea 2).

**(c) Ce rămâne.** Decizia metodologică propriu-zisă: grila casă rămâne pe preț total în motor,
dar **prezentarea în raport** trebuie să arate și prețurile unitare corectate (€/mp). Nimeni nu
a implementat încă stratul de prezentare, fiindcă (corect) depinde de confirmarea evaluatorului.

**(d) Opinia mea critică — aici consiliul a fost intern incoerent, iar chairman-ul a ales
versiunea cea mai alarmistă.** Doi membri (GPT-5.1 și Sonnet 4.5) au spus explicit că abordarea
pe preț total e **matematic echivalentă** cu €/mp dacă ajustarea de suprafață e bine fundamentată,
și au notat-o ca „acceptabil" / „defensabilitate 70%", NU ca respingere automată. Grok a spus
„acceptabilă în practică". Doar Gemini (membru) a urcat-o la „red flag critic", iar chairman-ul
(tot Gemini) a **promovat versiunea lui Gemini** în sinteză, ridicând tonul peste media panelului.
Asta e un artefact de chairman, nu un consens. **Concluzia mea:** problema e **reală dar de formă,
nu de fond**. Riscul concret nu e că matematica e greșită (nu e), ci că un verificator de bancă
care vede preț total fără coloana €/mp **cere clarificări** și asta consumă timp și încredere.
Soluția e ieftină (un strat de afișare), nu o rescriere a motorului. Recomand: **se face**, dar
ca prezentare, după confirmarea evaluatorului — exact cum a triat deja `plan-post-council.md`.
Un punct pe care **tot panelul l-a ratat:** Sonnet a ridicat singura obiecție serioasă de *fond*
— ajustarea de suprafață **liniară** (Δmp×preț) e greșită economic la diferențe mari, fiindcă mp-ul
marginal e degresiv. Asta e mai important decât preț-total-vs-€/mp și a fost pus corect ca B3.

## 1.2. Selecția comparabilei la grila de teren (ajustare proprietate vs. brută totală)

**(a) Ce a spus consiliul.** **Consens real, toți 4 membrii** — singurul punct metodologic pe
care panelul chiar e unanim. Selecția pe „ajustarea brută minimă **doar pe etapa de proprietate**"
ignoră ajustările mari din etapa de tranzacție (ofertă→tranzacție, condiții de piață). Riscul:
algoritmul alege o ofertă veche, mult ajustată la tranzacție, doar fiindcă fizic seamănă.
Recomandarea unanimă: criteriul principal = **ajustarea brută TOTALĂ** (etapa 1 + 2).

**(b) Ce e rezolvat.** Gardul e pus: ajustarea brută totală **se afișează deja lângă selecție**
(`plan-post-council.md A2`), iar motorul alertează peste praguri. Întrebarea de selecție-principală
e în peer-review (`protocol`, întrebarea 1).

**(c) Ce rămâne.** O singură decizie binară a evaluatorului: ajustarea brută totală devine
**criteriul principal** de selecție automată, sau rămâne afișată ca metrică secundară lângă
criteriul actual? (`plan-post-council.md B2`.)

**(d) Opinia mea.** Aici consiliul are **dreptate fără rezerve** și e cel mai solid punct al lor.
Recomandarea e ieftină, defensabilă și aliniată cu uzanța de verificare bancară. Aș merge mai
departe decât panelul: nu doar afișați brută-totală, ci **schimbați criteriul implicit de selecție**
pe brută-totală, fiindcă „afișăm metrica corectă dar selectăm pe cea greșită" e fix genul de
inconsistență pe care un verificator o prinde și o penalizează (a spus-o și GPT-5.1: „de ce ați
considerat acest comparabil cel mai relevant, deși are ajustare brută totală mai mare?").
Compromisul: schimbarea selecției poate modifica valori pe dosare existente → de aceea **trebuie**
confirmarea evaluatorului senior înainte, nu e un fix auto-safe.

## 1.3. Consistența cost ↔ piață (testul Breaza, depreciere implicită de 29%)

**(a) Ce a spus consiliul.** Chairman + Sonnet au rulat **cifrele reale din Breaza**:
CIN ≈ 151.000 €, valoarea alocată construcției prin extracție ≈ 107.600 € ⇒ **depreciere
implicită de ~29%** neexplicată. Dacă acea casă e relativ nouă, o depreciere de 29% sub costul
de înlocuire „blochează raportul la bancă". Cerere: trigger automat care obligă justificarea când
`|construcții − CIN| / CIN` depășește ±15-20%.

**(b) Ce e rezolvat.** **Exact asta e implementat.** `validation.py:76 valideaza_depreciere()`
cere justificare scrisă când deprecierea funcțională/externă e nenulă și `justificare_depreciere`
e gol → produce `Issue`. Triajul îl listează ca `A3` (depreciere implicită >20% → notă obligatorie).
Alocarea `construcții = proprietate − teren` e în `reconciliation.py:61 aloca_constructii()`.

**(c) Ce rămâne.** De confirmat la peer-review că pragul (20%) și mesajul sunt corecte
(`protocol`, întrebarea 4). Eventual: factorul de lichidare derivat (vezi 1.4).

**(d) Opinia mea.** Consiliul a pus **degetul pe cea mai bună observație din tot review-ul** —
și e cu atât mai valoroasă cu cât au derivat-o din **datele reale ale lui Adi**, nu din teorie.
Faptul că Adi a și implementat gardul (alertă de consistență) e răspunsul corect: aplicația
**nu ascunde** discrepanța, o **scoate la suprafață** și cere justificare. Asta e exact filozofia
„om în buclă" aplicată bine. Singura mea rezervă: deprecierea de 29% în Breaza s-ar putea să fie
**reală** (casă la țară, piață subțire, lichiditate redusă — toate trag valoarea de piață sub cost),
nu o eroare. Deci alerta e potrivită (forțează explicația), dar nu trebuie transformată într-un
**blocaj** care împiedică finalizarea — și aici codul face bine: nivel „alerteaza", nu „blocheaza".

## 1.4. Ce lipsește pentru GEV 520 (lichidare, certificare, risc garanție, oferte vs. tranzacții)

**(a) Ce a spus consiliul.** Patru lipsuri concrete: **(i)** valoarea de **lichidare/vânzare
forțată** (GEV 520 §6.4) — băncile o cer explicit; **(ii)** **Anexa 1 de certificare** (checklist
~18 puncte) generată și bifată în `.docx`; **(iii)** **grila de risc de garanție** cuantificată
(lichiditate, vandabilitate, risc juridic/tehnic) cu scor; **(iv)** haircut **ofertă→tranzacție**
obligatoriu (art. 4.3.4 — scrapingul aduce oferte, nu tranzacții confirmate).

**(b) Ce e rezolvat.** Gardul (iv) e pus: avertismentul „prețuri din OFERTE, nu tranzacții" +
reamintirea ajustării (`plan-post-council.md A4`). Restul (i-iii) sunt **B4/B5** — corect
încadrate ca metodologie de validat, nu de inventat de unul singur.

**(c) Ce rămâne.** Lichidarea, Anexa 1, grila de risc — toate de **confirmat ca formulă/conținut**
cu evaluatorul (factorul de lichidare îl dă evaluatorul: `protocol`, întrebarea 6), apoi de
implementat. Pachetul pentru bănci (`pachet-validare-banci.md`) cere exact aceste lucruri băncilor.

**(d) Opinia mea.** Corect și bine triat. **O nuanță unde consiliul a fost imprecis:** Gemini a
cerut integrarea cu **BIG** (Baza Imobiliară de Garanții) ca element „lipsă pentru GEV 520",
sugerând că raportul are nevoie de „număr de înregistrare BIG". Asta e **parțial greșit ca
poziționare**: BIG e un sistem la care **contribuie** evaluatorul după finalizare și e accesibil
prin ANEVAR cu restricții — nu e o sursă pe care un tool desktop o poate integra unilateral (e
corect listat ca blocant extern `C8`). Deci nu e o „lipsă a aplicației", e o dependență externă.
Per total, lichidarea + Anexa 1 sunt cele mai mari **goluri reale de conținut** care chiar pot
duce la respingere — sunt mai importante decât toată dezbaterea preț-total-vs-€/mp.

## 1.5. AML (Legea 129/2019) — risc penal

**(a) Ce a spus consiliul.** Punctul cu cea mai mare temperatură juridică. Patru sub-riscuri:
**(i)** Art. 33 — raportare cu „neglijență gravă" = închisoare 1-5 ani; un LLM care halucinează
într-un RTS expune evaluatorul penal. **(ii)** Art. 38 tipping-off — RTS/RTN salvate pe disc lângă
dosar pot fi văzute de client → dosar penal. **(iii)** Screening PEP/sancțiuni ca „placeholder" cu
bifă = ilegal (Norme 37/2021 cer consultarea bazelor reale). **(iv)** Pragul de numerar: aplicația
folosește 10.000 €, dar pentru tranzacții ocazionale ar putea fi **3.000 €** (art. 6).
Verdict unanim: **modulul AML e cel mai periculos din aplicație; nu se lansează fără audit juridic.**

**(b) Ce e rezolvat.** Toate gardurile cerute sunt **în cod, verificate**:
- Bannerul „Aplicația **NU verifică automat** listele de sancțiuni/PEP" cu linkuri la OpenSanctions
  și surse oficiale — `aml.html:14`.
- Confirmarea Art. 33 + Art. 38 **înainte** de a descărca RTS/RTN — `aml.html:124-129`
  (dialog: „DRAFT neverificat juridic... sancțiuni inclusiv penale... NU divulga clientului").
- RTS/RTN păstrate separat în folder `aml_confidential` (modul `aml/store.py` + `raportare.py`).
- **Dosarul de audit pentru jurist e deja scris** (`audit-aml-pentru-jurist.md`): cadru legal,
  tabel cu fiecare document generat + temeiul invocat, și **6 întrebări deschise** punctate
  (inclusiv pragul 10.000 vs 3.000 €, screening API obligatoriu sau nu, regula tipping-off).

**(c) Ce rămâne — BLOCANT ABSOLUT.** Auditul juridic propriu-zis (`C1`). Materialul e pregătit;
**lipsește avocatul AML care să-l semneze.** Plus decizia derivată: screening live (OpenSanctions,
gratuit) SAU dezactivarea totală a funcției cu trimitere la surse oficiale.

**(d) Opinia mea.** Consiliul are **dreptate 100% pe AML** și e zona unde scepticismul lor e cel
mai justificat. Faptul că Adi a pregătit deja `audit-aml-pentru-jurist.md` cu întrebările exacte
e maturitate — transformă „du-te la un avocat" (vag, scump, lung) în „pune avocatului aceste 6
întrebări" (țintit, 1-2 ore de consultanță). **Recomandarea mea, mai dură decât a consiliului:**
până la auditul juridic, **dezactivați generarea RTS/RTN by default** (nu doar avertisment +
confirmare). Argument: un avertisment plus o bifă **nu** acoperă riscul Art. 33 dacă textul e
generat de AI și conține o afirmație falsă — bifa dovedește că omul a fost avertizat, nu că textul
e corect. Norme interne / KYC / evaluare de risc pot rămâne active (sunt drafturi administrative cu
risc mic). Dar **RTS/RTN — documentele cu expunere penală — ar trebui să ceară activare explicită
post-audit**, nu să fie accesibile dintr-un buton la prima rulare. Acesta e single point of legal
failure al întregului produs.

## 1.6. GDPR și anonimizarea

**(a) Ce a spus consiliul.** Modelul (tokenizare `[CLIENT]`/`[ADRESA]` înainte de LLM, demascare
locală) e „bine gândit, peste medie" (consens). Riscul rezidual: **PII contextual** — descrieri
bogate („vilă P+2, 374 mp, vizavi de Primăria comunei cu 700 locuitori") permit re-identificare
indirectă (GDPR art. 4). Cereri: **(i)** casetă care arată **exact textul** care pleacă spre LLM +
buton de consimțământ; **(ii)** model `.docx` de politică GDPR + clarificare DPA cu furnizorul AI;
**(iii)** filtru-plasă (regex CNP/CF/adrese) ca safety-net.

**(b) Ce e rezolvat.** Gardul (iii) e pus: filtru regex pe textul trimis la AI + notă despre ce se
trimite (`plan-post-council.md A6`). Modelele GDPR (ii) **există ca documente**:
`gdpr/politica-prelucrare-MODEL.md` (cu secțiunea 4 dedicată sub-procesatorului AI și nota DPA) și
`gdpr/formular-consimtamant-MODEL.md`.

**(c) Ce rămâne.** Validarea juridică a pachetului GDPR (`C5`, mai ușor decât AML). Caseta de
„vezi exact ce pleacă spre AI + aprob" (i) — recomandată de 3 membri, **neimplementată încă** ca
UI dedicat (există filtrul regex, dar nu confirmarea vizuală explicită).

**(d) Opinia mea.** Consiliul e **rezonabil și corect**, fără exagerare. Modelul de anonimizare e
genuin peste media pieței. **Unde aș contesta consiliul:** Sonnet a urcat riscul GDPR la „nu suficient
pentru un audit ANSPDCP serios" și a cerut chiar **blurare automată de fețe/plăcuțe** în fotografii.
Asta e **over-engineering pentru stadiul actual** — operatorul de date este **evaluatorul**, nu
aplicația (corect documentat în `politica-prelucrare-MODEL.md §1`); riscul de re-identificare
contextuală există dar e gestionat rezonabil prin filtru + offline-mode. Blurarea de fețe e o
funcție de produs matur, nu un blocant de lansare. **Recomandarea mea pragmatică:** implementați
caseta „aprob textul trimis la AI" (e ieftină, închide obiecția consensuală și e un bun argument de
vânzare), validați juridic pachetul GDPR existent, dar **nu** blocați lansarea pe blurare de imagini.

## 1.7. Arhitectură, scraping, distribuție

**(a) Ce a spus consiliul.** Trei teme: **(i) Scraping** (imobiliare.ro/storia) — risc maxim,
nesustenabil (Cloudflare/CAPTCHA, ban IP, ToS, drept sui-generis pe baze de date). Soluția unanimă:
**extensie de browser** (omul navighează manual, extensia citește DOM → POST la localhost) = zero
scraping în backend. **(ii) Exe nesemnat** — „coșmarul antivirusului", SmartScreen ucide adopția.
**(iii) SQLite pe cloud-sync** (OneDrive/Dropbox) → „database locked".

**(b) Ce e rezolvat.**
- **Scraping:** spec-ul de migrare e **complet scris** (`spec-extensie-browser.md`): Manifest V3,
  content-scripts per portal, endpoint `/api/import-anunt`, fallback „lipește textul". Importul prin
  extensie/text **există deja parțial** în infrastructură. Estimat 2-4 zile pentru 2 portaluri.
- **Cloud-sync:** **rezolvat în cod** — `__main__.py:78-82` detectează OneDrive/Dropbox/Google Drive
  în calea bazei și **avertizează**; `_baza_scriere()` cade pe `%LOCALAPPDATA%\EvaluareANEVAR` dacă
  folderul exe e read-only.
- **Mărimea exe:** **deja rezolvată** — 50 MB, nu 176 MB (build verificat pe disc). Consiliul a
  evaluat o stare veche.

**(c) Ce rămâne.** **Certificatul de code-signing** (`C4`, ~150-300 €/an) — singura problemă de
distribuție genuin nerezolvată, și e **blocant extern** (achiziție + identitate). Migrarea
efectivă a scrapingului la extensie (`C6`) — specată, neimplementată; pe termen scurt scrapingul
rămâne cu disclaimer.

**(d) Opinia mea.** Consiliul a fost **excelent pe diagnostic, dar a citit parțial o stare veche**.
- **Code-signing:** au dreptate absolută, e cel mai bun raport cost/beneficiu din tot review-ul
  (~200 € rezolvă 80% din frecția de onboarding — a spus-o Gemini exact așa). **Prioritate reală.**
- **Scraping:** au dreptate pe termen lung, dar au **subevaluat cât de bună e deja poziționarea
  defensivă** a lui Adi — scrapingul e deja tratat ca sursă auxiliară cu disclaimer + gardă de
  pagină-listă (fixul HIGH din `plan-maine A8`, care oprește extragerea tăcută a unui preț greșit).
  Migrarea la extensie e „nice to have curând", nu „blocant de lansare". Un produs poate lansa cu
  scraping-cu-disclaimer + import manual + extensie ca fast-follow.
- **Exe nesemnat ≠ mărime:** consiliul le-a amestecat. Mărimea e rezolvată; semnătura nu. Singurul
  lucru de făcut e certificatul.
- **Ce a ratat consiliul:** nimeni nu a discutat **mecanismul de update** ca pe un risc de
  *conformitate*, deși Gemini l-a atins. Pentru un domeniu unde normele AML/ANEVAR se schimbă anual,
  un exe static **iese din legalitate** în liniște. Asta e mai grav decât pare și o reiau la §2.

## 1.8. Calitatea inginerească (ce a lăudat consiliul — și unde a fost prea generos)

**(a) Ce a spus consiliul.** Laude consistente: „top 5% proiecte" (Sonnet), arhitectură „excelentă
și perfect pliată pe profilul evaluatorului" (chairman), alegerea offline+.exe „corectă, chiar
preferabilă unui SaaS" (toți), 92% coverage / 375 teste = „reduce mult riscurile de regresie".

**(d) Opinia mea — un singur avertisment.** Coverage-ul e real și e azi **464 teste verzi**
(`plan-maine A`), prag CI 90%. Dar consiliul a tratat „92% coverage" ca dovadă de **corectitudine
metodologică**, ceea ce e o **eroare de inferență**: testele validează că *codul face ce a scris
programatorul*, reproducând valori „la cent" pe dosare reale (Mâneciu, Brașov, Bușteni, Breaza).
**Nu** validează că *metodologia e cea pe care o cere o bancă* — exact ce panelul însuși a semnalat
la 1.1-1.4. Cu alte cuvinte: ingineria e impecabilă, dar testele verzi **nu pot înlocui** peer-review-ul
de evaluator. E o capcană subtilă: un fondator se poate uita la „464 teste verzi, 92%" și conchide
„sunt gata", când de fapt validarea de **domeniu** (nu de cod) e cea care lipsește. Aceasta e,
de altfel, ideea centrală a §2.

---

# 2. Opinia mea independentă (Claude): cel mai mare risc real

Consiliul a fost foarte bun pe riscurile **vizibile și catalogabile** (AML, €/mp, scraping,
code-signing). Dar cred că **toată lumea — panel + plan — subevaluează trei lucruri**, în ordinea
gravității:

### Riscul #1 (cel mai subevaluat): validarea de domeniu e un SINGUR om, nedeblocabil de cod

Întregul produs stă pe o presupunere nevalidată: **că metodologia implementată e cea pe care o
acceptă băncile.** Tot ce e „gata" — 464 teste, 8 garduri, motor pe Decimal — validează
**implementarea**, nu **premisa**. Consiliul a cerut peer-review (C2) și validare bancară (C3) și
le-a numit „blocant comercial", dar le-a tratat ca pe niște task-uri printre altele. Eu le pun pe
**primul loc absolut**, din trei motive:

1. **Sunt singurul lucru pe care nici Adi, nici eu, nici un LLM nu îl poate face.** Codul îl scriem.
   Avocatul AML se plătește. Dar „acceptă banca X grila pe preț total?" are **un singur** răspuns
   valid: un evaluator senior + un ofițer de risc de bancă. Materialele sunt gata
   (`protocol-peer-review-evaluator.md`, `pachet-validare-banci.md`) — **lipsește doar omul.**
2. **Costul greșelii e asimetric și ireversibil reputațional.** Dacă lansezi cu o metodologie pe
   care prima bancă o respinge, primul evaluator-client pierde un raport în fața clientului lui și
   **nu se mai întoarce niciodată** — și spune și colegilor. Pe o piață mică și conservatoare
   (evaluatorii ANEVAR se cunosc între ei), o singură respingere publică poate închide produsul.
   Sonnet a numit asta corect: „reputație distrusă".
3. **E ieftin și rapid de eliminat.** 2-3 evaluatori × 1 oră fiecare pe dosare pe care **deja le au**.
   Nu e cercetare; e o după-amiază de telefoane. Raportul cost/risc e absurd de favorabil.

**Concluzie #1:** nimic altceva nu contează până nu ai **o singură semnătură** pe
`protocol-peer-review-evaluator.md` care zice „metodologia e defensabilă (cu/fără modificările X)".
Asta nu e un task din listă — e **poarta**.

### Riscul #2 (subevaluat de toți, atins doar de Gemini): produsul iese din legalitate în tăcere

Aplicația codifică **norme care expiră**: praguri AML, standarde SEV/GEV (revizuite anual),
indicatori de suspiciune HCD 58, cursuri, structura raportului bancar. Un `.exe` offline distribuit
azi va aplica, peste 18 luni, **reguli vechi** — fără ca evaluatorul (sau Adi) să știe. Pentru AML,
asta nu e un bug, e **expunere de conformitate**: evaluatorul raportează după un prag perimat.

Nimeni din panel n-a tratat asta ca risc de prim ordin (Gemini l-a numit „compromis ratat",
GPT-5.1 l-a redus la „update mechanism lipsă"). Eu îl ridic la **#2**, fiindcă interacționează
periculos cu riscul AML: un produs care „te ajută cu AML" dar **nu se actualizează** e mai
periculos decât niciun produs, fiindcă induce **fals sentiment de conformitate la termen**.

**Minimul absolut înainte de a vinde primul exemplar plătit:** un **kill-switch / notificare de
versiune** — la pornire, exe-ul verifică un fișier de versiune (GitHub Releases) și, dacă e prea
vechi sau marcat „critic", afișează un banner roșu „Actualizare obligatorie — normele s-au schimbat".
E `D3` în plan (notificare de versiune), listat ca *opțional*. **Nu e opțional pentru un produs
plătit într-un domeniu reglementat — e o obligație de diligență.** Costul: ~1 zi.

### Riscul #3 (out-of-the-box): lipsa telemetriei te face orb exact când treci la plată

Consiliul a notat în treacăt (GPT-5.1) că offline = „nu poți colecta telemetrie/bug-reports". Pe
faza de tool-trimis-prietenește, irelevant. **Pe faza de produs plătit (#4 comercializare), devine
critic:** când ai 20 de plătitori și unul are crash la generarea `.docx` pe un dosar anume, **nu
vei ști niciodată** — el renunță la abonament și pleacă tăcut. Widgetul de feedback există
(`distributie-evaluator.md`), dar e **pull manual** (cere-i userului folderul). Nu scalează.

**Recomandarea mea out-of-the-box:** gateway-ul de comercializare (`4-comercializare.md`) deja are
un canal online (Supabase) prin care trece fiecare apel AI. **Atașați la el un crash/error-ping
minimal, anonim** (doar: versiune, tip eroare, modul — zero PII, zero date de dosar). Costă aproape
nimic (un `try/except` care face POST la edge function pe care o ai deja), și transformă „orb la
20 de plătitori" în „văd ce se sparge la cine". Nu e în niciun plan acum. **Acesta e cel mai bun
ROI nehotărât din tot proiectul** pentru faza comercială.

### Ce NU mă îngrijorează (contra-curent față de panel)

- **Arhitectura monolit FastAPI+Jinja+SQLite.** Sonnet a avertizat de „Jinja PHP hell" la 15k linii
  și refactor modular la 50k. Irelevant pentru orizontul previzibil — produsul e single-user, 5.700
  linii, și nu va atinge 50k curând. **Optimizare prematură.** Nu cheltui nimic aici.
- **Mărimea exe.** Rezolvată (50 MB). Ignorați critica veche a consiliului.
- **GDPR-ul ca blocant.** E peste medie și gestionat. Validare juridică ușoară, nu blocant greu.

---

# 3. Starea de pregătire pentru lansare (release-readiness)

Legendă stare: ✅ gata · 🔧 în lucru · 🟡 blocat de decizie (Adi/evaluator) · ⛔ blocat extern (terț/plată).

## Metodologie (validare evaluator senior)
| Item | Stare | Cine deblochează |
|---|---|---|
| Motor de calcul (4 abordări, Decimal, 464 teste) | ✅ | — (gata) |
| Garduri prudențiale (ajustare >25% brut, depreciere >20%) | ✅ în cod (`validation.py`) | — |
| Afișare ajustare brută TOTALĂ lângă selecție | ✅ | — |
| **Selecție pe brută totală ca criteriu principal** | 🟡 | Adi (decizie B2) + evaluator (confirmare) |
| **Grilă casă: strat de prezentare €/mp** | 🟡 | Adi (B1) + evaluator |
| **Ajustare degresivă de suprafață** | 🟡 | evaluator (B3) |
| **Valoare de lichidare (factor)** | 🟡 | evaluator (factor) — `protocol` Q6 |
| **Anexa 1 certificare GEV 520 (checklist ~18 pct)** | 🟡 | evaluator (conținut) + Adi (implementare) |
| **Grilă de risc garanție cuantificată** | 🟡 | evaluator (criterii/ponderi) |
| **PEER-REVIEW SEMNAT (≥2 evaluatori, 5-10 dosare)** | ⛔ | **Adi: găsește 2-3 evaluatori** (material gata: `protocol`) |
| **Validare formă cu 2-3 bănci** | ⛔ | **Adi: trimite `pachet-validare-banci.md`** |

## Juridic (vezi docs/gdpr/ și docs/audit-aml-pentru-jurist.md)
| Item | Stare | Cine deblochează |
|---|---|---|
| Material audit AML pentru jurist (6 întrebări) | ✅ scris | — |
| Garduri AML în cod (banner, confirmare Art. 33/38, folder separat) | ✅ | — |
| **Audit juridic AML semnat** | ⛔ | **Adi: avocat AML (Legea 129)** — BLOCANT ABSOLUT |
| **Decizie screening: API live vs. dezactivat** | 🟡→⛔ | Adi (după sfatul juristului) |
| Model politică GDPR + formular consimțământ | ✅ scris (MODEL) | — |
| **Validare juridică pachet GDPR** | ⛔ | Adi: jurist GDPR (ușor) |
| **EULA / termeni de utilizare + limitare răspundere** | 🟡 | Adi + jurist (nescris încă) |
| Casetă „aprob textul trimis la AI" (UI consimțământ) | 🔧 (filtru regex există; UI nu) | Adi (decizie) |

## Tehnic (update / telemetrie / crash)
| Item | Stare | Cine deblochează |
|---|---|---|
| Logging centralizat + consolă la crash | ✅ | — |
| Fallback `%LOCALAPPDATA%` + avertisment cloud-sync | ✅ în cod (`__main__.py`) | — |
| Exe optimizat (50 MB) | ✅ | — |
| Backup automat dosare (D1) | 🔧 (parțial — folder `backups/`) | Adi |
| Migrare schemă DB la pornire (D2) | 🟡 neimplementat | Adi |
| **Notificare de versiune / kill-switch (D3)** | 🟡 neimplementat | **Adi — recomand ridicat la blocant (vezi §2 #2)** |
| **Telemetrie crash anonimă** | 🟡 neexistent | Adi (recomand pentru faza plătită — §2 #3) |
| Migrare scraping → extensie (C6) | 🔧 specat (`spec-extensie-browser.md`), neimplementat | Adi |

## Comercial (gateway, plăți, conturi)
| Item | Stare | Cine deblochează |
|---|---|---|
| Spec + plan implementare gateway (Supabase+Stripe) | ✅ complet | — |
| Cont local + identitate dosar | 🔧 schelet livrat (`plan-maine A1`); identitate = decizii B1-B4 | Adi |
| **Conturi externe (Supabase/Google/Stripe — Faza 0)** | ⛔ | **Adi: creează conturile (~1-2h)** |
| Gateway (proxy AI, sesiuni, cotă, webhook) | 🟡 neimplementat (plan gata) | Adi (decizie de start) |
| Praguri de preț validate | ⛔ | Adi: validare cu 5-10 evaluatori |

## Conformitate (GDPR / AML / AI Act)
| Item | Stare | Cine deblochează |
|---|---|---|
| GDPR — model tehnic (anonimizare + filtru) | ✅ | — |
| AML — garduri + material jurist | ✅ | — |
| **AI Act (transparență „text asistat de AI")** | 🟡 parțial (marcaj „draft AI") | Adi + jurist (vezi notă mai jos) |
| Disclaimer „raport asistat de AI, asumat de evaluator" în `.docx` | 🔧 recomandat de panel, de confirmat în generator | Adi |

> **Notă AI Act (pe care consiliul l-a ratat complet):** din feb. 2025 se aplică primele obligații
> din Regulamentul UE 2024/1689. Un asistent care redactează text pentru un document profesional
> cade probabil sub cerințe de **transparență** (utilizatorul/destinatarul trebuie să știe că textul
> e generat de AI). Probabil **risc limitat**, nu „high-risk" — dar merită un rând în întrebările
> către jurist. Marcajul „draft AI — verifică" deja existent ajută. Nimeni din panel nu l-a menționat.

## Suport
| Item | Stare | Cine deblochează |
|---|---|---|
| Ghid de distribuție către evaluator | ✅ (`distributie-evaluator.md`) | — |
| Widget feedback (local + opțional Google Forms) | ✅ | — |
| Exemplu de raport (Breaza, anonimizabil) | ✅ | — |
| Canal de suport structurat (post-plată) | 🟡 ad-hoc | Adi (faza comercială) |

---

# 4. Plan agregat final (secvență de lansare)

## (A) CE E GATA acum
- Motor de calcul complet (4 abordări SEV 103/105), pe Decimal, **464 teste verzi**, prag CI 90%.
- **Toate cele 8 garduri de protecție post-council, verificate în cod:** alerte prudențiale de
  ajustare, ajustare brută totală afișată, alertă consistență cost↔piață, avertisment oferte vs.
  tranzacții, banner + confirmare AML (Art. 33/38), filtru GDPR, marcaj „draft AI", avertisment
  cloud-sync.
- UI nou „output-first" funcțional end-to-end (cont → ÎNCEPE → workspace), stocare folder-per-dosar,
  import `.docx`, 4 dosare-exemplu.
- Exe 50 MB, pornire în ~2s, fallback `%LOCALAPPDATA%`.
- **Toate materialele de execuție pentru blocanți sunt scrise:** dosar audit AML, protocol
  peer-review, pachet validare bănci, modele GDPR, spec extensie, ghid distribuție.
- Spec + plan complet de comercializare (gateway Supabase+Stripe, metrare per raport).

## (B) CE E ÎN LUCRU
- Identitatea dosarului + lock după prima generare (decizii B1-B4 — deblochează metrarea #4).
- Conținut real în tab-urile AML/GDPR/Audit/Anexe din workspace (acum parțial linkuri/placeholdere).
- Backup automat (parțial), goluri de acoperire `ocr`/`generator` (în reducere autonomă).
- Migrarea scraping→extensie: specată, fallback cu disclaimer activ.

## (C) CE E PLANIFICAT (din topicurile abordate)
**Ordonat ca dependențe, nu ca listă:**
1. **Validări externe (paralelizabile, încep imediat):** peer-review evaluator (C2), validare bănci
   (C3), audit juridic AML (C1), validare GDPR (C5). **Toate au materialul gata** — lipsește execuția umană.
2. **Implementări gated de #1:** ce decid evaluatorii la B1-B8 (€/mp, selecție brută totală,
   degresiv, lichidare, Anexa 1, risc garanție); ce decide juristul la AML (prag, screening).
3. **Code-signing (C4):** achiziție certificat, independent de #1-#2.
4. **Comercializare (#4):** Faza 0 conturi → MVP gateway → 2-3 plătitori. După validări.

## (D) CE E NEPLANIFICAT dar recomand (idei noi, out-of-the-box)

**Scurt termen (înainte de primul exemplar plătit):**
- **D-nou-1 — Kill-switch / notificare de versiune obligatorie** (ridic `D3` din opțional la necesar).
  *De ce:* un produs reglementat care nu se poate „opri/avertiza" când normele se schimbă e o
  expunere de conformitate (§2 #2). *Compromis:* ~1 zi muncă; alternativa e risc juridic difuz dar real.
- **D-nou-2 — Dezactivare RTS/RTN by default până la auditul juridic** (mai dur decât avertismentul actual).
  *De ce:* bifa dovedește avertizarea, nu corectitudinea textului — Art. 33 rămâne expus (§1.5).
  *Compromis:* pierzi o funcție vizibilă la demo; câștigi eliminarea single-point-of-legal-failure.
- **D-nou-3 — Casetă „aprob exact textul trimis la AI"** (UI peste filtrul regex existent).
  *De ce:* închide obiecția GDPR consensuală a panelului + e argument de vânzare („vezi exact ce pleacă").
  *Compromis:* mic UI; aproape gratis.

**Mediu termen (faza comercială):**
- **D-nou-4 — Telemetrie crash anonimă prin gateway-ul deja planificat** (zero PII).
  *De ce:* fără ea ești orb la 20 de plătitori care pleacă tăcut (§2 #3). *Compromis:* un `try/except`
  + POST la o edge function pe care oricum o ai. **Cel mai bun ROI nehotărât din proiect.**
- **D-nou-5 — Generarea automată a pachetelor de validare ca `.docx`** (peer-review + scrisoare bancă
  direct din aplicație, pre-completate cu datele dosarului-demo). *De ce:* scade frecția de a rula
  validările externe (#1) — exact poarta critică. *Compromis:* mic; accelerează singurul blocant care
  contează.
- **D-nou-6 — „Mod offline-only" comutabil explicit** (un buton care taie orice apel extern, pentru
  dosare sensibile / clienți PEP). *De ce:* argument de conformitate puternic + simplifică povestea
  GDPR pentru cazurile grele. *Compromis:* mic; capabilitatea există deja (fără cheie = offline),
  doar de făcut explicită și vizibilă.

---

# 5. „Spune DA la asta" (rezumat de 1 pagină pentru aprobare)

**Ce aprobi:** secvența exactă până la lansarea pe piața liberă a tool-ului local plătit (fără
marketing). Produsul tehnic e gata; ce urmează e **validare de domeniu + juridic + 2 garduri noi**.

### Poarta 0 — Validări externe (încep ACUM, în paralel; tu le declanșezi)
> Toate au materialul scris. Lipsește doar **omul**. Acesta e drumul critic — restul așteaptă aici.

1. ☐ **Dă `audit-aml-pentru-jurist.md` unui avocat AML** (Legea 129). *Decizie umană: doar tu — alegi/plătești avocatul.* **BLOCANT ABSOLUT.**
2. ☐ **Trimite `protocol-peer-review-evaluator.md` la 2-3 evaluatori seniori** (1h fiecare, pe dosarele lor). *Decizie umană: doar tu — îi identifici.* **POARTA care validează premisa produsului.**
3. ☐ **Trimite `pachet-validare-banci.md` + raport demo la 2-3 bănci.** *Decizie umană: doar tu.*
4. ☐ **Dă modelele `gdpr/*-MODEL.md` la un jurist GDPR** (ușor, scurt).

### Poarta 1 — 2 garduri noi + code-signing (le pot face eu pe cod; tu decizi/cumperi)
5. ☐ **Dezactivează RTS/RTN by default** până la auditul AML (activare explicită post-audit). *Cod: eu. Decizie: tu confirmi.*
6. ☐ **Adaugă notificare de versiune obligatorie** (kill-switch reglementar, ~1 zi). *Cod: eu. Decizie: tu confirmi că o vrei.*
7. ☐ **Cumpără certificat code-signing** (~150-300 €/an) și semnează exe-ul. *Decizie umană: doar tu — achiziție + identitate.*

### Poarta 2 — Implementezi ce au decis experții (gated de Poarta 0)
8. ☐ Aplici răspunsurile evaluatorilor (B1-B8: €/mp prezentare, selecție brută totală, degresiv, lichidare, Anexa 1, risc garanție). *Cod: eu. Conținut/praguri: evaluatorul a decis.*
9. ☐ Aplici răspunsurile juristului AML (prag numerar, screening live vs. dezactivat). *Cod: eu. Decizie: juristul + tu.*
10. ☐ Validare formă cu băncile → integrezi cerințele comune. *Cod: eu.*

### Poarta 3 — Comercializare (după ce produsul e validat)
11. ☐ Creezi conturile externe (Supabase/Google/Stripe — Faza 0, ~1-2h). *Decizie umană: doar tu.*
12. ☐ Construiesc MVP-ul gateway (plan gata) + telemetrie crash anonimă. *Cod: eu.*
13. ☐ Validezi pragurile de preț cu 5-10 evaluatori → primii plătitori. *Decizie umană: doar tu.*

**Regula de aur (deja respectată în tot proiectul):** aplicația **avertizează**, nu decide.
Metodologia și pragurile legale **nu se ating** fără semnătura unui evaluator senior / jurist.

> **Dacă spui „da" la cele 13 de mai sus**, ordinea e: **Poarta 0 + pașii 5,6,7 pornesc azi în
> paralel** (validările sunt asincrone — durează la terți; gardurile le fac între timp). Poarta 2
> începe pe măsură ce sosesc răspunsurile. Poarta 3 e ultima. Estimarea realistă a panelului
> (2-3 luni până la uz real) e corectă — **dar e dominată de timpii de răspuns ai terților, nu de
> muncă de cod.** De aceea Poarta 0 trebuie pornită în prima zi.

---

## Rezumat final (sub 250 de cuvinte)

**Verdictul meu:** produsul tehnic este gata și ingineria e genuin peste medie (464 teste, 8 garduri
verificate în cod). Consiliul a fost bun pe riscurile catalogabile, dar chairman-ul a **exagerat**
problema preț-total-vs-€/mp (e formă, nu fond — matematic echivalentă; 3 din 4 membri au spus-o),
a citit o **stare veche** la distribuție (exe e 50 MB, nu 176; cloud-sync e deja gestionat în cod),
și a **ratat** AI Act-ul și update-ul-ca-risc-de-conformitate. A avut dreptate fără rezerve pe AML,
pe selecția comparabilei (brută totală) și pe consistența cost↔piață (derivată din datele reale ale
lui Adi — cea mai bună observație din review). Materialele de execuție pentru toți blocanții sunt
deja scrise; lipsește **execuția umană**, nu munca de cod.

**3 lucruri OBLIGATORII înainte de lansare:**
1. **Peer-review semnat de ≥2 evaluatori seniori** — validează însăși premisa produsului; e ieftin
   (o după-amiază), ireversibil reputațional dacă lipsește, și nimeni în afară de un evaluator nu-l poate da.
2. **Audit juridic AML** (Legea 129) — risc penal Art. 33/38; blocant absolut.
3. **Notificare de versiune / kill-switch** — fără el, produsul iese tăcut din legalitate când normele se schimbă.

**3 decizii pe care DOAR Adi le poate lua:**
1. **Pe cine** trimite la peer-review și la audit juridic (drumul critic — terți, asincron).
2. **Screening AML:** API live (OpenSanctions) vs. dezactivare totală cu trimitere la surse oficiale.
3. **Cumpără sau nu** certificatul de code-signing (~200 €/an) acum vs. lansare cu disclaimer SmartScreen.
