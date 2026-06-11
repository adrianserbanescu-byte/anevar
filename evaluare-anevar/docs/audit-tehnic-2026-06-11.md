# Audit tehnic — cod ANEVAR (Python/FastAPI)

Data: 2026-06-11. Scop: audit READ-ONLY (cod mort, duplicare, complexitate, arhitectură,
type safety, gestionare erori, mentenabilitate, gap-uri test/lint). Nicio modificare de cod.

Perimetru: `src/evaluare` (engine, assembler, web/routers, discovery, aml, db, report, importers,
models, ingestie, audit, ai). 9.295 LOC, 92 fișiere analizate.

## Sumar instrumentar

- **ruff** (`.venv/Scripts/ruff.exe check src/`, config py311, select E/F/I/B/UP/SIM/C4):
  **All checks passed!** (0 erori) — codul e lint-curat.
- **pyright** (`npx pyright --pythonpath .venv/Scripts/python.exe`, Python 3.13): **33 erori, 0 warnings**.
  Distribuție: 18 `reportArgumentType`, 12 `reportAttributeAccessIssue`, 1 `reportReturnType`,
  1 `reportOptionalMemberAccess`, 1 `reportCallIssue`. Pe fișiere: ai/narrative.py (11),
  engine/reconciliation.py (8), discovery/orchestrator.py (3), discovery/portal_search.py (3),
  db/storage.py (2), web/routers/aml.py (2), aml/risc.py (1), discovery/extractor.py (1),
  discovery/ponderi_store.py (1), web/routers/descoperire.py (1).
- **mypy / pyright**: nu sunt instalate în mediu; pyright rulat via npx (Node 24).
- **Teste**: 110 fișiere `tests/test_*.py`, coverage configurat la `fail_under=90` (~94% raportat).

Verdict general: bază de cod matură, disciplinată (lint curat, except specifice + logate, garduri
SSRF/CSRF/path-traversal, validare 422). Problemele găsite sunt de rafinare, nu structurale.
Cele mai relevante: erorile pyright reale (type erasure în câteva puncte), două piese de cod mort
(convertor PDF + `reconcile` vechi), duplicare de helper-e de formatare și două funcții lungi.

---

## type safety (pyright — 33 erori reale)

### tip-erasure prin `-> object` în routerul AML
`web/routers/aml.py:29` — `_client_din(req) -> object`. Returnează `ClientPF | ClientPJ` dar
adnotarea `object` șterge tipul, iar la `aml.py:54` și `:93` pyright raportează
`Argument of type "object" cannot be assigned to parameter "client" of type "Client"`. Fix:
adnotează `-> ClientPF | ClientPJ` (sau `Client`) și importă tipul la nivel de modul.

### `valoare_finala: Decimal | None` în ramurile de fallback ale reconcilierii
`engine/reconciliation.py:41,49,58` — `ReconciledResult(valoare_finala=cost_value/market_value, ...)`
unde valorile sunt `Decimal | None`. Logica garantează non-None (există un `raise` mai sus la 34-35),
dar tipul nu-l exprimă. Fie restrânge tipul cu un `assert`, fie folosește variabile non-Optional.

### `metoda_selectata: str` vs `Literal[...]`
`engine/reconciliation.py:118,121,125,129` — `_METODA.get(primara, primara)` întoarce `str`, dar
`ReconciledResult.metoda_selectata` e `Literal["piata","cost","ponderata","venit"]`. `_METODA.get`
poate produce o valoare în afara literalului (orice `primara` necunoscut trece direct). Risc real:
o etichetă de metodă neașteptată ajunge în API/raport. Restrânge maparea sau validează.

### `float` în loc de `Decimal`
`engine/reconciliation.py:103` — `Cannot access attribute "quantize" for class "float"`: pe o ramură
`sum(...)/total_pondere` poate fi `float` (dacă `RezultatAbordare.valoare` nu e strict `Decimal`).
Verifică tipul lui `RezultatAbordare.valoare`.

### `block.text` pe union-ul de blocuri Anthropic
`ai/narrative.py:273` (11 erori) — `block.text for block in message.content if getattr(block,"type",None)=="text"`.
Pyright nu poate restrânge union-ul (`ThinkingBlock`, `ToolUseBlock`, ...) doar pe `getattr`. Funcțional
e corect (guard pe `type=="text"`), dar pentru type-safety folosește `isinstance(block, TextBlock)`.

### `int | None` în loc de `Decimal | None`
`discovery/orchestrator.py:223,291` — `CandidateResult/LandDiscoveryResult(pret_mp=round(...))` dă `int`,
câmpul așteaptă `Decimal | None`. `db/storage.py:122` — `int(cur.lastrowid)` cu `lastrowid: int | None`.

### `_AttributeValue` din BeautifulSoup tratat ca `str`
`discovery/orchestrator.py:73`, `discovery/portal_search.py:82-83`, `discovery/extractor.py:85` —
atributele bs4 (`node["values"]`, `a["href"]`, `.get(...)`) au tip `_AttributeValue` (poate fi listă),
folosite direct ca `str`. Normalizează cu `str(...)` sau verifică tipul.

