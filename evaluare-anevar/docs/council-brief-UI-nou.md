# Brief pentru LLM Council — „Planul vostru pentru noul UI"

> Material AUTOSUFICIENT (reviewerii nu au acces la cod). Se trimite ca parte a interogării
> council adiționale (vezi `AUTONOM-taskuri.md` pkt. 3). Cerere: **fiecare model își dă PLANUL LUI
> INDIVIDUAL pentru noul UI** — cum ar trebui definit — cu **detaliere, riscuri și dependențe**.

## 1. Ce este aplicația (obiective)
Aplicație desktop **locală/offline** (`.exe` Windows, FastAPI+Jinja+SQLite, PyInstaller, 50 MB) care
**ASISTĂ un evaluator autorizat ANEVAR** la rapoarte de evaluare imobiliară (casă+teren, scop principal
**garantare credit ipotecar**; standarde **SEV 2025 / GEV 520**). Principiu fundamental **„om în buclă"**:
aplicația **propune**, evaluatorul **verifică, semnează și își asumă** valoarea. **Obiective:** (a) să
ușureze și să grăbească munca evaluatorului, NU să-l înlocuiască; (b) rapoarte conforme care **nu pică la
bancă**; (c) tool mic, mentenanță redusă, vandabil prin abonament; (d) AI doar pentru **proza narativă**
(numerele rămân deterministe). 489 teste + 57 e2e, acoperire ≥90%.

## 2. Toate feature-urile / modulele
- **Motor de calcul determinist** (`engine/`): cost (CIN segregat, catalog IROVAL — cost de nou − depreciere
  fizică interpolată pe vârstă + funcțională + externă); piață (grile de comparație, 2 etape: tranzacție
  compus + proprietate aditiv, selecție pe ajustare brută minimă); teren (grilă 2 etape, preț/mp); chirii→venit
  (capitalizare directă); DCF; reconciliere (primară/ponderată + alocare teren/construcție); validări SEV
  (Au≤Acd, min 3 comparabile, limite ajustare, outlier) + **8 garduri prudențiale** (alerte, nu blocaje).
- **Descoperire comparabile** (`discovery/`): caută anunțuri pe **imobiliare.ro / storia.ro** (OLX parțial),
  construiește URL de căutare, extrage URL-uri de anunț (preferă localitatea în slug → taie promovatele),
  parsează preț/suprafață/teren/atribute. **Scoring** auto-explicativ pe atribute primare (an, stare, finisaj,
  încălzire, teren, suprafață construită) + secundare definite de user. Returnează candidați rankaați + tabel
  de metodologie. Verificat live: imobiliare/storia corecte; OLX dă prețul dar rar suprafața.
- **Parser anunțuri** (`importers/url_parser.py`): JSON-LD (recursiv) + `__NEXT_DATA__` (storia) + og:meta +
  regex. **Gardă pagină-listă** (URL trunchiat → refuză, nu extrage tăcut un anunț promovat). Teren ≠ casă.
- **Import dosar din `.docx`** (`importers/docx_dosar.py`): nume fișier = identitate (id/nume/tip/localitate→județ);
  text = beneficiar/scop/dată. Robust la docx ilizibil.
- **AI narativ** (`ai/narrative.py`): Perplexity/Claude (injectabil + fallback șablon). Primește **text
  anonimizat/pseudonimizat** (regex CNP/CF/adresă). Temperatură joasă, „nu inventa surse", marcaj „draft AI".
- **Generator raport `.docx`** (`report/`): raport SEV complet (vezi §3). Anonimizator + secțiuni + ghid GEV.
- **Modul AML** (`aml/`, Legea 129/2019): KYC, beneficiar real, PEP, risc (4 factori + reguli EDD), 10
  indicatori HCD 58, raportare RTN/RTS (prag 10.000 €), documente .docx. **Ca asistență** — banner „nu verifică
  automat PEP/sancțiuni; verifică manual [linkuri oficiale]".
