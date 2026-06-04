# Jurnal de sesiune — Aplicație de asistență la evaluare ANEVAR

**Proiect:** asistent desktop (local, `.exe`) pentru rapoarte de evaluare casă + teren, garantarea
creditului, conform ANEVAR. **Pachet:** `evaluare-anevar/` (Python, FastAPI, PyInstaller).
**Creat:** 2026-06-03. **Actualizare:** orară (vezi secțiunea „Actualizări" la final).

> Acest jurnal rezumă tot ce s-a discutat și făcut în sesiune. Documentația strategică detaliată:
> `docs/plan-master.md`, `docs/module-aplicatie.md`, `docs/roadmap-anevar.md`, `docs/superpowers/specs/`,
> `docs/superpowers/plans/`, `docs/instructiuni-evaluator.md`.

---

## 1. Motorul de evaluare — teren și casă (validat pe dosare reale GBF)

- **`engine/land.py`** — grila de teren (EUR/mp). Descoperire cheie din grilele reale: metodologia are
  **două etape** (nu compunere secvențială pură): **tranzacție** (ofertă→tranzacție, drept, finanțare,
  condiții vânzare, cheltuieli, condițiile pieței) = secvențial → preț de bază; **proprietate**
  (localizare, acces, suprafață, deschidere…) = **aditiv** pe bază: `final = bază × (1 + Σ%)`. Selecția
  = ajustare brută minimă pe etapa de proprietate (oferta NU se contorizează).
  - Regresie: reproduce exact **Maneciu 44.000 / Brașov 78.000 / Bușteni 34.000 / Breaza 67.000 €**
    (toate 12 comparabile).
- **`engine/market.py`** — grila de casă rescrisă pe **preț total** (nu €/mp), aceleași două etape,
  arie utilă tratată ca ajustare valorică EUR. Valoare = total corectat al comparabilului ales.
  Regresie validată pe **3 dosare reale** (Bușteni, Maneciu, Brașov) — reproduse exact.
- `engine/cost.py` (CIN segregat IROVAL), `engine/reconciliation.py` (+ alocare construcții = proprietate − teren).
- `Adjustment.etapa` (tranzactie|proprietate) adăugat în model.

## 2. Grila UI + raportul GBF + narativ AI

- **Pagina `/grila`** — tabele editabile teren + casă; pre-populare casă din descoperire; buton „➕ grilă"
  pentru pre-populare teren din descoperirea de teren.
- **Raport `.docx`** (`report/generator.py`) — shell GBF complet: copertă, scrisoare de transmitere,
  declarație de conformitate, **termeni de referință**, 7 capitole SEV, **alocarea valorii**,
  **GEV 520**, anexe (foto + documente), semnătură. Valori formatate (2 zecimale / separator mii) +
  **echivalent LEI** la curs BNR.
- **Narativ AI** (`ai/narrative.py`) — per capitol, client injectabil (Anthropic/Perplexity),
  anonimizare GDPR înainte de apel, curățare text (citații/markdown). Acoperă și „Ipoteze" și „GEV 520".
- **Mod adnotări demo** — note de proveniență sub fiecare secțiune (calculat/extras/AI/exemplu/placeholder),
  buton „Raport cu note (demo)" + endpoint `?demo=1`.
- **Foto + documente** — upload în wizard → Anexa 2 (foto) / Anexa 3 (documente cadastrale).

## 3. Descoperire comparabile (casă + teren)

- `discovery/` + `importers/url_parser.py` — căutare portal (imobiliare/storia) → parsare → extragere →
  scor explicat → rank.
- **Bug-uri reale prinse de user și reparate:**
  - terenul din anunț nu apărea → propagat în `CandidateResult` + UI;
  - descrierea storia (cu specs) era în `__NEXT_DATA__`, nu în HTML-ul randat → `extrage_descriere`
    citește acum `ad.description` (LLM primește textul complet);
  - caracteristici structurate (an, încălzire, material) extrase din storia (`target`) și imobiliare
    (regex „Etichetă: valoare").
- **Descoperire teren** (`descopera_teren` + `/api/descopera-teren`) — €/mp + relevanță pe suprafață;
  verificat live pe Breaza.

## 4. Conectivitate date externe

- **Curs BNR** (`curs_bnr.py` + `/api/curs-bnr` + buton wizard) — feed public XML; verificat live.
- **Indicele imobiliar ANEVAR** (`indice_anevar.py` + `/api/indice-anevar` + buton grilă) — date publice
  (Google Charts în pagină), variații %/mp pe orașe; pentru ajustarea „condițiile pieței".

## 5. Conformitate standarde (din textul oficial SEV 2025)

- **SEV ediția 2025** (HCN 2/2025, în vigoare 1 iulie 2025) citată în declarații.
- **Numerotare corectată:** tip valoare = **SEV 102** (era 104); raportare = **SEV 106**; termeni = **SEV 101**.
- **GEV 520** — secțiunea de risc include factorii obligatorii **A5 (a–d)**, ipoteze speciale/vânzare
  forțată (A4), independență (A3), ipoteza transfer liber (A8), înregistrare BIG (§7).
- **SEV 101 (16 elemente) + SEV 106 (18 elemente)** — termenii de referință completați, inclusiv
  **factori ESG (mediu/social/guvernanță)** — element NOU obligatoriu în 2025.

## 6. Module noi implementate (schelete TDD)

- **`audit/`** — jurnal append-only înlănțuit prin hash (tamper-evident) + snapshot + **validare
  încrucișată** (cablată în `/api/evaluare`) + export `/api/evaluare/{id}/audit.txt`. 9 teste.
- **`ingestie/`** — OCR (PDF via fitz) + extractoare CF/releveu/plan/CPE (regex) + VLM injectabil;
  endpoint `/api/ingestie` + wiring în wizard (pre-completare câmpuri). 7 teste.
- **`aml/`** — modul complet de conformitate Legea 129/2019 (vezi §12).

## 7. Documentație strategică

- **`docs/plan-master.md`** — viziune + stadiu + **model de sisteme actualizat (6 sisteme)**: agent
  autonom → asistent cu om-în-buclă; ecosistem ANEVAR explicit; S6 Distribuție nou.
- **`docs/module-aplicatie.md`** — maparea modulelor pe cele 5 sisteme inițiale.
- **`docs/roadmap-anevar.md`** — Now/Next/Later (informat de cercetarea anevar.ro).
- **Spec-uri** (`docs/superpowers/specs/`): AML, BIG, ingestie, ANCPI, audit.
- **`docs/instructiuni-evaluator.md`** — ghid de pornire pentru evaluator (SmartScreen, AI opțional, GDPR).

## 8. Pachet de review (pentru evaluator)

- `docs/prezentare-pentru-evaluator.md` — sursă NotebookLM (recomandat format **Explainer**).
- `docs/prezentare-aplicatie.pptx` — 12 slide-uri (QA vizual cu subagent).
- `docs/exemplu-raport-breaza.docx` — raport real (subiect Breaza de Sus + 3 comparabile reale).

## 9. Cadru legal AML (din textele oficiale adăugate de user)

Citite: **Legea 129/2019**, **Normele Ord. ONPCSB 37/2021**, **HCD 58/2023**, **HCD 74/2022** (studii
de piață), model norme interne. Rezultat:
- **Plan complet de implementare** `docs/superpowers/plans/2026-06-03-modul-aml-129-2019-plan.md`
  (6 faze TDD, ancorat în articole).
- Praguri exacte: beneficiar real **>25%**, numerar **10.000 €**, PEP **+12 luni**, retenție **5 ani**,
  raport numerar **3 zile lucrătoare**; curs BNR la data tranzacției; **PFA exceptat** de persoana
  desemnată; **rapoartele ONPCSB separate** de dosar (tipping-off).
- AML trece de la „blocat juridic" la **„plan complet, definit"** (rămâne validare juridică finală +
  liste live + formularistica ONPCSB).
- HCD 74: anunțurile = oferte „neajustate, neverificate" → întărește disclaimer-ul pe comparabile.

## 12. Modul AML implementat (`aml/`) — Legea 129/2019 (6 faze TDD, 70 teste)

Planul din §9 a fost **executat integral**, TDD, în 6 faze (fiecare comisă separat):
- **Faza 0** — `constante.py` (praguri/termene cu articol sursă), `models.py` (PersoanaFizica,
  BeneficiarReal, StatutPEP, ClientPF/PJ, FactorRisc, EvaluareRisc, DosarAML), `incadrare.py`
  (PFA exceptat de persoana desemnată — Norme art. 7; audit independent 2-din-3 — Norme art. 9).
- **Faza 1** — `risc.py`: 4 factori ponderați → scor → categorie (redus/standard/sporit) + nivel
  măsuri; **reguli HARD** care forțează „sporit"/EDD (PEP efectiv prin regula 12 luni art. 3(6),
  listă sancțiuni, țară risc înalt, tranzacție complexă, relație la distanță — art. 17).
- **Faza 2** — `indicatori.py`: cei **10 indicatori** HCD 58 art. 6(10) ca checklist → propunere RTS;
  `raportare.py`: prag RTN 10.000 €, conversie EUR/LEI la curs BNR, termen RTN +3 zile lucrătoare,
  suspendare +24h prorogată, anti-fragmentare 15.000 € pe fereastră glisantă, `RaportRTN`/`RaportRTS`
  cu avertisment **tipping-off** (art. 38).
- **Faza 3** — `documente.py` (python-docx): norme interne **7 capitole** (Norme art. 8(1) a–g),
  evaluare de risc, **decizie de desemnare** (doar societate; refuzată pentru PFA), fișă KYC (PF/PJ +
  beneficiari reali + PEP), draft RTN, draft RTS.
- **Faza 4** — `serviciu.py` (orchestrare risc+indicatori+screening+documente), `liste.py` (liste
  externe injectabile + screening tolerant la diacritice/similaritate + `data/liste.json` placeholder),
  `store.py` (**StoreAML separat** de dosar, retenție 5 ani). Endpoints `/api/aml/evalueaza` +
  generare `.docx`, pagina `/aml` + link în wizard. RTS/RTN persistate într-un director confidențial.
- **Faza 5** — suită **269 teste verzi**; smoke 6 documente; **exe reîmpachetat** (spec include
  `aml/data`) și verificat live: PJ cu PEP → sporit + RTS; norme-interne.docx 37 KB; `/aml` → 200.

Rămâne extern: formularistica electronică ONPCSB (transmiterea o face evaluatorul pe rapoarte.onpcsb.ro),
listele live (sancțiuni/PEP-ANI/țări) de reîmprospătat, validarea juridică finală a textelor.

## 10. Decizii și principii stabilite

- **Om-în-buclă** (AI propune, evaluatorul decide) — din rațiuni de răspundere profesională (GEV 520) + GDPR.
- **GDPR-first** — date personale anonimizate înainte de orice apel extern.
- **Validare pe dovezi** — motoarele validate pe dosare reale GBF, nu pe presupuneri.
- **Clienți injectabili** (AI, fetcher, viitor BIG/ANCPI/VLM) → testabil offline.
- **TDD + rebuild + smoke** la fiecare modul.
- **Securitate:** cheia Perplexity NU se distribuie cu exe-ul; `.env` gitignored.
- **Wizard — navigare liberă, FĂRĂ validare între pași** (decizie user, 2026-06-04): se poate sări la
  orice pas (stepper clickabil); nu se blochează avansarea pentru câmpuri lipsă. A NU se reintroduce.

## 11. Stare curentă

- **269 teste verzi**, exe funcțional reîmpachetat (include `aml/data`).
- Tot ce e „cod pur" fără dependențe externe = implementat, **inclusiv modulul AML complet** (§12).
- Rămas blocat extern: `big/`, `ancpi/` (acces ANEVAR/ANCPI), AML — doar **listele live** + transmiterea
  electronică ONPCSB + validarea juridică finală, exe semnat (certificat), catalog IROVAL (plătit).

---

## Actualizări (orare)

> Regulă: se adaugă o intrare **doar dacă există ceva nou** de consemnat în ultima oră. Dacă nu e
> nimic nou, nu se scrie nimic.

### 2026-06-03 — jurnal creat
Sinteza completă a sesiunii (secțiunile 1–11 de mai sus). Ultimul livrat: planul de implementare AML
ancorat în Legea 129/2019 + Norme 37/2021 + HCD 58. Programată actualizarea orară a acestui jurnal.

### 2026-06-04 — modul AML implementat integral
Executat planul AML, TDD, 6 faze (vezi §12 nou): `constante/models/incadrare`, `risc`, `indicatori/
raportare`, `documente` (.docx), `serviciu/liste/store` + endpoints `/api/aml/*` + pagina `/aml`,
verificare. **+70 teste AML** (suita totală 199 → **269 verzi**). Exe reîmpachetat (spec include
`aml/data`) și verificat live. AML trece de la „plan complet" la **„implementat (cod pur)"**; rămân
externe doar listele live, formularistica electronică ONPCSB și validarea juridică.

### 2026-06-04 — accesibilitate WCAG 2.1 AA (faza 1)
Audit + fixuri pe `/wizard`, `/aml`, `/grila`, `/descoperire`: asociere `label`↔control (53
controale), `aria-label` pe controale fără etichetă, mesaje de stare anunțate (`role="status"`/
`aria-live`), bară de progres `role="progressbar"`, mutare focus pe pas la navigare, landmark-uri
`<main>`/`<nav>`, `alt` pe upload, contrast bară progres (2.56→4.58:1), `<th scope>` în grilă.
**Bug-fix colateral:** helper `$` lipsă în `grila.html` (butoanele „Indice ANEVAR"/„Caută terenuri"
erau nefuncționale). +11 teste (`test_web_a11y.py`); plan faza 2 în `docs/plan-accesibilitate.md`.
Exe reîmpachetat și verificat (4 pagini → 200). Suita: **280 verzi**.

### 2026-06-04 — redesign vizual „Cadastru" (frontend-design)
Sistem de design unitar `templates/_design.css`, injectat prin Jinja `{% include %}` în toate cele
6 pagini (zero CDN — **doar fonturi de sistem**, rulează în `.exe` offline). Estetică de registru
cadastral/topograf: pergament cald, cerneală bleumarin, **sienna de topograf** + verde cadastral,
linii de alamă; serife de document (Constantia/Cambria) + Segoe UI; cifre tabulare. Bandă-antet
tricoloră, kicker de marcă pe titlu, grilă cartografică de fundal, carduri-pas cu margine de registru,
bară de progres sienna→auriu, tabele-registru, pastile de risc, butoane sienna. QA vizual cu
preview (wizard/grilă/AML). Păstrează toată structura + accesibilitatea. Exe reîmpachetat și verificat
live (CSS livrat din bundle, offline). Suita: **280 verzi**.

### 2026-06-04 — wizard: stepper numerotat clickabil
La cererea userului, refăcută logica pașilor: bara de progres + „Pas X/Y" înlocuite cu un **stepper
cu 5 pași etichetați** (Adresă · Subiect · Comparabile · Calcul · Raport), stări făcut(verde)/
activ(sienna)/următor, **clickabil** pentru salt direct (`mergiLa`), conectori care se umplu.
Corectată inconsecvența: „Înainte" se dezactivează la ultimul pas. Accesibil (aria-current=step,
etichetă sr-only role=status, focus pe titlu, tastatură). Stil în `_design.css`; test actualizat
(stepper în loc de progressbar). Exe reîmpachetat și verificat. Suita: **280 verzi**.

