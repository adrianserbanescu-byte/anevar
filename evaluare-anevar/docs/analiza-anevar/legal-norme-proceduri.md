# Analiză: Legal + Norme + Proceduri ONCPSB + Arhivare

> **Temă:** cerințele legale și procedurale (arhivare, retenție, registru de evidență, instrucțiuni
> ONPCSB/AML) pe care aplicația ANEVAR (evaluare casă+teren pentru garantare credit) trebuie să le
> suporte. **Documente analizate:**
> - `Procedura de arhivare a dosarelor de lucru aferente misiunilor de evaluare` (recomandare ANEVAR; cea mai NOUĂ piesă procedurală, referă SEV 106 ed. 2025)
> - `HCD 58/2023` — Instrucțiunile ANEVAR pentru aplicarea Legii 129/2019 (AML/CFT) + Anexele 1–2 (decizie desemnare, norme interne)
> - `Ordin ONPCSB nr. 37/2021` — Normele de aplicare a Legii 129/2019 (stub de link în corpus; conținut acoperit de HCD 58 + cod)
> - `Legea 129/2019` (SB/FT; stub de link în corpus — conținut acoperit de constantele AML din cod)
> - `pagina anevar.pdf` (scanat, citit vizual) — pagina ANEVAR „Evaluarea pentru impozitare / BIG-BIF": recipisă BIF la dosar, fereastra de reutilizare 5 ani PF / 3 ani PJ, GEV 500, SEV 2025
>
> **Referință de prioritate:** SEV 2025 (`standardele-de-evaluare-a-bunurilor-2025.md`) + analizele existente
> `docs/SEV-2025-*.md`. **Regula contradicții:** SEV 2025 are prioritate; în rest câștigă documentul mai NOU.
> **Stare cod:** ✅ implementat · 🟡 parțial · 🔴 lipsă · ⛔ greșit. **Severitate:** blocant / important / minor.

---

## 1. CE CONȚINE fiecare document + CE-I UTIL pentru app

### 1.1. Procedura de arhivare a dosarelor de lucru (recomandare ANEVAR) — piesa centrală
Definește cadrul de arhivare aliniat **SEV 106 (Documentația și raportarea, ed. 2025)** + **Legea 129/2019**
+ **GDPR (Reg. 679/2016)**. Aplicabilă tuturor evaluatorilor (PF/PJ), pentru orice lucrare. Conține:

- **§4–5 Tipuri de documente de arhivat / structura dosarului misiunii:** contract/comandă/numire,
  termenii de referință, acte de proprietate (CVC, certificat de moștenitor), extras CF, plan cadastral,
  certificat de urbanism, autorizații, procese-verbale, **documente de lucru** (calcule, tabele de
  comparabile, capturi de ecran ale anunțurilor cu trasabilitate, note de verificare a ofertelor,
  fotografii, fișe de inspecție, studii de piață), **raportul în formă preliminară ȘI finală**,
  **documentele KYC (Legea 129/2019)**, corespondența relevantă, **recipisa BIG/BIF**.
- **§6 Registrul de evidență a rapoartelor de evaluare** — registru OBLIGATORIU pentru monitorizarea
  extinsă ANEVAR, cu min. ~13 câmpuri: număr de identificare raport (recomandat pe coperta raportului),
  nr./data contractului, client + utilizatori desemnați, obiect + localizare, proprietar, clasificarea
  pe tip (PI/BM/Î/IF), scop, **onorariu**, **data evaluării + data raportului + data predării**,
  **numele persoanei care a făcut verificarea internă a calității**, **clasificarea clientului pe risc
  AML (scăzut/mediu/ridicat)**, observații; opțional: data facturii, gradul de încasare.
