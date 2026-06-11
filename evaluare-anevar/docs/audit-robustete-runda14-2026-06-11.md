# Audit robustețe — RUNDA 14 (2026-06-11)

**Țintă:** suprafețele NOI neauditate (sesiuni + agenți): QC (`/api/dosar/{uid}/calitate`,
`/api/evaluare/{eid}/calitate`), Registru (`/registru`, `/api/registru`, `/api/registru.csv|.xlsx`,
`/api/dosar/{uid}/export.zip`), pregătire BIG (`/api/dosar/{uid}/big`), module noi (`big.py`, `esg.py`,
`valoare_prudenta.py`, `registru/`), wiring ESG/CPE/cod_postal în generator, câmpuri noi
(cod_postal, certificat_energetic, riscuri_fizice, nr_lucrare).

**Metodă:** READ-ONLY. Input-netrusted → excepție neprinsă → 500 / DoS. Probă concretă reprodusă
local (`.venv`) pentru fiecare finding. NU repetă findings RUNDA 9–13.

**Verdict:** 1 HIGH, 1 MEDIUM, 1 MEDIUM, 2 LOW. Suprafețele QC sunt bine gardate (reutilizează
`_context()` 422-guarded și/sau context deja persistat) — niciun finding pe ele. Modulele pure
`valoare_prudenta.py` și `big.py` (mapper) nu au surse de input-netrusted directe în afara wiring-ului
de mai jos.

---

## H14-1 (HIGH) — `/api/dosar/{uid}/big` și pagina `/registru` → 500 din `suprafata`/`valoare` = 0 sau negativ

- **Severitate:** HIGH (DoS pe pagina obligatorie `/registru` + endpoint BIG, declanșabil de un singur dosar).
- **Locație:** `src/evaluare/web/routers/registru.py` — `pregateste_big()` (l. 70-72, apel `big.construieste_payload_big`),
  `pagina_registru()` loop (l. 83-92, prinde DOAR `KeyError`), `pregateste_dosar_big()` (l. 114-134, niciun try pe construcție).
  Cauză rădăcină: `big.CampuriMinimeBIG.suprafata` și `.valoare_piata` au `Field(gt=0)`
  (`src/evaluare/big.py` l. 99, 105), iar `big._dec()` (l. 233-242) convertește tolerant `"0"`/`"-5"`/`"0.0"`
  în `Decimal` și îl pasează DIRECT în câmpul `gt=0` → `pydantic.ValidationError` (subclasă `ValueError`) NEPRINSĂ.
- **Probă:**
  1. `POST /api/dosar` (creează dosar) → `uid`.
  2. `POST /api/dosar/{uid}/salveaza` cu body `{"tip_proprietate":"teren","suprafata_teren":"0"}`
     (endpoint-ul acceptă `wizard: dict` arbitrar, fără validare — `curent.py` l. 159-165).
  3. `GET /api/dosar/{uid}/big` → **500** (ValidationError: `suprafata Input should be greater than 0`).
  4. `GET /registru` → **500 pe TOATĂ pagina** (loop-ul l. 87-90 prinde doar `KeyError`, nu `ValidationError`)
     — un singur dosar otrăvit dărâmă registrul întreg pentru toți.
  Reprodus end-to-end local: `salveaza_wizard(uid,{'suprafata_teren':'0'})` → loop `/registru` → `ValidationError`.
  Variante care declanșează: `suprafata` ∈ {`"0"`,`"-5"`,`"0.0"`}; `valoare_finala`/`valoare_piata` ∈ {`"0"`,`"-100"`}.
