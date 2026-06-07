# Acord de prelucrare a datelor cu caracter personal (DPA) — art. 28 GDPR

> **DRAFT — necesită validarea unui avocat din România înainte de utilizare. Nu constituie consultanță juridică.**

> Acest Acord se aplică **exclusiv** feliei în care Furnizorul prelucrează date **în numele** evaluatorului:
> **textul anonimizat** transmis componentei AI (gateway → LLM). Pentru datele păstrate **local** pe
> echipamentul evaluatorului, Furnizorul **nu are acces** și **nu este nici operator, nici împuternicit**.
> Pentru datele de cont/abonament ale evaluatorului, Furnizorul este **operator** (vezi Politica de
> confidențialitate), nu împuternicit.

**Încheiat între:**

- **Operatorul:** [DE COMPLETAT: evaluatorul / cabinetul — denumire], CUI/CNP [DE COMPLETAT], sediu
  [DE COMPLETAT], e-mail [DE COMPLETAT] — în calitate de **operator** de date („Operatorul");
- **Persoana împuternicită (Furnizorul):** [DE COMPLETAT: denumire firmă/PFA], CUI [DE COMPLETAT], sediu
  [DE COMPLETAT], e-mail [DE COMPLETAT] — în calitate de **persoană împuternicită** („Împuternicitul").

**Versiune:** 0.1 (draft) · **Data:** [DE COMPLETAT]. Se acceptă electronic la activarea contului și
constituie anexă la Termeni/EULA.

---

## Art. 1. Obiect și natura prelucrării

1.1. Împuternicitul prelucrează date cu caracter personal **în numele și pe seama** Operatorului, **exclusiv**
în scopul furnizării **componentei AI** (generarea de text narativ pe baza textului transmis de Aplicație),
prin gateway-ul propriu și prin furnizorul de model de limbaj (LLM) menționat în **Anexa 2**.

1.2. **Natura prelucrării:** recepție, transmitere către sub-împuternicitul LLM, procesare temporară și
returnare a rezultatului. Împuternicitul **nu** utilizează datele în scopuri proprii.

1.3. **Caracter limitat al datelor:** Aplicația **anonimizează** (înlocuiește identificatorii direcți —
nume, adresă, CF, cadastral — cu marcaje) **înainte** de transmitere; demascarea se face **local**, la
Operator. Părțile recunosc că, în funcție de conținut, textul poate avea caracter **pseudonimizat** și îl
tratează prudent ca date cu caracter personal în sfera GDPR. **[DE CONFIRMAT: avocat — dacă, în concret,
textul este anonim, prezentul DPA rămâne aplicabil cu titlu de bună practică.]**

## Art. 2. Durata

2.1. Prezentul Acord se aplică pe **durata** furnizării componentei AI (durata contului/abonamentului) și
încetează odată cu aceasta, sub rezerva obligațiilor care supraviețuiesc (ștergere/returnare, confidențialitate).

## Art. 3. Tipuri de date și categorii de persoane vizate

- **Categorii de persoane vizate:** persoanele menționate în textul transmis — de regulă **proprietari /
  clienți ai evaluatorului / debitori ipotecari** și, eventual, terți menționați.
- **Tipuri de date (după anonimizare):** fragmente de text descriptiv despre imobil și context, **fără**
  identificatori direcți (care sunt înlocuiți cu marcaje). Nu se transmit, prin design, CNP, nume, adresă
  exactă sau numere CF/cadastrale în clar.
- **Categorii speciale (art. 9):** **nu** se intenționează prelucrarea de categorii speciale; Operatorul se
  obligă să **nu** introducă astfel de date în textul trimis la AI.

## Art. 4. Obligațiile Împuternicitului (art. 28(3))

Împuternicitul:

a) prelucrează datele **numai pe baza instrucțiunilor documentate** ale Operatorului (prezentul Acord,
Termenii, configurarea Aplicației); dacă o obligație legală impune altă prelucrare, informează Operatorul în
prealabil, cu excepția interdicției legale;

b) asigură **confidențialitatea** (persoanele autorizate s-au angajat la confidențialitate sau au obligație
legală);

c) implementează **măsuri de securitate** adecvate (art. 32) — vezi **Anexa 1**;

d) respectă condițiile de angajare a **sub-împuterniciților** (Art. 5);

e) **asistă** Operatorul, în măsura posibilului, pentru a răspunde **cererilor persoanelor vizate**
(art. 12–23);

f) **asistă** Operatorul privind **securitatea, notificarea breșelor (art. 33–34) și DPIA (art. 35–36)**,
ținând cont de natura prelucrării și de informațiile disponibile;

g) la încetare, **șterge sau returnează** datele și șterge copiile existente, cu excepția păstrării impuse de
lege;

h) pune la dispoziția Operatorului **informațiile** necesare pentru a demonstra conformitatea și permite
**audituri/inspecții** rezonabile (Art. 7).

## Art. 5. Sub-împuterniciți (art. 28(2) și (4))

