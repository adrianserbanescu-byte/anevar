# Council Review Result

**Chairman:** google/gemini-3.1-pro-preview

## Final Synthesized Answer

Acesta este raportul consolidat al consiliului de evaluare (LLM Council). Am sintetizat cele mai bune perspective metodologice, tehnice și juridice, concentrându-ne pe solicitarea ta principală: **să identificăm zonele de tip „așa nu se face” și riscurile care garantează respingerea raportului de către o bancă sau care atrag răspundere legală**.

Din punct de vedere ingineresc, arhitectura tehnică (FastAPI + Jinja + SQLite offline, 92% coverage) este excelentă și perfect pliată pe profilul evaluatorului. Însă, intersecția dintre matematică, norme bancare (GEV 520) și legislația AML ascunde **câteva vulnerabilități critice** pe care trebuie să le rezolvi înainte de o lansare asumată.

Iată critica detaliată, structurată pe priorități.

---

### I. Metodologie de Evaluare (Risc major de respingere de la Bănci)

Băncile au departamente de verificare extrem de rigide, conduse de reguli și praguri automate (ex. ajustări maxime admise). Următoarele elemente vor duce la respingerea automată a rapoartelor:

**1. Grila pentru casă/apartament: Lucrul pe PREȚ TOTAL (Red Flag Critic) — AȘA NU**
*   **Problema:** Să faci grila de comparație pentru construcții pe *preț total*, tratând diferența de arie utilă drept ajustare valorică liniară (Δmp × preț unitar), este complet în afara uzanțelor bancare pentru rezidențial.
*   **De ce pică la bancă:** În România, rapoartele pentru garantare GEV 520 pe rezidențial se fac **aproape exclusiv pe EUR/mp**. Dacă lucrezi pe preț total, ajustarea valorică pentru o diferență de 30 mp va genera un procent de ajustare uriaș. Băncile au limite prudențiale (ex. max 15% pe o linie, max 30-40% brut total). Abordarea pe preț total distorsionează aceste procente și forțează respingerea automată. Mai mult, piața nu funcționează perfect liniar (un mp în plus la 120mp valorează mai puțin decât un mp în plus la 50mp).
*   **Soluția obligatorie:** Grila de construcții trebuie să transforme prețurile în EUR/mp. Ajustările se aplică procentual asupra prețului unitar, iar valoarea finală se obține înmulțind prețul unitar rezultat cu suprafața subiectului.

**2. Grila de teren: Selecția doar pe „Ajustarea la proprietate” — AȘA NU**
*   **Problema:** Dacă criteriul de selecție ignoră etapa de tranzacție, algoritmul poate alege o „ofertă” veche, supraevaluată masiv, care a suferit o ajustare de -30% la condiții de tranzacție/piață, doar pentru că fizic seamănă cu subiectul. SEV 105 și verificatorii bancari cer minimizarea ajustărilor *totale*.
*   **Soluția obligatorie:** Filtrează și selectează comparabila optimă folosind **Ajustarea Brută Totală (%)** (Etapa 1 + Etapa 2). Adaugă alerte vizuale dacă ajustarea brută trece de 25-30% sau cea netă trece de 15%.

**3. Reconciliere vs. Evaluarea pe Cost — Testul Breaza arată o problemă**
*   **Problema:** Matematica „proprietate = preț piață – teren” este metoda reziduală standard (extracție). Dar consiliul a rulat cifrele tale din Breaza: CIN = ~151.000 EUR. Valoarea alocată construcției prin extracție = ~107.000 EUR. Asta implică **o depreciere de piață bruscă de 29%**. Dacă acea casă din Breaza e relativ nouă, o depreciere neexplicată de 29% față de costul de înlocuire va bloca raportul la bancă.
*   **Soluția:** GEV 520 cere verificarea consistenței. Implementează un trigger automat: dacă `(Valoare Piață Construcție - CIN) / CIN` arată o diferență mai mare de ±15-20%, obligă utilizatorul (printr-un prompt AI sau secțiune în docx) să justifice explicit deprecierea (obsolescență funcțională/deteriorare) sau supraevaluarea.

**4. Ce lipsește pentru a respecta strict GEV 520:**
*   **Oferte vs. Tranzacții:** Scraping-ul aduce OFERTE. Aplicația trebuie să oblige evaluatorul să aplice un haircut (ajustare negociere ofertă → tranzacție), altfel încalcă art. 4.3.4 din GEV 520 care cere confirmarea prețurilor.
*   **Analiza Riscului de Garanție (pct. 6 din GEV):** Băncile cer explicit analiza lichidității, vandabilității și, adesea, *valoarea de lichidare forțată*. Lipsa acestora va rezulta în clarificări solicitate de departamentul de risc.
*   **Anexa 1 din GEV 520 (Certificarea):** Este un checklist standard (18 puncte). Trebuie generat și bifat automat în `.docx`.

---

### II. Risc AML, GDPR și Răspundere Juridică (Atenție la Risc Penal)

**5. Modulul AML (Legea 129/2019) — Capcana Penală**
*   **Problema 1 (Falsuri în Declarații):** Abordarea „aplicația propune, utilizatorul decide” e corectă filozofic, dar generează risc penal. Conform Art. 33, raportarea generată cu „neglijență gravă” se pedepsește cu închisoare de la 1 la 5 ani. Un LLM lăsat să halucineze date într-un RTS/RTN poate trimite evaluatorul în instanță.
*   **Problema 2 (Tipping Off - Art. 38):** Dacă rapoartele RTS/RTN generate sunt salvate de aplicație în foldere standard pe disc alături de dosar, există un risc imens ca acel client să le vadă. Legea interzice strict ca persoana vizată să afle că este raportată.
*   **Problema 3 (Screening PEP/Sancțiuni fals):** A avea funcția de verificare nominală drept un simplu „placeholder” în care utilizatorul pune o bifă este complet ilegal. Normele 37/2021 cer consultarea bazelor de date. Dacă evaluatorul bifează „verificat” în soft dar el nu a interogat OFAC/UE, încalcă obligațiile de raportare.
*   **Soluții obligatorii AML:** 
    *   Dezactivează complet screening-ul până integrezi un API real (OpenSanctions, gratuit, sau Reuters) SAU pune text roșu permanent pe pagină: „Aplicația NU verifică listele PEP/Sancțiuni. Verificați manual pe [Link-uri Oficiale]”.
    *   Documentele RTS generate trebuie să solicite acceptarea unui disclaimer masiv înainte de generare. Ele nu se salvează niciodată permanent în SQLite sau pe disc, ci se generează o singură dată la apăsarea butonului (Export Word) și aplicația face un bypass, lăsând zero urme în istoricul local.

**6. Modelul GDPR și Anonimizarea**
*   **Problema:** Transformarea `[Nume]` sau `[CNP]` e corectă, dar LLM-ul se hrănește cu „PII contextual”. Ex: „Casă 120mp, cu 3 camere, construcție parter galben, situată vizavi de Primăria comunei Tărtășești”. Orice persoană poate re-identifica proprietarul indirect (GDPR Art. 4).
*   **Soluția:** Afișează utilizatorului, într-o casetă non-editabilă, **exact textul brut care pleacă spre SDK-ul Anthropic/Perplexity**, cu un buton de consimțământ: „Confirm că acest text nu conține date identificabile sau indicii localizatoare”. Oferă un model `.docx` de politică GDPR (pentru clienții evaluatorului), menționând folosirea platformelor AI rezidente pe teritoriul SUA/UE ca *sub-procesatori*.

---

### III. Arhitectură, Scraping și Distribuție

**7. Capcana Scraping-ului (Imobiliare.ro / Storia) — AȘA NU pe termen lung**
*   **Problema:** Extragerea automată din backend Python (cel mai probabil cu requests / BeautifulSoup / Playwright) va pica rapid odată ce portalurile implementează protecții antibot agresive (Cloudflare, reCAPTCHA v3) și va duce la banarea IP-urilor evaluatorilor. În subsidiar, există și încălcarea Termenilor și Condițiilor și a Directivei UE pe baze de date (Sui Generis).
*   **Soluția Inteligentă:** Renunță la codul de scraping din backend. Construiește rapid o **Extensie de Chrome complet integrată**. Utilizatorul navighează manual, ca om, pe portal. Găsește anunțul, apasă un buton în extensia ta → extensia citește DOM-ul intern și dă un POST local către `http://localhost:[port_FastAPI]`. Ai 0 cod de scraping în backend, 0 capcane antibot, 0 banări de IP, și 0 probleme de rate-limiting (pentru că omul face throttling natural).

**8. Executabilul nesemnat și Stocarea SQLite**
*   **Problema (SmartScreen):** Un `.exe` de 176MB descărcat de pe net, din interiorul căruia pornește un server web intern (FastAPI), creat cu PyInstaller, fără semnătură digitală, este **coșmarul oricărui antivirus**. Pe un PC de bancă sau corporate, va fi șters instant ca focar de tip *trojan/malware*.
*   **Problema (SQLite pe Cloud):** Utilizatorii țin adesea aplicațiile „portabile” pe Google Drive / OneDrive. Când evaluatorul scrie în baza de date, serviciul de Cloud blochează fișierul (file lock) pentru sync. Aplicația ta va da crash cu `Database locked`.
*   **Soluții de Arhitectură:**
    1.  Cumpără URGENT un **Certificat Code Signing** (standard sau EV) și semnează codul înainte de a-l face `.exe`.
    2.  Forțează stocarea bazei de date în `%APPDATA%/EvaluatorANE_DB/` sau afișează o avertizare dacă detecți culegerea rutei într-un folder de OneDrive/Dropbox.
    3.  Ai nevoie de un mecanism minim de **Auto-Update** (măcar validarea versiunii la pornire și un prompt de download). Normele ONPCSB / ANEVAR se schimbă anual; un soft static iese din uzimentație.

---

### IV. Rezumat / Plan de Acțiune în 4 Pași (Priorități de Lansare)

