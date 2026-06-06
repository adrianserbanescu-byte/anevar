# B — Abordări și metode de evaluare: conformitate SEV 103 / 104 / 105 vs. motorul aplicației

**Rol:** audit de conformitate ANEVAR (abordări + metode).
**Domeniu:** SEV 2025 — SEV 103 *Abordări în evaluare* (+ Anexă A10/A20/A30), SEV 104 *Informații și date de intrare*, SEV 105 *Modele de evaluare*.
**Țintă:** motorul `src/evaluare/engine/` + `models/` + `assembler.py` + `profil.py` și planurile din `docs/`.
**Context:** aplicația **asistă** un evaluator (casă+teren, garantare credit). Standardul citit: `C:\Users\adyse\anevar\md files\standardele-de-evaluare-a-bunurilor-2025.md`.
**Data:** 2026-06-06.

Legendă status: ✅ implementat conform · 🟡 parțial / cu rezerve · ❌ lipsă / neconform · 📋 plan, neimplementat.
Bucket: **A** = corectitudine motor (trebuie remediat de noi) · **B** = decizie de raționament profesional (evaluatorul decide; noi doar alertăm/documentăm) · **C** = framing/raport/disclosure.

---

## 1. Cele trei abordări — obligativitate, selecție, neaplicare

| Cerință (SEV ref) | Status | Unde (fișier) | Gap/risc + recomandare | Bucket |
|---|---|---|---|---|
| Există cele 3 abordări principale: piață, venit, cost (SEV 103 §10.1, l.1236-1240) | ✅ | `engine/market.py`, `engine/venit.py` (+ DCF), `engine/cost.py`; orchestrare `assembler.py:115-189` | Toate trei sunt implementate ca motoare distincte și ajung în reconciliere. | — |
| Selecția abordării urmărește maximizarea datelor observabile (SEV 103 §10.2, l.1241; §10.10, l.1296) | 🟡 | `profil.py:17-74`, `assembler.py:61-74` | Aplicabilitatea abordărilor e **statică per tip de activ** (liste fixe în `ProfilEvaluare.abordari_aplicabile`), nu derivată din disponibilitatea/observabilitatea datelor. Nu există un test „câte date observabile susțin fiecare abordare". *Recomandare:* alertă când o abordare din profil rulează fără date observabile suficiente (ex. venit fără chirii de piață). | B |
| Considerarea mai multor abordări când datele concrete sunt insuficiente (SEV 103 §10.6, l.1267-1271) | 🟡 | `assembler.py:146-175` | Motorul rulează doar abordările pentru care s-au introdus date; nu *cere* a doua abordare de confirmare când prima e slab susținută. Garantare credit (GEV 520) cere de regulă piață **+** cost — vezi rândul următor. | B |
| **Obligativitatea fiecărei abordări „când se aplică"** (SEV 103 §20.2 l.1322-1331; §30.2 l.1374-1384; §40.2 l.1414-1429) | 🟡 | `profil.py` (liste fixe), `engine/validation.py:90-100` | Standardul leagă obligativitatea de **circumstanțe** (vânzări recente → piață; capacitate de venit dominantă → venit; recreabil/cost-based → cost). Motorul nu evaluează aceste circumstanțe; doar verifică coerența profil↔ponderi. Pentru casă+teren garantare, profilul `CASA_TEREN_GARANTARE` fixează `["cost","comparatie"]` — rezonabil ca *default*, dar fără verificarea declanșatorilor SEV. *Recomandare:* checklist de declanșatori per abordare (alertă, nu blocaj). | B |
| **Justificarea neaplicării** unei abordări (SEV 103 §40.3 l.1430-1443; §10.11 l.1301-1306; §10.13 l.1313-1317) | ❌ | — (negăsit) | Nu există câmp/validare care să **ceară justificarea scrisă** când o abordare relevantă NU este aplicată (ex. venit neaplicat la o proprietate generatoare de venit). E o cerință explicită SEV pentru conformitate. *Recomandare:* la fiecare abordare absentă din `abordari_aplicabile` care ar fi „uzual" relevantă, cere notă de justificare (model `justificare_depreciere`). | A (gard) / B (conținut) |
| Reconcilierea valorilor — **fără medie aritmetică simplă** (SEV 103 §10.7 l.1272-1277) | 🟡 | `engine/reconciliation.py:48-58`, `reconcile_profil:87-93`, `assembler.py:172-175` | Ponderarea folosește ponderi din profil/UI — OK. DAR „ponderata" cu `pondere_piata=0.5` produce exact **media aritmetică** pe 2 abordări, pe care §10.7 o exclude explicit dacă nu e justificată ca raționament. *Recomandare:* alertă când ponderile sunt egale/implicite („verificați dacă media e justificată; SEV interzice media mecanică"). | B |
| Indicații „foarte diferite" → nu se ponderează mecanic (SEV 103 §10.9 l.1284-1292) | ❌ | `engine/reconciliation.py` | Nu există verificarea **dispersiei** între indicațiile abordărilor. Dacă piața și costul diferă cu, ex., 40%, motorul ponderează liniștit. *Recomandare:* prag de divergență (ex. >15-20%) → alertă „analizați de ce diferă; nu ponderați orb" + cere notă. | A (gard) |
| Reconcilierea = proces descris în raport (SEV 103 §10.7 l.1275-1277) | 🟡 | `models/results.py` `ReconciledResult.nota`, `report/` | Există câmp `nota` (folosit la fallback), dar nu un **raționament de reconciliere obligatoriu** când se ponderează. *Recomandare:* notă de reconciliere obligatorie pe ramura „ponderata". | C |

