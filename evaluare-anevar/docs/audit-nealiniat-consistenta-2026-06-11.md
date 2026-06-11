# Audit funcționalitate nealiniată (consistency / cross-surface) — 2026-06-11

READ-ONLY. App ANEVAR (evaluare casă+teren pentru garantare credit). Persona = evaluator autorizat.
Scop: vânătoare SISTEMATICĂ a divergențelor de comportament între aceeași funcție expusă în locuri
diferite (workspace dosar inline vs pagini standalone /descoperire, /grila, /aml), drift
spec↔implementare, propagare de date stricată, concepte numite/formatate diferit, validări
inconsistente.

Surse principale analizate:
- Workspace dosar (inline): `src/evaluare/web/templates/curent/dosar.html` (1518 linii)
- Standalone: `templates/descoperire.html`, `templates/grila.html`, `templates/aml.html`
- Routere: `web/routers/{descoperire,grile,aml,curent,evaluare}.py`
- Motoare: `engine/{market,land,chirie}.py`; modele: `models/comparable.py`, `discovery/profiles.py`
- Portaluri: `discovery/portal_search.py`, `discovery/orchestrator.py`

---

## Rezumat sever (cele mai importante)

| # | Titlu | Sev | Tip |
|---|-------|-----|-----|
| N1 | Etichete monedă divergente la grila casă/chirii: „lei" (dosar) vs „EUR" (/grila) | high | nealiniat |
| N2 | Portal imoradar24.ro disponibil în /descoperire, dar lipsește în descoperirea inline din dosar | high | nealiniat |
| N3 | `nr_camere` nu se propagă din dosar la descoperirea inline → filtrul de apartament e dezactivat inline | high | nealiniat |
| N4 | Validare suprafață subiect inconsistentă între grila-casa/teren (acceptă ≤0) și grila-chirii (respinge) | high | nealiniat |
| N5 | Cap future-date pe `azi` lipsește în /aml standalone (există inline) + dată default hardcodată stale | medium | nealiniat |
| N6 | Câmpul „Valoare teren (lei)" pe Proprietate vs moneda EUR a calculului — unitate ambiguă | medium | nealiniat |
| N7 | Default `max_candidati` necontrolabil inline (hardcodat 20) vs control 1–50 în /descoperire | medium | nealiniat |
| N8 | Limita de 3 comparabile (NCOMP/NC) e hardcodată identic în ambele grile dar diferă de fluxul „n din medie" | low | nealiniat |
| N9 | „Componente non-imobiliare (mobilier)" lipsește la prima poziție etapă în dosar vs ordine /grila | low | nealiniat |

---

## N1 — Etichete monedă divergente la grilele de ajustări (high)

**Locul A** `templates/grila.html` (pagina standalone /grila):
- casă L144: `{nume:"Suprafață teren (EUR/mp × Δ)", tip:"valorica"}`
- casă L145: `{nume:"Arie utilă (EUR)", tip:"valorica"}`
- chirii L163: `{nume:"Cheltuieli incluse (ajustare EUR/mp)", tip:"valorica"}`

**Locul B** `templates/curent/dosar.html` (grilă inline din workspace):
- casă L1255: `{nume:"Suprafață teren (lei)",tip:"valorica"}`
- casă L1256: `{nume:"Arie utilă (lei)",tip:"valorica"}`
- chirii L1372: `{nume:"Cheltuieli incluse (lei/mp)",tip:"valorica"}`

**Cum diferă:** aceeași grilă, același endpoint backend (`/api/grila-casa`, `/api/grila-chirii`),
dar ajustările valorice sunt etichetate **EUR** în pagina standalone și **lei** în workspace.
Ajustarea valorică se adună direct la prețul comparabilului (în EUR, fiindcă comparabilele de
descoperire sunt în EUR). Un evaluator care urmează eticheta „lei" din dosar va introduce o sumă de
ordin de mărime greșit (~5× la cursul EUR≈4.97), poluând valoarea de piață/teren cu o eroare gravă.

