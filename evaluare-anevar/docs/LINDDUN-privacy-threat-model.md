# LINDDUN — Model de amenințări privacy + DSAR/erasure + zeroize-audit

**Aplicație:** ANEVAR — evaluare imobiliară (Python / FastAPI), repo `C:\Users\adyse\anevar`
**Domeniu de date:** PII-heavy, RO, sub incidența GDPR (Reg. UE 2016/679) — CNP, nume, adrese,
acte de proprietate, beneficiar bancar, date KYC.
**Tip livrabil:** audit privacy READ-ONLY (LINDDUN) — lane E.
**Data:** 2026-06-10

> **DRAFT — caracter consultativ.** Acest document informează deciziile GDPR ale
> evaluatorului / juristului; **nu înlocuiește un DPIA juridic** (art. 35 GDPR) și nici o
> opinie de avocat. Operatorul de date cu caracter personal este evaluatorul / cabinetul,
> nu aplicația software. Findings-urile sunt observații tehnice pe cod (fișier:linie), nu
> calificări juridice. Toate severitățile sunt apreciate în ipoteza de utilizare „local-first,
> un singur evaluator pe stația proprie" (modelul de deployment actual).

---

## 0. DFD modelat (fluxul datelor)

```
[1] INTRARE DOSAR                          [2] STOCARE
  formular wizard (web)  ─┐                  ┌─► SQLite  evaluari/import/feedback (db/storage.py)
  upload .docx / PDF     ─┼──► %TEMP%/  ────┤
  (import / submis)       │   (buffer)       └─► foldere pe disc  date/dosare/<uuid>/
                          │                       dosar.json (PII) + raport-*.docx
                          │                       + _cache_antete.json (PII: nume client)
                          ▼
                    [extragere identitate]
                                                [4] AI GATEWAY (extern)
[3] GENERARE raport.docx ──► %TEMP%/raport_*.docx ──┐    Anthropic Claude / Perplexity
                                                     │    primește facts ANONIMIZATE
                                                     ▼    (mask → unmask local)
                                              [anonymizer + safety-net regex]

[5] EXPORT / EXFIL                          [AML — flux separat]
  backup.db (SQLite întreg)                   date/aml_confidential/<tip>_NNNN.json
  backup-dosare.zip (toate folderele)          CNP în clar, retenție 5 ani (store.py)
  audit.txt (adresă+cadastral în clar)
```

**Limite de încredere (trust boundaries):** (a) stația evaluatorului ↔ AI gateway extern
(singura ieșire de rețea cu PII potențial); (b) aplicația ↔ disc local (%TEMP%, foldere, SQLite,
backup-uri) — toate **în clar, necriptate**.

---

## 1. LINDDUN — cele 7 categorii

Rezumat numeric (detalii mai jos):

| Cat. | Categorie | Findings | Severitate max |
|------|-----------|----------|----------------|
| **L** | Linking | 2 | Medium |
| **I** | Identifying | 2 | Medium |
| **N** | Non-repudiation | 1 | Low |
| **D** | Detecting | 1 | Low |
| **D** | Disclosure of information | 5 | **High** |
| **U** | Unawareness | 2 | Medium |
| **N** | Non-compliance | 3 | **High** |
| | **Total** | **16** | |

---

### L — Linking (corelarea persoanei între dosare)

**L1 — Niciun identificator stabil de persoană; linking pe nume liber. [Medium]**
`db/storage.py:97-113` (coloana `client_nume` TEXT) și `dosare_fs.py:52-53,72-82`
(`identitate` = `{nume_client, id_client, ...}`). Persoana e reprezentată ca text liber
(`client_nume`) plus, opțional, un `id_client` provenit din numele fișierului importat
(`importers/docx_dosar.py:39-42`). Nu există o cheie canonică de persoană, deci corelarea
„aceeași persoană în mai multe dosare" se poate face trivial prin potrivire de nume/`id_client`,
dar **fără control**: nu există nicio separare logică între dosarele aceluiași subiect, nici
flag de consimțământ per-persoană. Risc: un agregat de dosare devine un profil de-facto al
unei persoane (toate proprietățile evaluate, toate băncile, istoricul).
*Recomandare:* documentați explicit că aplicația NU pseudonimizează la nivel de stocare
(local-first), și că separarea pe cazuri/clienți e responsabilitatea organizatorică a
evaluatorului. Dacă se trece la multi-tenant, introduceți o cheie de subiect + scoping.