5.1. Operatorul acordă o **autorizare generală** Împuternicitului de a angaja sub-împuterniciți pentru
furnizarea componentei AI (în special **furnizorul de LLM** și infrastructura de găzduire), listați în
**Anexa 2**.

5.2. Împuternicitul impune sub-împuterniciților, prin contract, **aceleași obligații** de protecție a datelor
ca cele din prezentul Acord (art. 28(4)) și rămâne **răspunzător** față de Operator pentru îndeplinirea
acestora.

5.3. La **schimbarea/adăugarea** unui sub-împuternicit, Împuternicitul **notifică în prealabil** Operatorul
(prin Aplicație/e-mail) și acordă un termen rezonabil pentru **opoziție** motivată. În caz de opoziție
nesoluționabilă, Operatorul poate înceta utilizarea componentei AI (componenta locală offline rămânând
disponibilă).

## Art. 6. Transfer internațional

6.1. Dacă un sub-împuternicit (ex. LLM) prelucrează **în afara SEE**, transferul se face pe baza unui
**mecanism legal valid** (Clauze Contractuale Standard / EU-US Data Privacy Framework / procesare în UE),
precizat în **Anexa 2**. **[DE COMPLETAT: mecanismul aplicabil providerului ales.]**

## Art. 7. Audit

7.1. Împuternicitul pune la dispoziție, la cerere rezonabilă și cu preaviz, **documentația/atestările**
relevante (politici de securitate, certificări, DPA-uri ale sub-împuterniciților). Auditurile la fața locului
se realizează doar în condiții rezonabile, fără a afecta securitatea altor clienți, eventual prin terț
independent. [DE COMPLETAT: detalii procedură audit.]

## Art. 8. Notificarea breșelor

8.1. Împuternicitul notifică Operatorul **fără întârziere nejustificată** după ce ia cunoștință de o breșă
care afectează datele prelucrate în numele Operatorului, furnizând informațiile disponibile pentru ca
Operatorul să-și poată îndeplini obligațiile (art. 33–34).

## Art. 9. Răspundere

9.1. Răspunderea părților pentru încălcarea GDPR urmează **art. 82 GDPR** și legislația aplicabilă. Limitările
de răspundere din Termeni/EULA se aplică în măsura permisă de lege și **fără** a înlătura răspunderea
imperativă față de persoanele vizate.

## Art. 10. Dispoziții finale

10.1. În caz de conflict între prezentul Acord și Termeni/EULA **privind prelucrarea datelor**, prevalează
prezentul Acord. Legea aplicabilă: **legea română** și GDPR. Modificările se comunică conform Termenilor.

---

## Anexa 1 — Măsuri tehnice și organizatorice (art. 32)

- **Anonimizare la sursă:** înlocuirea identificatorilor direcți cu marcaje **înainte** de transmitere;
  demascare exclusiv locală.
- **Criptare în tranzit:** comunicații HTTPS/TLS între Aplicație, gateway și sub-împuternicit.
- **Minimizare:** se transmite doar textul necesar generării; fără stocare inutilă la Împuternicit.
- **Control acces:** acces restricționat la gateway pe bază de autentificare; chei API păstrate ca secrete la
  Împuternicit, **nu** în Aplicația livrată.
- **Separarea rolurilor:** datele dosarului rămân local la Operator; Împuternicitul nu are acces la ele.
- **Jurnalizare de securitate:** loguri minime (IP/oră) pentru prevenirea abuzului, cu retenție limitată.
- **[DE COMPLETAT: certificări/standarde aplicabile, ex. ISO 27001 al sub-împuterniciților; backup; gestionarea
  incidentelor.]**

## Anexa 2 — Lista sub-împuterniciților

| Sub-împuternicit | Rol / serviciu | Localizare prelucrare | Mecanism de transfer (dacă în afara SEE) | Retenție / antrenare |
|---|---|---|---|---|
| [DE COMPLETAT: furnizor LLM — ex. Perplexity / Anthropic] | Generare text narativ (AI) din text anonimizat | [DE COMPLETAT: UE/SUA] | [DE COMPLETAT: SCC / DPF / N/A] | [DE COMPLETAT: politica de retenție; „fără antrenare" / opt-out] |
| [DE COMPLETAT: Supabase] | Găzduire gateway, bază sesiuni/cotă | [DE COMPLETAT] | [DE COMPLETAT] | [DE COMPLETAT] |
| [DE COMPLETAT: cloud/găzduire] | Infrastructură | [DE COMPLETAT] | [DE COMPLETAT] | [DE COMPLETAT] |

> Notă: furnizorii care țin **exclusiv** de relația cu evaluatorul ca **persoană vizată** (ex. procesatorul de
> plăți, autentificarea) sunt sub-împuterniciți ai Furnizorului **în rolul său de operator** (Politica de
> confidențialitate), nu în cadrul prezentului DPA.

---

*Reamintire: DRAFT — necesită validarea unui avocat din România. Nu constituie consultanță juridică.*
