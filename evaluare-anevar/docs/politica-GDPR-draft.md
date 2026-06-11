# Politica de protecție a datelor (GDPR) — DRAFT pentru Adi / jurist

> **Status: DRAFT redactat de E (sesiune research) la dispatch-ul lui A, 2026-06-11.**
> Scop: document de **decizie** pentru Adi + jurist — transformă golurile constatate în
> [LINDDUN-privacy-threat-model.md](LINDDUN-privacy-threat-model.md) (16 findings) în politici
> concrete de adoptat. NU e text juridic final; fiecare §marcat **[DECIZIE]** cere validare juridică.
> Context produs: aplicație LOCALĂ (un .exe per evaluator, date pe mașina evaluatorului) — operatorul
> de date (în sens GDPR) este **evaluatorul/firma sa**, nu furnizorul aplicației. Aplicația trebuie să-i
> DEA evaluatorului uneltele ca să-și poată îndeplini obligațiile.

## 1. Roluri și temeiuri legale

| Element | Propunere | De validat |
|---|---|---|
| Operator | Evaluatorul autorizat / firma de evaluare (deține datele local) | [DECIZIE] confirmare jurist |
| Persoană împuternicită | Anthropic (doar pentru naratorul AI, opțional; date pseudonimizate) | [DECIZIE] necesită DPA? vezi §6 |
| Temei legal — dosar de evaluare | Art. 6(1)(b) executarea contractului (clientul cere evaluarea) + art. 6(1)(c) obligație legală (SEV/ANEVAR, GEV 520 — raport pentru creditor) | [DECIZIE] |
| Temei legal — modul AML | Art. 6(1)(c) obligație legală: **Legea 129/2019, art. 21** — păstrare 5 ani a documentelor CDD/rapoartelor (RTS/RTN) | confirmat de lege; jurist validează formularea |
| Date prelucrate | Identificare client/proprietar (nume, CNP, adresă, acte), date imobil (CF, cadastral), date financiare (valoare, credit), documente încărcate (.docx/PDF) | — |

## 2. Politica de retenție [DECIZIE-CHEIE — azi NU există TTL tehnic]

Constatare LINDDUN N2: retenția AML e *calculată* (`aml/store.py:42`, 5 ani) dar **nimic nu șterge la
expirare**; dosarele de evaluare nu au nicio durată definită. Propunere de matrice:

| Categorie | Durată propusă | Justificare | Mecanism tehnic (de implementat post-RC) |
|---|---|---|---|
| Dosar de evaluare (PII + raport) | **10 ani** de la predarea raportului | termenul de arhivare uzual al rapoartelor de evaluare (răspundere profesională; monitorizare ANEVAR) — [DECIZIE] jurist confirmă durata exactă | job de cleanup la pornire: dosare cu `data_raportului` > N ani → propune arhivare/ștergere (cu confirmarea evaluatorului, nu silențios) |
| Înregistrări AML (RTS/RTN/CDD) | **5 ani** (Legea 129/2019 art. 21), prelungibil la cererea ONPCSB | obligație legală; NU se șterg mai devreme chiar la cerere de erasure (art. 17(3)(b) GDPR — derogare obligație legală) | cleanup la `data_retentie` deja stocată; **de adăugat metodă de ștergere în `aml/store.py`** (azi nu există) |
| Backup-uri (`backup-dosare.zip`, `backup.db`) | aceeași durată ca sursa; backup-urile vechi se rotesc (`keep=3` există la .db) | un backup nu prelungește viața datelor | documentare + rotație și pentru .zip |
| Fișiere temporare (%TEMP%) | **0 — ștergere imediat după folosire** | LINDDUN D2 (High): `evaluare.py:108/183`, `aml.py:37` lasă PII în %TEMP% | A a preluat fix-ul pre-RC (curățare după folosire) |
| Loguri aplicație | **90 zile** [DECIZIE] | suficient pt debugging; D6: legitimația în log → de scos sau de inclus în rotație scurtă | rotația există; de verificat durata efectivă |
| Jurnal de audit hash-chain (`audit.txt`) | pe durata dosarului (e parte din dosar) | integritatea raportului = interes legitim puternic; vezi §4 tensiunea cu erasure | — |

## 3. DSAR — dreptul de acces (art. 15) [azi: IMPOSIBIL automat]

Constatare: nu există căutare după persoană; un DSAR „ce date aveți despre CNP X" cere azi scan manual
în ≥4 locuri (SQLite, foldere dosare, AML store, backup-uri).