**L2 — Coada de import anunțuri + comparabile leagă proprietăți de surse externe. [Low]**
`db/storage.py:160-187` (`import_anunturi`, dedup pe `sursa_url`). URL-urile de anunț și
comparabilele rămân persistente și pot lega proprietatea evaluată de anunțuri publice
(adresă aproximativă, preț). Risc redus (date deja publice), dar contribuie la re-identificare
prin combinare (vezi I1).

---

### I — Identifying (re-identificare din date aparent anonime)

**I1 — Anonimizare prin substituție de string, nu pseudonimizare reală. [Medium]**
`report/anonymizer.py:19-31`. `mask()` înlocuiește DOAR valorile exacte cunoscute
(`client_nume`, `beneficiar`, `adresa`, `numar_cadastral`, `carte_funciara`, `evaluator_nume`)
cu token-uri `[CLIENT]`/`[ADRESA]`/etc. Datele cantitative trimise la AI (`ai/narrative.py:114-155`
`_facts`) rămân: suprafață teren exactă, Au/Acd, an construcție, localitate (implicit prin zonă),
valoarea finală exactă, EUR/mp. Combinația suprafață + localitate + an + valoare poate
re-identifica o proprietate unică (și implicit proprietarul) chiar cu numele mascat —
un singur imobil de 412 mp construit în 1998 într-o localitate mică e identificabil.
*Recomandare:* documentați că „anonimizat" = pseudonimizat pe identificatori direcți, NU
anonim în sens art. 4(1)/considerent 26 GDPR; pentru cazuri sensibile, recomandați modul offline.

**I2 — Reziduu de PII scapă substituției exacte (variante de scriere). [Medium]**
`report/anonymizer.py:22` — `mask` face `str.replace` pe valoarea EXACTĂ. Dacă numele apare
cu diacritice diferite, abreviat, sau adresa apare parțial în alt format decât `meta.adresa`,
substituția ratează. Safety-net-ul `ai/narrative.py:77-88` (`_PII_REZIDUAL`) acoperă DOAR
CNP (13 cifre), telefon mobil RO și email prin regex — **nu** acoperă nume/adrese parțiale.
*Recomandare:* extindeți safety-net-ul (deja menționat în `plan-lansare-piata.md:189`) și/sau
adăugați normalizare diacritice înainte de `mask`. Pozitiv: CNP e prins de regex înainte de AI.

---

### N — Non-repudiation (jurnalul de audit leagă irefutabil persoana de o acțiune)

**N1 — Urma de audit cu hash conține PII în clar, prin design. [Low — by design, dar de documentat]**
`audit/raport_audit.py:23-25` + `web/routers/evaluare.py:162-163` și `curent.py:218-219`:
evenimentul `identificare` înregistrează `{adresa, cadastral, scop}` în jurnalul cu lanț de hash-uri
(`audit/jurnal.py`), exportat în `audit.txt`. Lanțul de hash e tamper-evident — exact scopul lui
pentru garantarea bancară (pozitiv pentru integritate). Tensiunea privacy: un jurnal inalterabil
leagă irefutabil o adresă/cadastral de o acțiune și de un moment, iar `audit.txt` se exportă în
clar (adresă vizibilă, nu mascată). În contextul garantării bancare acesta e un beneficiu
(non-repudiation = cerut), nu un defect — dar e o categorie LINDDUN relevantă de consemnat:
ștergerea PII (art. 17) intră în conflict cu inalterabilitatea jurnalului.
*Recomandare:* documentați că audit.txt e un livrabil intern/bancă (nu pentru subiectul de date)
și că la o cerere de ștergere jurnalul trebuie tratat ca excepție „obligație legală / pretenții
juridice" (art. 17(3)(b/e)). Verificați cu juristul.