- **Ingestie PDF** (`ingestie/`): CF/releveu/plan/CPE → câmpuri (cadastral, Au/Acd, teren) + OCR fallback.
- **GDPR**: filtru regex pe textul trimis la AI + modele politică/consimțământ.
- **Audit** (`audit/`): urmă de calcul + validare încrucișată.
- **Persistență**: SQLite (UI vechi) + **foldere** (UI nou, sursa de adevăr: `date/dosare/<uuid>/dosar.json`
  + versiuni `.docx`).

## 3. Fișiere exportate (output)
- **Raport de evaluare `.docx`** — documentul principal: scrisoare de transmitere, declarație de conformitate
  (citează ghidul GEV din profil), termeni de referință, identificarea proprietății, cele 3 abordări (cost/
  piață/venit unde aplicabil) cu grile, reconciliere, valoare finală, ipoteze + ipoteze speciale, anexe
  (foto — gated comercial; scanuri CF). Versiuni datate în folderul dosarului.
- **Documente AML `.docx`** (norme interne, decizie desemnare, fișă KYC, RTN, RTS).
- **Documente GDPR `.docx`** (politică, consimțământ).
- **Audit `.txt`** (urmă de calcul).
- **Feedback `.csv`** (de la testeri).

## 4. UI VECHI (wizard — referință, coexistă, de retras pe termen lung)
Flux ghidat **pas-cu-pas** (`/wizard`): Pas 1 adresă (dropdown județ+localitate, 13.250 localități) → Pas 2
subiect (tip proprietate comută grupuri de câmpuri: casă/apartament/industrial/agricol/special) → Pas 3
comparabile (import URL/extensie + descoperire) → Pas 4 calcul (metodă) → Pas 5 raport. Stare în localStorage.
Pagini: `/wizard`, `/formular` (monolit), `/grila` (3 grile: teren/casă/chirii, tab-uri WAI-ARIA), `/descoperire`,
`/aml`, `/dosare` (management SQLite). Antet `_topbar` (nav Evaluare/Dosare/Grile/Descoperire/AML) + subsol.

## 5. UI NOU „output-first" (versiunea curentă — ȚINTA, ce evaluăm)
Filozofie: pornești de la **output (documentele)** spre date. Flux: **pagină index** (alegi UI nou vs wizard) →
**cont local** (`/cont`: nume + legitimație + format nume dosar) → **ÎNCEPE** (`/incepe`: 5 opțiuni — Dosar nou /
Încarcă salvat / Importă dosarul tău (.docx) / Import asemănător [comercial] / Demo [comercial] + listă dosare
salvate din diff foldere) → **workspace dosar** (`/dosar/<uuid>`): tab-uri output **[Raport][AML][GDPR][Audit]
[Anexe]** + sub-tab-uri Raport **[Proprietate][Comparabile][Calcul][Generează]**. Toate câmpurile wizardului
mapate; popover „!" temporar = corespondentul din UI vechi. Stocare pe foldere. **Checkpoint de asumare**
(checkbox „om în buclă" care blochează Generează). Calcul fără persistență (`/api/dosar/{uid}/calcul`).
Pagină **/documente** (toate documentele livrate, randate offline). Cross-linkuri UI nou/vechi + Documente +
widget feedback pe **fiecare** pagină (antet+subsol). Paritate: grila de teren tocmai adăugată; **lipsesc încă**
chirii/venit/DCF + anexă foto/documente (gated comercial).

## 6. Ce cerem council-ului
Fiecare model, INDIVIDUAL: **planul tău pentru cum ar trebui definit noul UI** — structură de
pagini/tab-uri/fluxuri, ce arătăm inline vs link, cum tratăm identitatea dosarului + lock-ul, fluxul
Calcul→Generează, descoperirea integrată, paritatea cu wizardul, retragerea UI vechi. **Detaliere + riscuri +
dependențe.** Fii concret și critic. Răspuns în limba română.