---

## 2. Metode în cadrul abordării prin piață (SEV 103 Anexă A10, l.1454-1698)

| Cerință (SEV ref) | Status | Unde (fișier) | Gap/risc + recomandare | Bucket |
|---|---|---|---|---|
| Metoda comparației vânzărilor — pași A10.6 (l.1499-1516): unități comparație, comparabile relevante, analiză calitativă/cantitativă, ajustări, reconciliere | ✅ | `engine/market.py`, `engine/land.py`, `models/comparable.py` | Grila pe 2 etape (tranzacție secvențial + proprietate aditiv) acoperă pașii; unitate de comparație = preț total corectat (casă) / EUR/mp (teren). Metodologic apărabilă (validată pe grile reale). | B |
| Metoda listărilor comparabile — ofertele nu pot fi **singura** indicație (A10.3, l.1462-1480); importanță ponderată după angajament/expunere | 🟡 | `models/comparable.py:39` (`tip_oferta`), `engine/market.py` | Câmpul `tip_oferta` ("oferta"/"tranzactie") **există dar nu influențează** selecția/ponderarea în motor (etapa de tranzacție are o ajustare oferta→tranzacție manuală, dar nimic nu împiedică un set 100% oferte). *Recomandare:* alertă dacă toate comparabilele sunt oferte (SEV: nu doar oferte) + dezambiguizare în ajustarea oferta→tranzacție. | B |
| Selecția comparabilelor — preferință pentru număr mai mare, similaritate, recență, surse sigure, tranzacții încheiate (A10.7, l.1517-1535) | 🟡 | `engine/validation.py:46-73` | Există min. 3 comparabile + detecție outlier (deviație >50% față de mediană) + limită ajustare brută (25%). Recența/sursa/încheiat-vs-neîncheiat **nu sunt evaluate**. *Recomandare:* alertă pe vechime ofertă (`data_oferta` există dar nefolosit) și pe sursă. | B |
| Ajustări pentru diferențe (A10.8, l.1536-1559): fizice, **mărime**, localizare, restricții etc. | 🟡 | `engine/market.py` (etapa proprietate), `models/comparable.py` | Ajustările sunt definite de evaluator (corect = bucket B). **Risc de metodologie:** ajustarea de suprafață e tratată ca **liniară** EUR/mp × Δ (vezi market.py docstring l.10-12) — economiile de scară nu sunt modelate; pentru diferențe mari de arie poate denatura. *Recomandare:* alertă când ajustarea de suprafață depășește un prag sau Δarie e mare (>~30%). | B |
| Ajustarea = rezonabilă + **argumentată în scris + cuantificare** (SEV 103 §20.5 l.1358-1364; A10.8) | 🟡 | `models/comparable.py:30` (`Adjustment.justificare`) | Câmp `justificare` există **dar e opțional** (`= ""`); nimic nu cere justificare pentru o ajustare nenulă. *Recomandare:* gard — ajustare nenulă fără justificare → alertă (analog `valideaza_depreciere`). | A (gard) / B |
| Criteriul de selecție a comparabilei (multiplicator dintr-un interval — raționament; SEV 103 §20.6 l.1365-1368) | 🟡 | `engine/market.py:96`, `engine/land.py:69`, `engine/chirie.py:74` | **Regulă unică hardcodată**: se alege comparabila cu **ajustare brută minimă**. E o euristică rezonabilă, dar SEV cere *raționament*, nu o regulă mecanică, și **nu reconciliază** indicațiile multiple (A10.6(f)). Valoarea finală = o singură comparabilă, nu o reconciliere a setului. *Recomandare:* expune toate valorile corectate + permite evaluatorului să aleagă/pondereze; păstrează „brută minimă" doar ca sugestie. | B |
| Verificarea ajustării **nete** (nu doar brute) | 🟡 | `engine/validation.py:67-72` | Se validează doar **ajustarea brută** (>25% alertă). Practica ANEVAR/IROVAL verifică și **ajustarea netă** (prag uzual ~15-20%). `ajustare_neta` e calculată dar **nevalidată**. *Recomandare:* adaugă gard pe net. | A (gard) |
| Discounturi/prime: DLOM, DLOC, primă control, blocaj (A10.16-A10.17, l.1622-1698) | ❌ (N/A rezidențial) | — | Specifice întreprinderi/instrumente financiare; **irelevante** pentru casă+teren garantare. Fără acțiune; de menționat ca „neaplicabil" în raport dacă apar active de tip participație. | C |
| Metoda comparației vânzărilor de pe piața de capital (A10.9-A10.14) | ❌ (N/A) | — | Neaplicabil imobiliar rezidențial. Fără acțiune. | — |

