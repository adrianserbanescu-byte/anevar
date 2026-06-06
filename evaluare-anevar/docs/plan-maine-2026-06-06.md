# Plan pentru mâine + stadiu — 2026-06-06 (sesiune autonomă de noapte)

> Document pentru Adi, dimineața. Împărțit în: **(A)** ce am livrat azi-noapte,
> **(B)** decizii care te așteaptă, **(C)** backlog (vechi încă valabil vs. re-fazat),
> **(D)** plan de mâine (brainstorm / features rămase / cross-dependent),
> **(E)** scanare istoric (ce am putea readuce pe masă), **(F)** ce mai dezvolt singur.

---

## A. Ce am livrat azi-noapte (toate testate, 464 teste verzi, exe 50 MB)

| # | Livrare | Unde |
|---|---------|------|
| A1 | **Noul UI „output-first" complet**: cont local → ÎNCEPE (5 opțiuni) → workspace dosar | `web/routers/curent.py`, `templates/curent/*` |
| A2 | **Workspace dosar** cu tab-uri output (Raport/AML/GDPR/Audit/Anexe) + sub-tab-uri (Proprietate/Comparabile/Calcul/Generează) + toate câmpurile wizardului vechi mapate | `templates/curent/dosar.html` |
| A3 | **Popover „!"** lângă fiecare câmp = corespondentul din UI-ul vechi (Pas X) + detaliu (TEMPORAR, dev — îl ștergem ulterior) | `dosar.html` + `_design.css .hint-toggle.is-map` |
| A4 | **Stocare pe foldere** (sursa de adevăr): `date/dosare/<uuid>/dosar.json` + versiuni `.docx`; diff existente/noi/dispărute | `dosare_fs.py` |
| A5 | **Cont „Adi S" (legitimație 8717)**, format `id_client_nume_client_scop_tip_proprietate` | `cont.py`, `scripts/seed_dosare.py` |
| A6 | **4 dosare exemplu importate** din rapoartele Word (Paduraru/Bololoi/Vasilica/Cook) — se încarcă din «Dosare salvate» | `date/dosare/` (seed rulat) |
| A7 | **Import dosar din `.docx`** (filename = identitate sigură + text = beneficiar/scop/dată) — „Importă dosarul tău" e funcțional | `importers/docx_dosar.py`, endpoint `/api/dosar/import-docx` |
| A8 | **Audit import portaluri** (imobiliare/storia/olx) testat **live** pe anunțuri reale de case în Breaza + **2 fixuri de corectitudine** (vezi B-nota) | `importers/url_parser.py` |
| A9 | **Fixuri auto-safe** din 3 audituri (a11y + UX + design): chrome partajat, tab-uri WAI-ARIA, popover accesibil, placeholder în loc de date demo, indicator de salvare real | `dosar.html`, `incepe.html`, `cont.html`, `_design.css` |
| A10 | **Raport Breaza regenerat** (cod la zi, narativ AI real): valoare **135.267 EUR**; atașat la dosarul Breaza | `docs/exemplu-raport-breaza.docx` + `date/dosare/<breaza>/` |
| A11 | **Build .exe** verificat (fără biblioteci inutile — confirmat că se încarcă doar lxml/docx, nu numpy/scipy/etc.) | `dist/evaluare-anevar.exe` (50 MB, pornește în 2s) |