**Care e corect:** EUR (motorul nu convertește; prețurile comparabilelor sunt EUR). Eticheta „lei"
din dosar e greșită.

**Fix:** Aliniază etichetele din `dosar.html` la „EUR"/„EUR/mp" ca în `grila.html`. Ideal: extrage
catalogul ELEM (casă/teren/chirii) într-un singur fișier JS partajat (`_helpers.js` sau un nou
`_grile_elem.js`) inclus de ambele template-uri, ca să nu mai existe două definiții care pot drifta.

## N2 — Portalul imoradar24.ro lipsește în descoperirea inline (high)

**Locul A** `templates/descoperire.html` L110-111: select portal cu 3 opțiuni —
`imobiliare`, `storia`, **`imoradar`** (imoradar24.ro).
Backend: `discovery/portal_search.py` L22, L36-38 — imoradar e complet implementat (segmente URL
casă/apartament/teren).

**Locul B** `templates/curent/dosar.html`:
- L266-267: select `d-portal` are doar `toate`/`imobiliare`/`storia` (fără imoradar).
- L1003: `var PORTALURI=["imobiliare","storia"];` — „toate portalurile" inline exclude imoradar.

**Cum diferă:** workspace-ul dosarului (suprafața PRINCIPALĂ de lucru) nu poate căuta pe imoradar24.ro,
deși backend-ul îl suportă și pagina standalone îl oferă. „Toate portalurile" inline e o promisiune
incompletă (acoperă 2 din 3).

**Care e corect:** suportul backend + standalone = imoradar e valid. Inline ar trebui să-l includă.

**Fix:** Adaugă `<option value="imoradar">imoradar24.ro</option>` la `#d-portal` și
`var PORTALURI=["imobiliare","storia","imoradar"];` în dosar.html. (Notă: portal_search bază
`BAZE`/`_SEGMENT` deja conține imoradar — zero schimbare backend.)

## N3 — `nr_camere` nu se propagă la descoperirea inline → filtrul de apartament e dezactivat (high)

**Locul A** `templates/descoperire.html` L498-500: payload `subiect` include
`nr_camere:parseInt(d.nr_camere)||null`. Câmpul „Nr. camere" e expus (L127) când tip=apartament.

**Locul B** `templates/curent/dosar.html` L1067-1072 (`cerePortal`): obiectul `subiect` trimis la
`/api/descopera` conține `suprafata_construita`, `an`, `stare`, `finisaj`, `incalzire`, `teren` —
**dar NU `nr_camere`**. Workspace-ul nu are deloc un câmp „Nr. camere" pentru subiect în sub-tabul
Comparabile (există `etaj`/`an_bloc` la apartament pe Proprietate, dar nu nr. camere transmis la căutare).

**Efect downstream:** `discovery/orchestrator.py` L141-147, L209-212 — `_apartament_exclus()` filtrează
candidații cu >1 cameră diferență față de subiect, DAR doar dacă `subiect.nr_camere is not None`. Cu
descoperirea inline (nr_camere mereu None), filtrul de eligibilitate la apartament e tăcut dezactivat
→ se întorc apartamente cu nr. de camere foarte diferit, deși din standalone ar fi excluse.

**Care e corect:** standalone (trimite nr_camere → filtru activ, conform fix-ului #3 apartament).

**Fix:** Adaugă un câmp „Nr. camere" în sub-tabul Comparabile (sau pre-completează din date fizice
apartament) și include `nr_camere:parseInt(...)||null` în `subiect` la `cerePortal` în dosar.html.

## N4 — Validare suprafață subiect inconsistentă între grile (high)

**Locul A** `engine/chirie.py` L74-75: `if suprafata_subiect <= 0: raise ValueError(...)` → endpoint
`/api/grila-chirii` întoarce 422 clar la suprafață ≤0.