---

## 3. Metode în cadrul abordării prin venit (SEV 103 Anexă A20, l.1699-2055)

| Cerință (SEV ref) | Status | Unde (fișier) | Gap/risc + recomandare | Bucket |
|---|---|---|---|---|
| DCF — pași A20.4 (l.1714-1730): tip flux, perioadă explicită, previziune, valoare terminală, rată actualizare, actualizare | 🟡 | `engine/venit.py:56-72` (`evalueaza_dcf`) | DCF de bază corect (Σ flux_t/(1+r)^t + reziduală/(1+r)^n). DAR e **minimal**: fluxurile sunt o listă dată, fără modelare de tip flux (pre/post-impozit, real/nominal — A20.5 l.1731-1761), fără validarea perioadei explicite (A20.8-A20.11). *Recomandare:* expune ipotezele fluxului ca metadate documentate. | A (completitudine) / B |
| Capitalizarea directă (venit terminal fără perioadă explicită — A20.3 l.1708-1713; A20.10 l.1806-1813) | ✅ | `engine/venit.py:35-48` | NOI = (VBP − neocupare − cheltuieli); Valoare = NOI ÷ rată cap. Corect ca model; gard NOI>0 și rată>0. | — |
| Tipul fluxului consecvent cu rata (A20.5-A20.6 l.1731-1771); **pre/post-impozit** prudent (A20.6 l.1762-1771) | ❌ | `engine/venit.py` | Nicio distincție pre/post-impozit, real/nominal, monedă. Pentru imobiliar SEV cere de regulă **înainte de impozit** — nemarcat/neforțat. *Recomandare:* etichetă explicită a tipului de flux + avertisment de consecvență flux↔rată. | B |
| **Valoarea terminală** — metode: Gordon, valoare de ieșire, valoare de recuperare (A20.22-A20.28 l.1902-1936) | ❌ | `engine/venit.py:32,71` | Valoarea reziduală e o **sumă manuală unică** (`valoare_reziduala`); niciuna dintre cele 3 metode standard nu e implementată (fără Gordon g, fără factor de capitalizare de ieșire). Risc: terminal nedocumentat / inconsecvent. *Recomandare:* măcar Gordon (NOI×(1+g)/(r−g)) și/sau exit-cap, cu validări (r>g). | A (completitudine) / B |
| Rata de actualizare — metodă + **dovezi documentate** (A20.31-A20.34 l.1945-1983) | 🟡 | `engine/venit.py:19,32` | Rata e un input liber; **nu se cere** documentarea metodei (CAPM/WACC/build-up) nici dovezi (A20.34 l.1975-1983 = obligație SEV). *Recomandare:* câmp obligatoriu „metodă + componente rată" când se folosește venit/DCF. | A (gard) / C |
| Risc inclus în rată / previziune analizată (A20.13 l.1823-1834; A20.36-A20.38 l.1989-2037) | 🟡 | `assembler.py:137-144` | Fluxurile/ipotezele nu sunt supuse niciunei analize de plauzibilitate. Bucket B (raționamentul evaluatorului), dar o alertă de coerență ar ajuta. | B |
| Grila de chirii → VBP (susține capitalizarea) | ✅ | `engine/chirie.py` | Chirie de piață prin grilă (2 etape) → VBP anual (chirie×supr×12). Coerent cu metoda venit. Aceleași rezerve de selecție „brută minimă" ca la piață. | B |

