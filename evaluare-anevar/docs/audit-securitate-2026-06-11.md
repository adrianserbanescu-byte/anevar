# Audit de securitate — aplicația ANEVAR (2026-06-11)

Domeniu: `src/evaluare` (aplicație LOCALĂ single-user, fără login; date PII/CNP + AML).
Mod: READ-ONLY. Referințe: `fișier:linie`.

## Rezumat

Postura de securitate este SOLIDĂ. Apărările cheie sunt prezente și corecte:

- Anti-SSRF cu re-validare per-redirect (`url_parser.py:404-445`) — IP public obligatoriu, redirecturi urmate manual.
- Host-guard + CSRF Origin-check + plafon corp 50 MB + security headers/CSP (`web/app.py:60-117`).
- Anti path-traversal: `uid` validat ca UUID înainte de `rmtree` (`dosare_fs.py:33-45`); `_nume_fisier_sigur` (`curent.py:35-40`).
- SQL exclusiv parametrizat (`db/storage.py`); zero `eval`/`exec`/deserializare nesigură/apeluri shell directe; singurul `subprocess` (soffice) e cu listă de argumente, `shell=False`, cale locală (`report/pdf.py:37`).
- Anonimizare PII + plasă de siguranță CNP/tel/email înainte de narativul AI (`anonymizer.py`, `ai/narrative.py:77-88,194-197`).
- Dependențe: `pip-audit -r requirements.lock` → „No known vulnerabilities found"; CVE-uri tranzitive deja fixate (urllib3/idna/pypdf, `pyproject.toml:18-22`).
- `.gitignore` exclude `.env`, `*.db`, `date/` — fără date/secrete urcate; zero secrete hardcodate (grep curat; chei doar din `os.environ`, `config.py:41-44`).

Findings deschise mai jos (1 MEDIUM, 2 LOW/INFO). Nu repet findings închise (SSRF-redirect, prompt-injection, anonimizare CNP la narativ).

---

## F-SEC-1 (MEDIUM) — adresa trimisă neanonimizată la AI prin `/api/zona`

`zona.py:43` — `extrage_zona` trimite adresa BRUTĂ direct la furnizorul AI:

```python
raw = client.complete(SYSTEM_ZONA, f"Adresa: {adresa}")
```

Endpoint: `piata.py:77-80` (`POST /api/zona`). Adresa imobilului este dată cu caracter
personal (stradă + număr + localitate), iar fiind text liber poate include și numele
proprietarului sau alte date. Spre deosebire de fluxul narativ (`assembler.py:254-255`),
care construiește un `Anonymizer` ȘI aplică `filtreaza_pii_rezidual`, calea `/api/zona` NU
aplică NICIUNA dintre cele două plase. Rezultă o transmitere PII către terț (Anthropic /
Perplexity) fără mascare — divergență GDPR față de restul aplicației.

Recomandare: înainte de `client.complete`, treci adresa prin `filtreaza_pii_rezidual`
(minimul de paritate cu narativul) și, ideal, prin fallback-ul determinist offline când
nu e nevoie reală de LLM. `_fallback(adresa)` (`zona.py:28-34`) parsează deja județul +
localitatea local — în multe cazuri AI-ul nici nu e necesar.

## F-SEC-2 (LOW) — documente AML cu CNP rămân în temp, nume predictibil, fără ștergere

`aml.py:36-40` — `_doc_response` scrie `.docx`-ul AML (fișa KYC, RTN/RTS, evaluare risc —
conțin CNP, nume, serie act) în `tempfile.gettempdir()` cu nume FIX, predictibil
(`aml_fisa_kyc.docx`, `aml_rtn.docx`...) și întoarce `FileResponse` FĂRĂ `BackgroundTask`
de curățare. Astfel PII-ul rămâne pe disc în temp-ul partajat al mașinii nelimitat.

Contrast: endpointul de raport (`curent.py:284-295`) folosește token unic + `_sterge`
(BackgroundTask) care șterge copia temporară după trimitere.

Impact redus (mașină locală single-user), dar e PII sensibil persistat necriptat în locație
partajată cu nume ghicibil. Recomandare: nume cu sufix aleator (ca la raport) + `BackgroundTask`
care face `unlink(missing_ok=True)` după răspuns; aliniază cu igiena PII deja aplicată la raport.

## F-SEC-3 (LOW/INFO) — datele locale (DB, dosare, AML, cont) stocate necriptat

Toate PII-urile sunt în clar: `evaluari.db` (`db/storage.py`), `date/dosare/*/dosar.json`
(`dosare_fs.py`), `aml_confidential/*.json` (`aml/store.py` — fișierele individuale au totuși
`0o600`, dar directorul e creat cu perms implicite, `store.py:30`), `cont.json` (`cont.py`).
Backup-ul (`/api/backup-dosare.zip`, `curent.py:363-379`) împachetează tot necriptat.

Pentru o aplicație locală single-user e o decizie de design acceptabilă (deja documentată),
dar merită notat ca risc rezidual: orice acces la disc/backup expune CNP-uri. Recomandare
(opțional, dependent de modelul de amenințare al lui Adi): criptare at-rest a folderului
`aml_confidential` (cel mai sensibil — RTS/tipping-off) sau, minim, doc explicit + dependență
de criptarea de disc a stației (BitLocker). Niciun cod nou obligatoriu acum.

---

## Verificat și OK (fără finding)

- Injection (SQL): 100% parametrizat (`db/storage.py:111-217`); `PRAGMA user_version = {v}` e int controlat (`storage.py:89`).
- Command/subprocess: doar soffice, listă args, `shell=False`, cale locală validată (`report/pdf.py`).
- Template/SSTI: Jinja2 autoescape on; `|safe` doar pe conținut app-controlled (`document.html:12`, `_cartus.html`); date scraped trec prin `escapeHtml()`/`urlSafe()` în JS (`descoperire.html:183`, `grila.html:103`).
- SSRF: `_url_public_sigur` + re-validare per Location (`url_parser.py:404-445`); portalurile de căutare sunt allowlist fix (`portal_search.py:19-39`).
- Deserializare: doar `json.loads` pe input neîncredut (cu try/except → 422); modele Pydantic validate; fără formate de serializare nesigure.
- Prompt-injection: `SYSTEM_EXTRACT` cadrează datele ca neîncredute cu delimitatori (`extractor.py:18-25,157-159`) — finding închis, păstrat OK.
- Headers/CSRF/host-guard: acoperire pe TOATE răspunsurile via middleware (`app.py:65-109`).
- Secrete: zero hardcodate; chei doar din env (`config.py`); `.env` în `.gitignore`.
- Dependențe: pip-audit curat pe `requirements.lock`.