Nu poți vinde produsul unei entități care colaborează cu băncile în stadiul curent fără un risc ridicat de returnare a rapoartelor către evaluatori. Pentru a transforma acest instrument ingenios într-un standard de industrie, iată ordinea de execuție:

1.  **Refactorizare Grile Construcții (Urgent):** Treci exclusiv pe calcule unitare (`EUR/mp`), implementează alerte de praguri procentuale de ajustare (maxim brut, maxim net) și utilizează calculul totalului de ajustări brute pentru criteriul automat de propunere a comparabilei.
2.  **Audit AML și Disclaimere Penale (Urgent):** Blochează bypass-urile de conformitate, elimină stocarea persistentă de fișiere destinate ONPCSB și implementează validarea cu baze de date publice pentru Sancțiuni (sau retrage funcția din interfață și impune validarea explicită umană în afara aplicației).
3.  **Code Signing și Mecanica de Update (Tactic):** Achiziționează certificatul Microsoft pentru `.exe`-ul tău; fără el, experiența de *onboarding* va fi ucisă din fașă de sistemul de securitate Windows Defender / SmartScreen.
4.  **Mutarea Scraping-ului din Backend (Strategic):** Schimbă abordarea din server-side fetcher către o extensie de browser sau flow de import manual inteligent (Copy/Paste la text brut din care LLM-ul tău extrage parametri, feature deja pretabil infrastructurii actuale).

Ați construit o fundație tehnică impresionantă, cu un engineering de top pe zona de testare și arhitectură locală. Rezolvând aceste detalii foarte stricte ce țin de realitatea cruntă a băncilor, vei avea pe masă probabil cel mai bun asistent software local pentru evaluatorii din România.


## Peer ranking (lower avg = better)

1. **anthropic/claude-sonnet-4.5** — avg 1.25 (4 votes)
2. **google/gemini-3.1-pro-preview** — avg 2.0 (4 votes)
3. **openai/gpt-5.1** — avg 2.75 (4 votes)
4. **x-ai/grok-4.3** — avg 4.0 (4 votes)


---

# Appendix: Individual member responses


## openai/gpt-5.1

Răspunsul e structurat pe cele 4 blocuri de întrebări (metodologie, conformitate, arhitectură, produs) și încheiat cu o listă scurtă de priorități. Voi marca explicit unde văd riscuri majore / „așa nu e ok” sau „asta trebuie betonată înainte de producție”.

---

## 1. Metodologie de evaluare (SEV/GEV)

### 1.1. Grila de teren în 2 etape, selecția pe ajustarea brută minimă (doar etapa de proprietate)

Ce aveți:
- Etapa 1: ajustări secvențiale/compuse la nivel de tranzacție (ofertă→tranzacție, drept, finanțare, condiții, condițiile pieței).
- Etapa 2: ajustări aditive la nivel de proprietate (localizare, acces, utilități, suprafață, urbanism etc.).
- Selecție: comparabilul cu **ajustarea brută minimă pe etapa de proprietate**; partea „ofertă→tranzacție” nu intră în acest criteriu.

Cum se practică în mod obișnuit:
- În literatura IVS/tehnică se urmăresc de regulă:
  - fie **ajustarea brută totală** (sumă valorică absolută a ajustărilor),
  - fie ajustarea netă,
  - plus verificări de consistență (coerență prețurilor unitare corectate, outliers, coerență cu alte abordări).
- Separarea „tranzacție” vs „proprietate” e logică și utilă explicativ, dar:
  - În practică, un evaluator responsabil se uită la **totalul ajustărilor** pentru a aprecia comparabilitatea globală.

Risc metodologic:
- Să ignori în criteriul de selecție ajustările mari făcute la nivel de tranzacție (ex: ofertă cu discount tipic 15–20%, condiții speciale, vânzare forțată).
- Banca/ANEVAR pot întreba explicit: „De ce ați considerat acest comparabil cel mai relevant, deși are ajustare brută totală mai mare?”

Recomandare:
- Menține structura în două etape (e corectă și transparentă), dar:
  - În criteriul de selecție, folosește **ajustarea brută totală** (tranzacție + proprietate) ca indicator principal de comparabilitate.
  - Poți păstra și un indicator separat „ajustare brută la nivel de proprietate” ca metrică secundară, pentru discuție.
- În raport, explică clar logica: „Comparabilele selectate prezintă ajustare brută totală sub X% și ajustări la nivel de proprietate sub Y%, ceea ce indică similaritate bună cu proprietatea-subiect.”  
Asta e mult mai defensabil în fața unei revizuiri stricte.

### 1.2. Grila pentru casă pe preț total + ajustare valorică pentru diferența de arie utilă

Ce aveți:
- Lucrați pe **preț total** al proprietății-comparabil.
- Diferența de arie utilă tratată ca ajustare valorică (Δ mp × preț unitar).

Practica de piață:
- Sunt două școli:
  1. **Pe preț unitar** (€/mp util / €/mp construit) și apoi multiplicați la suprafața subiectului.
  2. Pe preț total, dar cu ajustarea de suprafață exprimată explicit pe mp și reconvertită în valoare.
- Standardele (IVS/SEV) nu impun strict una sau alta; cer **consistență și justificare economică**.

Puncte forte ale abordării voastre:
- E matematic echivalent cu abordarea pe preț unitar, dacă:
  - prețul unitar pentru ajustarea de suprafață e bine fundamentat și
  - nu amestecați în mod inconsistent alte ajustări.

Riscuri:
- Pentru un revizor, e mai ușor de urmărit un **raționament pe preț unitar** și apoi re-multiplicare, pentru că:
  - este standard în multe rapoarte de garantare,
  - scoate în evidență imediat poziționarea subiectului vs comparabile (€/mp).
- Lucrul direct pe preț total poate masca în text modul cum ați determinat prețul unitar implicit.

Recomandare:
- Din punct de vedere defensabil:
  - Intern puteți păstra calculul exact cum e (preț total + ajustare valorică de suprafață), DAR:
  - în raportul livrat să afișați explicit **prețurile unitare corectate** și raționamentul pe €/mp (casă + teren / doar casă, după caz).
- În interfață, luați în calcul să:
  - recalculați și salvați clar „preț unitar derivat” pentru fiecare comparabil, înainte și după ajustare,
  - afișați grila și extern în „paradigma €/mp”, pentru a reduce fricțiunea cu practicienii.

Verdict:
- Metodologic este acceptabil, dar pentru uz real de bancă e mai „natural” să fie prezentat clar și în forma clasică pe €/mp.
- Nu e „așa nu se face”, dar va ridica mai multe întrebări dacă nu prezentați și un tabel pe preț unitar.

### 1.3. Reconciliere + alocarea (construcții = proprietate − teren)

- Reconciliere:
  - Aveți toate cele 3 abordări majore (cost, comparație, venit), ceea ce e **peste** ce se vede în multe rapoarte de garantare (unde uneori se opresc la comparație teren + comparabil total).
  - Important: în raport trebuie să fie explicită:
    - ponderea acordată fiecărei abordări,
    - de ce abordarea prin comparație are pondere mai mare pentru garantare (piață actuală),
    - de ce abordarea prin cost e mai mult o **plauzibilitate superioară** (plafon) și nu neapărat bază principală.
- Alocare construcții = valoare proprietate − valoare teren:
  - Este metoda clasică și acceptată, folosită masiv la garanții.
  - De verificat să nu se aplice în situații în care:
    - terenul se evaluează la o valoare care duce la **valoare rămasă a construcției sub costul de demolare / clar nesustenabilă economic**; în astfel de cazuri standardele cer discuție explicită.
- Pentru garantare:
  - Băncile sunt în general ok cu această metodă, atât timp cât:
    - explicitați clar că terenul a fost evaluat prin comparație și construcția este rest de valoare.
    - nu există conflict evident cu costul de înlocuire (ex: CIN foarte peste valoarea de piață, ceea ce cere discuție despre depreciere/funcțională).

Verdict:
- Metodologic, alocarea este adecvată și standard.
- Aș adăuga un control automat: dacă rezultă valoare construcție < 0 sau sub o anumită limită realistă (ex: < 10% din CIN), inserați o alertă către evaluator să justifice sau să revizuiască parametrii.

### 1.4. Abordarea prin venit (capitalizare directă + DCF)

Structura actuală:
- Capitalizare directă:
  - VBP din grilă de chirii comparabile.
  - Vacanță, cheltuieli, NOI.
  - NOI / rată.
- DCF:
  - Fluxuri explicite + valoare reziduală.

Așa cum e descris:
- E în linie cu IVS/SEV 105 – nu văd abateri conceptuale.  
- Riscul major nu e structura, ci:
  - cum se stabilește **rata de capitalizare / discount**,
  - calitatea și sursa grilei de chirii (care acum e tot pe anunțuri).

Recomandări:
- Pentru uz bancar:
  - faceți explicit în raport că **abordarea prin venit** are caracter suport secundar atunci când:
    - nu există istoric stabil de închiriere,
    - utilizarea nu este preponderent investițională (ex: casă individuală ocupată de proprietar).
  - unde proprietatea este tipic rezidențială pentru consum propriu, băncile pot considera abordarea prin venit doar o verificare suplimentară, nu fundament primar.
- Implementați controale:
  - dacă proprietatea e „casă pentru locuire proprie” → marcați abordarea venit ca „auxiliară, în măsura relevanței”.
  - dacă evaluatorul alege să o nu folosească, sistemul să permită punctarea explicită a motivului (necesar în raport).

Verdict:
- Corectă ca structură; necesită doar:
  - mai multă transparență în logica de stabilire a ratei,
  - poziționare clară în raport în funcție de tipul de proprietate și scop.

### 1.5. Lipsește vreo abordare/verificare cerută pentru garantare?

Pentru garantare (GEV 520 + SEV 2025) aș verifica următoarele:

1. **Tipul valorii**:
   - Raportul trebuie să declare clar „valoare de piață conform SEV 102 / IVS 104” și, unde e cazul, „valoare de garanție conform GEV 520”.
   - Dacă faceți diferențiere între „valoarea de piață” și „valoarea de garanție” (mai prudentă, eventual cu ajustări de lichiditate etc.), modul de calcul trebuie explicit și foarte prudent.  
   Altminteri, multe bănci iau direct „valoarea de piață” ca „valoare de garanție” cu aplicarea internă a LTV-urilor.

