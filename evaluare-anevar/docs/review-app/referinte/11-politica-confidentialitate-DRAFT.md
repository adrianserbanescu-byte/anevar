# Politică de confidențialitate (protecția datelor cu caracter personal)

> **DRAFT — necesită validarea unui avocat din România înainte de utilizare. Nu constituie consultanță juridică.**

> **Atenție la domeniul de aplicare.** Această Politică descrie modul în care **Furnizorul** prelucrează
> datele **Utilizatorilor (evaluatorii)** — conturi, abonamente, sesiuni, telemetrie minimă — și felia în care
> Furnizorul acționează ca **persoană împuternicită** pentru textul anonimizat trimis componentei AI.
> Pentru datele **clienților evaluatorului** (proprietari, debitori), **operatorul este evaluatorul**, iar
> informarea persoanelor vizate se face de către evaluator (vezi `docs/gdpr/politica-prelucrare-MODEL.md`).

**Operator (pentru datele Utilizatorilor):** [DE COMPLETAT: denumire firmă/PFA], CUI [DE COMPLETAT], sediu
[DE COMPLETAT], e-mail protecția datelor: [DE COMPLETAT: ex. confidentialitate@domeniu].

**Versiune:** 0.1 (draft) · **Data:** [DE COMPLETAT].

---

## 1. Cine suntem și ce roluri avem

1.1. Prelucrarea se face conform **Regulamentului (UE) 2016/679 (GDPR)** și legislației naționale aplicabile.

1.2. **Roluri (rezumat):**

| Categorie de date | Rolul Furnizorului | Temei principal |
|---|---|---|
| Cont, autentificare, abonament, sesiuni, facturare, telemetrie minimă | **Operator** | Contract (art. 6(1)(b)); interes legitim anti-abuz (art. 6(1)(f)); obligație legală fiscală (art. 6(1)(c)) |
| **Text anonimizat** trimis componentei AI (gateway → LLM) | **Persoană împuternicită** a evaluatorului-operator | Conform DPA (art. 28); prelucrare pe baza instrucțiunilor operatorului |
| Datele dosarului păstrate **local** pe calculatorul evaluatorului | **Niciun rol** (Furnizorul nu are acces) | — |

## 2. Ce date prelucrăm (despre Utilizatori)

- **Date de cont și identificare:** nume, adresă de e-mail, identificatorul contului Google (la
  autentificarea prin Google) sau e-mailul pentru „magic link"; eventual **numărul legitimației ANEVAR**
  [DE COMPLETAT: dacă se colectează].
- **Date de abonament și facturare:** treaptă, status, perioadă, identificatori la procesatorul de plăți,
  date necesare facturării (denumire PFA/PJ, CUI, adresă). Datele complete ale cardului sunt prelucrate de
  procesatorul de plăți, **nu** de Furnizor.
- **Date de sesiune și utilizare a gateway-ului:** identificatori de sesiune, dispozitiv (hash), **adresă IP
  și marca temporală** a apelurilor (pentru securitate și prevenirea abuzului), contoare de consum (cota de
  rapoarte).
- **Text anonimizat trimis la AI:** fragmente de text din care identificatorii direcți (nume, adresă, CF,
  cadastral) au fost **înlocuiți cu marcaje** de către Aplicație înainte de transmitere. Furnizorul prelucrează
  acest text **doar** pentru a returna rezultatul AI.
- **Telemetrie/diagnostic (dacă este activată):** [DE COMPLETAT: lista exactă — ex. versiune app, tip eroare].
  Prin design, telemetria este **minimă** și **nu** include conținutul dosarelor. [DE COMPLETAT: dacă
  telemetria este opt-in, dezactivată implicit, sau inexistentă.]

> **Nu colectăm intenționat** și nu solicităm date cu caracter personal ale clienților evaluatorului către
> serverele noastre. Componenta AI primește **text anonimizat**; demascarea se face exclusiv **local**.

## 3. Scopurile prelucrării

- Crearea și administrarea **contului** și autentificarea.
- Furnizarea **abonamentului**, **metrarea** consumului AI, **facturarea**.
- **Securitatea** Serviciului, prevenirea fraudei/abuzului, aplicarea licenței (max. 2 sesiuni).
- Furnizarea componentei **AI** (procesarea textului anonimizat prin gateway către LLM), ca persoană
  împuternicită.
- **Asistență** și comunicări de serviciu (notificări tehnice, modificări de termeni).
- Respectarea **obligațiilor legale** (fiscale, contabile).
- [DE COMPLETAT: marketing/newsletter — doar cu temei valid, de regulă consimțământ sau interes legitim B2B,
  cu drept de opoziție.]

## 4. Temeiurile legale

- **Executarea contractului** (art. 6(1)(b)): cont, abonament, furnizarea Serviciului.
- **Obligație legală** (art. 6(1)(c)): facturare, contabilitate.
- **Interes legitim** (art. 6(1)(f)): securitate, prevenirea abuzului, îmbunătățirea Serviciului, comunicări
  de serviciu — cu evaluarea echilibrului de interese.