---

### D — Detecting (deducerea existenței unui dosar/persoane din răspunsuri/erori)

**D1 — 404 distinge „inexistent" de erori; enumerare posibilă, dar risc local redus. [Low]**
`web/routers/evaluare.py:73-77,89-93` și `curent.py:136-137,146-147`: `404 "Dosar inexistent"`
vs. răspuns 200 permite, în principiu, deducerea existenței unui dosar prin sondarea ID-urilor
(SQLite: întreg incremental — `evaluare.py` — deci enumerabil 1,2,3…). UUID-urile fluxului nou
(`dosare_fs`) sunt practic neghicibile (mitigare bună). Aplicația nu are autentificare per-utilizator
(local-first, un singur evaluator), deci „detecting" de către un terț presupune deja acces la
mașină — risc scăzut în modelul actual. Devine **High** dacă aplicația e expusă pe rețea/multi-user.
*Recomandare:* dacă apare expunere pe rețea, adăugați auth + rate-limiting; mențineți UUID
(nu ID incremental) ca identificator extern.

---

### D — Disclosure of information (expunere PII) — **zona cu cel mai mare risc**

**D2 — Fișiere temporare cu PII rămân în %TEMP% (fluxul vechi + backup + AML). [High]**
- `web/routers/evaluare.py:108` — `raport_{eid}.docx` scris în `%TEMP%` și **NU** este șters
  după trimitere (`FileResponse` fără `background` de cleanup). Raportul complet (nume client,
  adresă, cadastral, CF, valoare) rămâne pe disc în clar.
- `web/routers/evaluare.py:183` — `backup.db` (SQLite ÎNTREG, toate dosarele) copiat în
  `%TEMP%/anevar_backup`, `keep=3` → până la 3 copii integrale ale bazei rămân în %TEMP%, necurățate.
- `web/routers/aml.py:37` — documentul AML (CNP, beneficiar real) scris în `%TEMP%` și **niciodată**
  șters; `FileResponse` fără cleanup.
*Contrast (pozitiv):* fluxul NOU pe foldere curăță corect — `curent.py:281-286` șterge .docx-ul temp
prin `BackgroundTask`, iar import/submis folosesc `tmpdir` unic + `shutil.rmtree` în `finally`
(`curent.py:119-129`, `306-313`). Asimetria e clară: **vechiul API și AML nu au igienă PII temp.**
*Recomandare:* adăugați `BackgroundTask` de `unlink` la cele 3 endpoint-uri (paritate cu `curent.py`);
pentru `backup.db` ștergeți copia temp după streaming.

**D3 — `backup-dosare.zip` și `backup.db` sunt necriptate, conțin TOATE PII. [High]**
`web/routers/curent.py:354-370` (`backup-dosare.zip` = `rglob` peste tot `date/dosare/` →
toate `dosar.json` cu PII + toate `raport-*.docx`) și `db/storage.py:82-95` / `evaluare.py:181-189`
(`backup.db`). Arhivele se descarcă în clar, fără parolă/criptare, și apoi tipic ajung pe email/USB
către bancă. Un singur fișier `.zip` = întreg portofoliul de clienți. Backup-ul la pornire
(`__main__.py:91-94`) scrie copia DB lângă executabil, tot în clar.
*Recomandare:* documentați ca risc rezidual acceptat de evaluator (responsabilitate organizatorică)
SAU adăugați criptare opțională la export (parolă zip / age). Avertizați explicit în UI că .zip-ul
conține date personale ale tuturor clienților.

