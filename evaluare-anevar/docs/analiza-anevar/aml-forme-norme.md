# AML — formulare + norme interne + Legea spălării banilor + beneficiari reali

> **Temă:** analiza documentelor-model AML (formular KYC, decizie persoană desemnată, norme interne,
> informații beneficiari reali) + Legea 129/2019, raportat la ce **colectează și generează** modulul AML
> al aplicației (`src/evaluare/aml/`).
> **Referință de prioritate:** SEV 2025 (câștigă orice contradicție). În rest, documentul mai NOU câștigă.
> **Concluzie scurtă:** modulul AML al app-ului este deja **substanțial mai bogat** decât cele 4 documente-model
> (implementează risc ponderat, screening, RTN/RTS, anti-fragmentare, termene în zile lucrătoare, tipping-off).
> Gap-ul real NU e logica de backend, ci **(a) câmpuri din formularul standardizat KYC necolectate în UI**,
> **(b) consultarea Registrului Beneficiarilor Reali (RBR) — câmp există în model, lipsește din UI**, și
> **(c) câteva câmpuri de identificare/risc din formularul-model care nu au corespondent în fluxul web.**
>
> Stare: ✅ implementat · 🟡 parțial / model-da-UI-nu · 🔴 lipsă · ⛔ greșit
> Severitate: **B** = blocant conformitate · **M** = mediu · **m** = minor

---

## Sursele analizate (și ce sunt de fapt)

| Document | Ce este | Dată / temei |
|---|---|---|
| `formular-cunoastere-clientela-risc-sbft-actualizat.txt` | **Formular standardizat KYC + evaluare risc** (10 secțiuni: date client, scop, factori de risc client/tranzacție/produs/geografic, World-Check, nivel risc, măsuri de atenuare, concluzii) | model ANEVAR, Legea 129/2019 |
| `model-decizie-persoana-desemnata.txt` | **Decizie de desemnare** a persoanei responsabile (art. 23) — DOAR pentru societăți | art. 23 Legea 129/2019 |
| `model-norme-interne.txt` | **Norme și proceduri interne** (17 articole: MDC standard/simplificate/suplimentare, PEP, raportare RTN/RTS, păstrare evidențe, protecția personalului, instruire) | Ordinul ONPCSB 37/2021, art. 8 |
| `informatii-privind-beneficiarii-reali.txt` | Pagina ONRC — **procedura de acces la Registrul Beneficiarilor Reali (RBR)** (formular 8a, semnătură electronică, acces gratuit pentru entități raportoare la aplicarea MDC) | ONRC / Ord. MJ 7323/C/2020 |
| `spalare bani 2019.pdf` (scanat) | **NU e textul legii** — e pagina ANEVAR „Ghiduri și documente utile în aplicarea Legii 129/2019" (HCD 58/2023 + **HCD 62/2025**), listează toate modelele + explică **accesul gratuit la RBR** pentru evaluatori | ANEVAR, 2025 |

> Notă importantă: PDF-ul „spalare bani 2019" este o **pagină-index** (2 pagini), nu legea integrală.
> Temeiul legal detaliat e deja codat în `aml/constante.py` (fiecare prag cu articolul-sursă) și verificat
> în audituri anterioare. Articolele citate aici provin din cod + documentele-model, nu din legea integrală.

---

## 1. CE CONȚIN documentele + CE-I UTIL pentru app

### 1.1 Formularul standardizat KYC (cel mai relevant pentru UI)
Cele 10 secțiuni ale formularului-model, **maparea pe app**:

