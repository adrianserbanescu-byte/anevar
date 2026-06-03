# Plan master — Aplicație de asistență la evaluarea imobiliară ANEVAR

**Data:** 2026-06-03 · **Stare:** nucleu funcțional, validat pe dosare reale · **Teste:** 176 verzi
**Pachet:** `evaluare-anevar/` (Python, FastAPI, PyInstaller onefile) · **Documentație:**
`module-aplicatie.md`, `roadmap-anevar.md`, 7 spec-uri în `superpowers/specs/`.

---

## 1. Rezumat executiv

Aplicația asistă evaluatorul autorizat la întocmirea unui **raport de evaluare casă + teren pentru
garantarea creditului**, de la datele proprietății până la documentul `.docx` final. Rulează **local,
ca un singur `.exe`**; datele rămân pe calculator (AI doar pe date anonimizate, GDPR).

**Stadiu:** motorul de calcul și generatorul de raport sunt **complete și validate** pe 4 dosare
reale GBF (teren) și 3 (casă). Raportul e **conform SEV 2025 + GEV 520**. Descoperirea de comparabile
(casă și teren) și cursul BNR funcționează live. Restul (ingestie OCR, ANCPI, BIG, audit, AML) sunt
**module planificate cu spec**, majoritatea blocate de acces extern sau validare juridică.

---

## 2. Ce s-a schimbat față de viziunea inițială (și de ce)

Specificația inițială (NotebookLM) descria un **„agent AI autonom"** pe 5 sisteme. Pe parcurs,
direcția s-a rafinat — deliberat și validat:

1. **Agent autonom → asistent cu om-în-buclă.** AI-ul NU decide valoarea; produce doar narativ și
   extrage atribute, totul verificabil și marcat. Motiv: **răspunderea profesională** a evaluatorului
   (GEV 520: opinia trebuie independentă) + **GDPR** + acceptabilitate la bănci.
2. **Cloud/serviciu → desktop local (exe).** Datele sensibile nu pleacă de pe calculator; singurul
   apel extern (narativ) e pe date **anonimizate**.
3. **Metodologie „presupusă" → validată pe grile reale.** Motorul reproduce exact dosarele GBF
   (descoperire cheie: grilele au **două etape**, nu compunere secvențială pură).
4. **Ecosistem ANEVAR explicit.** Cercetarea pe anevar.ro a adăugat surse care nu erau în spec:
   **BIG, BIF, Indicele imobiliar ANEVAR, IROVAL**, plus obligația **AML (Legea 129/2019)** și
   numerotarea **SEV 2025** (SEV 102/106).

**Concluzie:** cele 5 sisteme rămân valide ca structură, dar le **actualizez** (§3) și adaug un
**al 6-lea** (distribuție & experiență), devenit central.

---

## 3. Model de sisteme — ACTUALIZAT (faza curentă)

| # | Sistem | Conținut | Status |
|---|---|---|---|
| **S1** | **Intrare date (ingestie)** | wizard manual + import din URL (cu caracteristici structurate) · **OCR/VLM documente** (CF, releveu, plan, CPE) | 🟡 nucleu ✅ · OCR 📋 |
| **S2** | **Conectivitate & date de piață** | scraping portaluri (casă+teren) ✅ · **BNR** ✅ · **ANEVAR: BIG/BIF, Indicele** 📋 · **ANCPI/e-Terra** 📋 · **IROVAL** (cost) 📋 | 🟡 |
| **S3** | **Motor de evaluare** | cost CIN + grilă casă (preț total) + grilă teren (€/mp) + reconciliere + alocare | ✅ validat |
| **S4** | **Generare raport (SEV 2025 / GEV 520)** | shell GBF, 7 capitole, checklist GEV 520, anexe foto+documente, narativ AI, mod adnotări | ✅ |
| **S5** | **Conformitate & încredere** | validări SEV ✅ · anonimizare GDPR ✅ · **audit trail** 📋 · **AML 129/2019** 📋 | 🟡 |
| **S6** | **Distribuție & experiență** *(nou)* | wizard 5 pași · exe onefile · packaging · pre-completare · curs BNR | ✅ nucleu · semnare/instalator 📋 |

Diferențe față de cele 5 inițiale: S2 acum numește explicit sursele ANEVAR; S4 trece de la „SEV 103"
la **SEV 2025** (raportare = SEV 106); S5 include explicit **AML**; **S6 e nou** (produsul real e o
unealtă desktop, nu un serviciu).

---

## 4. Ce s-a făcut (cu dovezi)

### S3 Motor de evaluare — ✅ complet, validat
- `engine/cost.py` (CIN segregat IROVAL, depreciere interpolată) — regresie pe model real.
- `engine/market.py` (grilă casă, **preț total, 2 etape**) — reproduce exact **Bușteni, Maneciu, Brașov**.
- `engine/land.py` (grilă teren, €/mp, 2 etape, selecție ajustare brută minimă) — reproduce exact
  **Maneciu 44.000 / Brașov 78.000 / Bușteni 34.000 / Breaza 67.000**.
- `engine/reconciliation.py` (reconciliere + alocare) · `assembler.py` (orchestrare).