2. **Analiza pieței**:
   - Există cerință explicită de prezentare a contextului pieței locale (trenduri de preț, lichiditate, timp de expunere). Ar trebui ca:
     - modulul de narativ AI / șablon să conțină explicit aceste elemente,
     - să nu se bazeze doar pe 3–4 comparabile ca „toată piața”.

3. **Verificări de plauzibilitate încrucișată**:
   - Pentru teren construibil: comparație cu **valoare de capitalizare a chiriei terenului** nu e obligatorie, dar unele bănci o apreciază ca verificare.
   - În practică, nu e obligatoriu să aveți altă abordare formală; ceea ce e critic e:
     - compararea rezultatelor celor 3 abordări,
     - justificarea abaterilor mari.

Concluzie:
- Nu văd o „abordare lipsă” obligatorie.
- Mai critic e cum veți explica reconcilierea și ce text standard de justificare generați, astfel încât rapoartele să fie ușor de apărat.

---

## 2. Conformitate & risc (GDPR, AML, răspundere)

### 2.1. Model GDPR (anonimizare înainte de AI)

Ce faceți:
- Toate datele personale (client, adresă, număr cadastral, CF, evaluator) → tokeni generici `[CLIENT]`, `[ADRESA]`, etc. înainte de a trimite la LLM.
- Dezanonimizare doar local, după primirea textului.
- Aplicația rulează local, baza e locală.

Puncte foarte bune:
- Principiul de „pseudonimizare puternică” înainte de a ieși din dispozitiv e foarte solid; pentru multe autorități, asta reduce masiv riscul.
- Faptul că nu trimiteți CF, CNP, adresă exactă, nume, este un plus major.

Riscuri reziduale:
1. **Date indirect identificabile**:
   - Dacă trimiteți totuși descrieri foarte concrete ale proprietății (ex: „vilă P+2+M, 374 mp utili, terreno 893 mp, pe strada X, lângă primărie, în comuna cu 700 locuitori”), se poate, în teorie, re-identifica persoana cu efort, chiar fără nume.
   - Limitaţi bogăţia detaliilor localizatoare trimise la LLM; țineți în LLM strict ce e nevoie pentru analiză narativă (tendințe, calitate, riscuri), nu și toată adresa contextuală.

2. **Loguri la furnizorul LLM**:
   - Dacă folosiți API comerciale, trebuie să verificați:
     - politica de retenție a datelor,
     - dacă datele sunt folosite pentru training,
     - locația (UE vs SUA),
     - acord DPA (Data Processing Agreement).
   - Ar trebui să recomandați explicit în documentație că evaluatorul trebuie să aibă un DPA/compliant GDPR cu furnizorul de LLM (Anthropic/Perplexity) dacă transmite date chiar și pseudonimizate.

3. **Tokeni de tip `[ADRESA]`**:
   - Dacă evaluatorul copiază în prompt text neanonimizat (de ex. manual), sistemul nu are cum să-l protejeze.
   - E important să aveți clar în UI o separare: „Această zonă e trimisă la AI; nu introduceți aici date cu caracter personal.”

Verdict:
- Modelul tehnic este **bine gândit și mult peste medie** pentru un instrument profesional.
- Nu e „blind spot” major, dar este nevoie de:
  - clarificare contractuală (DPA) cu furnizorul LLM,
  - avertismente explicite în UI/documentație despre ce NU trebuie introdus ca text liber,
  - eventual un filtru suplimentar de pattern-uri (CNP, adrese românești, numere CF) pe textul trimis la LLM, ca safety net.

### 2.2. Modul AML – „propune, evaluatorul transmite”

Situația:
- Modulul generează:
  - norme interne,
  - evaluare riscuri,
  - decizie desemnare,
  - fișe KYC,
  - RTN, RTS (dar stocate separat de dosar),
- Listele de sancțiuni/PEP sunt injectabile, nu live.
- Textele n-au fost supuse unei revizii juridice finale.

Aspecte de conformitate:

1. **Rolul aplicatiei**:
   - Dacă e clar poziționată ca instrument de asistență, fără să pretindă că asigură conformitatea integrală, e ok conceptual.  
   - Text clar în EULA / manual: „Nu constituie consultanță juridică. Evaluatorul rămâne singurul responsabil pentru conformitate AML.”

2. **Norme interne / evaluare de risc**:
   - Sunt documente care, legal, trebuie adaptate la specificul fiecărei entități (PFA vs SRL, volum tranzacții, profil clienți).
   - Un model generic generat de AI poate fi un bun **draft**, dar:
     - trebuie **NEAPĂRAT** trecut prin filtru juridic la inițiere; altfel riscați ca utilizatorul să creadă că e complet acoperit.

3. **RTS/RTN și confidențialitate**:
   - Faptul că îi țineți separat de dosar e corect conform Legii 129 (interdicție de divulgare).
   - Atenție ca aplicația să nu includă „shortcuts” de gen: export RTN/RTS și atașare automată în dosarul de evaluare – ar fi greșit.

4. **Screening sancțiuni/PEP**:
   - Placeholder injectabil = incomplet.
   - E foarte important să marcați în UI:
     - „Acest modul nu efectuează în mod autonom verificări live pe liste de sancțiuni. Evaluatorul trebuie să asigure verificările prin furnizori specializați sau surse oficiale.”
   - Altfel riscați să induceți un sentiment fals de conformitate.

Ce trebuie neapărat validat juridic:
- Template-urile de:
  - Norme interne,
  - Evaluarea globală de risc,
  - Procedura KYC și registrul de clienți,
  - Formatul fișelor RTS/RTN (alinierile la Normele ONPCSB, HCD 58).
- Formulările despre:
  - păstrarea datelor,
  - raportarea motivată vs automată,
  - măsuri de due diligence simplificat/sporit.

Verdict:
- Conceptual „propune, evaluatorul transmite” e corect; dar:
  - **nu lansați acest modul în producție** fără o revizie juridică de către un avocat specializat AML/Legea 129.
  - În lipsa ei, modulul AML ar trebui etichetat clar ca „beta / exemplu didactic” și nu ca ceva „de plin uz profesional”.

### 2.3. Răspunderea profesională și AI-ul care redactează narativul

Riscul:
- În eventualitatea unui litigiu / reclamație la ANEVAR:
  - raportul e semnat de evaluator, nu de AI. Legal, responsabilitatea e a evaluatorului.
  - TOTUȘI, dacă se poate demonstra că evaluatorul a folosit un șablon AI „copy-paste” fără minimă revizie, poate fi interpretat ca neglijență.

Cum să limitați riscul:
1. Tehnic:
   - Marcați în raport, eventual, un mic text: „Raport redactat cu asistența unui instrument software; conținutul a fost revizuit și asumat de evaluator.”
   - Ar fi util să păstrați o „history” a modificărilor manuale în secțiunea de narativ (cel puțin la nivel de log local), pentru ca evaluatorul să poată demonstra că a intervenit.

2. De utilizare:
   - Introduceți avertismente clare:
     - „Textul generat este o propunere; evaluatorul are obligația să-l verifice și să-l ajusteze pentru a reflecta realitatea cazului.”
   - Eventual, cerință ca evaluatorul să completeze câteva câmpuri manuale (de ex. „observații personale”), ca să evitați raport 100% auto-generat.

Verdict:
- Nu e „interzis” ca AI să asiste la redactare, dar:
  - trebuie să fie clar că este asistență, nu autor principal,
  - trebuie instrumentate tehnic și contractual măsuri care să oblige la revizie umană.

---

## 3. Arhitectură & inginerie

### 3.1. Server-rendered + `.exe` offline vs web app

Pentru publicul țintă (evaluatori ANEVAR, de obicei:
- cu toleranță relativ scăzută la cloud pentru date sensibile,
- cu PC-uri Windows, uneori cu acces la internet limitat în teren):

Avantaje ale soluției voastre:
- Offline complet → mare plus pentru confidențialitate și disponibilitate.
- Un singur `.exe` → simplu de distribuit, fără probleme de hosting.
- Server-rendered + Jinja → mai puține dependențe front-end, mai puține probleme de securitate web.

Compromisuri:
- Update-urile sunt manuale (nu aveți un canal de update automat).
- Nu puteți colecta ușor telemetrie anonimă sau bug reports centralizate, ceea ce face debugging-ul la clienți mai greu.
- Scalarea nu e relevantă (e single user), dar:
  - mentenanța versiunilor multiple la clienți poate deveni dificilă.

Verdict:
- Pentru **MVP profesional** în acest domeniu, decizia `.exe` offline este foarte potrivită, chiar preferabilă unui SaaS, mai ales din perspectiva GDPR/AML și acceptanță de bănci.
- Nu văd un „compromis ratat” major; doar să asigurați un mecanism decent de update (vezi secțiunea produs).

### 3.2. Riscuri de scalare/mentenanță (FastAPI + Jinja + SQLite local)

Scalare:
- Nu e relevant „scalare pe utilizatori simultani” – fiecare utilizează un exe propriu.
- Riscuri reale:
  - coruperea bazei SQLite dacă aplicația se închide brusc (crash, power off) în timpul scrierii.
  - evoluții de schemă (migrări) între versiuni.

Recomandări:
- Implementați:
  - migrare versiune DB (Alembic-like sau propriul mecanism) – la pornire, aplicația detectează versiunea schema și migrează.
  - backup automat al fișierului DB (de ex. la închidere sau la anumite intervale); eventual o comandă „Backup/Restore dosare”.
- Fiți extrem de conservatori cu actualizările de dependențe (deja faceți asta cu `requirements.lock` – foarte bine).

FastAPI + Jinja:
- Pentru un `.exe` local e un pic „heavy”, dar:
  - separarea clară a logicii prin routere, Pydantic etc. e net pozitivă pentru calitate, testare și mentenanță.
