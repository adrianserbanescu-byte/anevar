# Evaluare juridică de risc — lansarea pe piață a aplicației de asistență a evaluatorilor ANEVAR

> **DRAFT — necesită validarea unui avocat din România înainte de utilizare. Nu constituie consultanță juridică.**
>
> Documentul reprezintă o analiză internă de risc realizată pentru pregătirea lansării comerciale.
> Concluziile, calificările juridice și recomandările trebuie confirmate de un avocat român
> (de preferință cu specializare în protecția datelor / IT / dreptul afacerilor) și, pentru partea
> AML, de un consultant specializat. Conform regulii de guvernanță a proiectului, juridicul aparține
> „bucket C — jurist".

**Versiune:** 0.1 (draft inițial) · **Data:** [DE COMPLETAT: data redactării finale] · **Autor:** echipa de produs (asistat) · **Destinatar:** avocat validator

---

## 0. Rezumat executiv (pentru decident)

Produsul este o **aplicație desktop locală (.exe Windows, offline)** care **asistă** un evaluator
autorizat ANEVAR la întocmirea rapoartelor de evaluare imobiliară (SEV 2025 / GEV 520), pe principiul
**„om în buclă"**: aplicația propune, evaluatorul decide și semnează. Se vinde prin **abonament** către
evaluatori individuali (PFA / persoane juridice — deci **B2B profesional**). Componenta de inteligență
artificială (text narativ) rulează printr-un **gateway online propriu** care primește **doar text
anonimizat**. Datele clientului evaluării (inclusiv date cu caracter personal ale unor persoane fizice
— de regulă debitori ipotecari) rămân **local** pe calculatorul evaluatorului.

Riscurile juridice dominante, în ordinea priorității:

1. **Protecția datelor (GDPR)** — calificarea corectă a rolurilor (operator vs. persoană împuternicită),
   necesitatea unui **DPA art. 28** între furnizor și evaluator, transferul de text anonimizat către
   furnizorul de LLM (posibil în afara UE) și gestionarea telemetriei/logurilor de crash.
2. **Răspunderea profesională și limitarea răspunderii furnizorului** — aplicația **nu** își asumă
   valoarea evaluată; judecata profesională și semnătura aparțin evaluatorului ANEVAR.
3. **Proprietatea intelectuală** — standardele ANEVAR/SEV sunt protejate de drept de autor și **nu pot
   fi redistribuite** în produs; se referențiază, nu se copiază.
4. **AI Act (Reg. UE 2024/1689)** — obligații de transparență; analiza dacă „evaluarea pentru credit"
   atinge zona de risc ridicat.
5. **Cadrul comercial** — protecția consumatorului (B2B vs. B2C), comerț electronic, facturare/TVA pentru
   abonament digital, eventual regimul OSS la vânzări intra-UE.

Niciun risc identificat nu pare, la nivel preliminar, **blocant** pentru lansare, cu condiția punerii în
practică a **acțiunilor obligatorii înainte de lansare** din §13. Riscul rezidual major este de
**conformitate documentară** (lipsă DPA, lipsă informări), nu de model de business.

---

## 1. Descrierea produsului relevantă juridic

Elemente cu impact juridic, extrase din specificațiile interne
(`docs/specs/4-comercializare.md`, `4-comercializare-plan-implementare.md`,
`docs/plan-maine-2026-06-06.md`) și din memoria de proiect:

| Aspect | Descriere |
|---|---|
| Forma livrării | Aplicație desktop Windows (`.exe`), funcționează **offline** pentru calcul, grile, AML, GDPR, asamblare `.docx`, narativ-șablon. |
| Componenta online | Doar la acțiunea „Generează AI": app trimite **text anonimizat** către un **gateway propriu** (Supabase Edge Function + Postgres), care cheamă un **LLM** (în prezent **Perplexity**; istoric și **Anthropic Claude**) cu cheia furnizorului, metrează și facturează. |
| Date personale procesate | **Local:** date de identificare client/proprietar (nume, adresă, eventual CNP), date imobil (cadastru, CF, fotografii), date KYC/beneficiar real (modul AML). **Online (gateway/LLM):** doar text din care identificatorii direcți au fost înlocuiți cu marcaje (`[CLIENT]`, `[ADRESA]`, `[CF]`, `[CADASTRAL]`), demascarea făcându-se local. |
| Autentificare | Google Sign-In (principal) + magic-link email (fallback). Abonament Stripe legat de e-mail. |
| Stocare | **Local** pe calculatorul evaluatorului (foldere `date/dosare/<uuid>/`, eventual SQLite). Online: doar conturi, sesiuni, cotă de consum, date de facturare (la furnizorul de plăți / gateway). |
| Model de vânzare | Abonament lunar/anual, trepte (Solo/Pro/Nelimitat), trial. Client = evaluator PFA/PJ. |
| Modul AML | Implementat ca **asistență** (drafturi, fișe KYC, indicatori, RTN/RTS), cu avertismente că nu înlocuiește obligațiile entității raportoare și nu face screening live PEP/sancțiuni. |

