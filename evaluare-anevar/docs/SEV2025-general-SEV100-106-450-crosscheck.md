# SEV 2025 — Standarde generale (SEV 100/101/102/106) + SEV 450 asigurare — checklist conformitate raport vs. cod

> **Scop:** extinde cross-check-ul de conformitate SEV 2025 (după
> [GEV520-2025-crosscheck.md](GEV520-2025-crosscheck.md) și
> [SEV2025-GEV630-GEV500-crosscheck.md](SEV2025-GEV630-GEV500-crosscheck.md))
> pe **zonele GENERALE / transversale** care se aplică *oricărui* raport, indiferent de ghid:
> **(1) SEV 100 Cadrul general** — inclusiv noutățile 2025: *procedura de verificare a calității procesului
> de evaluare*, *scepticism profesional*, *utilizarea unui specialist / furnizor extern de servicii*;
> **(2) SEV 101 Termenii de referință** (elementele obligatorii §20.1 (a)–(p));
> **(3) SEV 102 Tipuri ale valorii** (valoarea de piață; sursa definiției tipului valorii);
> **(4) SEV 106 Documentare și raportare** (conținutul minim obligatoriu §30.6 (a)–(r));
> **(5) SEV 450 Evaluarea costurilor în scopul asigurării** — **standard NOU 2025** (fostul EVGN 6);
> app-ul are profil de asigurare (`ASIGURARE` în `profil.py`), deci se verifică alinierea.
>
> **Sursă:** `SEV 2025` (Standardele de evaluare a bunurilor, ed. 2025) — descărcat de pe
> [anevar.ro/images/_upload/sev-2025.pdf](https://www.anevar.ro/images/_upload/sev-2025.pdf)
> (fișier integral **8,72 MB**, complet). Paragrafe citate: **SEV 100** p. 3–6 (§§10–50),
> **SEV 101** p. 7–10 (§§10.1–30.2), **SEV 102** p. 11–18 + Anexă A10 (valoarea de piață),
> **SEV 106** p. 57–60 (§§10–40), **SEV 450** p. 277–281 (§§1–5).
> **În vigoare de la 1 iulie 2025** (Conferința Națională, hotărârea nr. 2/9 aprilie 2025).
>
> ⚠️ **Document de lucru (DRAFT).** Citatele au **diacriticele reconstruite** din extragerea PDF→text
> (pdftotext strică diacriticele); înainte de a fi tratate ca referință normativă, se confruntă cu PDF-ul
> oficial. **Decizia de conformitate revine evaluatorului autorizat / ANEVAR, nu aplicației** — aplicația
> nu poartă răspundere pentru conținutul rapoartelor generate.

---

## 1. Unde trăiesc aceste zone în cod

| Aspect | Fișier | Note |
|---|---|---|
| Registru secțiuni de raport | [report/sectiuni.py](../src/evaluare/report/sectiuni.py) | `_REGISTRU`, `ID_SECTIUNI`, `sectiuni_pentru_profil` — vezi **§4 (router mort)** |
| Generator raport (textul fiecărei secțiuni) | [report/generator.py](../src/evaluare/report/generator.py) | asamblare **hard-codată** în `genereaza_raport` (L650+); NU consumă registrul |
| Disclaimer aplicație (DRAFT + răspundere evaluator) | [generator.py:70–87](../src/evaluare/report/generator.py) | `DISCLAIMER_APLICATIE`, `_disclaimer_aplicatie` — în fruntea oricărui raport |
| Declarația de conformitate cu SEV | [generator.py:244–262](../src/evaluare/report/generator.py) | `_declaratie_conformitate` (6 afirmații) |
| Termeni de referință | [generator.py:265–364](../src/evaluare/report/generator.py) | `_termeni_referinta` — acoperă majoritatea §20.1 SEV 101 |
| Tipul valorii + sursa definiției | [generator.py:108–128](../src/evaluare/report/generator.py) | `_TIP_VALOARE_TXT`, `_tip_valoare_txt` (SEV 102 §20.4) |
| Profiluri (scop/tip valoare/ghid) | [profil.py](../src/evaluare/profil.py) | `ASIGURARE` (L58–61): `scop=asigurare`, `tip_valoare=asigurare`, `ghid=GEV_630`, `abordari=["cost"]` |
| Date administrative (date, evaluator, monedă…) | [models/meta.py](../src/evaluare/models/meta.py) | `EvaluationMeta` |
| Maparea scop→profil | [assembler.py:54–75](../src/evaluare/assembler.py) | `PROFIL_DUPA_SCOP["asigurare"] = ASIGURARE`; `rezolva_profil` |

> **Notă structurală cheie (vezi §4):** `generator.py` **NU importă** `report/sectiuni.py`. Secțiunile
> efective ies din asamblarea hard-codată în `genereaza_raport` + condiționări runtime
> (`if ctx.profil.ghid == "GEV_520"`, `if ctx.venit_result is not None`, …). Registrul de secțiuni
> (`_REGISTRU` / `sectiuni_pentru_profil`) e referit **doar din teste**, nu din calea de execuție.

---

## 2A. SEV 100 — Cadrul general al evaluării → acoperire în cod

Legendă: ✅ acoperit · ⚠️ parțial · ❌ lipsă/contradicție

| # | Cerință SEV 100 (2025) | § | Cod | Stare | Acțiune |
|---|---|---|---|---|---|
| 100-1 | **Declararea SEV utilizate + a conformității** în raportare | §10.3 | `_declaratie_conformitate` + `_scrisoare_transmitere`: „conform SEV, ed. 2025, în vigoare 1 iulie 2025 (HCN 2/2025)" | ✅ | — |
| 100-2 | **Principiile evaluatorului**: etică, competență, conformitate | §10.1–10.3 | declarație: independență, lipsa interesului, onorariu necondiționat, competență + asigurare RC | ✅ | — |
| 100-3 | **Scepticism profesional** (NOU 2025) — nivel adecvat în fiecare etapă | §10.4 | **inexistent** — niciun text „scepticism profesional"; verificat în `src/` | ❌ **gol (novație 2025)** | adaugă mențiune în declarație/termeni |
| 100-4 | **Procedura de verificare a calității procesului de evaluare** (NOU 2025) — proceduri documentate, evaluare periodică, risc al evaluării | §20.1–20.8 | **inexistent** ca text de raport; există motor de *validare a calculului* (`engine/validation.py`) și *audit-log* (`audit/raport_audit.py`), dar nicio mențiune a „procedurilor de verificare a calității" în raport | ❌ **gol (novație 2025)** | text scurt: procedurile de verificare aplicate au fost documentate (§20.5) |
| 100-5 | **Utilizarea unui specialist / furnizor extern de servicii** (NOU 2025) — dacă se folosește: convenit cu părțile, prezentat în raport, competența documentată | §30.1–30.3 | `_termeni_referinta` L342–343: „nu a fost cazul utilizării unui specialist…" (SEV 106 §30.6 o) | ✅ (negativă explicită) | OK; dacă se folosește efectiv, de adăugat competența §30.2 |
| 100-6 | **Conformitate cu standardele** — devierile de la SEV se explică/documentează; orice altă deviere → neconform | §40.1–40.6 | declarație afirmă conformitatea; **nu** există mecanism de raportare structurată a derogărilor (doar pe `GEV_520` se menționează derogările cerute de creditor) | ⚠️ derogările SEV nu au tratare generală de raportare | — |
| 100-7 | **Prioritatea cerințelor legale** contradictorii cu SEV + explicarea lor | §40.4–40.5 | neacoperit explicit (nu apare un bloc „cerințe legale care diferă de SEV") | ⚠️ neacoperit (rar relevant la rezidențial) | — |
| 100-8 | **Ediția SEV la dată retrospectivă/istorică** — se documentează ediția pe care s-a fundamentat + cea aplicabilă la dată | §50.2 | raportul citează doar ediția 2025; nicio logică de dată retrospectivă | ⚠️ neacoperit (relevant doar la evaluări retrospective) | — |

---

## 2B. SEV 101 — Termenii de referință (§20.1, elemente obligatorii) → acoperire în cod

`_termeni_referinta` (generator.py:265–364) este blocul care acoperă §20.1. Mapare element cu element:

| # | Element §20.1 SEV 101 | Cod | Stare |
|---|---|---|---|
| 101-a | **Activul/datoria supus(ă) evaluării** identificat clar | L284–287: adresă + nr. cadastral + CF | ✅ |
| 101-b | **Clientul** | L269: `client_nume (client_tip)` | ✅ |
| 101-c | **Utilizarea desemnată** (scopul) | L272: `Scopul evaluarii: {scop}` | ✅ |
| 101-d | **Utilizatorul desemnat** | L270–271: `beneficiar` (dacă există); GEV_520 L311: creditorul nominalizat | ⚠️ doar dacă `beneficiar` e completat |
| 101-e | **Evaluatorul** (calificat, conflict de interese) | L322–325 (SEV 101 20.1 e) + declarație independență | ✅ |
| 101-f | **Moneda evaluării** | L274–277: monedă + curs EUR/LEI | ✅ |
| 101-g | **Data evaluării** (+ data raportului dacă diferă) | L278–283: data evaluării, raportului, inspecției, valabilitate | ✅ |
| 101-h | **Tipul valorii** + **sursa definiției** citată/explicată | L273 + `_tip_valoare_txt` (referă SEV 102/IVS/IFRS) | ✅ |
| 101-i | **Natura/amploarea activităților + limitări** (inspecție, documentare) | L326–330 (SEV 101 20.1 i) | ✅ |
| 101-j | **Natura și sursa informațiilor** + verificare | L331–335 (SEV 101 20.1 j) | ✅ |
| 101-k | **Ipoteze speciale** convenite înainte | L296–305 (premise) + GEV_520 L314–320 (ipoteze speciale) | ⚠️ ipotezele speciale generale apar mai ales pe `GEV_520`; pe alte profiluri doar premisa generică |
| 101-l | **Specialist** (utilizare și rol) (NOU 2025) | L342–343: „nu a fost cazul…" | ✅ (negativă explicită) |
| 101-m | **Factori de mediu, sociali și de guvernanță (ESG)** (NOU 2025) | L336–340 (SEV 101/106 20.1/30.6 m) | ✅ (mențiune generică ESG în termeni) |
| 101-n | **Tipul raportului / documentația livrată** | L345–349 (raport scris, narativ) | ✅ |
| 101-o | **Restricții de utilizare/difuzare/publicare** | L345–349 (utilizare exclusivă în scop + acord scris) | ✅ |
| 101-p | **Conformitatea cu SEV** declarată în termeni; comunicare scrisă dacă devine neconform | conformitatea e declarată; **nu** există clauza „dacă pe parcurs devine clar că nu va fi conform, se comunică în scris clientului" (§20.1 p / 10.5 / 20.3) | ⚠️ clauza de neconformitate-pe-parcurs lipsește din text |
| 101-x1 | Termenii **conveniți în scris înainte de finalizare** | §20.2 — proces (contract), nu conținut de raport; în afara generatorului | n/a (proces) |
| 101-x2 | **Cerințe privind verificarea procesului/valorii** (§30) | nu se aplică — app-ul produce evaluări, nu verificări de evaluare (SEV 400) | n/a |

> **Observație 101:** blocul de termeni de referință este **solid** și citează explicit paragrafele SEV 101.
> Golurile sunt: (101-k) ipotezele speciale dincolo de `GEV_520`, (101-p) clauza de comunicare scrisă a
> neconformității pe parcurs. ESG (101-m) e prezent **în termeni** ca mențiune generică — dar lipsește din
> *analiza de valoare* (vezi golul ESG semnalat în crosscheck-ul GEV 630/500, #ESG-1…9, care rămâne valabil).

---

## 2C. SEV 102 — Tipuri ale valorii → acoperire în cod

> Definiția valorii de piață (A10.1): *„suma estimată pentru care un activ … ar putea fi schimbat la data
> evaluării, între un cumpărător hotărât și un vânzător hotărât, într-o tranzacție nepărtinitoare, după un
> marketing adecvat și în care părțile au acționat fiecare în cunoștință de cauză, prudent și fără
> constrângere."*

| # | Cerință SEV 102 (2025) | § | Cod | Stare |
|---|---|---|---|---|
| 102-1 | Tipul valorii **adecvat utilizării desemnate** | §10.1, 20.4 | profilurile leagă `scop`→`tip_valoare` (`PROFIL_DUPA_SCOP`); garantare/litigiu→piață, asigurare→asigurare, raportare→justă | ✅ (cu rezerva inversiunii GEV 500 — vezi crosscheck precedent §C) |
| 102-2 | **Sursa definiției tipului valorii** citată sau explicată | §20.4, §10.2 | `_tip_valoare_txt` adaugă referința SEV 102/IVS 104/IFRS 13 la fiecare slug | ✅ |
| 102-3 | Tipurile definite în SEV: **valoare de piață, chirie de piață, valoare echitabilă, valoare de investiție, valoare a sinergiei, valoare de lichidare** | §20.2 / Anexă A10–A60 | `TipValoare` Literal: `piata/investitie/justa/lichidare/asigurare/chirie` | ⚠️ **discrepanță de nomenclatură**: codul are `justa` (≈ valoare justă IFRS A70/A80) și `asigurare`, dar **lipsesc** `echitabila` (A30) și `sinergie` (A50) ca tipuri SEV-definite; `chirie` ≈ A20 ✓ |
| 102-4 | **Valoarea de piață reflectă cea mai bună utilizare (CMBU)** | Anexă A10.4 | cap. 5 CMBU (`generator.py:745–750`) — dar narativ AI/manual, opțional | ⚠️ CMBU e prezentă structural, dar conținutul depinde de narator |
| 102-5 | Valoarea de piață **exclude** finanțări atipice, sale-and-leaseback, concesii speciale, element specific unui proprietar | Anexă A10.2 (a), A10.7 | text definițional standard; codul nu modelează aceste excluderi (motorul lucrează pe oferte ajustate la tranzacție) | ⚠️ implicit (nu se modelează, dar nici nu se încalcă) |
| 102-6 | **Premise ale valorii**: cea mai bună utilizare / utilizare existentă / vânzare ordonată / vânzare forțată | §10.3 / A90–A120 | premisa „utilizare continuă" în termeni (L296–299); „vânzare forțată" pe `GEV_520` (valoarea de lichidare L536–549) | ✅ (utilizare continuă + vânzare forțată pe garantare) |
| 102-7 | Terminologie 2025: **„utilizare desemnată"** înlocuiește vechiul „scopul evaluării" | cuprins SEV 102 | codul folosește încă `scop` / „Scopul evaluarii" ca etichetă în raport | ⚠️ etichetă veche („scop") vs. termen 2025 („utilizare desemnată") — cosmetic, dar de aliniat la noua terminologie |

> **#102-3 (nomenclatură tipuri valoare):** `_TIP_VALOARE_TXT` (L110–116) etichetează `justa` drept „valoare
> justă (SEV 102 / IFRS 13)" — corect ca **alt tip** (A70/A80), dar **nu** ca tip *definit în SEV*; iar
> `asigurare` e etichetat „cost de înlocuire net (GEV 630)" — vezi **§2E / SEV 450**: pentru asigurare,
> referința corectă este **SEV 450**, nu (doar) GEV 630.

---

## 2D. SEV 106 — Documentare și raportare (§30.6, conținut minim) → acoperire în cod

Mapare a celor **18 cerințe minime** (§30.6 a–r) față de raportul generat:

| # | Cerință minimă §30.6 SEV 106 | Cod | Stare |
|---|---|---|---|
| 106-a | **Termenii de referință conveniți** | `_termeni_referinta` (secțiune dedicată) | ✅ |
| 106-b | **Activele/datoriile supuse evaluării** | copertă + termeni + cap. 4 | ✅ |
| 106-c | **Identitatea evaluatorului** | copertă + declarație + semnătură | ✅ |
| 106-d | **Clientul** | copertă + termeni + cap. 1 | ✅ |
| 106-e | **Utilizarea desemnată** (scopul) | copertă + termeni + cap. 1 | ✅ |
| 106-f | **Utilizatorii desemnați** | `beneficiar` (dacă există) | ⚠️ doar dacă completat |
| 106-g | **Moneda evaluării** | termeni + copertă (+ echivalent LEI) | ✅ |
| 106-h | **Data(ele) evaluării** | copertă + termeni + cap. 1 | ✅ |
| 106-i | **Tipul valorii utilizat** | `_tip_valoare_txt` (cu sursă) | ✅ |
| 106-j | **Abordarea/abordările utilizate** | cap. 6 + „SEV 103/105" (L755) | ✅ |
| 106-k | **Metoda/modelul de evaluare aplicat** | cap. 6 (grile, cost, venit) + reconciliere | ✅ |
| 106-l | **Sursele + modul de selectare a informațiilor** semnificative | termeni L331–335 + anexa 1 (surse comparabile) | ✅ |
| 106-m | **Date ESG semnificative** utilizate/luate în considerare (NOU 2025) | mențiune generică în termeni (L336–340); **dar fără analiză ESG efectivă** în corpul valorii | ⚠️ mențiune da, analiză nu (vezi #ESG crosscheck precedent) |
| 106-n | **Ipoteze semnificative/speciale + condiții limitative** | cap. 2 „Ipoteze generale și speciale" (narativ) + premise termeni | ⚠️ depinde de narator; nu o secțiune structurată de ipoteze speciale distincte |
| 106-o | **Constatările unui specialist / furnizor extern** | termeni L342–343 (negativă) | ✅ (negativă explicită) |
| 106-p | **Valoarea + raționamentul evaluării** | cap. 7 reconciliere + valoarea finală | ✅ |
| 106-q | **Declarația de conformitate cu SEV** | `_declaratie_conformitate` | ✅ |
| 106-r | **Data raportului** (poate diferi de data evaluării) | copertă + termeni + cap. 1 | ✅ |
| 106-x | Raportul **scris**; nu se afirmă conformitatea dacă o limitare o afectează | §10.2, §30.8 — raport `.docx` scris; clauza „nu afirma conformitatea dacă există limitare" nu e explicită | ⚠️ formatul scris ✓; clauza §30.8 lipsește |

> **Observație 106:** acoperire **foarte bună** a celor 18 cerințe minime — 14/18 ✅, restul ⚠️ (dependente de
> completarea câmpurilor opționale sau de naratorul AI). Golurile reale: (106-m) ESG ca *dată de intrare în
> valoare* (nu doar mențiune), (106-n) ipotezele speciale ca secțiune **distinctă** (GEV 630 §111 cere asta),
> (106-x) clauza §30.8 de a NU afirma conformitatea când o limitare o afectează.

---

## 2E. SEV 450 — Evaluarea costurilor în scopul asigurării (STANDARD NOU 2025) → acoperire în cod

> ⚠️ **Atenție la denumire și natură.** SEV 450 (fostul EVGN 6) se numește **„Evaluarea *costurilor* în scopul
> asigurării"** — este o estimare de **cost** (cost de înlocuire / valoare de reconstruire totală), **NU** o
> valoare de piață și **nu** o „valoare de asigurare" generică. §4.1: *„o estimare a valorii de asigurare sau
> a costului de refacere trebuie să se bazeze mai degrabă pe **costul de înlocuire total**, decât pe valoarea
> de piață"*. Sursa: European Valuation Standards, 10th ed., 2025 © TEGOVA (deci ghid de tip EVS/EVGN).
>
> 📌 **Important — separarea utilizărilor desemnate (GEV 520 §4 și §9):** un raport cu utilizarea desemnată
> **garantare** NU poate fi folosit pentru asigurare, și invers. Profilul `ASIGURARE` din app este un profil
> **distinct** (scop=asigurare) — corect ca separare; problema e că **conținutul de raport pentru asigurare
> nu există** (vezi mai jos).

Profil în cod: `ASIGURARE` (profil.py:58–61) = `tip_activ=casa`, `scop=asigurare`, `tip_valoare=asigurare`,
`abordari_aplicabile=["cost"]`, **`ghid="GEV_630"`**.

| # | Cerință SEV 450 (2025) | § | Cod | Stare |
|---|---|---|---|---|
| 450-1 | Baza valorii pentru asigurare = **costul de înlocuire total / valoarea de reconstruire totală**, NU valoarea de piață | §4.1, §3.7 | profil `ASIGURARE` are `abordari=["cost"]` → corect ca abordare; **dar** `_tip_valoare_txt["asigurare"]` zice „cost de înlocuire **net** (GEV 630)" | ⚠️ **contradicție subtilă**: SEV 450 cere cost de înlocuire **total** (fără deducere pentru depreciere, §3.6/§3.7.2), nu **net**; iar referința corectă e **SEV 450**, nu GEV 630 |
| 450-2 | Standardul/ghidul citat trebuie să fie **SEV 450** | tot standardul | codul NU citează nicăieri „SEV 450"; `_TIP_VALOARE_TXT` și declarația citează GEV 630 | ❌ **gol**: SEV 450 nu e referit deloc în `src/` |
| 450-3 | **Costul de refacere** include: demolare, curățare amplasament, **îndepărtare moloz/deșeuri**, schele/susținere temporară | §3.4, §4.2–4.4 | motorul de cost (`engine/cost.py`) e generic (elemente CIB); niciun câmp/text pentru demolare, moloz, susținere | ❌ **gol** (specifice asigurării) |
| 450-4 | **Onorarii profesionale** (arhitect, topograf, inginer) + taxe certificat urbanism / autorizație renovare | §3.4, §4.6 | neacoperit | ❌ gol |
| 450-5 | **Performanța energetică** a clădirii eligibile luată în calcul (vezi EVS 6) | §4.5 | neacoperit | ❌ gol |
| 450-6 | **Suprafața** clădirilor — bază de măsurare conform practicii locale și surselor de cost recunoscute | §4.7 | `building.au/acd` există; nicio mențiune de bază de măsurare pentru asigurare | ⚠️ date de suprafață da; context asigurare nu |
| 450-7 | Avertizare **sub-asigurare** (sumă fixă < cost total de reconstruire) + reevaluare regulată | §3.7.4, §3.8.1, §3.9 | neacoperit | ❌ gol |
| 450-8 | **TVA**: dacă asiguratul nu poate recupera TVA, se clarifică dacă polița/legislația permit creșterea costurilor cu TVA | §5 (ultim alineat) | `valoare_fara_tva` există ca flag general, dar fără logica TVA-asigurare | ⚠️ neacoperit specific |
| 450-9 | **Raportare §5** — elemente specifice: adresa beneficiarului poliței; localizare + utilizare proprietate **și a proprietăților adiacente**; clădire/etaje/facilități/acces; **fișă constructivă + fotografii numeroase**; certificate de urbanism/avize; **starea fizică + estimarea deteriorărilor** | §5 | raportul generic are descriere (cap. 4) + anexă foto + (parțial) acces/utilități/urbanism; **lipsesc**: proprietăți adiacente, fișa constructivă dedicată asigurării, starea/estimarea deteriorărilor, structura de raportare §5 | ❌ **gol**: nu există bloc de raport pentru asigurare (cum există `_adauga_risc_garantie` pentru GEV 520) |
| 450-10 | Chiria de piață pentru utilizare temporară (relocare asigurat), când e cazul | §1.4 | neacoperit | ⚠️ neacoperit (ocazional) |

> **Concluzie SEV 450:** profilul `ASIGURARE` **există** și alege corect abordarea prin cost, dar **nu există
> niciun conținut de raport specific asigurării**. Generatorul produce aceeași schelă de 7 capitole + alocare,
> **fără** un bloc `_adauga_*` pentru SEV 450 (analog cu `_adauga_risc_garantie` pe `GEV_520`). În plus,
> standardul de referință în cod e GEV 630 + „cost de înlocuire **net**", în timp ce SEV 450 cere **SEV 450**
> + cost de înlocuire **total** (fără depreciere). Pe un raport real de asigurare, lipsesc complet: §5
> (raportarea specifică), demolarea/molozul/onorariile (§4), avertismentul de sub-asigurare (§3.7/§3.9).

---

## 3. Concluzie — diferențe care contează (priorizate)

### A. 🔴 SEV 450 — profil de asigurare fără conținut de raport conform

`ASIGURARE` (profil.py:58–61) declară scop=asigurare și abordare=cost, dar generatorul **nu emite niciun
bloc SEV 450**. Pe un raport real de asigurare ies: referința greșită (GEV 630 + „cost net" în loc de
**SEV 450** + „cost de înlocuire **total**"), și lipsesc integral cerințele §4–§5 (demolare/moloz/onorarii,
sub-asigurare, raportarea §5 cu proprietăți adiacente + fișă constructivă + stare/deteriorări). → fie se
adaugă un `_adauga_asigurare` (analog `_adauga_risc_garantie`), fie profilul `ASIGURARE` se marchează ca
„neacoperit complet — necesită completare manuală de către evaluator" până la implementare.

### B. 🟠 Noutățile SEV 100 lipsesc din raport (scepticism + proceduri de verificare a calității)

- **#100-3 scepticism profesional** (§10.4) și **#100-4 procedura de verificare a calității procesului**
  (§20.1–20.8) sunt **novații 2025 obligatorii** și **nu apar** în niciun text de raport. Sunt ușor de
  adăugat (1–2 fraze în declarația de conformitate / termeni): app-ul are deja `engine/validation.py` și
  `audit/raport_audit.py` care *implementează* de facto proceduri de verificare — dar raportul nu le declară.

### C. 🟠 Router de secțiuni MORT — `sectiuni.py` nu e consumat de generator

`report/sectiuni.py` (`_REGISTRU`, `sectiuni_pentru_profil`, `ID_SECTIUNI`) **nu e importat de
`generator.py`** și e referit **doar din teste** (`tests/test_sectiuni.py`). Secțiunile reale ies din
asamblarea hard-codată în `genereaza_raport`. Consecințe:
- **Registrul induce în eroare** ca sursă de adevăr (pare să dirijeze raportul, dar nu o face).
- Mapările din registru (ex. `raportare_financiara`→`GEV_500`) **nu au efect** la rulare.
- **Test de „completitudine"** (vezi §4) trece pe registru, dar nu garantează că generatorul emite secțiunea.

→ ori se conectează generatorul la `sectiuni_pentru_profil` (cu un dispatch id→funcție), ori se elimină
registrul ca cod mort (deja semnalat în `docs/AUTONOM-taskuri.md:127`: *„router-by-profile mort?"*).

### D. 🟡 Întăriri parțiale (text prezent dar dependent de context/narator)

- **#101-p / #106-x** — clauza „nu se afirmă conformitatea dacă o limitare o afectează / se comunică în scris
  clientului dacă devine neconform" (SEV 101 §20.3, SEV 106 §30.8) lipsește din text.
- **#101-k / #106-n** — ipotezele speciale ca **secțiune distinctă** apar robust doar pe `GEV_520`.
- **#102-3** — `TipValoare` nu include `echitabila` (A30) și `sinergie` (A50); `justa`+`asigurare` sunt „alte
  tipuri", nu tipuri SEV-definite — de clarificat eticheta.
- **#102-7** — terminologie: „scopul evaluării" (etichetă veche) vs. „utilizare desemnată" (termen 2025).
- **#106-m / ESG** — ESG e doar **mențiune** în termeni, nu **dată de intrare în valoare** (golul ESG complet
  din crosscheck-ul GEV 630/500 rămâne valabil pe toate profilurile).

### E. ✅ Solid (matchuri exacte cu standardele generale)

- **SEV 106 §30.6** — **14/18** cerințe minime acoperite direct, cu citare de paragraf; structura de 7 capitole
  + termeni + declarație + anexe mapează 1:1 conținutul minim obligatoriu.
- **SEV 101 §20.1** — bloc de termeni de referință complet, cu citarea explicită a sub-punctelor (e, i, j, n, o)
  și a noutăților 2025 (specialist §20.1 l, ESG §20.1 m).
- **SEV 102 §20.4 / §30.6(i)** — tipul valorii e **mereu** însoțit de sursa definiției (`_tip_valoare_txt`).
- **SEV 100 §10 + §30.6(o)** — principiile evaluatorului (declarație) + negativa explicită „fără specialist".
- **Disclaimer aplicație** — DRAFT + răspunderea/verificarea revin evaluatorului, în fruntea oricărui raport
  (generator.py:70–87), aliniat cu spiritul §10.5/§40 (răspunderea profesională a evaluatorului).

---

## 4. Check de COMPLETITUDINE — secțiuni înregistrate vs. emise de generator

Mapare a fiecărui id din `_REGISTRU` (sectiuni.py:7–22) la funcția/blocul care îl emite în `generator.py`:

| id secțiune (`_REGISTRU`) | Emis în generator? | Unde |
|---|---|---|
| `coperta` | ✅ | `_coperta` (L174) |
| `scrisoare_transmitere` | ✅ | `_scrisoare_transmitere` (L204) |
| `declaratie_conformitate` | ✅ | `_declaratie_conformitate` (L244) |
| `termeni_referinta` | ✅ | `_termeni_referinta` (L265) |
| `descriere_proprietate` | ✅ | cap. 4 inline (L702) |
| `analiza_piata` | ✅ | cap. 3 inline (L695) |
| `abordare_cost` | ✅ | `_adauga_tabel_cost` (L439) |
| `abordare_comparatie` | ✅ | `_adauga_grila_comparatie` (L370) |
| `abordare_venit` | ✅ | bloc venit inline (L762–777) — doar dacă `venit_result`/`dcf_valoare` setate |
| `reconciliere` | ✅ | cap. 7 inline (L782) |
| `alocare_valoare` | ✅ | `_adauga_alocare` (L470) — doar dacă `alocare_constructii` setată |
| `gev_520` | ✅ | `_adauga_risc_garantie` (L508) — doar pe `ghid==GEV_520` |
| **`raportare_financiara`** | ❌ **NU** | **niciun generator** — id înregistrat dar **gol** |
| `anexe` | ✅ | `_adauga_anexe` (L591) |

**Rezultat: o singură secțiune înregistrată-dar-goală — `raportare_financiara`** (confirmă observația din
[SEV2025-GEV630-GEV500-crosscheck.md](SEV2025-GEV630-GEV500-crosscheck.md) #500-1). Nu există altele goale
în registru.

> ⚠️ **Avertisment de metodă (vezi §3.C):** acest check pe registru e *informativ*, dar **nu** reflectă calea de
> execuție — `generator.py` **nu folosește** registrul. Practic, „completitudinea" reală a raportului depinde
> de asamblarea hard-codată + de câmpurile runtime (`venit_result`, `alocare_constructii`, `ghid`), NU de
> `_REGISTRU`. Două goluri *funcționale* (nu de registru) mai importante:
> - **SEV 450 / asigurare**: profilul `ASIGURARE` (`ghid=GEV_630`) **nu** are bloc dedicat — raportul de
>   asigurare iese fără conținut SEV 450 (vezi §2E / §3.A). Nu e prins de check-ul pe registru fiindcă nu
>   există un id „asigurare" în `_REGISTRU`.
> - **GEV 630 (`COMERCIAL_INCHIRIAT`, `INDUSTRIAL`, `AGRICOL`, `IMPOZITARE`, `LITIGII`, `SPECIAL`)**: pe toate
>   profilurile `GEV_630`, raportul folosește aceeași schelă fără bloc de text dedicat ghidului (doar `GEV_520`
>   are bloc propriu). Nu e „secțiune goală în registru", dar e un gol de conținut per-ghid.

---

## 5. Modificări concrete propuse (pentru sesiunea de fix, nu aici)

1. **`generator.py` — bloc SEV 450 pentru profil asigurare** (`_adauga_asigurare`, analog
   `_adauga_risc_garantie`): cost de înlocuire **total** (nu net, §3.6/§4.1), demolare/curățare/moloz/schele
   (§4.2–4.4), onorarii profesionale + taxe urbanism (§4.6), avertisment **sub-asigurare** + reevaluare
   regulată (§3.7/§3.9), raportarea §5 (proprietăți adiacente, fișă constructivă, stare/deteriorări), TVA
   asigurat (§5). Apelat pe `scop==asigurare`. Citează **SEV 450**, nu GEV 630.
2. **`generator.py` / `_TIP_VALOARE_TXT`** — corectează eticheta `asigurare`: „cost de înlocuire **total**,
   conform **SEV 450**" (acum: „cost de înlocuire net (GEV 630)").
3. **`generator.py` — scepticism profesional (§10.4) + procedurile de verificare a calității (§20)**: 1–2
   fraze în `_declaratie_conformitate` / `_termeni_referinta` (novații 2025; app-ul are deja `validation.py`
   + `raport_audit.py` ca substrat).
4. **`generator.py` — clauza de neconformitate** (SEV 101 §20.3 / SEV 106 §30.8): „dacă o limitare/restricție
   afectează conformitatea cu SEV, evaluatorul nu afirmă conformitatea / o comunică în scris clientului".
5. **`report/sectiuni.py` ↔ `generator.py`** (§3.C): ori se **conectează** generatorul la
   `sectiuni_pentru_profil` (dispatch id→funcție, inclusiv un generator pentru `raportare_financiara`), ori se
   **elimină** registrul ca cod mort (cf. `AUTONOM-taskuri.md:127`).
6. **`profil.py` / `TipValoare`** (§2C #102-3, #102-7): clarifică nomenclatura tipurilor (echitabilă/sinergie
   lipsesc; justă/asigurare = „alte tipuri") și aliniază eticheta „scop" la „utilizare desemnată" (terminologie 2025).
7. **Teste:** caz `ASIGURARE` care asertează prezența blocului SEV 450 + referința „SEV 450"; caz care
   asertează prezența mențiunii de scepticism profesional / proceduri de verificare în declarație.

> Toate textele rămân *draft generat de aplicație*; **evaluatorul autorizat validează și își asumă conținutul**
> (conform disclaimerului existent în rapoarte, generator.py:70–87). Aplicația nu poartă răspundere normativă.