- Faptul că aveți 375 de teste și 92% coverage reduce mult riscurile de regresie.

Verdict:
- Arhitectura e solidă pentru un instrument desktop „serios”.
- Punctele sensibile sunt:
  - managementul de migrare DB,
  - robusteză la crash,
  - suport tehnic pentru utilizatorii non-tehnici (loguri, mod de diagnostic).

### 3.3. Scraping portaluri ca sursă primară de comparabile

Riscuri:

1. **Juridic (ToS, drepturi de autor, acces automatizat)**:
   - Majoritatea portalurilor imobiliare românești includ în ToS interdicții explicite pentru scraping automat / utilizare comercială fără acord.
   - Pentru un produs comercial:
     - folosirea scraping-ului fără acord poate duce la:
       - blocarea IP-urilor,
       - litigii (la limită),
       - cerințe de încetare.

2. **Tehnic**:
   - Schimbare de layout rupe la un moment dat extragerea.
   - Riscul de date parțial extrase → comparabile cu atribute greșite (de ex. confundare arie utilă cu construită).

3. **Calitate de date**:
   - Anunțurile de tip **ofertă**, nu tranzacție, pot fi mult supraevaluate.
   - În lipsa accesului la Baze ANEVAR/BIG, calibrările pot fi slabe.

Alternative:
- Ideal:
  - **Parteneriat contractual** cu unul dintre portaluri sau cu un agregator de date (API oficial), cu licență clară.
  - Acces pe bază de API la BIG (dacă devine disponibil pentru integratori), dar asta e, de obicei, limitat la membrii ANEVAR și chiar atunci cu restricții.
- Pragmatic:
  - continuați scraping-ul, dar:
    - **nu îl poziționați în marketing ca funcție principală** („se conectează la imobiliare.ro”) ci ca „instrument de asistență automatizată pentru căutarea ofertelor publice”.
    - tehnic, oferiți posibilitatea ca evaluatorul să introducă manual comparabilele și să folosească doar motorul de grilă / calcul.
    - aveți fallback clar când scraping-ul eșuează (nu-l mascați ca „nu sunt anunțuri”).

Verdict:
- Din punct de vedere comercial/legal: este una dintre cele mai mari zone de risc.
- Pentru un produs „gata de bancă”, aș prioritiza:
  - fie obținerea unui acord explicit de la 1–2 portaluri,
  - fie minim poziționarea clară ca utilitar auxiliar, cu disclaimere ferme.

---

## 4. Produs & distribuție

### 4.1. Ce ar putea face un raport să fie respins de o bancă?

Din perspectiva unui ofițer de risc / analist credite:

1. **Inconsistențe metodologice vizibile**:
   - Lipsa clară a justificării pentru alegerea comparabilelor (de aceea e critic să explicați clar criteriul de „ajustare brută totală mică”).
   - Prețuri anunțate de portaluri tratate ca „tranzacții” fără ajustare explicită de tip ofertă→tranzacție.

2. **Lipsuri în structură obligatorie**:
   - Neprecizarea tipului valorii (Valoare de piață, data evaluării, baza valorii etc. conform SEV 102).
   - Lipsa capitolului de analiză a pieței locale / situației urbanistice.

3. **Text standard prea „generic”**:
   - Narativ AI sau șablon foarte generic, cu fraze care par copiate din alt caz sau nepotrivite situației (de ex. se menționează „proprietatea are incintă împrejmuită” la un teren agricol deschis).
   - Orice indiciu că evaluatorul nu a „pus osul”: băncilor nu le place senzația de template gros.

4. **Erori de formă**:
   - Neconcordanțe între cifre (tabel vs narativ).
   - Lipsa datelor evaluatorului / licenței ANEVAR / poliței de asigurare.

Ce lipsește pentru „gata de producție”:
- Un set de **șabloane narative calibrate foarte strict** pe tipuri de proprietate / scop, astfel încât fără LLM să acopere cerințele minime SEV/GEV.
- O **secțiune clară de reconciliere**:
  - „Rezultatele prin abordarea costului, prin comparație și prin venit sunt: X, Y, Z. S-a considerat valoarea finală Y pentru că…”
- O listă de verificări finale (checklist) integrată în UI: „Verificat tip valoare; verificat data evaluării; menționat surse de date; menționat restricții.”

### 4.2. Distribuția (`.exe` nesemnat, Win10+)

Probleme practice:

1. **SmartScreen / antivirus**:
   - Utilizatorii non-tehnici se tem de avertismente; pot refuza instalarea.
   - Băncile pot fi reticente să primească fișiere rezultate dintr-o aplicație considerată de Windows ca „necunoscută”.

2. **Compatibilitate**:
   - Windows 8.1/10/11 e ok; lipsa Win7 e mai puțin critică în 2026, dar încă veți găsi câțiva utilizatori.
   - Important să documentați clar cerințele minime.

3. **Update-uri**:
   - Fără semnătură digitală și fără updater automat, mulți utilizatori vor rămâne pe versiuni vechi.
   - Pentru un domeniu reglementat (SEV 2025, standarde care se schimbă) asta e o problemă.

Recomandări:
- Semnarea codului:
  - Investiți într-un **certificat de code signing** (ideal EV dacă vă permite bugetul); reduce masiv friction-ul SmartScreen.
- Updater:
  - un mecanism intern simplu:
    - aplicația verifică periodic o versiune disponibilă pe un server (doar număr și checksum),
    - notifică utilizatorul, care poate descărca manual noul `.exe`.
  - Fără auto-update complet, dar măcar notificare.

### 4.3. Top 3 lucruri de prioritarizat înainte de uz real

1. **Audit metodologic + juridic**:
   - Metodologic:
     - Ajustați logica de selecție comparabile (bazată pe ajustare brută totală).
     - Revizuiți și documentați clar modul de lucru cu oferte vs tranzacții.
   - Juridic (AML):
     - Dați tot modul AML (norme, proceduri, KYC, RTN/RTS) la revizie unui avocat sau consultant AML.
     - Marcați explicit în UI și documentație rolul de „draft / asistență, nu conformitate garantată”.

2. **Calibrarea și „hardening”-ul raportului `.docx` pentru bănci**:
   - Includeți:
     - capitole standardizate pentru analiză piață, ipoteze și limitări, reconciliere.
     - o listă internă de control calitate (checklist final) bifabilă de evaluator.
   - Producție de „rapoarte pilot” cu 2–3 evaluatori practicieni cu experiență în garantare și ajustarea șabloanelor pe feedback-ul lor.

3. **Securizarea și legalizarea surselor de date**:
   - Pe termen scurt:
     - tratați scraping-ul ca „feature experimental”, cu disclaimere.
     - oferiți flux excelent pentru introducere manuală de comparabile.
   - Pe termen mediu:
     - căutați măcar un acord cu un portal sau cu o sursă de date semi-oficială.
   - În paralel:
     - optimizați modul GDPR/LLM (pattern-filter pentru date personale în prompt, clarificări DPA).

---

Dacă vreți, pot merge mai adânc în:
- structura exactă a grilelor (ce câmpuri, ce tip de ajustări),
- cum să formulați texte standard în raport astfel încât să fie „auditabile” și ușor de personalizat de evaluator.


## google/gemini-3.1-pro-preview

Acesta este un review independent, concentrat pe identificarea vulnerabilităților metodologice, tehnice și de conformitate. Domeniul evaluărilor ANEVAR pentru garantare (GEV 520) este extrem de conservator și rigid; băncile au departamente de verificare care resping dosare pentru abateri tehnice minore. 

Iată analiza critică și răspunsurile la întrebările tale, punând accent pe **„ce nu e bine”** și **„ce va genera respingeri”**.

---

### I. Metodologie și Evaluare (Risc major de respingere la Bănci)

**1. Grila de teren: selecția pe ajustarea brută minimă doar pe etapa de proprietate.**
*   **Critică (Așa Nu):** Metodologia standard și uzanțele verificatorilor din bănci (și GEV) cer ca proprietatea selectată drept valoare de bază (sau cu ponderea cea mai mare) să fie cea cu **numărul minim de ajustări, valoarea brută (absolută) minimă și valoarea netă minimă pe TOATĂ grila**, nu doar pe elementele de proprietate. Corecțiile de piață, tranzacție sau finanțare modifică substanțial baza de comparație. Dacă ignori prima etapă în criteriul de selecție, poți alege o comparabilă cu diferențe masive de condiții de piață (ex. ofertă veche de 2 ani, mult ajustată), ceea ce un verificator de bancă va penaliza.
*   **Recomandare:** Criteriul de selecție/ponderare trebuie să folosească **Ajustarea Brută Totală (%)** și **Ajustarea Netă Totală (%)**.

**2. Grila de casă/apartament: calculul pe PREȚ TOTAL calculat ca ajustare valorică.**
*   **Critică (Așa Nu - Risc Critic):** Acesta este probabil cel mai mare „red flag” din dosarul tău. În România, pentru garantare (GEV 520), proprietățile construite (case, apartamente, spații comerciale) se evaluează și se compară **aproape exclusiv pe Preț Unitar (EUR/mp arie utilă sau desfășurată)**. Compararea pe preț total și ajustarea diferenței de suprafață ca sumă fixă distorsionează complet procentele de ajustare pe care băncile le monitorizează strict.
*   **De ce pică la bancă:** Băncile au limite in sistemele lor (ex. ajustare maximă brută admisă = 30-40%, ajustare max pe o linie = 15%). Dacă lucrezi pe total, ajustarea de suprafață va sări procente uriașe, forțând respingerea.
*   **Recomandare:** Orice grilă de construcție se face transformând prețurile de tranzacție/ofertă în **EUR / mp**. Ajustările se aplică procentual asupra prețului unitar (EUR/mp). La final, valoarea de piață unitară (EUR/mp) se înmulțește cu suprafața subiectului.