- **§7 Modalități de arhivare:** fizic / electronic (scanat, **back-up periodic**) / mixt.
- **§8 Termene de păstrare:** **minimum 5 ani** (Legea 129/2019: 5 ani de la încetarea relației/finalizarea
  lucrării; SEV 106: „perioadă rezonabilă"; recomandare ANEVAR: min. 5 ani pentru TOATE documentele).
- **§10 Protecția datelor:** parole schimbate periodic, **criptare**, back-up; pentru fizic — spații încuiate.
- **§11 Organizarea arhivei:** dosare numerotate/indexate, denumire = min. **nr. lucrare + an**, directoare
  structurate (ex. `2025_NrLucrare_NumeClient`).
- **§12 Control și audit:** documentele trebuie ușor accesibile/verificabile pentru audit ANEVAR/autorități.

**Util pentru app:** este harta directă a ceea ce un dosar electronic trebuie să conțină, cum se numerotează,
cât se păstrează și cum se exportă pentru o inspecție ANEVAR. Mapează aproape 1:1 pe `dosare_fs.py`
(folder per dosar + versiuni .docx) și pe storage-ul AML.

### 1.2. HCD 58/2023 — Instrucțiunile AML ale ANEVAR (+ Anexele 1–2)
Încadrează evaluatorii ca **entități raportoare** (Legea art. 5(1)(e)). Obligații: desemnarea persoanei
responsabile (DOAR PJ — PFA/PF independent sunt scutiți), evaluarea riscurilor SB/FT, **norme interne +
proceduri de control**, **raportare la ONPCSB** (RTN ≥ 10.000 €, RTS), **instruire anuală**, **păstrarea
documentelor 5 ani** (art. 8), **măsuri KYC** (standard/simplificate/suplimentare), **interzicerea divulgării
(tipping-off, Legea art. 38)**. Anexa 1 = model decizie de desemnare; Anexa 2 = norme interne (KYC, raportare,
păstrare evidențe min. 5 ani, protecția personalului, instruire). Termene operaționale: RTN +3 zile lucrătoare,
RTS → suspendare 24h.

**Util:** definește exact ce module AML trebuie să producă (decizie desemnare, norme interne, fișă KYC,
RTN/RTS) și regula critică: **documentele AML/RTS se păstrează SEPARAT de dosarul clientului** (Anexa 2 art.
14(3)) — altfel risc de divulgare accidentală.

### 1.3. Ordin ONPCSB 37/2021 + Legea 129/2019 (în corpus = stub-uri de link)
Fișierele `ordin 37.md` și `LEGE nr.md` din corpus sunt **doar antetul + linkuri** către legislatie.just.ro
(conținutul integral nu e în text). Substanța lor (praguri, termene, retenție, KYC, articole) este **deja
internalizată** în `aml/constante.py` cu citarea articolului-sursă și în HCD 58 (care le rezumă). Nu adaugă
cerințe noi față de ce e deja extras.

### 1.4. pagina anevar.pdf (scanat) — Evaluarea pentru impozitare / BIG-BIF
Pagina web ANEVAR „Baze de date BIG și BIF". Relevant procedural:
- **recipisa BIF** care dovedește înregistrarea datelor din raport **se păstrează la dosarul evaluării**;
- punctul de vedere ANEVAR: evaluările de impozitare pot fi reutilizate **în interiorul a 5 ani (PF) / 3 ani
  (PJ)** de la precedenta evaluare;
- distincția **data evaluării vs. data raportului** la impozitare;
- confirmă **SEV 2025 (ed. adoptată prin Hotărârea nr. 2/2025)** și GEV 500 (impozitare) ca fiind în vigoare;
- recomandările privind **studiile de piață (art. 111 Cod fiscal)** — studiile NU pot fi folosite ca sursă/valoare
  de referință în rapoartele de evaluare (limită de utilizare).

**Util:** confirmă obligația de a stoca recipisa BIG/BIF la dosar (BIG pentru garantare, BIF pentru impozitare)
și fereastra de reutilizare — relevant dacă app-ul va atinge și fluxul de impozitare.

---

## 2. RELEVANȚA vs. SEV 2025 + CONTRADICȚII rezolvate

| Aspect | SEV 2025 spune | Documentele procedurale spun | Cine câștigă + de ce |
|---|---|---|---|
| **Termen de păstrare** | SEV 106: „perioadă rezonabilă", neprecizat numeric | Legea 129/2019 + recomandarea ANEVAR: **min. 5 ani** | **5 ani câștigă.** Nu e o contradicție reală: procedura ANEVAR concretizează „rezonabil" la pragul legal AML. App: retenție ≥ 5 ani. |
| **Conținutul dosarului** | SEV 106 cere documentația care susține raționamentele + trasabilitate | Procedura §4–5 detaliază lista exactă (acte, CF, comparabile cu print-screen, KYC, recipisă BIG) | **Convergente.** Procedura = operaționalizarea SEV 106; ambele se aplică cumulativ. |
| **Registrul de evidență a rapoartelor** | Nu e cerut explicit de SEV (e cerință de monitorizare ANEVAR) | Procedura §6: **obligatoriu**, ~13 câmpuri | **Procedura câștigă** (SEV tace) — e o cerință profesională ANEVAR, nu un standard de evaluare. |
| **Stocarea RTS/AML** | SEV nu reglementează | HCD 58 Anexa 2 art. 14(3): RTS **NU** în dosarul clientului (tipping-off) | **HCD 58 câștigă** (domeniu AML, în afara SEV). Cod-ul deja respectă (store AML separat). |
| **Recipisa BIG la garantare** | GEV 520 §83–84 (SEV 2025): recipisa BIG = anexă obligatorie a raportului | Procedura §4 + pagina ANEVAR: recipisa BIG/BIF la dosar | **Convergente, prioritate SEV/GEV 520.** Vezi gap G5 din `SEV-2025-gap-implementare.md`. |
| **Protecția datelor** | SEV nu reglementează GDPR | Procedura §10 + GDPR: criptare, parole, back-up, acces restricționat | **GDPR/procedura câștigă** (SEV tace). |

**Concluzie:** nu există contradicție de fond cu SEV 2025. Documentele procedurale **completează** SEV 2025 pe
zonele pe care standardul de evaluare nu le acoperă (arhivare, registru, AML, GDPR), iar unde se ating (conținut
dosar, recipisă BIG) sunt convergente. Prioritatea SEV 2025 nu e contestată de niciun document.

---

## 3. GAP-URI de implementare (ce trebuie app-ul să facă/adauge)

**Ce e deja implementat (verificat în cod):**
- ✅ **Dosar = folder per lucrare** cu versiuni .docx, **retenție 10 versiuni**, hash SHA256 de integritate
  (tamper-evidence ADR-003), identitate blocată după asumare — `dosare_fs.py` (`adauga_versiune_docx`,
  `verifica_integritate`, `_inregistreaza_versiune`).
- ✅ **Store AML SEPARAT** de dosar, append-only, **dată de retenție +5 ani** calculată (`data_retentie`),
  permisiuni 0o700/0o600 — `aml/store.py`, `RETENTIE_ANI=5`/`RETENTIE_PRELUNGIRE_MAX_ANI=5` în `constante.py`.
- ✅ **Generatoare AML conforme HCD 58:** decizie desemnare (doar PJ), norme interne (7 capitole = Norme art.
  8(1) a–g), fișă KYC (PF/PJ + beneficiar real + PEP), draft RTN/RTS cu avertisment **tipping-off** — `aml/documente.py`.
- ✅ **Termene AML:** RTN +3 zile lucrătoare, suspendare RTS +24h prorogat, anti-fragmentare 15.000 € — `aml/raportare.py`.
- ✅ **Backup arhivă:** endpoint `/api/backup-dosare.zip` arhivează toate dosarele într-un .zip — `web/routers/curent.py:363`.
- ✅ **GDPR:** generatoare politică de prelucrare + acord client, cu retenție „5 ani" și operator = evaluatorul — `gdpr/documente.py`.
- ✅ **Recipisa BIG** tratată în raport (text + checklist, condiționat creditor/ANAF) — `report/generator.py:555–608`.

**Gap-uri (numerotate, cu severitate):**

### G-LNP-1 🔴 Registrul de evidență a rapoartelor de evaluare — LIPSEȘTE ca livrabil — **important**
Procedura §6 cere un registru OBLIGATORIU (pentru monitorizarea extinsă ANEVAR) cu ~13 câmpuri. În cod NU
există: storage-ul (`db/storage.py`) reține doar `client_nume, valoare_finala, nume, creat_la`; nu există
**număr de identificare a raportului**, **onorariu**, **data predării**, **numele verificatorului intern**,
**clasificarea clientului pe risc AML**, **scop/utilizator desemnat** ca rând de registru, nici **export**
(singurul CSV e pentru feedback — `pagini.py:148`). „Registru de evaluare" din UI e doar text de antet.
**Acțiune:** tabel `registru_rapoarte` + pagină + **export CSV/XLSX** cu cele ~13 câmpuri din §6. Multe câmpuri
există deja parțial (`meta.py`: client, adresă, cadastral, data_evaluarii, data_raportului, scop, utilizator_desemnat,
evaluator_legitimatie) — lipsesc: nr. identificare raport, onorariu, data predării, verificator intern, risc AML client.

### G-LNP-2 🔴 Câmp „data retenției" / „a se păstra până la" pe dosarul de evaluare — **important**
AML are `data_retentie` (+5 ani), dar **dosarul de evaluare** (`dosare_fs.py`/`db/storage.py`) NU are dată de
retenție. Procedura §8 cere min. 5 ani pentru TOATE documentele misiunii, nu doar pentru cele AML. Fără un câmp
de retenție pe dosar, app-ul nu poate semnala „dosar eligibil pentru ștergere / sub termen de păstrare".
**Acțiune:** câmp `data_retentie` derivat din `data_raportului + 5 ani` în `dosar.json`; UI: nu permite ștergerea
fără avertisment „încă în termenul de păstrare de 5 ani".

### G-LNP-3 🔴 Câmp „verificare internă a calității" (cine + data) — **important**
Atât SEV 100 (declarația de verificare a calității, deja în raport — `generator.py:261`), cât și Procedura §6
(numele verificatorului intern în registru) presupun consemnarea verificării interne **anterioare predării**.
În model NU există câmp pentru **cine** a verificat raportul intern și **când**. La PJ acesta e și o cerință
de control intern AML (HCD 58 art. 5).
**Acțiune:** câmpuri `verificator_intern_nume` + `data_verificare_interna` în `meta.py`/wizard; intră în registru.

### G-LNP-4 🟡 Numerotarea/indexarea dosarului după convenția ANEVAR (nr. lucrare + an) — **minor/important**
Procedura §11 cere denumire = min. **nr. lucrare + an** și directoare `2025_NrLucrare_NumeClient`. App-ul
folosește UUID-uri ca nume de folder (`dosare_fs._cale`) + nume liber (`nume_dosar`). Lipsește un **număr de
lucrare secvențial pe an** (ex. `2026/0042`) care să fie și numărul de identificare al raportului (G-LNP-1) și
să apară pe coperta raportului.
**Acțiune:** alocare atomică a unui număr de lucrare `AAAA/NNNN` (pattern-ul O_EXCL există deja la `aml/store._next_id`);
afișat pe raport + în registru.

### G-LNP-5 🟡 Câmp dedicat „recipisă BIG/BIF" în setul de documente al dosarului — **important**
GEV 520 §83–84 (SEV 2025) + Procedura §4 + pagina ANEVAR cer recipisa BIG (garantare) / BIF (impozitare) ca
**document anexat la dosar**. În cod recipisa apare ca **text în raport**, dar NU ca un câmp/atașament urmărit
în `models/meta.py` sau în structura dosarului (nu există checklist „recipisă atașată: da/nu"). Coincide cu gap-ul
G5 din `docs/SEV-2025-gap-implementare.md`.
**Acțiune:** câmp `recipisa_big` (atașament + dată înregistrare) în dosar + punct de checklist obligatoriu.

### G-LNP-6 🟡 Export/„pachet de inspecție" pentru audit ANEVAR — **important**
Procedura §12 cere ca dosarul să fie ușor accesibil/verificabil la audit ANEVAR/autorități. Există
`/api/backup-dosare.zip` (TOATE dosarele), dar NU un **export per-dosar** (un singur dosar + raport integritate
+ registru) ca pachet pentru un inspector. La un control nu vrei să exporți întreaga arhivă (PII a tuturor
clienților) ci un singur dosar.
**Acțiune:** endpoint `/api/dosar/{uid}/export.zip` (dosar.json + .docx + raport `verifica_integritate`).

### G-LNP-7 🟡 Criptare a arhivei electronice — **important (depinde de mediul de deploy)**
Procedura §10 cere **criptare** + parole schimbate periodic pentru arhiva electronică; GDPR draft din cod
menționează „bază SQLite, backup periodic, acces restricționat" dar **fără criptare la repaus**. Datele
(dosare + SQLite + AML) sunt în clar pe disc. Permisiunile 0o700/0o600 ajută pe Linux/macOS dar sunt **no-op pe
Windows** (mediul-țintă curent).
**Acțiune:** documentat ca cerință de deploy (BitLocker/FileVault) + opțional criptare la repaus a folderului
`date/`; menționat explicit în politica GDPR generată.

### G-LNP-8 🟡 Clasificarea clientului pe risc AML legată de dosarul de evaluare — **minor/important**
Procedura §6 cere ca registrul să conțină **clasificarea clientului pe risc** (scăzut/mediu/ridicat). Motorul
AML calculează deja categoria de risc (`aml/risc.py`, `EvaluareRisc.categorie`), dar aceasta NU e legată/persistată
pe dosarul de evaluare corespunzător (sunt module separate). Registrul (G-LNP-1) are nevoie de această legătură.
**Acțiune:** persistă categoria de risc AML ca câmp pe dosar (referință între KYC și dosar), populat în registru.

### G-LNP-9 🟡 Reutilizarea evaluării (fereastra 5 ani PF / 3 ani PJ) — **minor**
Pagina ANEVAR (impozitare) menționează fereastra de reutilizare (5 ani PF / 3 ani PJ). Pentru garantare,
GEV 520 §7 cere re-desemnarea utilizatorului la reutilizarea unui raport (= gap G6 din `SEV-2025-gap-implementare.md`).
App-ul nu urmărește data evaluării anterioare / eligibilitatea de reutilizare.
**Acțiune:** la prioritate joasă (relevant mai ales pentru fluxul de impozitare, nu pentru garantare); minim — o
notă în termeni + checklist la reutilizare.

### G-LNP-10 🟡 Instruirea anuală + revizuirea anuală a normelor (urmă/reminder) — **minor**
HCD 58 art. 10 + Anexa 2 art. 17 cer **instruire anuală** a personalului + **revizuirea normelor cel puțin o
dată pe an** (art. 5(3)). App-ul generează documentele dar nu reține o **dată de revizuire/instruire** și nu
reamintește. Relevant doar pentru PJ cu angajați.
**Acțiune:** câmp „data ultimei instruiri/revizuiri" + reminder (la +12 luni); prioritate joasă pentru PFA.

---

## 4. Recomandare de prioritizare

1. **G-LNP-1 (registru de evidență a rapoartelor)** + **G-LNP-3 (verificator intern)** + **G-LNP-4 (nr. lucrare/an)**
   — sunt cuplate: registrul are nevoie de numărul de lucrare și de verificatorul intern. Cea mai mare lipsă
   procedurală; **obligatoriu pentru monitorizarea extinsă ANEVAR**.
2. **G-LNP-2 (retenție pe dosar 5 ani)** + **G-LNP-6 (export per-dosar pentru audit)** — pregătesc app-ul pentru
   un control ANEVAR fără a expune toată arhiva.
3. **G-LNP-5 (recipisă BIG)** — convergent cu gap-ul SEV 2025 deja documentat (G5); de făcut împreună.
4. **G-LNP-7 (criptare)** + **G-LNP-8 (risc AML pe dosar)** — întăresc conformitatea GDPR/AML.
5. **G-LNP-9, G-LNP-10** — ulterior (nișă: impozitare / PJ cu angajați).
