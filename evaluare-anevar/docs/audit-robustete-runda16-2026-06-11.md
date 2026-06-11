# Audit robustețe — RUNDA 16 (2026-06-11)

**Țintă:** suprafața de **DESCOPERIRE + IMPORT** care procesează HTML/text NETRUSTED din portaluri și
din extensia de browser: `/api/descopera`, `/api/descopera-teren`, `/api/import-anunt`, `/api/import-url`,
`/api/grila-*`, `/api/anunturi-importate*` + parserele (`importers/url_parser.py`,
`discovery/extractor.py`, `discovery/orchestrator.py`, `discovery/portal_search.py`).

**Metodă:** READ-ONLY. Citire cod + **probe reproduse local** (`.venv` Python 3.13.13, `PYTHONUTF8=1`):
funcții directe + `TestClient(create_app(...))` end-to-end. Pentru fiecare finding: payload concret,
locație exactă, fix. NU repet findings RUNDA 9–15 (data ISO/an absurd, `nume_fisier`, DoS body 50MB,
Infinity→Decimal la `_to_decimal`, AML liste/string, registru/BIG `gt=0`).

**Verdict de ansamblu:** suprafața de import e bine gardată pe clasa „Infinity Decimal" (R9), dar are
**3 vectori NOI confirmați** care întorc **500** sau **blochează workerul** pe input HTML/text ostil, plus
2 findings minore. Toate sunt pe coduri *neacoperite* de rundele anterioare: `RecursionError` din
`json.loads` (nu e `ValueError`, deci scapă de toate gărzile existente), **ReDoS** pe 3 regex-uri din
parser/orchestrator, și `OverflowError` din extractor.

| ID | Severitate | Rezumat | Locație |
|----|-----------|---------|---------|
| **F-16-1** | **HIGH** | `json.loads` pe `__NEXT_DATA__`/JSON-LD adânc imbricat → `RecursionError` (NU `ValueError`) → **500** neprins | `url_parser.py:308` (+`:101,162`, `orchestrator.py:39`) via `/api/import-anunt`, `/api/import-url`, `/api/descopera*` |
| **F-16-2** | **HIGH** | **ReDoS** pe regexul „N mp" în `parse_listing_html` → titlu/og ostil blochează workerul (n=5000 → 3.2s, n=20000 → >30s) | `url_parser.py:347` via `/api/import-anunt`, `/api/import-url`, `/api/descopera*` |
| **F-16-3** | **HIGH** | **ReDoS** pe `_RE_TEREN_TEXT` în orchestrator → titlu/descriere ostil (n=20000 → 10s, n=50000 → 69s) | `orchestrator.py:97` via `/api/descopera`, `/api/descopera-teren` |
| **F-16-4** | **MEDIUM** | `max_candidati` **nemărginit + negativ** acceptat (1e9, -5) → amplificare fetch/parse per request | `schemas.py:87,115` (`DescoperaRequest`, `DescoperaTerenRequest`) |
| **F-16-5** | **LOW** | `OverflowError` din `_int_safe(int(float('inf')))` pe ieșire LLM ostilă (`an: 1e400`) → neprins de gărzile endpoint → **500** | `extractor.py:69` via `/api/descopera` (cu `client` LLM configurat) |

---

## F-16-1 (HIGH) — `RecursionError` din `json.loads` pe blob imbricat → 500 neprins

**Locație:** `src/evaluare/importers/url_parser.py:306-310` (JSON-LD), `:101` (`_din_nextdata`),
`:162` (`_caracteristici_storia`); `src/evaluare/discovery/orchestrator.py:39` (`_descriere_din_nextdata`).

```python
# url_parser.py:306
for script in soup.find_all("script", type="application/ld+json"):
    try:
        data = json.loads(script.get_text() or "")
    except (json.JSONDecodeError, TypeError, ValueError):   # <-- NU prinde RecursionError
        continue
```