**3. Reconcilierea și alocarea (Construcții = Proprietate - Teren).**
*   **Critică:** Metoda extracției (reziduală) este corectă și perfect apărabilă. Reconcilierea este corectă, dar asigură-te că pentru scopul „garantare”, abordarea prin piață are pondere maximă, iar abordarea prin cost este tratată ca limită superioară a valorii (principiu de prudență cerut de bănci).

**4. Abordarea prin venit (Capitalizare directă + DCF).**
*   **Critică:** Structura e corectă, dar **inutilă (chiar riscantă) pentru 90% din ipotecarele standard (rezidențial)**. Introducerea forțată a unor rate de capitalizare arbitrare pe case/apartamente atrage discuții inutile cu revizorii din bănci. 
*   **Recomandare:** Ține modulul izolat. Pentru proprietăți comerciale/investiții e vital. Pentru „casa din Breaza”, dezactivează-l by default, altfel rapoartele vor fi supraîncărcate („over-engineered”).

**5. Ce lipsește pentru garantare (GEV 520)?**
*   **Baza Imobiliară de Garanții (BIG):** Băncile cer integrarea cu BIG. Raportul trebuie să conțină numărul de înregistrare BIG, iar prețurile din BIG sunt preferate comparabilelor din portaluri. Aplicația are nevoie de un flux (chiar și manual) clar pentru a injecta datele din BIG.
*   **Tabel Limitări Ajustări:** Nu am văzut menționată alertarea pentru depășirea pragurilor prudențiale (ex. avertisment vizual/în raport când un ajustament > 15% sau brut total > 30%).

---

### II. Conformitate, GDPR și Risc AML

**6. Modelul GDPR (Anonimizare înainte de LLM).**
*   **Critică:** Paradigma e corectă, dar aplicarea ei e extrem de dificilă. În descrierea narativă (analiza pieței, descrierea vecinătăților), LLM-ul are nevoie de context. Anonimizarea regex/șablon `[CLIENT]` e ușoară. Riscul e „PII-ul contextual” (ex: coordonate GPS transmise la API, coduri poștale exacte, bucăți din extrasul CF care conțin cnp-uri sau nume de vecini pe limitele de proprietate ignorate de OCR/mascare).
*   **Recomandare:** Pune un layer vizual unde evaluatorul **vede exact string-ul trimis către LLM** și dă „Aprob trimiterea”. Oferă o exonerare de răspundere (Disclaimer: Utilizatorul e responsabil ce date trimite în cloud).

**7. Modulul AML.**
*   **Critică:** Abordarea „aplicația propune, utilizatorul decide și raportează la ONPCSB” este singura abordare legală. Un soft nu poate avea cod CAEN de evaluator pentru a raporta el. 
*   **Riscul critic (Art. 38 - Tipping off):** Ai zis că drafturile RTN/RTS se păstrează separat de dosar. Mare atenție! Dacă fișierele sunt indexate pe disc sau rămân într-un folder nesecurizat de unde clientul sau un terț le poate vedea accidental, evaluatorul riscă dosar penal pentru divulgarea raportării de tranzacție suspectă.
*   **Recomandare:** Orice RTS generat local ar trebui exportat, iar baza de date SQLite să îi facă „wipe” (zero-fill) automat din jurnalul aplicației, păstrând doar o bifă: „RTS generat la data de”.

**8. Răspunderea profesională (AI redactor).**
*   **Critică:** ANEVAR și instanțele/băncile nu recunosc „AI-ul a greșit”. Evaluatorul semnează și este 100% responsabil (malpraxis). Dacă LLM-ul halucinează („fundații de piatră” când erau de beton), banca respinge raportul, iar la litigiu, evaluatorul plătește.
*   **Recomandare:** Generează doar „schelete” de text, folosește *low temperature* la LLM pentru a tăia creativitatea, și **obligă utilizatorul printr-o barieră UX** (ex. checkbox de confirmare citire pe fiecare box de text generat de AI) să îl valideze.

---

### III. Arhitectură și Inginerie

**9. Server-rendered local (FastAPI + Jinja + SQLite) într-un `.exe`.**
*   **Alegerea este excelentă pentru profilul utilizatorului** (de obicei un evaluator singur la birou, care folosește Windows, e obsedat de confidențialitatea datelor lui, are conexiuni de net variabile, merge pe teren).
*   **Compromis ratat (Dezavantajul major): Actualizările (Updates).** Legislația ANEVAR/AML se schimbă anual. Portalurile web se schimbă lunar (pică scraperul). Pentru fiecare fix, utilizatorul trebuie să descarce și să înlocuiască manual un `.exe` de 176MB.
*   **Recomandare:** Implementează un mecanism de *auto-update* la pornire (aplicația ping-uie un URL, dacă există versiune nouă, descarcă și înlocuiește executabilul prin fișier bat temporar, sau măcar arată un banner ROȘU "Update critic necesar").

**10. Riscuri stocare locală.**
*   **Critică:** SQLite pe Windows este vulnerabil dacă evaluatorul vrea să țină baza de date direct într-un folder de Google Drive/OneDrive/Dropbox pentru backup. Aceste servicii blochează fișierul (file lock) în timp ce fac sync, ceea ce va bloca interogările aplicației (Database Locked error).
*   **Recomandare:** Stochează SQLite-ul în `%APPDATA%/EvaluatorApp`, nu vizibil utilizatorului, și oferă butoane clare de „Export Dosar (JSON/.eval)” pentru backup/partajare manuală.

**11. Scraping-ul (Imobiliare.ro / Storia).**
*   **Critică (Risc Major):** Acesta nu este un model sustenabil. Ambele portaluri folosesc tehnologii anti-bot agresive (Cloudflare, CAPTCHA). Dacă evaluatorul rulează scraper-ul, IP-ul lui din birou va fi banat în 3 zile. În plus, scraping-ul de proprietate intelectuală pentru a o vinde în rapoarte comerciale încalcă ToS-ul lor.
*   **Recomandare arhitecturală:** Modifică sursa spre o **Extensie de Chrome complet integrată**. Utilizatorul navighează *manual* ca om pe imobiliare.ro, apasă un buton în extensia ta („Trimite în EvaluatorApp”), extensia ia DOM-ul și îl trimite la API-ul local rulat pe `localhost`. Zero cod de scraping web, zero riscuri de a fi blocat de Cloudflare.

---

### IV. Distribuție și Produs (Priorități de Lansare)

**12. De ce ar fi respins raportul azi de un verificator de bancă?**
*   Abordarea casei prin *Preț Total* în grilă. (Respingere automată, considerată eroare de metodologie de bază).
*   Lipsa analizelor obligatorii impuse de GEV 520 (Analiza lichidității, risc de nefinalizare, analiză HBE - Cea mai bună utilizare).
*   Limbaj care „sună dubios/a chatbot”. Verificatorii citesc 10-15 rapoarte pe zi, simt imediat o „halucinație” semantică și dau retur pentru „lipsă rigoare în redactare”.

**13. Problema cu un .exe nesemnat pe Windows 10/11.**
*   **Critică:** Este iadul adopției comerciale. Windows SmartScreen îl va bloca cu un ecran roșu înfricoșător. Mulți evaluatori lucrează pe laptopuri unde nu au drepturi depline de Admin sau antivirusul (Bitdefender/Windows Defender) va șterge direct `.exe`-ul împachetat cu PyInstaller din cauza semnăturii de comportament (false positive).
*   **Soluție urgentă:** Trebuie să cumperi un **Certificat Code Signing standard sau EV** (aprox. 150-300 Euro/an) și să semnezi digital `.exe`-ul generat. Fără asta, vei petrece 80% din timpul de suport făcând excepții în antiviruși prin TeamViewer.

**14. TOP 3 Priorități înainte de lansare:**

1.  **Corectarea metodologiei Grilelor de Construcții (Casă/Apartament):** Trecerea obligatorie pe calcule în **Preț Unitar (EUR/mp)** și implementarea alertelor prudențiale pe nivel de ajustări (+ limitarea abordării pe venit pentru ipotecare rezidențiale).
2.  **Achiziția unui Certificat Code Signing și Sistem de Update:** Semnează executabilul și creează o metodă simplă de a livra actualizări. Ai un scraper și norme AML: aplicația ta *va avea nevoie* de update-uri lunare.
3.  **Refacerea modului de „Descoperire Comparabile”:** Renunță la scraping Python backend (va pica inevitabil de la Cloudflare). Treci pe Copy-Paste structurat (text drop direct in app care extrage atribute cu LLM) sau o extensie de browser.

**Concluzie generală:** Arhitectura software și ideea sunt extrem de bine ancorate în realitatea muncii unui evaluator (automatizarea muncii de „om-mașină”, generare docx, UI clarificat). Dacă rezolvi problema Prețului Total vs Unitar în grilă și blochezi posibilitatea de a trimite PII contextual la cloud-ul AI, ai un produs "enterprise-ready".


## anthropic/claude-sonnet-4.5

# Review independent — Asistent evaluare imobiliară ANEVAR

Apreciez documentația exhaustivă. Voi fi direct și onest, prioritizând riscurile de conformitate și metodologie.

---

## A. METODOLOGIE DE EVALUARE — Riscuri critice

### 1. **Grila de teren (2 etape) — PROBLEMATICĂ**

**Problema majoră**: Separarea în două etape cu selecția pe "ajustarea brută minimă pe etapa de proprietate" **ignoră impactul etapei de tranzacție**.

- Un comparabil cu ajustare mică la proprietate dar ajustare **masivă** la tranzacție (ex. +40% ofertă→tranzacție) poate fi selectat greșit în fața unuia cu ajustări totale mai mici dar echilibrate.
- **SEV 105 § 20.7**: "Evaluatorul trebuie să evite combinațiile în care ajustările nete sau brute devin excesive." Nu specifică „doar pe etapa 2".
- **GEV 520 § 4.3.2**: Banca verifică "consistența ajustărilor totale"; o ajustare de +35% tranzacție + -5% proprietate (net 30%, brut 40%) e mai riscantă decât +10% + +15% (net 25%, brut 25%).