**Concluzie de încadrare:** furnizorul software vinde un **instrument** (SaaS hibrid: desktop + un serviciu
online metrat de AI), nu un serviciu de evaluare și nici un serviciu juridic/AML. Acest fapt este central
pentru întreaga analiză de răspundere și de roluri GDPR.

---

## 2. Calificarea părților sub GDPR (Reg. (UE) 2016/679)

### 2.1. Principiul director

Sub GDPR, **operatorul** (art. 4 pct. 7) este cel care stabilește **scopurile și mijloacele** prelucrării;
**persoana împuternicită** (art. 4 pct. 8) prelucrează **în numele** operatorului, pe baza instrucțiunilor
acestuia. Calificarea nu depinde de denumirea din contract, ci de **rolul factual**.

### 2.2. Evaluatorul = operator (controller)

Pentru datele clienților săi (proprietar, debitor ipotecar, terți menționați în raport), **evaluatorul
ANEVAR (PFA/PJ) este operator**:

- el decide **scopul** (întocmirea raportului de evaluare, conformitatea AML, relația cu banca/clientul);
- el decide **mijloacele esențiale** (ce date colectează, ce raport produce, cui îl predă);
- datele sunt deținute și controlate **local**, pe echipamentul lui;
- obligația de raportare AML (Legea 129/2019) îi revine **lui** ca entitate raportoare, nu furnizorului.

În consecință, evaluatorul răspunde de: temei legal, informarea persoanelor vizate, drepturile acestora,
securitate, retenție, eventuale notificări de breșă. Modelele din `docs/gdpr/` (politică + consimțământ)
sunt corecte ca direcție și îl tratează just pe evaluator drept operator.

### 2.3. Furnizorul software = persoană împuternicită, DAR cu domeniu strict limitat

**Argumentare nuanțată — esențială pentru DPA:**

- **Pentru datele stocate local** (foldere dosare, SQLite, fotografii): furnizorul **nu are acces** la ele
  și **nu le prelucrează** — aplicația rulează pe calculatorul evaluatorului, offline. Aici furnizorul
  **nu este nici operator, nici persoană împuternicită** pentru conținutul dosarului; el este doar
  **furnizor de produs software** (analog unui editor de text). Acest punct trebuie afirmat clar
  contractual, pentru a nu extinde nejustificat răspunderea furnizorului.
- **Pentru textul trimis la gateway/LLM**: furnizorul **operează gateway-ul** și **decide mijloacele
  tehnice** (ce LLM, cu ce cheie, cum metrează). Întrucât prelucrează text **în numele** evaluatorului
  și pentru scopul stabilit de acesta (redactarea analizei din raport), furnizorul este, pentru această
  felie, **persoană împuternicită** (art. 28 GDPR). Faptul că textul este **anonimizat** atenuează, dar
  nu elimină automat calificarea (vezi §2.4 — riscul de re-identificare).
- **Pentru datele de cont/abonament/sesiuni** (e-mail, identitate Google, IP/oră în loguri, date de
  facturare): aici furnizorul stabilește **el** scopurile (autentificare, licențiere, anti-abuz,
  facturare). Pentru aceste date, furnizorul este **operator în nume propriu** față de **evaluator ca
  persoană vizată** (clientul B2B). Aceasta este o relație GDPR separată, acoperită de Politica de
  confidențialitate (doc. 11), nu de DPA.

> **Sinteză roluri (de validat juridic):**
> - Date dosar (local) → furnizor = **nici operator, nici împuternicit** (doar furnizor de software).
> - Text la AI (gateway/LLM) → evaluator = **operator**, furnizor = **persoană împuternicită**, LLM = **sub-împuternicit**.
> - Cont/abonament/telemetrie a evaluatorului → furnizor = **operator** (evaluatorul e persoana vizată).

### 2.4. Anonimizare vs. pseudonimizare la AI — punct sensibil

Specificația folosește termenul „anonimizat": identificatorii direcți (nume, adresă, CF, cadastral) sunt
înlocuiți cu marcaje, iar demascarea se face **local**. Juridic, dacă demascarea este posibilă (există o
hartă de corespondență locală), prelucrarea trimisă la AI este, riguros, **pseudonimizare**, nu anonimizare
ireversibilă în sensul Considerentului 26 GDPR. În plus, **adresa exactă a unui imobil** poate fi
**indirect identificantă** (un imobil unic într-o localitate mică).

**Implicații (de confirmat de avocat):**

