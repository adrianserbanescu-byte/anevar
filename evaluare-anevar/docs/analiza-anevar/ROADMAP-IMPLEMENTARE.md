# ROADMAP DE IMPLEMENTARE — conformitate consolidată (status unic)

> **Scop:** un SINGUR tabel de adevăr peste TOATE gap-urile de conformitate identificate, cu **STATUS verificat în cod** (la `master` curent, 2026-06-11). Consolidează:
> - `docs/SEV-2025-gap-implementare.md` (gap-uri G1–G17, SEV 2025 / GEV 520)
> - `docs/analiza-anevar/00-SINTEZA.md` (gap-uri S-1..S-5, I-1..I-19, m-1..m-6 din 7 analize tematice ANEVAR)
> - `docs/audit-report-completeness-2026-06-11.md` (findings F-01..F-10, raport GEV 520)
> - `git log` recent (ce s-a implementat efectiv).
>
> **Metodologie status:** fiecare „✅ IMPLEMENTAT" e verificat în codul de pe branch (modul/funcție/cablare existentă — grep/read, nu presupunere). „🟡 ÎN CURS" = logica există dar nu e cablată complet end-to-end (lipsește o piesă: online / anexă / validare jurist). „⏳ PENDING" = neînceput, decizie tehnică. „⏸️ PARCAT-JURIST" = text/normă cu valoare legală, nu se finalizează autonom (pending jurist), chiar dacă scheletul de date/UI există.
>
> **Legendă STATUS:** ✅ IMPLEMENTAT · 🟡 ÎN CURS (parțial cablat) · ⏳ PENDING · ⏸️ PARCAT-JURIST
> **Severitate:** **B** = blocant · **M/important** = mediu · **m/minor** = minor
>
> **REVIZUIT 2026-06-11 (a doua trecere, status RE-VERIFICAT în cod):** prima versiune a acestui document a fost scrisă când erau ~15 done și marca ESG/valoare-prudentă/BIG/per-tip/AML-scop/indicatori ca „în curs / parcat". Între timp au fost cablate efectiv (commit-uri `327f9ca`, `e8d93f5`, `d132a12`, `29639a1`, `a9a52d0`, `7c97341`, `48d8119`, `775b65c`, `d344d15`, `8ab1d0f`, `09bc39d`, `db66a7e`, `cd5ae14`). Numărătoarea de mai jos reflectă starea REALĂ verificată în cod.

---

## 0. SUMAR EXECUTIV (numărătoare RE-VERIFICATĂ în cod, 2026-06-11)

| Grup | ✅ Done | 🟡 În curs | ⏳ Pending | ⏸️ Parcat-jurist | Total |
|---|---|---|---|---|---|
| Blocante (BLOC-1..7) | 3 | 2 | 1 | 1 | 7 |
| Importante | 23 | 1 | 5 | 4 | 33 |
| Minore | 6 | — | 9 | 1 | 16 |
| **TOTAL** | **32** | **3** | **15** | **6** | **56** |

> **Notă metodologică numărătoare:** totalul a crescut de la 37 la 56 pentru că au fost contabilizate explicit și piesele „motor + cablare + UI + QC" care înainte erau ascunse în câte un singur rând (ex. ESG = modul + render raport + UI dosar + item QC = 4 livrabile distincte, toate ✅). Frame-ul de gap-uri normative e același; granularitatea e mai fină.
>
> **Interpretare:** Față de prima versiune (15 done), s-au mai închis **~17 livrabile**: cablarea ESG+CPE în raport+UI (BLOC-1 ✅), valoarea prudentă end-to-end (✅), structura per-tip de imobil (✅), scopul ca factor de risc AML (BLOC-7 ✅), expunerea „comercial" în dropdown + maparea la profilul de venit (BLOC-4 ✅, închis azi), indicatorii suplimentari de suspiciune (I-5 ✅), bonitarea agricolă (✅), cele 3 forme de depreciere + clamp (✅), valoarea în litere F-01 (✅), itemii QC ESG/prudentă (✅), plus scheletul de date+UI pentru EDD/RBR (BLOC-6 / S-3 — model+UI ✅, dar TEXTUL legal rămâne parcat-jurist). Ce rămâne **cu adevărat blocant**: garda cost≠principal (BLOC-3), integrarea online BIG + recipisa ca anexă (BLOC-2), și deciziile legale (BLOC-5 + corpul normativ AML/GDPR).