**Recomandare**: 
- Adaugă **filtru** înainte de selecție: exclude comparabile cu ajustare brută totală > 25% sau netă > 15% (praguri GEV 520).
- Afișează **rang după ajustare brută totală** alături de selecția ta, lăsând evaluatorul să decidă.
- Justifică metodologic în raport: "Comparabil selectat pe baza ajustărilor de proprietate minimale, ajustările de tranzacție fiind considerate..."

**Defensabilitate actuală**: 60%. O bancă riguroasă poate respinge dacă comparabilul ales are ajustare totală mare dar e selectat pentru ajustare proprietate mică.

---

### 2. **Grila casă (preț total cu ajustare de arie) — ACCEPTABILĂ dar RISCANTĂ**

**Problema**: Tratarea diferenței de suprafață ca ajustare valorică simplă (Δmp × preț/mp) presupune **liniaritate perfectă**, ceea ce e fals pentru proprietăți rezidențiale.

- O casă de 80 mp vs. 120 mp: valoarea marginală a mp-ului suplimentar **scade** (baie 2 adaugă mai puțin decât baie 1).
- **SEV 105 § 20.10(d)**: "Ajustările pot fi procentuale, valorice sau o combinație, în funcție de natura caracteristicii." Pentru suprafață, piața funcționează **degresiv**.

**Argumentul pentru preț total** (corect): Evită distorsiunea prețului/mp care scade cu suprafața.

**Dar**: Ajustarea lineară pe diferență e **tot distorsionată**.

**Recomandare**:
- Implementează ajustare **degresivă** pentru diferențe de suprafață >20%: ex. primii 20 mp la preț unitar complet, următorii 20 mp la 85%, peste 40 mp la 70%.
- **Sau** păstrează varianta actuală **doar dacă diferențele de suprafață <25%** și documentezi limitarea în raport: "Ajustarea liniară aplicabilă pentru diferențe mici de suprafață."
- Adaugă **avertizare** dacă Δmp > 30%: "Diferență semnificativă — verificați dacă ajustarea liniară e adecvată."

**Defensabilitate actuală**: 70%. Funcționează pentru cazuri apropiate, dar risc de respingere dacă comparabilele diferă substanțial în mărime.

---

### 3. **Reconciliere + alocare — RISCANTĂ pentru garantare**

**Problema critică**: Alocarea `construcții = proprietate − teren` **nu e validată independent**.

- **GEV 520 § 4.2.5**: "Valoarea construcțiilor trebuie verificată prin abordarea costului pentru consistență."
- Dacă valoarea pieței e 135k EUR, teren 27k EUR → construcții 108k EUR, dar **CIN = 150k EUR**, înseamnă **depreciere de piață implică de -28%** neexplicată în raport.
- **Banca verifică**: dacă alocarea construcții < 50% din CIN pentru o casă recentă, ridică steaguri roșii (subevaluare sau teren supraevaluat).

**Exemplul Breaza**:
- Teren 27.664 EUR, CIN+teren 178.735 EUR (deci CIN = 151.071 EUR), piață 135.267 EUR → alocare construcții 107.603 EUR.
- Depreciere implică: (151k - 107k) / 151k = **29% sub cost**. Dacă casa e <15 ani, asta e **nesustenabil** fără analiză explicită (obsolescență funcțională, supraofertă, condiție proastă).

**Recomandare**:
- Adaugă **verificare de consistență**: dacă |construcții alocate − CIN| > 20%, generează **avertizare obligatorie** + secțiune în raport: "Reconcilierea costului cu piața indică depreciere/apreciere de X%, explicată prin [obsolescență funcțională/locație inferioară/...]".
- Pentru garantare, **GEV 520 cere analiza riscului de garanție**: dacă piața < cost, explică de ce (piață în declin, supraofertă, stadiu șantier).
- Implementează **indicatori de risc automat**: (piață − cost)/cost; (construcții alocate)/CIN; dacă < 0.7 → risc sporit.

**Defensabilitate actuală**: 50%. Lipsește justificarea diferențelor; bancă prudentă poate respinge.

---

### 4. **Abordarea venitului — STRUCTURĂ CORECTĂ, lipsă de validare**

**Capitalizare directă + DCF**: metodologie corectă conform SEV 105 § 30-40.

**Dar lipsește**:
- **Validarea ratei de capitalizare**: SEV 105 § 33 cere "extragerea ratei din tranzacții comparabile sau analiza ratelor de piață." Откуда 7% sau 9%? 
- **Pentru garantare (GEV 520)**: abordarea venitului e **secundară** la rezidențial (predomină piața) dar **obligatorie** la comercial/industrial. Raportul trebuie să justifice de ce e/nu e folosită.
- **DCF**: rate de actualizare și exit cap rate — откуда? Dacă sunt inputuri manuale fără documentare, bancă respinge.

**Recomandare**:
- Adaugă **bază de date locală de rate de cap** (extracte din rapoarte publice ANEVAR/Colliers/CBRE) sau solicită input manual cu **obligație de citare sursă**.
- În raport: secțiune "Fundamentarea ratei de capitalizare/actualizare" cu calcul: (NOI observat / preț tranzacție) pentru ≥3 tranzacții comparabile.
- Dacă lipsesc date → **dezactivează abordarea** cu mesaj: "Insuficiente date de piață pentru aplicarea fiabilă a abordării venitului."

---

### 5. **Ce lipsește pentru garantare (GEV 520)?**

**Obligatorii pentru bancă, absente/insuficiente**:

1. **Analiza riscului de garanție (GEV 520 § 6)**: Ai mențiune, dar trebuie **cantitativă**:
   - Lichiditate (timp de vânzare estimat)
   - Comerciabilitate (restrângere piață, ex. casă >500 mp)
   - Risc juridic (servituți, litigii, CF provizoriu)
   - Risc tehnic (construcție informală, lipsă autorizație)
   - **Valoarea de lichidare forțată** (GEV 520 § 6.4): bancă cere explicit.

   **Acțiune**: Adaugă **grilă de risc** (6 categorii, scor 1-5, pondere) → risc total → include în raport + sugerează *valoare de lichidare = piață × (1 - factor risc)*, ex. 0.7-0.9.

2. **Certificarea conformității raportului (GEV 520 Anexa 1)**: Checklist explicit cerut de bancă — 18 puncte (ex. "Valoarea excludă TVA", "Costul exclude profit dezvoltator", "Ipoteza activitate continuă"). 

   **Acțiune**: Generează **Anexa de certificare** cu bifarea automată a punctelor aplicabile + declarație evaluator.

3. **Fotodocumentare obligatorie**: GEV 520 cere minim 6 foto (fațadă, interior, vecinătăți, acces, utilități, defecte). 

   **Verifică**: Raportul tău include? Dacă nu → adaugă secțiune cu placeholder-uri + instrucțiuni.

4. **Verificarea tranzacțiilor comparabile**: GEV 520 § 4.3.4 cere "confirmarea prețurilor prin surse independente (notar, agent)." Scrapingul de anunțuri = **prețuri de ofertă**, nu tranzacții.

   **Acțiune**: Avertizare clară: "Prețurile sunt extrase din OFERTE; evaluatorul trebuie să ajusteze la tranzacție (−5% la −15% tipic) sau să obțină prețuri confirmate."

---

## B. CONFORMITATE & RISC JURIDIC

### 6. **GDPR — Model INADECVAT pentru scară**

**Problema**: Anonimizarea înainte de AI e corectă în principiu, dar **execuția e riscantă**:

- **Re-identificare**: Chiar anonimizat, combinația `[ORAȘ]` + "casă 120 mp, 3 camere, an 2015" + street view din screenshot poate **triangula identitatea** (GDPR Art. 4(5): "persoană identificabilă indirect").
- **Screenshot-uri/foto**: Dacă includ numere poștale, plăcuțe, mașini → **date personale** (ICO UK a amendat pentru asta).
- **Jurnal de audit cu hash-uri**: Dacă hash-ul e pe date ne-anonimizate, jurnalul e **bază de date personale** → trebuie documente (politică de păstrare, drept de ștergere — cum îl implementezi pe SQLite local?).

**Recomandare (conformitate reală)**:
- **DPO**: Pentru uz profesional la scară, evaluatorul (ca operator date) trebuie să aibă **politică GDPR documentată**. Aplicația poate genera **șablon de politică** specifică ("Prelucrare date în evaluări imobiliare — baza legală: consimțământ client + interes legitim profesional").
- **Consimțământ explicit**: La crearea dosarului, generează **formular consimțământ GDPR** (Jinja template) pre-completat: "Subsemnatul [CLIENT] sunt de acord ca datele personale... să fie prelucrate pentru evaluare imobiliară conform..."
- **Limitare AI**: Documentează că AI primește **doar cifre agregat + text generic** (nu "Ion Popescu la Strada X" ci "Proprietate P1 în zona Z1"). Păstrează **log de anonimizare** (ce a fost înlocuit) separat, șters după livrare raport.
- **Foto**: Adaugă **funcție de bluare automată** (plăcuțe, feței) înainte de includere în raport dacă e trimis la AI pentru descriere.

**Risc rezidual**: 40% — ești mai bine decât majoritatea, dar nu suficient pentru audit ANSPDCP serios.

---

### 7. **AML — Risc MAJOR, model juridic periculos**

**Problema critică**: "Propune, evaluatorul transmite" e corect **în principiu**, dar **execuția actuală are goluri letale**:

#### 7a. **Textele generate (RTS/RTN/norme) — RĂSPUNDERE PENALĂ**

- **Legea 129/2019 Art. 33**: Raportarea cu **rea-credință sau neglijență gravă** = **închisoare 1-5 ani**.
- Un RTS generat de AI cu **falsuri** (ex. "beneficiar real verificat în baza X" când nu a fost) poate fi considerat **neglijență gravă** chiar dacă evaluatorul l-a revizuit (standardul e "diligenţă profesională", nu doar "am citit").

