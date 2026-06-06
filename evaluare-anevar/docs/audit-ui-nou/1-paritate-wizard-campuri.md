# Audit paritate funcțională — UI VECHI (wizard) vs UI NOU (workspace dosar)

**Scop:** ce s-a PIERDUT funcțional (frontend + backend) în UI-ul nou (`curent/dosar.html`) față de wizard pe zona date-proprietate + flux. Accesibilitatea e tratată de alt agent.

**Fișiere analizate**
- VECHI: `src/evaluare/web/templates/wizard.html` (1–777), `form.html`, `_helpers.js`
- NOU: `src/evaluare/web/templates/curent/dosar.html` (1–291), `routers/curent.py`, `routers/evaluare.py`
- Suport: `curent/incepe.html`, `curent/cont.html`, `master_config.py`, `dosare_fs.py`, `assembler.py`, `models/meta.py`, `models/property.py`, `_design.css`

**Concluzie-cheie:** TOATE câmpurile lipsă din UI-ul nou sunt suportate de backend (`EvaluationInput`/`EvaluationMeta`/`BuildingData`/`LandData` le acceptă). Deci fiecare omisiune e o **regresie de frontend**, nu o limitare a motorului. UI-ul nou trimite mai puține date către același endpoint, deci raportul iese mai sărac.

---

## 1. Răspunsuri la regresiile semnalate de owner