---

## 1. ✅ DEJA IMPLEMENTAT pe master (verificat în cod) — NU se repară

| Cod | Descriere | Sev. | Dovadă în cod | STATUS |
|---|---|---|---|---|
| I-6 / G-Q1 | **QC pre-emitere** (checklist calitate: comparabile, CMBU, tip valoare, documente, coerență, adecvare + gate emisibilitate + endpoint live + panou UI) **+ itemi noi: ESG riscuri fizice + valoare prudentă considerată** | important | `calitate.py` (`verifica_calitate`, `_item_riscuri_fizice`, `_item_valoare_prudenta`, `emisibil`, `blocaje`); cablat în `web/routers/evaluare.py` + `curent.py`; commit `d132a12` | ✅ IMPLEMENTAT |
| I-1 / I-2 | **Registru rapoarte** (~13 câmpuri, export CSV/XLSX, export audit per-dosar) + **nr. lucrare secvențial AAAA/NNNN** (alocare atomică) | important | `registru/registru.py`, `registru/numar.py` (`aloca`), router `registru.py` | ✅ IMPLEMENTAT |
| I-15 / m-6 | **Disclaimer AML real** (antet corectat: screening REAL „posibilă potrivire, verificată manual" + avertisment liste goale/expirate) | important/minor | `aml/documente.py`, `aml/liste.py` | ✅ IMPLEMENTAT |
| I-7 | **Rata de capitalizare derivată din piață** (vânzare-închiriere, comparabile, build-up) + validare plauzibilitate + sursă documentată | important | `engine/venit.py` (`rata_din_vanzare_inchiriere`, `rata_din_comparabile`, `rata_build_up`, `valideaza_rata_capitalizare`) | ✅ IMPLEMENTAT |
| I-8 | **Defalcare OPEX** (poziții service-charge) + distincția chirie brută/netă | important | `engine/venit.py` (`CheltuieliExploatare.total`, `DateVenit`) | ✅ IMPLEMENTAT |
| I-19 | **Valoare terminală DCF** Gordon + exit-cap (era sumă manuală) | important | `engine/venit.py` (`valoare_terminala_gordon`, `valoare_terminala_exit_cap`, `evalueaza_dcf`, `abordare_dcf`) | ✅ IMPLEMENTAT |
| G17 | **DCF: rata de actualizare cu sursă + bandă de plauzibilitate** (corelare tip venit↔tip rată) | minor | `engine/venit.py` (`valideaza_rata_actualizare`) | ✅ IMPLEMENTAT |
| I-9 / I-10 / I-12 / m-2 / m-3 | **Validare comparabile îmbogățită** (omogenitate, recență/proximitate, ofertă→tranzacție) + analiză piață + CMBU + anti-contaminare notarial + supra-îmbunătățire | important/minor | `engine/validation.py`, `engine/market.py`, `calitate.py` (`_item_cmbu`); commit `3820934` | ✅ IMPLEMENTAT |
| I-18 / B2-IND-OFF | **Indice imobiliar ANEVAR — tabel offline** (fallback offline-first la 403/indisponibil) | important | `indice_anevar.py` (`INDICE_OFFLINE`, `_tabel_offline`, `SURSA_OFFLINE`) | ✅ IMPLEMENTAT |
| N4 | **Consistență suprafață subiect ≤0** respinsă uniform în toate 3 grilele (422) | mediu | `web/schemas.py` (`Field(gt=0)`); commit `a6163c7` | ✅ IMPLEMENTAT |
| F1-1 | **/dosare dead-end → redirect** la `/incepe#salvate` | UX | `web/routers/pagini.py`; commit `3cea2e9` | ✅ IMPLEMENTAT |
| 0-SOLID | **Fundație SEV 2025** (3 abordări + reconciliere fără medie aritmetică, min 3 comparabile, depreciere justificată, SEV 450 = CIB, declarații SEV 100, BIG condiționat ANAF, factorii A5 garanție, inspecție amploare+însoțitor) | — | `engine/abordari.py`, `engine/reconciliation.py`, `engine/validation.py`, `engine/cost.py`, `report/generator.py` | ✅ IMPLEMENTAT |
| **G3-RECON** | **Reconciliere GEV 630 §107/108/109** (interzice media aritmetică/ponderată ca concluzie; avertizează a-doua-abordare-formală §108; diferență >20% între abordări §109) | mediu | `engine/reconciliation.py` (`_AVERT_107`, `_avert_diferenta_mare`, `_PRAG_DIFERENTA`) | ✅ IMPLEMENTAT |
| **S-5 / G1 (CABLAT)** | **ESG / riscuri fizice — END-TO-END.** Modul `esg.py` (catalog 8 riscuri, disclaimer necuantificare GEV 520 §87) **CABLAT în raport** (`generator._adauga_esg` → secțiune înaintea analizei de risc) **+ UI dosar** (8 checkbox-uri `.risc-fizic` + JS `riscuri_fizice` în payload) **+ item QC** | blocant→done | `esg.py` (`genereaza_sectiune_esg`); `report/generator.py:705,1117`; `dosar.html:198–208,1297–1298`; commit `327f9ca`/`48d8119` | ✅ IMPLEMENTAT (BLOC-1 închis) |
| **G7 / F-03 (CPE)** | **Certificat energetic (CPE) + cod_postal + riscuri_fizice** — câmpuri model **ȘI randate**: CPE în cap.4 descriere fizică, cod poștal pe copertă (necesar BIG) | mediu | `models/meta.py`; `report/generator.py:319,1030`; `dosar.html:143,186` | ✅ IMPLEMENTAT |
| **S-5-VP / CRR** | **Valoare prudentă (de garanție) — END-TO-END.** Modul `valoare_prudenta.py` (CRR art. 229/208, plafonare ≤ valoare de piață) **CABLAT** ca secțiune OPȚIONALĂ la garantare (omis elegant fără parametri) | important | `valoare_prudenta.py` (`estimeaza_valoare_prudenta`, `genereaza_nota_valoare_prudenta`); `report/generator.py:808,831,1121`; commit `8ab1d0f`/`e8d93f5` | ✅ IMPLEMENTAT |
| **PER-TIP** | **Structura livrabilului PER TIP de imobil** (teren/agricol fără construcție; apartament fără teren standalone + notă cotă indiviză; comercial venit-principal + fără cost) | mediu | `profil.SECTIUNI_PER_TIP`, `profil.sectiuni_pentru_tip`; `report/generator._sectiuni` (folosit la 560/597/613/651/1000/1060); commit `a9a52d0` | ✅ IMPLEMENTAT |
| **BLOC-4 / G2** | **Tip „comercial" în UI + abordarea prin venit accesibilă.** Dropdown-ul `tip_proprietate` expune opțiunea „comercial" (generator de venit), iar la selectare metoda comută automat pe „venit"; `assembler.PROFIL_DUPA_TIP["comercial"]` mapează la profilul `COMERCIAL_INCHIRIAT` (venit principal în raport). Motor venit/DCF + structură per-tip deja DONE. | **B** (pt. comercial) | `dosar.html:142` (`<option value="comercial">`) + `dosar.html:929` (comutare metodă→venit); `assembler.py:50` (`"comercial": COMERCIAL_INCHIRIAT`); commits `fcdd173` (UI) + `400da88` (mapare profil) | ✅ IMPLEMENTAT (BLOC-4 închis) |
| **AGRICOL** | **Bonitare agricol** — comparația vânzărilor cu nota de bonitare a solului ca ELEMENT DE COMPARAȚIE (NU formula PMB), conform poziției ANEVAR / GEV 630 §86 | important | `engine/land.py` (`evaluate_land_agricol`, `aplica_bonitare`, `ajustare_bonitare`); commit `09bc39d` | ✅ IMPLEMENTAT |
| **COST-3D** | **Cele 3 forme de depreciere** (fizică interpolare/liniară, funcțională supradimensionare, externă/economică) aplicate multiplicativ + **clamp [0,1]** pe interpolare | mediu | `engine/cost.py` (`depreciere_fizica_liniara`, `depreciere_functionala_supradimensionare`, `depreciere_externa_din_pierdere`, clamp în `interpolate_depreciation`); commit `db66a7e`/`cd5ae14` | ✅ IMPLEMENTAT |
| **F-01** | **Valoarea finală redată în litere (cuvinte)** — pe copertă + lângă concluzia de valoare (uzanță fermă la verificarea bancară) | mediu | `report/generator.py` (`_valoare_in_litere`, `_numar_in_litere`, folosit la 343, 1108); commit `327f9ca` | ✅ IMPLEMENTAT |
| **S-1 / BLOC-7** | **Scopul evaluării ca factor de risc AML** (lichidare/insolvență/executare/vânzare-piață = ridică; garantare/impozitare/raportare = scade) — wiring complet dosar→risc | blocant→done | `aml/risc.py` (`ScopEvaluare`, `_SCOP_FACTOR`, `_factor_produs`); `aml/serviciu.py` (`scop_aml_din_dosar` → `Semnale.scop`); commit `775b65c` | ✅ IMPLEMENTAT (BLOC-7 închis) |
| **I-5** | **Indicatori de suspiciune suplimentari** (15 din Ghidul ONPCSB imobiliar peste cei 10 HCD 58: revânzări rapide, onorariu-influență, offshore/paravan, proprietar interpus, credite multiple etc.) | important | `aml/indicatori.py` (`INDICATORI_GHID_IMOBILIAR`, `SemnaleIndicatori`); commit `d344d15` | ✅ IMPLEMENTAT |
| **BR-PJ** | **Beneficiar real lipsă la PJ = factor de risc** (neconsultat în registrul central ridică factorul „client", documentat ca motiv la „sporit") | mediu | `aml/risc.py` (`_beneficiar_real_lipsa`); commit `775b65c` | ✅ IMPLEMENTAT |
| **F1-SEC** | **Securitate cod nou** (registru/BIG): anti formula-injection CSV/XLSX, control-char, poison-data fail-soft (dosar otrăvit ≠ 500) | securitate | commit `902eea4`/`36c6d74`; `web/routers/registru.py` (`_pozitiv`, try/except ValidationError) | ✅ IMPLEMENTAT |
| **ROBUST-14/15** | **Robustețe runde 14–15** (DoS marginire `Field(max_length)` pe câmpuri AML+noi, suprafețe negative registru/BIG → fără 500) | robustețe | commit `913436b`/`f7a23ec`; `aml/models.py` `_MAX_NUME`, `esg.RiscIdentificat.observatie max_length` | ✅ IMPLEMENTAT |

---

## 2. 🔴 BLOCANTE (BLOC-1..7) — de rezolvat înainte de a duce un raport la bancă

| Cod | Descriere | Sev. | Stare verificată în cod | STATUS |
|---|---|---|---|---|
| **BLOC-1** = G1 / S-5 / F-02 / F-03 | **Cablarea ESG + CPE în RAPORT și UI.** | **B** | ✅ **ÎNCHIS.** `esg` importat în `generator.py:18`, randat de `_adauga_esg` (apelat la 1117); CPE+cod_postal randate (319/1030); dosar.html are 8 checkbox-uri + CPE + JS payload (1295–1298). | ✅ IMPLEMENTAT |
| **BLOC-2** = S-4 / G5 / F-09 | **Cablarea BIG în flux + integrare online + recipisă ca anexă.** Modul `big.py` (payload + recipisă) + **acțiune „pregătește pentru BIG" CABLATĂ** (router registru: `pregateste_big`, status per-rând pe `/registru`, endpoint `/api/dosar/{uid}/big` cu checklist lipsuri). LIPSEȘTE: integrarea online cu portalul BIG + atașarea recipisei ca anexă obligatorie în raportul .docx. | **B** | `big` importat în `web/routers/registru.py:18`; flux + checklist DONE (commit `7c97341`). Online + recipisă-anexă = NU (necesită manualul ANEVAR-BIG — vezi §6). | 🟡 ÎN CURS (flux ✅) + ⏳ PENDING (online + anexă, blocat pe manual) |
| **BLOC-3** = G3 | **Garda „cost ≠ abordare principală la garantare".** `assembler.py` acceptă tăcut `metoda="cost"` ca primară pe profil `GEV_520`, fără alertă (GEV 520 §31/§34 cer accept scris al creditorului). | **B** | `engine/validation.py` n-are `valideaza_metoda_vs_ghid`; `assembler.py` default `metoda="cost"` fără gardă. Neimplementat. | ⏳ PENDING |
| **BLOC-4** = G2 | **Tip „comercial" + abordarea prin venit accesibile din UI.** | **B** (pt. comercial) | ✅ **ÎNCHIS** — vezi §1 (BLOC-4/G2): dropdown-ul `tip_proprietate` expune „comercial" (`dosar.html:142`, comutare auto metodă→venit la `:929`) + `assembler.PROFIL_DUPA_TIP["comercial"] = COMERCIAL_INCHIRIAT` (`assembler.py:50`); commits `fcdd173` + `400da88`. Motor venit/DCF + structură per-tip deja DONE. | ✅ IMPLEMENTAT |
| **BLOC-5** = G4 / F-07 / S-2 | **Declarație conflict de interese tip EBA + plata necondiționată** (GEV 520 §81–82). Text de conformitate cu implicații legale. | **B** | Neimplementat în `generator.py`. | ⏸️ PARCAT-JURIST (text legal) |
| **BLOC-6** = S-2 / I-3 | **EDD risc ridicat: sursa fondurilor + a averii + aprobarea conducerii pentru PEP + monitorizare sporită.** **Scheletul de DATE + UI există** (`DosarAML.sursa_fonduri/sursa_avere/aprobare_conducere_superioara_pep/monitorizare_sporita` + câmpuri în `aml.html`). RĂMÂNE parcat: textul de declarație pe proprie răspundere a clientului + validarea juridică a fluxului EDD (Legea 129/2019 art. 17). | **B** | Model `aml/models.py:151–155` ✅; UI `aml.html:85–93` ✅ (commit `29639a1`). Text legal + validare jurist = parcat (AML = bucket C). | 🟡 ÎN CURS (model+UI ✅) / ⏸️ text-jurist |
| **BLOC-7** = S-1 | **Scopul evaluării ca factor de risc AML.** | **B** | ✅ **ÎNCHIS** — vezi §1 (S-1/BLOC-7): `risc.ScopEvaluare` + `serviciu.scop_aml_din_dosar`. | ✅ IMPLEMENTAT |

---

## 3. 🟠 IMPORTANTE — întăresc conformitatea

| Cod | Descriere | Sev. | STATUS | Note |
|---|---|---|---|---|
| S-3 / I-4 | **RBR (Registrul Beneficiarilor Reali) + fișă KYC + modalitate identificare BR.** Câmpuri model (`ClientPJ.consultat_rbr/nr_extras_rbr/data_extras_rbr`, `BeneficiarReal.modalitate_identificare`) **ȘI UI** (`aml.html`). | important | 🟡 ÎN CURS (model+UI ✅) / ⏸️ text-jurist | `aml/models.py:115–119,86`; `aml.html:68–79` (commit `29639a1`). Tratarea normativă BR-lipsă/PEP + corpul AML = parcat |
| I-5 | **Indicatorii suplimentari din ghid** (revânzări rapide, onorariu-influență, offshore, paravan) | important | ✅ IMPLEMENTAT | `aml/indicatori.py` (vezi §1) — **mutat din parcat**; 15 indicatori `ghid_imobiliar` |
| I-17 | **Versiuni AML actualizate** (HCD 62 + CFH 74/2025) + **politica GDPR ANEVAR oct. 2025** | important | ⏸️ PARCAT-JURIST | GDPR = DRAFT în `docs/politica-GDPR-draft.md` (fiecare § `[DECIZIE]` cere jurist); corp AML = parcat |
| G6 / F-06 | **Re-desemnarea utilizatorului** (raport pt alt scop ≠ utilizabil la garantare fără re-desemnare) | mediu | ⏳ PENDING | notă în termeni + checklist (`generator.py`) |
| F-08 | **Randarea câmpurilor existente** în descrierea fizică cap.4 (`structura`, `finisaje`, `deschidere` — există pe `Building` dar NU sunt randate) | mediu | ⏳ PENDING | efort mic; `report/generator.py` cap.4 (CPE/cod_postal DEJA randate; rămân structura/finisaje/deschidere) |
| G8 / I-12 / F-04 | **Analiza de piață structurată** (arie, fază ciclu, segment preț, tendință) cu back-stop determinist | mediu | 🟡 ÎN CURS | `generator._adauga_structura_piata` randează schelet structurat peste narativ (I-12 motor ✅); shell rămâne parțial narativ |
| I-16 | **Structura formală a dosarului de lucru** (4 secțiuni ANEVAR + integritate/retenție) | important | ⏳ PENDING | `dosare_fs.py` mapează ~1:1; lipsesc cele 4 secțiuni explicit |
| I-14 | **Reminder actualizare/revizuire anuală** (date client + norme interne) | important | ⏳ PENDING | flux UI |

> Notă: I-1, I-2, I-5, I-6, I-7, I-8, I-9, I-10, I-12(motor), I-15, I-18, I-19 sunt **DONE** — vezi §1.

---

## 4. ⏸️ PARCAT-JURIST — nu se finalizează autonom (decizii legale/produs)

| Cod | Descriere | De ce e parcat | Stare schelet |
|---|---|---|---|
| BLOC-5 (G4/F-07) | Declarație conflict de interese EBA + plata necondiționată | text de conformitate cu valoare juridică | nimic în cod |
| BLOC-6 (S-2/I-3) | EDD: text declarație client + validare flux | corp normativ AML — pending jurist | **model + UI ✅** (date colectabile) |
| S-3 / I-4 | RBR + fișă KYC + tratarea BR-lipsă/PEP (text normativ) | corp AML | **model + UI ✅** |
| I-17 (GDPR) | Politica GDPR ANEVAR oct. 2025 | `docs/politica-GDPR-draft.md` = DRAFT; fiecare `[DECIZIE]` cere jurist | draft doc |
| I-17 (AML) | Versiuni AML HCD 62 + CFH 74/2025 | corp AML | — |
| m-4 | Câmpuri identificare PJ/împuternicit/traducere + măsuri atenuare | corp AML | parțial în `ClientPJ` (`imputernicit`, `traducere_legalizata`) |

> **Regula de memorie (AML = bucket C):** NU se editează/commit TEXT juridic AML în foreground; loop-ul autonom îl deține (revert + re-aplică, pending jurist). Scheletul de DATE/UI (câmpuri colectabile, fără text normativ obligatoriu) a fost construit; declarațiile/normele rămân parcate.

---

## 5. ⏳ MINORE — ulterior / cazuri de nișă

| Cod | Descriere | STATUS |
|---|---|---|
| G9 / I-11 | Metode teren reziduală/parcelare/extracție/alocare (azi comparație EUR/mp + bonitare agricol în `land.py`) | ⏳ PENDING (nișă — teren de dezvoltare) |
| G11 | „A doua abordare formală" (pondere ~0) — DETECTATĂ acum prin §108 | ✅ IMPLEMENTAT (`reconciliation` §108) |
| G12 | Ierarhia datelor de intrare SEV 104 / SEV 230 ca metadată pe comparabile | ⏳ PENDING |
| G13 | Chirie peste piață (GEV 520 A6) — fără notă de risc | ⏳ PENDING |
| G14–G16 | PGA going-concern/OER, active epuizabile, coordonate Stereo 70 teren | ⏳ PENDING (nișă comercial/special) |
| G10 | Scopuri `vanzare`/`expropriere`/`aport` definite în `profil.py` dar lipsesc din dropdown | ⏳ PENDING |
| F-10 | Anexă cu desfășurătorul ajustărilor pe criterii | ⏳ PENDING |
| m-1 | Audit terminologic UI/raport vs. glosar + glosar in-app + disclaimer „nu e AVM" | ⏳ PENDING |
| m-5 | Criptare arhivă electronică (permisiunile 0o700/0o600 = no-op pe Windows) | ⏳ PENDING |

---

## 6. 📥 RESURSE LIPSĂ de descărcat (deblochează BLOC-2 + AML)

| Prioritate | Document | Deblochează |
|---|---|---|
| **blocant** | BIG — Manual de utilizare (`anevar.ro/images/documente/manual_utilizare_ad-3_0.pdf`) | BLOC-2 (integrare online + recipisă-anexă) |
| important | HCD 62 + CFH 74/2025 (formular KYC consolidat) | AML (parcat-jurist) |
| important | Indicele imobiliar ANEVAR (live) | I-18 (fallback offline deja DONE) |
| important | Politica de protecție a datelor ANEVAR oct. 2025 | GDPR (parcat-jurist) |

> WebFetch e blocat 403 pe anevar.ro — descărcare manuală / alt canal. **Sursa PdV ESG a fost deja procesată** (a alimentat `esg.py`, acum cablat).

---

## 7. ORDINEA RECOMANDATĂ (ce urmează)

1. **BLOC-3** (gardă cost≠principal) — gardă de validare, motor deja DONE; efort mic. *(BLOC-4 „comercial" în dropdown = ✅ închis azi — vezi §1.)*
2. **F-08** (randare structura/finisaje/deschidere în cap.4) — quick win, efort mic.
3. **BLOC-2** (BIG): atașarea recipisei ca anexă acum; integrarea online după descărcarea manualului ANEVAR.
4. **G6/F-06** (re-desemnare utilizator), **I-16** (structură dosar 4 secțiuni), **G8** (analiză piață structurată completă în raport).
5. **Parcat-jurist** (BLOC-5; finalizarea TEXTULUI EDD/RBR pe scheletul deja construit; AML HCD 62/CFH 74; GDPR): pe măsură ce Adi + juristul deblochează; NU autonom.
6. Minore (§5): oportunist, low-risk.

---

## 8. Funcționalități produs livrate (dincolo de conformitate)

> Piese de **valoare-produs** (UX / motor de descoperire) construite în paralel cu gap-urile normative. Nu apar în numărătoarea de conformitate (§0), dar sunt parte din livrabilul real verificat în cod.

| Funcționalitate | Descriere | Dovadă în cod |
|---|---|---|
| **Candidați salvați per-dosar** | Salvarea comparabilelor descoperite în „shortlist"-ul dosarului, înainte de importul în grilă; deduplicare + plafon anti-DoS (cele mai vechi cad). Disponibilă **inline în `dosar.html`** ȘI **standalone la `/descoperire`**. | `dosare_fs.py` (`salveaza_candidat`, `listeaza_candidati_salvati`, `_cale_candidati`, `MAX_CANDIDATI_SALVATI=500`); endpoint-uri `POST /api/dosar/{uid}/candidat-salvat` + `GET /api/dosar/{uid}/candidati-salvati`; `descoperire.html:597,725` |
| **50+50 la descoperire (fetch + paginare)** | Descoperirea aduce până la `max_candidati=50` per cerere, cu paginare în UI pentru a parcurge loturi suplimentare (50+50). Plafonul e mărginit server-side (`le=50`). | `web/schemas.py:95,125` (`max_candidati: Field(default=50, ge=1, le=50)`); `web/routers/descoperire.py:55,87`; `descoperire.html:534,539,546` (paginare) |
| **Extracție etaj apartament** | Etajul apartamentului extras din anunț (câmp structurat `Floor_no` sau regex „etaj 3"/„parter"/„3/5") și folosit ca driver de scoring la apartamente. | `discovery/orchestrator.py:209–213`; `discovery/ponderi.py:26` (`"etaj": 5`); `discovery/scoring.py:29` (`PRAG_ETAJ`) |
| **Hint-uri precompletare /grila** | Câmpurile grilei se precompletează din contextul dosarului (ex. suprafață teren subiect) cu hint vizual „precompletat cu…". | `web/templates/grila.html:48` (`supr-teren-hint` „precompletat cu suprafața teren”) |
| **Scoring recență / proximitate / segment** | Ajustări metodologice ADITIVE peste similaritatea de atribute (operaționalizează G7 / articole-piață): recența anunțului (grație 180z, prag 540z, penalizare max 30%), proximitatea (grație <1 km, prag ≥15 km) și segmentul de piață — calibrabile (euristici SEV 103 A10.7). | `discovery/scoring.py:32–42` (`RECENTA_*`, `PROXIMITATE_*`, `ScoreBreakdown.explicatie`) |
| **RUNDA 16 — robustețe** | Garde anti-DoS pe inputuri attacker-controlled: `RecursionError` prins la parsarea blob-urilor adânc imbricate (`__NEXT_DATA__` / JSON-LD), regex mărginite anti-**ReDoS** (truncare înainte de regex, cuantificatori mărginiți), plafon `max_candidati` (server-side `le=50`). | `importers/url_parser.py:30,109,175,377,404,422,436`; `web/schemas.py:95,125` |

---

**Documente-sursă:** `docs/SEV-2025-gap-implementare.md` · `docs/analiza-anevar/00-SINTEZA.md` · `docs/audit-report-completeness-2026-06-11.md` · `docs/GEV520-2025-crosscheck.md` · `docs/politica-GDPR-draft.md`.