### 2026-06-04 — wizard: bara de sus reorganizată
Eticheta „Alternative:" grupa greșit toate cele 4 linkuri ca alternative la wizard (artefact istoric).
Separate: **„Instrumente:"** (descoperire · grilă · AML — complementare) și **„Vizualizare alternativă:"**
(formular clasic — singura cu adevărat alternativă). Exe reîmpachetat.

### 2026-06-04 — identitate evaluator persistentă (B3) + decizii
**B3 făcut:** numele + legitimația evaluatorului se cer la Pas 1 și se **rețin între sesiuni**
(`localStorage["evaluator"]` separat de dosar — supraviețuiește la „Reset dosar"), pre-completate la
fiecare deschidere, editabile. +1 test; verificat live + smoke exe (281 teste). **B1 (export PDF
in-app): decis „nu e cazul"** (rămâne Word→PDF). Liste de lucru noi: `docs/taskuri-ramase.md`.

### 2026-06-04 — critica de design + plan UI/accesibilitate consolidat
Rulat `design-critique` pe app (preview live). Findings cheie: `/result` prea minimal (valoare
neevidențiată, `316000.0000` neformatat, descărcare ca link text); **contrast `.hint` ≈3.9:1 < AA**
(regresie din redesign); densitate pierdută pe descoperire/grilă (labeluri inline → bloc). Consolidat
cu Accesibilitate Faza 2 în `docs/plan-ui-accesibilitate.md` (Grupuri 1–4, ordonate, autonome).

### 2026-06-04 — plan-master extindere platformă (B2, brainstorming)
Decizie user (B2): extindere la **toate tipurile de evaluări imobiliare în toate condițiile**.
Brainstorming → spec `docs/superpowers/specs/2026-06-04-platforma-evaluare-imobiliara-master-design.md`:
matrice 5 axe (tip activ × scop × tip valoare × abordare × ghid), arhitectură **Varianta 1** (profil de
evaluare + registru de abordări + raport pe secțiuni), **abordarea prin venit v1 = capitalizare directă**,
roadmap fazat (Fazele 0–7). Validare pe standard acum + dosar real ulterior. Urmează plan pentru Faza 0
(Fundația) după review-ul userului pe spec.

### 2026-06-04 — planuri de implementare platformă (Faza 0 TDD + Fazele 1–7)
Scrise (writing-plans): `docs/superpowers/plans/2026-06-04-faza0-fundatie.md` — plan **TDD complet,
executabil** pentru Faza 0 (7 task-uri: `ProfilEvaluare`, `RezultatAbordare`+adaptoare, motor venit
capitalizare directă, `reconcile_profil` aditiv, registru secțiuni, profil în `ReportContext`, verificare),
ancorat în codul real, **strict aditiv** (281 teste rămân plasa de siguranță). Și
`docs/superpowers/plans/2026-06-04-faze-1-7-roadmap-implementare.md` — planuri structurate pentru Fazele
1–7 (apartament · comercial/venit · industrial · agricol · scopuri noi · DCF+chirii · special), cu
dependențe + input extern necesar. Urmează execuția Faza 0 (subagent-driven sau inline — la alegerea userului).

### 2026-06-04 — Faza 0 (Fundația) IMPLEMENTATĂ (subagent-driven)
Executată Faza 0 din planul platformei, subagent-driven (implementer + review spec + review calitate per
task, + review final opus). Livrat, **strict aditiv**: `profil.py` (`ProfilEvaluare` + `CASA_TEREN_GARANTARE`),
`engine/abordari.py` (`RezultatAbordare` + adaptoare), `engine/venit.py` (capitalizare directă, cu validări
spec §3), `engine/reconciliation.py` (`reconcile_profil` aditiv + `metoda_selectata` cu „venit", ponderare
degenerată consistentă), `report/sectiuni.py` (registru filtrat pe ghid + abordări), `profil` în
`ReportContext`. **305 teste verzi** (281→305), pyflakes curat, **exe reîmpachetat + smoke /wizard 200**.
Cadrul e **dormant** (referit doar de teste). Review-ul final (opus): READY, fără blocaje; recomandări duse
în re-spec. **Re-spec post-fază** (regula standing): roadmap-ul fazelor 1–7 actualizat cu interfețele reale
+ **Faza 0.5 „Cablare"** (promovează cadrul din dormant în live, regresie strictă) ca următoarea sarcină +
recomandări (Protocol `Abordare`, `detalii` tipizat, `SectiuneSpec`, `valideaza_profil`). Comituri `add75bf … dd3f54b`.

### 2026-06-04 — quick-wins UI/a11y (G1.1 + Grup 3) + Faza 0.5 (Cablare)
La cererea userului (autonomie totală): mai întâi **quick-wins UI/a11y** — G1.1 contrast `.hint`
(`#6c7686`→`#5a6270`, 3.9:1→5.3:1 WCAG AA) + **Grup 3 `/result` ca certificat** (valoare hero ro-RO +
echivalent EUR/LEI la curs BNR + butoane CTA; helper `_fmt_numar`). Apoi **Faza 0.5 — Cablare**
(subagent-driven, 3 task-uri): `valideaza_profil` (consistență abordări/ponderi) + `construieste_context`
reconciliază prin `reconcile_profil` (peste `RezultatAbordare`) + `EvaluationInput.profil` — **pipeline-ul
de calcul promovat din dormant în LIVE, value-echivalent** (toate regresiile cu valori identice).
**311 teste verzi**, pyflakes curat, exe reîmpachetat + smoke (`/api/evaluare`=316.000,00; `/evaluare/{id}`=200).
Amânate explicit: refactor generator pe registru, Protocol `Abordare`, `detalii` tipizat, `SectiuneSpec`
(când le cere o fază). Următorul: **Faza 1 — Apartament** (autonom).

### 2026-06-04 — Faza 1 (Apartament) IMPLEMENTATĂ (subagent-driven)
Executată Faza 1, aditiv, 5 task-uri: profil `APARTAMENT_GARANTARE`; câmpuri apartament pe `BuildingData`
(`etaj`, `nr_niveluri_bloc`, `an_bloc`, `cota_teren_indiviza`, opționale) + validare `etaj ≤ niveluri`;
descriere de raport adaptată („Apartament: …", condițional → cele 12 teste de raport rămân verzi); wizard
cu selector **tip proprietate** (casă/apartament) + câmpuri apartament + persistență localStorage.
Motorul de comparație neschimbat. **319 teste verzi**, pyflakes curat, **exe reîmpachetat + smoke**
(apartament prin piață → 250.000; `/wizard` are selectorul). Comituri `9c3cd86 … 461070c`.
Următorul: **Faza 2 — Comercial/venit** (cablează `venit` în flux + UI DateVenit + secțiune raport venit;
necesită refactorul amânat al generatorului + ideal un dosar real de validare — se construiește pe standard).
