# Modul AML + GDPR + flux UI — note de REVIEW (factual, cu referințe)

> Document pentru evaluatori (+ jurist). Notele descriu CE FACE codul, nu ce ar trebui să facă.
> Referințele sunt căi de fișier (absolute) + linii. Toate datele AML/KYC rămân LOCAL; niciun apel AI pe ele.
> Citările de articole din lege (art. X) sunt cele scrise în cod — **toate marcate DRAFT, pending validare jurist**.

Sursă cod (rădăcină): `C:/Users/adyse/anevar/evaluare-anevar/`

---

## 1. AML — Legea 129/2019 + Norme Ord. ONPCSB 37/2021 + HCD 58/2023 ANEVAR

Modul: `src/evaluare/aml/` (pur, fără I/O de rețea — testabil offline). Orchestrare: `serviciu.py::evalueaza_relatie`.
Expunere web: `src/evaluare/web/routers/aml.py`. UI: tab „AML" în `templates/curent/dosar.html` (port din `templates/aml.html`).

### 1.1 Ce face modulul (pipeline)
`evalueaza_relatie(tip_entitate, client, *, azi, semnale_risc, semnale_indicatori, liste)` întoarce un dict cu:
`evaluare_risc`, `categorie`, `nivel_masuri`, `motive_sporit`, `indicatori`, `propune_rts`, `screening`,
`necesita_persoana_desemnata`, `documente_necesare`. (`serviciu.py:30-67`)

