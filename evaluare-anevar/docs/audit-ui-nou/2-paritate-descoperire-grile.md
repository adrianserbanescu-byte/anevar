# Audit paritate — Modulul de descoperire comparabile + grile de ajustare (UI vechi vs. UI nou)

**Data:** 2026-06-06
**Scop:** audit FUNCȚIONAL (frontend + backend) de paritate pe modulul de descoperire comparabile și grilele de ajustare, între UI vechi (`/descoperire`, `/grila`) și UI nou (`/dosar/{uid}`, sub-tabul Comparabile). NU accesibilitate.

**Reclamația owner-ului:** „Ai TĂIAT modulul de căutare în noul UI" + „subtabul Comparabile cerea informații pentru a le găsi, au dispărut."

**Verdict scurt: RECLAMAȚIA E CONFIRMATĂ.** Tot modulul de căutare (formular + tabel rezultate + scoring + bifare + import-în-grilă) și cele 3 grile de ajustare pe etape EXISTĂ și sunt funcționale, dar **EXCLUSIV în UI-ul vechi**. În UI-ul nou, sub-tabul Comparabile e redus la 2 `textarea` libere (`preț;suprafață`) + 2 link-uri externe (`↗`) către paginile vechi. Backend-ul e intact și NU e orfan — paginile vechi sunt încă montate și funcționale; doar nu sunt re-folosite *inline* în UI-ul nou.

---

## Tabel de paritate