### S4 Generare raport — ✅ complet, conform 2025
- `report/generator.py`: copertă, scrisoare, declarații, **termeni de referință (SEV 101)**, 7
  capitole, **GEV 520 cu factorii obligatorii A5 + înregistrare BIG**, alocare, anexe (foto +
  documente), semnătură, **mod adnotări demo**, cifre la 2 zecimale.
- `ai/narrative.py` (narativ per capitol, client injectabil, curățare text) · `report/anonymizer.py`.

### S2 Conectivitate (parțial) — ✅ portaluri + BNR
- `discovery/` + `importers/url_parser.py`: descoperire **casă și teren**, extragere structurată
  (an, încălzire, material din storia/imobiliare), scor explicat, descriere din `__NEXT_DATA__`.
- `curs_bnr.py` + `/api/curs-bnr` + buton wizard (verificat live: 1 EUR = 5.2592 LEI).

### S1 Intrare date (parțial) — ✅ wizard + import
- `web/` wizard 5 pași (dropdown-uri județ/localitate, atribute, validări, foto+documente),
  import din URL, pre-completare grilă casă din descoperire.

### S5 Conformitate (parțial) — ✅ validări + GDPR
- `engine/validation.py` (min comparabile, outlier, limită ajustare) · anonimizare înainte de AI.

### S6 Distribuție — ✅ nucleu
- exe onefile PyInstaller; pornire cu browser auto; SQLite local; rebuild repetat verificat.

**Suport:** `localitati.py` (42 județe / 13.250 localități), `zona.py`, `config.py`, `money.py`,
`db/storage.py`.

---

## 5. Ce mai e de făcut (consolidat)

### Acum / rapid (cod pur, fără dependențe externe) — în mare parte DONE
Closed în această fază: conformitate SEV 2025, GEV 520, curs BNR, disclaimer comparabile, validare
casă (3 dosare), anexă documente, descoperire teren. **Rămâne:** export PDF (workaround Word
documentat), hint Indicele ANEVAR (parțial).

### Module planificate (fiecare cu spec)
| Modul | Sistem | Valoare | Blocaj |
|---|---|---|---|
| `ingestie/` (OCR + VLM) | S1 | Reduce transcrierea manuală din CF/releveu/plan/CPE | Cost model VLM; acuratețe scanuri |
| `ancpi/` (e-Terra) | S2 | Verificare cadastrală oficială | **Acces ANCPI** |
| `big/` (BIG) | S2 | Comparabile reale de garantare + înregistrare GEV 520 | **Acces membru ANEVAR** |
| `audit/` (audit trail) | S5 | Urmă de audit + validare încrucișată | — (implementabil) |
| `aml/` (Legea 129/2019) | S5 | Conformitate AML (diferențiator) | **Validare juridică** |

### Distribuție (S6)
exe **semnat** (evită SmartScreen) + instalator + instrucțiuni evaluator — necesită **certificat
code-signing**.

---

## 6. Principii & constrângeri (de respectat în orice fază viitoare)

1. **Om-în-buclă:** AI-ul propune, evaluatorul decide; fiecare cifră verificabilă (adnotări de
   proveniență).
2. **GDPR-first:** date personale anonimizate înainte de orice apel extern; demascare locală.
3. **Conformitate standarde:** raportul citează ediția în vigoare (acum SEV 2025) + GEV 520.
4. **Validare pe dovezi:** motoarele se validează pe dosare reale, nu pe presupuneri.
5. **Clienți injectabili:** AI, fetcher, (viitor) BIG/ANCPI — toate injectabile → testabile offline.
6. **TDD + rebuild + smoke:** fiecare modul cu teste; exe reîmpachetat și verificat.

---

## 7. Riscuri & dependențe principale

- **Acces extern** (ANCPI, BIG, IROVAL) — blochează `ancpi/`, `big/`, actualizarea IROVAL. *Acțiune:
  clarificare devreme cu ANEVAR/filiala.*
- **Validare juridică** (AML 129/2019) — `aml/` necesită confirmarea unui specialist conform.
- **Scraping fragil** — portalurile își pot schimba layout-ul; parser tolerant + fixturi reduc riscul.
- **Selecție comparabile casă** — regula curată poate diferi de marcajul manual din foile reale
  (acceptat de evaluator).
- **Distribuție** — exe nesemnat → avertisment SmartScreen (cost certificat).

---

## 8. Recomandare de ordine (faze viitoare)

1. **`audit/`** — singurul modul planificat **fără dependență externă**; crește încrederea și
   reproducibilitatea. Implementabil acum (schelet testabil).
2. **`ingestie/`** (OCR + VLM cu client injectabil) — valoare mare pentru evaluator; testabil cu
   fixturi, fără acces special (doar cost model, opțional).
3. **Clarificare acces ANEVAR** → apoi `big/` + `ancpi/` (cele mai autoritare date, dar blocate).
4. **`aml/`** — după validare juridică (diferențiator de conformitate).
5. **Distribuție** — certificat de semnare + instalator, când produsul intră în uz real.

*Acest plan înlocuiește înțelegerea „celor 5 sisteme inițiale" cu modelul actualizat din §3. Vezi
`module-aplicatie.md` pentru maparea modul-cod și `roadmap-anevar.md` pentru prioritizarea Now/Next/Later.*
