# Plan de implementare — redesign „Descoperă" (din council + investigație)

> Distilează `council-digest.md` + `output1-investigatie.md` într-un plan acționabil. Principiu cheie:
> **separ INGINERIA de DECIZIA DE METODOLOGIE.** Structura (model per-categorie, switch de model, parsere,
> geocoding) = inginerie, o pot face. **Valorile ponderilor + reprezentarea scorului = bucket B** (evaluator/Adi)
> — le propun ca punct de pornire, dar le calibrezi/decizi tu. Cod-ul ar merge pe `sesiune-b` → A integrează.

---

## 0. DECIZII PE ADI (gate înainte de cod metodologic)
Council-ul e în consens pe STRUCTURĂ, dar diverge pe valori. De decis:

| # | Decizie | Opțiuni (council) | Tip |
|---|---------|-------------------|-----|
| D1 | Pondere **Teren** la casă (azi ×1, „prea mic") | ×2 (Grok) … ×3 log (Claude) … ×5 (Gemini) … ~0.1 urban (GPT) | bucket B (metodologie) |
| D2 | **Reprezentarea scorului**: un singur 0–100% vs. **radar chart pe 3–4 axe** (Locație/Fizic/Calitate/Funcțional) | Claude + GPT vor radar; chairman păstrează % | produs/UX |
| D3 | **Scădem ponderea** stare(×4)/finisaj(×3) fiindcă vin doar din LLM? | consens „da + confirmare manuală", dar valoarea = a ta | bucket B |
| D4 | **Pivot ANCPI/notariat** (preț FINAL tranzacționat) ca „strat 0" peste anunțuri (preț ASK +10–15%) | doar Claude; strategic, acces la date | strategic |
| D5 | **Distanța**: consens = NU în scorul %, doar badge/tie-breaker (Grok dissent) | merg pe consens dacă nu spui altfel | metodologie |

> Restul planului (structura) NU e blocat de astea — pot construi „țeava", cu ponderile ca **config** ce le setezi tu.

### D5 — detaliere localizare/distanță (decizia Adi, 2026-06-07)
**Zona/cartierul = semnal categoric PRIMAR; distanța-în-metri = tie-breaker SECUNDAR, doar în aceeași zonă.**
- **Match localizare:** aceeași stradă > stradă vecină/același cartier ≫ cartier diferit. Cartier diferit, chiar la ~2 km = **„obiect economic diferit"** (ex. *Primăverii ≠ Pantelimon*) → decide ZONA, nu km.
- **Granularitate după mărimea localității:** sate/comune = **localitatea** (distanța între străzi irelevantă); orașe < 50k = **cartier**; orașe mari = **sub-zonă/rază** (aici distanța-între-străzi devine tie-breaker util).
- **Calcul:** **haversine** (linie dreaptă, offline ieftin — proxy acceptabil la scară de cartier; **NU routing** încă). Precizie limitată de adresa din anunț: stradă+nr → punct exact; doar stradă → centroid stradă; doar cartier → folosești zona **categoric**, nu km.
- **Afișare (per D5):** **text**, ex. „Același cartier (Ultracentral) · 400m" / „Cartier diferit (Pantelimon)" — NU km brut băgat în scorul %.
- **Bucket-B (Adi calibrează):** cât cântărește fiecare prag de zonă. Inginerie (B): structura — zonă categoric + distanță tie-breaker în zonă.

---

## P0 — fundație (1–2 sprinturi; consens 4/4)

### P0.1 — Decuplează modelul de casă → model per-categorie *(inginerie)*
- Azi: `discovery/profiles.py` are UN singur `SubjectProfile/CandidateProfile` (atributele casei) + `scoring.py` un singur `PONDERI`/`ORDINE`. Toate categoriile folosesc modelul casei.
- De făcut: profil + set de ponderi/atribute **per categorie** (#1…#5), selectate după `tip_activ`. Ponderile = **config** (un dict per categorie), ca să le calibrezi fără cod.
- Fișiere: `discovery/profiles.py`, `discovery/scoring.py`, `discovery/orchestrator.py`, `web/routers/descoperire.py`.

### P0.2 — Scoring Apartament #2 *(inginerie + D1/D3)*
- Cea mai mare valoare: „60–70% din piață", azi scorat cu logica de casă.
- Promovează în formulă atributele **deja extrase dar nefolosite**: `nr_camere`, `etaje` (sunt în `ParsedListing`).
- Propunere council (de calibrat de tine): filtru ±1 cameră; Suprafață ×7, Etaj ×5 (neliniar — parter/ultimul ≠ intermediar), Nr. camere ×4, An ×3, Stare ×2.
- Notă tehnică: „Etaj" la apartament necesită extracție de etaj curent + total (azi `etaje` = nr. niveluri, gândit pt casă) — mic add la parser/extractor.

### P0.3 — Risc LLM pe stare/finisaj *(inginerie UI + D3)*
- Badge **„⚠️ Estimat de AI"** pe atributele venite din LLM + buton **Confirmă** (după validare → atributul devine „validat", revine la pondere maximă).
- Fișiere: `descoperire.html` (UI), payload-ul de scor (marcaj sursă atribut). Scăderea efectivă a ponderii = D3.

### P0.4 — Switch extracție pe model ieftin *(inginerie; validat empiric)*
- Investigația + council confirmă: `llama-3.3-70b` / `gemini-flash` ≈ Claude pe field-extraction, ~10× mai ieftin.
- De făcut: configurabil modelul extractorului (via clientul AI / `settings`), Claude ca **fallback** la confidență scăzută. Atenție: se leagă de **ADR AI-gateway** (nu strica fluxul existent).
- Fișiere: `discovery/extractor.py`, clientul AI / `settings`. Test: scor identic pe eșantionul nostru.

---

## P1 — acoperire + locație (săpt. 3–6; consens 4/4)

### P1.1 — Parser VDI.ro + Imoradar24 → deschide #3 industrial / #5 special
- „Acoperirea > acuratețea algoritmului în această etapă." Imobiliare/storia nu acoperă bine comercial/industrial.
- Imoradar24 = agregator → strategie: discovery pe el → urmează redirect spre sursa originală → scrape acolo (sau parser direct). **Necesită dedup.**
- Fișiere: `importers/url_parser.py` (parsere noi), `discovery/portal_search.py` (segmente noi).

### P1.2 — Geocodare offline → distanța ca tie-breaker *(inginerie + D5)*
- OSM România (Geofabrik) + SIRUTA + index spațial (PostGIS/Nominatim local) → distanță haversine, offline, cost ulterior zero (~2–3 zile).
- Distanța = **badge/penalizare separată** afișată („90% (−15% distanță 3km)"), NU în scorul %. La industrial/agricol = distanță față de infrastructură.
- Rezolvă și problema de precizie „Breaza → Gura Beliei/Nistorești".

---

## P2 / Backlog — diferențiatori (gated, decizie de produs)

- **Export „Comparabile ANEVAR"** (tabel Subiect vs Candidați + justificare → în raportul .docx/.xlsx). Council: „ultimul 20% care face produsul util; altfel ai doar un search mai deștept." **Recomandat sus în backlog.**
- **Ground Truth / feedback loop:** loghează ce **respinge** evaluatorul din listă (Overlap@5 target >60%) — singura metrică reală de succes.
- **Decay temporal:** penalizare pe vechimea anunțului (preț ASK vechi ≠ piață azi).
- **Idei îndrăznețe (Q10, mari, gated):**
  - *Vision pe foto* — VLM pe primele imagini, „scor structural, ignoră descrierea agentului" (textul „superb/renovat" = sursa erorilor). Lansare „X-Ray Premium".
  - *Copilot care învață din respingere* — `score = α·reguli + (1−α)·învățat`, lock-in per evaluator.
  - *Piață sintetică* — graf de proprietăți cu propagare de preț.

---

## Riscuri & dependențe
- **Ponderile** sunt bucket B → fără calibrarea ta, P0.2/P0.3 rămân „structură + config implicit".
- **Switch model extracție** atinge ADR AI-gateway → testare atentă, fallback obligatoriu.
- **Parsere noi** = fragile la schimbări de layout (ca tot scraping-ul) → izolează + loghează eșecuri (lane-ul de logging).
- **Stabilitate build de feedback:** nimic din P0–P1 nu intră în build-ul de feedback până nu zici tu (per regula de a nu destabiliza).
- **Coordonare:** codul P0–P2 ar merge pe `sesiune-b` → A integrează pe master.

## Ordine recomandată (consens council)
**P0.2 (Apartament) → P0.4 (model ieftin) → P0.3 (risc LLM) → P0.1 (decuplare) → P1.1 (acoperire) → P1.2 (geocoding) → P2 (export ANEVAR).**
