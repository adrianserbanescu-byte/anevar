# Audit UX — workspace dosar, tab „Raport" → sub-tab „Proprietate" (2026-06-11)

**Scop:** brief de layout pentru următorul agent care reface sub-tabul „Proprietate" din
`src/evaluare/web/templates/curent/dosar.html`. READ-ONLY — acest raport NU modifică `dosar.html`
(alt agent îl atinge). Feedback Adi: „UI prost" — formular înghesuit, prea multe `?`,
paginare/spațiere proastă, câmpuri aglomerate.

**Zona auditată:** `<section id="sp-proprietate">` — liniile **51–176** din `dosar.html`
(versiunea de la commit `f684b63`). Conține două blocuri mari: **„Identificare"** (L63–120) și
**„Date fizice"** (L121–175).

---

## 1. Harta actuală a sub-tabului (ce e acolo, în ordine)

| # | Bloc / `field-row` | Linii | Câmpuri | Observație |
|---|---|---|---|---|
| 0 | `<details>` Pre-completare din documente (extras CF/releveu) | 52–62 | tip doc + fișier | OK ca accordion |
| 1 | H3 **Identificare** | 63 | — | un singur H3 pentru ~20 câmpuri eterogene |
| 2 | ID client · Nume client | 72–75 | 2 | identitate client |
| 3 | Scop · Tip proprietate | 76–86 | 2 (select) | parametri evaluare — alt concern decât client |
| 4 | Județ · Localitate (+alt) · Stradă | 87–93 | 3 | localizare |
| 5 | Nr. cadastral · Carte funciară · Proprietar · Beneficiar | 94–99 | 4 | mix: cadastral + **părți** (proprietar/beneficiar) |
| 6 | Dreptul evaluat · Act proprietate · Sarcini/grevări | 100–107 | 3 | regim juridic |
| 7 | Data raport · Data evaluării · Data vizită | 108–112 | 3 | date |
| 8 | (small) notă „Data evaluării goală → azi" | 113 | — | notă liberă între rânduri |
| 9 | Amploare inspecție · Însoțitor · Observații inspecție | 114–120 | 3 | inspecție |
| 10 | H3 **Date fizice** | 121 | — | — |
| 11 | `fieldset` Apartament (hidden) | 122–129 | 4 | type-specific |
| 12 | `fieldset` Industrial (hidden) | 130–132 | 1 | type-specific |
| 13 | `fieldset` Teren agricol (hidden) | 133–141 | 2 | type-specific |
| 14 | `#grup-teren`: suprafață · regim · valoare teren | 142–148 | 3 | teren |
| 15 | `fieldset` Utilități (5 checkbox) | 149–156 | 5 | teren |
| 16 | Cale de acces (full-width) | 157–158 | 1 | teren |
| 17 | Regim urbanistic / restricții (full-width) | 159–160 | 1 | teren |
| 18 | `#grup-constructie`: Au · Acd · An referință | 162–167 | 3 | construcție |
| 19 | `#grup-cost`: Elemente de cost · Depreciere (2× textarea) | 168–174 | 2 | cost |