**Locul B** `engine/market.py` (`evaluate_market`) — `suprafata_subiect` nu mai intră în formulă și
NU e validat; `engine/land.py` L111 — `valoare = pret_ales * suprafata_subiect` fără gardă pe semn.
Schemele `GrilaCasaRequest`/`GrilaTerenRequest` (`web/schemas.py` L90-98) cer doar
`suprafata_subiect: Decimal` (fără `gt=0`).

**Cum diferă:** la suprafață subiect = 0 sau negativă:
- grila-chirii → 422 (respins, corect).
- grila-casa → 200 (acceptat — suprafața subiect e ignorată, dar tăcut).
- grila-teren → 200 cu `valoare_teren` negativă/zero (pret_ales × suprafață negativă).

Trei endpoint-uri „frați" tratează aceeași intrare invalidă diferit. (Confirmat și de observația
internă 5359.)

**Care e corect:** respingerea (ca la chirii). O suprafață ≤0 nu produce o estimare utilă; teren mai
ales emite o valoare negativă.

**Fix:** Adaugă `Field(gt=0)` pe `suprafata_subiect` în cele 3 scheme grilă (sau validare în
`evaluate_land`/`evaluate_market` simetrică cu `evalueaza_chirie`). Aliniază mesajul 422.

## N5 — Cap future-date lipsă pe `azi` în /aml standalone + dată default hardcodată (medium)

**Locul A** `templates/curent/dosar.html` L858-867: TOATE `input[type=date]` (inclusiv `aml_azi`)
primesc `d.max=azi` și clamp `if(d.value>azi) d.value=azi`. Inline, data AML nu poate fi în viitor.

**Locul B** `templates/aml.html` L48: `<input type="date" id="azi" value="2026-06-03">` — fără
`max`, fără clamp, și cu o **dată default hardcodată stale** (3 iunie 2026). Standalone-ul nu include
`_helpers.js` și nu are logica de clamp din dosar.