### 1.1 Butonul de ajutor „?" (wireAjutor / hint-toggle) — **NU (regresie confirmată)**
- Wizard: funcția completă `wireAjutor()` construiește un buton `?` (`.hint-toggle`, text `"?"`) lângă fiecare label, leagă `aria-describedby`, popover deschis/închis, Escape + click-afară pentru închidere. Apelată la init. Dovadă: `wizard.html:703-744` (definiție), `wizard.html:774` (apel în lanțul de init), `wizard.html:729` (`btn.textContent="?"`).
- UI nou: există **DOAR** butonul „!" (mapare vechi→nou), NU „?". Codul construiește `.hint-toggle.is-map` cu `textContent="!"`. Dovadă: `dosar.html:195-217`, în special `dosar.html:200` (`b.textContent="!"`) și comentariul `dosar.html:157` („TEMPORAR (dev); se va șterge"). `wireAjutor` nu există nicăieri în `dosar.html` (0 ocurențe).
- CSS-ul pentru ambele există deja (`_design.css:206` `.hint-toggle`, `:226` `.hint-toggle.is-map`), deci „?" ar putea fi readus fără muncă de stil.
- **Verdict owner: corect.** „?" (ajutorul didactic per câmp) a fost șters; a rămas doar „!" (mapare de dezvoltare, temporară). Ar trebui să existe ambele — „?" e ajutorul de producție, „!" e un artefact de dev.
- **Impact: MARE.** Hint-urile didactice (ce înseamnă Acd, an_referinta, cotă indiviză, rată de capitalizare etc.) sunt singura documentație in-app; fără ele un evaluator nou nu știe ce introduce.

### 1.2 Schimbarea setului de câmpuri la TIP proprietate — **NU (regresie confirmată)**
- Wizard: `<select id="tip_proprietate" onchange="aplicaTip(this.value)">` (`wizard.html:139`) + funcția `aplicaTip()` (`wizard.html:417-426`) face show/hide pe `ap-fields`, `ind-fields`, `agr-fields`, `grup-teren` (ascuns la apartament), `grup-constructie` (ascuns la agricol). Apelată și la init (`wizard.html:774`). Și `asambleaza()` golește elemente/depreciere când tip=agricol (`wizard.html:617-620`).
- UI nou: `<select id="tip_proprietate">` **fără** `onchange` și **fără** funcție echivalentă (`dosar.html:47-50`). Nu există `aplicaTip`, `ap-fields`, `ind-fields`, `agr-fields`, `grup-teren`, `grup-constructie` (0 ocurențe în `dosar.html`). Câmpurile specifice de tip (etaj, niveluri bloc, an bloc, cotă indiviză, înălțime liberă, categorie folosință, clasă calitate) **nu există deloc** în formular. Singura adaptare la tip e în `asambleaza()`: `faraConstr=(tip==="agricol")` golește elements/depreciation (`dosar.html:261-262`).
- **Verdict owner: corect.** Setul de câmpuri NU se mai schimbă la selecția tipului; mai mult, câmpurile condiționate au dispărut complet din UI (vezi tabelul, secțiunea „câmpuri specifice de tip").
- **Impact: CRITIC.** Pentru apartament nu se poate introduce etaj/cotă indiviză; pentru hală nu se poate introduce înălțimea liberă; pentru teren agricol nu se pot introduce categoria de folosință și clasa de calitate — toate suportate de `BuildingData`/`LandData` (`property.py:52-56`, `:67-68`). Backend-ul le primește, UI-ul nu le oferă.

### 1.3 Cursul EUR (curs BNR, /api/curs-bnr) — **NU (regresie confirmată)**
- Wizard: câmp `curs_valutar` + buton `#btn-curs-bnr` „↻ Curs BNR (azi)" care apelează `GET /api/curs-bnr?moneda=EUR` și completează cursul + afișează data BNR. Dovadă: `wizard.html:333-339` (UI), `wizard.html:575-584` (handler fetch). Cursul e trimis în payload (`meta.curs_valutar`, `wizard.html:642`).
- UI nou: **0 ocurențe** pentru `curs-bnr`, `curs_valutar`, `btn-curs-bnr` în `dosar.html`. `asambleaza()` din UI nou NU pune `curs_valutar` pe `meta` (`dosar.html:259-260` — doar `beneficiar` e adăugat opțional).
- Backend: `EvaluationMeta.curs_valutar` există (`meta.py:28`) și e folosit la afișarea echivalentului EUR/LEI (`routers/evaluare.py:147-152`). Endpoint-ul `/api/curs-bnr` e referit de wizard; rămâne neapelat din UI nou.
- **Verdict owner: corect.** UI-ul nou nu mai trage și nici nu mai trimite cursul. Conversia EUR↔LEI din raportul de garanție (uzual cerută) nu mai are sursă de curs.
- **Impact: MARE.** Rapoartele de garantare folosesc de regulă EUR cu echivalent LEI la cursul BNR; fără câmp + fără buton, evaluatorul nu poate seta cursul → echivalentul lipsește din raport.

### 1.4 Opțiunile de la „Generează" — **parțial pierdute + o opțiune nouă adăugată**
Wizard (Pas 5) oferă 3 acțiuni + atașare fișiere la Pas 4:
- `📄 Generează și descarcă raportul .docx` — **PĂSTRAT** (`dosar.html:136` `#genereaza`).
- `📝 Raport cu note (demo)` (`?demo=1`, adnotări de proveniență) — **PIERDUT.** Dovadă VECHI: `wizard.html:363`, `wizard.html:690-695` (`descarcaRaport(true)` → `?demo=1`); backend suportă: `evaluare.py:57,65` (`demo`/`adnotari`). UI nou cheamă `POST /api/dosar/{uid}/raport.docx` care în `curent.py:147` apelează `genereaza_raport(..., adnotari=False)` hardcodat — **nicio cale spre demo**.
- `🧾 Urmă de audit (.txt)` — **PIERDUT din acțiunile directe.** VECHI: `wizard.html:364`, `:696-699` (`/api/evaluare/{id}/audit.txt`; backend `evaluare.py:99-129`). UI nou: tab „Audit" spune doar „se descarcă … în versiunea comercială" (`dosar.html:147`) — fără buton.
- Atașare **Fotografii** (Anexa 2) + **Documente** (Anexa 3) la Pas 4 — **PIERDUT.** VECHI: `wizard.html:341-350` (inputuri `foto`/`doc`), `:548-573` (wireUpload, base64 în memorie), trimise ca `photos`/`documente` (`wizard.html:667-668`). UI nou: tab „Anexe" zice „Atașarea fișierelor vine cu versiunea comercială" (`dosar.html:149`); `asambleaza()` nu trimite `photos`/`documente`. Backend le acceptă (`assembler.py:97-98,185-186`).
- **NOU în UI nou (nu e pierdere):** checkbox de asumare profesională care **blochează** „Generează" până la bifare (`dosar.html:131-136,191-193`). Bun — îl notez ca îmbunătățire, nu regresie.
- **Impact: demo MIC** (review intern), **audit MARE** (urmă probatorie cerută la garantare/litigii — gated la „comercial"), **foto/documente MARE→CRITIC** (Anexa 2/3 sunt cerute de structura SEV a raportului; gated la „comercial").

### 1.5 Comentariul „Identificare (obligatorii la creare; se blochează după prima generare)" — **înșelător; nu reflectă codul**
- Textul sugerează că (a) câmpurile de Identificare sunt **obligatorii la creare** și (b) se **blochează după prima generare** a raportului. Dovadă: `dosar.html:36`.
- Realitate cod:
  - „Dosar nou" trimite `wizard:{}` gol și sare direct în workspace (`incepe.html:60-66`); `creeaza_dosar` nu validează niciun câmp (`curent.py:47-54`). Deci **NU sunt obligatorii la creare** — pot rămâne goale; numele dosarului devine `?_?_?` (`master_config.py:44`, `nume_dosar` pune „?" pentru lipsă).
  - **NU există nicio blocare** după generare. Câmpurile de identitate n-au atribut `disabled`/`readonly` și nu se dezactivează nicăieri după `POST …/raport.docx` (`dosar.html:280-288`). `dosare_fs` recalculează identitatea la FIECARE salvare (`dosare_fs.py:80-92`), fără să o înghețe. Schimbarea identității ar trebui (per comentariile din cod) să facă „dosar nou", dar nu e implementat (`dosare_fs.py:21-23` e doar o notă).
- **Are sens? Nu așa cum e scris.** Comentariul descrie un comportament neimplementat (contract viitor). Ar trebui fie (1) implementat (validare la creare + freeze al câmpurilor de identitate după prima versiune .docx), fie (2) reformulat ca să nu mintă utilizatorul (ex. „Identificare — recomandate; vor fi blocate după prima generare în versiunea comercială").
- **Impact: MARE.** Promite o garanție de integritate a dosarului (identitate înghețată = trasabilitate) care nu există → risc de încredere falsă + dosare cu nume „?_?_?".

### 1.6 Flux creare dosar + denumire folder — **se cer informațiile prea târziu; nu se blochează**
- Numele dosarului = template ales la cont (min 3 câmpuri, ex. `id_client_nume_client_tip_proprietate`) compus din valorile wizard (`cont.html:21-30`, `master_config.py:14-45`, `dosare_fs.py:48`).
- Problema de moment: dosarul se creează **înainte** să existe vreo valoare (`wizard:{}` → `incepe.html:62-63`), deci numele inițial e `?_?_?`. Se recalculează abia când userul completează și se declanșează autosave (`dosare_fs.py:88-91`). Nu există ecran/validare „completează câmpurile din titlu înainte de a crea". Owner-ul cere explicit câmpurile din numele folderului „la momentul potrivit" — acum nu se cer la creare.
- `id_client` e marcat `editabil_dupa_creare: False` (`master_config.py:15`) și e descris ca unic, dar UI-ul nu îl face `readonly` după creare și nu verifică unicitatea (input liber `dosar.html:38`).
- Blocare după prima generare: vezi 1.5 — inexistentă.
- **Verdict:** fluxul „creează gol, completează pe urmă" e funcțional dar **nu respectă** contractul de denumire (câmpuri de titlu cerute la momentul potrivit + `id_client` blocat). 
- **Impact: MARE.** Foldere numite `?_?_?` pe disc, `id_client` neunic/needitabil doar pe hârtie, fără freeze de identitate.

---

## 2. Tabel paritate câmp-cu-câmp + funcție-cu-funcție

Legendă: ✅ prezent · 🟡 prezent dar degradat/parțial · ❌ lipsă. Liniile = referință din wizard.

### 2.1 Identificare / lucrare (wizard Pas 1)

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Nume client | ✅ | nou `dosar.html:39` ↔ vechi `wizard.html:67` | — |
| ID client (unic, needitabil) | 🟡 | nou `dosar.html:38` (nu există în wizard ca atare); needitabil/unic neimplementat `master_config.py:15` | mare |
| Proprietar (dacă diferă) | ❌ | vechi `wizard.html:72`; backend `meta.py:16`; absent în `dosar.html` | mic |
| Județ | 🟡 | nou input liber `dosar.html:53` vs vechi `<select>` din `/api/localitati` `wizard.html:49,462-479` | mare |
| Localitate | 🟡 | nou input liber `dosar.html:54` vs vechi select + „altă localitate" + slug auto `wizard.html:51-59,472-484` | mare |
| Stradă, nr. | ✅ | nou `dosar.html:55` ↔ vechi `wizard.html:61` | — |
| Nr. cadastral | ✅ | nou `dosar.html:58` ↔ vechi `wizard.html:78` | — |
| Carte funciară | ✅ | nou `dosar.html:59` ↔ vechi `wizard.html:82` | — |
| Beneficiar / finanțator (bancă) | ✅ | nou `dosar.html:60` ↔ vechi `wizard.html:88` | — |
| Scopul evaluării | ✅ | nou `dosar.html:43-46` ↔ vechi `wizard.html:94-100` | — |
| Evaluator (nume) | 🟡 | nou: din cont, hardcodat în payload `dosar.html:259` (`{{ cont.nume }}`), fără câmp editabil; vechi câmp + persistență `wizard.html:107,430-435` | mic |
| Legitimație evaluator | 🟡 | nou: din cont `dosar.html:259`; vechi câmp `wizard.html:112` | mic |
| Data evaluării | ✅ | nou `dosar.html:64` ↔ vechi `wizard.html:118` | — |
| Data raportului | ✅ | nou `dosar.html:63` ↔ vechi `wizard.html:122` | — |
| Data inspecției/vizită | ✅ | nou `dosar.html:65` ↔ vechi `wizard.html:126` | — |

### 2.2 Import / pornire rapidă

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Import PDF cu pre-completare (CF/releveu/plan/CPE) | ❌ | vechi `wizard.html:32-44,586-612` (`/api/ingestie`, mapare câmpuri); absent în `dosar.html` (există doar import .docx întreg pe `incepe.html:75-87`) | mare |
| Import anunț din URL (imobiliare/storia) | ❌ | vechi `wizard.html:271-274,533-546` (`/api/import-url`); absent în `dosar.html` | mare |

### 2.3 Proprietate — tip + câmpuri condiționate (wizard Pas 2)

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Select „Tip proprietate" (5 tipuri) | 🟡 | nou prezent dar inert `dosar.html:47-50`; vechi cu `onchange=aplicaTip` `wizard.html:139` | critic |
| Show/hide câmpuri la tip (`aplicaTip`) | ❌ | vechi `wizard.html:417-426`; nicio funcție în `dosar.html` | critic |
| Etaj (apartament) | ❌ | vechi `wizard.html:149`; backend `property.py:52`; absent | mare |
| Nr. niveluri bloc | ❌ | vechi `wizard.html:150`; backend `property.py:53`; absent | mare |
| An construcție bloc | ❌ | vechi `wizard.html:151`; backend `property.py:54`; absent | mare |
| Cotă teren indiviză (mp) | ❌ | vechi `wizard.html:153`; backend `property.py:55`; absent | mare |
| Înălțime liberă (industrial) | ❌ | vechi `wizard.html:160`; backend `property.py:56`; absent | mare |
| Categorie de folosință (agricol) | ❌ | vechi `wizard.html:165-173`; backend `property.py:67`; absent | mare |
| Clasă de calitate 1–5 (agricol) | ❌ | vechi `wizard.html:174`; backend `property.py:68`; absent | mare |

### 2.4 Teren + construcție (date fizice)

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Suprafață teren (mp) | ✅ | nou `dosar.html:69` ↔ vechi `wizard.html:181` | — |
| Valoare teren (lei) | ✅ | nou `dosar.html:70` ↔ vechi `wizard.html:186` | — |
| Au — arie utilă | ✅ | nou `dosar.html:73` ↔ vechi `wizard.html:197` | — |
| Acd — arie construită desfășurată | ✅ | nou `dosar.html:74` ↔ vechi `wizard.html:200` | — |
| An referință | ✅ | nou `dosar.html:75` ↔ vechi `wizard.html:205` | — |
| Elemente de cost (textarea) | ✅ | nou `dosar.html:77-79` ↔ vechi `wizard.html:209-211` | — |
| Depreciere fizică (textarea) | ✅ | nou `dosar.html:80-81` ↔ vechi `wizard.html:212-215` | — |

### 2.5 Comparabile (wizard Pas 3)

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Atribute potrivire: An construcție subiect | ❌ | vechi `wizard.html:231` (`attr_an`); absent în `dosar.html` | mare |
| Atribute potrivire: Stare construcție | ❌ | vechi `wizard.html:236-243` (`attr_stare`); absent | mare |
| Atribute potrivire: Nivel finisaj | ❌ | vechi `wizard.html:246-252` (`attr_finisaj`); absent | mare |
| Atribute potrivire: Tip încălzire | ❌ | vechi `wizard.html:255-256` (`attr_incalzire`); absent | mare |
| Atribute secundare (FYI, AI) | ❌ | vechi `wizard.html:263-267`; absent | mic |
| Buton „Descoperă comparabile în zonă" | 🟡 | nou doar link extern `dosar.html:85-86` (`/descoperire`); vechi inline `wizard.html:268,486-512` (`/api/descopera`, candidați bifabili, tabel atribute) | mare |
| Tabel candidați + bifare → grilă | ❌ inline | vechi `wizard.html:498-531` (`tabelAtribute`, `aduna`); nou delegat la pagină separată `dosar.html:85-86` | mare |
| Import anunț din URL (în Pas 3) | ❌ | vechi `wizard.html:271-274`; absent | mare |
| Comparabile grilă (preț;supr) | ✅ | nou `dosar.html:87-88` ↔ vechi `wizard.html:279` | — |
| Comparabile teren (preț/mp;supr) | ✅ (nou, plus față de wizard) | nou `dosar.html:89-90`; backend `land_comparables` `assembler.py:84,125-127` | — |
| Link „Grile detaliate" | ✅ | nou `dosar.html:91` (`/grila`) | — |

### 2.6 Metodă & calcul (wizard Pas 4)

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Adresă pentru raport (cu diacritice) | ❌ | vechi `wizard.html:287-288,449,482-484` (`adresa_raport` + `composeAdresa`); nou compune adresa brut din județ+localitate+stradă `dosar.html:259`, fără câmp editabil | mare |
| Select Metodă (cost/piață/ponderată/venit/dcf) | ✅ | nou `dosar.html:96-99` ↔ vechi `wizard.html:293-299` | — |
| Câmpuri Venit (VBP, neocupare, cheltuieli, rată cap) | ✅ | nou `dosar.html:103-113` ↔ vechi `wizard.html:300-310` | — |
| Câmpuri DCF (fluxuri, rată, rezidual) | ✅ | nou `dosar.html:114-122` ↔ vechi `wizard.html:311-321` | — |
| Show/hide Venit/DCF la metodă | ✅ | nou `dosar.html:245-249` (`sincronMetoda`) ↔ vechi `wizard.html:293` inline | — |
| Monedă raportare (EUR/LEI) | ✅ | nou `dosar.html:100-101` ↔ vechi `wizard.html:324-327` | — |
| Curs valutar EUR/LEI (câmp) | ❌ | vechi `wizard.html:333-334`; backend `meta.py:28`; absent | mare |
| Buton „↻ Curs BNR (azi)" | ❌ | vechi `wizard.html:337,575-584` (`/api/curs-bnr`); absent | mare |
| Preluare VBP din grila de chirii | ❌ | vechi `wizard.html:746-757` (`preiaVbpGrila`, `localStorage vbp_din_grila`); absent în `dosar.html` | mic |
| Fotografii (Anexa 2) | ❌ | vechi `wizard.html:341-345`; backend `assembler.py:97`; nou „comercial" `dosar.html:149` | mare |
| Documente (Anexa 3) | ❌ | vechi `wizard.html:346-350`; backend `assembler.py:98`; nou „comercial" `dosar.html:149` | mare |
| Buton „Calculează" | ✅ | nou `dosar.html:123,270-279` ↔ vechi `wizard.html:351,671-688` | — |
| Afișare valoare finală | ✅ | nou `dosar.html:275` ↔ vechi `wizard.html:685` | — |
| Afișare ALERTE de validare (warn/block) | 🟡 | backend întoarce `alerte` (`curent.py:136`), dar UI nou NU le afișează (`dosar.html:275` arată doar valoarea); vechi le randează `wizard.html:680-685` | mare |

### 2.7 Raport / generare (wizard Pas 5)

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Generează + descarcă .docx | ✅ | nou `dosar.html:136,280-288` ↔ vechi `wizard.html:362,690-695` | — |
| Raport cu note (demo / adnotări) | ❌ | vechi `wizard.html:363,690-695`; backend `evaluare.py:57,65`; nou hardcodat `adnotari=False` `curent.py:147` | mic |
| Urmă de audit (.txt) | ❌ | vechi `wizard.html:364,696-699`; backend `evaluare.py:99-129`; nou „comercial" `dosar.html:147` | mare |
| Versionare .docx în folder | ✅ (nou) | nou `curent.py:148`, `dosare_fs.py:109-122` | — |
| Checkbox asumare profesională (blochează Generează) | ✅ (nou, plus) | nou `dosar.html:131-136,191-193` | — (îmbunătățire) |
| Backup dosare (.db) | 🟡 | vechi `wizard.html:376` (`/api/backup.db`); nou inexistent în workspace (alt model: foldere) | mic |
| Formular clasic (link) | ❌ | vechi `wizard.html:377`; absent | mic |
| Reset dosar | 🟡 | vechi `wizard.html:375,460`; nou: autosave continuu, fără reset explicit | mic |

### 2.8 Funcții JS / comportamente live

| Element (wizard) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| Ajutor „?" per câmp (`wireAjutor`) | ❌ | vechi `wizard.html:703-744`; absent | mare |
| Mapare „!" vechi→nou | ✅ (nou, temporar) | nou `dosar.html:195-217` (marcat „se va șterge") | mic |
| `aplicaTip` (câmpuri pe tip) | ❌ | vechi `wizard.html:417-426`; absent | critic |
| Liste județ/localitate din API + slug auto | ❌ | vechi `wizard.html:462-484`; nou input liber | mare |
| Curs BNR live | ❌ | vechi `wizard.html:575-584`; absent | mare |
| Ingestie PDF → pre-completare | ❌ | vechi `wizard.html:586-612`; absent | mare |
| Descoperire comparabile inline + bifare | ❌ | vechi `wizard.html:486-531`; nou link extern | mare |
| Import URL anunț | ❌ | vechi `wizard.html:533-546`; absent | mare |
| Upload foto/documente (base64) | ❌ | vechi `wizard.html:548-573`; nou „comercial" | mare |
| Recap live „Date dosar" (panou lateral) | ❌ | vechi `wizard.html:380-394,758-772` (`actualizeazaRecap`); absent în `dosar.html` | mic |
| Afișare alerte validare la calcul | ❌ | vechi `wizard.html:680-685`; nou ignoră `alerte` | mare |
| Persistență evaluator între sesiuni | 🟡 | vechi localStorage `wizard.html:430-435`; nou: din cont (alt model, OK) | — |
| Autosave în folder (debounce) | ✅ (nou) | nou `dosar.html:219-227` | — |
| Tabs/sub-tabs WAI-ARIA | ✅ (nou) | nou `dosar.html:229-243` | — |

---

## 3. Rezumat — Top 8 pierderi (ordonate după impact)

1. **CRITIC — Câmpurile nu se schimbă la tipul de proprietate + câmpurile specifice lipsesc.** Fără `aplicaTip` și fără etaj/cotă indiviză/înălțime liberă/categorie folosință/clasă calitate, apartamentele, halele și terenurile agricole nu se pot descrie corect, deși backend-ul le acceptă (`dosar.html:47-50` vs `property.py:52-68`).
2. **MARE — Ajutorul „?" per câmp a dispărut**; a rămas doar „!" (mapare de dev, temporară). Singura documentație in-app s-a pierdut (`dosar.html:195-217` vs `wizard.html:703-744`).
3. **MARE — Alertele de validare nu se mai afișează.** Backend-ul le întoarce, UI-ul nou le ignoră → evaluatorul nu vede „prea puține comparabile/outlier/ajustare prea mare" (`curent.py:136` vs `wizard.html:680-685`).
4. **MARE — Curs BNR + câmp curs valutar eliminate.** Conversia EUR↔LEI cerută la garantare nu mai are sursă (`wizard.html:333-339,575-584` absent în nou).
5. **MARE — Foto (Anexa 2) + documente (Anexa 3) blocate ca „comercial".** Anexele cerute de structura SEV nu se pot atașa, deși pipeline-ul le suportă (`dosar.html:149` vs `assembler.py:97-98`).
6. **MARE — Județ/localitate degradate la text liber.** S-au pierdut listele oficiale + slug-ul auto pentru portaluri + numele cu diacritice în raport (`dosar.html:53-54` vs `wizard.html:462-484`).
7. **MARE — „Identificare obligatorii la creare; se blochează după prima generare" e fals.** Nimic nu e obligatoriu, nimic nu se blochează; dosare cu nume `?_?_?`, `id_client` neunic/needitabil doar pe hârtie (`dosar.html:36` vs `incepe.html:60-66`, `dosare_fs.py:80-92`).
8. **MARE — Ingestie PDF, import URL, descoperire inline + urmă de audit** mutate în afara fluxului sau eliminate; pre-completarea și trasabilitatea probatorie se pierd (`wizard.html:586-612,533-546,486-531,696-699`).

*(Pierderi MICI notabile: proprietar diferit, atribute secundare AI, raport demo, preluare VBP din grila de chirii, recap lateral live, formular clasic.)*