**Cauză rădăcină:** decoderul C de JSON din CPython **recursează** pe array-uri/obiecte imbricate. Un
`<script type="application/ld+json">[[[…3000…0…]]]</script>` (sau `<script id="__NEXT_DATA__">`) depășește
limita de recursie → `json.loads` ridică **`RecursionError`**. `RecursionError` e subclasă de `RuntimeError`,
**nu** de `ValueError` → blocul `except (json.JSONDecodeError, TypeError, ValueError)` NU îl prinde →
propagă din `parse_listing_html`.

La nivel de endpoint:
- `/api/import-anunt` prinde doar `except ValueError` (`descoperire.py:115`) → **500**.
- `/api/import-url` prinde doar `except (ValueError, OSError)` (`piata.py:24`) → **500**.
- `/api/descopera*` prind doar `(requests.RequestException, ValueError, OSError)` → **500**.

**Probă (end-to-end, confirmată — TestClient re-ridică excepția de server, dovada că NU e prinsă):**
```python
nested = "[" * 3000 + "0" + "]" * 3000
html = f'<script type="application/ld+json">{nested}</script>'
c.post("/api/import-anunt", json={"html": html, "url": "http://x"})
# RecursionError: maximum recursion depth exceeded while decoding a JSON array
#   -> url_parser.py:308 json.loads -> 500 (neprins de except ValueError)
```
Reprodus identic și cu `<script id="__NEXT_DATA__">{nested}</script>` și cu `/api/import-url` (fetcher ostil).
Câteva sute de KB de paranteze = un singur request care întoarce 500; trivial de trimis din extensie sau
de un portal compromis/MITM pe fluxul de descoperire.

**Fix:** prinde și `RecursionError` (sau `Exception` larg, cu log) la fiecare `json.loads` pe conținut
netrusted din parser/orchestrator — minim cele 4 locuri de mai sus:
```python
except (json.JSONDecodeError, TypeError, ValueError, RecursionError):
    continue   # / return None,None,None,None  / return {}  / return ""
```
Defense-in-depth la endpoint: în `/api/import-anunt` și `/api/import-url`, extinde `except` la
`(ValueError, OSError, RecursionError)` → 422. Opțional, plafonează lungimea blobului `__NEXT_DATA__`/JSON-LD
înainte de `json.loads` (ex. respinge >2 MB) ca să nu cheltui timp pe payload-uri patologice.

---

## F-16-2 (HIGH) — ReDoS pe regexul „N mp" în `parse_listing_html`

**Locație:** `src/evaluare/importers/url_parser.py:347`
```python
for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*mp\b", text_cautare, re.IGNORECASE):
```
`text_cautare` = `titlu` + `og:title` + `og:description` — **toate attacker-controlled** (HTML din extensie
sau portal). Ramura rulează ori de câte ori `suprafata is None` (cazul normal pe anunțuri fără date
structurate). Pe un titlu format dintr-un șir lung de cifre care **nu** se termină în `mp`, motorul `re`
încearcă fiecare poziție de start (`finditer`) × backtracking pe `\d+` → cost super-liniar.

**Probă (confirmată):**
```python
up.parse_listing_html(f"<title>{'1'*5000} X</title>", "http://x")    # 3.20 s
up.parse_listing_html(f"<title>{'1'*20000} X</title>", "http://x")   # > 30 s (timeout)
```
Un `<title>` de ~20 KB blochează workerul zeci de secunde pe **un singur** request; câteva request-uri
concurente epuizează pool-ul (`/api/import-anunt`, `/api/import-url`, și fiecare candidat din `/api/descopera`).

**Fix:** ancorează / mărginește numărul de cifre, ex. `r"(\d{1,7}(?:[.,]\d{1,3})?)\s*mp\b"` (o suprafață
realistă are ≤7 cifre). Și/sau truncă `text_cautare` la o lungime rezonabilă (ex. 5–10 KB) înainte de
regex — titlul/descrierea legitime sunt scurte.

---

## F-16-3 (HIGH) — ReDoS pe `_RE_TEREN_TEXT` în orchestrator