- Tratează prudent textul trimis la AI ca **date cu caracter personal pseudonimizate**, deci **în sfera
  GDPR** → DPA + sub-împuternicit rămân necesare.
- Întărește anonimizarea: elimină nu doar numele/adresa, ci și **suprafețe + localitate + indicii unice**
  combinate care ar permite re-identificarea, sau cel puțin documentează că riscul rezidual este scăzut.
- Menține și promovează **modul complet offline** (fără AI) ca opțiune pentru cazuri sensibile — este un
  argument puternic de minimizare (art. 5(1)(c)) și un diferențiator comercial.
- **[DE COMPLETAT: decizie avocat]** dacă, pe baza nivelului concret de anonimizare, textul la AI poate fi
  tratat ca **anonim** (în afara GDPR) — caz în care DPA pentru felia AI ar deveni opțional, dar recomandat
  oricum din precauție și ca cerință a furnizorului LLM.

### 2.5. Temei legal, minimizare, transfer

- **Temei legal (la nivelul evaluatorului-operator):** art. 6(1)(b) executarea contractului cu clientul;
  art. 6(1)(c) obligație legală pentru AML (Legea 129/2019); art. 6(1)(f) interes legitim profesional.
  Pentru **CNP**, atenție la cerințele suplimentare din legislația națională privind prelucrarea codului
  numeric personal — de folosit doar dacă este strict necesar.
- **Minimizare (art. 5(1)(c)):** arhitectura „local-first + doar text anonimizat la AI" este, prin design,
  conformă cu minimizarea și cu **protecția datelor din concepție și implicită (art. 25)**. Acesta este un
  punct forte de apărat și documentat (un mini-DPIA / analiză art. 25 ar fi util — vezi §11).
- **Transfer internațional:** dacă furnizorul de LLM stochează/procesează **în afara SEE** (ex. SUA), se
  aplică **Cap. V GDPR**. Soluții: (i) furnizor LLM acoperit de **EU-US Data Privacy Framework** (dacă
  certificat), sau (ii) **Clauze Contractuale Standard (SCC)** + evaluare de impact a transferului (TIA),
  sau (iii) alegerea unui LLM cu procesare **în UE**. **[DE COMPLETAT: numele și jurisdicția furnizorului
  LLM final + mecanismul de transfer aplicabil.]**

---

## 3. DPA (Acord de prelucrare) și acordul cu sub-împuternicitul

### 3.1. DPA furnizor ↔ evaluator (obligatoriu)

Pentru felia în care furnizorul este persoană împuternicită (textul la AI), **art. 28(3) GDPR impune un
contract scris** (DPA) care să prevadă: obiectul, durata, natura și scopul prelucrării; tipul de date și
categoriile de persoane vizate; obligațiile și drepturile operatorului; precum și clauzele obligatorii
(instrucțiuni documentate, confidențialitate, securitate art. 32, sub-împuterniciți art. 28(2)/(4),
asistență la drepturile persoanelor vizate, asistență la breșe/DPIA, ștergere/returnare la final, audit).

→ Livrat ca **doc. 13 (DPA-DRAFT)**, cu anexa sub-împuterniciților. Se semnează/acceptă electronic la
activarea contului (parte din onboarding), separat de EULA și de Termeni.

> Notă de prudență: dacă avocatul confirmă că textul la AI este **anonim** (în afara GDPR), DPA devine din
> obligatoriu în **recomandat** (bună practică + cerință a furnizorului LLM). Recomandarea fermă este să
> existe oricum, dat fiind riscul de re-identificare din §2.4.

### 3.2. Acord cu sub-împuternicitul (LLM)

Furnizorul nu poate angaja un sub-împuternicit (LLM) fără **autorizarea** operatorului (art. 28(2)) și fără
să-i impună **prin contract aceleași obligații** de protecție a datelor (art. 28(4)). Practic:

- Se acceptă **DPA-ul / Termenii de prelucrare** ai furnizorului LLM (Perplexity / Anthropic etc.) —
  acestea există de regulă ca documente standard ale providerului.
