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

## 10. Decizii și principii stabilite

- **Om-în-buclă** (AI propune, evaluatorul decide) — din rațiuni de răspundere profesională (GEV 520) + GDPR.
- **GDPR-first** — date personale anonimizate înainte de orice apel extern.
- **Validare pe dovezi** — motoarele validate pe dosare reale GBF, nu pe presupuneri.
- **Clienți injectabili** (AI, fetcher, viitor BIG/ANCPI/VLM) → testabil offline.
- **TDD + rebuild + smoke** la fiecare modul.
- **Securitate:** cheia Perplexity NU se distribuie cu exe-ul; `.env` gitignored.

## 11. Stare la momentul creării jurnalului

- **~199 teste verzi**, exe funcțional reîmpachetat.
- Tot ce e „cod pur" fără dependențe externe = implementat.
- Rămas blocat extern: `big/`, `ancpi/` (acces ANEVAR/ANCPI), `aml/` faze 4+ (liste live, transmitere
  ONPCSB, validare juridică), exe semnat (certificat), catalog IROVAL (plătit).

---

## Actualizări (orare)

> Regulă: se adaugă o intrare **doar dacă există ceva nou** de consemnat în ultima oră. Dacă nu e
> nimic nou, nu se scrie nimic.

### 2026-06-03 — jurnal creat
Sinteza completă a sesiunii (secțiunile 1–11 de mai sus). Ultimul livrat: planul de implementare AML
ancorat în Legea 129/2019 + Norme 37/2021 + HCD 58. Programată actualizarea orară a acestui jurnal.