**Locație:** `src/evaluare/discovery/orchestrator.py:97-101`
```python
_RE_TEREN_TEXT = re.compile(
    r"(?:teren\w*(?:\s+de)?\s*:?\s*([\d][\d.  ]*)\s*(?:mp|m²|m2)"
    r"|([\d][\d.  ]*)\s*(?:mp|m²|m2)\s+teren)",
    re.IGNORECASE,
)
```
Apelat din `descopera` (`orchestrator.py:192`) pe `parsed.titlu` și `descriere` — ambele derivate din HTML
ostil. Clasa `[\d.  ]*` (cifre + punct + două feluri de spațiu) urmată de `(?:mp|m²|m2)` backtrack-uiește
catastrofal pe un șir lung care nu se termină în unitate.

**Probă (confirmată):**
```python
orch._teren_din_text("teren " + "1"*20000 + "X")   # 10.35 s
orch._teren_din_text("teren " + "1"*50000 + "X")   # 68.95 s
orch._teren_din_text("teren " + "1. "*5000 + "X")  #  1.98 s  (varianta cu punct/spațiu)
```
Pe fluxul `/api/descopera` și `/api/descopera-teren`, un singur anunț cu descriere ostilă (sau un portal
care injectează un astfel de text) blochează workerul ~un minut → DoS.

**Fix:** mărginește repetițiile, ex. `([\d][\d.  ]{0,12})` (max ~13 caractere = suprafață realistă), și/sau
truncă textul pasat în `_teren_din_text` (deja se preferă `parsed.titlu` — limitează-l). Posesiv/atomic nu
e direct în `re`, dar limita de lungime e suficientă.

---

## F-16-4 (MEDIUM) — `max_candidati` nemărginit (și negativ) la schemă

**Locație:** `src/evaluare/web/schemas.py:87` (`DescoperaTerenRequest`), `:115` (`DescoperaRequest`)
```python
max_candidati: int = 20    # fără Field(ge=..., le=...)
```
**Probă (confirmată):** `DescoperaRequest(..., max_candidati=10**9)` → acceptat (1000000000);
`DescoperaTerenRequest(..., max_candidati=-5)` → acceptat (-5). UI-ul clampează client-side la 1..50
(`descoperire.html:489`, `:130`), dar API-ul nu — un client direct ocolește clamparea.

În orchestrator, `urls = cauta_anunturi_multi(...)[:max_candidati]` (`orchestrator.py:167`, `:275`): un
`max_candidati` uriaș nu limitează lista (o lasă întreagă), iar cu un fetcher live, fiecare URL găsit
declanșează un `fetcher(url)` + `parse_listing_html` (deci și F-16-2). Valoarea negativă produce
`urls[:-5]` → tăcut omite ultimii N candidați (rezultat surprinzător, nu crash). Nu e 500 pe cont propriu,
dar **amplifică** F-16-2/F-16-3 și e o slăbiciune de amplificare DoS.

**Fix:** `max_candidati: int = Field(default=20, ge=1, le=50)` pe ambele scheme (paritate cu clamp-ul UI) →
422 pe valori în afara intervalului, fără să te bazezi pe front-end.

---

## F-16-5 (LOW) — `OverflowError` din extractor pe ieșire LLM ostilă → 500

**Locație:** `src/evaluare/discovery/extractor.py:68-72`
```python
def _int_safe(x) -> int | None:
    try:
        return int(x)
    except (TypeError, ValueError):   # <-- NU prinde OverflowError
        return None
```
`extrage_atribute` face `json.loads` pe răspunsul LLM (`extractor.py:174`); un `an: 1e400` din JSON devine
`float('inf')`, iar `_int_safe(int(float('inf')))` ridică **`OverflowError`** (subclasă de `ArithmeticError`,
NU de `ValueError`). Doar `json.loads` e în try-ul `except (ValueError, TypeError)` (`:175`); `_build_profile`
→ `_int_safe` rulează **după** try → `OverflowError` propagă din `descopera` → endpoint-ul `/api/descopera`
prinde doar `(requests.RequestException, ValueError, OSError)` → **500**.

