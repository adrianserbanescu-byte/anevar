# Redesign Proprietate + Comparabile (din grilaj cu Adi, 2026-06-11)

> Spec rezultat din `/grill-me`. Decizii confirmate de Adi. **Template-urile de grilă = PENDING** (Adi revine cu conținutul rândurilor/criteriilor per tip).

## Constrângere de implementare
Aproape tot trăiește în `src/evaluare/web/templates/curent/dosar.html` (un singur fișier, script fragil — vezi bug-ul `'ico'`). NU se paralelizează agenți pe acest fișier → **secvențial**, cu `node --check` pe template-ul RANDAT (test `test_template_js_valid`) la fiecare pas. INTERZIS `{{ icon() }}` în string-uri JS.

## LOT A — backend (paralelizabil, fișiere distincte)
- **A1 — Cod poștal auto (Poșta Română):** modul nou `cod_postal.py` + endpoint (ex. `/api/cod-postal?judet=&localitate=&strada=&nr=`) care interoghează serviciul Poșta Română (cod-postal.posta-romana.ro). Robust: timeout, fallback la None + mesaj dacă serviciul nu răspunde; cache pe (adresă). Dacă Poșta Română nu e interogabilă curat programatic → raportează + propune fallback (dataset RO / Nominatim). NU rupe pagina dacă pică (offline → câmpul rămâne manual).
- **A2 — An PIF pe Building:** câmp nou `an_pif` (an punere în funcțiune) pe `models/property.py` Building; `engine/cost.py` folosește vârsta = `an_referinta − an_pif` la nivel de clădire (azi PIF e doar per-element de cost). Backward-compat (fără an_pif → comportament actual). Contract UI: dosar.html trimite `building.an_pif`.

## LOT B — Proprietate (1 agent, dosar.html, după/paralel cu A la contract)
1. **Dată:** redenumește „Data vizită" → „Data inspecției" (id rămâne `data_inspectiei`; un singur câmp, fără date noi).
2. **AU ↔ AD/ACD bidirecțional, coef 0.80:** completezi `#au` → `#acd = au/0.80`; completezi `#acd` → `#au = acd×0.80`; ambele editabile, ultima editare câștigă; nu suprascrie ce a tastat userul manual după.
3. **An referință + PIF:** `#an_referinta` precompletat cu anul curent (editabil); **câmp NOU `#an_pif`** „An PIF (punere în funcțiune)" lângă el; hint „vârsta = referință − PIF". Trimite `building.an_pif` (contract A2).
4. **Cale acces → dropdown:** `Drum asfaltat · Drum pietruit · Drum de pământ · Servitute de trecere · Altul`; la „Altul" → câmp free-text. (Înlocuiește `#acces` text liber; păstrează cheia `land.acces` în payload = valoarea aleasă sau free-textul.)
5. **Utilități:** + checkbox „Fosă septică" + câmp free-text „Altele" (intră în `land.utilitati`).
6. **Riscuri fizice:** secțiunea ESG/riscuri fizice → `<details>` colapsat implicit (minimizat).
7. **Mută „date de cost"** (elemente IROVAL + puncte depreciere) din Proprietate → tab-ul **Calcul**.
8. **Valoare teren:** mută `#valoare_teren` jos, lângă grila de teren din Comparabile (pregătește pentru preluare auto — vine în Lot C).

## LOT C — Comparabile redesign (1 agent, dosar.html, DUPĂ B; structural acum, template când revine Adi)
1. **Grilă = workspace integrat:** căutare + candidați (live + salvați) + ajustări, toate în grilă.
2. **Descoperă → ELIMINAT** complet ca tab; funcționalitatea (căutare portaluri + rezultate) devine **modul de căutare în capul fiecărei grile**.
3. **Import candidați → completează automat grila** (rânduri din candidați).
4. **Teren subiect = preluat din Proprietate** (suprafață teren); **valoare teren** se preia din rezultatul grilei de teren → populează `#valoare_teren` (mutat în Lot B jos).
5. **Casa:** suprafața subiect a grilei casă = **AU**.
6. **Linie nouă „Suprafață candidat"** în grilă.
7. **Grila teren → jos → toate portalele** (lista de portaluri la căutarea de teren).
8. **Grila de chirii → DOAR comercial** (ascunsă la casă+teren și la apartament).
9. **Template de început per grilă:** PENDING — Adi dă rândurile/criteriile predefinite per tip (casa/teren/comercial).

## Verificare obligatorie (fiecare lot care atinge dosar.html)
- `pytest tests/test_template_js_valid.py` (node --check pe template randat) → verde.
- `pytest -k "web_curent or descoper or grila or assembler"` → verde.
- Smoke live + verificare în browser (consolă 0 erori + dropdown-uri populate).