- **Fix recomandat:** în `registru.pregateste_big`, nu pasa valori ne-pozitive în câmpurile `gt=0`:
  tratează `<=0` ca lipsă (None) — ex. un helper `_dec_pozitiv(v)` care întoarce `None` dacă `_dec(v) is None or <= 0`
  (semantica „valoare invalidă = câmp lipsă → apare în checklist-ul de lipsuri", coerent cu intenția modulului).
  ȘI defense-in-depth: în `pagina_registru` loop și în `pregateste_dosar_big`, prinde `(KeyError, ValidationError)`
  (sau `ValueError`) → sări dosarul / marchează `{"gata": false, "eroare": ...}` în loc de 500.
  Alternativ: relaxează constrângerea la `ge=0` în `big.py` dacă 0 e o valoare acceptabilă pentru checklist.

---

## H14-2 (MEDIUM) — Scriitorul XLSX emite caractere de control → `.xlsx` corupt (registru nedeschizibil)

- **Severitate:** MEDIUM (integritate livrabil: exportul de registru devine nedeschizibil în Excel/LibreOffice;
  declanșabil prin orice câmp text al registrului).
- **Locație:** `src/evaluare/registru/xlsx_min.py` — `_esc()` (l. 40-42) și `_celula()` (l. 55-63):
  escapează doar `& < > "`, dar NU elimină caracterele de control interzise de XML 1.0 (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F).
  Acestea ajung RAW în `<t xml:space="preserve">…</t>` → XML invalid → Excel respinge fișierul.
- **Probă:** `xlsx_min.workbook(['col'], [['bad\x01\x02\x0bchar']])` produce un `sheet1.xml` care conține
  byte-ul 0x01 brut; `ET.fromstring(sheet1.xml)` → `ParseError: not well-formed (invalid token)`.
  Vector real: salvează în orice câmp de registru (ex. `observatii_registru`, `nume_client`) un text cu un
  caracter de control (lipit din PDF/Word, `\x0b` din copy-paste), apoi `GET /api/registru.xlsx` → fișier corupt.
- **Fix recomandat:** în `_esc()` (sau înainte de el), elimină/înlocuiește caracterele de control invalide XML:
  `text = "".join(c for c in text if c == "\t" or c == "\n" or c == "\r" or ord(c) >= 0x20)` (păstrează tab/newline,
  scoate restul sub 0x20 + 0x7F-0x9F la nevoie). Aplică-l și pe `nume_foaie` în `workbook()`.

---

## H14-3 (MEDIUM) — Injecție de formule CSV/XLSX în exportul de registru (și BIG payload pe coperta)

- **Severitate:** MEDIUM (CSV/formula injection — execuție de conținut în Excel-ul destinatarului, ex. evaluator/auditor ANEVAR care deschide registrul exportat).
- **Locație:** `src/evaluare/registru/registru.py` — `csv_text()` (l. 136-144) și `xlsx_bytes()` (l. 147-151):
  scriu valorile câmpurilor (client, observații, obiect etc.) NEPREFIXATE. O celulă care începe cu `=`, `+`, `-`, `@`
  (sau `\t`,`\r`) e interpretată ca formulă LIVE de Excel/LibreOffice la deschidere.
- **Probă:** `reg.csv_text([{...,'client':'=cmd|\'/c calc\'!A1','observatii':'@SUM(1+1)'}])` → CSV-ul conține
  `=cmd|...` și `@SUM(...)` ca prefix de celulă (verificat: `'=cmd' in txt == True`, `'@SUM' in txt == True`).
  Aceeași expunere la XLSX (valorile text intră ca inline strings neprefixate). Vector: `nume_client`/`observatii_registru`
  controlate de user → `/api/registru.csv` sau `.xlsx`.
- **Fix recomandat:** la export (CSV și XLSX), prefixează cu apostrof `'` orice celulă text care începe cu
  `= + - @ \t \r` (neutralizare standard CSV-injection), SAU prefixează un spațiu/zero-width. Centralizează într-un
  helper `_neutralizeaza_formula(s)` aplicat în `_matrice()` (l. 130-133) ca să acopere ambele exporturi simultan.
  Notă: aceeași clasă există și la `/api/feedback.csv` (`web/routers/pagini.py` l. 150-160) — pre-existent, dar
  candidat la același fix dacă se rezolvă centralizat.

---

## H14-4 (LOW) — `registru.rand()` → `TypeError: unhashable type` dacă `dosar["risc_aml"]` e listă/dict

- **Severitate:** LOW (nu e declanșabil prin căile de scriere actuale — `risc_aml` nu se scrie niciodată la
  nivelul top al `dosar.json`; doar prin `dosar.json` fabricat manual / importat).
- **Locație:** `src/evaluare/registru/registru.py` l. 109-110:
  `_RISC_ETICHETA.get(dosar.get("risc_aml") or _g(w, "risc_aml"), …)` — `dosar.get("risc_aml")` NU e trecut prin
  `_g()` (care stringifică), deci dacă e o listă/dict, `dict.get(cheie_nehashabilă)` → `TypeError` neprins în
  `randuri()` (l. 122-124 prinde doar `KeyError`) → 500 pe `/registru`, `/api/registru`, `.csv`, `.xlsx`.
- **Probă:** `reg.rand({'uuid':'…','risc_aml':['x'],'wizard':{}})` → `TypeError: unhashable type: 'list'`.
  Reachable doar via import de folder dosar (`dosare_fs.importa_folder`) cu un `dosar.json` manipulat, sau editare
  manuală pe disc — NU prin `/api/dosar/{uid}/salveaza` (acela scrie doar sub `wizard`).
- **Fix recomandat:** normalizează cheia înainte de `.get`: `cheie = str(dosar.get("risc_aml") or _g(w,"risc_aml") or "")`
  o singură dată, apoi `_RISC_ETICHETA.get(cheie, cheie)`. Defense-in-depth: în `randuri()` extinde `except` la
  `(KeyError, ValueError, TypeError)` ca un dosar otrăvit să fie SĂRIT, nu să dărâme tot registrul.

---

## H14-5 (LOW) — `randuri()` recitește TOATE dosarele necachezat la fiecare apel export (amplificare DoS)

- **Severitate:** LOW (degradare de performanță / amplificare, nu crash; relevant doar la volume mari de dosare).
- **Locație:** `src/evaluare/registru/registru.py` `randuri()` (l. 115-127): pentru fiecare dosar listat apelează
  `fs.incarca(uid)` (citește + parsează `dosar.json`), FĂRĂ cache pe mtime (spre deosebire de `dosare_fs.listeaza()`
  care e cachezat). `/registru` adaugă încă un `fs.incarca(uid)` per rând în loop-ul BIG (l. 88) → 2× citiri/dosar.
  `/api/registru`, `.csv`, `.xlsx` apelează fiecare `randuri()` din nou (fără cache între ele).
- **Probă:** un singur `GET /registru` cu N dosare = ~2N citiri+parse JSON; 4 endpoint-uri (pagină+json+csv+xlsx)
  reapelate ⇒ ~8N. Fără limită superioară pe N (numărul de dosare nu e mărginit). Nu e o vulnerabilitate de
  securitate, dar e o suprafață de amplificare pentru un client care lovește repetat exporturile.
- **Fix recomandat:** derivă rândurile din antetele deja cachezate de `dosare_fs.listeaza()` unde e posibil, sau
  cachează `randuri()` pe `mtime_ns` agregat (același tipar ca `_cache_antete.json`). În `/registru`, refolosește
  dosarul deja încărcat în loc de un al doilea `fs.incarca(uid)` (împachetează `rand()` + `pregateste_big()` pe
  ACELAȘI obiect dosar).

---

## Suprafețe verificate FĂRĂ finding (negative results, pentru trasabilitate)

- **`/api/dosar/{uid}/calitate`** (`curent.py` l. 213-223): reutilizează `_context(inp)` care prinde
  `(ValueError, ArithmeticError)` → 422; `fs.incarca` KeyError → 404. `calitate.verifica_calitate` operează pe
  context validat (parse de date tolerant în `_parse_data`, comparații `Decimal` deja gardate). Robust.
- **`/api/evaluare/{eid}/calitate`** (`evaluare.py` l. 87-100): `eid` mărginit `Annotated[int, ge=1, le=2^63-1]`
  (anti-OverflowError, RUNDA anterioară); context vine din storage (deja persistat, nu poate fi otrăvit cu input nou). Robust.
- **`/api/dosar/{uid}/export.zip`** (`curent.py` l. 410-447): `uid` validat ca UUID prin `fs.folder_dosar→_cale`
  (anti path-traversal); `folder.glob("*")` NErecursiv, scrie doar `p.name` în zip (fără path traversal la write);
  exclude `.lock`. Numele fișierului zip sanitizat (`replace("/","-")`). Robust.
- **`/api/backup-dosare.zip`** (`curent.py` l. 392-408): `rglob` peste `baza()` (rădăcina app, nu input user). Robust.
- **`esg.genereaza_sectiune_esg`** wiring (`report/generator.py` l. 663-679): `riscuri_fizice` filtrat
  (`if r and r.strip()`), etichete libere → `RiscIdentificat(cheie=…)` (string), fallback pe denumire=cheie. Nicio conversie negardată.
- **`certificat_energetic` / `cod_postal`** wiring (`generator.py` l. 307-308, 938-940): interpolate ca text simplu,
  fără conversie numerică. Robust.
- **`registru/numar.aloca`** (`registru/numar.py`): alocare atomică `O_EXCL`, glob `{an}_*` cu `int()` gardat
  (`except (ValueError, IndexError)`). Robust.
- **`valoare_prudenta.py`, `big.py` (mapper/recipisă)**: module pure; singurul wiring web e prin `registru.py`
  (acoperit de H14-1). `estimeaza_valoare_prudenta`/`emite_recipisa` nu sunt expuse pe niciun endpoint.

---

*Notă de mediu:* fișierul `web/routers/registru.py` a fost modificat de o sesiune concurentă în timpul auditului
(commit `7c97341 feat(registru): actiune „pregateste pentru BIG"` a adăugat `/api/dosar/{uid}/big` și wiring-ul
`big`). Findings-urile de mai sus reflectă starea de la commit-ul `7c97341` (HEAD la momentul auditului).