**Probă (confirmată):**
```python
extrage_atribute("text", [("garaj","da")], EvilClient('{"an": 1e400, ...}'))
# OverflowError: cannot convert float infinity to integer
# idem pentru {"an": {"valoare": 1e400}}  (forma dict)
```
Condiționat de un **client LLM configurat** (în multe deploy-uri `client=None` → fallback determinist, fără
suprafață). Textul `descriere` e HTML ostil → un atacant poate face prompt-injection ca LLM-ul să emită
`"an": 1e400`. Probabilitate mai mică (depinde de complianța modelului), de aici LOW.

**Fix:** extinde garda din `_int_safe` și `_to_decimal` (extractor) la `(TypeError, ValueError, ArithmeticError)`
(sau `Exception`) → întoarce `None`. Defense-in-depth: la `/api/descopera`, adaugă `ArithmeticError` în
clauza `except` → 502/422 în loc de 500.

---

## Suprafețe verificate FĂRĂ finding (rezultate negative, pentru trasabilitate)

- **`_to_decimal` / `_to_decimal_ro` (url_parser):** taie non-finit la sursă (R9) — `1e400` → `None`. Confirmat
  pe JSON-LD `price=1e400` → 200 (preț dezbrăcat), nu 500. Robust.
- **Regexul de preț `(\d[\d.\s]{3,})\s*(eur|euro|€|lei)` (`url_parser.py:358`):** pe șiruri lungi de
  cifre/puncte/spații fără monedă rulează în <20 ms la n=40000 — `\s` nu se potrivește pe `.`, deci nu
  backtrack-uiește. Robust.
- **`_caracteristici_imobiliare` (`url_parser.py:215`):** toate clasele sunt mărginite
  (`{2,40}`, `{1,16}`, `\d{4}`) → fără ReDoS. Robust.
- **`_din_nextdata` / `_caracteristici_storia` / `_descriere_din_nextdata`:** traversare cu **stack explicit**
  (nu recursie Python) → fără `RecursionError` la *traversare*. Vulnerabilitatea e doar la `json.loads`
  însuși (F-16-1), nu la walk.
- **SSRF pe `/api/import-url`:** `_url_public_sigur` re-validează FIECARE `Location` în bucla de redirect
  manuală (`fetch_html:435`), blochează loopback/privat/link-local/reserved, plafon 5 redirecturi. Solid —
  niciun SSRF rezidual găsit pe acest flux.
- **`/api/grila-*`:** `suprafata_subiect: Field(gt=0)` + comparabile cu `Field(gt=0)` pe preț/suprafață;
  motorul prins în `except (ValueError, ArithmeticError)` → 422 (`grile.py:47,63,84`). Valori degenerate
  (subnormale/uriașe) → 422, nu 500. Robust.
- **`/api/anunturi-importate*`:** doar listare/ștergere pe SQLite, fără parsing de HTML netrusted. Fără
  suprafață de 500 nouă.
- **`max_candidati` negativ:** `urls[:-5]` → omite tăcut candidați (rezultat surprinzător), dar NU crash;
  acoperit de fixul F-16-4.
- **Plafon corp 50 MB (`app.py:94`):** validează doar header-ul `Content-Length`; payload-urile ReDoS/
  RecursionError de mai sus sunt **mici** (KB–zeci de KB) → trec sub plafon. Plafonul nu apără de F-16-1..3.

---

*Notă:* probe rulate pe `src/evaluare/` la `HEAD` `400da88` (master, 2026-06-11); fișierele țintă
(`url_parser.py`, `orchestrator.py`, `extractor.py`, `schemas.py`) sunt neschimbate față de momentul
auditului. F-16-1 și F-16-5 sunt fixabile prin lărgirea clauzelor `except` (clase de excepție care nu sunt
`ValueError`); F-16-2/F-16-3 prin mărginirea repetițiilor în regex + truncarea textului; F-16-4 prin
`Field(ge=1, le=50)`. Toate sunt schimbări mici, fără atingerea logicii de business.