---

## 4. Metode în cadrul abordării prin cost (SEV 103 Anexă A30, l.2056-2231)

| Cerință (SEV ref) | Status | Unde (fișier) | Gap/risc + recomandare | Bucket |
|---|---|---|---|---|
| Metoda costului de înlocuire — pași A30.4 (l.2076-2083): cost integral, depreciere (fizică/funcțională/externă), scădere | ✅ | `engine/cost.py:50-79` | CIN = CIB×(1−Dfn)×(1−C_nf)×(1−C_ex). Structura segregată (catalog IROVAL) + teren → valoare cost. Conform metodei. | — |
| Metoda costului de **reconstruire** (A30.6-A30.7 l.2088-2100) | ❌ | — | Neimplementată ca metodă distinctă (replică exactă vs. echivalent modern). Pentru casă comună rar necesară, dar relevantă la clădiri atipice/patrimoniu. *Recomandare:* marcaj că motorul aplică **înlocuire**, nu reconstruire; notă în raport. | B / C |
| Metoda **însumării** (A30.8-A30.9 l.2104-2113) | ❌ (N/A) | — | Specifică societăți de investiții/portofolii. Neaplicabil casă+teren. | — |
| Elemente de cost — directe **+ indirecte** inclusiv onorarii, regie, finanțare, **profitul investitorului** (A30.11-A30.13 l.2117-2150) | 🟡 | `models/property.py:9-25` (`CostElement`) | Modelul are doar `cantitate × cost_unitar` per element. **Costuri indirecte și profitul promotorului/investitorului** nu sunt câmpuri distincte; intră eventual „ascuns" în costul unitar de catalog. SEV cere considerarea lor explicită (A30.11). *Recomandare:* câmp(uri) pentru indirecte + profit promotor (cu prudența A30.12 vs. dublă numărare finanțare/profit). | B |
| Depreciere fizică — recuperabilă vs. nerecuperabilă; bazată pe vârstă/durată viață (A30.17-A30.19 l.2178-2205) | 🟡 | `engine/cost.py:27-47`, `models/property.py:28-33` | Depreciere fizică prin **interpolare liniară** într-un tabel vârstă→depreciere (+ clamp). Apărabil (tabele tip IROVAL/Ross-Heidecke aproximate), dar e o **alegere de metodologie**: liniaritatea între puncte poate subestima/supraestima. VCP = vârstă **cronologică** ponderată, nu efectivă (nu ajustează pentru renovări→vârstă efectivă). *Recomandare:* alertă/opțiune pentru vârstă efectivă; documentează sursa tabelului. | B |
| Depreciere funcțională (2 forme) + economică/externă, **dedusă după fizică+funcțională** (A30.20-A30.21 l.2206-2229) | 🟡 | `engine/cost.py:50-55`, `validation.py:76-87` | Formula aplică C_nf și C_ex **multiplicativ** alături de Dfn — ordine corectă ca efect (externă pe rest), iar deprecierea nenulă **cere justificare** (`valideaza_depreciere`) ✅. Dar funcțională/externă sunt **scalari unici**, fără subcategoriile A30.20 (capital excedentar vs. exploatare excedentară). Bucket B. | B |
| Activ parțial finalizat (SEV 103 §40.4 l.1444-1449) | ❌ | — | Necontemplat (construcție în curs). Rar la garantare casă finalizată; de notat ca limitare. | C |