### dict invariance
`web/routers/descoperire.py:78` (`dict[str,float]` vs `dict[str,int] | None`) și
`discovery/ponderi_store.py:53` — incompatibilități de invarianță `dict`. Folosește `Mapping` sau
aliniază tipurile valorii.

### `aml/risc.py:64`
`nivel_masuri` are `-> NivelMasuri` dar returnează rezultatul unui `dict[...]["..."]` tipat `str`.
Adnotează literalul pe dict.

---

## cod mort / nefolosit

### Convertorul docx→PDF este complet dormant
`report/pdf.py:70` `docx_to_pdf` e injectat prin `web/app.py:35` (`pdf_converter=`) → `web/deps.py:31`
(`Deps.pdf_converter`), dar **niciun router nu îl apelează** (`grep pdf_converter src/.../routers` = gol).
Comentariul din `web/routers/curent.py:253-254` confirmă: aplicația nu mai produce PDF (decizie 2026-06-08).
~80 LOC + plumbing mort. Recomandare: elimină câmpul din `Deps`/`create_app` sau documentează explicit
că e API public rezervat. Lăsat așa, induce în eroare (pare folosit).

### `reconcile()` (vechi) — folosit doar în teste
`engine/reconciliation.py:14-64` `reconcile(market, cost, metoda, ...)`. În `src/` producția folosește
exclusiv `reconcile_profil` (assembler.py:238). `reconcile` apare doar în teste
(test_reconciliation, test_end_to_end, test_faza0_echivalenta). E o variantă istorică (2 abordări)
suprapusă cu `reconcile_profil` (N abordări). Recomandare: marchează ca legacy sau migrează testele
pe `reconcile_profil` și retrage funcția.

---

## duplicare

### Helper-e de formatare numerică triplate
`_b2` și `_pct` sunt definite identic în `ai/narrative.py:98,106` și `report/generator.py:131,140`;
`_fmt` doar în `report/generator.py:98`. Aceeași logică `Decimal(str(x)).quantize(...)` + fallback.
Recomandare: un modul comun `evaluare/format_num.py` (sau extinde `web/format.py`) cu `b2/pct/fmt`,
importat din ambele. Reduce drift-ul (deja diverg pe ce excepții prind: generator prinde `Exception`,
narrative prinde `(InvalidOperation, ValueError, TypeError)`).

### Boilerplate import-docx-base64 duplicat în routere
Blocul „decode data-URL base64 + cap 35MB + tmpdir unic + write_bytes + cleanup" e copiat în
`web/routers/curent.py:105-139` (import-docx), `:297-323` (incarca-submis) și parțial
`web/routers/piata.py:60-72`. Recomandare: un helper `_decode_upload(continut, nume, limita)` în
`web/deps.py` sau un util comun.

### Pattern grilă-de-comparație duplicat în generator
`report/generator.py` `_adauga_grila_comparatie` (376-410) și `_adauga_grila_teren` (413-442) au
structură aproape identică (header 4 coloane, loop indici_mediati/index_selectat/marcaj DA *). Se pot
unifica printr-un helper parametrizat.

---

## complexitate excesivă / funcții lungi

### `report/generator.py` — god-module de raport (850 LOC)
Cel mai mare fișier. `genereaza_raport` (690-850) e o funcție de ~160 de linii care asamblează manual
toate cele 7 capitole + shell GBF inline. Capitolul 4 (descriere fizică, 742-783) e un lanț dens de
`if`-uri pe câmpuri opționale. Recomandare: extrage capitolele inline (1-7) în funcții `_capN(doc, ctx)`
ca restul shell-ului, ca `genereaza_raport` să fie doar orchestrare. Îmbunătățește testabilitatea pe capitol.

### `discovery/orchestrator.py:descopera` (150-231) — ~80 linii
Pipeline cu multe responsabilități inline: fetch, parse, extract, fuziune date structurate vs LLM
(6 blocuri `if parsed.X is not None`), filtru apartament, scoring, declasare, marcare atipic, sort.
Recomandare: extrage „fuziunea atributelor parser↔LLM" (183-208) într-un `_fuzioneaza_atribute(extraction, parsed)`.

### `web/app.py:create_app` — middleware monolitic (65-109)
`doar_host_local` face 4 lucruri (host-check, CSRF origin, plafon 50MB, security headers + cache).
Funcțional corect, dar greu de testat izolat. Recomandare: separă în middleware-uri distincte sau
funcții helper apelate din el.

---

## mentenabilitate (magic numbers, naming, docstring)

- **Magic numbers fără constantă numită**: `35_000_000`/`"~25 MB"` (curent.py:120,309; piata.py),
  `50_000_000` (app.py:86), `0.85` factor lichidare (generator.py:570), `0.20` prag consistență
  (generator.py:503), `Decimal("0.40")` toleranță teren (orchestrator.py:122), `factor 3` outlier €/mp
  (orchestrator.py:253), `150`/`500` truncări de string (curent.py:40; dosare_fs.py:234). Recomandare:
  ridică-le la constante de modul cu nume (ex. `LIMITA_UPLOAD_BYTES`, `FACTOR_LICHIDARE_GEV520`).