- Se verifică: **politica de retenție** a providerului, dacă **folosește datele la antrenare** (de
  preferat: **opt-out / „no training"** sau plan enterprise care exclude antrenarea), **localizarea
  serverelor** și **mecanismul de transfer** (SCC/DPF).
- Sub-împuternicitul se trece în **Anexa 2 a DPA** (lista sub-împuterniciților), cu obligația de **notificare
  prealabilă** a evaluatorilor la **schimbarea** providerului LLM și **drept de opoziție**.

**[DE COMPLETAT: numele exact al providerului LLM, link la DPA-ul lui, jurisdicția, politica de antrenare,
mecanismul de transfer.]**

---

## 4. Răspunderea profesională și limitarea răspunderii furnizorului

### 4.1. Principiul „om în buclă"

Produsul **propune**; evaluatorul **decide și semnează**. Valoarea finală, raționamentul profesional,
conformitatea cu SEV 2025 / GEV 520 și semnătura aparțin **exclusiv evaluatorului autorizat ANEVAR**.
Aplicația este un **instrument de asistență**, nu un evaluator automat și nu un substitut al judecății
profesionale.

### 4.2. Consecințe contractuale (limitarea răspunderii)

- Furnizorul **nu garantează** corectitudinea valorii evaluate, conformitatea raportului cu standardele,
  ori potrivirea pentru un anumit scop (ex. decizia de creditare a băncii).
- Furnizorul **nu răspunde** față de terți (bancă, client final al evaluatorului, ANEVAR) pentru conținutul
  rapoartelor — răspunderea profesională rămâne a evaluatorului (inclusiv față de organismele profesionale
  și de asigurarea de răspundere profesională).
- Se introduc **disclaimere** și **plafoane de răspundere** (cap pe valoarea abonamentului pe o perioadă,
  excluderea daunelor indirecte) — vezi EULA (doc. 12) §limitare și disclaimerul profesional (doc. 14).
- **Limite imperative:** în România/UE, răspunderea **nu poate fi exclusă** pentru **dol, culpă gravă,
  vătămare corporală/deces**, și nu pot fi înlăturate **drepturile imperative ale consumatorului** dacă
  vreun client este consumator (vezi §6). Clauzele de limitare trebuie redactate să **reziste** testului de
  caracter abuziv și de bună-credință — **[DE COMPLETAT: avocat — calibrarea plafonului și a excluderilor].**

### 4.3. Special: outputul AI

Textul generat de AI poate conține erori/„halucinații". Disclaimerul trebuie să spună explicit că **textul
narativ AI este un draft de verificat de evaluator** înainte de includere în raport, iar răspunderea pentru
conținutul final este a evaluatorului. (Aliniat cu obligațiile de transparență din AI Act — §7.)

---

## 5. Proprietate intelectuală

### 5.1. Standardele ANEVAR/SEV — NU se redistribuie

Textele oficiale **SEV 2025**, **GEV 520**, precum și actele AML referențiate (Legea 129/2019, Norme
Ord. 37/2021, HCD 58/74) păstrate în `md files/` sunt **opere/colecții protejate** (drept de autor
ANEVAR pentru standarde; pentru actele normative se aplică regimul special al textelor oficiale, dar
adaptările/comentariile/coletările pot fi protejate). **Riscul concret:** redistribuirea integrală a
standardelor ANEVAR în produs (în `.exe`, în fișiere livrate, în output) poate încălca **Legea nr. 8/1996**
privind dreptul de autor și drepturile ANEVAR.

**Reguli de gestionare (obligatorii):**

- **Nu** se împachetează textele integrale ale standardelor ANEVAR în `.exe` livrat clienților.
- Se folosesc **referințe** (ex. „conform SEV 2025, secțiunea X" / „potrivit GEV 520") și **parafrazări
  proprii**, nu citate extinse.
- Materialele din `md files/` rămân **resurse interne de dezvoltare**, nu artefacte de distribuție.
- Citatele scurte sunt admise doar în limitele **dreptului de citare** (art. 33 Legea 8/1996: scop critic/
  ilustrativ, întindere justificată, cu indicarea sursei și autorului).
- **[DE VERIFICAT: avocat]** dacă este necesară o **licență/acord cu ANEVAR** pentru un instrument comercial
  care implementează metodologia ANEVAR și folosește mărci/denumiri ANEVAR, și dacă există reguli ANEVAR
  privind tool-uri comerciale terțe (menționate în spec ca „de verificat — bucket C").

### 5.2. Mărci și denumiri

„ANEVAR", „SEV", „GEV" pot fi **mărci/denumiri protejate**. Folosirea lor în marketing și în produs trebuie
să fie **descriptivă** și **fără a sugera afiliere/aprobare** din partea ANEVAR (decât dacă există acord).
Recomandare: disclaimer „produs independent, neafiliat și neavizat de ANEVAR" — **[DE COMPLETAT: confirmare
poziție ANEVAR].**

### 5.3. Software-ul propriu

Codul, interfața, structura raportului `.docx`, motoarele de calcul și prompturile sunt **opera furnizorului**
și se licențiază sub **EULA proprietar** (doc. 12), cu **interdicția partajării licenței** și a
decompilării/redistribuirii. Dependențele open-source folosite (ex. `lxml`, `python-docx`) impun
respectarea licențelor lor — **[DE COMPLETAT: inventar licențe terțe / fișier NOTICE].**

---

## 6. Protecția consumatorului și contracte la distanță (B2B vs. B2C)

### 6.1. Calificarea clientului

Clienții-țintă sunt **profesioniști** (evaluatori PFA/PJ) care contractează **pentru activitatea lor
profesională**. În acest caz **NU** sunt „consumatori" în sensul **OUG nr. 34/2014** (care transpune
Directiva 2011/83/UE privind drepturile consumatorilor) și nici al legislației de clauze abuzive (Legea
193/2000), care protejează persoana fizică ce acționează **în afara** activității profesionale.