---

## 5. Ierarhia / selecția datelor de intrare (SEV 104, l.2234-2375)

| Cerință (SEV ref) | Status | Unde (fișier) | Gap/risc + recomandare | Bucket |
|---|---|---|---|---|
| Maximizarea informațiilor **observabile** (SEV 104 §10.3 l.2257-2260; §10.4) | 🟡 | `engine/validation.py`, `discovery/` | Există descoperire de comparabile + validări, dar nicio ierarhie explicită „observabil > derivat > subiectiv". *Recomandare:* etichetare sursă date (observabil/estimat) și preferință în alerte. | B |
| Caracteristici info relevante: acuratețe, completitudine, **actualitate**, transparență (SEV 104 §30.2 l.2280-2289) | 🟡 | `models/comparable.py` (`sursa`, `data_oferta`, `data`) | Câmpurile de sursă/dată **există** dar nu sunt **validate** (actualitate, urmărire sursă). *Recomandare:* alertă actualitate (oferte vechi) + sursă obligatorie. | B |
| Date insuficiente/nesusținute → **neconform SEV** (SEV 104 §40.4 l.2305-2306) | 🟡 | `engine/validation.py:46-54` | Min. 3 comparabile = un prag de suficiență (bun). Dar pentru venit/cost nu există praguri analoge de suficiență a datelor. *Recomandare:* extinde garda de „date insuficiente" la venit (fără chirii) și cost (fără elemente). | A (gard) |
| Documentarea sursei/selecției datelor (SEV 104 §50 l.2310-2318) | 🟡 | `report/`, `models/comparable.py` | `sursa`/`justificare` există; documentarea în raport e parțială și opțională. *Recomandare:* secțiune „surse date" obligatorie. | C |
| Factori **ESG** (SEV 104 Anexă A10 l.2323-2375; element de ajustare A10.8(l) l.1557) | ❌ | — | Niciun câmp/ajustare ESG. Pentru rezidențial garantare e marginal, dar SEV 2025 îl cere „în măsura măsurabilului". *Recomandare:* opțional — câmp ESG (risc inundație/energetic) la teren/clădire (există `clasa_energetica`, neexploatat ca ajustare). | B / C |

---

## 6. Modelul de evaluare (SEV 105, l.2378-2470)

| Cerință (SEV ref) | Status | Unde (fișier) | Gap/risc + recomandare | Bucket |
|---|---|---|---|---|
| **AVM-ul nu produce evaluare conformă** — modelul cere raționament profesional (SEV 105 preambul l.2388-2390; §10.5 l.2404-2406) | 🟡 | tot motorul + UI | Motorul e **determinist** și poate produce o valoare end-to-end (`assembler`). Conform doar dacă e încadrat clar ca **asistare**, evaluatorul deciziile-cheie (selecție comparabile, ajustări, rată, ponderi). Riscul e de **percepție/disclosure**: un motor care alege singur comparabila (brută minimă) și ponderează la 0.5 alunecă spre AVM. *Recomandare:* (a) deciziile-cheie să fie explicit ale evaluatorului; (b) disclaimer „instrument de asistare, nu AVM" în raport. | C (+ B pe automatismele de selecție/ponderare) |
| Caracteristici model adecvat: acuratețe, completitudine, actualitate, **transparență** (SEV 105 §30.1 l.2417-2433) | 🟡 | `engine/*` (cod lizibil), lipsă doc model | Transparență bună la nivel de cod (formule documentate în docstrings). Lipsește **documentația de model** orientată-evaluator (cum funcționează, limitări). *Recomandare:* fișă de model (vezi rândul de documentare). | C |
| Model testat pentru funcționalitate/acuratețe (SEV 105 §40.4 l.2447-2449; §10.4 l.2401-2403) | ✅ | `tests/` (≈345 teste — vezi memorie/jurnal) | Suită de teste extinsă acoperă motoarele. Conform spiritului §40.4. | — |
| Limitări semnificative explicate/justificate; altfel **neconform** (SEV 105 §40.6-40.7 l.2453-2459) | 🟡 | — | Limitările de metodologie (liniaritate suprafață/depreciere, selecție brută-minimă, terminal manual) **nu sunt documentate** ca limitări de model. *Recomandare:* listă de limitări cunoscute în fișa de model + raport. | C |
| **Documentarea modelului** — fundamentare, intrări/ieșiri, intrări semnificative, limitări, QA (SEV 105 §50.1 l.2461-2467) | 📋 | `docs/` (lipsă fișă dedicată) | Nu există un document „fișă de model" pe structura §50.1. *Recomandare:* creează `docs/conformitate/fisa-model-SEV105.md` cu cele 5 elemente. | C |