**D4 — `dosar.json` și `_cache_antete.json` stochează PII în clar pe disc. [High]**
`dosare_fs.py:72-82` (`dosar.json`: `creator_nume`, `creator_legitimatie`, `identitate.nume_client`,
wizard întreg cu adresă/cadastral/CF) și `dosare_fs.py:310-323` (`_cache_antete.json` cache cu
`nume`+`identitate` → nume client). Toate în plaintext JSON. *Pozitiv (deja acoperit):*
`sterge()` (`dosare_fs.py:141-146`) scoate IMEDIAT din index + cache la ștergere (fix G1 / re-audit) —
bună igienă, evită PII tranzitoriu. Riscul rămâne: dacă stația e compromisă/ne-criptată la nivel
de disc, toate datele sunt lizibile.
*Recomandare:* recomandați criptarea discului (BitLocker) ca măsură art. 32 în ghidul de instalare;
documentați că aplicația se bazează pe securitatea OS, nu criptează la nivel de aplicație.

**D5 — `audit.txt` și erorile 422 pot ecou PII. [Medium]**
- `audit/raport_audit.py:24` + `evaluare.py:162` — `audit.txt` afișează adresa și cadastralul în
  CLAR (nu mascate), deci e un al doilea canal de disclosure pe lângă raport.