**Consecințe dacă relația rămâne strict B2B:**

- **Dreptul de retragere de 14 zile NU se aplică** (este un drept al consumatorului). Se poate oferi
  voluntar un **trial** (deja prevăzut) — mai bun comercial decât o obligație legală.
- Obligațiile de informare precontractuală din OUG 34/2014 **nu se aplică** ca atare; rămân, totuși,
  cerințele de transparență din **comerțul electronic** (vezi §6.3) și buna-credință contractuală
  (Cod civil).

### 6.2. Riscul de „consumator ascuns"

Dacă, în practică, se vinde și către **persoane fizice care nu acționează profesional** (ex. un student, un
curios), pentru **acei** clienți s-ar aplica **OUG 34/2014** (informare + drept de retragere de 14 zile,
cu excepția conținutului digital început cu consimțământ expres și renunțare la retragere). **Recomandare:**

- Restrânge vânzarea la profesioniști (ex. cerând **legitimația ANEVAR** la activare — deja prevăzut în
  spec) și declară în Termeni că serviciul se adresează **exclusiv profesioniștilor**.
- Dacă totuși se admit consumatori, pregătește un **set B2C** (informări complete + formular de retragere +
  clauza de renunțare la retragere pentru conținut digital, art. 16 lit. m OUG 34/2014). **[DE COMPLETAT:
  decizie comercială — pur B2B sau mixt.]**

### 6.3. Informări precontractuale minime (oricum recomandate)

Indiferent de calificare, înainte de plată trebuie afișate clar: **identitatea furnizorului** (denumire,
CUI, sediu, contact), **prețul total** (cu/fără TVA), **caracteristicile serviciului**, **durata și
reînnoirea** abonamentului, **modul de denunțare**, **cerințele tehnice** (Windows, conexiune pentru AI).
→ Acoperite în Termeni (doc. 10) și pe pagina de checkout.

---

## 7. AI Act (Reg. (UE) 2024/1689)

### 7.1. Clasificarea sistemului

Aplicația încorporează un **sistem de IA** (componenta narativă bazată pe LLM). Analiza de risc:

- **Nu** este o practică **interzisă** (Titlul II / art. 5): nu face scoring social, manipulare, etc.
- **Risc ridicat (Anexa III)?** Punctul sensibil este **evaluarea bonității / accesul la credit**
  (Anexa III, pct. 5 lit. b vizează IA folosită pentru a **evalua bonitatea persoanelor fizice sau pentru
  a stabili scorul de credit**). **Distincție-cheie de argumentat:** produsul **nu evaluează bonitatea
  debitorului** și **nu acordă/refuză credit**; el asistă la **evaluarea valorii unui imobil** (garanție).
  Decizia de creditare aparține băncii, pe baza raportului semnat de evaluator. Prin urmare, la o citire
  rezonabilă, **componenta AI nu intră** în Anexa III pct. 5(b). **[DE CONFIRMAT: avocat — încadrarea,
  ținând cont și de eventuale ghiduri ale Comisiei/AI Office.]**
- Concluzie preliminară: **risc limitat / minim** — sistem de IA care **interacționează** și **generează
  text**, cu **obligații de transparență** (art. 50), nu obligații de sistem de risc ridicat.

### 7.2. Obligații de transparență (art. 50)

- Utilizatorii (evaluatorii) trebuie să **știe** că interacționează cu/folosesc un sistem de IA → afișaj
  clar „text generat de IA", deja prezent ca principiu („Generează AI").
- Conținutul **generat artificial** (text) ar trebui să poată fi recunoscut ca atare în relația profesională;
  în context, evaluatorul **integrează și își asumă** textul în raportul propriu — disclaimerul (doc. 14)
  trebuie să clarifice că outputul AI este un **draft asistiv**.

### 7.3. Calendar și roluri

- AI Act se aplică **etapizat** (interdicțiile primele, obligațiile de transparență și cele pentru sisteme
  de risc ridicat ulterior, conform calendarului regulamentului). **[DE COMPLETAT: avocat — termenele
  aplicabile la data lansării.]**