- **Consimțământ** (art. 6(1)(a)): acolo unde se aplică (ex. telemetrie opt-in, marketing), revocabil oricând.
- Pentru felia de **persoană împuternicită**, temeiul prelucrării aparține **operatorului** (evaluatorul);
  Furnizorul acționează pe baza **instrucțiunilor documentate** din DPA.

## 5. Componenta AI și sub-împuterniciții (transfer internațional)

5.1. Pentru a genera textul narativ, gateway-ul Furnizorului transmite **textul anonimizat** către un
furnizor de model de limbaj (LLM): **[DE COMPLETAT: nume provider LLM — ex. Perplexity / Anthropic]**.

5.2. Acest furnizor LLM acționează ca **sub-împuternicit**. Furnizorul depune eforturi pentru a selecta un
sub-împuternicit care oferă garanții adecvate (securitate, politică „**fără antrenare**" pe datele transmise,
retenție limitată). **[DE COMPLETAT: politica de retenție și de antrenare a providerului ales.]**

5.3. **Transfer în afara SEE:** dacă sub-împuternicitul procesează în afara Spațiului Economic European
(ex. SUA), transferul se face pe baza unui mecanism legal valid: **[DE COMPLETAT: Clauze Contractuale
Standard (SCC) / EU-US Data Privacy Framework / procesare în UE]**. La cerere, se pot furniza informații
despre garanțiile aplicate.

5.4. **Alternativa fără transfer:** componenta locală (fără AI) funcționează **complet offline** și **nu**
implică niciun transfer extern — recomandată pentru cazuri sensibile.

## 6. Alți destinatari / persoane împuternicite ale Furnizorului

Furnizorul folosește prestatori care pot prelucra date în numele său (operator → împuterniciții săi):

- **[DE COMPLETAT: Supabase]** — autentificare, bază de date conturi/sesiuni/cotă.
- **[DE COMPLETAT: Google]** — autentificare (Google Sign-In).
- **[DE COMPLETAT: Stripe]** — procesare plăți și facturare.
- **[DE COMPLETAT: furnizor de e-mail]** — comunicări de serviciu / magic link.
- **[DE COMPLETAT: găzduire/cloud]**.

Cu fiecare se încheie/acceptă un **acord de prelucrare (DPA)**; unii pot procesa în afara SEE, cu mecanisme
de transfer corespunzătoare. Lista actualizată se poate obține la cerere.

## 7. Perioada de păstrare

- **Date de cont:** pe durata contului + o perioadă rezonabilă ulterioară [DE COMPLETAT].
- **Date de facturare/contabile:** conform termenelor legale fiscale aplicabile [DE COMPLETAT: ex. 10 ani].
- **Loguri de securitate (IP/oră, sesiuni):** [DE COMPLETAT: ex. 6–12 luni].
- **Text anonimizat la AI:** nu este stocat de Furnizor mai mult decât necesar procesării; retenția la
  sub-împuternicit depinde de politica acestuia [DE COMPLETAT].
- **Telemetrie:** [DE COMPLETAT].

## 8. Drepturile persoanelor vizate

Conform GDPR, aveți dreptul la: **acces**, **rectificare**, **ștergere**, **restricționare**, **opoziție**,
**portabilitate**, **retragerea consimțământului** (unde se aplică) și de a **nu** fi supus unei decizii
automate cu efecte semnificative. Cererile se adresează la: **[DE COMPLETAT: e-mail protecția datelor]**.

Aveți dreptul de a depune **plângere** la **Autoritatea Națională de Supraveghere a Prelucrării Datelor cu
Caracter Personal (ANSPDCP)**, [DE COMPLETAT: date de contact ANSPDCP].

> Notă: dacă datele privesc clientul **unui evaluator** (proprietar/debitor), cererea trebuie adresată
> **evaluatorului-operator**; Furnizorul, ca împuternicit, va asista operatorul conform DPA.

## 9. Securitate

9.1. Furnizorul aplică măsuri tehnice și organizatorice adecvate (art. 32): comunicații criptate (HTTPS),
control al accesului, principiul **local-first** (datele dosarului rămân pe echipamentul Utilizatorului),
**anonimizarea** textului înainte de transmiterea la AI, minimizarea telemetriei.

9.2. În caz de **breșă de securitate**, Furnizorul respectă obligațiile de notificare aplicabile
(art. 33–34) și asistă operatorul-evaluator pentru felia de împuternicit.

## 10. Decizii automate și profilare

10.1. Furnizorul **nu** ia decizii automate cu efecte juridice semnificative asupra persoanelor vizate.
Componenta AI **generează text asistiv**, sub controlul evaluatorului (om în buclă); ea nu produce o decizie
automată în sensul art. 22.

## 11. Modificări ale Politicii

11.1. Politica poate fi actualizată; versiunea în vigoare este publicată în Aplicație/pe site, cu data
ultimei modificări. Modificările substanțiale se comunică Utilizatorilor.

## 12. Contact

Pentru orice întrebare privind protecția datelor: **[DE COMPLETAT: e-mail]**, **[DE COMPLETAT: adresă]**.
[DE COMPLETAT: dacă există DPO — date de contact DPO.]

---

*Reamintire: DRAFT — necesită validarea unui avocat din România. Nu constituie consultanță juridică.*