- Erorile 422 din FastAPI/Pydantic ecou input-ul: la `EvaluationInput` invalid, validatorul implicit
  Pydantic întoarce câmpul problematic și valoarea (`web/routers/evaluare.py:44`, `curent.py:172`).
  Mesajele 422 custom din cod (`assembler` „Date insuficiente: {e}", `aml.py:26`) sunt formulate
  prudent (nu ecou întreg payload-ul AML — `aml.py:26` zice doar eticheta, **pozitiv**), dar validarea
  automată Pydantic poate include valori de câmp în `detail`. Aceste erori pot ajunge în loguri/consolă.
*Recomandare:* verificați că handler-ul de excepții nu loghează body-ul; pentru AML, mențineți
mesajele generice (deja făcut). Mascați adresa în `audit.txt` dacă e destinat altcuiva decât băncii.

**D6 — Logul rotativ scrie legitimația ANEVAR a creatorului (PII). [Medium]**
`web/routers/curent.py:93` — `log.info("dosar creat uid=%s creator_leg=%s", uid, cont.get("legitimatie"))`.
Legitimația ANEVAR e un identificator personal al evaluatorului. În modul `.exe` logul se scrie
într-un fișier rotativ pe disc (`logging_setup.py:48-59`), deci PII-ul persistă. Restul logurilor
sunt curate (doar `uid`, metodă, nr. anexe — vezi `generator.py:846-849`, comentat explicit „fără PII").
*Recomandare:* eliminați `creator_leg` din log sau înlocuiți cu un hash scurt; nu există redactare PII
centralizată în `logging_setup.py`.

---

### U — Unawareness (subiectul știe că datele lui merg la un AI extern?)

**U1 — Consimțământul AI există ca MODEL, dar nu e impus tehnic în flux. [Medium]**
`gdpr/documente.py:55-80` generează un acord de prelucrare cu bife „☐ Sunt de acord cu folosirea
asistentului AI" / „☐ Solicit prelucrarea exclusiv offline". Excelent ca transparență (pozitiv).
DAR: în codul de flux (`assembler.py:254-255`, `config.py:50-56`) decizia de a folosi AI depinde
EXCLUSIV de prezența unei chei API (`narrative_client()`), **nu** de un flag de consimțământ al
clientului per-dosar. Nu există în `dosar.json` / wizard un câmp „client a consimțit la AI" care să
poată dezactiva trimiterea. Deci un evaluator poate trimite facts (pseudonimizate) la Anthropic fără
ca bifa de consimțământ să fi fost verificată tehnic.
*Recomandare:* legați alegerea offline/AI de un flag per-dosar (consimțământ), nu doar de cheia API;
sau documentați clar că respectarea bifei e procedurală (sarcina evaluatorului).

**U2 — Transparența în raport e bună, dar adresată băncii, nu subiectului. [Low — în mare acoperit]**
`report/generator.py:356-370` — raportul conține un paragraf explicit „Asistare software și
componentă AI (transparență)" care declară că se trimite doar text anonimizat, fără date personale.
*Pozitiv, deja acoperit.* Limită: raportul e citit de bancă/client-comanditar, nu neapărat de
persoana vizată (proprietarul/garantul). Modelul de consimțământ acoperă subiectul, dar vezi U1.

---

### N — Non-compliance (lipsă politici GDPR: retenție, temei legal, DPIA)

**N2 — Politica de retenție există ca text-model, dar NU e implementată tehnic (excepție: AML). [High]**
`gdpr/documente.py:42-44` declară retenție „de regulă 5 ani". Tehnic:
- Dosare (foldere + SQLite): **fără TTL / cleanup** — datele rămân indefinit până la ștergere manuală.
  Singura rotație e pe VERSIUNILE .docx (`dosare_fs.py:149,163-165` `PASTREAZA_VERSIUNI=10`) și pe
  backup-uri (`storage.py:93` `keep`), nu pe PII-ul dosarului.
- AML (`aml/store.py:35-47`): **calculează** `data_retentie` (+5 ani, art. 21) — pozitiv — DAR
  nimic nu citește/aplică acel câmp pentru ștergere automată; e doar metadată.
*Recomandare:* implementați un job de retenție (sau cel puțin un raport „dosare expirate") care
folosește `creat_la` / `data_retentie`; documentați politica efectivă vs. cea declarată.

**N3 — Niciun DPIA / screening art. 35 efectuat; doar menționat. [High]**
`docs/legal/00-evaluare-juridica-RO.md:404-411` recomandă explicit un „mini-DPIA / evaluare a
necesității DPIA (screening)" și îl marchează `[DE CONFIRMAT: avocat]`. CNP-ul (categorie cu
cerințe naționale suplimentare — `00-evaluare-juridica-RO.md:138`) e prelucrat în modulul AML.
Nu există în repo un DPIA finalizat sau un registru de prelucrări (art. 30).
*Recomandare:* consemnați screening-ul DPIA (chiar dacă concluzia e „DPIA complet neobligatoriu");
documentați temeiul legal per categorie (deja schițat în model: art. 6(1)(b/c/f), Legea 129/2019).

**N4 — Transfer internațional (SEE) neclarificat pentru gateway-ul AI. [Medium]**
`ai/narrative.py:249-274` (Anthropic) / `215-246` (Perplexity) — ambii furnizori procesează tipic
în SUA. `00-evaluare-juridica-RO.md:143` semnalează necesitatea clauzelor de transfer (SCC / decizie
de adecvare) și a unui DPA cu furnizorul. Chiar dacă se trimite doar text pseudonimizat, transferul
de date pseudonime poate intra sub GDPR (re-identificabile de operator).
*Recomandare:* DPA + clauze de transfer cu furnizorul AI, sau implicit offline pentru cazuri sensibile;
decizie juridică.

---

## 2. Data-retention + DSAR / erasure readiness

### Retenție — **LIPSEȘTE (tehnic)**
- Politică declarată: 5 ani (model `gdpr/documente.py:42`, AML `aml/constante.RETENTIE_ANI`).
- Implementare: **niciun TTL/cleanup pe PII**. Se rotesc doar versiunile .docx (max 10),
  backup-urile DB (`keep`) și lock-urile orfane. AML calculează `data_retentie` dar nu o aplică.
- Verdict: **GOL real** — datele persistă indefinit; ștergerea e 100% manuală.

### DSAR (art. 15 — „ce date aveți despre CNP X") — **LIPSEȘTE**
- Nu există nicio funcție de căutare după persoană. Singurele `cauta_*` din cod
  (`discovery/portal_search.py:100,126`) caută ANUNȚURI imobiliare, nu persoane.
- `db/storage.py:list()` listează toate dosarele (id, client_nume) — căutarea ar fi un scan
  manual liniar pe `client_nume`; nu acoperă AML (fișiere JSON separate) și nici PII din
  `raport-*.docx` / backup.zip / %TEMP%.
- Cross-dosar pentru aceeași persoană: imposibil automat (vezi L1 — fără cheie de subiect).
- Verdict: **GOL real** — un DSAR în 30 zile necesită căutare manuală în ≥4 locuri
  (SQLite, foldere, `aml_confidential/`, backup-uri); fezabil cu efort, dar neasistat de aplicație.

### Erasure (art. 17 — „ștergeți persoana X complet") — **PARȚIAL**
- `dosare_fs.sterge()` (`dosare_fs.py:141-146`): șterge folderul + scoate din index + cache.
  **Bun**, dar per-dosar (uuid), nu per-persoană.
- `db/storage.sterge(eid)` (`storage.py:119-121`): șterge rândul SQLite, per-id.
- **Ce RĂMÂNE după o ștergere „completă":**
  1. Backup-uri DB (`backups/`, `%TEMP%/anevar_backup`, lângă .exe) — conțin rândul șters.
  2. `backup-dosare.zip` deja generat/exportat — în afara controlului aplicației.
  3. Fișiere %TEMP% necurățate (`raport_{eid}.docx`, doc AML — vezi D2).
  4. **AML store** (`aml/store.py`): **NU are metodă de ștergere** — doar `salveaza/listeaza/citeste`.
     CNP-ul AML e neșterbil prin aplicație (și intenționat append-only pentru tipping-off, dar fără
     cale de erasure deloc).
  5. Loguri rotative (legitimație creator — D6).
  6. Jurnalul de audit/`audit.txt` deja exportat (N1).
- Verdict: **PARȚIAL** — ștergerea per-dosar e curată, dar nu există ștergere per-persoană, iar
  backup-urile + AML + %TEMP% lasă reziduuri. Erasure „complet" nu e atins fără pași manuali.

---

## 3. Zeroize-audit pe căile PII în memorie

> Tool: nu există un skill/CLI `zeroize-audit` rulat (deferred în mediu); analiza de mai jos e
> manuală, pe căile de buffer din cod. Aplicația e Python/CPython — **nu există zeroizare a memoriei
> posibilă în mod fiabil** (string-uri imutabile, GC, fără `mlock`); orice PII în RAM persistă până
> la GC și poate ajunge în swap/crash-dump. Acesta e o limită inerentă, nu un bug punctual.

**Z1 — Anonimizatorul reține maparea real↔token în memorie pe toată durata cererii. [info]**
`report/anonymizer.py:14-31` — `Anonymizer.real_to_token` (Pydantic `BaseModel`) ține valorile
REALE (nume, adresă, CF) cât timp obiectul trăiește; `unmask()` (`narrative.py:210`) le re-injectează.
Maparea e necesară funcțional (demascare locală) și nu se loghează/persistă (pozitiv). Reziduu în RAM
post-cerere până la GC — nezeroizabil în CPython. *Acceptabil; de documentat ca limită.*

**Z2 — Ce ajunge efectiv la Anthropic/Perplexity. [acoperit corect]**
`ai/narrative.py:194-209`: ordinea e `_facts(ctx)` → `anonymizer.mask()` → `filtreaza_pii_rezidual()`
→ trimitere. Deci identificatorii direcți din `meta` sunt mascați ÎNAINTE de trimitere, iar CNP/tel/email
reziduale sunt prinse de regex. **Pozitiv: CNP nu ajunge la AI** (dublă plasă: anonymizer + safety-net).
Limită: datele cantitative re-identificabile rămân (I1). Cheia API nu se loghează.

**Z3 — Buffere upload .docx/PDF în %TEMP%. [acoperit la fluxul nou; vezi D2 pt vechi]**
- Flux nou: `curent.py:119-129` (import) și `306-313` (submis) — `tmpdir` unic + `shutil.rmtree`
  în `finally`. Bufferul `raw` (bytes decodate) e o variabilă locală, GC după funcție (nezeroizabil).
  **Igienă disc bună.**
- Flux vechi + AML: NU șterg (vezi D2) — fișierele cu PII rămân pe disc, nu doar în RAM.
*Recomandare:* aliniați D2; pentru memorie, nu se poate zeroiza în Python — mențineți durata de viață
a bufferelor cât mai scurtă (deja făcut prin variabile locale).

---

## 4. Sinteză — top 5 riscuri privacy acționabile

1. **D2 — fișiere temp cu PII necurățate** (`web/routers/evaluare.py:108`, `:183`; `web/routers/aml.py:37`) — **High**.
   Raport complet + backup DB integral + doc AML cu CNP rămân în `%TEMP%`. Fix: `BackgroundTask` unlink
   (paritate cu `curent.py:281-286`).
2. **N2 — retenție declarată dar neimplementată** (`gdpr/documente.py:42`, `aml/store.py:42`) — **High**.
   Date PII persistă indefinit; `data_retentie` AML calculată dar neaplicată. Fix: job/raport de expirare.
3. **D3 — backup-uri necriptate cu tot portofoliul** (`web/routers/curent.py:354-370`, `db/storage.py:82-95`) — **High**.
   Un `.zip`/`.db` = toate datele clienților, în clar. Fix: criptare opțională la export + avertisment UI.
4. **N3 — niciun DPIA/screening art. 35 + erasure AML imposibil** (`docs/legal/00-evaluare-juridica-RO.md:404-411`,
   `aml/store.py` fără `sterge`) — **High**. Fix: screening DPIA consemnat + metodă de erasure controlată în AML.
5. **I1 — „anonimizat" = pseudonimizat, date cantitative re-identificabile** (`report/anonymizer.py:19-31`,
   `ai/narrative.py:114-155`) — **Medium**. Fix: documentați limita; mod offline pentru cazuri sensibile;
   extindeți safety-net (I2).

---

## 5. Ce este DEJA acoperit (pozitive de păstrat)

- **Anonimizare înainte de AI** cu dublă plasă: `anonymizer.mask()` pe identificatori direcți +
  regex safety-net pentru CNP/telefon/email (`ai/narrative.py:77-88,194-209`). CNP **nu** ajunge la AI.
- **Transparență AI în raport** (`report/generator.py:356-370`) — declară explicit text anonimizat,
  numere deterministe, fără date personale la AI.
- **Model de consimțământ + politică GDPR** generabile (`gdpr/documente.py`), cu opțiune offline și
  bife AI; disclaimere DRAFT corecte (operatorul = evaluatorul, nu aplicația).
- **Ștergere curată per-dosar** cu igienă imediată index+cache (`dosare_fs.py:141-146` — fix G1).
- **Separarea AML de dosar** (tipping-off art. 38) cu store dedicat + retenție 5 ani calculată
  (`aml/store.py`, `web/routers/aml.py:45`).
- **Igienă temp la fluxul nou** (`curent.py:119-129,281-286,306-313`) — tmpdir unic + rmtree + BackgroundTask.
- **Loguri în general fără PII** (`generator.py:846` comentat „fără PII"; excepția e D6).
- **Anti-path-traversal pe uid** (`dosare_fs._cale:33-45`) — protejează ștergerea de `rmtree` rogue.
- **Evaluare juridică RO existentă** (`docs/legal/00-evaluare-juridica-RO.md`) care semnalează deja
  transfer internațional, DPA, CNP, DPIA — cadru bun de completat.

---

## 6. Tools apelate

- Read / Grep / Glob / Bash (ls) — explorare READ-ONLY a `evaluare-anevar/src` și `docs/`.
- `zeroize-audit` (skill disponibil în mediu): **nu a fost rulat** — analiza buffer/memorie e manuală
  (secțiunea 3); CPython nu permite zeroizare fiabilă a memoriei, deci un scan automat ar fi confirmat
  doar limita inerentă.
- Niciun fișier `src/` modificat. Niciun commit. Doar acest document a fost creat.

**Cale document:** `C:\Users\adyse\anevar\evaluare-anevar\docs\LINDDUN-privacy-threat-model.md`
