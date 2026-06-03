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