---

## Top 5 riscuri de metodologie

1. **Neaplicarea unei abordări nu cere justificare; divergența între abordări nu e gardată** (SEV 103 §40.3 l.1430-1443; §10.9 l.1284-1292; §10.7 l.1272-1277). Motorul ponderează (inclusiv media simplă la 0.5) fără să verifice dispersia și fără notă obligatorie de reconciliere. **Acțiune (A-gard):** prag de divergență → alertă + notă obligatorie; cere justificare pentru abordări relevante neaplicate.

2. **Selecția comparabilei = regulă unică „ajustare brută minimă", fără reconcilierea setului** (SEV 103 §20.6 l.1365-1368; A10.6(f) l.1515-1516; A10.7 l.1517-1535). Identic în `market.py:96`, `land.py:69`, `chirie.py:74`. Riscă să alunece spre AVM (SEV 105 l.2388-2390). **Acțiune (B):** expune toate valorile corectate + alegere/ponderare de către evaluator; „brută minimă" doar sugestie.

3. **Valoarea terminală DCF e o sumă manuală; lipsesc Gordon / valoarea de ieșire / recuperare** (SEV 103 A20.22-A20.28 l.1902-1936) și rata de actualizare nu cere documentare (A20.34 l.1975-1983). **Acțiune (A-completitudine + gard):** implementează cel puțin Gordon și exit-cap (validare r>g) și cere „metodă + componente" pentru rată.

4. **Ajustările (inclusiv suprafață) sunt liniare și fără justificare obligatorie; doar ajustarea brută e validată, nu și cea netă** (SEV 103 §20.5 l.1358-1364; A10.8 l.1536-1559). `Adjustment.justificare` e opțional; `ajustare_neta` e calculată dar nevalidată; suprafața = EUR/mp×Δ liniar (`market.py` l.10-12). **Acțiune (A-gard + B):** gard pe ajustare nenulă fără justificare, gard pe net, alertă pe Δarie mare.

5. **Costul de înlocuire ignoră explicit costurile indirecte + profitul promotorului, iar deprecierea folosește vârstă cronologică + interpolare liniară** (SEV 103 A30.11-A30.13 l.2117-2150; A30.17-A30.19 l.2178-2205). `CostElement` are doar `cantitate×cost_unitar`; VCP = vârstă cronologică (fără vârstă efectivă/renovări). **Acțiune (B):** câmpuri pentru indirecte/profit (cu prudența anti-dublare A30.12) + opțiune vârstă efectivă; documentează sursa tabelului de depreciere.

---

### Rezumat (≤180 cuvinte)

Motorul implementează corect **scheletul** celor trei abordări SEV 103: comparația vânzărilor (grilă pe 2 etape, `market.py`/`land.py`/`chirie.py`), capitalizarea directă și DCF de bază (`venit.py`), și costul de înlocuire segregat cu depreciere (`cost.py`). Suita de teste și formulele documentate satisfac spiritul SEV 105 §40.4. **Golurile de conformitate** (nu erori de calcul) sunt concentrate în jurul *raționamentului obligatoriu*: nu se cere justificarea neaplicării unei abordări (SEV 103 §40.3), nu se gardează divergența între abordări și media mecanică (§10.7/§10.9), selecția comparabilei e o regulă unică „brută minimă" fără reconcilierea setului (A10.6(f)), iar DCF nu are valoare terminală standardizată (Gordon/exit) și rată documentată (A20.22-A20.34). Costul ignoră explicit indirectele și profitul promotorului (A30.11). Majoritatea sunt **bucket B** (decide evaluatorul — noi alertăm) sau **C** (framing/raport, mai ales disclaimer-ul „asistare, nu AVM" cerut de SEV 105). Câteva sunt **A-gard** (justificare ajustări, divergență, ajustare netă, suficiență date venit/cost). Nicio neconformitate de aritmetică pură.