**Politică propusă:** evaluatorul răspunde la DSAR în **30 de zile** (art. 12(3)); aplicația trebuie să
ofere (post-RC, feature mic): **căutare cross-dosar după nume/CNP** care listează: dosarele unde apare
persoana + rolul (client/proprietar/beneficiar) + documentele încărcate + dacă există înregistrări AML
*(atenție: existența unui RTS NU se divulgă persoanei — interdicția de tipping-off, Legea 129/2019
art. 25; răspunsul DSAR pe zona AML se limitează la datele CDD, NU la raportări — [DECIZIE] jurist
formulează excepția corect)*.

## 4. Erasure — dreptul la ștergere (art. 17) [azi: PARȚIAL]

Constatare: ștergerea per-dosar e curată (`dosare_fs.sterge()`), dar nu există ștergere **per-persoană**;
rămân: backup-uri, %TEMP%, AML (fără metodă de ștergere), loguri, `audit.txt` exportat.

**Politică propusă:**
1. Cererea de ștergere se evaluează per temei: datele sub obligație legală (AML 5 ani; raport predat
   creditorului sub GEV 520) **NU se șterg** — art. 17(3)(b); se informează persoana despre derogare.
2. Pentru ce SE poate șterge: procedura = ștergere dosar(e) + regenerare backup (backup-ul vechi se
   rotește/șterge la următorul ciclu — de documentat că ștergerea devine efectivă în backup în ≤N zile).
3. Jurnalul hash-chain: poziția propusă = jurnalul e parte a raportului (obligație profesională /
   interes legitim) — nu se sparge lanțul; [DECIZIE] jurist confirmă poziția (LINDDUN N1).
4. Post-RC: metodă de ștergere în `aml/store.py` (pentru expirarea retenției, nu pentru cereri).

## 5. DPIA / evaluarea de impact (art. 35) [azi: INEXISTENT]

Prelucrare la scară: CNP + date financiare + profilare implicită (evaluare pt creditare) → **screening
DPIA recomandat**. Propunere: LINDDUN-ul existent (16 findings) = baza tehnică a DPIA-ului; juristul
adaugă partea de necesitate/proporționalitate. Livrabil separat, pre-lansare (nu pre-RC). [DECIZIE]

## 6. Transferul către AI (Anthropic) — transparență și temei

Stare BUNĂ (verificat în cod): CNP/tel/email sunt înlocuite cu `[REDACTAT-CNP]` etc. înainte de
trimitere (`narrative.py:78` + safety-net `:197`); raportul declară textul AI (`[AI] generat…`).
Rămas (LINDDUN U1/I1):
- **[DECIZIE]** consimțământ/informare: clientul e informat în contract/angajament că fragmente
  pseudonimizate se trimit unui furnizor AI (Anthropic, posibil SEE→SUA — DPA + SCC-urile Anthropic
  acoperă; jurist verifică). Propunere: clauză standard în termenii de referință + opțiunea existentă
  „fără AI" rămâne default-ul fără cheie API.
- I1 (re-identificare din cantitative): risc acceptat-documentat sau generalizare (ex. localitate →
  județ) în promptul AI — [DECIZIE], cost/beneficiu pe calitatea narativului.

## 7. Măsuri tehnice parcate (decizie pre-lansare, nu pre-RC)
- Criptarea backup-urilor la repaus (`backup-dosare.zip`/`backup.db` — LINDDUN D3, High) sau măcar
  avertisment în UI la descărcare („conține date personale, păstrați securizat").
- TTL/cleanup automat per §2.
- Căutare cross-dosar pt DSAR per §3.

## 8. Ce e DEJA acoperit (nu necesită decizie)
Pseudonimizare înainte de AI + plasă de siguranță; transparență AI în raport; ștergere curată per-dosar;
separarea AML de dosar (tipping-off); igiena temp pe fluxul nou; disclaimer profesional (CJEU SCHUFA,
human-in-the-loop — GDPR art. 22 acoperit); 0 chei API în surse.

---
*Întrebări deschise pentru jurist, concentrat: (a) durata exactă de arhivare a dosarului de evaluare
(10 ani?); (b) formularea derogării art. 17(3)(b) pe AML + tipping-off în răspunsul DSAR; (c) poziția pe
jurnalul hash-chain vs erasure; (d) clauza de informare AI în termenii de referință; (e) dacă DPA-ul
standard Anthropic + SCC e suficient pentru transferul SEE→SUA.*
