# Răspuns LLM Council — modulul „Descoperă" (2026-06-07)

> Panel: GPT-5.1 · Claude Sonnet 4.5 · Gemini 3.1 Pro (chairman) · Grok 4.3. Întrebări: Q1–Q10 din council-brief.md.

---

# Council Answer (Chairman: google/gemini-3.1-pro-preview)

Salutare! În calitate de Președinte al Council-ului de Modele AI, am analizat și sintetizat concluziile paneliștilor noștri (care au inclus analize tehnice, de produs și de evaluare ANEVAR). Rezultatul de mai jos reprezintă „înțelepciunea colectivă” a consiliului, filtrată pentru a fi maxim de acționabilă pentru echipa voastră tehnică și de produs.

Vom contesta agresiv tiparele care par a fi doar împrumutate din e-commerce sau de la motoare clasice de căutare; piața imobiliară și rigorile ANEVAR necesită o cu totul altă finețe. 

Iată răspunsurile consolidate, cu accent masiv pe cerințele voastre cheie (Q1, Q4, Q9, Q10).

---

### Q1 — Criterii principale, ponderi, formule per categorie
**CONTESTAREA PREMISEI:** Actualul model de similaritate continuă pură (distanță liniară) este deficitar în real-estate. Diferențele la anul construcției în România nu sunt liniare, ci au **„Value Cliffs” (praguri abrupte)** — ex. diferența între 1975 și 1979 nu e doar 4 ani matematici, ci „înainte sau după cutremurul din 1977”. De asemenea, aplicarea aceluiași calapod pentru un apartament și o hală industrială e o greșeală.

Strategia corectă implică 2 pași: **(1) Filtrul de eligibilitate** (must-have-uri invizibile în scor, care doar triază lista) urmat de **(2) Scor de similaritate**. 

Pentru risc LLM (Stare și Finisaj, momentan ×4 și ×3): Ele adunate dictează prea mult dintr-un input volatil creat pentru marketing de către agenți. **Acțiune:** Reduceți suma ponderilor lor, marcați-le vizual (cu un semnal de tip warning ⚠️ „Estimat de AI”) și cereți **Confirmare Manuală**. Un buton de „Confirm” lângă atribut în UI transformă estimarea într-un adevăr validat, moment în care poate influența scorul la capacitate maximă. 

**Propuneri specifice per categorie (Scoring):**
*   **#1 Casă+Teren (Revizuit):** Suprafață (×6), **Teren (×5)** — în RO valoarea caselor e puternic dependentă de teren; vechea pondere ×1 era eronată, An (×4 — ponderat în trepte decadale/cutremur), Stare LLM (×2), Finisaj LLM (×1), *[Promovare metadata extrasă]*: Număr camere (×2). 
*   **#2 Apartament (Extrem de URGENT):** Aici piața = 60-70%. *Filtru obligatoriu:* ±1 cameră. *Scoring:* Suprafață (×7), **Etaj (×5)** — formula nu e liniară (un etaj intermediar 3 vs 4 e d=0.1, dar Parter/Ultimul vs Intermediar se penalizează sever cu d=0.7), **Nr. Camere (×4)**, An (×3), Stare (×2).
*   **#3 Spațiu Industrial:** *Nu prioritizați scoringul încă.* Aveți nevoie de date. Storia/Imobiliare sunt foarte slabe aici. Implementați repede **parser pe VDI.ro și Imoradar24**. *Scoring vizat ulterior:* Suprafață (×5), Înălțime liberă (×5), Acces TIR (×4) - *pe acestea 2 extrageți-le boolean cu prompturi simple*, Energie trifazic/Utilități (×3). 
*   **#4 Teren Agricol:** Suprafață (×5, *calculată logaritmic*, diferența de la 500mp la 1000mp nu e la fel cu 15.000mp vs 15.500mp), Deschidere la drum/Acces (×4), Categorie de folosință (arabil vs pășune) (×4) - utilități dacă există.
*   **#5 Proprietate Specială:** (Catch-all). **Contestăm premisa:** Nu se poate crea un scor numeric universal valid. Transformați UI-ul într-o abordare „asistată semi-manual”. Când userul intră pe #5, obligă-l să aleagă el din check-boxuri: „Ce atribute contează la această căutare? (Capacitate / Vitrină comercială / etc.)”. Calculați similaritatea exclusiv pe axele alese on-the-fly.

---

### Q4 — Distanța în ranking (Când și cum o tratăm?)
**CONTESTAREA PREMISEI:** Distanța introdusă cu greutate mare în forumula procentuală va genera erori, deoarece pin-urile / descrierile locațiilor de pe agregatoare sunt adesea inexacte („aproximari de zonă”). Dacă penalizezi cu un algoritm strict niște date geografice fuzzy, scorul de 0-100% devine inutilizabil. 

**Recomandare:** Distanța este **dependentă de context**, nu universală.
1.  **Pentru #2 Apartamente & #1 Case în marile orașe:** O integrați ca pe un **Tie-Breaker filtru gradual**. Scorul se calculează fără distanță (0-100%). Dacă proprietatea depășește o rază, aplicați o penalizare separată la final (ex: „Scor 90% (-15% pentru distanță 3km din alt cartier)”). 
2.  **Pentru #3 Industrial & #4 Teren:** Distanța contează, dar **nu față de subiect, ci față de infrastructură!** (Autostradă, Drum județean betonat, acces CF). 
3.  **Implementare:** Fără API-uri Google scumpe. Descărcați dump-ul OSM (OpenStreetMap România) + o bază de date SIRUTA și rulați un geocoding local (Offline cu PostGIS). Efortul e de 2-3 zile de implementare, costul ulterior pe server este zero.

---

### Q2 & Q3 — Criterii secundare și Granularitate locație
*   **Q2 (Secundare):** Sistem actual: Criteriile secundare din UI stau degeaba și doar bifează dacă există în text. Schimbați abordarea: transformați-le în **"Boosters" (sporuri de valoare)**. Când evaluatorul caută „Lift” sau „Acoperiș nou”, sistemul le găsește și îi afișează un prompt transparent: *"Am găsit Lift. Confirmă pentru a adăuga +10% la relevanță"*. Utilizatorul controlează cât de importantă e acea descoperire textuală, nu un black-box.
*   **Q3 (Locație):** Granularitatea o faceți pe praguri algoritmice. Sate/Comune: nivel de localitate. Orașe (<50k loc): localitate/cartier. Orașe mari (ex. București, Cluj, >100k locuitori): *Sub-zonă / Rază*. Un apartament în Primăverii vs unul în Pantelimon sunt obiecte economice diferite, deci macro-cartierul sau distanța scurtă (< 1.5 km) trebuie tratate ca filtrul de zero/unu. Extrageți zonele din text offline dacă nu se poate căuta post-filtrare pe site-uri.

---

### Q5, Q6, Q7 — Stack, Extracție NLP și Surse (Mutați-vă de pe Claude / OLX)
*   **Cost & Layering (Q5/Q7):** Un „consiliu de modele multiple” e prea scump și adaugă latență la nivelul vostru curent, unde problema e HTML-ul murdar, nu semantica filosofică. Mutați pipeline-ul de extracție pe un model rapid și ieftin dedicat strictului JSON (Llama 3.3 70B sau Gemini 1.5 Flash via openrouter), a căror diferență factuală de performanță pe field-extraction față de Claude e nulă, dar reduc costurile de ~10x. Folosiți Claude Doar ca fallback dacă logica deterministă din spate ține scorul de confidență scăzut. 
*   **Discovery Web:** LLM Search-urile tip Perplexity sunt groaznice pe crawlat real-estate autohton din cauza site-urilor statice, SPA-urilor și protecțiilor Anti-Scraping. *Mutați efortul în crearea unui parser pentru Imoradar24* (folosiți-l doar pentru **discovery**, pentru indexare, apoi din el trasați URL-ul site-ului original —Storia, Imob— și faceți scrape acolo, căci pe agregator datele stau prost).
*   **Ce facem cu OLX (Q6)?** Scoateți-l din formula de ranking. Aglomerați evaluatorul cu proprietăți fără suprafață. **Pivot:** Păstrați OLX integrat via API propriu strict pentru a oferi „Sanity Check al pieței de preț / mp pe zonă”, afișat ca un grafic/avertisment lateral, nu ca și opțiuni comparabile scorate.
*   **Grade de încredere:** Aplicați-le prin etichete vizuale per **Atribut** (ex: *„An Construcție 🟢 Structurat”*, *„Finisaj 🟡 Estimat LLM”*). Oamenii nu au încredere în scoruri globale abstracte.

---

### Q9 — Ce NU ați întrebat dar ar trebui? (Premise demontate și Unghiuri oarbe)
V-ați concentrat pe "cum să obținem o cifră perfectă de 87% similaritate". În realitatea unui evaluator ANEVAR, asta este doar prima parte a problemei. Ce lipsește: 

1. **Lipsa Ground Truth (Validare Proactivă):**
Nu ați specificat cum veți măsura succesul algoritmului. Puneți sistemul în față la 5 evaluatori ANEVAR cu portofoliul lor. Dacă din Top 5 al sistemului lipsesc alegerile lor umane în mod constant, aplicația doar generează un zgomot inutil. Trebuie să logați de fiecare dată **ce respinge evaluatorul din lista voastră** pentru a înțelege exact ce greșesc regulile.
2. **Unda Temporală (Decay vs Inflație):**
Anunțurile imobiliare vechi de 8 luni nu au același ecou pe fondul pieței cu unele de ieri (mai ales în piețe dinamice). Când aduceți comparabile vechi, adăugați penalizări de vechime temporală a prețului pe axa vremii.
3. **Formatul de ieșire (Raportul):**
De ce folosește acest tool un evaluator? Să-l pună într-un raport! Nu aveți funcție de „Exportă Comparabile ANEVAR” (Tabel cu Subiect vs Candidați + Căsuță de Justificare Generată pt deviații). Dacă îl lăsați pe utilizator să facă copy-paste manual, n-ați inovat procesul de business destul, ați creat doar un motor de search mai deștept.

---

### Q8 — Ordinea de PRIORITATE pentru echipă (Execuția pragmatică)

