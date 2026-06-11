# ROADMAP DE IMPLEMENTARE — conformitate consolidată (status unic)

> **Scop:** un SINGUR tabel de adevăr peste TOATE gap-urile de conformitate identificate, cu **STATUS verificat în cod** (la `master` curent, 2026-06-11). Consolidează:
> - `docs/SEV-2025-gap-implementare.md` (gap-uri G1–G17, SEV 2025 / GEV 520)
> - `docs/analiza-anevar/00-SINTEZA.md` (gap-uri S-1..S-5, I-1..I-19, m-1..m-6 din 7 analize tematice ANEVAR)
> - `docs/audit-report-completeness-2026-06-11.md` (findings F-01..F-10, raport GEV 520)
> - `git log` recent (ce s-a implementat efectiv: commit-urile `ab7ad30`→`41fdf23`).
>
> **Metodologie status:** fiecare „✅ IMPLEMENTAT" e verificat în codul de pe branch (modul/funcție existentă). „🟡 ÎN CURS" = logica există dar nu e cablată end-to-end (raport+UI). „⏳ PENDING" = neînceput, decizie tehnică. „⏸️ PARCAT-JURIST" = blocat pe decizie legală/produs (nu se implementează autonom).
>
> **Legendă STATUS:** ✅ IMPLEMENTAT · 🟡 ÎN CURS (parțial cablat) · ⏳ PENDING · ⏸️ PARCAT-JURIST
> **Severitate:** **B** = blocant · **M/important** = mediu · **m/minor** = minor

---

## 0. SUMAR EXECUTIV (numărătoare)

| Grup | ✅ Done | 🟡 În curs | ⏳ Pending | ⏸️ Parcat-jurist | Total |
|---|---|---|---|---|---|
| Blocante rămase | — | 2 | 1 | 3 | 6 |
| Importante | 13 | 1 | 5 | 4 | 23 |
| Minore | 2 | — | 5 | 1 | 8 |
| **TOTAL** | **15** | **3** | **11** | **8** | **37** |

> **Interpretare:** Motorul de calcul + AML-backend + scheletul de raport sunt **majoritar DONE**. Ce rămâne se concentrează pe (a) **cablarea ESG/BIG în raport+UI** (module deja scrise, neconectate), (b) **integrarea online BIG** (necesită manual ANEVAR), (c) **deciziile legale AML/EDD/RBR/GDPR** care nu se implementează autonom.

---

## 1. ✅ DEJA IMPLEMENTAT pe master (verificat în cod) — NU se repară