- **Docstring lipsă pe API public**: `engine/reconciliation.py:aloca_constructii` are docstring, dar
  câteva endpoint-uri AML (`aml_norme_interne`, `aml_decizie` etc.) și helper-ele `_doc_response`,
  `_client_din` din web/routers/aml.py n-au docstring (în restul codebase-ului convenția e respectată).
- **Inconsecvență `Exception` vs excepții specifice** la formatare: generator.py prinde `Exception`
  (linii 103,135,144) — prea larg pentru o conversie `Decimal`; narrative.py prinde specific. Aliniază.
- **Diacritice mixte în identificatori/comentarii**: cod RO fără diacritice în nume, dar cu diacritice
  în string-uri — consistent, dar `git grep` pe termeni devine fragil. (observație minoră.)

---

## arhitectură (layering, cuplaje, god-objects)

Pozitiv: layering clar web (routers) → domain (assembler/profil) → engine, cu DI prin `Deps` și
`construieste_context`. Routerele nu ating motoarele direct; assembler orchestrează. ADR-001
(routere pe domenii) respectat.

Observații:
- **Două sisteme de stocare paralele**: `db/storage.py` (SQLite — evaluări, import, feedback) și
  `dosare_fs.py` (foldere — UI nou). UI-ul nou folosește exclusiv folderele; SQLite rămâne pentru
  import-anunțuri + feedback + dosarele vechi. Coexistența e intenționată (documentată), dar crește
  suprafața de mentenanță. `Storage.save/load/list/get_dosar/redenumeste/sterge/set_wizard_snapshot`
  (storage.py:106-166) deservesc fluxul vechi — verifică dacă mai e folosit din UI (candidat la retragere).
- **Importuri locale dese în corpul funcțiilor** (curent.py:80,108-112; aml.py — aproape fiecare
  endpoint importă în corp). Justificat parțial (lazy load, evită ciclice / cost pornire .exe), dar
  ascunde dependențele și îngreunează analiza statică. Recomandare: ridică la nivel de modul unde nu
  există ciclu real.
- **`dosare_fs.py` (459 LOC)** e un modul-procedural mare cu stare globală pe disc (cache/index/lock).
  Cohesiv tematic, dar amestecă: CRUD dosar, versiuni+integritate (ADR-003), lock concurență, cache
  antete, diff index, import folder. Candidat la împărțire în 2-3 module (`dosare_fs`, `versiuni`, `lock`).

---

## gestionare erori / resurse

Pozitiv: except-urile sunt în general specifice și logate (`(OSError, ValueError)`, `binascii.Error`),
nu fail-open tăcut. Garduri SSRF (url_parser:404-445, re-validare redirect), CSRF/host-local (app.py),
path-traversal (dosare_fs `_cale` validează UUID), TOCTOU (`_scrie` → KeyError). 422 consecvent la
input invalid. Resursele temporare se șterg (BackgroundTask, `shutil.rmtree(..., ignore_errors=True)`).

Observații punctuale:
- `migrare.py:80` — `except Exception as e  # noqa: BLE001` (skip-pe-eroare pe lot). Acceptabil pentru
  un job de migrare best-effort, dar e singurul `except Exception` care nu e pe o operație clar delimitată;
  confirmă că nu maschează erori de programare.
- `report/generator.py:103,135,144` — `except Exception` pe formatare numerică (vezi mentenabilitate);
  prea larg, ar trebui `(InvalidOperation, ValueError, TypeError)`.
- `db/storage.py` — fiecare metodă deschide o conexiune nouă (`_connect`). Corect pentru SQLite local,
  dar fără pooling; la volum mare ar conta (nu e cazul aici).

---

## gap-uri de test

Coverage e ridicat (~94%, 110 fișiere). Zone de verificat:
- **`report/pdf.py` / `docx_to_pdf`** — cod dormant, probabil neacoperit (e și omis din coverage prin
  `vlm.py`? nu — doar vlm.py e omis). Dacă rămâne în cod, fie testează-l, fie retrage-l.
- **Ramurile de fallback pyright-suspecte** din `reconcile_profil` (sub-două-abordări, primara lipsă):
  merită teste explicite pe etichetele `metoda_selectata` întoarse, dat fiind type-mismatch-ul.
- **`_METODA.get(primara, primara)` cu `primara` necunoscut** — test pentru a confirma că nu produce
  o etichetă în afara literalului în API.

---

## Recomandări prioritizate

1. Rezolvă cele 33 erori pyright reale (type erasure AML `-> object`, `Decimal | None` în reconciliation,
   `Literal` pe metoda_selectata, `block.text` cu isinstance). Adaugă pyright în CI/pre-commit.
2. Retrage codul mort: `pdf_converter`/`docx_to_pdf` (sau documentează-l explicit) și `reconcile` vechi.
3. Centralizează helper-ele de formatare `b2/pct/fmt` și boilerplate-ul de upload base64.
4. Sparge `genereaza_raport` pe capitole (`_capN`) și extrage fuziunea de atribute din `descopera`.
5. Ridică magic numbers la constante numite (limite upload, factori GEV).
