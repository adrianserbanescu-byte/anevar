# Import comparabile prin URL (scraping direct) — Plan 4 (partea 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Evaluatorul lipește URL-ul unui anunț (imobiliare.ro / storia.ro), iar aplicația extrage automat prețul și suprafața și le returnează ca un comparabil parțial, de confirmat manual.

**Architecture:** Un modul `importers/url_parser.py` parsează HTML-ul unui anunț folosind, în ordine, datele structurate schema.org (`application/ld+json`), apoi meta-tag-uri Open Graph, apoi None. Fetcher-ul HTTP este injectabil → testabil offline pe fixturi HTML salvate (fără rețea). Un endpoint `POST /api/import-url` expune funcția în aplicația web.

**Tech Stack:** Python 3.11+, requests, beautifulsoup4, pytest. Reutilizează `evaluare.models.comparable.Comparable`.

**Decizie:** scraping direct (gratis, fragil). Parserul preferă datele structurate (stabile) și degradează grațios. Fără rețea în teste.

**Avertisment documentat în cod:** scraping-ul direct poate încălca Termenii și Condițiile site-urilor și se poate strica la schimbări de layout. Folosit pe răspunderea evaluatorului, cu rate-limiting minim.

**Depinde de:** Planurile 1-3. Branch: `feature/nucleu-calcul`.

---

## Structura de fișiere

```
evaluare-anevar/
├── pyproject.toml                          # MODIFICAT: requests, beautifulsoup4
├── src/evaluare/importers/
│   ├── __init__.py                         # NOU
│   └── url_parser.py                       # NOU: parsare anunt -> ParsedListing -> Comparable
├── src/evaluare/web/app.py                 # MODIFICAT: endpoint POST /api/import-url + fetcher injectabil
└── tests/
    ├── fixtures/
    │   ├── imobiliare_listing.html         # NOU: fixtura HTML (JSON-LD)
    │   └── storia_listing.html             # NOU: fixtura HTML (JSON-LD)
    ├── test_url_parser.py                  # NOU
    └── test_web_import.py                  # NOU
```

---

## Phase 0 — Dependențe

### Task 0: Adaugă requests și beautifulsoup4

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Adaugă în blocul `dependencies`** (după `jinja2>=3.1`):
```toml
    "requests>=2.31",
    "beautifulsoup4>=4.12",
```

- [ ] **Step 2: Instalează**

Run (din `evaluare-anevar/`): `python -m pip install --timeout 120 --retries 5 requests beautifulsoup4`

- [ ] **Step 3: Verifică**

Run: `python -c "import requests, bs4; print('ok')"` → `ok`.
Run: `python -m pytest -q` → 68 passed.

- [ ] **Step 4: Commit (din repo root)**
```bash
git add evaluare-anevar/pyproject.toml
git commit -m "chore: dependinte scraping (requests, beautifulsoup4)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 1 — Parserul de anunțuri

### Task 1: `importers/url_parser.py` + fixturi

**Files:**
- Create: `src/evaluare/importers/__init__.py`  (empty)
- Create: `src/evaluare/importers/url_parser.py`
- Create: `tests/fixtures/imobiliare_listing.html`
- Create: `tests/fixtures/storia_listing.html`
- Test: `tests/test_url_parser.py`

- [ ] **Step 1: Creează fixturile**

`tests/fixtures/imobiliare_listing.html`:
```html
<!DOCTYPE html>
<html lang="ro"><head><meta charset="utf-8">
<title>Casa individuala 5 camere, Otopeni</title>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product",
 "name":"Casa individuala 5 camere, Otopeni",
 "offers":{"@type":"Offer","price":"250000","priceCurrency":"EUR"}}
</script>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"RealEstateListing",
 "name":"Casa Otopeni",
 "floorSize":{"@type":"QuantitativeValue","value":"180","unitCode":"MTK"}}
</script>
<meta property="og:title" content="Casa individuala 5 camere, Otopeni - 250.000 EUR">
</head><body><h1>Casa individuala 5 camere</h1><p>Suprafata utila 180 mp.</p></body></html>
```

`tests/fixtures/storia_listing.html`:
```html
<!DOCTYPE html>
<html lang="ro"><head><meta charset="utf-8">
<title>Vila P+1, Pipera</title>
<script type="application/ld+json">
{"@context":"https://schema.org","@graph":[
  {"@type":"Residence","name":"Vila P+1, Pipera",
   "floorSize":{"@type":"QuantitativeValue","value":"220","unitCode":"MTK"}},
  {"@type":"Offer","price":"1350000","priceCurrency":"RON"}
]}
</script>
</head><body><h1>Vila P+1</h1></body></html>
```

- [ ] **Step 2: Scrie testul care eșuează**

`tests/test_url_parser.py`:
```python
from decimal import Decimal
from pathlib import Path

import pytest