### Fixurile de corectitudine la import (A8) — importante pentru încredere
1. **Date greșite tăcute (HIGH)**: un URL trunchiat/expirat redirecta la o pagină de **listă/căutare**,
   iar aplicația extrăgea **tăcut** prețul unui anunț **promovat nelegat** (ex. storia → „550.000 €/57 mp").
   Acum pagina-listă e **detectată** și **refuzată clar** (nu mai poți primi un comparabil greșit dintr-o
   greșeală de copy-paste). Verificat live.
2. **Teren confundat cu casa (MED)**: OLX „Casă cu 2000mp Teren" → suprafața casei era pusă 2000.
   Acum „mp teren" se atribuie terenului, nu casei. Verificat live.
> Concluzie audit: **imobiliare + storia** extrag corect preț/casă/teren; **OLX** dă prețul dar
> rareori suprafața construită (în date structurate) → importul cere completare manuală (eșec
> *zgomotos*, corect). În Breaza, OLX nu avea anunțuri proprii (a extins căutarea la zone vecine).

**Verificare în browser real** (Playwright, am navigat la anunțuri și am citit ce vede un om):
| Portal | În browser (om) | API parser | Verdict |
|--------|-----------------|-----------|---------|
| imobiliare (Breaza, 226mp) | 138.000 € · utilă 226 · teren 400 | 138000 / 226 / 400 | ✅ identic |
| storia (Breaza de Sus, 255mp) | 239.000 € · 255 · teren 980 | 239000 / 255 / 980 | ✅ identic |
| OLX (175.000 €) | 175.000 € · **fără câmp de suprafață** | 175000 / suprafață None | ✅ corect (lipsa e în date, nu în parser) |
> Deci „API vs. ce citesc eu pe site" = **identic** unde datele există; unde OLX nu are suprafață
> structurată, nici omul n-o vede (e doar în descrierea liberă) → importul cere completare manuală.

---

## B. Decizii care te așteaptă (din audituri + istoric) — le discutăm dimineața

> Astea **nu** le-am implementat singur pentru că schimbă produsul / metodologia / fluxul.

1. **Ordinea de creare a dosarului.** „Dosar nou" creează acum un dosar **gol** și completezi
   identitatea în workspace (am reparat ca numele să nu mai rămână „?_?_?"). Alternativă: un
   pas/modal scurt care cere identitatea **înainte** de a crea folderul. → *Care variantă?*
2. **Blocarea identității după prima generare.** Acum câmpurile rămân editabile cu o notă.
   Trebuie să **forțăm** read-only după prima generare + o cale clară „asta-i dosar nou + credit"?
   *Care e exact declanșatorul (prima generare?) și calea de override?*
3. **„Importă dosarul tău" = ce anume?** Acum importă un **raport `.docx`**. Există în cod și
   `importa_folder()` (adoptă/clonează un **folder** de dosar după legitimație) — neconectat la UI.
   *Le separăm în două acțiuni („Importă raport .docx" vs „Importă folder dosar")?*
4. **`CAMPURI_NUME_DOSAR` vs `CAMPURI_IDENTITATE`.** Formatul numelui poate folosi câmpuri care **nu**
   sunt de identitate (ex. data vizită) → numele se poate schimba la fiecare editare, deși „identitatea"
   se presupune stabilă. *Restrângem formatul doar la câmpuri de identitate?*
5. **Home cu 5 opțiuni, 2 dezactivate** (Import asemănător + Demo = comercial). *Le ținem ca teasere
   sau le ascundem pe build-ul offline ca să iasă în față cele 3 care funcționează?*
6. **Calcul → Generează: o singură sursă de adevăr?** Acum „Generează" reasamblează independent
   (poate diferi de ce ai calculat). *Forțăm „Generează" să ceară un Calcul reușit prima?*
7. **Moneda implicită.** E „LEI" la Calcul, dar garanția bancară e de regulă **EUR**. *Punem EUR
   implicit la scop „garantare"?*
8. **Popover „!" temporar** — confirmi că-l ștergem după ce validezi maparea vechi→nou? (e marcat
   peste tot ca „TEMPORAR/dev").
9. **`pptx` de prezentare** — fișierul `docs/prezentare-aplicatie.pptx` era **deschis în PowerPoint**
   (lock activ), deci **nu l-am regenerat** ca să nu-ți pierd modificările. Îl regenerez când îl
   închizi (sau îl scriu sub alt nume dacă-mi spui).

---

## C. Backlog

### C1. „Ancient backlog" — încă valabil (din `backlog-ux.md`, neînvechit)
| Item | Stare | Notă |
|------|-------|------|
| Ținte tactile 44×44px (WCAG 2.5.5 AAA) | deschis | nu e cerut de AA; estetic îngroașă butoanele pe desktop |
| Densitate „hints" (progressive disclosure în wizard) | deschis | atinge tot wizardul vechi; risc mediu |
| Form clasic `/formular` — paritate de copy | deschis | doar dacă rămâne folosit (vezi C2) |
| Goluri de acoperire: `ai/narrative` 82%, `ocr` 76%, `generator` 88% | deschis | plan: mock-uri pe căile de eroare + fixturi mici |

### C2. „Major re-phase backlog" — re-încadrat după decizia *fără duplicare UI*
| Subiect | Re-încadrare |
|---------|--------------|
| **#1 UI output-first** | **Parțial LIVRAT** (A1-A3). Rămâne: blocare identitate (B2), lock format (B4), conținut real în tab-urile AML/GDPR/Audit/Anexe (acum sunt linkuri/placeholdere) |
| **#2 Rapoarte salvate** | **Stocare LIVRATĂ** (folder=adevăr). Rămâne: partea de **identitate** (depinde de B1-B4) |
| **Wizard vechi + `/formular`** | de **retras treptat** (noul UI = unicul țintă). De decis când oprim întreținerea lor |
| **B — Regenerare text AI** (strict/template/nou per capitol) | **temelie pusă** (importul `.docx` extrage capitole) — de brainstormat fluxul la „Generează" |
| **D — Import „dosar asemănător"** | **temelie pusă** (`docx_dosar` + `importa_folder`) — de brainstormat matricea de merge |
| **#4 Comercializare** (AI gateway) | neschimbat: spec+plan complete, proiect separat cloud, la final |
| **#3 Localități user** | neschimbat: mic, buildabil oricând |

---

## D. Plan de mâine

### D1. De brainstormat (cu tine — sunt decizii de produs/flux)
- **Identitatea dosarului** (B1-B4) — cel mai important, deblochează #2 și metrarea din #4.
- **Fluxul „Generează" cu regenerare text AI** (feature B): per capitol AI, arată textul vechi
  (din ultima sursă), opțiuni Strict/Template/Generare-nouă (matricea `master_administration`) + hints.
- **Conținutul tab-urilor de output** (AML/GDPR/Audit/Anexe în workspace) — ce arătăm inline vs. link.

### D2. Features rămase din topicurile deja abordate
- #2: identitate + credit (post-brainstorm B1-B4).
- #1: lock identitate, lock format nume, retragere wizard vechi.
- B și D (regenerare + import asemănător) — au temelie, le definim fluxul.

### D3. Cross-dependent de brainstorming-uri viitoare
- **Metrarea per raport (#4)** depinde de definiția finală a **identității** (#1/#2).
- **Regenerarea AI (B)** depinde de **matricea master_administration** (stări strict/template/nou) —
  de confirmat conținutul matricei.
- **Import asemănător (D)** depinde de aceeași matrice + de regula adoptă/clonează (legitimație).

---

## E. Scanare istoric — ce am putea readuce pe masă acum
- **`/formular` (form clasic)** — pagină secundară fără trecerea de UX-copy; cu noul UI, probabil
  o retragem. *De confirmat.*
- **Localități user (#3)** — cel mai mic feature, buildabil imediat, util la review. Nu l-am atins.
- **Extensia de browser** (`spec-extensie-browser.md`) — importul prin extensie există; merită un
  test e2e dedicat și un buton clar în noul UI (acum importul URL e în pagini separate).
- **Goluri de acoperire `ocr`/`narrative`** — de redus cu fixturi mici (nu necesită tine).
- **`portal_search` (discovery)** — la audit am văzut că extragerea listei prinde **anunțuri
  promovate cross-categorie** (ex. licențe taxi pe căutarea de case). De călit (filtru pe categorie).

---

## F. Ce mai dezvolt singur (fără să te aștept) — în ordine
1. **Test e2e nou-UI** în `_pw_smoke.py` (cont → ÎNCEPE → dosar nou → completare → calcul → generează).
2. **Călire `portal_search`**: ignoră anunțurile promovate/cross-categorie la descoperire (bug din audit E).
3. **Reduc golurile de acoperire** `ocr`/`narrative` cu fixturi mici + căi de eroare.
4. **#3 Localități user** dacă rămâne timp (mic, izolat, buildabil).
5. La fiecare pas: teste + lint + (la final) **rebuild exe**.

> Tot ce e în **F** îl fac autonom. Tot ce e în **B/D1** te așteaptă pe tine.