**Acțiune obligatorie**:
- **Disclaimer de necitire**: La fiecare document AML generat, alert box roșu: ⚠️ **"ACEST DOCUMENT ESTE DRAFT NEVERIFICAT JURIDIC. Art. 33 Legea 129/2019 prevede închisoare pentru raportare neglijentă. Verificați fiecare afirmație cu avocat înainte de transmitere."**
- **Șablon minimal, nu AI**: Pentru norme interne/proceduri, folosește **template fix** (copiat din ghiduri ONPCSB publice), nu generare AI — risc prea mare.
- **Generare RTS/RTN dezactivată implicit**: Funcția să ceară **activare explicită** + bifă "Accept răspundere penală Art. 33" înainte să genereze.

#### 7b. **Screening liste (sancțiuni/PEP) — GAURĂ CRITICĂ**

- **Norme ONPCSB 37/2021 Art. 11**: "Identificarea PEP și a persoanelor sancționate se face prin consultarea bazelor de date actuale."
- "Placeholder injectabil" = **neconformitate totală**. Un evaluator care BIFEAZĂ "verificat PEP" fără screening real = **încălcare Art. 8 alin. 2** (KYC insuficient).

**Acțiune URGENTĂ**:
- **Integrare API real** înainte de lansare: World-Check (Thomson Reuters, plătit), OpenSanctions (open-source, gratis), EU Sanctions Map, OFAC. 
- **Sau**: Dezactivează complet funcția cu mesaj: "Screening PEP/sancțiuni trebuie făcut manual de evaluator pe [link-uri oficiale]. Aplicația NU efectuează verificare automatică."
- **Nu bifa fără verificare**: Dacă lista e goală, raportul de risc trebuie să spună: "⚠️ Screening PEP/sancțiuni neefectuat — evaluator trebuie să verifice manual."

#### 7c. **Prag numerar 10.000 EUR — INCOMPLET**

- **Art. 6 alin. 1 lit. b**: Pragul e **3.000 EUR** pentru tranzacții ocazionale (nu client permanent), nu 10.000 EUR.
- **Norme 37/2021 Art. 5**: KYC simplificat până la 15.000 EUR (risc redus), nu standard.

**Acțiune**: Validează **cu avocat AML** toată logica de praguri — ești pe teren minat.

---

### 8. **AI redactează analiza — Risc MODERAT, gestionabil**

**Nu e periculos DACĂ**:
- Evaluatorul revizuiește (implementat ✓)
- AI primește date anonimizate (implementat ✓)
- Raportul indică clar: "Text asistat de AI, revizuit și asumat de evaluatorul autorizat [nume], [număr autorizare]."

**Problema**: **Hallucinațiile** — AI poate inventa "conform studiului ANEVAR 2024..." inexistent.

**Acțiune**:
- **Validare factual**: După generare, rulează **checker automat** (regex) care detectează afirmații factuale nesusținute: "conform studiului X", "datele arată Y" fără referință → evidențiază cu galben + tooltip: "⚠️ Verificați sursă."
- **Restricție prompt**: Instrucțiuni explicite: "Nu inventa surse. Dacă afirmi date factuale, folosește doar cele din contextul furnizat. Pentru interpretări, folosește formulări: 'analiza sugerează', 'poate indica'."
- **Audit trail**: Loghează prompt-ul și răspunsul complet (anonimizat) în jurnal → dacă e litigiu, evaluatorul poate arăta: "Am verificat textul generat înainte de includere."

**Răspundere**: Evaluatorul răspunde **întotdeauna** — AI e doar instrument (ca Excel). Dar trebuie să facă revizuirea **verificabilă** (nu doar "am citit").

---

## C. ARHITECTURĂ & INGINERIE

### 9. **Server-rendered + .exe offline — Alegere CORECTĂ pentru target**

**Pro**:
- Offline = confidențialitate maximă (datele nu ies din calculator).
- Single .exe = fără instalare complexă (public netehnică).
- Jinja = modificări de template ușoare (evaluatorul poate customiza header-uri).

**Contra (minor)**:
- UX limitat față de SPA (dar acceptabil pentru uz profesional, nu consumer).
- Distribuție (avertizmente SmartScreen) — real dar rezolvabil.

**Compromis ratat — MINOR**: 
- Lipsa **backup automat**. SQLite local = dacă se corupe/șterge accidental, pierdere de date. 
  - **Acțiune**: Adaugă export automat periodic (ex. JSON/ZIP la fiecare salvare) într-un folder `backups/` cu rotație 30 zile.

**Verdict**: Arhitectura e potrivită. Nu schimba.

---

### 10. **Scalare/mentenanță — Riscuri LOW, dar pregătește-te**

**Riscuri identificate**:

1. **FastAPI + Jinja amestec**: Pe termen lung, logica se scurge în template-uri (Jinja devine "PHP hell"). 
   - **Prevenție**: Enforced **logică zero în Jinja** — doar afișare; toate calculele în routere/servicii.

2. **SQLite concurență**: Single-user acum, dar dacă vrei multi-utilizator cloud later, SQLite nu scales (write lock).
   - **Pregătire**: Modelele Pydantic fac abstracție — poți migra la Postgres cu <500 linii.

3. **Monolit 10k+ linii**: Pe la 15k linii, mentenanța devine greoaie.
   - **Acțiune**: Extrage module mari (AML, generator raport) în **pachete separate** (`anevar_aml`, `anevar_docgen`) cu API clar → reutilizabile, testabile izolat.

4. **Dependență de AI SDK**: Anthropic/Perplexity pot schimba API → breakage.
   - **Ai deja**: Fallback la template ✓. 
   - **Adaugă**: Versiunea SDK fixată în `requirements.lock` + **abstracție** (interfață `AIProvider` → `AnthropicProvider`, `PerplexityProvider`) → switch fără rewrite.

**Verdict**: Arhitectura actuală e sustenabilă până la ~5x creștere (50k linii / 1000 utilizatori). După → refactor modular.

---

### 11. **Scraping portaluri — Risc MAXIM, nesustenabil**

**Probleme legale**:
- **ToS**: Imobiliare.ro/Storia au clauze anti-scraping. Risc de **C&D (cease & desist)** sau blocare IP.
- **GDPR**: Anunțurile conțin contacte (tel, email) = date personale. Scrapingul = prelucrare fără bază legală → **Art. 83(5) GDPR** = amenzi până la 20M EUR sau 4% cifră afaceri.
- **Baze de date sui generis** (Directiva 96/9/EC): Extracția substanțială = încălcare drept sui generis → **daune-interese**.

**Probleme tehnice**:
- **Fragilitate**: Orice schimbare layout → breakage. Întreținere costisitoare.
- **Rate limiting**: Portalurile detectează bot → CAPTCHA/blocare.

**Alternative (URGENTE)**:

1. **API oficial**: Contactează Storia/Imobiliare.ro pentru **acces API comercial**. Cost (probabil câteva sute EUR/lună) < risc juridic.

2. **Parteneriat ANEVAR**: Dacă asociația are acord cu portaluri → negociază acces pentru membrii.

3. **Bază de date proprie**: Îi încurajezi pe utilizatori să introducă manual comparabile → construiești bază comună (anonimizată, cu consimțământ) → ANEVAR devine agregator.

4. **Import CSV**: Oferă template CSV → evaluatorul exportă din portaluri (manual/semi-automat cu extension browser) → importă în aplicație. Mai greoi dar **100% legal**.

5. **Screening specializat**: Integrare cu **servicii B2B** (ex. Bright Data, Apify) care au acorduri legale cu surse → deleghezi riscul.

**Acțiune IMEDIATĂ**:
- **Disclaimer**: "⚠️ Descoperirea automată folosește anunțuri publice. Utilizatorul e responsabil să verifice conformitatea cu ToS platformelor. Producătorul nu răspunde pentru încălcări."
- **Rate limiting agresiv**: Max 1 request/5s, max 20/sesiune → reduce riscul de detecție.
- **Planifică migrare**: Scraping-ul e **tehnică de bootstrap**, nu soluție long-term.

**Verdict**: Risc juridic **RIDICAT**. Funcția e utilă dar nesustenabilă — prioritizează alternative în 6-12 luni.

---

## D. PRODUS & ADOPȚIE

### 12. **Ce face raportul respins de bancă? Top 3 motive**

1. **Ajustări totale excesive fără justificare** (>25% brut sau >15% net) — risc în grila ta actuală.
   - **Fix**: Adaugă validări automate + avertizări.

2. **Lipsă certificare de conformitate GEV 520** (Anexa 1 checklist) — lipsește.
   - **Fix**: Generează anexa automat.

3. **Comparabile neconfirmate** (oferte, nu tranzacții) fără ajustare explicită ofertă→tranzacție sau surse independente.
   - **Fix**: Obligă input "ajustare ofertă" (default -10%) + tooltip "GEV 520 cere confirmare prin notar/agent."

**Bonus**: Inconsistență cost vs. piață neexplicată → fix discutat la pct. 3.

---

### 13. **Distribuție — Probleme practice**

1. **SmartScreen**: `.exe` nesemnat → avertizare la descărcare. 
   - **Fix**: **Code signing certificate** (Sectigo, DigiCert, ~300 EUR/an). Costsitor dar elimină fricțiuni la adopție.

2. **Win7 incompatibil**: Python 3.12 nu rulează.
   - **Risc low**: Win7 support a expirat 2020; <5% piață profesională. Dacă e cerere, backport la Python 3.9 (ultimul cu Win7) costă ~2 zile.

3. **Dimensiune (176 MB)**: OK pentru LAN/USB, problematică pentru download pe net lent.
   - **Optimizare**: Exclude dependențe fat (ex. Pillow cu codecs nefolosite) → posibil sub 100 MB.

4. **Update mechanism lipsă**: Cum primește utilizatorul versiunea nouă? Manual e greoi.
   - **Fix**: Adaugă **check update automat** la pornire (GET pe GitHub Releases API) → notificare + link download.

---

### 14. **Top 3 priorități înainte de uz real (ordinea contează)**

#### **1. CONFORMITATE AML (CRITIC — risc penal)**
- Validare juridică completă (avocat specializat AML) a tuturor textelor generate.
- Integrare screening PEP/sancțiuni real SAU dezactivare totală cu disclaimer.
- Audit extern (ONPCSB oferă consultanță) — 1-2 zile, ~1000-2000 EUR, **non-negociabil**.