| Funcție (vechi) | În UI nou? | Dovadă (fișier:linii) | Impact |
|---|---|---|---|
| **Formular căutare casă** (portal + județ + localitate) | ❌ | vechi: `descoperire.html:26-30`; nou: absent — `dosar.html:84-92` (doar textarea + link) | Mare — utilizatorul nu poate căuta comparabile fără a părăsi dosarul |
| **Atribute subiect casă** (an, stare 1-5, finisaj 1-4, încălzire, teren) ca input pt. scoring | ❌ | vechi: `descoperire.html:31-35`; nou: absent în sub-tabul Comparabile | Mare — exact „informațiile cerute ca să le găsească" reclamate de owner |
| **Atribute secundare** (textarea „nume: valoare") pt. scoring | ❌ | vechi: `descoperire.html:36-37`; nou: absent | Mediu — pierde rafinarea relevanței |
| **Buton „Caută comparabile"** + apel `POST /api/descopera` | ❌ | vechi: `descoperire.html:38`, `:157-201`; backend viu: `descoperire.py:22-42` | Mare — căutarea casă nu se declanșează din UI nou |
| **Tabel rezultate cu scor de relevanță** (badge %, atribute, explicație) | ❌ | vechi: `descoperire.html:141-156` (`randCandidat`, `tabelAtribute`); nou: absent | Mare — niciun rezultat vizibil inline |
| **Bifare candidați + „Trimite la grila casă"** (prefill via `localStorage`) | ❌ | vechi: `descoperire.html:147`, `:191-200`; consumat de `grila.html:163-176` | Mare — fluxul descoperire→grilă rupt în UI nou |
| **Copiere comparabile bifate** (`pret;suprafata`) | ❌ | vechi: `descoperire.html:184-190` | Mic — workaround manual posibil |
| **Descoperire TEREN** (formular + `POST /api/descopera-teren` + „➕ grilă") | ❌ | vechi: `grila.html:34-45`, `:228-254`; backend viu: `descoperire.py:44-55` | Mare — căutarea de terenuri lipsește complet din UI nou |
| **Grilă TEREN** — ajustări pe etape (tranzacție 6 + proprietate 11), preț/mp×supr | ❌ | vechi: `grila.html:26-47`, `ELEM.teren` `:81-93`; backend viu: `grile.py:17-27` | Mare — în UI nou doar `textarea` `preț/mp;suprafață` (`dosar.html:89-90`) |
| **Grilă CASĂ** — 16 elemente, %/EUR, etape, arie utilă EUR/mp×Δ | ❌ | vechi: `grila.html:49-60`, `ELEM.casa` `:94-111`; backend viu: `grile.py:29-38` | Mare — în UI nou doar `textarea` `preț;suprafață` (`dosar.html:87-88`) |
| **Grilă CHIRII** — 9 elemente → VBP anual → wizard venit | ❌ | vechi: `grila.html:62-72`, `ELEM.chirii` `:112-122`; backend viu: `grile.py:40-54` | Mare — abordarea prin venit din chirii nu are intrare în UI nou |
| **Selecție comparabil pe ajustare brută minimă + alerte prudențiale (🚩 25%/15%)** | ❌ | vechi: `grila.html:274-310` (`afiseaza`); nou: absent (calcul direct fără grilă) | Mare — control GEV 520 pierdut în fluxul UI nou |
| **Indicele imobiliar ANEVAR** (`/api/indice-anevar`) pt. ajustarea „timp" | ❌ | vechi: `grila.html:16-18`, `:204-218`; backend viu: `piata.py:83-93` | Mediu — ajutor de ajustare „condițiile pieței" indisponibil inline |
| **Import URL anunț** (`POST /api/import-url`) | 🟡 | backend viu: `piata.py:20-41`; UI vechi-wizard îl folosește; **niciun buton în UI nou** (`dosar.html` n-are apel) | Mediu — endpoint orfan față de UI nou (doar import .docx există: `curent.py:56-85`) |
| **Import din extensia de browser** (coadă anunțuri → grila casă) | ❌ | vechi: `descoperire.html:16-24`, `:52-107`; backend viu: `descoperire.py:57-93` | Mediu — secțiunea „Anunțuri importate din extensie" + „Trimite la grilă" lipsesc din UI nou |
| **Metodologie scoring** (tabel ponderi/cote/formulă) | ❌ | vechi: `descoperire.html:109-117` + `scoring.py:151` `metodologie()`; backend viu | Mic — transparență metodologică pierdută inline |
| **Avertisment ofertă→tranzacție** (GEV 520 §4.3.4) | 🟡 | vechi: `descoperire.html:10-14`, `grila.html:10-17`; nou: parțial (mențiuni în mapare `dosar.html`, fără bannerul explicit pe comparabile) | Mic — risc de conformitate redus, dar prezent ca text de ghidare |

Legendă: ✅ prezent inline în UI nou · 🟡 parțial / accesibil indirect · ❌ absent din UI nou (există doar în UI vechi).

---

## Verificările explicite cerute

**(1) Sub-tabul Comparabile din UI nou mai are formular de CĂUTARE (descoperire)?**
**NU.** `dosar.html:84-92` conține: un `<p class="hint">` cu link extern „Descoperire ↗" (`/descoperire`, `target="_blank"`), `textarea#comparabile` (`preț;suprafață`), `textarea#comparabile_teren` (`preț/mp;suprafață`) și un al doilea link „Grile ↗" (`/grila`). **Nu există** niciun input județ/localitate, selector portal, atribute subiect, buton „Caută", tabel rezultate, badge de relevanță sau checkbox de bifare. Confirmat și prin căutare: niciun `judet|localitate|portal|Caut|bif|checkbox|relevant|scor` în `curent/incepe.html` și niciun astfel de element în `curent/dosar.html` (doar câmpurile de identitate `judet`/`localitate` ale proprietății la `:53-54`, fără rol de căutare). → **Reclamația owner-ului „au dispărut" este corectă.**

**(2) Cele 3 grile (teren/casă/chirii) cu ajustări pe etape există în UI nou?**
**NU — doar `textarea` simplu.** Grilele complete (tabele cu 9-17 elemente de ajustare, `procentuala`/`valorica`, etapă tranzacție vs. proprietate, selecție pe ajustare brută minimă, alerte 🚩) există integral numai în `grila.html` (`ELEM` `:80-123`, `buildTable` `:156-160`, `afiseaza` `:274-310`). În UI nou, întreaga grilă e înlocuită de două `textarea` (`dosar.html:87-90`) care trimit `comparables`/`land_comparables` brute la `/api/dosar/{uid}/calcul` (`dosar.html:255-256`, `curent.py:122-137`) — fără ajustări pe elemente, fără selecție brută-minimă, fără praguri prudențiale.

**(3) Import URL / import din extensie mai e accesibil din UI nou?**
**Parțial/Nu.** Import URL: endpoint `POST /api/import-url` viu (`piata.py:20-41`), dar **niciun buton/apel** în UI nou — orfan față de noul flux (UI nou are doar import .docx: `curent.py:56-85`, `import-docx`). Import din extensie: secțiunea „Anunțuri importate" + coada (`descoperire.html:16-24`, `:52-107`; backend `descoperire.py:57-93`) **nu apare** în UI nou; extensia POST-ează în coadă (CORS configurat `app.py:24-30`), dar coada se consumă doar prin pagina veche `/descoperire` → grila veche.

**(4) Backend descoperire/grilă — refolosit de UI nou sau orfan?**
**Funcțional, dar NU re-folosit de UI nou — accesibil doar prin paginile vechi.** Toate routerele sunt montate (`app.py:35`: `evaluare, grile, descoperire, piata, aml, curent, pagini`). Endpoint-urile `/api/descopera`, `/api/descopera-teren`, `/api/grila-teren|casa|chirii`, `/api/indice-anevar`, `/api/import-url`, `/api/import-anunt`, `/api/anunturi-importate*` răspund normal. UI-ul nou (`dosar.html`) **nu apelează niciunul** dintre ele — folosește doar `/api/dosar/{uid}/{salveaza,calcul,raport.docx}`. Deci backend-ul NU e cod mort, dar este „orfan" din perspectiva UI-ului nou: viu doar pentru că paginile vechi `/descoperire` și `/grila` rămân active și sunt linkuite cu `↗`.

---

## Modulul de căutare — ce s-a tăiat exact și ce ar trebui re-integrat (inline, nu link)

**Ce s-a tăiat (din perspectiva sub-tabului Comparabile al UI-ului nou):**
1. Tot **formularul de descoperire casă**: portal, județ, localitate + atributele subiectului (an, stare 1-5, finisaj 1-4, încălzire, teren) + atribute secundare — adică exact „informațiile cerute ca să le găsească" (`descoperire.html:26-40`).
2. **Tabelul de rezultate** cu scor de relevanță, comparație atribut-cu-atribut subiect↔anunț, explicație, badge de încredere (`descoperire.html:132-156`).
3. **Bifarea + trimiterea în grilă** (`localStorage` `grila_prefill_casa`) — puntea descoperire→grilă (`descoperire.html:191-200` ↔ `grila.html:163-176`).
4. **Descoperirea de teren** integrată în grilă (`grila.html:34-45`, `:228-254`).
5. **Cele 3 grile de ajustare pe etape** + selecția pe ajustare brută minimă + alertele prudențiale 25%/15% (`grila.html` integral).
6. **Indicele ANEVAR**, **importul URL** și **coada extensiei** ca asistențe inline.

**Ce ar trebui re-integrat inline în sub-tabul Comparabile (recomandare, fără cod):**
- Un **formular de căutare** (portal + județ + localitate; pre-completate din identitatea dosarului `judet`/`localitate` deja existente la `dosar.html:53-54`) + atributele subiectului (refolosibile din `suprafata_teren`, `an_referinta`, plus stare/finisaj/încălzire) → `POST /api/descopera` / `/api/descopera-teren`.
- Un **tabel de rezultate** cu relevanță + checkbox; bifatele să populeze direct `textarea#comparabile` / `#comparabile_teren` (sau o grilă reală), eliminând pasul `localStorage`+redirect.
- O **grilă de ajustare pe etape** (re-folosind `ELEM` + `afiseaza` din `grila.html`) în loc de `textarea` brute, cu apel la `/api/grila-casa|teren|chirii` și păstrarea selecției pe ajustare brută minimă + alertele 🚩 (control GEV 520).
- Buton **Import URL** și (opțional) panoul **coadă extensie** pentru paritate completă.
- Toate API-urile necesare există deja și sunt montate — re-integrarea e pur frontend (sub-tab Comparabile), fără modificări de backend.

---

## Fișiere examinate (referință)

- UI vechi: `src/evaluare/web/templates/descoperire.html`, `src/evaluare/web/templates/grila.html`
- Backend: `src/evaluare/web/routers/descoperire.py`, `piata.py`, `grile.py`
- Discovery: `src/evaluare/discovery/orchestrator.py`, `scoring.py`, `extractor.py` (+ `profiles.py`, `results.py`, `portal_search.py`)
- UI nou: `src/evaluare/web/templates/curent/dosar.html`, `curent/incepe.html`, `curent/cont.html`; `src/evaluare/web/routers/curent.py`
- Montare routere: `src/evaluare/web/app.py:35`; comutator UI: `src/evaluare/web/templates/_nav_cross.html`
