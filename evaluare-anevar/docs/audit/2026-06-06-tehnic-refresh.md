# Audit tehnic/arhitectural — „major refresh" (2026-06-06)

Scop: riscuri **arhitecturale**, **datorie tehnică**, **scalabilitate/întreținere** pe ce s-a construit
în refresh (UI „output-first", stocare pe foldere `dosare_fs`, cont local, documente, import .docx) ȘI
pe ce se planifică (note-viitoare / features-pending). **NU** stil de cod (alt audit). Fișiere citite:
`dosare_fs.py`, `cont.py`, `master_config.py`, `documente.py`, `importers/docx_dosar.py`,
`web/routers/curent.py`, `web/routers/pagini.py`, `web/routers/evaluare.py`, `web/app.py`, `web/schemas.py`,
`assembler.py`, `templates/curent/dosar.html`, `db/storage.py`, `__main__.py`, `config.py`.

Severitate: **H** = blochează/coruptie/divergență de date · **M** = datorie reală, fricțiune la scară ·
**L** = mic/izolat. „Auto-safe?" **DA** = fix mic, izolat, fără decizie de produs (îl pot face singur).

| # | Sev | Zonă | Risc / Observație | Recomandare | Auto-safe? |
|---|-----|------|-------------------|-------------|:----------:|
| 1 | **H** | Coexistență stocare | UI-ul nou (folder) cheamă **`/api/evaluare` vechi** la fiecare „Calculează"; acesta face **necondiționat `storage.save(ctx)`** (`evaluare.py:33`) → un rând NOU în SQLite `evaluari` la **fiecare clic**, orfan față de folder (eid aruncat). Divergență activă + creștere SQLite nelimitată. | Endpoint „calc-only" fără persistare (sau flag `persist=false`) pentru UI nou; SQLite să nu mai fie scris din fluxul folder. | NU (atinge contract API + flux produs) |
| 2 | **H** | Identitate dosar | `CAMPURI_IDENTITATE` definit, dar lock-ul **nu e impus nicăieri** (câmpurile rămân editabile post-generare). Toată metrarea #4 (1 credit/identitate) atârnă de un invariant inexistent → abuz „altă proprietate, același credit". | Tranșează B1–B4 la #1, apoi impune read-only server-side + `identitate_hash` persistat la prima generare. | NU (decizie de produs — vezi Decizii) |
| 3 | **M** | Migrare/compat | Două sisteme paralele **fără punte**: dosarele vechi SQLite (`evaluari`, schema v4 cu `wizard_json`) **nu** sunt vizibile/migrabile în UI-ul nou (foldere). Pagina veche `/dosare` și noua `/incepe` listează mulțimi disjuncte. La retragerea wizardului vechi → dosare vechi devin inaccesibile. | Decide: migrare unică SQLite→folder, SAU congelare explicită (read-only legacy). Scrie un script de migrare înainte de a retrage UI vechi. | NU (decizie + risc de date) |
| 4 | **M** | Drift schemă JS↔Py | `asambleaza()` (JS, `dosar.html:222`) **dublează** logica payload-ului `EvaluationInput`: mapare hardcodată SCOP→tip_valoare, date implicite `"2026-01-16"`, construcție meta câmp-cu-câmp. **Omite** `land_comparables`, `pondere_piata`, `date_venit`, `date_dcf`, `photos`, `documente` → metode venit/DCF și anexele foto/doc **inaccesibile** din UI nou. Schema Python se schimbă → JS tace. | O singură sursă: endpoint care primește `snapshot()` brut și asamblează `EvaluationInput` în Python; JS nu mai construiește payload-ul. | NU (refactor de contract) |
| 5 | **M** | Scalabilitate scan | `listeaza()` deschide+parsează **fiecare** `dosar.json` la **fiecare** `/incepe` (`diff()`); `wizard` întreg e inclus în fișier, dar antetul citește tot. La sute de dosare = sute de citiri+`json.loads` sincrone/request. | Cache antete în `_index.json` (deja scris) cu invalidare pe `mtime`; citește `dosar.json` complet doar la nevoie. | DA (intern, fără schimbare de comportament) |
| 6 | **M** | Robustețe index/scriere | `_index.json` și `dosar.json` se scriu **ne-atomic** (`write_text` direct). Crash/întrerupere la scriere → JSON trunchiat. `diff()` prinde `ValueError` și **sare** dosarul → pare „dispărut" deși există. Niciun `.tmp`+`os.replace`. | Scriere atomică (temp + `os.replace`) peste tot în `dosare_fs`/`cont`; backup `dosar.json` ca la SQLite. | DA (utilitar `_scrie_atomic`, izolat) |
| 7 | **M** | Identitate vs nume | `CAMPURI_NUME_DOSAR` (format nume) ≠ `CAMPURI_IDENTITATE` (set blocabil): numele poate include `data_vizita`/`data_raport` → numele dosarului **se schimbă** la fiecare editare deși „identitatea" e stabilă. `salveaza_wizard` recalculează numele necondiționat. | Restrânge formatul numelui la câmpuri de identitate (sau marchează clar non-identitate ca „needitabile în nume"). | NU (decizie — B4) |
| 8 | **M** | `id_client` „unic" | `master_config` declară `id_client` `free_text_unic`, dar **unicitatea nu e verificată** nicăieri (creare/import). Doi clienți pot primi același ID → nume de dosar coliziune, ipoteze rupte la #4. | Validare de unicitate la creare/import (scan antete) + mesaj clar; auto-incrementează la coliziune. | NU (atinge fluxul de creare) |
| 9 | **M** | Concurență scriere | Model mono-proces uvicorn (`__main__:96`), dar fără workers ≠ fără concurență: request-uri suprapuse + extensia browser (CORS POST) + 2 sesiuni concurente (plan #4) → `dosar.json`/`_index.json` fără lock = ultima scriere câștigă / index corupt. `diff()` citește+rescrie indexul fără serializare. | Lock per-dosar (fișier lock sau `threading.Lock` per uuid) cel puțin pe scrierile de index; documentează asumpția mono-instanță. | NU (depinde de modelul de concurență — #4) |
| 10 | **M** | Foldere sync cloud | `__main__` avertizează doar pentru **SQLite** în OneDrive/Dropbox. `date/dosare/` (sute de fișiere mici + `_index.json` rescris des) în folder sync e la fel de expus la lock/coruptie/conflict, dar **fără** avertisment. | Extinde avertismentul la `OUTPUT_DIR/dosare`; ghid „ține datele local". | DA (extinde verificarea existentă) |
| 11 | **M** | Generează ≠ Calcul | `/api/dosar/{uid}/raport.docx` reasamblează independent (`asambleaza()` din nou) și **nu** persistă wizardul înainte; nu cere un Calcul reușit. Raportul `.docx` salvat poate diferi de valoarea afișată / de `dosar.json`. | Forțează „Generează" să folosească ultimul snapshot salvat + Calcul validat; salvează wizardul în tranzacție cu versiunea `.docx`. | NU (decizie — B6) |
| 12 | **L** | Versiuni `.docx` nelimitate | `adauga_versiune_docx` adaugă un `.docx` datat la **fiecare** generare, fără plafon/curățare. Generări repetate → folder umflat (spre deosebire de SQLite backup `keep=10`). | Politică de retenție (păstrează ultimele N + cele „marcate") sau curățare la cerere. | DA (mic, izolat) |
| 13 | **L** | Import folder neconectat | `importa_folder()` (adoptă/clonează după legitimație) **există dar nu e rutat** în UI (confirmat B3) — cod neexersat de teste e2e → bitrot. Decide dacă „Importă" = `.docx` sau folder. | Conectează la o rută + test, SAU mută în „experimental" până la decizie. | NU (decizie — B3) |
| 14 | **L** | Anti-coruptie tăcută | `listeaza()`/`_citeste_index()` înghit `OSError/ValueError` și **continuă silențios** → un `dosar.json` corupt dispare din listă fără semnal pentru user. | Loghează + marchează dosarul „necitibil" în UI în loc să-l ascunzi. | DA (logging + un câmp) |
| 15 | **L** | Identitate parțială în nume | `_identitate()` păstrează doar câmpurile **ne-goale** → un dosar creat gol are `identitate={}`; ulterior două dosare „goale" sunt nedistinctibile pe identitate, doar pe uuid. | Persistă cheile de identitate chiar goale (sau marcaj „incomplet") pentru comparații viitoare la #4. | NU (leagă de modelul de identitate) |
| 16 | **L** | Heuristici hardcodate | `docx_dosar.py` (dicț. `_JUDET`/`_TIP`) și `asambleaza()` (mapare SCOP) au cunoștințe de domeniu hardcodate în 2–3 locuri diferite (Py importer, Py assembler, JS). Drift la adăugarea unui scop/județ. | Centralizează enum-urile scop/tip/județ într-un singur modul (sau `master_config`) consumat de toate. | DA (consolidare, fără schimbare de comportament) |
| 17 | **L** | `master_config` în build | Opțiuni admin „hardcodate în .exe" (intenționat pentru Slice A), dar `note-viitoare` cere **matrice de compatibilitate capitole** „generată la build" pentru B/D → riscă să umfle un fișier de config statice cu logică ce ar trebui să vină din gateway (#4). | Tratează matricea ca date versionate (fișier dedicat), nu cod; planifică sursa gateway de la început. | NU (decizie de arhitectură — vezi Decizii) |

## Decizii arhitecturale pentru Adi (necesită decizie umană)

1. **Soarta SQLite-ului în refresh.** Două stocări coexistă, iar UI-ul nou **scrie activ** în SQLite la
   fiecare Calcul (#1), în plus față de foldere. Decizie: (a) SQLite devine pur „calc-only/no-persist"
   pentru UI nou și sursa de adevăr e folderul; (b) păstrăm SQLite ca index/cache peste foldere; (c)
   migrăm complet și retragem SQLite. Fără o decizie, datele diverg și cresc necontrolat.

2. **Migrarea dosarelor vechi.** Dosarele din `evaluari` (SQLite v4, cu `wizard_json`) nu apar în noul
   UI. Le migrăm o singură dată în foldere, sau le congelăm explicit (legacy read-only) înainte de a
   retrage wizardul vechi? Fără asta, retragerea UI vechi = pierdere de acces la istoricul real.

3. **Definirea + impunerea identității (deblochează #2 și metrarea #4).** Care câmpuri = identitate,
   care e declanșatorul de lock (prima generare?), unde se impune (server-side), cum arată
   `identitate_hash`. Azi lock-ul nu există → modelul de credit din #4 nu are fundament.

4. **O singură sursă pentru payload-ul de evaluare (JS vs Python).** `asambleaza()` dublează schema și
   pierde tăcut câmpuri (venit/DCF/foto/documente). Mutăm asamblarea integral în Python (JS trimite
   snapshot brut)? Decizie care simplifică drastic întreținerea și elimină o clasă de bug-uri silențioase.

5. **Modelul de concurență/instalare.** Mono-proces local acum, dar #4 promite 2 sesiuni concurente +
   backup online + extensie care POST-ează. Confirmăm „o instanță, un evaluator, date locale" (și
   adăugăm locking minim), sau proiectăm de la început pentru acces concurent/sync? Afectează nevoia de
   scriere atomică, lock-uri și avertismentele cloud (#6, #9, #10).

6. **„Importă" = ce, exact, și unde stă matricea B/D.** Importă raport `.docx` (acum) vs folder
   (`importa_folder`, neconectat) — și matricea de compatibilitate capitole (feature B/D) e date sau cod,
   build-time sau gateway? Definește suprafața de import și evită ca `master_config` să devină depozit de
   logică ce aparține #4.

---

### Rezumat (≤150 cuvinte)

Refresh-ul e coerent ca direcție (folder = sursa de adevăr, UI output-first), dar are **un risc H concret
nesesizat**: noul UI cheamă `/api/evaluare` vechi, care salvează **necondiționat** în SQLite la fiecare
Calcul — deci cele două stocări nu doar coexistă, ci **diverg activ** și SQLite crește nelimitat cu rânduri
orfane. Al doilea risc H: **identitatea dosarului nu e impusă**, iar întreaga metrare #4 atârnă de acest
invariant inexistent. Datoria tehnică reală: **drift schemă JS↔Python** (`asambleaza()` pierde tăcut
venit/DCF/foto/documente), scrieri **ne-atomice** ale `dosar.json`/`_index.json` (coruptie la crash),
scanare O(n) la fiecare `/incepe`, și **lipsa unei punți de migrare** de la dosarele vechi. Multe fixuri
sunt auto-safe (scriere atomică, cache index, retenție, consolidare enum-uri). Cele 6 decizii de mai sus
necesită însă alegeri de produs înainte de a continua. **Nu am modificat cod.**