- Roluri: furnizorul aplicației este, cel mai probabil, **„furnizor" (provider)** al sistemului IA integrat
  (sau „deployer" pentru modelul terț, în funcție de arhitectură). De clarificat raportul cu **furnizorul
  modelului fundamental (GPAI)**, care are propriile obligații. **[DE CONFIRMAT: avocat.]**

---

## 8. AML — granița furnizor software vs. entitate raportoare

- **Entitatea raportoare** în sensul **Legii nr. 129/2019** este **evaluatorul autorizat** (vezi
  `docs/audit-aml-pentru-jurist.md`, §1; art. 5). **Furnizorul software NU este entitate raportoare** prin
  simplul fapt că oferă un instrument de asistență AML — el nu prestează servicii din sfera art. 5 și nu
  intră în relația de afaceri cu clientul final.
- Modulul AML **asistă** (generează drafturi de norme interne, fișe KYC, indicatori, RTN/RTS) și **nu**
  înlocuiește obligațiile evaluatorului. Aplicația **nu** face screening live PEP/sancțiuni (liste
  demonstrative injectabile) și afișează avertismente.
- **Granița (de afirmat în disclaimer + EULA + Termeni):** drafturile AML sunt **modele de personalizat**;
  decizia de a raporta/nota o tranzacție suspectă, screening-ul în baze oficiale, respectarea pragurilor și
  a termenelor, precum și interdicția de tipping-off (art. 38) sunt **răspunderea evaluatorului**. Furnizorul
  **nu** răspunde pentru neraportare/raportare eronată.
- Întrebările de fond AML (prag numerar 10.000 € vs. 3.000 € la tranzacții ocazionale; screening API
  obligatoriu sau trimitere la surse + bifă; persistența RTN/RTS vs. tipping-off; formulări anti-„neglijență
  gravă") rămân de decis de **consultantul AML** — vezi `docs/audit-aml-pentru-jurist.md` §3. Acestea
  privesc **corectitudinea produsului** pentru evaluator, dar **nu** schimbă faptul că furnizorul nu este
  entitate raportoare.

---

## 9. Răspundere pentru defecte software, telemetrie și loguri de crash

### 9.1. Defecte software

- Produsul se livrează „**ca atare**" (as is), cu garanțiile legale minime imperative care nu pot fi
  înlăturate. Se exclud garanțiile implicite în limita permisă de lege; se promit, totuși, **disponibilitate
  rezonabilă** a gateway-ului și remedieri prin update-uri (fără SLA ferm la lansare). **[DE COMPLETAT:
  nivel de serviciu / SLA dacă se promite vreunul.]**
- Atenție la noua **Directivă (UE) 2024/2853 privind răspunderea pentru produse defecte** (care include
  explicit software-ul) și la propunerile privind răspunderea în materie de IA — pot impune un regim mai
  strict. **[DE CONFIRMAT: avocat — impactul la data lansării și măsura în care răspunderea poate fi
  limitată față de profesioniști.]**

### 9.2. Telemetrie și loguri de crash — din nou GDPR

- **Punct de risc real:** orice **telemetrie**, **raport de crash** sau **log** colectat **de pe
  calculatorul evaluatorului** poate conține **date cu caracter personal** (ale evaluatorului și, în cel mai
  rău caz, fragmente din dosar — căi de fișiere cu nume de client, stack traces cu date). Aici furnizorul
  redevine **operator** (sau împuternicit, după caz) și are obligații GDPR.
- **Reguli recomandate:**
  - **Implicit dezactivat** sau **opt-in** explicit pentru telemetrie; minimizare strictă a câmpurilor.
  - **Niciun conținut de dosar** în loguri trimise online; scrubbing de PII din stack traces și căi.
  - Gateway-ul loghează **IP/oră** pentru anti-abuz (interes legitim) — de documentat scopul, retenția și
    informarea în Politica de confidențialitate (doc. 11).
  - Datele de **cont/sesiune/facturare** — operator furnizorul; bază: contract (art. 6(1)(b)) + interes
    legitim anti-abuz (art. 6(1)(f)).
- **[DE COMPLETAT: lista exactă a datelor de telemetrie/crash colectate, dacă vreuna, + retenția.]** Dacă
  **nu** se colectează telemetrie online, acest risc dispare aproape complet — recomandare: **menține
  telemetria minimă/locală** cât timp e posibil.

---

## 10. Comerț electronic, facturare și TVA (obligații ale furnizorului)

- **Comerț electronic — Legea nr. 365/2002** (transpune Directiva 2000/31/CE): obligații de **informare**
  (identitate furnizor, date de contact, CUI, prețuri clare), reguli privind comunicările comerciale și
  încheierea contractelor prin mijloace electronice. → Acoperite în Termeni + pagina de vânzare.
- **Facturare/TVA — abonament digital:**
  - Serviciul = **serviciu prestat electronic** (TBE). Pentru clienți **din România**: facturare cu TVA RO
    conform Codului fiscal; **e-Factura** poate fi aplicabilă în relațiile B2B conform reglementărilor în
    vigoare. **[DE COMPLETAT: contabil — regim TVA, cote, e-Factura, plafon de scutire.]**
  - Pentru clienți **din alte state UE**: la servicii electronice se aplică regula locului unde este stabilit
    **beneficiarul**; pentru B2C intra-UE poate deveni relevant regimul **OSS** (One Stop Shop); pentru B2B
    intra-UE se aplică **taxarea inversă**. **[DE COMPLETAT: contabil — dacă se vinde în UE, înregistrare
    OSS + praguri.]**
  - **Stripe** ca procesator de plăți nu preia obligațiile fiscale ale furnizorului; furnizorul rămâne
    responsabil de emiterea facturilor și raportarea TVA.
- **Obligații fiscale generale ale furnizorului:** formă de organizare (PFA/SRL), înregistrare fiscală,
  eventual înregistrare în scop de TVA, contabilitate. **[DE COMPLETAT: structura juridică a furnizorului +
  consultanță contabilă.]**

---

## 11. Documentație GDPR necesară la furnizor (registru, DPIA, breșe)

- **Registrul activităților de prelucrare (art. 30):** pentru rolul de operator (conturi/telemetrie) și,
  acolo unde e cazul, pentru rolul de împuternicit (gateway AI).
- **Analiză art. 25 / mini-DPIA:** arhitectura „local-first + doar text anonimizat la AI" merită documentată
  ca măsură de protecție din concepție; un **DPIA** complet probabil **nu** este obligatoriu (prelucrarea
  online e minimă și pseudonimizată), dar o **evaluare a necesității DPIA** (screening) trebuie consemnată.
  **[DE CONFIRMAT: avocat.]**
- **Procedură de breșă (art. 33–34):** cine notifică, în ce termen (72h la ANSPDCP), cum se asistă
  evaluatorul-operator dacă breșa atinge felia de împuternicit.
- **Punct de contact pentru protecția datelor / eventual DPO:** un **DPO** probabil **nu este obligatoriu**
  (nu pare prelucrare la scară largă de categorii speciale), dar un **e-mail dedicat** (ex.
  `confidentialitate@[domeniu]`) este necesar. **[DE COMPLETAT: date de contact.]**

---

## 12. Alte aspecte de avut în vedere

- **ANEVAR — reguli privind instrumente comerciale terțe / metodologie:** verifică dacă există norme
  deontologice care restricționează folosirea unor tool-uri automate sau care impun avertizări în raport.
  **[DE VERIFICAT cu ANEVAR / avocat.]**
- **Asigurare de răspundere profesională:** rămâne a evaluatorului; furnizorul poate evalua o **asigurare
  proprie** (RC profesională / E&O) pentru produsul software.
- **Conturi Google/Stripe/Supabase:** fiecare are propriii termeni și DPA — furnizorul devine **operator**
  față de datele de cont și trebuie să încheie/accepte **DPA-urile** cu acești procesatori (sub-împuterniciți
  ai furnizorului pentru datele de cont). **[DE COMPLETAT: listă procesatori + DPA-uri.]**
- **Localizarea datelor de cont:** Supabase/Stripe pot procesa în afara SEE → SCC/DPF, de documentat în
  Politica de confidențialitate.

---

## 13. Matrice de riscuri (probabilitate × impact) și acțiuni obligatorii înainte de lansare

**Legendă:** Probabilitate (P) și Impact (I): **R** = redus, **M** = mediu, **Î** = înalt. Nivel de risc =
combinația (orientativ).

| # | Risc | P | I | Nivel | Acțiune obligatorie înainte de lansare |
|---|------|---|---|-------|----------------------------------------|
| R1 | Lipsa DPA furnizor↔evaluator pentru felia AI | Î | Î | **Înalt** | Semnătură DPA (doc. 13) la onboarding; clarificare rol anonim/pseudonim cu avocatul. |
| R2 | Transfer LLM în afara SEE fără mecanism valid | M | Î | **Înalt** | Alegere LLM cu SCC/DPF sau procesare UE; TIA; trecere în Anexa 2 DPA. |
| R3 | Re-identificare din text „anonimizat" trimis la AI | M | M | **Mediu-Înalt** | Întărire anonimizare (localitate/indicii unice); documentare risc rezidual; opțiune offline promovată. |
| R4 | Răspundere pentru valoarea evaluată / output AI eronat | M | Î | **Înalt** | Disclaimer profesional (doc. 14) + clauze limitare în EULA/Termeni; afișare „draft AI de verificat". |
| R5 | Redistribuirea standardelor ANEVAR/SEV (drept de autor) | M | Î | **Înalt** | Eliminarea textelor integrale din `.exe`; doar referințe/parafrazări; verificare licență/poziție ANEVAR. |
| R6 | Telemetrie/crash cu PII din dosar trimise online | M | M | **Mediu** | Telemetrie opt-in/minimă; scrubbing PII; fără conținut de dosar în loguri. |
| R7 | Încadrare AI Act risc ridicat (credit) tratată greșit | R | Î | **Mediu** | Argument documentat „evaluare imobil ≠ bonitate"; confirmare avocat; transparență art. 50. |
| R8 | „Consumator ascuns" → OUG 34/2014 neaplicată | M | M | **Mediu** | Restrângere la profesioniști (legitimație ANEVAR); clauză „doar B2B"; set B2C pregătit dacă se admit consumatori. |
| R9 | TVA/facturare/e-Factura/OSS neconforme | M | M | **Mediu** | Consultanță contabilă; configurare facturare RO + UE înainte de prima vânzare. |
| R10 | AML: produsul induce evaluatorul în eroare (praguri/screening) | M | Î | **Mediu-Înalt** | Validare AML (audit dedicat) + disclaimere clare „asistență, nu substitut"; granița furnizor. |
| R11 | Lipsă informări precontractuale / Termeni / Politică | M | M | **Mediu** | Publicarea doc. 10–14 validate înainte de checkout. |
| R12 | Răspundere pentru produse defecte (Dir. 2024/2853 software) | R | M | **Mediu** | Garanții „as is" în limita legii; monitorizare termene transpunere; confirmare avocat. |

### Checklist „MUST-HAVE" înainte de lansare

- [ ] DPA (doc. 13) validat de avocat și integrat în onboarding (acceptare electronică).
- [ ] Provider LLM final ales, cu mecanism de transfer (SCC/DPF/UE) și politică „no training" confirmate.
- [ ] Termeni (doc. 10), Politică de confidențialitate (doc. 11), EULA (doc. 12), Disclaimer (doc. 14) —
      validate de avocat și publicate.
- [ ] Eliminarea textelor integrale ale standardelor ANEVAR/SEV din build-ul livrat; doar referințe.
- [ ] Poziția față de ANEVAR clarificată (licență/afiliere/disclaimer „neavizat").
- [ ] Regim TVA / facturare RO (+ OSS dacă UE) configurat (contabil).
- [ ] Telemetrie: decizie clară (minimă/opt-in/local), fără PII de dosar; documentat în Politică.
- [ ] Registru art. 30 + procedură de breșă + e-mail de contact pentru protecția datelor.
- [ ] Validare AML (audit dedicat) — vezi `docs/audit-aml-pentru-jurist.md`.

---

## 14. Ce TREBUIE neapărat decis de un avocat real (nu poate fi tranșat intern)

1. **Calificarea textului la AI** ca **anonim** (în afara GDPR) vs. **pseudonim** (în GDPR) — determină dacă
   DPA este obligatoriu sau doar recomandat.
2. **Mecanismul de transfer internațional** corect pentru providerul LLM ales și redactarea/validarea SCC.
3. **Calibrarea clauzelor de limitare a răspunderii** (plafon, excluderi) astfel încât să reziste testului
   de bună-credință / clauze abuzive și limitelor imperative.
4. **Încadrarea exactă sub AI Act** (risc limitat vs. eventuale atingeri ale Anexei III) și rolul (provider/
   deployer) + termenele aplicabile la lansare.
5. **Drept de autor ANEVAR/SEV** și **necesitatea unei licențe/acord cu ANEVAR** pentru un produs comercial
   care implementează metodologia și folosește denumirile.
6. **Validarea AML** (praguri, screening, tipping-off, formulări anti-culpă gravă) — consultant specializat.
7. **Regimul fiscal** (TVA, e-Factura, OSS) — contabil/fiscalist.

---

## 15. Lista documentelor produse (acest pachet)

| Fișier | Conținut |
|---|---|
| `00-evaluare-juridica-RO.md` | Acest document — evaluarea de risc. |
| `10-termeni-si-conditii-DRAFT.md` | Termeni și Condiții de utilizare (RO). |
| `11-politica-confidentialitate-DRAFT.md` | Politica de confidențialitate GDPR a furnizorului. |
| `12-acord-licenta-EULA-DRAFT.md` | EULA cu limitarea răspunderii + interdicția partajării licenței. |
| `13-DPA-acord-prelucrare-DRAFT.md` | Acord de prelucrare (art. 28) + anexa sub-împuterniciților. |
| `14-disclaimer-profesional-DRAFT.md` | Disclaimerul profesional (instrument de asistență). |

*Documente conexe existente:* `docs/gdpr/politica-prelucrare-MODEL.md` și `formular-consimtamant-MODEL.md`
(pentru evaluator ca operator, față de clienții săi); `docs/audit-aml-pentru-jurist.md` (validare AML).

---

*Sfârșit document. Reamintire: DRAFT — necesită validarea unui avocat din România. Nu constituie consultanță juridică.*