from evaluare.importers.url_parser import (
    ParsedListing,
    parse_listing_html,
    to_comparable,
    import_from_url,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_parse_imobiliare_extracts_price_and_surface():
    parsed = parse_listing_html(_html("imobiliare_listing.html"),
                                sursa_url="https://imobiliare.ro/x")
    assert parsed.pret == Decimal("250000")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("180")
    assert parsed.sursa_url == "https://imobiliare.ro/x"


def test_parse_storia_handles_graph():
    parsed = parse_listing_html(_html("storia_listing.html"),
                                sursa_url="https://storia.ro/y")
    assert parsed.pret == Decimal("1350000")
    assert parsed.moneda == "RON"
    assert parsed.suprafata == Decimal("220")


def test_parse_returns_none_fields_when_absent():
    parsed = parse_listing_html("<html><body>nimic</body></html>")
    assert parsed.pret is None
    assert parsed.suprafata is None


def test_to_comparable_builds_from_parsed():
    parsed = ParsedListing(pret=Decimal("250000"), moneda="EUR",
                           suprafata=Decimal("180"), titlu="Casa",
                           sursa_url="https://imobiliare.ro/x")
    comp = to_comparable(parsed)
    assert comp.pret == Decimal("250000")
    assert comp.suprafata == Decimal("180")
    assert comp.sursa == "https://imobiliare.ro/x"
    assert comp.tip_oferta == "oferta"


def test_to_comparable_requires_price_and_surface():
    parsed = ParsedListing(pret=None, moneda=None, suprafata=Decimal("180"),
                           titlu="", sursa_url="")
    with pytest.raises(ValueError):
        to_comparable(parsed)


def test_import_from_url_uses_injected_fetcher():
    html = _html("imobiliare_listing.html")
    parsed = import_from_url("https://imobiliare.ro/x", fetcher=lambda url: html)
    assert parsed.pret == Decimal("250000")
    assert parsed.suprafata == Decimal("180")
```

- [ ] **Step 3: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_url_parser.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.importers'`.

- [ ] **Step 4: Implementează parserul**

`src/evaluare/importers/__init__.py` — empty file.

`src/evaluare/importers/url_parser.py`:
```python
"""Import comparabile dintr-un anunt online (scraping direct).

AVERTISMENT: scraping-ul direct poate incalca Termenii si Conditiile site-urilor
si se poate strica la schimbari de layout. Folosit pe raspunderea evaluatorului.
Parserul prefera datele structurate schema.org (stabile) si degradeaza gratios.
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Callable, Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from evaluare.models.comparable import Comparable

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


class ParsedListing(BaseModel):
    """Datele extrase dintr-un anunt (partiale, de confirmat de evaluator)."""

    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None
    titlu: str = ""
    sursa_url: str = ""


def _to_decimal(value) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def _iter_nodes(data):
    """Itereaza recursiv nodurile dintr-un obiect JSON-LD (dict/list/@graph)."""
    if isinstance(data, list):
        for item in data:
            yield from _iter_nodes(item)
    elif isinstance(data, dict):
        yield data
        if "@graph" in data:
            yield from _iter_nodes(data["@graph"])


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata din HTML-ul unui anunt."""
    soup = BeautifulSoup(html, "html.parser")
    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _iter_nodes(data):
            offers = node.get("offers")
            if isinstance(offers, dict):
                if pret is None and "price" in offers:
                    pret = _to_decimal(offers.get("price"))
                    moneda = moneda or offers.get("priceCurrency")
            if pret is None and node.get("@type") == "Offer" and "price" in node:
                pret = _to_decimal(node.get("price"))
                moneda = moneda or node.get("priceCurrency")
            floor = node.get("floorSize")
            if suprafata is None and isinstance(floor, dict):
                suprafata = _to_decimal(floor.get("value"))

    titlu = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        titlu = title_tag.string.strip()

    return ParsedListing(pret=pret, moneda=moneda, suprafata=suprafata,
                         titlu=titlu, sursa_url=sursa_url)


def to_comparable(parsed: ParsedListing) -> Comparable:
    """Construieste un Comparable dintr-un ParsedListing (cere pret + suprafata)."""
    if parsed.pret is None or parsed.suprafata is None:
        raise ValueError(
            "Anuntul nu contine pret si suprafata; completati manual comparabilul."
        )
    return Comparable(
        sursa=parsed.sursa_url or "url",
        pret=parsed.pret,
        suprafata=parsed.suprafata,
        tip_oferta="oferta",
    )


def fetch_html(url: str) -> str:
    """Descarca HTML-ul unui anunt (live). Nu se foloseste in teste."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    return resp.text


def import_from_url(
    url: str, fetcher: Callable[[str], str] = fetch_html
) -> ParsedListing:
    """Descarca si parseaza un anunt. Fetcher injectabil pentru testare offline."""
    html = fetcher(url)
    return parse_listing_html(html, sursa_url=url)
```

- [ ] **Step 5: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_url_parser.py -v`
Expected: PASS (6 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 6: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/importers/__init__.py evaluare-anevar/src/evaluare/importers/url_parser.py evaluare-anevar/tests/fixtures/imobiliare_listing.html evaluare-anevar/tests/fixtures/storia_listing.html evaluare-anevar/tests/test_url_parser.py
git commit -m "feat: parser anunt URL (schema.org JSON-LD) -> Comparable"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Endpoint de import în aplicația web

### Task 2: `POST /api/import-url` cu fetcher injectabil

**Files:**
- Modify: `src/evaluare/web/app.py`
- Test: `tests/test_web_import.py`

**Context de design:** `create_app` capătă un parametru opțional `fetcher` (implicit
`evaluare.importers.url_parser.fetch_html`). Endpoint-ul `POST /api/import-url` primește
`{"url": "..."}`, parsează și întoarce `{pret, moneda, suprafata, titlu, sursa_url}`. Dacă
parserul nu găsește nimic util, întoarce câmpuri `null` (nu eroare) — evaluatorul completează manual.

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_import.py`:
```python
from pathlib import Path

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

FIXTURES = Path(__file__).parent / "fixtures"


def _client(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    html = (FIXTURES / "imobiliare_listing.html").read_text(encoding="utf-8")
    app = create_app(storage=storage, client=None, fetcher=lambda url: html)
    return TestClient(app)


def test_import_url_returns_parsed_fields(tmp_path):
    client = _client(tmp_path)
    resp = client.post("/api/import-url", json={"url": "https://imobiliare.ro/x"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["pret"] == "250000"
    assert data["suprafata"] == "180"
    assert data["moneda"] == "EUR"


def test_import_url_empty_when_nothing_found(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    app = create_app(storage=storage, client=None,
                     fetcher=lambda url: "<html><body>nimic</body></html>")
    client = TestClient(app)
    resp = client.post("/api/import-url", json={"url": "https://x"})
    assert resp.status_code == 200
    assert resp.json()["pret"] is None
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_import.py -v`
Expected: FAIL (endpoint-ul nu există / `create_app` nu acceptă `fetcher`).

- [ ] **Step 3: Modifică `app.py`**

În `src/evaluare/web/app.py`, adaugă importurile (lângă celelalte):
```python
from typing import Callable
from pydantic import BaseModel
from evaluare.importers.url_parser import fetch_html, import_from_url
```
Adaugă un model de cerere (la nivel de modul, înainte de `create_app`):
```python
class ImportUrlRequest(BaseModel):
    url: str
```
Schimbă semnătura `create_app` ca să accepte `fetcher`:
```python
def create_app(storage: Storage, client: Optional[NarrativeClient],
               fetcher: Callable[[str], str] = fetch_html) -> FastAPI:
```
Adaugă endpoint-ul (înainte de `return app`):
```python
    @app.post("/api/import-url")
    def importa_url(req: ImportUrlRequest) -> dict:
        parsed = import_from_url(req.url, fetcher=fetcher)
        return {
            "pret": str(parsed.pret) if parsed.pret is not None else None,
            "moneda": parsed.moneda,
            "suprafata": str(parsed.suprafata) if parsed.suprafata is not None else None,
            "titlu": parsed.titlu,
            "sursa_url": parsed.sursa_url,
        }
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_import.py -v`
Expected: PASS (2 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/tests/test_web_import.py
git commit -m "feat: endpoint POST /api/import-url (parsare anunt -> campuri comparabil)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Verificare finală

### Task 3: Suită completă + reconstruire .exe

**Files:** niciunul (verificare)

- [ ] **Step 1: Rulează toată suita**

Run: `python -m pytest -q`
Expected: toate testele trec (Plan 1+2+3+4).

- [ ] **Step 2: Reconstruiește executabilul cu noul modul**

Run (din `evaluare-anevar/`): `python -m PyInstaller --noconfirm --clean evaluare-anevar.spec`
Expected: `dist/evaluare-anevar.exe` reconstruit fără erori.

- [ ] **Step 3: Commit final (dacă a rămas ceva)**
```bash
git status
git add -A && git commit -m "chore: verificare import URL + rebuild exe" || echo "nimic de comis"
```

---

## Recapitulare acoperire

| Cerință | Task |
|---|---|
| Parsare anunț (preț, suprafață) din date structurate | Task 1 |
| Degradare grațioasă când lipsesc date | Task 1 |
| Fetcher injectabil (teste offline pe fixturi) | Task 1, 2 |
| Endpoint web de import | Task 2 |
| Avertisment ToS/fragilitate documentat | Task 1 (docstring) |

**Rămâne (UI):** un buton „Import comparabil din URL" în formular care apelează `/api/import-url`
și pre-completează un rând de comparabil, plus suport în formular pentru metoda „piață" cu listă
de comparabile. Enhancement de UI, separat — backend-ul de import e complet și testat.

**Input necesar de la evaluator:** testează importul pe URL-uri reale; dacă structura site-ului
diferă de fixturi (alte câmpuri JSON-LD), trimite-mi un exemplu de HTML salvat ca să extind parserul.