Total: **~35 câmpuri** vizibile/condiționale sub **doar 2 titluri** (H3 „Identificare" și
H3 „Date fizice"). Aceasta e cauza-rădăcină a senzației de „înghesuit": densitate mare,
ierarhie vizuală minimă.

---

## 2. Probleme CONCRETE de layout

### P1 — „Identificare" e un sac cu 5 concern-uri diferite, fără separatoare (L63–120)
Sub un singur `<h3>Identificare</h3>` stau, la rând, grupuri care nu au legătură vizuală:
1. **Client** (ID, nume) — L72–75
2. **Parametrii evaluării** (scop, tip proprietate) — L76–86
3. **Localizare** (județ, localitate, stradă) — L87–93
4. **Identificare cadastrală + părți** (nr. cadastral, CF, proprietar, beneficiar) — L94–99
5. **Regim juridic** (drept evaluat, act, sarcini) — L100–107
6. **Date-cheie** (raport, evaluare, vizită) — L108–112
7. **Inspecție** (amploare, însoțitor, observații) — L114–120

Pentru un evaluator, „scop + tip proprietate" și „date inspecție" sunt etape mentale distincte;
acum totul curge într-un singur perete de câmpuri. **Nimic nu marchează unde se termină un grup
și începe altul** → ochiul nu are puncte de odihnă (lipsa „chunking"-ului).

### P2 — Prea multe `?` hint-toggle, injectate automat pe APROAPE FIECARE câmp (L560–612)
`AJUTOR` (L560–592) are **~30 de intrări**; din care **~22 cad în sub-tabul Proprietate**
(id_client, nume_client, scop, tip_proprietate, judet, localitate, adresa_strada, numar_cadastral,
carte_funciara, beneficiar, data_raportului, data_evaluarii, data_inspectiei, suprafata_teren,
valoare_teren, au, acd, an_referinta, elemente, depreciere, comparabile, comparabile_teren).
Loop-ul L608–612 pune un buton `?` lângă **fiecare** `label[for]` care are intrare în `AJUTOR`.
Rezultat: un rând de 3–4 câmpuri ajunge să aibă 3–4 butoane `?` mici → zgomot vizual constant,
exact reclamația lui Adi. Multe popovere sunt triviale și nu merită un control dedicat
(ex. `localitate:"Localitatea proprietății."`, `suprafata_teren:"Suprafața terenului (mp)."`,
`adresa_strada:"Strada și numărul; apar în raport."`).

### P3 — Hint-uri DUBLATE: paranteză în label + popover `?` pe același câmp
Câteva câmpuri au și hint inline în `<label>`, ȘI un `?` popover injectat — informație concurentă:
- `beneficiar` — label „(banca finanțatoare)" (L98) **+** popover „Banca finanțatoare / utilizatorul…" (L570)
- `valoare_teren` — label „(opțional — manual; sau din grila…)" (L147) **+** popover „Valoarea terenului (manual; sau…)" (L575)
- `data_evaluarii` — popover (L572) **+** small separat „ℹ️ Data evaluării: dacă o lași goală…" (L113)

Aceeași idee spusă de 2 ori, în 2 stiluri (paranteză gri vs. popover) → redundanță + inconsistență.
Alte labels au DOAR hint inline, fără popover (proprietar, sarcini, acces, restrictii_urbanism) →
inconsistență invers: când e paranteză, când e `?`, fără regulă.

### P4 — Spațiere/ritm vertical neuniform
- Note libere („small" / „ℹ️") inserate ÎNTRE `field-row`-uri (L113, L171) rup ritmul de grilă —
  apar ca text orfan între rânduri de inputuri.
- Override-ul local din `<head>` (L11–13) face `main .field-row` un **grid** `auto-fill minmax(200px,1fr)`,
  dar `_design.css` (L196) îl definește global ca **flex** cu `flex:1 1 160px`. Cele două modele de
  layout coexistă; orice câmp pus în afara unui `.field-row` (ex. „Cale de acces", L157;
  „Regim urbanistic", L159 — `.field`/`label` libere, nu în rând) nu mai prinde aliniere pe grid →
  marginile-stânga „sar" față de rândurile de deasupra.
- `fieldset`-urile type-specific (Apartament/Industrial/Agricol, L122–141) au fiecare `<legend>` +
  bordură; când devin vizibile se amestecă vizual cu `fieldset` Utilități (L149) → 2 stiluri de
  „cutie" (legend-box) în aceeași coloană, fără ierarhie clară între ele.

### P5 — Câmpuri aglomerate pe rând (lățimi inegale + truncare label)
- L94–99: **4 câmpuri** pe un rând (cadastral, CF, proprietar, beneficiar). Pe grid `minmax(200px)`
  asta cere ≥800px ca să nu wrap-eze; sub atât, al 4-lea cade pe rândul 2 singur → rând „șchiop".
- Labels lungi cu paranteză („Sarcini / grevări (extras CF) (ipoteci, servituți…)", L106;
  „Observații / neconcordanțe la inspecție", L119) într-un `.field` de 200px → label pe 2–3 rânduri,
  care împinge inputul în jos doar pe acea coloană → rânduri cu înălțimi inegale, aspect „zimțat".
- `flex:2` pe câmpuri „late" (sarcini L106, observatii L119, inspecție L119) e setat **inline**
  (`style="flex:2"`) și „tradus" în grid prin `grid-column:span 2` (head L13) — funcționează, dar e
  un hack fragil: lățimea „specială" e hardcodată pe câmp, nu derivă dintr-un sistem.

### P6 — Lipsă progres / orientare în formularul lung
Sub-tabul „Proprietate" e cel mai lung din workspace, dar nu are niciun indicator de secțiune
(doar 2 H3). Nu există ancore/sub-navigație internă; userul derulează un perete de inputuri fără
să știe „unde e" sau cât mai are. (Există navigare între SUB-TAB-uri jos — `nav-inapoi`/`nav-inainte`,
L1242–1243 — dar nimic în interiorul sub-tabului „Proprietate".)

---

## 3. Recomandări de fix (pentru agentul de layout)

### R1 — Sparge „Identificare" în 4–5 secțiuni cu titlu propriu (rezolvă P1, P6)
Înlocuiește singurul `<h3>Identificare</h3>` cu sub-secțiuni clare (H3 sau `<fieldset><legend>`):
1. **Client & scop** — ID client, nume, scop, tip proprietate
2. **Localizare** — județ, localitate, stradă
3. **Identificare cadastrală & părți** — nr. cadastral, CF, proprietar, beneficiar
4. **Regim juridic** — drept evaluat, act, sarcini/grevări
5. **Date & inspecție** — data raport/evaluare/vizită + amploare/însoțitor/observații
Fiecare secțiune cu spațiere generoasă deasupra (ex. `margin-top:28px` + un `hr.brass-rule` ușor,
clasa există deja, vezi `dosar.html` L225). Asta dă „chunking" și puncte de odihnă.

### R2 — Reducere drastică `?` popovere (rezolvă P2)
Păstrează popover-ul `?` DOAR pe câmpurile unde explicația e ne-evidentă / cu format/calcul:
`elemente`, `depreciere`, `au`/`acd` (relația Au≤Acd, CIN), `data_evaluarii` (regula „goală→azi"),
`comparabile`/`comparabile_teren` (formatul `preț;suprafață`), `rata_cap`/`vbp`/`fluxuri` (dacă apar).
Elimină din `AJUTOR` intrările tautologice (localitate, judet, suprafata_teren, adresa_strada,
nume_client, id_client etc.) — un label clar nu are nevoie de popover. Țintă: de la ~22 la ~6–8 `?`
în sub-tab. (Mecanic: scoți cheia din `AJUTOR`, L560–592; loop-ul L608 nu mai injectează nimic.)

### R3 — O singură sursă pentru hint, nu două (rezolvă P3)
Pentru fiecare câmp, alege UN canal: ori paranteză inline (hint scurt, mereu vizibil), ori popover
`?` (explicație lungă, la cerere) — nu ambele. Recomandare: paranteză pentru hint ≤4 cuvinte,
popover pentru restul. Elimină dublurile la `beneficiar`, `valoare_teren`, `data_evaluarii`
(scoate fie paranteza, fie intrarea din `AJUTOR`, fie nota „small" separată de la L113).

### R4 — Normalizează grila și ritmul (rezolvă P4, P5)
- Pune TOATE câmpurile în `.field-row` (inclusiv „Cale de acces" L157 și „Regim urbanistic" L159,
  acum libere) ca să prindă același grid → margini-stânga aliniate pe verticală.
- Maxim **3 câmpuri/rând** în zonele dense (sparge rândul de 4 de la L94–99 în 2+2) ca să eviți
  rândul „șchiop" sub 800px.
- Mută notele orfane („ℹ️" L113, „small" L171) ca hint atașat câmpului relevant, nu text liber
  între rânduri.
- Unifică modelul de „cutie": fie fieldset-uri pentru toate grupurile, fie niciunul + titluri H3 —
  nu amesteca `fieldset`+`legend` (Utilități, type-specific) cu H3 simple în aceeași coloană.
- Înlocuiește `style="flex:2"` inline cu o clasă utilitară (ex. `.field--wide`) ca lățimea „specială"
  să fie sistemică, nu hardcodată pe câmp.

### R5 — (opțional) sub-navigație internă pentru sub-tabul lung (rezolvă P6)
Dacă rămâne lung, adaugă un mini-index ancore sus („Client · Localizare · Cadastral · Juridic ·
Date · Date fizice") care derulează la fiecare secțiune. Low-effort, mare câștig de orientare.

---

## 4. Note pentru implementare
- **Aliniere la sistemul existent:** există deja `.btn-bar` / `.btn-bar-jos`, `hr.brass-rule`,
  `fieldset>legend` stilat, `.field-row`/`.field` — refolosește-le, nu inventa componente noi
  (estetică Rams, `_design.css`).
- **Atenție la persistență:** `snapshot()`/`restore` (L620+) iterează `main input,select,textarea`
  după `id`. Orice câmp regrupat TREBUIE să-și păstreze `id`-ul, altfel se pierde la salvare
  (vezi comentariul existent L150 despre checkbox-uri fără id). Regruparea = doar mutare în DOM +
  titluri/spațiere, NU redenumire de id-uri.
- **Tab-uri:** „Proprietate" e sub-tabul implicit (`aria-selected="true"`, L44) — orice agent care
  vine din `/grila` prin butonul „◀ Înapoi la dosar" aterizează aici, deci e prima impresie a
  workspace-ului. Merită prioritizat.

---

*Audit întocmit read-only; nu s-a modificat `dosar.html`. Referințe de linie = commit `f684b63`.*
