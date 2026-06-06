# Strategie de comercializare — întrebări + recomandări pentru Adi

> **Pentru Adi, de citit dimineața.** Document de **decizii de luat**, nu de execuție.
> Scris de Claude (sesiune autonomă, 2026-06-06), pe baza:
> [`4-comercializare.md`](specs/4-comercializare.md),
> [`4-comercializare-plan-implementare.md`](specs/4-comercializare-plan-implementare.md),
> [`plan-maine-2026-06-06.md`](plan-maine-2026-06-06.md),
> [`note-viitoare.md`](specs/note-viitoare.md), + citire cod (`logging_setup.py`,
> `__main__.py`, `master_config.py`).
>
> **Cum se citește:** fiecare secțiune are (a) decizia, (b) opțiuni, (c) **RECOMANDAREA mea +
> de ce**, (d) compromisuri. Recomandarea e clară și asumată — nu „depinde". Sunt critic în mod
> deliberat: rolul meu aici e să-ți arăt unde gândirea e solidă și unde e naivă, nu să te laud.
>
> **Premisa produsului (nu se schimbă):** .exe Windows offline care ASISTĂ evaluatorul ANEVAR;
> abonament; AI narativ printr-un gateway online (primește doar text anonimizat, metrează per
> raport). Filozofie: **„om în buclă"** — instrumentul ajută, NU înlocuiește.
>
> **Disclaimer onest:** nu am vorbit cu niciun evaluator. Tot ce ține de adopție, preț și
> dorințe de piață sunt **ipoteze de validat**, nu adevăruri. Le marchez ca atare.

---

## 0. Verdict de o pagină (dacă citești un singur lucru)

**Partea tehnică a planului comercial e foarte bună — probabil 80% gata gândită.** Arhitectura
„offline + gateway care metrează doar apelul AI" e corectă, elegantă și ieftin de întreținut.
Anonimizarea înainte de gateway e un avantaj de vânzare real. Metrarea pe identitatea proprietății
(nu pe fișier) e inteligentă și anti-abuz.

**Partea comercială (non-tehnică) e subdezvoltată și aici e tot riscul.** Planul însuși spune
„riscul e adopția, nu costul" — corect — dar apoi **nu face aproape nimic** în privința adopției.
Lipsesc: un plan de onboarding, un model de încredere (de ce ar avea un evaluator încredere să-ți
trimită text prin gateway-ul tău?), un plan de suport, o definiție de „succes" și de churn, și — cel
mai important — **canalul: cum afli că exiști pentru cei 1.000-4.000 de evaluatori ANEVAR activi?**

**Cea mai mare gaură strategică, deasupra tuturor:** nu există o validare cu oameni reali înainte de
a construi infrastructura. Recomandarea care contează cel mai mult din tot documentul: **înainte de
Supabase/Stripe/OAuth, pune 5 evaluatori reali să folosească exe-ul gratuit și ascultă.** Restul e
inginerie pe care o știi deja face.

---

## 1. Reshape comercial — ce facem bine, ce facem prost, ce ne lipsește

### (a) Decizia
Validăm direcția de transformare în produs comercial din `4-comercializare.md`: e solidă, sau are
găuri care ne costă bani și timp dacă pornim acum?

### (b) Opțiuni
- **B1.** Pornim implementarea comercială ca în plan (gateway → Stripe → trepte).
- **B2.** Pornim, dar adăugăm explicit lucrurile lipsă (onboarding, suport, încredere, retenție)
  ca task-uri de prim rang, nu „faza 3".
- **B3.** **Nu** pornim infrastructura încă; facem întâi o validare cu evaluatori reali pe exe-ul
  gratuit + landing page cu listă de așteptare; construim gateway-ul doar după 5-10 semnale clare.

### (c) RECOMANDAREA mea: **B3 acum → B2 imediat ce ai 3 plătitori-promisiune**

**Ce faci bine (păstrează — nu te atinge):**
- **Filosofia „offline-first + metrezi doar ce te costă".** Asta e diferențiatorul. Un evaluator
  poate lucra fără net, plătește doar lustruirea AI. E corect tehnic și onest comercial.
- **Anonimizarea înainte de gateway** — deja există în cod. E argument de vânzare + simplifică GDPR.
  Foarte puțini concurenți pot spune „datele clientului tău nu pleacă niciodată".
- **Metrare pe identitatea proprietății, nu pe fișier.** Elimină frustrarea „am dat re-download și
  m-a taxat". Anti-abuz inteligent fără să pedepsești userul cinstit.
- **Stack-ul cu mentenanță mică** (Supabase + Stripe + 1 edge function). Realist pentru un singur om.
- **„Riscul e adopția, nu costul".** Diagnoză corectă. Problema e că restul planului n-o tratează.

**Ce faci prost (sau naiv):**
- **Construiești infrastructura înainte de a valida cererea.** Faza 0 (conturi Supabase/Stripe/
  Google) + Faza 1 (gateway + login + metrare + Stripe) = câteva zile-om pentru a putea încasa de la
  **zero clienți validați**. Asta e ordinea inversă. Validezi întâi că oamenii VOR, apoi încasezi.