**P0 (URGENT / 1-2 Sprint-uri):**
*   Demuplați modelul de casă și refactorizați de urgență Scoringul pentru Apartamente (#2), introducând logicile de Număr Camere și Etaj în formulă, cu pondere mare.
*   Reduceți ponderea AI-ului pe Stare/Finisaj și adăugați Flow-ul de Aprobare vizuală a atributelor nesigure.
*   Treceți pe la Layer-ul LLM mai ieftin (Llama/Gemini Flash) ca să salvați buget.

**P1 (Săptămâna 3-6):**
*   Urcați parser-ul pentru VDI.ro, deschizând verticala categorii #3 (Industrial). Acoperirea este mai importantă decât acuratețea algoritmului în această etapă.
*   Geocodarea offline (PostGIS + OSM) pentru implementarea corectă a filtrelor geografice.

**P2 (Viitor/ Backlog imediat):**
*   Feature-ul de „Export în format ANEVAR Standard” - killer feature pentru monetizare și retenție.
*   Integrare Imoradar24 pentru discovery la sate, unde Storia scade drastic sub radar, urmată de scrape la destinație.

---

### Q10 — Cea mai INOVATOARE Idee (Mișcarea îndrăzneață)
Dacă am fuziona cele mai bune direcții neexplorate (propuse de panel) ale modelului vostru, ideea care v-ar ridica exponențial peste competiție este:

**Trecerea la Evaluarea Vizuală asamblată pe un Copilot Reinforcement Learning (Ocolirea cuvintelor mincinoase)**

1.  **Evaluatorul Vizual Hibrid:** Extragerea „stării” (1-5) și a „finisajelor” (1-4) dintr-un text scris de un agent ("superb", "complet renovat") este sursa masivă a problemelor voastre. Faceți un pas înainte: Da-ți scrape la primele 3 imagini ale proprietății și rulați un prompt de clasificare cu un Vision-Language Model (ex. GPT-4o-Vision) *„Privește aceste imagini. Dă un scor structural (1-5) pentru perete/pardoseli și ignoră orice descriere a agenților”*. 
2.  **Copilotul care „Învață din Plictiseală/Respingere”:** Integrați acest output vizual cu noul layout în care omu' pune Feedback la rezultate (Da/Nu). Când un evaluator adaugă o comparabilă care era abia pe Rank-ul 5 în grila voastră (și le ignoră pe primele 4), antrenați asincron un model ușor care mapifică "ce îl face pe Evaluator fericit" (probabil favorizează micro-locații specifice, surse specifice sau un prag de preț/mp) – sistemul devine din static (bazat strict pe formule) într-unul custom, per agenție / per evaluator. Asta va crea un *lock-in* al clienților: sistemul va fi „prea bun și prea antrenat pe preferințele mele ANEVAR” ca ei să mai renunțe vreodată la serviciul vostru. 

*Cel mai mare risc:* Costurile superioare de processare a imaginilor și creșterea volumului de scraping de trafic greu. Aș lansa funcția ca opțiune „Deep Scan/X-Ray Scan Premium”, activată manual (pe un buton separat), doar acolo unde textele sunt scurte și confuze, iar user-ul e dispus să aștepte 3 secunde în plus.

Sperăm că detalierea și acuratețea cuvântului nostru vor acționa ca un playbook de produs gata te implementat! Spor la codat!

## Peer ranking (lower avg = better)

1. **openai/gpt-5.1** — avg rank 1.5 (4 votes)
2. **anthropic/claude-sonnet-4.5** — avg rank 1.75 (4 votes)
3. **google/gemini-3.1-pro-preview** — avg rank 2.75 (4 votes)
4. **x-ai/grok-4.3** — avg rank 4.0 (4 votes)

*Council members: openai/gpt-5.1, google/gemini-3.1-pro-preview, anthropic/claude-sonnet-4.5, x-ai/grok-4.3*

## Individual member responses

### openai/gpt-5.1

Răspund pe rând la Q1–Q10. Voi fi foarte concret, cu propuneri acționabile și prioritizate. Contest explicit unele premise la Q1, Q4, Q9, Q10.

---

## Q1 — Criterii principale per categorie (cu ponderi + formule)  
+ prioritatea între „acoperire” vs „scoring” + ce promovăm în scor

### Premisă de contestat
Modelul actual pornește de la ideea „similaritatea = sumă ponderată de diferențe pe câteva atribute”. În evaluare ANEVAR, comparabilitatea e mult mai condiționată de:
- localizare / micro-localizare;
- tipologic (casă vs vilă P+M vs duplex etc.);
- uz și segment de piață (industrial logistic vs producție, retail vs birouri).

Aș trata problema în 2 straturi:
1. Filtrare de „eligibilitate” (must-have / range strict), apoi  
2. Scor de similaritate (fine-tuning între comparabile deja rezonabile).

Dacă nu separați asta, veți avea scoruri frumoase pentru comparabile fundamental nepotrivite (ex: apartament la 1977 în cartier complet diferit, dar cu suprafață + an similare).

### Notă despre formule
Păstrați formula actuală (distanță liniară normalizată, tăiată la 1) ca default, dar:
- folosiți **scale diferite** per criteriu (nu totul raportat la 25 de ani, 100% diferență etc.);
- introduceți **„binning”** la unele atribute (ex: anul înainte/după 1989; înainte/după 2008; clustere de suprafețe).

---

### #1 Casă + teren (categoria deja modelată)

#### 1.1. Recomand structura în 2 pași:

**(A) Filtru de eligibilitate (înainte de scor):**
- Tip proprietate: casă/vilă/duplex — exclud blocuri convertite, spații comerciale.
- Localizare:
  - obligatoriu: aceeași localitate (sau aceeași zonă urbană pentru marile orașe; vezi Q3);
  - opțional filtrabil: același cartier / rază max (dacă aveți geocodare).
- Interval suprafață utilă locuință: 50–200% vs subiect (ex: dacă subiectul are 120 mp, accept 60–240 mp).
- Interval teren: 20–500% (mai permisiv, dar filtrabil de utilizator).
- Valabilitate anunț / stadiu (activ, nu „archived” – dacă puteți deduce).

**(B) Criterii de scor principal (max 100), propunere:**

Voi da ponderi relative (suma ≈ 100). Puteți păstra formula actuală `1 − Σ(w*d)/Σ(w)`.

1. Localizare fină (distanță sau proximitate de zonă) – **25**  
   - Dacă nu aveți geocodare:  
     - d=0 dacă același cartier/zonă micro (când e menționat);  
     - d=0.3 același oraș;  
     - d=0.7 localități imediat învecinate;  
     - d=1 altă zonă (chiar dacă portalul le bagă la „Breaza”).  
   - Dacă introduceți geocodare:  
     - d = min(dist_km / D_max, 1), cu D_max ~3 km pentru oraș mic, 7–10 km pentru oraș mare.

2. Suprafață utilă locuință – **20**  
   - NU suprafață construită brută dacă aveți și utilă.  
   - d = min(|s−c| / (0.3s), 1) – penalizați după ±30% diferență.

3. Teren – **10**  
   - d = min(|s−c| / (1.0s), 1) – adică la dublu/înjumătățire aveți d≈1.  
   - Pentru urban dens, ponderea e mai mică sau ajustabilă de user.

4. An construcție – **15**  
   - În loc de |s−c|/25, folosiți praguri:
     - dacă ambele după 2000 → d = |s−c| / 20 (mai strict, cazuri moderne);
     - dacă unul înainte de 1990, unul după → setați d=1 (altă generație tehnologică);
     - altfel: |s−c| / 40.
   - Sau mai simplu (MVP):  
     - d = 0 dacă decade similare (±5 ani)  
     - d = 0.5 dacă 6–20 ani diferență  
     - d = 1 dacă >20 ani.

5. Tip construcție / material / regim înălțime – **10**  
   - Deja extrageți material, tip clădire, nr. etaje.  
   - d = 0 dacă tip foarte asemănător (ex: P+1 mediu vs P+1 mediu);  
     0.5 dacă diferență moderată (parter vs P+2);  
     1 dacă e clar altă clasă (casă veche neizolată vs vilă nouă P+2).

6. Stare tehnică (1–5, LLM) – **8**  
7. Finisaj (1–4, LLM) – **5**  
   - Ambele doar din LLM → reduceți ponderea actuală.  
   - d = |s−c| / (max_range−1) ca acum, dar:
     - marcați scorul de relevanță cu un „confidence badge” dacă 40%+ din pondere se bazează pe LLM.

8. Tip încălzire – **7**  
   - Formula actuală (0 / 0.5 / 1) e ok ca MVP, dar:
     - extindeți „aceeași familie” (centrală proprie gaz vs pompe de căldură = 0.5, dar sobe lemne vs centrală = 1).

Total ~100.

#### 1.2. Atribute deja extrase, de promovat în scor:
- Material/tip clădire: DA (casă/duplex/vilă/tradițională), pondere 10.
- Nr. camere: DA, dar ca filtru de eligibilitate (exclude garsoniere ca „comparabile” la casă 5 camere).
- Etaj: NU relevant la casă, doar să excludă anunțuri greșit clasificate.

#### 1.3. Stare/finisaj (LLM) – ce facem cu riscul:

- Reduceți ponderea agregată LLM la **sub 20%** din scorul total la casă (propus: 8+5=13).
- Marcați vizual: „Scor bazat parțial pe estimarea automată a stării/finisajului (model AI)”.
- Dați opțiune evaluatorului să:
  - confirme manual sau să modifice stare/finisaj pentru un comparabil (override);
  - vedeți efectul imediat în scor (transparent).

---

### #2 Apartament

Apartamentele au structură diferită de casă. Modelul actual (preluat de la casă) e inadecvat.

#### 2.1. Filtru de eligibilitate:
- Tip: apartament, nu casă, nu spațiu comercial.
- Același oraș + preferabil același cartier / ansamblu / zonă (militari residence vs militari vechi sunt diferite micro-piețe).
- Nr. camere: ±1 față de subiect (obligatoriu).
- Regim de înălțime/tip bloc: bloc vechi (înainte ‘90) vs nou (după 2000), preferabil același segment.
- Înălțime etaj vs etaj total: nu compari parter cu etaj 10 din 10 în același fel.

#### 2.2. Criterii de scor (suma ≈ 100):

1. Localizare fină – **30**  
   - d = funcție de distanță/categorie de cartier:  
     - 0 pentru același cartier/ansamblu;  
     - 0.4 același oraș alt cartier;  
     - 1 altă localitate.

2. Nr. camere – **15**  
   - Dacă nu e identic:  
     - 2 vs 3 camere: d=0.5;  
     - altă diferență: d=1.
   - Sau filtru dur (nu intra în listă dacă diferă).

3. Suprafață utilă – **20**  
   - d = min(|s−c| / (0.25s), 1).

4. An bloc / tip bloc (vechi vs nou) – **15**  
   - d = 0 dacă același segment (ex: înainte de ‘90 vs înainte de ‘90);  
     1 dacă cross-segment (vechi vs nou).

5. Etaj și poziționare în bloc – **10**  
   - d mic pentru etaje medii apropiate;  
   - penalizați diferențe mari de confort (parter vs ultim, fără lift etc.).

6. Stare/finisaj LLM – **7**  
7. Încălzire – **3**  
8. Lift (da/nu; dacă se poate extrage) – **5**.

Atribute de promovat aici:
- Nr. camere (principal).
- Etaj și număr etaje (principal).
- Tip bloc/material (principal).

---

### #3 Spațiu industrial / comercial

Aici criteriile se schimbă radical. Premisa „suprafață, an, stare, finisaj” e insuficientă.

#### 3.1. Filtru de eligibilitate:
- Tip utilizare: depozit / producție / retail stradal / birouri – măcar la nivel grosier.
- Zonalitate: parc logistic vs hală izolată vs spațiu central.
- Interval suprafață: 50–200% vs subiect.
- Parametri cheie: acces TIR, înălțime liberă, existență rampă (dacă se pot extrage ca boolean).

#### 3.2. Criterii scor (≈100):

1. Tip utilizare / funcțiune – **25**  
   - d=0 pentru același (depozit–depozit);  
   - 0.5 pentru înrudite (depozit–producție);  
   - 1 pentru diferite (retail–industrial).

2. Suprafață utilă / hală – **20**  
   - d = min(|s−c| / (0.4s), 1).

3. Localizare (macro) – **20**  
   - Distanță față de nod rutier/centură / localitate – aici mai mult contează accesul decât strict cartierul.

4. Parametri funcționali – **20** (dacă puteți extrage):
   - Înălțime liberă (H), acces TIR, rampă, putere electrică instalată.  
   - d = 0 dacă toți parametrii critici sunt la același nivel (ex: „acces TIR & H≥subiect”);  
     altfel crește spre 1.

5. An construcție / stare structurală – **10**  
6. Stare/finisaj LLM – **5**.

Aici, prioritatea NU este să rafinați scoringul cu LLM, ci să:
- extindeți ACOPERIREA (VDI, imoradar24, site-uri specializate);
- extrageți parametri funcționali (H, rampă, TIR) chiar cu reguli simple.

---

### #4 Teren agricol

Aici actualul model „suprafață doar” este aproape realist, dar lipsesc 2 criterii esențiale:
- localizare (comună, extravilan/intravilan, acces drum);
- categoria de folosință (arabil, fâneață, livadă) / calitatea solului (dacă e verificabil).

#### 4.1. Filtru eligibilitate:
- Tip: teren agricol, nu intravilan construibil (sau etichetă clară).
- Suprafață: 50–200% (configurabil).
- Localizare: măcar aceeași comună.

#### 4.2. Scor (≈100):

1. Localizare – **35**  
   - Dacă nu aveți geocodare:  
     - d=0 aceeași comună și zonă agricolă;  
     - 0.5 comună vecină;  
     - 1 alte zone.

2. Suprafață – **30**  
   - d = min(|s−c| / (0.3s), 1).

3. Categoria de folosință – **20**  
   - arabil vs arabil → 0;  
   - arabil vs fâneață → 0.5;  
   - arabil vs livadă / pășune → 1, etc.

4. Acces drum / deschidere – **10** (dacă se poate extrage).
5. Alți factori (împrejmuit, utilități apropiate) – **5**.

---

### #5 Proprietate specială (catch-all)

Aici orice model numeric universal riscă să fie fals-precis. Premisa de contestat:  
„Putem avea un model unic de scoring numeric pentru proprietăți speciale.”

Aș face altceva:
- două nivele:  
  1. clasificare grosieră (pensiune, hotel mic, benzinărie, fabrică, teren cu potențial comercial etc.);  
  2. comparare doar în interiorul aceluiași sub-tip.

#### 5.1. Filtru eligibilitate:
- obligatoriu același sub-tip (pensiuni cu pensiuni, hotel cu hotel etc.);
- aceeași localitate / zonă turistică / coridor comercial.

#### 5.2. Scor – FOARTE simplificat, adaptat subtipului:
- Pensiune:
  - nr. camere / locuri – 30;
  - localizare turistică – 30;
  - stare/finisaj – 20;
  - dotări (restaurant, piscină) – 20.
- Spațiu comercial stradal:
  - flux pietonal / stradă principală (proxy din descriere) – 40;
  - suprafață – 30;
  - vitrină / poziționare – 30.

În practică, aș:
- marca categoria #5 ca „asistență semiautomată”:  
  - comparabilele sunt mai mult sugerate, nu „scorate științific”;
- permite evaluatorului să aleagă manual ce contează (ponderi ajustabile în UI).

---

### Prioritizarea între „acoperire” (#3/#5) vs „scoring”

1. **High impact / low effort (imediat):**
   - Ajustați modelul pentru #2 (apartamente) – azi e fundamental greșit.
   - Reduceți ponderea LLM (stare/finisaj) la casă (#1) și marcați incertitudinea.
   - Introduceți nr. camere, etaj, tip bloc în scor la apartamente.

2. **Medium impact / medium effort:**
   - Minimizați modelul pe #3/#5: începeți cu filtre dure, scoring simplu.

3. **High impact / higher effort:**
   - Extindeți ACOPERIREA pentru industrial/comercial (#3, #5):
     - imoradar24 parser dedicat;
     - VDI.ro;
     - 1–2 site-uri specializate.
   - Fără acoperire, un model sofisticat de scor e inutil.

---

## Q2 — Criterii secundare în UI per tip

Recomand structură:

1. **Criterii principale (în scor)** – clar definite per tip (din Q1).
2. **Criterii secundare „asistate de AI” (în afara scorului, dar vizibile)**:
   - rămân așa pentru:
     - facilități (garaj, piscină, beci, pivniță);
     - detalii estetice (șemineu, vedere, mobilier inclus);
     - elemente greu standardizabile (calitatea vecinătății).

3. **Criterii secundare care merită promovate la principale, per tip:**
   - Apartament: nr. camere, etaj, lift (de la secundar la principal).
   - Casă: tip construcție (de la secundar la principal).
   - Industrial: acces TIR, H liberă (principal imediat ce le puteți extrage robust).
   - Teren: acces drum, categoria de folosință (principal).

4. **Prezentare în UI, diferit per tip:**
   - Pentru fiecare tip, preset de criterii secundare sugerate (checkbox-uri), plus câmp liber:
     - Apartamente: „balcon/terasă, loc parcare, boxă, lift, anvelopare termică”.
     - Case: „garaj, piscină, an extindere, casă de vacanță vs rezidențială”.
     - Industrial: „înălțime liberă, rampă, acces TIR, curte betonată”.
     - Teren: „irigații, deschidere la drum, PUG/PUZ”.
   - Toate rămân în afara scorului numeric, dar:
     - colorare/fleg vizuală dacă un comparabil bifează mai multe criterii secundare dorite decât altul (fără a schimba scorul).

---

## Q3 — Granularitate locație per tip + variația cu mărimea localității

### Principiu:

- Locația are **importanță diferită** per tip:
  - extrem de importantă la apartamente și comercial stradal;
  - importantă la casă;
  - mai mult „macro” la industrial și agricol.

### Recomandari per tip:

1. **Apartament (#2):**
   - Oraș mare: nivel „cartier” sau microzonă (ex: Drumul Taberei vs Militari).
   - Oraș mic: nivel localitate, eventual sub-zonă central/periferic dacă se poate deduce.
   - Prag automat:
     - dacă populație > 150k → folosiți cartier ca unitate de bază;
     - altfel localitate.

2. **Casă (#1):**
   - Oraș mare: tot cartier, dar prag de distanță acceptabil puțin mai mare.
   - Orășele/sate: localitate sau grup de localități imediat învecinate (în aceeași micro-piață).

3. **Industrial (#3):**
   - Nivel macro: acces la drumuri naționale, autostrăzi, centură; nu atât cartierul.
   - Prag: distanța în km față de nod rutier / parc industrial.

4. **Teren agricol (#4):**
   - Localitate/comună și vecinătăți.

5. **Proprietăți speciale (#5):**
   - Pensiuni/hoțel: zonă turistică (stațiune, zonă montană/litoral).
   - Retail: stradă/zonalitate.

### Cum decideți pragul automat (fără geocodare avansată):

- Definiți un **„indice de granulație”** per localitate:
  - mare: municipiu reședință de județ și orașe >150k locuitori;
  - mediu: oraș 30–150k;
  - mic: <30k și sate.
- Reguli:
  - apartamente în mare: scorul de locație folosește cartier;
  - în mediu: scorul folosește oraș, doar penalizare mică pe alt cartier;
  - în mic: tot orașul/comuna considerat relativ omogen.

---

## Q4 — Distanța fizică în ranking

### Contest premisa:
„Distanța ar trebui neapărat încorporată în scorul numeric global.”

Pentru multe evaluări ANEVAR, comparabilul poate fi la 3–5 km și totuși foarte bun (ex: zone periurbane), în timp ce două proprietăți la 500 m pot fi în micro-piețe diferite (una la bulevard, una în spate).

Aș trata „distanța” așa:

1. **Caracteristică ponderată în scor (pentru rezidențial / retail)**, DAR:
   - nu distanța brută, ci **„similaritate de zonă”** (vezi Q1 la locație).
   - Distanța fizică devine un proxy doar când nu aveți suficient context textual.

2. **Filtru gradual la căutare (b)**:
   - userul alege: „comparable în aceeași localitate”, „+5 km”, „+10 km”.
   - Sistemul respectă filtrul înainte de scoring.

3. **Tie-breaker (c)**:
   - dacă două proprietăți au același scor, se ordonează după distanță (mai aproape = sus).

4. **Penalizare afișată, dar în afara scorului (d)**:
   - exemplu de tip badge: „+12 km față de subiect – zonă diferită”;
   - util în raport: evaluatorul știe de ce a folosit sau nu comparabilul.

### Greutate recomandată (dacă o includeți în scor):

- Apartamente: **15–25%** din scor (sub formă de „similaritate zonă” mai mult decât km).
- Case: **15–20%**.
- Retail stradal: **30%** (locația e rege).
- Industrial/logistic: **10–15%** (mai important e tipul nodului rutier).
- Teren agricol: **20–25%** (calitatea zonei agricole, nu neapărat metri exacți).

### Cum calculăm distanța (tehnic):

- Fără geocodare:  
  - comparăm textul: același cartier/zonă/landmark → d=0; alt cartier → d=0.5; altă localitate → d=1.
- Cu geocodare (Nominatim/OSM + SIRUTA):
  - distanță haversine între coordonate subiect și comparabil;
  - normalizăm cu un prag D_max (per tip și mărimea localității): `d = min(dist_km / D_max, 1)`.

---

## Q5 — Ce model/API pentru ce strat

### 1. Extracție (atribute din text/__NEXT_DATA__)

- Panelul vostru deja arată: extracția e commodity.
- Recomand:
  - trecere la un model **ieftin, stabil**, ex:
    - Llama-3.1/3.2/3.3-70B instruct sau.
    - Claude 3.5 Haiku e overkill la preț.
  - definire clară de **schema JSON** și prompt fix; test unitare cu 50–100 de anunțuri.

- Arhitectură:
  - local (sau self-hosted) model mare economic, plus fallback la un model mai puternic pentru cazuri ambigue.

### 2. Discovery web (căutare de anunțuri)

- Nu e doar „nice to have”, e diferențiator:  
  - Sonar e slab pe deep-link; Exa performează bine.
- Recomand:
  - **layer hibrid**:
    - Scraping direct pentru principalele portaluri (storia, imobiliare, eventual OLX) – zero cost de query;
    - + un strat de search Exa pentru:
      - completarea acoperirii (#3, #5, hyperlocal, agregatori gen imoradar24);
      - fallback când portalurile nu au suficiente rezultate.
  - Implementați un **limiter de cost**:
    - primii N comparabili via scrape;
    - dacă <M comparabile valide, apelați search-API (Exa) până atingeți M.

### 3. Merită parser dedicat pe imoradar24?

Da, dar condiționat:
- imoradar24 e agregator → dedup obligatoriu.
- Prioritate:
  1. Parser direct pentru 1–2 site-uri industrial/comercial (VDI, site-uri specializate);  
  2. Abia apoi imoradar24, dar strict pentru subsetul de categorii unde nu aveți acoperire.

---

## Q6 — OLX și încredere per sursă

### (a) Merită păstrat OLX?

- Da, dar:
  - tratat ca **sursă „low structure / low trust”**, folosită:
    - pentru volum suplimentar când alte portaluri nu au destule comparabile;
    - ca „ofertă informativă”, nu ca prim-tier.

- Consecințe:
  - indicați explicit în UI „sursă: OLX (informații limitate, nevalidate)”;
  - pentru OLX:
    - puneți automat „încredere scăzută” (badge);
    - cereți completări manuale de la utilizator (suprafață, an, etc.).

### (b) Grad de încredere per sursă în UI (nu în scor)

Da, are sens și e util practic:

- Ex:
  - Storia / Imobiliare: „structurat, verificat parțial”;
  - OLX: „particulari, date nevalidate”;
  - VDI / portaluri comerciale: „specializat, profesional”.

Le-aș afișa ca:
- un mic badge colorat (verde / galben / gri) + tooltip:
  - „Grad de încredere în datele listate (nu influențează scorul numeric, doar interpretarea evaluatorului)”.

---

## Q7 — Robustețe extracție cu mai multe surse

### Contest parțial premisa „consiliu de API-uri”

Un „consiliu” (mai multe modele LLM care extrag în paralel + consolidare) își are rostul la:
- sarcini cu ambiguitate semantică mare, nu la extract de text destul de concret.

Aici:
- extracția e repetitivă și bine definită;
- erorile principale vin din:
  - date lipsă / confuze;
  - structuri HTML variate.

### Recomandare:

1. **Arhitectură simplă (preferată)**:
   - un singur model principal de extracție (ieftin, stabil);
   - un modul de **validare deterministică** (post-procesare):
     - dacă suprafața <10mp sau >1.000.000mp → respinge;
     - dacă anul <1900 sau >anul curent+1 → respinge;
     - dacă lipsesc prea multe atribute cheie → mark „low confidence”.

2. **Fallback punctual, nu consiliu:**
   - dacă un anunț e decis „low confidence”:
     - retrimite-l la un model „premium” (GPT-4, Claude Sonnet) doar pentru extragere reîncercată;
   - 95% din trafic merge pe modelul ieftin, 5% pe premium.

3. **Status quo vs consiliu complet:**
   - un consiliu complet (3+ modele + reconciliere) e probabil overkill la cost și latență;
   - ROI foarte slab comparat cu:
     - îmbunătățiri de parser HTML;
     - geocodare;
     - extindere de surse.

---

## Q8 — Riscuri, dependențe, ordine de prioritate

### Riscuri majore

1. **Model de scor perceput ca „exact” dar bazat pe date incerte (LLM, OLX).**
   - Mitigare: badge de încredere, pondere mică LLM, transparență.

2. **Aglutinare de portaluri fără dedup solid.**
   - Mitigare: hashing pe titlu+suprafață+preț+coordonate când le aveți.

3. **Dependință puternică de un singur search-API (Exa etc.).**
   - Mitigare: fallback la scraping + caching local.

4. **Complexificare UI pentru evaluatori.**
   - Mitigare: preseturi per tip, mod „simplu” / „avansat”.

### Ordine de prioritate (foarte concret)

**P0 (imediat, 1–2 sprinturi):**
1. Redefiniți modelul pentru apartamente (#2) – criterii + ponderi + filtrare.
2. Reduceți ponderea LLM (stare/finisaj) și marcați în UI („bazat pe AI; verifică manual”).
3. Introduceți în scor atribute deja extrase esențiale:
   - nr. camere, etaj, tip bloc pentru apartamente;
   - material/tip clădire pentru case.

**P1 (următoarele 2–3 sprinturi):**
4. Implementați macro-locație în scor (similaritate zonă) – chiar și fără geocodare, doar textual.
5. Adăugați 1–2 surse noi pentru industrial/comercial (VDI + încă una).
6. Implementați gradient de încredere per sursă în UI.

**P2 (mai departe):**
7. Geocodare (OSM/Nominatim/SIRUTA) cu distanță în km pentru rezidențial.
8. Parser imoradar24 cu dedup.
9. Criterii avansate pentru industrial (#3) – parametri funcționali.

---

## Q9 — Ce nu ați întrebat, dar ar trebui? Contest o premisă de bază

### Premisă de contestat: „Un singur scor 0–100% e modul optim de a exprima similaritatea.”

În practica de evaluare:
- comparabilitatea e **multidimensională**:
  - contribuie diferit la analiză: locație, caracteristici fizice, juridice, tranzacționale;
- evaluatorul vrea să înțeleagă rapid „de ce” un comparabil e sus, nu doar „cât”.

Dacă aș proiecta „Descoperă” de la zero:

1. Aș separa clar:
   - **filtrul de eligibilitate** (trece/nu trece – „candidați comparabili”);
   - **profilul de similaritate** în 3–4 axe, nu un singur scor:
     - Locație (0–100);
     - Caracteristici fizice (0–100);
     - Calitate/finisaj (0–100);
     - Parametri funcționali (pentru industrial/comercial).

2. Aș păstra un scor global doar ca rezumat, dar:
   - în UI aș arăta „radar chart”/bar-chart cu cele 3–4 axe;
   - evaluatorul poate decide să ignore scorul global și să se uite la axa care contează pentru cazul concret.

3. Aș face sistemul **configurabil per evaluator / tip raport**:
   - preset ANEVAR standard;
   - posibilitatea de a salva „profile de evaluare” cu ponderi proprii (ex: un evaluator axat pe rezidențial urban, altul pe industrial).

4. Aș proiecta încă de la început:
   - o „istorie a deciziilor” – ce comparabile au fost acceptate/respins, cu motiv (manual), pentru a antrena pe viitor un model de ranking bazat și pe feedback uman, nu doar pe reguli.

---

## Q10 — Cea mai inovatoare idee (o singură mișcare îndrăzneață)

**Idee:**  
Transformați „Descoperă” dintr-un simplu motor de similaritate într-un **„co-pilot de selecție comparabile” care învață din deciziile evaluatorului**.

### Ce înseamnă concret:

1. Pe lângă scorul de similarity rule-based actual:
   - logați pentru fiecare subiect:
     - ce comparabile au fost propuse;
     - ce comparabile a ales efectiv evaluatorul;
     - ce comparabile a respins (și eventual motivul selectat rapid dintr-o listă: prea departe, alt cartier, stare diferită etc.).

2. Folosiți acest istoric pentru a antrena:
   - un model (chiar simplu: gradient boosting / logistic regression) care:
     - ia în input toate atributele comparabilului (incl. text, locație, sursă, tip);
     - prezice „probabilitatea să fie ales de evaluator ca bun comparabil”.

3. În timp, rankingul devine:
   - hibrid: `score_final = α * score_rules + (1 − α) * score_learned`, unde:
     - `score_learned` reflectă preferințele reale ale evaluatorilor (inclusiv micro-locații, trust în surse, biasuri raționale).

4. UI:
   - afișați motivele „explaianable”:  
     - „proprietățile de acest tip au fost selectate frecvent ca bune comparabile în zona X, pentru subiecte similare.”

### De ce ar funcționa:

- În piață reală, cea mai mare valoare e **experiența empirică a evaluatorilor**, nu doar regulile normative.
- Sistemul devine mai bun cu timpul, adaptat:
  - la oraș, segment de piață, chiar stilul fiecărui evaluator sau firmă.
- Diferențiator puternic față de orice tool static.

### Cel mai mare risc:

- Date insuficiente / zgomotoase la început:
  - prea puține cazuri per tip astfel încât modelul învață pattern-uri proaste;
  - divergențe mari între evaluatori (preferințe personale).
- Mitigare:
  - porniți cu un scor „learned” doar ca tie-breaker secundar (10–20% din scor);
  - colectați explicit justificări simple pentru respingere (etichete), să puteți filtra „respingeri arbitrare”.

---

Dacă fac rezumatul de priorități acționabile:

1. Refaceți modelul pentru apartamente (#2) și reduceți asumarea LLM la casă (#1).
2. Introduceți localizare/micro-locație jako criteriu major (și eventual distanță ca tie-breaker).
3. Extindeți acoperirea pentru industrial/comercial (#3/#5) cu 1–2 surse noi.
4. Introduceți transparență: badge-uri de încredere per sursă și per atribut (LLM vs structurat).
5. Planificați de acum colectarea feedback-ului evaluatorilor pentru un viitor model de ranking „învățat”.

### google/gemini-3.1-pro-preview

Iată răspunsul detaliat din partea panelului de council, redactat cu o abordare critică, analitică și focusată pe utilitatea reală pentru un evaluator ANEVAR. Am contestat ipotezele acolo unde modelul actual prezintă limitări.

---

### Q1 — Criterii principale, Ponderi și Similaritate per Categorie
**Contestare premisă:** Formula uniformă de distanță liniară `min(|s−c|/s, 1)` este problematică (detaliez la Q9 de ce). De asemenea, ponderea pentru „Teren (×1)” la #1 este nefiresc de mică pentru România, unde terenul dictează masiv valoarea.

**Propuneri per categorie:**
*   **#1 Casă + Teren:** Suprafață constr. (×5), **Teren (×5** - mărit de la ×1), An (×3), Stare (×3), Finisaj (×2). Încălzire (×1).
*   **#2 Apartament:** *Trebuie promovate atributele extrase.* Suprafață (×5), **Camere (×4)**, **Etaj (×3)**, An (×3), Stare (×3), Finisaj (×2).
*   **#3 Spațiu Industrial:** *Extragerea nouă necesară.* Suprafață (×5), **Înălțime utilă (×5)**, **Acces TIR/Rampă (×4)**, Utilități (curent trifazic) (×3), Stare (×2). *Prioritate surse:* Nu ajustați scorul aici până nu integrați surse ca Imoradar24/VDI.ro; Storia are acoperire prea slabă pe industrial.
*   **#4 Teren Agricol:** Suprafață (×5), Deschidere la drum (×4), Categorie de folosință (arabil/pășune) (×4).
*   **#5 Proprietate Specială:** *Contest premisa:* Nu poți avea un model de scor fix pentru un „catch-all” eterogen (hotel vs. cramă). **Soluția:** Când userul alege #5, aplicația trebuie să-i ceară să-și *selecteze manual ancorele* din lista de atribute extrase, înainte de a calcula rankingul.

**Riscul LLM (Stare/Finisaj):** Ponderea lor adunată (7) este prea mare pentru un output netestabil. **Acțiune:** Reduceți suma lor la max 5 (vezi #1 și #2 mai sus). Adăugați un *badge vizual* în UI (ex. un icon cu ochi) care semnalează „Estimat de AI” și obligă evaluatorul să dea un click de confirmare (bifă) înainte ca acel comparabil să intre în grila finală ANEVAR.

### Q2 — Criteriile secundare din UI
Rămân în afara formulei algoritmice de ranking, pentru a păstra predictibilitatea.
**Acționabil:** Transformați-le în **„Booster manual”**. Dacă LLM-ul găsește în text un criteriu secundar introdus de user (ex: „pompă de căldură”), UI-ul să afișeze un buton: *„Criteriu confirmat. Aplică +5% la relevanță?”*. Astfel, evaluatorul controlează ponderarea excepțiilor, nu algoritmul. Colectarea trebuie făcută din dropdown-uri cu sugestii auto-completate specific per categorie (ex. pentru #2 sugerezi „lift”, „vedere spre parc”).

### Q3 — Granularitatea locației
Diferă masiv în funcție de **dimensiunea unității administrativ-teritoriale**.
*   *Sate/Comune:* Nivelul de localitate este suficient.
*   *Orașe mici (<50k loc):* Localitate / Cartier.
*   *Orașe mari (București, Cluj, Timișoara):* **Nivelul de stradă sau poligon/raza (500m-1km) este critic.** (Un apartament în Primăverii vs. Ferentari, ambele în Sector 1).
**Decizie automată:** Folosiți un fișier static offline (SIRUTA/OSM). Dacă localitatea căutată are >50k locuitori (sau aria > X kmp), modulul activează automat forțarea filtrului post-căutare pe cartier/rază.

### Q4 — Distanța în ranking
**Contestare premisă:** Deoarece coordonatele de pe portaluri sunt adesea aproximative, introducerea în formula de relevanță (0-100%) va distorsiona agresiv și eronat rezultatele.
**Recomandare: Opțiunea (d) hibridizată cu (c).** Distanța se calculează offline (OSM/Nominatim geocoding pe strada extrasă din text). **Nu** intră în scorul de 0-100%. Este afișată ca un „Tie-breaker” vizual, sub relevanță: *„Scor 88% | ~1.2 km distanță”*. Userul poate sorta după ea (filtru gradual), iar pentru #4 (Terenuri), devine indicator de penalizare dacă depășește raza relevantă agricolă.

### Q5 — Modele API și Stratificare
*   **Extracție:** Claude e prea scump pentru o taskă comoditizată cum e extracția structurată. Treceți pe un model rapid și ieftin dedicat JSON-urilor (ex. Llama-3.3-70b via OpenRouter sau Gemini-1.5-Flash).
*   **Discovery:** Construirea unui „Strat hibrid de discovery prin LLM (Exa)” e o capcană a costurilor/latenței. **Cea mai bună rută (ROI):** Scrieți un parser dedicat (scraping direct) pentru **Imoradar24.ro**. Fiind agregator, rezolvă problema acoperirii fără costul pe interogare cerut de un API de Search AI.

### Q6 — OLX și „Încrederea per sursă”
**(a) OLX:** Păstrați-l. OLX e sursa unde proprietarii direcți vând „sub radarul” agențiilor, arătând valoarea reală a pieței (crucial în ANEVAR). Deficitul de date se rezolvă lăsând câmpurile goale în modulul „Descoperă”, cu obligația ca evaluatorul să le completeze vizualizând imaginile.
**(b) Index de încredere UI:** Da. Introduceți un `Source Quality Score` (Storia = High, Imob = Med, OLX = Low), vizibil ca un indicator de tip „semafor” lângă anunț.

### Q7 — Robustețea extracției: Consiliul sau Altceva?
*Nu adăugați un consiliu de API-uri (voting system).* Va tripla costul, timpul de răspuns și frustrarea userului, pentru un gain de precizie de 2%.
**Arhitectură alternativă:** Folosiți un singur model (ieftin) dar forțați un mecanism de *Self-Consistency*. Cereți modelului să returneze în JSON: `{"finisaj": 3, "confidence": "high/medium/low", "citat_dovadă": "..."}`. Afișați doar alertele pentru „low confidence” în UI.

### Q8 — Ordinea de PRIORITATE absolută
1.  **Rezolvarea Scoring-ului:** Crearea și implementarea modelelor distincte de scoring pentru #2, #3, #4 (promovarea atributelor deja extrase ca Etaj/Camere). Este inacceptabil ca #2 să fie evaluat cu logica de casă.
2.  **Reducerea COSTULUI/Latenței:** Schimbarea modelului de extracție LLM (Claude -> Llama/Gemini Flash).
3.  **Acoperire Surse Noi:** Dezvoltarea parserului pentru Imoradar24 (pentru a debloca zona industrială/agricolă).
4.  **Distanță (Locație):** Implementarea offline a Nominatim pentru geocoding și calcul distanță.
5.  **Criterii secundare:** UI upgrade (Booster manual).

### Q9 — Ce ne scapă? (Contestarea premisei fundamentale)
**Vrem să contestăm formula liniară de calcul a similarității.**  
Formula actuală: `min(|s−c|/25, 1)` pentru An construcție este greșită contextual în România.
*De ce?* Diferența între 1955 și 1965 (10 ani = 0.4 deviație) contează puțin. Diferența între 1975 și 1979 (doar 4 ani = 0.16 deviație) este **critică**, din pricina cutremurului din 1977. La fel, diferența de etaj: Parter vs. Etaj intermediar nu e o distanță carteziană (2 etaje), ci o ruptură de piață.
*Soluția:* Dacă am reface „Descoperă”, **similaritatea ar folosi "Value Cliffs" (scări de valori), nu doar distanță liniară.** Anumite atribute necesită mapping categorial cu penalizări severe discrete, nu interpolare.

### Q10 — Cea mai inovatoare idee (Bold Move)
* **Ideea: Evaluator Vizual de Finisaje și Stare (Text-blind)**.
Treceți de la extracția din text (unde agenții imobiliari mint constant cu cuvinte precum „Lux”, „Recent renovat”) la analiza directă a IMAGINILOR scrapuite. Folosiți un model vision-language multimodal (e.g., GPT-4o-Vision sau Gemini Pro Vision) pentru a privi primele 3-5 poze din anunț. Promptul: *„Evaluează starea structurii (1-5) și nivelul finisajelor (1-4) privind aceste poze, ignorând textul”*.
* **De ce va funcționa:** Va diferenția produsul masiv; pentru un evaluator ANEVAR, „adevărul” e dictat de imagine, nu de copy-ul anunțului. Va transforma o aplicație utilitară într-un "X-Ray" imobiliar.
* **Cel mai mare risc:** Creșterea substanțială a volumului de trafic (descărcarea pozelor), declanșarea sistemelor anti-scraping severe de la Storia/Imobiliare, și costul mai mare per inferență al modelelor Vision comparative cu text-only. Se poate lansa ca „mod premium / deep scan” declanșat manual pe top 10 rezultate.

### anthropic/claude-sonnet-4.5

# Răspunsuri Council – Modulul „Descoperă"

## Q1 – Criterii principale per categorie: ponderi, formule, priorități

### Categoria #1 – Casă + Teren (deja modelată)
**Critici la modelul actual:**
- Suprafața construită (×5) și Anul (×5) sunt corect cele mai importante
- **PROBLEMĂ GRAVĂ**: Stare (×4) + Finisaj (×3) = 35% din greutate totală, dar vin 100% din LLM pe text liber → risc enorm de volatilitate
- Încălzirea (×2) e supra-ponderată – un apartament fără încălzire centrală dar cu pompă de căldură nu e 10% mai puțin relevant

**Propunere revizuită:**
```
Suprafață construită    ×6   min(|s-c|/max(s,c), 1)      [normalizare simetrică]
An construcție          ×5   min(|s-c|/30, 1)            [30 ani = prag realist RO]
Suprafață teren         ×3   min(|log(s)-log(c)|/2, 1)   [logaritmic – 200→400mp mai puțin grav decât 1000→2000mp]
Stare (1-5)            ×2   min(|s-c|/4, 1) + FLAG      [REDUS + marcaj „estimat LLM"]
Nr. camere             ×2   min(|s-c|/max(s,c), 1)      [PROMOVAT – extrem de important la case]
Finisaj (1-4)          ×1   min(|s-c|/3, 1) + FLAG      [REDUS – subiectiv]
Încălzire              ×1   0/0.3/1 (identic/familie/diferit) [REDUS]
```
**ACȚIUNE CRITICĂ**: Adaugă UI toggle „Confirmă stare/finisaj" cu dropdown 1-5/1-4 – dacă userul confirmă, ȘTERGE flag-ul și CREȘTE ponderea înapoi (stare ×4, finisaj ×2).

---

### Categoria #2 – Apartament (NEMODELARE ACUM)
**Criterii principale:**
```
Suprafață utilă         ×7   min(|s-c|/max(s,c), 1)      [CEL MAI IMPORTANT]
Etaj                    ×5   formula custom ⬇             [CRUCIAL – parter ≠ etaj 10]
Nr. camere              ×4   |s-c|=0→0; =1→0.3; ≥2→1     [decuplare tipologie]
An construcție          ×3   min(|s-c|/40, 1)            [bloc comunist vs nou]
Stare (1-5)            ×2   min(|s-c|/4, 1) + FLAG
Compartimentare         ×1   0/1 (decomandat vs semidec/circ) [extragere LLM din text „decomandat"]
```

**Formulă etaj (×5):**
```python
if subiect.etaj == "parter" and candidat.etaj == "parter": d=0
elif subiect.etaj == "ultimul" and candidat.etaj == "ultimul": d=0
elif subiect.etaj in ["parter","ultimul"] XOR candidat.etaj in ["parter","ultimul"]: d=0.7
else: d = min(|etaj_s - etaj_c| / 5, 1)  # etaje intermediare
```

**Atribute promovate**: 
- **Nr. camere** (extrage deja) → pondere ×4
- **Etaj** (extrage deja) → pondere ×5
- Material NU (irelevant la apartamente – contează starea, nu dacă e BCA sau cărămidă)

---

### Categoria #3 – Spațiu Industrial (NEMODELARE ACUM)
**ATENȚIE**: Imobiliare.ro/Storia au acoperire SLABĂ aici → prioritizează ACOPERIRE înaintea scoringului.

**Criterii principale:**
```
Suprafață construită    ×6   min(|s-c|/max(s,c), 1)
Înălțime liberă (m)     ×5   min(|s-c|/s, 1)              [CRITIC – hale necesită ≥4-6m]
Suprafață teren         ×4   logaritmic
Rampe/Accese TIR        ×3   0/1 (are/nu are)             [binary – extracție LLM]
An construcție          ×2   min(|s-c|/50, 1)             [mai puțin relevant]
Certificări (PIF/etc)   ×2   0/1                          [parcare industrială]
Putere electrică (kW)   ×1   min(|s-c|/max(s,c), 1)
```

**PRIORITATE MAXIMĂ**: Adaugă parsere VDI.ro (lider industrial RO) + Imoradar24 ÎNAINTE de tuning scoring. Fără surse, scoringul e inutil.

---

### Categoria #4 – Teren Agricol (parțial modelat)
**Model actual** (doar suprafață) e **prea simplist** dar pe direcția corectă.

**Criterii principale:**
```
Suprafață               ×8   min(|log(s)-log(c)|/3, 1)    [logaritmic obligatoriu]
Clasificare teren       ×5   0/0.5/1 (intravilan/extravilan agricol/extravilan neproductiv)
Acces drum              ×3   0/0.5/1 (asfaltat/pietruit/inexistent) [LLM din „acces drum..."]
Utilități (apă/curent)  ×2   formula custom (0=toate, 0.25 per lipsă)
Pantă/Relief            ×1   0/0.5/1 (plan/ușoară/abruptă)
```

**Notă**: La terenuri, distanța față de DN/centru devine FOARTE relevantă (vezi Q4).

---

### Categoria #5 – Proprietate Specială (catch-all eterogen)
**PROBLEMĂ FUNDAMENTALĂ**: Categoria e prea largă (hoteluri, cabinete medicale, spații birouri, etc). 

**Opțiuni:**
1. **RECOMANDAT PE TERMEN SCURT**: Aplică modelul #1 (casă) ca fallback REZONABIL, cu un WARNING vizibil: „Scor estimativ – verifică manual relevanța".
2. **TERMEN LUNG**: Split în sub-categorii:
   - #5a Birouri → model apropiat de #2 (apartament) dar + parcare/acces auto
   - #5b Spații comerciale → model hibrid #1/#3
   - #5c Hoteluri/Pensiuni → model custom (nr. camere, clasificare stele, capacitate)
   - #5d Agricole speciale (ferme, sere) → model apropiat #4

**Decizie acum**: Păstrează #5 monolitic, aplică modelul #1, prioritizează split-ul DUPĂ ce ai acoperire de surse pe #3.

---

### PRIORITIZARE GLOBALĂ (Q1):
1. **IMM (0-2 săptămâni)**: 
   - Implementează modelul #2 (apartamente) – 60% din piața RO
   - Adaugă UI „Confirmă stare/finisaj" cu reducere pondere LLM
   - Promovează nr. camere + etaj în ranking

2. **URGENT (2-6 săptămâni)**:
   - Adaugă parsere VDI.ro + strategie Imoradar24 (vezi Q5)
   - Implementează modelul #3 (industrial) DUPĂ parsere

3. **MEDIU (2-3 luni)**:
   - Îmbunătățește #4 (teren) cu clasificare/acces
   - Geocoding + distanță (vezi Q4)
   - Split #5 în sub-categorii

---

## Q2 – Criterii secundare: scor vs. metadata?

**CONTESTARE PREMISĂ**: Distincția „principal vs secundar" e artificială și confuză pentru user.

**Propunere alternativă – sistem cu 3 nivele:**

### Nivel 1: Criterii CORE (întotdeauna în scor)
Suprafață, an, stare, camere, etaj – specifice categoriei (din Q1)

### Nivel 2: Criterii OPȚIONALE PONDERATE (user alege dacă intră în scor)
UI: checkbox „Include în relevanță" + slider pondere 1-5
- Balcon/terasă (apartamente)
- Garaj/locuri parcare
- Grădină (case)
- Pod/subsol
- Orientare (apartamente)

**Formula**: când userul bifează, adaugă criteriu cu pondere configurabilă în formula existentă.

### Nivel 3: FILTRE BINARE (show/hide, NU scor)
- „Doar cu geamuri termopane"
- „Doar cu AC"
- „Fără risc seismic"

**Colectare per tip**: 
- La #2 (apart): expune ca opționale balcon, orientare, lift
- La #1 (casă): expune ca opționale garaj, grădină, gard
- La #3 (industrial): expune rampe TIR, birouri anexă, vestiare

**ACȚIUNE**: Elimină conceptul de „secundar = nu intră în scor". Fă-le transparente: „Acest criteriu adaugă 10% la greutatea scorului – poți ajusta sau dezactiva."

---

## Q3 – Granularitate locație per tip

**RĂSPUNS SCURT**: Locația e CONTEXT-DEPENDENT, nu TYPE-DEPENDENT.

### Framework de decizie automată:

```python
def get_location_granularity(tip_proprietate, populatie_localitate, suprafata_oras_km2):
    # Nivel 1: Localitate întreagă OK
    if populatie < 10_000:
        return "localitate"  # Breaza, Sinaia – tot e relevant
    
    # Nivel 2: Cartier/zonă obligatoriu
    if populatie >= 50_000 or tip in [APARTAMENT, SPATIU_INDUSTRIAL]:
        if tip == APARTAMENT:
            threshold_km = 1.5  # 15-20 min mers pe jos
        elif tip == SPATIU_INDUSTRIAL:
            threshold_km = 5    # acces logistic relevant
        else:
            threshold_km = 3
        return f"raza_{threshold_km}km"
    
    # Nivel 3: Stradă relevantă (orașe mari + case premium)
    if populatie >= 200_000 and tip == CASA:
        return "strada"  # Dorobanți vs Militari contează
    
    return "localitate"  # fallback
```

### Implementare practică (fără geocoding complet):

**FAZA 1 (now)**: 
- Extrage din text „zona X" / „cartier Y" / „strada Z" (deja în text anunț)
- Afișează în UI, permite user să filtreze text „conține Centru"
- NU influențează scorul încă

**FAZA 2 (cu geocoding)**: 
- Geocoding offline pe adrese extrase (Nominatim + cache local)
- Calculează distanță linie dreaptă
- Aplică praguri automate din formulă de mai sus

### Cazuri speciale:
- **Terenuri agricole (#4)**: Distanța față de drum național > distanța față de „subiect" – vezi Q4
- **Industrial (#3)**: Acces A1/A3 mai important decât proximitate cu subiectul
- **Zone de frontieră**: Breaza (Prahova) vs Brebu (Prahova) – 15km dar piețe diferite → validare pe bază de comună SIRUTA, nu doar distanță

**CONCLUZIE Q3**: Implementează extracția zonă/stradă din text (2 zile muncă), afișează în UI, amână geocoding până ai validat ipoteza că users chiar folosesc filtrul.

---

## Q4 – Distanța în ranking: CÂND și CUM?

**CONTESTARE PREMISE**: Întrebarea presupune că distanța e univoc de la subiect → candidat. GREȘIT.

### Framework distanță = funcție de CONTEXT, nu proprietate:

| Tip | Distanța relevantă | Mod calcul | Integrare în scor |
|-----|-------------------|------------|-------------------|
| **#2 Apartament** (oraș >100k) | Față de SUBIECT | Euclidiană directă | **(b) Filtru gradual** – penalizare blândă >2km: scor × (1 - 0.05×km_peste_2) |
| **#2 Apartament** (oraș <50k) | Indiferentă | - | **(e) Deloc** |
| **#1 Casă** (rural) | Față de CENTRU localitate | Euclidiană | **(c) Tie-breaker** – la scor egal ±2%, preferă mai aproape de centru |
| **#1 Casă** (urban) | Față de SUBIECT + zonă | Euclidiană + verificare zonă | **(b) Filtru** – penalizare >5km SAU zonă diferită |
| **#3 Industrial** | Față de NODURI LOGISTICE (A1/A3/port/aeroport) | Distanță drum (nu linie dreaptă) | **(a) Caracteristică ponderată** (×2) – crucial pentru logistică |
| **#4 Teren agricol** | Față de DRUM ASFALTAT + centru | Distanță drum | **(a) Caracteristică** (×3) – accesibilitate = preț |
| **#5 Speciale** | Depinde de subtip | - | **(c) Tie-breaker** implicit |

### Implementare recomandată – sistem hibrid:

**FAZA 1 (fără geocoding complet)**:
```python
# La apartamente în orașe >100k
if categorie == APARTAMENT and populatie > 100_000:
    if candidat.zona_extrasa != subiect.zona_extrasa:
        scor_final *= 0.85  # penalizare 15% pentru zonă diferită
    # Afișează WARNING: „Cartier diferit – verifică manual relevanța"
```

**FAZA 2 (cu geocoding)**:
```python
def adjust_score_by_distance(scor_base, tip, distanta_km, context):
    if tip == APARTAMENT:
        if context.populatie < 50_000:
            return scor_base  # (e) deloc
        else:
            penalty = max(0, (distanta_km - 2) * 0.05)  # (b) filtru gradual
            return scor_base * (1 - min(penalty, 0.3))  # cap la 30% penalizare
    
    elif tip == INDUSTRIAL:
        # (a) caracteristică ponderată
        dist_nod_logistic = get_nearest_highway_km(candidat)
        d_normalized = min(dist_nod_logistic / 20, 1)  # 20km = max relevant
        return scor_base  # se adaugă în formula principală, nu aici
    
    elif tip == TEREN_AGRICOL:
        dist_drum = get_nearest_paved_road_km(candidat)
        d_normalized = min(dist_drum / 5, 1)
        return scor_base  # (a) în formulă principală
    
    else:  # CASA, SPECIALE
        # (c) tie-breaker – nu modifică scor, doar ordine la egalitate
        return scor_base
```

### Cum calculăm distanța?

**Opțiuni evaluate**:
1. **Geocoding live** (Google/Mapbox) – ❌ cost, rate limits, dependență
2. **Nominatim offline** (OSM Romania dump) – ✅ RECOMANDAT
3. **Distanță aproximativă pe bază de comună SIRUTA** – ✅ fallback ieftin
4. **Extracție coordonate din anunț** – ❌ Storia/Imobiliare nu expun lat/lng public

**IMPLEMENTARE PRACTICĂ**:
```bash
# Setup one-time (2-3 ore)
1. Download OSM Romania extract (350MB)
2. Importă în PostgreSQL + PostGIS (local)
3. Geocoding: adresă text → query local → lat/lng (20ms)
4. Cache rezultate în DB (99% din adrese se repetă)
```

**DECIZIE Q4**: 
- Apartamente orașe mari: **(b) filtru gradual** cu penalizare blândă după 2km
- Industrial/teren: **(a) caracteristică ponderată** față de infrastructură
- Restul: **(c) tie-breaker** sau **(e) deloc**
- Implementare: Nominatim offline (fezabil, cost zero după setup)

---

## Q5 – Model/API per strat: cost vs. calitate

**CONSTATARE VALIDATĂ**: Extracția e commodity, discovery NU e.

### Strategie per strat:

#### STRAT 1: Extracție atribute (din HTML scrapuit)
**SWITCH IMEDIAT** de la Claude Haiku ($0.80/$4) la **Llama 3.3 70B** ($0.10/$0.32) sau **Qwen 2.5 72B** ($0.18/$0.54).

**Justificare**: 
- Panel 9/9 modele = acuratețe identică pe task-ul acesta
- Economie: $0.32 vs $4 pe 1M tokeni output = **12.5× mai ieftin**
- Risc zero – fallback la Claude dacă detecția e incertă (flag `confidence < 0.8`)

**Implementare**:
```python
# Tiering extracție
def extract_attributes(html, text):
    # Încearcă ieftin
    result = llama_3_3_70b.extract(text, temperature=0)
    
    if result.confidence > 0.8:
        return result  # 95% din cazuri
    else:
        # Fallback scump doar când e neclar
        return claude_haiku.extract(text, temperature=0)
```

**ECONOMIE**: La 1000 anunțuri/lună × 2000 tokeni medie = 2M tokeni → economie $7.36/lună (insignifiant) DAR principiul contează la scale.

---

#### STRAT 2: Discovery surse noi

**PROBLEMĂ CRITICĂ**: Perplexity Sonar = ZERO rezultate verificate. Exa/search APIs = rezultate bune DAR concentrate pe agregatori (Imoradar24).

**OPȚIUNI EVALUATE**:

**A) Scraping direct parsere noi** (VDI, Imoradar24, etc)
- PRO: Date curate, control complet, cost zero după implementare
- CON: 2-3 zile muncă per parser, mentenanță la schimbări HTML
- **RECOMANDAT pentru VDI.ro** (industrial) și **storia/imobiliare** (deja ai)

**B) Imoradar24 ca agregator**
- PRO: Accesează surse multiple (15+) printr-un singur parser
- CON: E agregator = link-uri externe → risc 404, necesită dedup, câmpuri inconsistente
- **STRATEGIE**: Folosește Imoradar24 pentru DISCOVERY (găsește anunțuri), apoi urmărește link-ul sursă originale și scrapuiește de acolo

**C) Search API (Exa/Tavily) pentru long-tail**
- PRO: Găsește surse hyperlocal (imobiliarebreaza.ro), utile în comune mici
- CON: Cost $5-20 per 1000 searches, rezultate variabile
- **RECOMANDAT**: Folosește ca **fallback** când scrapingul direct returnează <3 rezultate

**D) Bundle „consiliu de discovery"**
- RESPINS – overhead prea mare, beneficiu marginal

---

#### STRATEGIE FINALĂ (hibridă, tiering):

```python
def discover_comparables(subiect, categorie):
    results = []
    
    # Tier 1: Scraping direct (FREE, rapid, fiabil)
    results += scrape_storia(subiect)
    results += scrape_imobiliare(subiect)
    
    if categorie == INDUSTRIAL:
        results += scrape_vdi(subiect)  # ADAUGĂ ACUM
    
    # Tier 2: Agregator dacă Tier 1 sărac
    if len(results) < 5:
        imoradar_links = scrape_imoradar24_listings(subiect)
        for link in imoradar_links:
            original_source = follow_redirect(link)  # ex storia.ro/abc
            if original_source not in [r.url for r in results]:
                results += scrape_url(original_source)
    
    # Tier 3: Search API ca last resort (PAID, lent)
    if len(results) < 3 and PREMIUM_ENABLED:
        exa_results = exa_search(subiect, max_results=10)
        results += [scrape_url(r.url) for r in exa_results if is_scrapable(r.url)]
    
    return deduplicate(results)  # pe URL + titlu
```

**COST ESTIMAT**:
- Tier 1+2: $0 (scraping)
- Tier 3: ~$0.05 per căutare × 15% din cazuri = $0.0075 per subiect medie
- La 500 subiecte/lună = **$3.75/lună** (acceptabil)

**PRIORITATE**: Implementează scraper VDI.ro (2 zile) ÎNAINTE de orice search API.

---

## Q6 – OLX și încredere per sursă

### (a) Merită păstrat OLX?

**NU în forma actuală** – dar cu un pivot.

**ANALIZĂ**:
- Date OLX = doar preț + titlu (fără suprafață, an, stare)
- OLX NU e în căutarea automată (doar extensie browser = volum mic)
- Imobiliare/Storia acoperă 80% din piața RO

**DECIZIE**: 
- **Scoate OLX** din pipeline-ul automat (economisește complexitate)
- **EXCEPȚIE**: Păstrează integrarea extensiei browser pentru userii power (rare case unde OLX are exclusive – ex. zone rurale) DAR marchează clar „Date incomplete – folosește cu atenție"

**PIVOT UTIL**: Integrează **OLX API** (https://www.olx.ro/api) pentru VALIDARE PREȚ, nu pentru comparabile:
```python
# După ce ai 5-10 comparabile din Storia/Imobiliare
olx_similar = olx_api.search(zona, tip, suprafata_range)
avg_price_olx = mean([r.price for r in olx_similar])

if abs(avg_price_olx - avg_price_principale) > 0.25:
    WARNING: "Prețurile pe OLX diferă cu 25% – posibilă anomalie piață"
```

---

### (b) Grad de încredere per sursă în UI?

**DA, dar nu ca „scor de încredere" – ca METADATA TRANSPARENTĂ.**

**ANTI-PATTERN**: ❌ „Sursă: Storia.ro – Încredere 95%" (subiectiv, confuz)

**PATTERN RECOMANDAT**: ✅ Badge-uri cu semnificație clară

```
┌─────────────────────────────────────┐
│ ⭐ STORIA.RO                       │
│ ✓ An verificat (din date structurate) │
│ ✓ Suprafață verificată             │
│ ⚠️ Stare estimată de AI             │
│ ⚠️ Finisaj estimat de AI            │
│ 📍 Adresă: str. Exemple, nr. 10    │
│ 🔗 Vezi anunț original              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 📰 IMOBILIARE.RO                    │
│ ⚠️ Toate atributele extrase din text│
│ ℹ️ Posibile inconsistențe           │
│ 🔗 Vezi anunț original              │
└─────────────────────────────────────┘
```

**REGULI DE AFIȘARE**:
1. **Verde** (✓): Atribut din date structurate (__NEXT_DATA__)
2. **Galben** (⚠️): Atribut din LLM cu confidence >0.7
3. **Roșu** (❌): Atribut lipsă sau confidence <0.5
4. **Badge sursă**: Nume + logo, link către original

**NU modifica scorul** pe baza sursei – lasă userul să decidă.

**EXCEPȚIE**: Permite user să excludă o sursă complet („Ascunde toate de pe X") – preferință salvată.

---

## Q7 – Robustețe extracție: consiliu de API-uri?

**RĂSPUNS SCURT**: NU pentru extracție generică, DA pentru câmpuri critice ambigue.

**CONTESTARE**: „Consiliu de API-uri" sună sofisticat dar adaugă:
- Latență (3× mai lent)
- Cost (3× mai scump)
- Complexitate (logică de consolidare)

**CÂND MERITĂ** un consiliu:
- Câmpuri CRITICE cu ambiguitate mare: „stare generală" când textul e contradictoriu („renovat recent" dar „necesită mici lucrări")
- Câmpuri cu RISC FINANCIAR: clasificare teren (intravilan vs extravilan = 10× diferență preț)

**IMPLEMENTARE CHIRURGICALĂ**:

```python
def extract_with_consensus(text, field):
    if field in ["stare", "clasificare_teren"]:
        # Rulează 3 modele ieftine în paralel
        results = await asyncio.gather(
            llama_3_3_70b.extract(text, field),
            qwen_2_5_72b.extract(text, field),
            gemini_flash.extract(text, field)
        )
        
        # Votare simplă
        consensus = Counter([r.value for r in results]).most_common(1)[0]
        
        if consensus[1] >= 2:  # 2/3 acord
            return consensus[0], confidence=0.9
        else:
            # Dezacord – escaladează la model puternic
            return claude_sonnet.extract(text, field), confidence=0.6
    
    else:
        # Câmpuri simple – model ieftin suficient
        return llama_3_3_70b.extract(text, field)
```

**COST**: 
- Câmpuri normale: $0.32/M tokeni (status quo optimizat)
- Câmpuri critice cu dezacord (5% din cazuri): $0.32×3 + $15 fallback = $15.96/M tokeni (dar pe volum mic)
- Impact total: +$0.50/lună la 1000 anunțuri

**ALTERNATIVĂ MAI SIMPLĂ** (RECOMANDATĂ):
În loc de consiliu, **VALIDARE ÎN POST-PROCESARE**:

```python
def validate_extracted_state(state_llm, text_original):
    # Reguli simple bazate pe cuvinte cheie
    keywords_state_5 = ["nou", "la cheie", "2024", "2023"]
    keywords_state_1 = ["demolat", "ruină", "restructurare"]
    
    if state_llm == 5 and not any(kw in text_original.lower() for kw in keywords_state_5):
        return state_llm, confidence=0.4  # SUSPICION
    
    return state_llm, confidence=0.85
```

**DECIZIE Q7**: 
- NU implementa consiliu generic
- DA implementa validare keywords pentru stare/finisaj
- DA implementa consiliu DOAR pentru clasificare teren (#4) când e ambiguă

---

## Q8 – Riscuri, dependențe, ORDINE DE PRIORITATE

### RISCURI MAJORE (impact × probabilitate):

| Risc | Impact | Prob | Mitigare |
|------|--------|------|----------|
| **1. Scraping blocat de Storia/Imobiliare** | 🔴 CRITIC (pierd 80% surse) | 🟡 MEDIE (15%) | Rotație IP, headers realistice, rate limiting, backup parsere |
| **2. LLM instabil pe stare/finisaj** | 🟠 MARE (35% din scor volatil) | 🔴 MARE (30%) | Reduce pondere (Q1), validare keywords, UI confirm |
| **3. Geocoding greșit în zone rurale** | 🟡 MEDIU | 🔴 MARE (40%) | Validare pe comună SIRUTA, fallback la localitate |
| **4. Modelul #2/#3 neimplementat** | 🟠 MARE (60% cerere neacoperită) | 🔴 CERT (100%) | PRIORITATE 1 – vezi mai jos |
| **5. Costuri API explodează** | 🟡 MEDIU | 🟢 MICĂ (10%) | Switch la modele ieftine (Q5), capping $50/lună |
| **6. Anunțuri stale (vândute)** | 🟡 MEDIU (user frustrare) | 🟡 MEDIE (25%) | Verificare 404, marcaj „anunț >60 zile" |

### DEPENDENȚE CRITICE:
1. **Scraping**: Fără protecție anti-block → module moare în 2-6 luni
2. **Geocoding**: Fără el, Q3/Q4 rămân neimplementabile (dar e implementabil – risc scăzut)
3. **Parsere noi (#3 industrial)**: Fără VDI, categoria e inutilizabilă

---

### ORDINE DE PRIORITATE (Roadmap 6 luni)

#### 🚨 P0 – CRITICAL (săptămâna 1-2):
1. **Reduce dependența de LLM pe stare/finisaj**
   - Implementează UI „Confirmă stare" cu dropdown
   - Reduce ponderi (×4→×2, ×3→×1) + flag „estimat"
   - Validare keywords (1 zi muncă)
   - **IMPACT**: -60% volatilitate scoring
   
2. **Switch la modele ieftine pentru extracție**
   - Llama 3.3 70B în loc de Claude Haiku
   - **IMPACT**: -85% cost extracție (simbolic acum, important la scale)

#### 🔥 P1 – HIGH (săptămâna 3-6):
3. **Implementează modelul #2 (apartamente)**
   - Criterii + ponderi din Q1
   - Promovează etaj (×5) și nr. camere (×4)
   - **IMPACT**: 60% din piața RO devine utilizabilă corect
   - **EFORT**: 3-5 zile (ranking logic + teste)

4. **Adaugă parser VDI.ro**
   - Scraping + extracție industrial
   - **IMPACT**: Categoria #3 devine funcțională
   - **EFORT**: 2-3 zile

5. **Protecție anti-block scraping**
   - Rotație User-Agent, rate limiting 1 req/2s, retry logic
   - **IMPACT**: Reduce risc #1 de la 15% → 3%
   - **EFORT**: 1-2 zile

#### 📊 P2 – MEDIUM (luna 2-3):
6. **Geocoding offline (Nominatim)**
   - Setup PostgreSQL+PostGIS, import OSM Romania
   - Geocoding adrese extrase, cache rezultate
   - **IMPACT**: Deblochează Q3/Q4 (distanță în ranking)
   - **EFORT**: 3-4 zile (setup + integrare)

7. **Implementează distanță în ranking** (după #6)
   - Conform framework Q4 (filtru gradual apartamente, caracteristică industrial)
   - **IMPACT**: +15-25% acuratețe ranking în orașe >100k
   - **EFORT**: 2 zile

8. **Îmbunătățește modelul #4 (teren agricol)**
   - Adaugă clasificare, acces drum, utilități (Q1)
   - **IMPACT**: Categoria devine profesională (ANEVAR compliant)
   - **EFORT**: 2-3 zile

#### 🔬 P3 – LOW (luna 4-6):
9. **Integrare Imoradar24 (agregator)**
   - Discovery → follow redirect → scrape sursă originală
   - **IMPACT**: +10-20% acoperire în zone mici
   - **EFORT**: 3 zile

10. **Split categoria #5 în sub-categorii**
    - Birouri, comerciale, hoteluri, agricole speciale
    - **IMPACT**: Acuratețe pe nișe
    - **EFORT**: 5-7 zile (modele + UI)

11. **Search API ca fallback** (Exa)
    - Tier 3 discovery pentru long-tail
    - **IMPACT**: Marginal (+5% acoperire edge cases)
    - **EFORT**: 1-2 zile, +$5-10/lună cost

#### ❄️ BACKLOG:
- Consiliu API-uri pentru câmpuri critice (Q7) – doar dacă validarea keywords eșuează
- Integrare OLX API pentru validare preț (Q6 pivot)
- Verificare automată anunțuri stale (404 check lunar)

---

## Q9 – Ce NU v-am întrebat? Premise contestate? Design de la zero?

### 🎯 Ce NU ați întrebat dar TREBUIE discutat:

#### 1. **VALIDARE – cine verifică că rankingul e bun?**

**PROBLEMĂ CRITICĂ LIPSĂ**: Nu aveți nicio metrică de GROUND TRUTH.

**Întrebări neadresate**:
- Un evaluator ANEVAR ar alege aceleași comparabile cu sistemul vostru?
- Ați validat scorurile cu 10 evaluatori pe 50 de subiecte?
- Există un feedback loop (user marchează „comparabil irelevant")?

**PROPUNERE**:
```python
# Adaugă în UI pentru fiecare comparabil
┌─────────────────────────────────┐
│ Relevanță: 87%                  │
│ [👍 Relevant] [👎 Irelevant]   │
└─────────────────────────────────┘

# Backend
if user_feedback == "irrelevant":
    log_to_analytics(subiect, candidat, scor_calculat, "rejected")
    # Trigger: la 10 reject-uri pe aceeași pereche → review formula
```

**VALIDARE PROACTIVĂ**:
- Colaborare cu 5 evaluatori ANEVAR: fiecare primește 20 subiecte random, alege manual 5 comparabile, compară cu outputul sistemului
- Metrică: **Overlap@5** (câte din top 5 sistemului sunt în top 10 ale expertului?)
- Target: Overlap@5 > 60% = utilizabil, >80% = excelent

**RISC MAJOR NEADRESAT**: Construiți un sistem fără să știți dacă e mai bun decât alegerea manuală.

---

#### 2. **FEEDBACK LOOP TEMPORAL – prețurile evoluează**

**PROBLEMĂ NEADRESATĂ**: Anunțurile au timestamp, piața se schimbă.

**Întrebări**:
- Un comparabil din 2023 e relevant pentru o evaluare din 2025?
- Cum ponderați vechimea anunțului?

**PROPUNERE**:
```python
def temporal_decay(scor_base, data_anunt, data_evaluare):
    zile_vechime = (data_evaluare - data_anunt).days
    
    if zile_vechime < 90:
        decay = 1.0  # perfect
    elif zile_vechime < 180:
        decay = 0.95  # acceptabil
    elif zile_vechime < 365:
        decay = 0.85  # discount 15%
    else:
        decay = 0.70  # discount 30%, marcaj „anunț vechi"
    
    return scor_base * decay
```

**UI**: Badge „🕒 Anunț din ianuarie 2024 – prețurile pot fi diferite acum"

---

#### 3. **ANOMALII ȘI OUTLIERI – detectare proactivă**

**PROBLEMĂ NEADRESATĂ**: Un anunț fake (ex. vilă 500mp la 50k EUR) distorsionează media de preț.

**PROPUNERE**:
```python
def detect_outliers(comparabile):
    prices = [c.pret for c in comparabile]
    median = statistics.median(prices)
    
    for c in comparabile:
        if c.pret < median * 0.4 or c.pret > median * 2.5:
            c.flag_outlier = True
            c.warning = "⚠️ Preț suspect – verifică manual"
```

**UI**: Outlieri afișați ultimii, cu marcaj vizibil.

---

#### 4. **EXPORT PENTRU RAPORT ANEVAR – lipsește complet**

**OBSERVAȚIE**: Modulul e util pentru evaluator DAR evaluatorul trebuie să producă un RAPORT conform ANEVAR.

**ÎNTREBARE LIPSĂ**: Sistemul exportă datele într-un format utilizabil în raportul final?

**PROPUNERE**:
```python
# Buton „Exportă pentru raport"
def export_anevar_format(comparabile_selectate):
    return {
        "tabel_comparabile": pandas.DataFrame([
            {
                "Nr. crt.": i,
                "Adresă": c.adresa,
                "Suprafață (mp)": c.suprafata,
                "An": c.an,
                "Preț total (EUR)": c.pret,
                "Preț/mp (EUR)": c.pret / c.suprafata,
                "Sursă": c.url,
                "Observații": c.diferente_fata_de_subiect
            }
            for i, c in enumerate(comparabile_selectate, 1)
        ]).to_excel("comparabile.xlsx"),
        
        "justificare_ajustari": generate_llm_justification(subiect, comparabile_selectate)
    }
```

**IMPACT**: Reduce timpul evaluatorului cu 40% (din experiență).

---

### 🚫 PREMISE CONTESTATE:

#### **PREMISA 1**: „Rankingul 0-100% e util pentru evaluator"

**CONTESTARE**: Procentul e **OPAC** – userul nu înțelege de ce 87% vs 74%.

**ALTERNATIVĂ**:
- Scor calitativ: ⭐⭐⭐⭐⭐ „Foarte similar" / ⭐⭐⭐ „Similar moderat" / ⭐ „Slab similar"
- SAU afișează DIFERENȚELE explicit:

```
┌─────────────────────────────────────┐
│ str. Exemplu 10, 120mp, 2020        │
│                                      │
│ Foarte similar (⭐⭐⭐⭐⭐)           │
│ ✓ Suprafață apropiată (+5mp)       │
│ ✓ An identic (2020)                 │
│ ⚠️ Stare inferioară (3 vs 5)        │
│ ✓ Aceeași zonă                      │
│                                      │
│ Diferențe estimate: -€8,000 (stare)│
└─────────────────────────────────────┘
```

**DE CE E MAI BUN**: Transparență → încredere. Evaluatorul vede DE CE sistemul preferă un anunț.

---

#### **PREMISA 2**: „LLM-ul e black-box pentru extracție"

**CONTESTARE**: Cereți LLM-ului să extragă dar NU îi cereți să JUSTIFICE.

**FIX SIMPLU**:
```python
# Prompt modificat
"""
Extrage din text:
- Stare (1-5): [valoare]
  CITAT: "[partea din text care justifică]"
  
- Finisaj (1-4): [valoare]
  CITAT: "[partea din text care justifică]"
"""
```

**AFIȘARE UI**:
```
Stare: 4/5 (Foarte bună)
📝 "Proprietatea a fost renovată complet în 2022, instalații noi"
[✏️ Corectează]
```

**IMPACT**: User poate corecta când LLM greșește, AI învață din corecții (fine-tuning viitor).

---

#### **PREMISA 3**: „Căutarea automată = portal real estate"

**CONTESTARE**: Portalurile au doar 60-70% din anunțuri – restul sunt pe site-uri agenții locale, Facebook Marketplace, grupuri private.

**REALITATE**: Pentru evaluări ANEVAR, transactions REALE (nu anunțuri) sunt cel mai bun comparabil → aveți acces la baze de date notariale (ANCPI)?

**PIVOTARE RADICALĂ**:
```python
# Strat 0: Transactions reale (dacă accesibil)
if ANCPI_ACCESS:
    transactions_reale = query_ancpi(zona, tip, perioada_6_luni)
    # Acestea au PRIORITATE peste anunțuri
    
# Strat 1: Anunțuri (secundar)
anunturi = scrape_portals(...)
```

**DIFERENȚĂ CRITICĂ**: Tranzacție reală = preț FINAL negociat. Anunț = preț ASK (adesea 10-15% peste piață).

---

### 🔨 Dacă aș proiecta „Descoperă" de la zero:

#### **DESIGN ALTERNATIV – „Evaluare asistată", nu „Căutare automată":**

**FILOSOFIE**: Evaluatorul ȘTIE ce caută, sistemul îl ASISTĂ, nu înlocuiește.

**FLUX NOU**:
```
1. User descrie subiectul (formular structurat + text liber)
   → Sistem SUGEREAZĂ criterii relevante bazate pe tip
   
2. Sistem CAUTĂ în paralel:
   - Transacții reale (ANCPI/notariat)
   - Anunțuri active (portaluri)
   - Anunțuri istorice (arhivă proprie)
   
3. Afișare în 3 coloane:
   ┌──────────────┬──────────────┬──────────────┐
   │ TRANSACȚII   │ ANUNȚURI NOI │ SIMILARE     │
   │ (6 luni)     │ (active)     │ (salvate)    │
   └──────────────┴──────────────┴──────────────┘
   
4. User DRAG-AND-DROP în raport
   → Sistem generează justificare ajustări automat
   
5. Export direct în template ANEVAR (.docx)
```

**DIFERENȚE CHEIE**:
- ❌ NU mai e „ranking 0-100%" opac
- ✅ E „asistent transparent" – userul conduce, AI ajută
- ❌ NU mai ascunde sursele/logica
- ✅ Expune diferențele explicit
- ❌ NU mai presupune că AI știe mai bine
- ✅ Permite override complet + învățare din feedback

---

## Q10 – Cea mai inovatoare idee (mișcare îndrăzneață)

### 💡 IDEEA: **„Piața Sintetică" – simulare dinamică de preț bazată pe grafuri de proprietăți**

#### **CE:**
În loc să rankăm comparabile STATICE, construim un **GRAF DINAMIC** al pieței imobiliare locale și estimăm prețul subiectului prin **propagare în graf**.

#### **CUM FUNCȚIONEAZĂ:**

**FAZA 1: Construcția grafului**
```python
# Noduri = toate proprietățile din zonă (anunțuri + transactions + subiecte evaluate)
# Muchii = similaritate ponderată (formula actuală)

Graf:
    Subiect (120mp, 2020, stare 4)
        ├─ 0.92 → Anunț A (115mp, 2019, stare 4) [€95k]
        ├─ 0.87 → Tranzacție B (125mp, 2021, stare 5) [€102k sold]
        ├─ 0.81 → Subiect anterior C (120mp, 2018, stare 3) [€88k evaluat]
        └─ 0.76 → Anunț D (130mp, 2020, stare 4) [€98k]
```

**FAZA 2: Estimare prin propagare**
```python
def estimate_price_graph(subiect, graf):
    # Găsește K=10 vecini cu similaritate >0.7
    neighbors = graf.get_neighbors(subiect, min_similarity=0.7, k=10)
    
    # Ponderare inversă cu distanța
    weights = [n.similarity ** 2 for n in neighbors]  # pătrat = mai mult accent pe cei apropiați
    
    # Ajustare pentru diferențe
    adjusted_prices = []
    for n in neighbors:
        base_price = n.price
        
        # Ajustare suprafață
        if n.suprafata != subiect.suprafata:
            base_price *= (subiect.suprafata / n.suprafata)
        
        # Ajustare stare (€200/mp diferență per nivel)
        if n.stare != subiect.stare:
            base_price += (subiect.stare - n.stare) * 200 * subiect.suprafata
        
        # Ajustare temporală (dacă e transaction veche)
        base_price *= (1 + INFLATION_INDEX[n.data → TODAY])
        
        adjusted_prices.append(base_price)
    
    # Medie ponderată
    estimated = np.average(adjusted_prices, weights=weights)
    
    # Interval de încredere (std dev ponderată)
    confidence_interval = np.sqrt(np.average((adjusted_prices - estimated)**2, weights=weights))
    
    return estimated, confidence_interval
```

**FAZA 3: Vizualizare interactivă**
```
UI: GRAF 3D interactiv (Three.js)
- Noduri = proprietăți (culoare = tip, mărime = preț)
- Muchii = similaritate (grosime = forța legăturii)
- User poate:
  - Scoate noduri outliere (recalculare live)
  - Adăuga noi comparabile manual
  - Vedea „lanțuri de influență" (cum anunțul X influențează estimarea)
```

**EXEMPLU VIZUAL**:
```
      [Tranz €102k]
           ║ 0.87
           ║
    [SUBIECT ?]────0.92────[Anunț €95k]
           ║
           ║ 0.81
      [Eval €88k]

Estimare: €96,500 ± €4,200
Influențe: Tranzacție B (35%), Anunț A (40%), Eval C (25%)
```

---

#### **DE CE AR FUNCȚIONA:**

1. **Transparență radicală**: Evaluatorul vede EXACT de ce sistemul propune un preț
2. **Robuștețe la outlieri**: Un anunț fake (€50k vilă) are impact MINOR dacă e izolat în graf
3. **Învățare continuă**: Pe măsură ce adaugi evaluări, graful devine mai dens → estimări mai precise
4. **Conformitate ANEVAR**: Metoda grafurilor = „piață comparativă" (recunoscută metodologie)
5. **Diferențiere competitivă**: Niciun competitor RO nu are așa ceva (verificat)

---

#### **CEL MAI MARE RISC:**

**RISC #1 – Complexitate percepută**
- Evaluatori conservatori pot respinge „AI graph" ca prea complex
- **MITIGARE**: Dual UI – mod simplu (listă clasică) + mod avansat (graf). Introduce graful ca „beta feature" cu tutorial video.

**RISC #2 – Date insuficiente în zone rurale**
- Grafuri rare (5-10 noduri) dau estimări volatilă
- **MITIGARE**: Fallback automat la metoda clasică când `len(neighbors) < 5`. Afișează „Date insuficiente pentru estimare graf – vezi comparabile tradiționale".

**RISC #3 – Performanță la scale**
- Graf cu 100k noduri = calcul lent
- **MITIGARE**: 
  - Index spațial (QuadTree pe lat/lng) – filtrare la 5km radius înainte de calcul similaritate
  - Precomputare nocturnă a muchiilor pentru zone populate
  - Lazy loading – construiește subgraf local doar când e nevoie

**RISC #4 – Validare**
- Cum știi că graful e mai bun decât media aritmetică?
- **MITIGARE**: A/B test pe 100 subiecte evaluate manual de ANEVAR – compară eroare medie absolută (MAE) între:
  - Metoda clasică (ranking top 5 → medie)
  - Metoda graf (propagare ponderată)
  - Target: MAE graf < MAE clasic cu >10% → keep, altfel revert

---

#### **IMPLEMENTARE (6 săptămâni)**:

**Săptămâna 1-2**: Backend graf
- Bibliotecă: NetworkX (Python) sau Neo4j (dacă vrei persistență)
- Algoritem: construcție graf + propagare ponderată
- API: `/estimate_graph` returnează preț + interval + vecini influenți

**Săptămâna 3-4**: UI vizualizare
- Three.js / D3.js pentru graf interactiv 3D/2D
- Sidebar cu explicații („Anunțul X contribuie cu 35% la estimare")
- Toggle simplu/avansat

**Săptămâna 5**: Validare
- Test cu 50 subiecte reale vs evaluări ANEVAR existente
- Colectare feedback de la 5 evaluatori pilot

**Săptămâna 6**: Polish + documentație
- Tutorial video
- Documentație ANEVAR compliance
- Launch ca beta

---

### **ALTERNATIVĂ (dacă graful e prea îndrăzneț):**

**„Evaluare colaborativă cu memory"**

- Salvează TOATE evaluările anterioare ale userului într-un „portfolio personal"
- Când evaluezi un nou subiect, sistemul PRIORITIZEAZĂ comparabile similare cu ce ai evaluat înainte
- Rațiune: Dacă ai evaluat 20 de case în Breaza, noua evaluare în Breaza ar trebui să fie CONSISTENTĂ cu istoricul tău
- UI: „Ai evaluat 3 proprietăți similare luna trecută – vezi comparație"
- **IMPACT**: Reduce inconsistența între evaluări (problema #1 în audit ANEVAR)

---

## 📋 SUMAR EXECUTIV (TL;DR pentru CEO)

### ✅ IMPLEMENTEAZĂ ACUM (P0-P1, 6 săptămâni):
1. **Reduce riscul LLM** pe stare/finisaj – UI confirm + pondere redusă
2. **Modelul #2 (apartamente)** – 60% din piață
3. **Parser VDI.ro** – categoria industrial devine funcțională
4. **Switch la modele ieftine** – economie cost + same quality

### 📊 NEXT (P2, 2-3 luni):
5. **Geocoding offline** + **distanță în ranking** (apartamente orașe mari)
6. **Îmbunătățire teren agricol** (clasificare, acces)

### 🚀 BOLD MOVE (6 săpt prototip):
7. **Piața Sintetică (graf)** – diferențiator competitiv, transparență radicală

### ⚠️ GOLURI CRITICE NEADRESATE:
- **Validare cu evaluatori ANEVAR** (ground truth lipsește!)
- **Export raport ANEVAR** (ultimul 20% care face produsul util)
- **Feedback loop** (cum învață sistemul din corecții?)

**COST TOTAL estimat (P0-P2)**: 4-6 săptămâni dezvoltare, ~$50-100/lună operațional.

### x-ai/grok-4.3

**Răspuns structurat la Q1–Q10**

### Q1 — Criterii principale per categorie + ponderi + formule
Contest premisa „un singur model de similaritate ponderată liniară”. Formula actuală este rigidă și penalizează agresiv atributele LLM (stare ×4 + finisaj ×3) care sunt volatile. Propun 5 modele distincte:

| Categorie | Criterii principale (pondere) | Formulă similaritate | Note prioritizare |
|-----------|-------------------------------|----------------------|-------------------|
| **#1 Casă+teren** | Suprafață (×5), An (×4), Stare (×3), Finisaj (×2), Teren (×2), Încălzire (×1) | Păstrăm formula actuală, dar reducem ponderea Stare/Finisaj cu 1 punct fiecare | Cel mai matur model |
| **#2 Apartament** | Suprafață (×5), Etaj (×4), Nr. camere (×4), Stare (×3), Finisaj (×2), An (×2) | `d_etaj = min(|e−c|/3,1)` (prag 3 etaje). Etaj devine principal | Promovăm „etaj” și „camere” din datele deja extrase |
| **#3 Spațiu industrial** | Suprafață (×5), Înălțime utilă (×4), Acces auto (×4), Zonare/industrial (×3), Utilități (×2) | `d_acces = 0/0.5/1` (da/parțial/nu) | Prioritate **acoperire** (VDI.ro + Imoradar24) înainte de scoring fin |
| **#4 Teren agricol** | Suprafață (×5), Calitate sol (×4), Acces drum (×3), Irigații/energie (×2) | `d_sol` = mapare categorică (0/0.3/0.7/1) | Model separat de #1 |
| **#5 Proprietate specială** | Model hibrid: 3–4 atribute obligatorii alese de user + fallback embedding semantic | Similaritate cosine pe descriere + preț/mp normalizat | Nu încercăm să modelăm totul determinist |

**Măsuri imediate recomandate:**
- Stare/Finisaj: reducem ponderea la ×3 / ×2 și afișăm badge „extras automat – verifică”.
- Atribute deja extrase dar nefolosite: **promovăm** etaj + nr. camere la #2 și acces auto la #3.
- Prioritizare surse: #3 și #5 înainte de rafinarea scoringului #1.

### Q4 — Distanța în ranking
**Ar trebui inclusă, dar cu greutate mică.** Recomand opțiunea **(c) tie-breaker** cu penalizare mică (max −8–10 puncte).

- Calcul: distanță stradală (Haversine + OSM) → normalizată `min(d/800m, 1)` pentru localități mari și `min(d/1.5km, 1)` pentru localități mici.
- Prag: dacă distanța > 2 km sau > 30% din raza de căutare → devine filtru dur (nu doar tie-breaker).
- Motiv: portalurile nu permit căutare după stradă, deci distanța e un semnal secundar. Nu merită ponderi mari în formula principală.

### Q9 — Ce ne scapă (contestare premise)
Cea mai importantă premisă de contestat: „similaritatea deterministă ponderată pe atribute este metoda optimă”.

Alternative mai puternice:
- Embedding semantic al descrierii anunțului (text-embedding-3-small sau model RO fine-tunat) ca strat complementar.
- Verificare de consistență preț/mp (outlier detection) — dacă un comparabil are preț cu >35% abatere de la mediană, penalizare separată.
- Deduplicare cross-source (același imobil pe 2 portaluri) — lipsește complet azi.
- „Calitate vs cantitate”: ar trebui un mecanism care oprește căutarea când are deja 6–7 comparabile cu relevanță >75%, în loc să returneze 15–20 slabe.

### Q10 — Cea mai inovatoare idee (o singură mișcare)
**Transformă „Descoperă” într-un motor de similaritate bazat pe embeddings + graf de proprietăți.**

- Cum funcționează: fiecare anunț devine un nod cu embedding (text + atribute structurate). La query, se extrage embedding-ul subiectului și se face nearest-neighbor search pe toate anunțurile indexate + rezultate live.
- De ce ar funcționa: rezolvă simultan problema categoriilor eterogene (#5), dependența de reguli manuale și lipsa de granularitate locație.
- Cel mai mare risc: cost și latență la indexing + necesitatea unui strat de deduplicare foarte bun. Soluție de start: index doar anunțurile din ultimele 18 luni + re-indexare săptămânală.

---

**Ordine de prioritate recomandată (Q8 pe scurt):**  
1. Acoperire #3/#5 (surse + parser minimal)  
2. 5 modele de scoring separate  
3. Embedding semantic ca strat complementar  
4. Distanță ca tie-breaker  
5. UI pentru confirmare stare/finisaj

Răspunsurile la Q2, Q3, Q5, Q6, Q7 pot fi detaliate suplimentar dacă vrei.