| Cod | Descriere | Sev. | Dovadă în cod | STATUS |
|---|---|---|---|---|
| I-6 / G-Q1 / F— | **QC pre-emitere** (checklist verificare internă a calității: comparabile, CMBU, tip valoare, documente, coerență, adecvare + gate emisibilitate + endpoint live + panou UI) | important | `calitate.py` (`verifica_calitate`, `emisibil`, `blocaje`); cablat în `web/routers/evaluare.py` + `curent.py` | ✅ IMPLEMENTAT |
| I-1 / I-2 | **Registru rapoarte de evaluare** (~13 câmpuri, export CSV/XLSX, export audit per-dosar) + **nr. lucrare secvențial AAAA/NNNN** (alocare atomică) | important | `registru/registru.py` (`randuri`, `csv_text`, `xlsx_bytes`, câmp `_verificator`), `registru/numar.py` (`aloca`), router `registru.py` | ✅ IMPLEMENTAT |
| I-15 / m-6 | **Disclaimer AML real** (antet corectat: reflectă screening-ul REAL „posibilă potrivire, verificată manual" + avertisment liste goale/expirate) | important/minor | `aml/documente.py:36–43`, `aml/liste.py` | ✅ IMPLEMENTAT |
| I-7 | **Rata de capitalizare derivată din piață** (4 metode: vânzare-închiriere, comparabile, build-up) + **validare plauzibilitate** + sursă documentată | important | `engine/venit.py` (`rata_din_vanzare_inchiriere`, `rata_din_comparabile`, `rata_build_up`, `valideaza_rata_capitalizare`) | ✅ IMPLEMENTAT |
| I-8 | **Defalcare OPEX** (poziții service-charge) + distincția chirie brută/netă | important | `engine/venit.py` (`CheltuieliExploatare.total`, `DateVenit`) | ✅ IMPLEMENTAT |
| I-19 / G— | **Valoare terminală DCF** Gordon + exit-cap (era sumă manuală) | important | `engine/venit.py` (`valoare_terminala_gordon`, `valoare_terminala_exit_cap`, `evalueaza_dcf`, `abordare_dcf`) | ✅ IMPLEMENTAT |
| G17 | **DCF: rata de actualizare cu sursă + bandă de plauzibilitate** (corelare tip venit↔tip rată) | minor | `engine/venit.py` (`valideaza_rata_actualizare`); commit `7865213` | ✅ IMPLEMENTAT |
| I-9 / I-10 / I-12 / m-2 / m-3 | **Validare comparabile îmbogățită** (omogenitate, recență/proximitate, ofertă→tranzacție) + **analiză piață structurată** + **CMBU** + anti-contaminare notarial + supra-îmbunătățire | important/minor | `engine/validation.py`, `engine/market.py`, `calitate.py` (`_item_cmbu`); commit `3820934` | ✅ IMPLEMENTAT |
| I-18 / B2-IND-OFF | **Indice imobiliar ANEVAR — tabel offline** (fallback offline-first când pagina live e 403/indisponibilă) | important | `indice_anevar.py` (`INDICE_OFFLINE`, `_tabel_offline`, `SURSA_OFFLINE`); commit `a85fdd2` | ✅ IMPLEMENTAT |
| N4 | **Consistență suprafață subiect ≤0** respinsă uniform în toate 3 grilele (casă/teren/chirii → 422) | mediu | `web/schemas.py` (`Field(gt=0)`); commit `a6163c7` | ✅ IMPLEMENTAT |
| F1-1 | **/dosare dead-end → redirect** la `/incepe#salvate` (o singură sursă de adevăr) | UX | `web/routers/pagini.py:130–134`; commit `3cea2e9` | ✅ IMPLEMENTAT |
| S-4 (parțial) | **Modul big.py** — pregătire payload export raport→BIG (câmpuri minime, nomenclatoare tip proprietate, mapper, checklist câmpuri lipsă, RecipisaBIG + rectificative + audit trail) | blocant | `big.py` (`CampuriMinimeBIG`, `construieste_payload_big`, `valideaza_campuri_minime`, `emite_recipisa`); commit `8991567` | ✅ IMPLEMENTAT (logica) — vezi BLOC-2 pentru cablare/online |
| S-5 / G1 (parțial) | **Modul esg.py** — riscuri fizice ESG (catalog 8 riscuri PdV ANEVAR, nomenclator autorități-sursă, generator secțiune cu disclaimer de necuantificare, checklist) | blocant | `esg.py` (`genereaza_sectiune_esg`, `checklist_riscuri_fizice`); commit `792a72f` | ✅ IMPLEMENTAT (logica) — vezi BLOC-1 pentru cablare în raport+UI |
| G7 / F-03 / S-5 | **Câmpuri model** noi: `cod_postal`, `riscuri_fizice`, `certificat_energetic (CPE)` în `meta.py` + `LandComparable.sursa` | mediu | `models/meta.py`, `models/comparable.py`; commit `41fdf23` | ✅ IMPLEMENTAT (câmpuri) — randarea în raport = BLOC-1 |
| 0-SOLID | **Fundație SEV 2025** (3 abordări + reconciliere fără medie aritmetică, min 3 comparabile, depreciere justificată, SEV 450 = CIB, sursa definiției valorii, declarații SEV 100, BIG condiționat ANAF, factorii A5 garanție, inspecție amploare+însoțitor) | — | `engine/abordari.py`, `engine/reconciliation.py`, `engine/validation.py`, `engine/cost.py`, `report/generator.py` | ✅ IMPLEMENTAT |

---

## 2. 🔴 BLOCANTE RĂMASE (B) — de rezolvat înainte de a duce un raport la bancă

| Cod | Descriere | Sev. | Ce mai lipsește (verificat în cod) | STATUS |
|---|---|---|---|---|
| **BLOC-1** = G1 / S-5 / F-02 / F-03 | **Cablarea ESG + CPE în RAPORT și UI.** Modulul `esg.py` și câmpurile (`riscuri_fizice`, `certificat_energetic`) EXISTĂ, dar **nu sunt importate** în `report/generator.py` și nu apar în UI. Raportul GEV 520 ed. 2025 cere secțiune ESG + redarea certificatului energetic. | **B** | `grep` confirmă: `esg` neimportat în orice modul; `generator.py` nu referă `riscuri_fizice`/`CPE`/`cod_postal`. Commit `792a72f` notează explicit „NU exista wiring in generator/UI (follow-up)". | 🟡 ÎN CURS |
| **BLOC-2** = S-4 / G5 / F-09 | **Cablarea BIG în flux + integrare online + recipisă ca anexă.** Modulul `big.py` (payload + recipisă) EXISTĂ, dar **nu e importat** nicăieri; nu există integrare online cu portalul BIG, iar recipisa nu e atașată ca anexă obligatorie în raport. Necesită **manualul ANEVAR-BIG** (descărcat manual — vezi §5). | **B** | `grep` confirmă `big` neimportat; commit `8991567` notează „NU implementeaza integrarea online cu portalul BIG". | 🟡 ÎN CURS (logica) + ⏳ PENDING (online, blocat pe manual) |
| **BLOC-3** = G3 | **Garda „cost ≠ abordare principală la garantare".** `assembler.py` acceptă tăcut `metoda="cost"` ca primară pe profil `GEV_520`, fără alertă (GEV 520 §31/§34 cer accept scris al creditorului). | **B** | `engine/validation.py` n-are `valideaza_metoda_vs_ghid`. Neimplementat. | ⏳ PENDING |
| **BLOC-4** = G2 | **Tip „comercial" + abordarea prin venit accesibile din UI.** Motorul de venit/DCF e DONE (vezi §1, I-7/I-8/I-19), dar dropdown-ul `tip_proprietate` din `dosar.html` nu expune „comercial" și `PROFIL_DUPA_TIP` nu-l mapează; grila de chirii nu alimentează automat VBP. | **B** (pt. comercial) | Motor ✅ / UI+mapare ⏳. | ⏳ PENDING |
| **BLOC-5** = G4 / F-07 / S-2 | **Declarație conflict de interese tip EBA + plata necondiționată** (GEV 520 §81–82). Declarația de conformitate acoperă independența SEV 100, dar nu menționează EBA/conflict de interese distinct, nici plata necondiționată de acordarea creditului. **Text de conformitate cu implicații legale.** | **B** | Neimplementat în `generator.py`. | ⏸️ PARCAT-JURIST (text legal) |
| **BLOC-6** = S-2 / I-3 | **EDD risc ridicat: sursa fondurilor + a averii + aprobarea conducerii pentru PEP** + **declarație pe proprie răspundere client** (Legea 129/2019 art. 17). | **B** | Motor AML n-are colectare sursă-fonduri/avere; corp normativ AML = bucket parcat. | ⏸️ PARCAT-JURIST (AML — loop autonom + jurist) |
| **BLOC-7** = S-1 | **Scopul evaluării ca factor de risc AML** (lichidare/insolvență/executare = risc; garantare = redus). | **B** | `aml/risc.py` nu folosește scopul ca dimensiune de risc. | ⏸️ PARCAT-JURIST (AML) |

---

## 3. 🟠 IMPORTANTE — întăresc conformitatea (nu blochează un dosar rezidențial simplu)

| Cod | Descriere | Sev. | STATUS | Note |
|---|---|---|---|---|
| S-3 / I-4 | **RBR (Registrul Beneficiarilor Reali) în UI + fișă KYC**; BR lipsă la PJ → avertisment de risc; PEP cu categorie/tip/dată | important | ⏸️ PARCAT-JURIST | câmp în model, absent din UI/KYC; corp AML = parcat |
| I-5 | **Indicatorii din ghid** neacoperiți de cei 10 din HCD 58 (revânzări rapide, onorariu-influență, offshore, paravan) | important | ⏸️ PARCAT-JURIST | `aml/indicatori.py` (AML) |
| I-17 | **Versiuni AML actualizate** (HCD 62 + CFH 74/2025, oct. 2025) + **politica GDPR ANEVAR oct. 2025** | important | ⏸️ PARCAT-JURIST | GDPR = DRAFT în `docs/politica-GDPR-draft.md` (fiecare § marcat `[DECIZIE]` cere jurist) |
| G6 / F-06 | **Re-desemnarea utilizatorului** (raport pt alt scop ≠ utilizabil la garantare fără re-desemnare + modificare BIG) | mediu | ⏳ PENDING | notă în termeni + checklist (`generator.py`) |
| F-01 | **Valoarea finală redată în litere** (cuvinte) — uzanță fermă, așteptată la verificarea bancară | mediu (quick win) | ⏳ PENDING | efort mic, impact mare; `report/generator.py` |
| F-08 | **Randarea câmpurilor existente** în descrierea fizică cap.4 (`structura`, `finisaje`, `ac`, `deschidere`, `clasa_energetica`) — date introduse dar pierdute în raport | mediu | ⏳ PENDING | efort mic; `report/generator.py` cap.4 |
| G8 / I-12 / F-04 | **Analiza de piață structurată** (aria de piață, fază ciclu cartier, segment preț, tendință) cu back-stop determinist — azi narativ AI/placeholder | mediu | 🟡 ÎN CURS | parțial acoperit de îmbogățirea `market.py` (I-12 done la nivel motor); shell raport rămâne narativ |
| I-16 | **Structura formală a dosarului de lucru** (4 secțiuni ANEVAR + integritate/retenție) | important | ⏳ PENDING | `dosare_fs.py` mapează ~1:1; lipsesc cele 4 secțiuni explicit |
| I-14 | **Reminder actualizare/revizuire anuală** (date client + norme interne) — termen calculat, fără flux/reminder | important | ⏳ PENDING | flux UI |

> Notă: I-1, I-2, I-6, I-7, I-8, I-9, I-10, I-11(parțial), I-12(motor), I-15, I-18, I-19 sunt **DONE** — vezi §1.

---

## 4. ⏸️ PARCAT-JURIST — nu se implementează autonom (decizii legale/produs)

| Cod | Descriere | De ce e parcat |
|---|---|---|
| BLOC-5 (G4/F-07) | Declarație conflict de interese EBA + plata necondiționată | text de conformitate cu valoare juridică |
| BLOC-6 (S-2/I-3) | EDD: sursa fondurilor/averii + aprobare conducere PEP + declarație client | corp normativ AML — deținut de loop-ul autonom + validare jurist |
| BLOC-7 (S-1) | Scopul evaluării ca factor de risc AML | logică AML cu implicații normative |
| S-3 / I-4 | RBR + fișă KYC + tratarea BR-lipsă/PEP | corp AML |
| I-5 | Indicatori suplimentari de risc din ghid | corp AML |
| I-17 (GDPR) | Politica GDPR ANEVAR oct. 2025 (aliniere draft) | `docs/politica-GDPR-draft.md` = DRAFT; fiecare `[DECIZIE]` cere jurist |
| I-17 (AML) | Versiuni AML HCD 62 + CFH 74/2025 | corp AML |
| m-4 | Câmpuri identificare PJ/împuternicit/traducere + măsuri atenuare | corp AML |

> **Regula de memorie (AML = bucket C):** NU se editează/commit text juridic AML în foreground; loop-ul autonom îl deține (revert + re-aplică, pending jurist). Aici e doar inventariat ca PARCAT.

---

## 5. ⏳ MINORE — ulterior / cazuri de nișă

| Cod | Descriere | STATUS |
|---|---|---|
| G9 / I-11 | Metode teren reziduală/parcelare/extracție/alocare (azi doar comparație EUR/mp în `land.py`) | ⏳ PENDING (nișă — teren de dezvoltare) |
| G11 | „A doua abordare formală" (pondere ~0) nu e detectată | ⏳ PENDING |
| G12 | Ierarhia datelor de intrare SEV 104 / SEV 230 ca metadată pe comparabile | ⏳ PENDING |
| G13 | Chirie peste piață (GEV 520 A6) — fără notă de risc | ⏳ PENDING |
| G14–G16 | PGA going-concern/OER, active epuizabile, coordonate Stereo 70 teren | ⏳ PENDING (nișă comercial/special) |
| G10 | Scopuri `vanzare`/`expropriere`/`aport` definite în `profil.py` dar lipsesc din dropdown | ⏳ PENDING |
| F-10 | Anexă cu desfășurătorul ajustărilor pe criterii | ⏳ PENDING |
| m-1 | Audit terminologic UI/raport vs. glosar (Scop→Utilizare desemnată, comparație→abordarea prin piață) + glosar in-app + disclaimer „nu e AVM" | ⏳ PENDING |
| m-5 | Criptare arhivă electronică (permisiunile 0o700/0o600 = no-op pe Windows) | ⏳ PENDING |

---

## 6. 📥 RESURSE LIPSĂ de descărcat (deblochează BLOC-1/BLOC-2 + AML)

| Prioritate | Document | Deblochează |
|---|---|---|
| **blocant** | BIG — Manual de utilizare (`anevar.ro/images/documente/manual_utilizare_ad-3_0.pdf`) | BLOC-2 (integrare online + câmpuri export) |
| **blocant** | PdV ANEVAR — aprecierea riscurilor fizice la garantare | BLOC-1 (ESG — deja folosit ca sursă pt `esg.py`) |
| important | HCD 62 + CFH 74/2025 (formular KYC consolidat) | AML (parcat-jurist) |
| important | Indicele imobiliar ANEVAR (live) | I-18 (fallback offline deja DONE) |
| important | Politica de protecție a datelor ANEVAR oct. 2025 | GDPR (parcat-jurist) |

> WebFetch e blocat 403 pe anevar.ro — descărcare manuală / alt canal.

---

## 7. ORDINEA RECOMANDATĂ (ce urmează)

1. **BLOC-1** (cablare ESG + CPE în raport+UI) — modulul e scris, e doar wiring; cel mai mare gol normativ 2025.
2. **F-01** (valoare în litere) + **F-08** (randare câmpuri existente) — quick wins, efort mic, impact bancă.
3. **BLOC-3** (gardă cost≠principal) + **BLOC-4** (comercial+venit în UI) — garduri/UI, motor deja DONE.
4. **BLOC-2** (BIG): cablare flux + recipisă anexă acum; integrare online după descărcarea manualului ANEVAR.
5. **G6/F-06** (re-desemnare utilizator), **I-16** (structură dosar 4 secțiuni), **G8** (analiză piață structurată în raport).
6. **Parcat-jurist** (BLOC-5/6/7, AML, GDPR): pe măsură ce Adi + juristul deblochează; NU autonom.
7. Minore (§5): oportunist, low-risk.

---

**Documente-sursă:** `docs/SEV-2025-gap-implementare.md` · `docs/analiza-anevar/00-SINTEZA.md` · `docs/audit-report-completeness-2026-06-11.md` · `docs/GEV520-2025-crosscheck.md` · `docs/politica-GDPR-draft.md`.