- **Tratezi adopția ca „marketing de făcut la final".** Adopția nu e un pas; e întregul joc. Pentru
  un produs vândut la o nișă profesională mică (evaluatori ANEVAR), **distribuția > produsul**.
- **Presupui că prețul e principala obiecție.** La un profesionist care taxează 400-1.500 lei/raport,
  99-349 lei/lună e zgomot. Obiecția reală va fi **încredere** („merită rapoartele standard ANEVAR?
  banca le acceptă? AI-ul scrie ceva ce-mi pune semnătura în pericol?") și **inerția** („am deja un
  Word-template care merge").

**Ce lipsește complet (găurile pe care trebuie să le umpli):**

| Lipsă | De ce contează | Minim viabil |
|---|---|---|
| **Onboarding** | Un .exe care pornește în gol = abandon. Primul raport reușit în <30 min e momentul „aha". | 3 dosare-exemplu (LE AI deja, A6) + un tur de 60s + un raport demo gata-făcut. |
| **Model de încredere** | „De ce să-ți trimit text prin gateway-ul tău?" e prima întrebare a unui profesionist. | Pagină clară „ce pleacă / ce nu pleacă" + arată anonimizarea în UI înainte de trimitere + ToS/GDPR. |
| **Suport** | Un singur om = suportul te omoară dacă nu-l canalizezi. | Email + FAQ + un buton „Trimite jurnal de eroare" în app (vezi §4). NU telefon. |
| **Retenție / churn** | Abonament fără retenție = găleată găurită. Trebuie să știi DE CE pleacă oamenii. | Metrici: rapoarte/lună per user; alertă la „0 rapoarte în 30 zile" → email de re-activare. |
| **Activare (nu doar înregistrare)** | „A făcut cont" ≠ „a generat un raport". Doar al doilea contează. | Definește „user activat" = a generat ≥1 raport AI. Urmărește rata de activare. |
| **Conformitate ANEVAR ca produs** | Dacă banca/ANEVAR respinge rapoartele, ești mort. Aici e riscul existențial. | Validare cu 2-3 bănci (ai deja `pachet-validare-banci.md`) ÎNAINTE de a vinde la scară. |

### (d) Compromisuri
- B3 **întârzie „primul leu"** cu câteva săptămâni. Compromis acceptabil: primul leu de la clientul
  greșit (care apoi pleacă) e mai scump decât întârzierea. Validarea e mai ieftină decât churn-ul.
- B3 cere să **vorbești cu oameni** (vânzări, nu cod) — partea inconfortabilă pentru un developer.
  Dar e exact partea care decide dacă proiectul trăiește.
- Riscul lui B3: „paralizie prin validare". Antidot: **timebox de 3 săptămâni** pentru validare, apoi
  decizi GO/NO-GO indiferent de cât de „complet" te simți.

---

## 2. Pagina de administrare a userilor (master-admin)

### (a) Decizia
Cum administrăm concret userii: ce gestionează adminul, unde rulează, securitate, audit.

### (b) Opțiuni
- **B1. Admin „gata făcut":** folosești **Supabase Studio** (consola web a Supabase) + SQL direct +
  câteva view-uri. Zero cod de admin scris de tine.
- **B2. Admin minimal custom:** o pagină web mică (protejată) care citește/scrie tabelele de licențe
  prin service_role, cu acțiuni curente (suspendă, resetează cotă, schimbă legitimație).
- **B3. Admin „produs":** panou complet cu roluri, audit log vizual, bulk actions, dashboard.

### (c) RECOMANDAREA mea: **B1 acum (Supabase Studio + 3-4 view-uri SQL) → B2 când ai >20 useri**

**De ce B1 la început:** ai 0-10 useri. Un panou de admin custom pentru 5 clienți e **gold-plating
clasic**. Supabase Studio îți dă deja: tabel de useri, editare rânduri, SQL editor, RLS, logs. Scrii
3-4 **view-uri / funcții SQL** ca să faci operațiile curente într-o comandă și gata. Construiești panou
abia când frecvența operațiilor manuale devine o bătaie de cap (≈20+ useri).

**Ce gestionează adminul (modelul de date — îl ai deja schițat în `master_config.py`):**

`master_config.py` definește deja separarea corectă:
- `CAMPURI_CONT_DOAR_ADMIN = ["email", "nume_complet", "legitimatie", "format_dosare"]` — **doar
  adminul** le schimbă, niciodată userul din app. Asta e fix decizia bună. Păstreaz-o.
- `CAMPURI_CONT_ALESE_DE_USER = ["format_dosare"]` — singurul ales de user la creare.

Adminul (tu) gestionează, în tabelele gateway:
1. **Conturi:** activează / suspendă / șterge; vezi status abonament, email, dată creare.
2. **Legitimații ANEVAR:** asociază / schimbă / **șterge (doar admin, din DB)** — exact ca în spec.
   Aceasta e câmpul „blocat per user".
3. **Câmpuri blocate per user:** numele complet, formatul dosarelor, legitimația (cele 4 de mai sus).
4. **Cote:** treaptă (Solo/Pro/Nelimitat), `cota_lunara`, reset manual al perioadei, pachete extra.
5. **Anulări / refunds:** prin **Stripe Customer Portal / dashboard** (NU le reimplementa — Stripe e
   sursa de adevăr pentru bani; webhook-ul sincronizează `status` în `abonamente`).
6. **Sesiuni:** vezi sesiunile active per user, „deconectează dispozitiv" (invalidează un rând).

**Arhitectura concretă recomandată:**

```
GATEWAY (Supabase)
├── auth.users                    (gestionat de Supabase Auth — Google SSO + magic-link)
├── abonamente                    (status, treaptă, cotă, stripe ids)  ← din plan
├── consum                        (audit de facturare: cine, ce, când)  ← din plan
├── sesiuni                       (max 2/cont, enforcement licență)     ← din plan
├── profil_user                   (NOU: legitimatie, nume_complet, format_dosare, blocat_de_admin)
├── admin_audit                   (NOU: cine-admin a făcut ce-acțiune, când, pe ce user)
└── RLS pe tot                    (userul își vede DOAR rândul lui; service_role vede tot)
```

- **Unde rulează:** parte din gateway (Supabase). NU în .exe. .exe-ul nu trebuie să aibă niciodată
  capabilitate de admin — altfel un user cu un debugger devine admin. Adminul = Supabase Studio
  (consolă web, autentificată cu contul TĂU de Supabase, separat de conturile de evaluator).
- **Securitate:** (1) **service_role key NU pleacă niciodată** spre client — stă doar în edge
  functions ca secret. (2) **RLS pe toate tabelele** — userul își vede doar rândul lui; orice acces
  cross-user trece prin edge function care verifică. (3) **2FA pe contul tău de Supabase** (ești
  single point of failure — contul tău de admin = cheile regatului). (4) Adminul nu modifică niciodată
  date din .exe; doar din consola web peste HTTPS.
- **Audit:** tabel `admin_audit` (cine, ce acțiune, pe ce user, când). Pentru un produs care ține
  legitimații profesionale și bani, **trebuie** să poți răspunde „cine a schimbat legitimația lui X
  și când". E și protecție pentru tine (dovadă că n-ai umblat abuziv la conturi).

### (d) Compromisuri
- Supabase Studio e „brut" — nu arată frumos, nu are butoane custom. Dar pentru 5-20 useri e **exact
  suficient** și costă 0 ore de dezvoltare. Frumusețea panoului nu aduce niciun leu în plus.
- View-urile SQL cer să fii confortabil cu SQL la operațiile rare (ești). Compromis bun vs. a
  întreține o aplicație de admin separată.
- Riscul cu service_role: dacă vreodată scapă, expune toate datele. De aceea **niciodată în client,
  niciodată în git, doar secret de edge function** — și 2FA pe contul tău.

---

## 3. Procesul de update al aplicației deployate pe calculatoarele clienților

### (a) Decizia
Cum livrăm update-uri la un .exe offline care stă pe laptopurile evaluatorilor.

### (b) Opțiuni
- **B1. Manual:** trimiți .exe nou pe email / link de download; userul îl înlocuiește singur.
- **B2. „Nag" semi-automat:** la pornire app-ul întreabă gateway-ul „care e ultima versiune?"; dacă e
  mai nouă → banner „Versiune nouă disponibilă — descarcă" cu link. Userul descarcă manual.
- **B3. Auto-update complet:** app verifică, descarcă semnat, înlocuiește binarul, repornește
  (gen Squirrel/Sparkle/electron-updater). Canal stable/beta, rollback.

### (c) RECOMANDAREA mea: **B2 la lansare → B3 când ai >50 useri și un ritm de release stabil**

**De ce nu B3 din prima:** auto-update real care se înlocuiește singur pe Windows e **surprinzător de
greu** și riscant (fișier în uz, permisiuni, antivirus care blochează un .exe nesemnat care se
auto-modifică, update întrerupt → binar corupt → user blocat). Pentru un singur dezvoltator, B3 prematur
e o sursă de incidente care îți consumă exact timpul pe care nu-l ai. Un update care strică instalarea
clientului e mai rău decât un update întârziat.

**De ce B2 e suficient și corect la început:**
- Ai **deja jumătate din infrastructură**: gateway-ul e contactat oricum la fiecare apel AI și la
  login. Adaugi un endpoint trivial.
- Userul rămâne în control (un profesionist preferă să decidă când se schimbă unealta lui de lucru —
  nu vrea ca un update surpriză să-i schimbe comportamentul în mijlocul unui raport pentru bancă).

**Soluția concretă B2 (de implementat):**

```
1. Endpoint gateway:  GET /version
   → { "stable": "1.4.0", "min_supported": "1.1.0",
       "url": "https://.../evaluare-anevar-1.4.0.exe",
       "sha256": "…", "note": "https://.../note-versiune#1.4.0",
       "obligatoriu": false }

2. La pornirea .exe (non-blocant, în thread — ca _deschide_browser):
   - citește versiunea locală (o constantă în build, ex. __version__)
   - GET /version (timeout 3s; offline → ignoră tăcut, NU bloca pornirea)
   - dacă local < stable → banner în UI: „Versiune nouă 1.4.0 — vezi noutăți / Descarcă"
   - dacă local < min_supported → mesaj mai ferm: „Versiune prea veche; AI-ul poate fi
     dezactivat. Te rugăm actualizează." (gateway poate refuza AI pe versiuni sub min_supported)

3. Download: link direct către un .exe SEMNAT (vezi mai jos), găzduit pe Supabase Storage / R2 / S3.
   După descărcare, opțional verifici sha256 afișat → încredere.

4. Canale: /version?canal=beta întoarce build-ul beta; userul intră în beta dintr-un toggle în
   Setări. Default = stable.
```

**Semnătura binarului — important, nu opțional pe termen mediu:** un .exe **nesemnat** declanșează
SmartScreen („Windows protected your PC") și sperie orice profesionist; antivirușii pot pune în
carantină. Recomand: **certificat code-signing** (OV ~70-100€/an sau EV pentru reputație SmartScreen
instant). Memoria proiectului notează deja „exe semnat (certificat)" ca blocant extern — **ridică-l
la prioritate înainte de lansarea comercială**, nu după. Un evaluator nu instalează software nesemnat
pe calculatorul de lucru.

**Rollback:** păstrează ultimele 2-3 versiuni semnate la URL-uri stabile. „Rollback" la B2 = schimbi
`stable` în `/version` înapoi la versiunea bună și anunți. Simplu și suficient.

**Note de versiune:** o pagină web simplă (sau secțiune în landing) `note-versiune` — userii
profesioniști vor să știe ce s-a schimbat (mai ales dacă afectează calculul/raportul care le poartă
semnătura). E și un semnal de „produs viu, întreținut" = încredere.

### (d) Compromisuri
- B2 lasă userii pe versiuni vechi (unii nu actualizează niciodată). Mitigare: `min_supported` în
  `/version` → poți forța prin „AI-ul nu mai merge sub versiunea X" (pârghie blândă, fără a sparge
  partea offline care rămâne mereu funcțională).
- B2 cere efort manual al userului. Pentru o nișă mică e ok; pentru scară mare frustrează → atunci
  treci la B3.
- Certificatul costă bani/an înainte de primul venit. Dar e **condiție de intrare** pe calculatoare
  profesionale, nu un lux. Tratează-l ca pe un cost obligatoriu de lansare.

---

## 4. Tratarea defecțiunilor (crash-uri, funcții care nu merg) pe calculatoarele clienților

### (a) Decizia
Cum creăm, colectăm (opt-in GDPR!), triajăm și reparăm defecțiunile pe teren.

### (b) Opțiuni
- **B1. Pasiv:** loguri locale (deja există); userul ți le trimite manual când se plânge.
- **B2. Opt-in telemetrie:** un buton „Trimite raport de eroare" + crash-handler global care prinde
  și erorile din timpul rulării (nu doar la pornire) și oferă trimitere anonimizată la gateway.
- **B3. Telemetrie automată continuă** (Sentry-style): trimite toate erorile automat, mereu.

### (c) RECOMANDAREA mea: **B2 — opt-in explicit, niciodată automat fără consimțământ**

**Ce ai deja (bază bună, dar incompletă):**
- `__main__.py` prinde erorile **la pornire** → scrie `eroare-pornire.log` + afișează „detalii salvate
  în…". Bun, dar **acoperă doar pornirea**.
- `logging_setup.py` scrie un `evaluare-anevar.log` **rotativ** (1 MB × 3) lângă .exe în modul frozen.
  Bun pentru diagnoză locală.
- **GAURA:** erorile **din timpul rulării** (un endpoint API care crapă, un import URL care eșuează, un
  apel la gateway care dă excepție în UI) nu sunt prinse de un handler global — ajung în log dacă au
  noroc, dar nu există o cale prin care userul să ți le trimită ușor.

**Ce de adăugat (concret):**

1. **Handler global de excepții, extins dincolo de pornire:**
   - **Backend (FastAPI):** un `exception_handler` global → orice excepție neprinsă într-un request
     → loghează cu un **`incident_id`** scurt (ex. 8 caractere) + întoarce userului un mesaj prietenos
     „Ceva n-a mers (cod ABC123). Poți trimite un raport de eroare din Setări." Userul vede un cod, nu
     un traceback.
   - **Process-level:** `sys.excepthook` + `threading.excepthook` → scrie în log + marchează ca incident.
   - **Frontend (UI):** prinde erorile de fetch către API → același mesaj cu cod.

2. **Buton „Trimite raport de eroare" (opt-in, GDPR):**
   - În Setări / la afișarea unui incident: „Trimite acest raport dezvoltatorului?" cu **preview a ce
     se trimite** (transparență). Trimite la gateway: `incident_id`, versiune app, OS, traceback,
     ultimele N linii de log — **fără date de client** (rulează prin același anonimizator pe care-l
     ai deja înainte de gateway; sau, mai sigur, NU include conținut de dosar deloc, doar tehnic).
   - **Consimțământ explicit de fiecare dată** (sau o setare „trimite automat rapoarte de eroare
     anonime" oprită implicit, pe care userul o poate porni). Niciodată automat fără opt-in — ești
     un produs care se laudă cu confidențialitatea; telemetrie ascunsă ar distruge exact acel avantaj.

3. **Colectare la gateway:** tabel `incidente` (incident_id, user_id opțional, versiune, os, mesaj,
   traceback, log_excerpt, creat_la). Dedup pe hash de traceback → vezi „eroarea X a lovit 7 useri".

4. **Triaj + ciclu fix→release:**
   - Dashboard simplu (un view SQL / o pagină) ordonat după **frecvență × nr. useri afectați**.
   - Repari → release (canalul din §3) → marchezi incidentul „rezolvat în 1.4.1".
   - **Bucla:** incident → repro local din traceback + log → fix + test de regresie → release B2 →
     anunț în note-versiune.

**GDPR — reguli ferme:**
- Opt-in, nu opt-out. Preview a ce se trimite. Fără PII de client (doar tehnic).
- Politica de date a gateway-ului acoperă explicit „rapoarte de eroare tehnice anonimizate".
- Retenție limitată pe incidente (ex. 90-180 zile), apoi ștergere.

### (d) Compromisuri
- Opt-in → vei prinde **mai puține** crash-uri decât telemetria automată (mulți nu apasă butonul).
  Compromis corect: pentru un produs cu confidențialitatea ca argument de vânzare, **încrederea >
  completitudinea datelor de crash**. Compensezi prin a face butonul vizibil și fără fricțiune când
  apare un incident.
- Un dashboard de incidente e cod în plus. Minim: trimite incidentele și citește-le din Supabase
  Studio la început; construiește dashboard doar când volumul cere.
- Handler global bine făcut cere puțină muncă de design (să nu „înghită" erori pe care vrei să le vezi
  în dev). Dar fără el, defecțiunile pe teren sunt invizibile = orbire pe care nu ți-o permiți la scară.

---

## 5. Model de preț — opinie

### (a) Decizia
Abonament vs. per-raport vs. hibrid; praguri; freemium/demo; ancorare pe valoare vs. cost.

### (b) Logica noastră actuală (din `4-comercializare.md`)
- COGS ~zero (~$0.005/apel; ~$2-3/lună per evaluator activ). Deci **cota nu acoperă costul — e doar
  pentru tiering + anti-abuz.** Corect.
- Valoare: un raport manual = 4h senior / 8h junior; cu tool → ~1-1.5h ⇒ **economie 2.5-6.5h/raport
  ≈ 350-490 lei valoare**. Clientul final plătește 400-1.500 lei/raport.
- Trepte propuse: Solo 99 lei/10 rapoarte, Pro 199/40, Nelimitat 349/~150, pachet +49/+10.

### (c) RECOMANDAREA mea: **abonament cu trepte (hibrid blând), ancorat 100% pe VALOARE, nu pe cost — dar SIMPLIFICĂ la lansare la O SINGURĂ treaptă**

**Opinia mea critică pe model:**

1. **Per-raport pur = NU.** Creează „anxietate de contor" — userul ezită să genereze de teamă că
   plătește, exact opusul a ce vrei (vrei să-l faci dependent de viteză). La un profesionist, prețul
   per-acțiune e o fricțiune psihologică mult mai mare decât un abonament fix pe care îl uită.

2. **Abonament cu trepte = DA**, dar gândit ca **viteză/liniște**, nu ca „pachet de credite". Mesajul
   nu e „cumperi 40 de rapoarte", ci „**pentru 199 lei/lună nu mai pierzi 3h pe raport**". Treptele
   există ca să segmentezi după volum (= după venitul evaluatorului), nu ca să recuperezi cost.

3. **Hibrid blând = DA, dar discret:** abonament principal + pachet de depășire (+49/+10) ca plasă, nu
   ca model. Pachetul există ca să nu blochezi un evaluator activ în vârf de sezon, nu ca să-l mulgi.

4. **Ancorare pe valoare — aici e marea oportunitate ratată de planul actual.** Planul îți spune
   prețul (99/199/349) **pornind de la cât crezi că „merită un abonament SaaS"**, nu de la valoarea
   creată. Calculul tău propriu zice: economisești **350-490 lei/raport**. Un evaluator Pro care face
   40 rapoarte/lună economisește **14.000-19.600 lei/lună** de valoare. Îi ceri 199. Capturezi **~1-1.5%**
   din valoarea pe care i-o creezi. **E enorm de ieftin.** Out-of-the-box: ai loc să fii de 2-3× mai
   scump și tot ești o ofertă absurd de bună. **Recomand să testezi praguri mai SUS**, nu mai jos:
   Pro la 299-399 lei ar fi încă „no-brainer" pentru cineva care taxează 400-1.500/raport. Prețul mic
   nu doar lasă bani pe masă — **semnalează „jucărie"** unei audiențe profesionale care asociază preț
   cu seriozitate.

5. **Freemium vs. trial — recomand TRIAL, nu freemium permanent.** Freemium permanent la o nișă mică
   îți umple baza de useri care nu plătesc niciodată și consumă suport. Recomand: **trial 14 zile** SAU
   **primele 3-5 rapoarte AI gratis** (oricum, primul care expiră). Plus un **mod DEMO** (deja prevăzut)
   pentru cont fără abonament: vede UI-ul + un raport-exemplu, dar nu generează propriu — exact cât să
   guste valoarea. Asta convertește prin „aha", nu prin „gratis pe veci".

6. **Ancorare în UI:** lângă fiecare raport generat, arată **„Ai economisit ~3h (~400 lei)"**. Și pe
   pagina de preț: „Un singur raport îți acoperă abonamentul pe **2 luni**." Vinzi economia, nu accesul
   la un LLM.

**Structura pe care o recomand la LANSARE (simplificată):**

| Fază | Ce vinzi | De ce |
|---|---|---|
| **Lansare** | **O singură treaptă** (ex. „Pro", ~199-299 lei, ~40 rapoarte fair-use) + trial 14 zile + Demo | Trepte multiple = paralizie de alegere + cod în plus, cu 0 date despre cum cumpără oamenii. Plan multi-treaptă fără clienți reali e ghicit. |
| **Scalare (>10 plătitori)** | Adaugi Solo (jos) + Nelimitat (sus), pe baza datelor reale de consum | Acum știi unde se grupează userii → tarifezi informat. |

### (d) Compromisuri
- O singură treaptă la lansare pierde userii „prea mici pentru Pro" (volum foarte mic). Compromis ok:
  acei useri au oricum LTV mic și suport mare; îi prinzi în faza 2 cu Solo, după ce înțelegi piața.
- Prețul mai sus riscă să sperie la o piață obișnuită cu „ANEVAR = scump deja". Mitigare: **testezi**
  (oferă la 5 evaluatori 199 și la alți 5 „299" și vezi reacția). Nu ghici prețul — A/B pe oameni reali.
- Anchoring „ai economisit 400 lei" poate părea agresiv dacă e prea în față. Ține-l factual și discret
  (un rând, nu un banner) ca să întărească, nu să irite.

---

## 6. „Instrument util, nu înlocuitor"

### (a) Decizia
Cum implementăm transformarea păstrând principiul „ajut evaluatorul, nu-i iau jobul": ce automatizăm,
ce lăsăm explicit omului, cum comunicăm, cum măsurăm „timpul economisit".

### (b) Opțiuni
- **B1.** Maximizăm automatizarea (AI scrie cât mai mult, userul doar aprobă) — „fast but scary".
- **B2.** „Om în buclă" explicit: AI propune, omul decide, fiecare ieșire AI e clar marcată ca draft
  de revizuit, valorile calculate rămân ale motorului determinist, nu ale AI-ului.
- **B3.** AI doar la cerere, minim — riscă să nu aducă destulă valoare ca să justifice plata.

### (c) RECOMANDAREA mea: **B2 — „om în buclă" ca principiu de design vizibil, nu doar slogan**

Acest principiu nu e doar etică/marketing — la rapoarte care **poartă semnătura și răspunderea
profesională a evaluatorului în fața băncii și ANEVAR**, „om în buclă" e și **management de risc**.
Un evaluator NU va folosi un tool care îi pune în raport text pe care nu l-a controlat. Deci principiul
îți și vinde produsul.

**Ce AUTOMATIZĂM (repetitivul, non-judecata):**
- Extragere comparabile din portaluri (ai deja — discovery).
- Calcule deterministe (grilă, cost CIN, teren, reconciliere) — **acestea NU sunt AI**, sunt motorul
  tău; rămân sursa de adevăr pentru cifre. AI-ul nu atinge o valoare numerică finală.
- Asamblare `.docx`, formatare, structură SEV/GEV (repetitiv, fără judecată).
- AML/GDPR/checklist conformitate (repetitiv, regulat).
- **Prima ciornă** a capitolelor narative (descriere, motivare) — ca punct de plecare, nu ca final.

**Ce LĂSĂM EXPLICIT omului (judecata profesională):**
- **Valoarea finală** și reconcilierea abordărilor — decizia evaluatorului, întotdeauna.
- Alegerea/respingerea comparabilelor (AI sugerează scor, omul bifează — ai deja bifele în discovery).
- Ipotezele speciale, condițiile limitative, orice afectează concluzia.
- **Validarea fiecărui text AI** — nimic generat nu intră în raport fără un pas de revizuire.

**Principii concrete de design (de pus în UI):**
1. **Tot ce vine de la AI e marcat „Ciornă AI — revizuiește".** Vizibil, nu ascuns. Userul vede clar
   ce a scris mașina vs. ce a scris/aprobat el.
2. **„Approve to commit":** un text AI nu devine parte din raport până nu apasă userul „Accept/Editez".
   Editarea e încurajată (câmp deschis), nu doar accept/reject.
3. **AI-ul nu inventează cifre.** Numerele din narativ vin din motorul de calcul (template cu valori),
   nu din LLM. Așa eviți halucinațiile pe exact lucrul care contează — cifrele.
4. **Trasabilitate:** la fiecare capitol, „de unde vine asta" (calcul / comparabile / ciornă AI / scris
   de tine). Construiește încredere + e util la apărarea raportului.
5. **Limbaj UI de „asistent", nu de „autor":** butoanele zic „Generează ciornă", „Propune text",
   „Sugerează comparabile" — nu „Scrie raportul". Cuvintele contează: poziționează omul ca autor.

**Marketing-de-produs (nu reclamă) — cum comunici:**
- Mesaj central: **„Termini un raport în 1h în loc de 4. Tu rămâi evaluatorul; noi ștergem munca
  repetitivă."** NU „AI care face rapoarte de evaluare" (sperie + sună a înlocuire + atrage controlul
  ANEVAR).
- Pune „om în buclă" ca **valoare**, nu disclaimer: „Fiecare cifră e calculată determinist. Fiecare
  text e o ciornă pe care tu o aprobi. Răspunderea și semnătura rămân ale tale — la fel și controlul."
- Evită complet promisiuni de „acuratețe AI" / „valoare corectă garantată" — ar transfera spre tine o
  răspundere pe care nu o vrei și ar fi fals.

**Cum măsurăm „timpul economisit" (metrică-far):**
- Definește o **bază** (raport manual = X h, din interviuri cu evaluatori: probabil 3-5h).
- Măsoară **timpul real în app** per dosar (de la creare la `.docx` final) — ai deja stocare pe foldere
  cu timestamp; e ușor.
- Afișează userului: „Acest raport: 1h12m. Estimat manual: ~4h. **Economisit: ~2h48m.**"
- Agregat pentru tine (retenție + marketing): „economie medie/raport", „ore economisite total".
- **Atenție:** măsoară onest. Dacă tool-ul nu economisește timp real, afli devreme (semnal de produs),
  nu te minți cu un număr inventat. Metrica e și instrument de adevăr intern, nu doar de marketing.

### (d) Compromisuri
- B2 e „mai lent" decât automatizarea totală (omul revizuiește) — dar viteza fără încredere = produs
  nevândabil la această nișă. La rapoarte cu răspundere profesională, „lent dar sigur" câștigă.
- Marcarea „ciornă AI" peste tot poate părea că subminează valoarea AI-ului. Invers: **crește**
  încrederea, deci adopția. Un profesionist plătește pentru un asistent în care are control, nu pentru
  o cutie neagră.
- Măsurarea timpului real poate arăta economii mai mici decât speri. E inconfortabil dar **valoros** —
  mai bine știi.

---

## 7. Mindset implicit + out-of-the-box pentru ce urmează

### (a) Decizia
Pentru funcțiile/UI vechi și curent: ce păstrăm, ce retragem, ce reinventăm. Plus: brainstorm pe
termen scurt + produs pe termen mediu.

### (b) Context (din `plan-maine` + `note-viitoare`)
- Decizie deja luată: **fără duplicare UI** — noul UI „output-first" („curent") = unicul țintă; wizardul
  vechi + `/formular` = referință, de retras treptat.
- Schelet nou UI livrat (cont → ÎNCEPE → workspace dosar cu tab-uri output). Stocare pe foldere livrată.
- Popover „!" de mapare vechi→nou e **TEMPORAR** (de șters după validare).
- Decizii de produs care te așteaptă: identitate dosar, lock după prima generare, monedă EUR la
  garantare, etc. (`plan-maine` §B).

### (c) RECOMANDAREA mea

**CE PĂSTRĂM (active reale — nu te atinge):**
- **Motoarele de calcul deterministe** (teren, cost CIN, grilă, reconciliere) — validate pe dosare
  reale GBF. Acesta e **moat-ul** tău. Nimeni nu-l replică ușor. Nu e „AI hype" — e corectitudine.
- **Modulul AML complet** + GDPR + audit + conformitate SEV/GEV. Diferențiator serios față de „un
  template Word". E muncă pe care un concurent AI-generic n-o are.
- **Discovery comparabile** (scraping portaluri validat 100% preț/suprafață). Economisește timp real.
- **Noul UI output-first** + stocarea pe foldere. Direcția e bună (output-first = vede valoarea repede).
- **Anonimizatorul** înainte de gateway. Argument de vânzare + GDPR.

**CE RETRAGEM (datorie de întreținut, fără retur):**
- **Wizardul vechi + `/formular`** — confirmă decizia „fără duplicare". Recomandare concretă: **îngheață**
  (fără feature-uri noi) acum; **retrage** după ce noul UI atinge paritatea de conținut în tab-urile de
  output (AML/GDPR/Audit/Anexe, acum placeholdere) și după ce 2-3 evaluatori confirmă noul flux. NU
  întreține două UI-uri în paralel după lansarea comercială — te ucide ca singur dezvoltator.
- **Popover „!" temporar** — șterge-l imediat ce ai validat maparea vechi→nou (e marcat ca dev peste tot).
- **Cele 2 opțiuni dezactivate din Home** (Import asemănător + Demo, comerciale): pe build-ul offline
  pre-comercial, **ascunde-le** (nu teasere care frustrează); le aprinzi când există gateway-ul.

**CE REINVENTĂM / regândim:**
- **„Importă dosarul tău"** — acum face un singur lucru (raport `.docx`), iar `importa_folder` e
  neconectat. Reinventează ca **un singur punct de import** clar, cu două intenții explicite („raport
  .docx" vs „folder dosar"), nu două butoane confuze (decizia B3 din `plan-maine`).
- **Identitatea dosarului** (`plan-maine` §B1-B4) — e **dependența-cheie** care deblochează metrarea
  comercială (#4). Recomand să o tranșezi **înainte** de orice cod de gateway: setul exact de câmpuri
  de identitate, lock-ul după prima generare, calea „dosar nou + credit". Fără asta, metrarea n-are
  pe ce se ancora. **Aceasta e prioritatea #1 de produs**, peste tot ce ține de comercial.
- **Regenerarea AI per capitol** (Strict/Template/Nou) + matricea `master_administration` — feature
  puternic, dar **amână-l** până după lansarea comercială minimă. E rafinament, nu condiție de „primul
  leu".

**Brainstorm pe termen SCURT (definit — următoarele 2-4 săptămâni):**
1. **Validare cu oameni** (vezi §1, B3): 5 evaluatori pe exe-ul gratuit + landing cu listă de
   așteptare. Output: GO/NO-GO comercial + praguri de preț reale + top 3 obiecții.
2. **Tranșează identitatea dosarului** (§7, deblochează metrarea). Decizie de produs, apoi cod mic.
3. **Certificat code-signing** (deblochează §3 update + încredere la instalare). Cost + setup.
4. **Pachet de validare bănci** (ai deja `pachet-validare-banci.md`): confirmă cu 2-3 bănci că
   rapoartele sunt acceptate. **Risc existențial — verifică-l devreme.**

**Produs pe termen MEDIU (2-6 luni, dacă GO):**
1. **MVP comercial** ca în plan (gateway + 1 treaptă + Stripe + login Google), DAR cu §1-B2 adăugat:
   onboarding + suport + retenție de la început.
2. **Auto-update B2** + telemetrie opt-in B2 (§3-§4).
3. **Paritate noul UI** (conținut real în tab-urile output) → **retragerea wizardului vechi**.
4. **Regenerarea AI per capitol** + import „dosar asemănător" (features de adâncime, după ce baza vinde).

**Out-of-the-box (idei de luat sau lăsat):**
- **„Modul de apărare a raportului":** un sumar trasabil (de unde vine fiecare cifră/text) pe care
  evaluatorul îl poate arăta băncii/la control ANEVAR. Transformă „om în buclă" într-un **feature
  vandabil**, nu doar o filozofie. Diferențiator puternic, ieftin de făcut (ai deja datele).
- **Distribuție prin ANEVAR însuși:** dacă ANEVAR ar accepta tool-ul ca „compatibil/recomandat",
  rezolvi distribuția dintr-o lovitură. Merită explorat un dialog instituțional (canal, nu reclamă).
  Riscant și lent, dar e pârghia de distribuție cea mai mare la o nișă reglementată.
- **Backup online al dosarelor** (prevăzut în note) ca **add-on plătit** — valoare reală (un evaluator
  se teme să piardă dosare) + venit recurent + crește lock-in. COGS mic (stocare).
- **Nu** te extinde la alte tipuri de evaluări (comercial, industrial) până nu domini casă+teren+
  garantare. Focusul pe o nișă îngustă bine servită bate lățimea, la un singur dezvoltator.

### (d) Compromisuri
- Retragerea wizardului vechi prea devreme = riști să pierzi un flux pe care cineva încă îl folosește.
  Mitigare: îngheață întâi, retrage după paritate + confirmare. Nu ține însă două UI-uri viu la nesfârșit.
- Amânarea regenerării AI per capitol = un feature „cool" întârziat. Dar nu e condiție de venit;
  prioritizează ce aduce primul leu și încredere.
- Dialogul cu ANEVAR e lent/incert și te poate distrage de la a vinde direct. Tratează-l ca pariu pe
  termen lung, în paralel, nu ca blocant.

---

## REZUMAT — cele mai importante 5 decizii pentru Adi (≤200 cuvinte)

1. **Validează ÎNAINTE de a construi infrastructura.** Nu porni Supabase/Stripe încă. Pune 5
   evaluatori reali pe exe-ul gratuit + o landing cu listă de așteptare, timebox 3 săptămâni, apoi
   GO/NO-GO. Riscul e adopția — atac-o întâi. *(§1)*

2. **Tranșează „identitatea dosarului" acum — e dependența-cheie.** Metrarea comercială (#4) nu are pe
   ce se ancora fără ea. Decizie de produs mică, deblochează tot restul. Prioritate #1. *(§7, §1)*

3. **Prețuiește pe VALOARE, mai sus, nu pe cost.** Economisești 350-490 lei/raport; ceri 199. Testează
   Pro la 299-399 pe oameni reali. La lansare: **o singură treaptă** + trial 14 zile + Demo. Prețul mic
   semnalează „jucărie" unei piețe profesionale. *(§5)*

4. **Code-signing + update B2 + telemetrie opt-in, de la lansare.** Un .exe nesemnat sperie
   profesioniștii (SmartScreen/antivirus). Update „nag" via `/version`; crash-reports opt-in (GDPR),
   nu automat — confidențialitatea e argumentul tău de vânzare. *(§3, §4)*

5. **„Om în buclă" = feature vandabil, nu doar slogan.** AI marcat „ciornă, revizuiește"; cifrele vin
   din motorul determinist, nu din LLM. Construiește încredere = adopție. Confirmă cu 2-3 bănci că
   rapoartele sunt acceptate — risc existențial. *(§6, §7)*