| Secțiune formular | Câmp în app | Stare |
|---|---|---|
| 1. Date generale client (PF/PJ, rezidență, PEP, beneficiar real + modalitate identificare) | `ClientPF` / `ClientPJ`, `StatutPEP`, `BeneficiarReal` (model **complet**) | 🟡 model bogat, UI minimal |
| 2. Scopul evaluării (10 opțiuni: garantare împrumuturi, raportare financiară, impozitare, expropriere, insolvență…) | — **NU există** câmp „scop AML" în `DosarAML` | 🔴 lipsă |
| 3. Factori risc client (structură off-shore, jurisdicții FATF, activitate neobișnuită, frecvență) | `Semnale.tara_risc_inalt`, parțial | 🟡 parțial |
| 4. Factori risc tranzacție (valoare disproporționată, presiune finalizare, doc. incomplete, scop vag) | `SemnaleIndicatori` (presiune, scop nedefinit) + `Semnale.tranzactie_complexa` | ✅ acoperit (alt vocabular) |
| 5. Factori risc produs/serviciu (complexitate, valoare mare activ) | `Semnale.tranzactie_complexa` | 🟡 parțial |
| 6. Factori geografici (listă țări risc FATF/UE/ONU) | `liste.este_tara_risc`, `tari_risc_inalt`/`tari_necooperante` | ✅ |
| 7. Verificări World-Check / baze publice (client + beneficiar real) | `liste.screening` (sancțiuni + PEP, toleranță diacritice) | ✅ (cu disclaimer „nu e listă live") |
| 8. Evaluarea nivelului de risc (scăzut/mediu/ridicat) | `evalueaza_risc` → `redus`/`standard`/`sporit` + scor ponderat | ✅ (mai sofisticat decât formularul) |
| 9. Măsuri de atenuare (doc. suplimentare, verificări, consultare responsabil, raportare ONPCSB) | `nivel_masuri` (simplificate/standard/suplimentare) | 🟡 mapat pe nivel, nu pe checklist de măsuri |
| 10. Concluzii și asumare (semnătură evaluator, data) | fișa KYC `.docx` are linie de semnătură | ✅ |

**Util:** formularul confirmă că arhitectura app-ului (4 factori de risc ponderați + indicatori + screening) **acoperă și depășește** formularul-model. Câmpurile lipsă sunt punctuale (scop AML, modalitate identificare beneficiar real).

### 1.2 Decizia persoanei desemnate
Util: confirmă regula codată în `incadrare.necesita_persoana_desemnata` — **PFA/persoană fizică NU are obligația** (Norme art. 7), societatea da. App-ul generează `genereaza_decizie_desemnare` și **refuză** generarea pentru PFA (ridică `ValueError` → 400). ✅ corect implementat.

### 1.3 Normele interne
Util: cele 17 articole ale modelului ↔ cele 7 capitole din `documente._CAPITOLE_NORME` (Norme art. 8(1) a-g). App-ul generează norme-cadru cu temei pe fiecare capitol. ✅ acoperit ca structură. Modelul ANEVAR e mai detaliat la **MDC pe categorii de PJ străine / fiducii** (art. 4(3),(4) din model) — app-ul are câmpurile (`traducere_legalizata`, `acte_constituire`) dar nu generează text dedicat fiduciei.

### 1.4 Beneficiari reali / RBR
Util: documentul ONRC + pagina ANEVAR stabilesc că evaluatorul autorizat, ca **entitate raportoare**, are **acces GRATUIT** la RBR la aplicarea MDC. App-ul are deja câmpul `BeneficiarReal.consultat_registru_central` și `neconcordanta_registru` (obligația de a raporta neconcordanțe la ONRC) — **dar nu le colectează în UI și nu le pune în fișa KYC**.

---

## 2. RELEVANȚĂ vs SEV 2025 + contradicții rezolvate

- **Fără contradicții cu SEV 2025.** AML (Legea 129/2019 + Norme ONPCSB 37/2021 + HCD 58/2023, HCD 62/2025) și SEV 2025 sunt **planuri normative complementare**: SEV reglementează *conținutul evaluării*; AML reglementează *cunoașterea clientului și raportarea*. Nu se suprapun pe aceleași reguli, deci regula „SEV câștigă" nu se activează.
- **Punct de contact:** scopul „garantarea împrumuturilor" apare în AMBELE — formularul KYC §2 și GEV 520. App-ul tratează scopul de evaluare în fluxul SEV (`profil.py`), dar **nu îl propagă în dosarul AML** (vezi G2). Aici nu e contradicție, e o **legătură nefăcută** între cele două module.
- **Document mai nou câștigă:** pagina ANEVAR (HCD 62/2025) este mai nouă decât modelele individuale; ea **confirmă** (nu contrazice) structura: aceleași modele (formular, decizie, norme) + accesul gratuit RBR. Nimic de revizuit în cod din cauza datei.
- **Indicatori de suspiciune:** modelul de norme (art. 10) descrie suspiciunea generic; app-ul folosește cei **10 indicatori concreți din HCD 58/2023 art. 6(10)** (`indicatori.INDICATORI`) — mai specific și mai nou → app-ul e **corect** că preferă HCD 58.

---

## 3. GAP-URI de implementare

### G1 🟡 RBR (Registrul Beneficiarilor Reali) — câmp în model, absent din UI **[B]**
**Cerință:** evaluatorul, ca entitate raportoare, **trebuie** să consulte RBR la identificarea beneficiarului real și **să raporteze neconcordanțele** la ONRC (Legea art. 19(5); pagina ANEVAR + ONRC). Accesul e gratuit.
**Cod:** `models.BeneficiarReal.consultat_registru_central` și `.neconcordanta_registru` **există** dar:
(a) UI-ul (`aml.html`) nu le bifează niciodată; (b) fișa KYC (`documente.genereaza_fisa_kyc`) **nu le afișează**; (c) `aml.html` colectează **un singur** beneficiar real fără procent/tip control/CNP.
**Severitate B** — fără dovada consultării RBR în fișă, KYC-ul pentru PJ e formal incomplet.
**Acțiune:** în `aml.html` — secțiune „beneficiari reali" repetabilă (nume, CNP, **procent >25%**, tip control, PEP, **bifă „consultat RBR"** + „neconcordanță RBR"); în `genereaza_fisa_kyc` afișează `consultat_registru_central`/`neconcordanta_registru` pe fiecare BR + link informativ către `myportal.onrc.ro`.

### G2 🔴 Scopul evaluării (AML §2) nu e colectat / propagat **[M]**
**Cerință:** formular KYC §2 — scopul declarat (garantare împrumut, impozitare, expropriere…) e factor de risc și element de dosar AML.
**Cod:** `DosarAML` **nu are câmp `scop`**; `aml.html` nu îl cere. Modulul SEV are scopul (`profil.py`) dar nu îl pasează la AML.
**Acțiune:** câmp `scop` în `DosarAML` + dropdown în `aml.html` (preluat din lista §2); opțional propagat automat din dosarul de evaluare când e „garantare credit".

### G3 🟡 Câmpuri de identificare din formular necolectate în UI **[M]**
**Cerință:** formular §1 + Norme art. 4: pentru BR — **modalitate de identificare** (declarație client / extras ONRC / alte surse); pentru PJ străină — traducere legalizată; pentru împuternicit — document împuternicire.
**Cod:** modelul are `traducere_legalizata`, `document_imputernicire`, `acte_constituire`, dar `aml.html` colectează doar denumire+CUI și **un** BR fără aceste atribute. „Modalitate de identificare BR" **nu există** ca enum nici în model.
**Acțiune:** adaugă enum `modalitate_identificare_br` în `BeneficiarReal`; expune în UI câmpurile PJ existente (împuternicit, traducere legalizată, acte constituire).

### G4 🟡 Măsurile de atenuare (formular §9) nu sunt un checklist **[M]**
**Cerință:** formular §9 — listă de măsuri aplicate (solicitare documente suplimentare, verificări în registre, consultare responsabil CSB/CFT, raportare ONPCSB).
**Cod:** app-ul derivă doar `nivel_masuri` (simplificate/standard/suplimentare) din categorie. Nu există un checklist de **măsuri efectiv aplicate** consemnat în fișă.
**Acțiune:** secțiune „măsuri de atenuare aplicate" în fișa KYC (text liber + bife), ca evidență a EDD pentru risc sporit.

### G5 🟡 Reevaluare periodică — calculată, dar fără mecanism de reminder **[m]**
**Cerință:** Norme art. 1(3) — MDC se reaplică periodic (de regulă anual) pe durata relației.
**Cod:** `risc._adauga_luni` calculează `data_reevaluare` (36/24/12 luni pe categorie) și o pune în doc — **bun**. Dar nu există persistență a dosarului AML cu alertă la scadență (store-ul salvează doar RTN/RTS, nu dosarul KYC).
**Acțiune:** persistă `DosarAML` cu `data_reevaluare`; opțional listă „relații scadente la reevaluare".

### G6 🟡 Fiducii / construcții juridice (Norme art. 4(4)) — fără tratare dedicată **[m]**
**Cerință:** model norme art. 4(4) — la client parte într-un contract fiduciar se rețin copii ale declarațiilor de înregistrare a fiduciei.
**Cod:** `ClientPJ` nu modelează fiducia distinct; normele generate nu au paragraf de fiducie.
**Acțiune:** la prioritate joasă (caz rar la evaluare imobiliară de garantare); notă în norme + câmp opțional.

### G7 🟡 KYC pe PEP — formularul cere data încetării; UI doar bifă „este PEP" **[m]**
**Cerință:** PEP rămâne relevant 12 luni după încetarea funcției (art. 3(6)); formularul are categorie + tip PEP.
**Cod:** modelul `StatutPEP` are `categorie`, `tip`, `data_incetare_functie` (cu validare ISO) și `pep_efectiv` calculează corect cele 12 luni — **excelent**. Dar `aml.html` trimite doar `{este_pep: true/false}`, **fără** categorie/tip/dată → logica celor 12 luni nu poate funcționa din UI.
**Acțiune:** expune în UI `data_incetare_functie` (opțional) + select categorie/tip PEP, ca regula HARD din `risc.py` să aibă datele.

### G8 ✅ Praguri și termene — corecte (nu e gap, e confirmare)
Toate pragurile din formular/norme sunt codate corect cu temei: numerar 10.000 € (art. 7(1)), anti-fragmentare 15.000 € (art. 7(4)), tranzacție ocazională 15.000 € (art. 13), retenție 5 ani (art. 21), RTN +3 zile lucrătoare (art. 7(7)), suspendare RTS +24h (art. 8(3)), perioadă post-PEP 12 luni (art. 3(6)), praguri audit independent 2-din-3 (Norme art. 9). ✅

---

## 4. Prioritizare

**🔴 De făcut (conformitate KYC pentru clienți PJ):**
1. **G1 — RBR**: bifă „consultat RBR" + „neconcordanță" în UI și în fișa KYC; beneficiari reali repetabili cu procent/tip control/CNP.
2. **G7 — PEP complet în UI** (categorie/tip/data încetării) — altfel regula celor 12 luni e inertă din interfață.

**🟠 Importante (evidență de dosar):**
3. G2 (scop AML), G3 (câmpuri identificare PJ/împuternicit/traducere), G4 (checklist măsuri de atenuare).

**🟡 Ulterior (nișă / mecanică):**
4. G5 (persistență dosar + reminder reevaluare), G6 (fiducii).

> **Concluzie de încredere:** backend-ul AML (`risc.py`, `raportare.py`, `liste.py`, `documente.py`,
> `constante.py`) este **conform și mai bogat** decât documentele-model. Gap-ul dominant este de tip
> **„model bogat ↔ UI sărac"**: `aml.html` expune o fracțiune din câmpurile pe care modelele le pot purta.
> Reparațiile sunt aproape exclusiv în `aml.html` + 2 metode din `documente.py`, fără rescriere de motor.

**Documente conexe:** `docs/SEV-2025-gap-implementare.md`, `src/evaluare/aml/` (modul complet),
`docs/politica-GDPR-draft.md` (datele KYC sunt PII → GDPR).