### 1.2 KYC / cunoașterea clientului — `aml/models.py`
- `PersoanaFizica`: nume, prenume, cnp, tip_act (CI/pasaport/permis_sedere), serie/nr act, cetățenie, domiciliu, ocupație. Temei citat: Legea art. 15(1)(a); Norme art. 18(1)(a). (`models.py:27-39`)
- `StatutPEP`: este_pep, categorie (8 categorii funcții publice, Legea art. 3(2) a-h), tip (titular/membru_familie/asociat_apropiat), data_incetare_functie (ISO, pentru cele 12 luni). (`models.py:41-47`, `19-24`)
- `BeneficiarReal` (extinde PF): procent, tip_control (proprietate/alte_mijloace/senior_management), pep, consultat_registru_central, neconcordanta_registru. Prag control beneficiar real **> 25%** (`constante.py:7`, „>=25% + 1 acțiune", Legea art. 4(2)(a)(1)). (`models.py:50-58`)
- `ClientPF` și `ClientPJ` (PJ / PJ_straina): denumire, cui, sediu, acte, reprezentant_legal, împuternicit, `traducere_legalizata` (obligatorie PJ străină, art. 15(2)), listă beneficiari_reali. (`models.py:60-80`)
- `DosarAML`: tip_entitate_evaluator (PJ/PFA), persoana_desemnata, client, evaluare_risc, indicatori, data_creare, data_retentie. (`models.py:103-114`)

### 1.3 Evaluarea riscului — `aml/risc.py::evalueaza_risc`
Model de scor cu 4 factori ponderați, fiecare cu valoare 1=redus / 2=standard / 3=sporit:
| Factor | Pondere | Sursă |
|---|---|---|
| client | 2 | PEP efectiv sau pe listă sancțiuni → 3; client_cunoscut → 1; altfel 2 |
| produs_serviciu (tranzacția) | 1 | tranzactie_complexa → 3; tranzactie_uzuala → 1; altfel 2 |
| canal | 1 | canal_la_distanta → 3; canal_fata_in_fata → 1; altfel 2 |
| geografic | 2 | tara_risc_inalt → 3; tara_risc_redus → 1; altfel 2 |

Scor = Σ(valoare×pondere) / Σ(pondere). **Praguri categorie** (`risc.py:146-153`):
- scor ≤ **1.4** → `redus` (măsuri „simplificate")
- scor ≥ **2.2** → `sporit` (măsuri „suplimentare" / EDD)
- altfel → `standard` (măsuri „standard")

**Reguli HARD (forțează „sporit" indiferent de scor)** — Legea art. 17(1)/(2) (`risc.py:132-144`):
1. PEP efectiv (titular sau în primele **12 luni** de la încetare — art. 17(1)(c); `PERIOADA_POST_PEP_LUNI=12`, `constante.py:22`)
2. Persoană pe listă de sancțiuni
3. Țară terță cu risc înalt / necooperantă — art. 17(1)
4. Tranzacție complexă / neobișnuit de mare / fără scop economic — art. 17(1)
5. Relație fără prezență fizică (la distanță) — art. 17(2)

`pep_efectiv()` calculează cele 12 luni din `data_incetare_functie` vs `azi` (`risc.py:53-59`). Pentru PJ se verifică PEP pe fiecare beneficiar real (`risc.py:77-84`).
Rezultatul (`EvaluareRisc`) include și `data_reevaluare` = azi + {redus:36, standard:24, sporit:12} luni (politică internă, `risc.py:25`, `162`).

### 1.4 Indicatori de suspiciune — `aml/indicatori.py`
Catalog FIX de **10 indicatori**, temei `HCD 58/2023 art. 6(10)` (`indicatori.py:18-39`): grabă excesivă; presiune cu documente insuficiente; nemulțumire nejustificată; presiune pentru valoare predeterminată; scop nedefinit; PEP implicat; istoric atipic de tranzacționare; tranzacții în dezacord cu piața; drepturi litigioase; antecedente penale.
`propune_rts()` = TRUE dacă **cel puțin un** indicator e bifat (HCD 58 art. 7) (`indicatori.py:69-71`). Plus câmp liber `observatii`.

### 1.5 Screening PEP / sancțiuni — `aml/liste.py` + `aml/data/liste.json`
- **INJECTABIL, NU live.** Listele se încarcă din `data/liste.json` (sau injectate); modulul NU face apeluri automate. (`liste.py:1-8, 52-58`)
- Screening tolerant: normalizare fără diacritice + `SequenceMatcher`, prag similaritate **0.86**; orice potrivire = „Posibilă potrivire — verificați manual sursa oficială" (niciodată decizie automată). (`liste.py:19, 28, 61-72`)
- `liste.json` actual e **PLACEHOLDER** explicit (`_nota`): `sanctiuni: []`, `tari_necooperante: []`, `pep_functii` = 9 funcții exemplu, `tari_risc_inalt` = [Coreea de Nord, Iran, Myanmar]. Trebuie reîmprospătat manual din surse oficiale (UE/ONU, ANI, CE, ONPCSB/GAFI) înainte de uz real. (`data/liste.json:1-22`)
- UI avertizează explicit: „Aplicația **NU verifică automat** sancțiuni/PEP" cu linkuri către OpenSanctions / EU Sanctions Map. (`dosar.html:315-317`)

### 1.6 Documente generate (.docx) — `aml/documente.py`
Set returnat de `serviciu.py:51-55`: mereu `norme_interne`, `evaluare_risc`, `fisa_kyc`; `decizie_desemnare` doar dacă entitatea e societate; `rts` dacă există indicatori. Fiecare doc are antet cu avertisment DRAFT (vezi §1.8).
1. **Norme interne** — 7 capitole (Norme art. 8(1) a-g): raportare/evidențe, KYC, administrarea riscurilor, control intern/conformitate, protecția personalului, whistleblowing, instruire. (`documente.py:74-112`)
2. **Evaluarea de risc** — categorie, nivel măsuri, scor, date, tabel factori, motive risc sporit. (`documente.py:118-141`)
3. **Decizie de desemnare** persoană responsabilă AML/CFT — **DOAR societate**; pentru PFA aruncă `ValueError` (Norme art. 7; Legea art. 23(4)) → API întoarce 400. (`documente.py:147-174`, `aml.py:64-73`)
4. **Fișă KYC** — date PF/PJ, beneficiari reali (>25%), statut PEP, rezultat risc; câmpuri de verificare/semnătură. (`documente.py:193-230`)
5. **RTN** (raport numerar) — prag echiv. **10.000 €** (Legea art. 7(1)), termen **3 zile lucrătoare**, conversie curs BNR; „se transmite exclusiv ONPCSB". (`documente.py:236-248`, `raportare.py:34-36, 73-76`)
6. **RTS** (raport suspiciune) — avertisment **tipping-off** vizibil sus (interdicție de divulgare, Legea art. 38), motiv, suspendare +24h, indicatori; „stocat SEPARAT de dosar". (`documente.py:254-274`, `raportare.py:20-24`)

### 1.7 Praguri/cifre legale — `aml/constante.py` (fiecare cu articolul-sursă)
beneficiar real **0.25**; numerar RTN **10.000 €**; KYC tranzacție ocazională **15.000 €**; anti-fragmentare **15.000 €**; transfer fonduri **1.000 €**; post-PEP **12 luni**; retenție **5 ani** (+ prelungire max 5); termen RTN **3 zile lucrătoare**; suspendare RTS **24h**; audit independent obligatoriu la depășirea a ≥2 din 3 praguri: active **16.000.000 lei**, CA **32.000.000 lei**, **50** salariați (Norme art. 9; `incadrare.py:18-27`).
Anti-fragmentare: `raportare.py::tranzactii_legate` — fereastră glisantă 30 zile, însumare ≥ 15.000 € (art. 7(4)).

### 1.8 Ce e DRAFT / pending jurist
- Antetul fiecărui .docx conține: „**DRAFT GENERAT AUTOMAT — NEVERIFICAT JURIDIC**. A se valida de un consultant/jurist AML. Legea 129/2019 art. **43/44/49** prevede sancțiuni (inclusiv penale) pentru raportarea cu rea-credință/neglijență. Aplicația NU efectuează verificări automate pe listele de sancțiuni/PEP." (`documente.py:34-40`)
- UI cere `confirm()` înainte de a genera RTN/RTS, cu același avertisment art. 43/44/49. (`dosar.html:750`)
- Listele de screening = placeholder, de reîmprospătat manual (§1.5).
- Citările de articole (art. 3/4/7/8/15/17/21/23/38; Norme art. 7-22; HCD 58) sunt scrise în cod ca temei — **de verificat de jurist**.

### 1.9 Stocare separată (tipping-off) — `aml/store.py`
`StoreAML` scrie în director dedicat `<db_path>.parent/aml_confidential`, **separat** de dosarul de evaluare, append-only, 1 fișier JSON per înregistrare (`rts_NNNN.json` / `rtn_NNNN.json`), cu `data_retentie` = data + 5 ani. RTN și RTS sunt persistate la generare (`aml.py:88-89, 100`). Motiv: tipping-off + retenție (Legea art. 38, art. 21).

---

## 2. GDPR / anonimizare înainte de AI

### 2.1 Fluxul exact (date reale → AI → demascare locală)
Lanțul de apel: `assembler.py:191-192` → `build_anonymizer(inp.meta)` apoi `generate_narrative(ctx, client, anonymizer)`.
1. **Construire mapă** din datele personale ale lucrării: `build_anonymizer` (`report/anonymizer.py:34-44`) creează perechi real→token doar pentru câmpurile ne-goale:
   `client_nume→[CLIENT]`, `adresa→[ADRESA]`, `numar_cadastral→[CADASTRAL]`, `carte_funciara→[CF]`, `evaluator_nume→[EVALUATOR]`.
2. **Mascare** înainte de orice trimitere: `Anonymizer.mask()` înlocuiește valorile reale cu token-uri, **cele mai lungi întâi** (ca o valoare să nu fie subșir al alteia). (`anonymizer.py:19-24`, `narrative.py:195-196`)
3. **Plasă de siguranță (regex)** aplicată DUPĂ mascare, înainte de trimitere — `filtreaza_pii_rezidual` (`narrative.py:77-88, 197`): tipare RO scăpate →
   - CNP 13 cifre `\b[1-9]\d{12}\b` → `[REDACTAT-CNP]`
   - mobil RO `\b(?:\+?40|0)7\d{8}\b` → `[REDACTAT-TEL]`
   - email → `[REDACTAT-EMAIL]`
4. **Către AI pleacă DOAR textul anonimizat** = rezumat de cifre calculate (`_facts`, `narrative.py:114-155`) + ghid per capitol. System prompt cere păstrarea marcajelor `[CLIENT]/[ADRESA]/[CADASTRAL]/[CF]/[EVALUATOR]` exact și interdicția de a inventa surse/cifre. (`narrative.py:63-73`)
5. **Demascare LOCALĂ** după răspuns: `anonymizer.unmask()` pune valorile reale la loc (`narrative.py:210`), apoi curățare markdown/citații web (`_curata_narativ`).
6. **Fără client AI → placeholdere**, complet offline, niciun transfer extern. (`narrative.py:191-192, 158-159`)

### 2.2 Clienți AI (sub-procesatori)
`AnthropicNarrativeClient` (Claude, model implicit `claude-sonnet-4-6`, prompt caching pe system, temperature 0.2) și `PerplexityNarrativeClient` (sonar). Ambii injectabili; constructorul nu apelează rețea. (`narrative.py:215-275`)

### 2.3 Ce NU pleacă niciodată
- **Datele AML/KYC** (CNP, beneficiar real, PEP, indicatori) — modulul AML e pur, fără apel AI (`aml/models.py:1-5`, `serviciu.py:3`).
- Valorile personale brute din raport — înlocuite cu marcaje înainte de trimitere; doar cifre + text anonimizat ajung la AI.
- Generarea AML și narativul AI sunt fluxuri separate.

### 2.4 Documente / drafturi GDPR
- Generabile din UI (.docx model) prin `/api/gdpr/politica.docx` și `/api/gdpr/consimtamant.docx` (`aml.py:103-111`; `gdpr/documente.py`).
- Surse text: `docs/gdpr/politica-prelucrare-MODEL.md` (operator = evaluatorul, NU aplicația; sub-procesatori AI Anthropic/Perplexity pe text anonimizat; alternativă offline; retenție ~5 ani; date locale SQLite) și `docs/gdpr/formular-consimtamant-MODEL.md` (bifă „de acord cu AI pe text anonimizat" / „exclusiv offline"; drepturi GDPR; plângere ANSPDCP). Ambele marcate **MODEL — de validat de jurist**.
- Drafturi legale conexe în `docs/legal/` (toate „**DRAFT — necesită validarea unui avocat din România**"): `00-evaluare-juridica-RO.md`, `10-termeni-si-conditii-DRAFT.md`, `11-politica-confidentialitate-DRAFT.md`, `12-acord-licenta-EULA-DRAFT.md`, `13-DPA-acord-prelucrare-DRAFT.md` (art. 28 GDPR), `14-disclaimer-profesional-DRAFT.md`.

---

## 3. Flux UI NOU (output-first) — `templates/curent/`

Rute: `web/routers/curent.py`. Ordinea reală: **cont → ÎNCEPE → workspace dosar**.

### 3.1 Pagina cont — `curent/cont.html` (`GET /cont`)
Setezi o singură dată: nume evaluator + legitimație ANEVAR + **formatul numelui de dosar** (minim 3 câmpuri bifate, în ordine — ex. `id_client_scop_tip_proprietate`), cu previzualizare live. `POST /api/cont` → redirect la `/incepe`. (`cont.html:34-50`)

### 3.2 ÎNCEPE — `curent/incepe.html` (`GET /incepe`)
- Dacă nu există cont → mesaj „Creează cont".
- Acțiuni: **Dosar nou** (formular cu doar câmpurile de identitate din `format_dosar`), **Încarcă dosar salvat** (tabel dosare cu „Deschide"), **Importă dosarul tău** (`.docx` → `POST /api/dosar/import-docx`). „Import asemănător" și „Demo" sunt dezactivate (badge „comercial").
- „Creează dosarul" → `POST /api/dosar` cu `{wizard:{...}}` → redirect `/dosar/{uuid}`. Datele-dată au max=azi (fără date viitoare) + format românesc. Secțiune „Dosare dispărute" (folder șters) cu „scoate din listă". (`incepe.html:20-143`)

### 3.3 Workspace dosar — `curent/dosar.html` (`GET /dosar/{uid}`)
Salvare **automată în folder** (debounce 700ms) la orice `input/change`, cu indicator de stare „● salvat în folder" (`POST /api/dosar/{uid}/salveaza`; `dosar.html:514-522`). UID + `wizard` injectate din backend. Pattern tab-uri WAI-ARIA (săgeți/Home/End).

**4 tab-uri principale** (`dosar.html:18-23`): Raport · AML · GDPR · Audit.

#### Tab RAPORT — 5 sub-tab-uri (`dosar.html:28-34`)
- **Proprietate** (`dosar.html:36-152`): pre-completare inline din PDF (extras CF/releveu/plan/CPE) prin `POST /api/ingestie` → completează câmpuri (cadastral, CF, suprafețe, arii, proprietar), cu „VERIFICĂ valorile". Identificare (id_client, nume_client, scop, tip_proprietate — ultimele două **blocate** după creare fiindcă intră în identitate/nume), județ/localitate ca liste din `/api/localitati`, adresă, cadastral, CF, proprietar, beneficiar (bancă), drept evaluat, act, sarcini/grevări, 3 date (raport/evaluare/vizită), amploare+observații inspecție. Date fizice dinamice pe tip (apartament/industrial/agricol/teren/construcție), utilități GEV 630, acces, restricții urbanism, elemente de cost + depreciere (abordarea prin cost).
- **Comparabile** (`dosar.html:154-239`): **descoperire inline** prin `POST /api/descopera` și `/api/descopera-teren` (portaluri imobiliare.ro/storia.ro, scor de relevanță, bifează→importă în grilă); import dintr-un URL (`/api/import-url`); coadă „anunțuri din extensia de browser" (`/api/anunturi-importate`). 3 **grile de ajustări** randate în JS (casă 16 elemente, teren 17, chirii 9), fiecare pe 2 etape (tranzacție compus / proprietate aditiv) cu **alertă prudențială ajustare brută > 25% (GEV 520)**; endpoints `/api/grila-casa`, `/api/grila-teren`, `/api/grila-chirii`; grila de chirii produce VBP pentru metoda Venit.
- **Calcul** (`dosar.html:241-275`): metodă (cost/piață/ponderată/venit/DCF — cost/ponderată active doar pe construcții), monedă, curs BNR auto (`/api/curs-bnr`), câmpuri venit/DCF condiționate de metodă. „Calculează" → `POST /api/dosar/{uid}/calcul` → valoare finală + **alerte de validare** (nivel `blocheaza`/avertisment). (`dosar.html:990-1005`; backend `curent.py:132-147`)
- **Anexe** (`dosar.html:277-286`): încărcare **fotografii (Anexa 2)** + scanuri/documente (Anexa 3) → base64 incluse în .docx; cerință SEV 2025 (GEV 630).
- **Generează** (`dosar.html:288-303`): vezi checkpoint mai jos.

#### Checkpoint de asumare la «Generează» (om-în-buclă)
Butonul „Generează și descarcă raportul" e **disabled** până când evaluatorul bifează: „Confirm că am verificat datele și **îmi asum profesional** valoarea și conținutul raportului, ca evaluator autorizat ANEVAR (semnătura îmi aparține; aplicația doar asistă)." (`dosar.html:292-298, 448-452`). Comentariu în cod: convergență audit juridic + LLM council — asumarea trăiește în UI, cu urmă în dosar.
La generare, dacă lipsesc data evaluării/raportului → `confirm()` explicit (risc juridic la garantare: o dată greșită afectează valabilitatea), apoi `POST /api/dosar/{uid}/raport.docx` (opțional `?adnotari=1` = note de proveniență/demo). Fiecare generare = **versiune persistentă** în folder; copia din %TEMP% se șterge după trimitere (igienă PII). (`dosar.html:1006-1021`; backend `curent.py:182-195`). Avertisment afișat: textul AI e doar proză narativă (draft), **toate valorile numerice sunt deterministe** (motorul de calcul), nu produse de AI.

#### Tab AML (port din `aml.html`; `dosar.html:313-358, 735-775`)
Avertisment „NU verifică automat sancțiuni/PEP". Câmpuri: entitate evaluator (PFA/PJ) + data; client (PF/PJ, nume/prenume/CNP/denumire/CUI), bifă PEP; 4 semnale de risc; cele 10 indicatori de suspiciune. „Evaluează relația" → `POST /api/aml/evalueaza` → afișează categorie risc (badge), nivel măsuri, motive sporit, indicatori activi (+ „se propune RTS"), posibile potriviri screening (marcate demonstrative), apoi butoane pentru fiecare document necesar (`/api/aml/*.docx`). RTS/RTN cer `confirm()` (art. 43/44/49). Data evaluării e sincronizată între Identificare și AML (`dosar.html:579-580`).

#### Tab GDPR (`dosar.html:360-367, 712-723`)
Două butoane: „Politică de prelucrare (.docx)" + „Acord de consimțământ (.docx)" → `/api/gdpr/politica.docx` / `/api/gdpr/consimtamant.docx` (modele). Linkuri către politica de confidențialitate + disclaimer profesional.

#### Tab AUDIT (`dosar.html:368-373, 725-733`)
„Generează urma de audit" → `POST /api/dosar/{uid}/audit.txt` → jurnal hash-înlănțuit + validare încrucișată pentru valorile curente, afișat inline (și descărcabil .txt din tab Generează). Backend: `JurnalAudit` + `valideaza_incrucisat` (`curent.py:149-180`).

---

## 4. Flux VECHI (wizard 5 pași) — `templates/wizard.html` (+ `form.html`)

Încă există. `wizard.html`: stepper cu **5 pași** — **1 Adresă** (& lucrare; import PDF, județ/localitate, client/proprietar/evaluator, cadastral/CF, scop, date) · **2 Subiect** · **3 Comparabile** · **4 Calcul** · **5 Raport**. Datele personale sunt anonimizate ([CLIENT]/[ADRESA]/[CADASTRAL]/[CF]) înainte de orice apel AI (note repetate în UI, ex. `wizard.html:67-84`). `form.html` = varianta „formular clasic" cu toate câmpurile pe o pagină (același set + aceleași note de anonimizare; `form.html:7-50`).

**Relația vechi ↔ nou:** UI-ul nou („output-first") reorganizează aceiași pași în tab-uri/sub-tab-uri într-un singur workspace per dosar, cu salvare pe foldere (NU SQLite) și identitate stabilită la creare. Maparea explicită vechi→nou e încă în cod ca ajutor de tranziție: obiectul `MAPARE` (câmp nou → „Pas N · etichetă veche") și popover-ul „!" lângă fiecare label (`dosar.html:381-406, 506-508`) — marcat „TEMPORAR (dev); se va șterge". Vechiul UI mai e accesibil din `index.html` / `_topbar.html` (`/`, `/dosare`, `/aml` standalone); cel nou din `/incepe`.

---

## 5. Endpoints relevante (referință rapidă)
- AML: `POST /api/aml/evalueaza`; docx `/api/aml/{norme-interne,evaluare-risc,decizie,fisa-kyc,rtn,rts}.docx`; pagină standalone `GET /aml`. (`routers/aml.py`)
- GDPR: `POST /api/gdpr/{politica,consimtamant}.docx`. (`routers/aml.py:103-111`)
- Dosar nou: `POST /api/cont`, `POST /api/dosar`, `POST /api/dosar/import-docx`, `GET /dosar/{uid}`, `POST /api/dosar/{uid}/{salveaza,calcul,audit.txt,raport.docx}`. (`routers/curent.py`)
- AI narativ + anonimizare se declanșează în pipeline-ul de raport: `assembler.py:191-192` (`build_anonymizer` + `generate_narrative`).