**Cum diferă:** pe pagina /aml standalone evaluatorul poate seta data evaluării AML în viitor; inline
nu. În plus, /aml pornește cu o dată fixă din trecut (nu „azi"), inducând o dată greșită pe documentele
AML generate dacă nu e schimbată manual.

**Care e corect:** comportamentul inline (max=azi, default = azi).

**Fix:** În aml.html, înlocuiește `value="2026-06-03"` cu populare din JS la `new Date()...slice(0,10)`,
adaugă `max` = azi + clamp (reutilizează blocul din dosar.html L858-867 sau mută-l în `_helpers.js`).

## N6 — „Valoare teren (lei)" pe Proprietate vs moneda EUR a calculului (medium)

**Locul A** `templates/curent/dosar.html` L216: câmpul subiect `valoare_teren` etichetat
„Valoare teren (lei)". Hint L216: „opțional — manual; sau din grila de teren".

**Locul B** `assembler.py` L182-189, L241-242: `valoare_teren` intră în `evaluate_cost` și în
`aloca_constructii` ca valoare absolută, fără conversie de monedă. Dacă moneda raportării e EUR
(default în Calcul, `dosar.html` L356 `<option value="EUR" selected>`), valoarea terenului introdusă
„în lei" se amestecă cu o bază de cost/valoare în EUR. Mai mult, grila de teren produce
`valoare_teren` în EUR (prețuri comparabile EUR/mp), iar acel rezultat suprascrie câmpul „(lei)".

**Cum diferă:** eticheta spune „lei", dar pipeline-ul tratează numărul în moneda activă (de regulă EUR),
iar sursa alternativă (grila) îl umple în EUR. Concept (valoare teren) etichetat cu o unitate care nu
se potrivește cu fluxul.

**Care e corect:** unitatea trebuie să fie moneda raportării (EUR la garantare), nu „lei" fix.

**Fix:** Schimbă eticheta în „Valoare teren ({{moneda}})" sau scoate unitatea fixă și clarifică în
hint că e în moneda aleasă la Calcul; sau convertește explicit la curs dacă rămâne în lei.

## N7 — Control `max_candidati` absent inline (medium)

**Locul A** `templates/descoperire.html` L129-131: input numeric „Câte comparabile" (1–50, default 20),
trimis ca `max_candidati: maxc` (clamp 1–50, L489).

**Locul B** `templates/curent/dosar.html` L1066, L1072: `max_candidati:20` hardcodat în ambele ramuri
(`/api/descopera` și `/api/descopera-teren`). Workspace-ul nu expune niciun control.

**Cum diferă:** backend-ul + schema acceptă orice `max_candidati` (default 20, configurabil — vezi
`schemas.py` L87, L111 și fix-ul „8→20 configurabil"). Standalone oferă controlul; workspace îl fixează
mut la 20. Un evaluator în dosar nu poate cere mai multe/mai puține comparabile.

**Care e corect:** ambele variante sunt funcționale, dar capacitatea diferă fără motiv. Workspace-ul
(suprafața principală) ar trebui să ofere cel puțin paritate.

**Fix:** Adaugă un input „Câte comparabile (1–50)" în sub-tabul Comparabile și folosește-l în `cerePortal`,
identic cu /descoperire.

## N8 — Limita de 3 comparabile hardcodată în grilele inline + standalone (low)

**Locul A** `templates/grila.html` L107: `const NCOMP = 3;` (toate cele 3 grile standalone).
**Locul B** `templates/curent/dosar.html` L1246, L1310, L1364: `var NC=3;` (×3, câte una per grilă inline).

**Cum diferă:** consistent între A și B (ambele 3), DAR motorul M2 mediază „cele mai similare N
comparabile" (`cfg.nr_comparabile_medie`, `engine/*.py`) și acceptă liste mai lungi. UI-ul (ambele
suprafețe) plafonează rigid la 3 coloane, deci un evaluator nu poate introduce >3 comparabile în grilă,
deși standardul cere minim 3 și motorul suportă mai multe. E o limită UI replicată în 4 locuri, ușor
de driftat la o viitoare editare.

**Care e corect:** ≥3 (minim legal), dar nu plafonat la exact 3; cel puțin trebuie să fie aceeași
valoare în toate cele 4 definiții (acum coincid, dar prin coincidență, nu prin sursă unică).

**Fix:** Centralizează `NCOMP` într-o singură constantă partajată; permite adăugarea de coloane
(„+ comparabil") ca la grid-urile editabile de cost. Cel puțin: comentariu + constantă unică pentru a
preveni driftul.

## N9 — Ordine/conținut elemente grilă casă ușor divergente (low)

**Locul A** `templates/grila.html` L136-153 (casă, 16 elemente): include „Componente non-imobiliare
(mobilier)" pe poziția 2.
**Locul B** `templates/curent/dosar.html` L1247-1264 (casă, 16 elemente): ordine identică, dar e o a
doua copie manuală a aceleiași liste (plus diferența de unitate din N1).

**Cum diferă:** listele coincid azi ca elemente/ordine (bun), dar sunt întreținute separat — orice
adăugare/reordonare într-un loc nu se reflectă în celălalt. Combinat cu N1 (unități deja divergente),
e dovada că cele două cataloage au început deja să drifteze.

**Care e corect:** o singură sursă de adevăr.

**Fix:** Vezi N1 — extrage catalogul ELEM într-un modul JS partajat inclus de ambele template-uri.

---

## Notă transversală

Cauza-rădăcină comună a N1, N8, N9: **grilele inline din `dosar.html` sunt un port manual (copy-paste)
al `grila.html`**, fără sursă comună. Comentariile din cod o spun explicit („port din grila.html").
Driftul a început deja (unitățile EUR↔lei). Recomandare prioritară: un singur catalog ELEM + un singur
set de helpere de grilă, incluse de ambele suprafețe. Similar pentru descoperire (N2, N3, N7): inline
și standalone construiesc payload-ul `/api/descopera` separat, cu seturi de câmpuri ușor diferite.