**Estimare**: 3-4 săptămâni, 3000-5000 EUR (avocat + screening API).

---

#### **2. VALIDARE METODOLOGIE DE EVALUARE (CRITIC — risc de respingere)**
- **Peer review ANEVAR**: Cere unui evaluator senior autorizat (sau mai bine 3) să verifice:
  - Grila teren (selecție pe ajustare minimă proprietate).
  - Grila casă (ajustare liniară suprafață).
  - Reconciliere + alocare.
  - Verifică pe 5-10 dosare reale → compară valori aplicație vs. manual.
- **Validare bancă**: Trimite raport demo la 2-3 bănci (ING, BCR, BRD) → feedback formal ce lipsește.
- **Fix discrepanțe identificate** (ex. adaugă verificări consistență cost vs. piață).

**Estimare**: 2-3 săptămâni (organizare + revizii).

---

#### **3. RAFINARE CONFORMITATE GDPR + JURIDIC (IMPORTANT — risc de amendă)**
- Generează **package GDPR complet**: politică prelucrare, formular consimțământ, registru prelucrări (ANEVAR ca operator, aplicația ca instrument).
- **Disclaimer juridic clar** în toate documentele generate: "Document generat automat — verificare juridică obligatorie înainte de utilizare. Producătorul nu răspunde pentru erori."
- **Termeni de utilizare** (EULA) la prima pornire: enumeră limitări răspundere, obligația verificării outputurilor, conformitate ToS surse externe.

**Estimare**: 1-2 săptămâni, 1000-2000 EUR (avocat GDPR).

---

**Restul** (code signing, API portaluri, optimizări UI) sunt **nice-to-have** — poți lansa fără, cu disclaimere adecvate.

---

## E. VERDICT FINAL

### **Ce merge bine** (chiar foarte bine):
- **Calitate inginerească**: 375 teste, 92% acoperire, CI, linting — top 5% proiecte pe care le-am văzut.
- **Arhitectură potrivită**: Offline, single .exe, server-rendered — alegeri corecte pentru target.
- **Viziune corectă**: "Om în buclă", AI asistent (nu decident) — filosofia e sănătoasă.
- **Documentare exhaustivă**: Acest dosar de review e model de urmat.

### **Ce e periculos** (oprește lansarea):
1. **AML fără validare juridică** — risc penal (închisoare) pentru utilizator. **Blocker absolut.**
2. **Scraping ilegal** — risc GDPR + ToS. **Blocker medium-term** (6-12 luni).
3. **Metodologie nevalidată de practician** — risc de respingere rapoarte → reputație distrusă. **Blocker comercial.**

### **Ce e rafinat dar acceptabil**:
- Grila cu ajustări — defensabilă cu documentare suplimentară.
- GDPR anonimizare — peste medie dar nu bulletproof.
- AI narativ — OK cu verificări factuale adiționale.

---

## F. RECOMANDARE FINALĂ

**NU lansa în producție fără**:
1. Audit juridic AML complet (3-4 săptămâni).
2. Peer review metodologie de la ≥2 evaluatori ANEVAR seniori (2-3 săptămâni).
3. Package GDPR + disclaimere (1-2 săptămâni).

**Timeline realist până la uz real**: **2-3 luni** de la acum (dacă începi imediat validările).

**Cu fixurile de mai sus**, aplicația poate fi **excelentă** — ai fundație tehnică solidă; lipsesc validările de domeniu și juridice care transformă "prototip impresionant" în "instrument profesional utilizabil".

---

**Întrebare pentru tine**: Ai buget + acces la expertise juridică AML și evaluatori seniori pentru validările astea? Dacă nu, prioritatea 0 e să le identifici — fără ele, proiectul e imposibil de lansat responsabil.

Mult succes — e un produs ambițios și bine gândit. Cu due diligence corectă, poate deveni standard în industrie. 🎯


## x-ai/grok-4.3

**Review independent — Asistent evaluare ANEVAR (MVP)**

Evaluarea de mai jos se bazează exclusiv pe documentația furnizată. Nu am acces la cod. Voi răspunde structurat la cele 14 întrebări, cu accent pe riscuri reale de reglementare și conformitate (cum ai cerut).

### Metodologie

**1. Grila teren în 2 etape + selecție pe ajustarea brută minimă (etapa de proprietate)**  
Metoda este **defensabilă**, dar fragilă.  
Problema principală: alegerea comparabilului exclusiv pe baza ajustării brute minime de la etapa a doua (proprietate) ignoră magnitudinea ajustărilor din prima etapă (tranzacție). O bancă sau un reviewer ANEVAR poate argumenta că ai selectat un comparabil "ieftin" care necesita ajustări mari la nivel de tranzacție.  
Recomandare: adaugă în raport **obligatoriu** o coloană cu ajustarea brută totală (etapa 1 + etapa 2) și justifică de ce ai ales criteriul "ajustare brută minimă pe etapa de proprietate". Altfel riscul de contestare este real.

**2. Grila casă pe preț total cu ajustare de arie utilă**  
Abordarea este **acceptabilă** în practică, dar nu este cea mai elegantă.  
Tratând diferența de suprafață ca ajustare valorică (preț unitar × Δmp) poți crea distorsiuni când proprietățile diferă semnificativ ca mărime. Mai corect ar fi să folosești **preț unitar ajustat** și apoi să refaci valoarea totală. Diferența nu este dramatică la intervale mici de suprafață, dar devine vizibilă la proprietăți foarte diferite.

**3. Reconciliere + alocare (construcții = proprietate − teren)**  
Standard și corect pentru evaluări de garantare. Nu văd probleme majore aici.

**4. Abordarea prin venit**  
Structura (capitalizare directă + DCF) este corespunzătoare. Singura observație: grila de chirii comparabile ar trebui să aibă același tratament riguros ca și grilele de vânzare (ajustări secvențiale + aditive). Momentan pare mai sumar.

**5. Elemente lipsă pentru garantare**  
- Analiza **Highest and Best Use** (HBU) este menționată vag. La garantare băncile cer uneori o secțiune explicită.  
- Lipsa unei verificări de **sensitivity analysis** pe rata de capitalizare și pe valoarea reziduală (în DCF).  
- Nu apare o secțiune clară de **marketability / lichiditate** a garanției (GEV 520 cere uneori).

### Conformitate & Risc

**6. GDPR (anonimizare înainte de AI)**  
Modelul este **suficient de bun** pentru un instrument local.  
Riscul rezidual real este re-identificarea prin combinație de date (adresă + suprafață + an construire + client). Dacă LLM-ul primește chiar și date parțial anonimizate, riscul există. Soluția actuală (anonimizare locală + demascare locală) este pragmatică și corectă.

**7. Modul AML**  
Abordarea "propune, evaluatorul transmite" este **corectă legal**.  
Ce trebuie validat juridic neapărat:
- Textele RTS/RTN (art. 38 Legea 129/2019)
- Logica de stabilire a categoriei de risc (redus/standard/sporit)
- Indicatori de suspiciune

Fără validare juridică, acest modul este **cel mai periculos** din aplicație din punct de vedere al răspunderii.

**8. Răspundere profesională (text AI)**  
Da, este periculos.  
Evaluatorul semnează, dar dacă LLM-ul produce un text cu nuanțe greșite (chiar dacă evaluatorul "revizuiește"), ANEVAR sau banca pot argumenta lipsă de diligență profesională. Riscul crește dacă evaluatorul folosește textul AI ca bază principală. Ar trebui un disclaimer explicit în raport sau o funcție care marchează clar secțiunile generate de AI.

### Arhitectură & Inginerie

**9. Server-rendered + .exe offline**  
Alegerea este **corectă** pentru publicul țintă. Un evaluator ANEVAR nu vrea SaaS cu date sensibile. Compromisul ratat: ați putea oferi și o variantă web locală (localhost) pentru cei care vor multi-monitor / experiență mai fluidă, dar .exe rămâne varianta sigură.

**10. Scalare / mentenanță**  
Arhitectura actuală (FastAPI + Jinja + SQLite) este potrivită pentru single-user. Riscurile reale sunt:
- refactoring-ul logicii de calcul când apar modificări SEV/GEV
- dependența de PyInstaller (fragil la update-uri de biblioteci)

**11. Scraping portaluri**  
Risc **ridicat** atât tehnic cât și legal.  
La prima plângere de la un portal sau la prima modificare majoră de layout, funcționalitatea moare. Ar trebui tratat ca sursă **secundară** (nu primară). Alternativa realistă pe termen mediu este integrarea cu baza de date ANEVAR (dacă devine disponibilă membrilor).

### Produs & Distribuție

**12. Ce ar face raportul respins de bancă**
- Lipsa justificării ajustărilor (valorile "exemplu" din grile)
- Formatul .docx diferit de template-ul băncii
- Secțiune de risc garanție (GEV 520) prea generică
- Lipsa referințelor la surse oficiale (BIG, ANCPI)

**13. Distribuție (.exe nesemnat)**  
Problemă reală de adopție. Mulți evaluatori vor vedea avertismentul SmartScreen și vor renunța. Semnarea codului (EV code signing) ar trebui să fie prioritară.

**14. 3 priorități înainte de uz real**

1. **Validare juridică AML** (cel mai important risc de conformitate)
2. **Testare cu minimum 3-4 bănci** pe rapoarte reale (ceea ce cer ei în plus față de SEV)
3. **Semnare cod + documentație clară** privind limitările ajustărilor (ca evaluatorul să nu folosească valorile implicite fără verificare)

### Concluzie generală

Aplicația este **bine gândită tehnic** și respectă principiul "om în buclă". Cel mai mare risc nu este arhitectura, ci **zona gri de conformitate** (AML + text generat de AI + ajustări implicite). Dacă aceste trei zone nu sunt adresate, riscul de răspundere profesională rămâne semnificativ, chiar dacă aplicația funcționează tehnic impecabil.
