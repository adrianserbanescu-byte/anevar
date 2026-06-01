# Descoperire comparabile — extracție LLM + orchestrator + UI — Implementation Plan (partea 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Completează modulul de descoperire: extracția atributelor cu LLM (din descrierea reală a anunțului, mapând text→treaptă), orchestratorul complet (search → scrape → parse → extract → score → rank), endpoint-ul web și pagina UI cu tabelul de metodologie + lista de candidați (breakdown + bife + integrare în comparabile).

**Architecture:** Peste nucleul determinist (Planul-nucleu), adaugă: `discovery/extractor.py` (LLM injectabil, JSON validat, fallback fără cheie), `discovery/results.py` (rezultate), `discovery/orchestrator.py` (leagă tot), o funcție `metodologie()` în `scoring.py`, plus endpoint `POST /api/descopera`, rută `GET /descoperire` și pagina `descoperire.html`. Totul cu fetcher + client LLM injectabili → testat offline.

**Tech Stack:** Python 3.11+, Pydantic v2, beautifulsoup4, FastAPI/Jinja2, pytest. Fără dependențe noi.

**Spec sursă:** `docs/superpowers/specs/2026-05-31-descoperire-comparabile-design.md`.
**Depinde de:** Planul-nucleu `2026-05-31-descoperire-comparabile-nucleu.md` (profiles, scoring,
portal_search, parser întărit) **trebuie implementat înainte**. Plus Planurile 1-4. Branch: `feature/nucleu-calcul`.

**Reutilizat:** `NarrativeClient` (protocol `.complete(system, user) -> str`) ca client de extracție;
`Comparable` + `to_comparable()` pentru integrarea cu grila; `create_app(storage, client, fetcher)`.

---

## Structura de fișiere

```
evaluare-anevar/
├── src/evaluare/
│   ├── discovery/
│   │   ├── results.py              # NOU: SecondaryAttributeResult, CandidateExtraction, CandidateResult
│   │   ├── extractor.py            # NOU: extrage_atribute (LLM injectabil) + parse atribute secundare
│   │   ├── orchestrator.py         # NOU: extrage_descriere + descopera (pipeline complet)
│   │   └── scoring.py              # MODIFICAT: adauga metodologie()
│   └── web/
│       ├── app.py                  # MODIFICAT: POST /api/descopera + GET /descoperire
│       └── templates/
│           └── descoperire.html    # NOU: tabel metodologie + candidati cu bife
└── tests/
    ├── test_discovery_extractor.py # NOU (client fals)
    ├── test_discovery_metodologie.py # NOU
    ├── test_discovery_orchestrator.py # NOU (fetcher+client fals)
    └── test_web_descopera.py       # NOU (TestClient)
```

---

## Phase 1 — Rezultate + extractor LLM

### Task 1: `discovery/results.py`

**Files:**
- Create: `src/evaluare/discovery/results.py`
- Test: `tests/test_discovery_results.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_discovery_results.py`:
```python
from decimal import Decimal

from evaluare.discovery.profiles import CandidateProfile, ScoreBreakdown
from evaluare.discovery.results import (
    SecondaryAttributeResult, CandidateExtraction, CandidateResult,
)


def test_secondary_result():
    s = SecondaryAttributeResult(nume="tamplarie", stare="diferit",
                                 valoare_gasita="lemn stratificat")
    assert s.stare == "diferit"


def test_candidate_extraction():
    e = CandidateExtraction(profile=CandidateProfile(an=2008),
                            secundare=[SecondaryAttributeResult(nume="garaj",
                                       stare="potrivit", valoare_gasita="da")])
    assert e.profile.an == 2008
    assert e.secundare[0].nume == "garaj"


def test_candidate_result():
    b = ScoreBreakdown(relevanta=86, dissimilaritate=0.143, atribute=[],
                       atribute_cunoscute=4, incredere_scazuta=False, explicatie="...")
    r = CandidateResult(url="https://x", titlu="Casa", pret=Decimal("250000"),
                        suprafata=Decimal("180"), breakdown=b, secundare=[])
    assert r.pret == Decimal("250000")
    assert r.breakdown.relevanta == 86
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_discovery_results.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează modelele**

`src/evaluare/discovery/results.py`:
```python
"""Rezultate ale descoperirii: extracție LLM și candidat scorat."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

from evaluare.discovery.profiles import CandidateProfile, ScoreBreakdown

StareSecundar = Literal["potrivit", "diferit", "nementionat"]


class SecondaryAttributeResult(BaseModel):
    """Rezultatul unui atribut secundar (FYI) pentru un candidat."""

    nume: str
    stare: StareSecundar
    valoare_gasita: Optional[str] = None


class CandidateExtraction(BaseModel):
    """Ce a extras LLM-ul dintr-un anunț: profil primar + atribute secundare."""

    profile: CandidateProfile
    secundare: list[SecondaryAttributeResult] = Field(default_factory=list)


class CandidateResult(BaseModel):
    """Un candidat complet, scorat și gata de afișat/selectat."""

    url: str
    titlu: str = ""
    pret: Optional[Decimal] = None
    suprafata: Optional[Decimal] = None
    breakdown: ScoreBreakdown
    secundare: list[SecondaryAttributeResult] = Field(default_factory=list)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_discovery_results.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/results.py evaluare-anevar/tests/test_discovery_results.py
git commit -m "feat: modele rezultate descoperire (extractie + candidat scorat)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

### Task 2: `discovery/extractor.py` — extracție LLM (injectabil, fallback)

**Files:**
- Create: `src/evaluare/discovery/extractor.py`
- Test: `tests/test_discovery_extractor.py`

**Context de design:** `extrage_atribute(descriere, atribute_secundare, client)` cere LLM-ului să
extragă DIN TEXTUL FURNIZAT atributele primare (mapând text→treaptă pentru stare/finisaj, →categorie
pentru încălzire) și starea atributelor secundare. Clientul are interfața `.complete(system, user)
-> str` (reutilizat din `ai.narrative.NarrativeClient`). Răspunsul e JSON (posibil în fence
markdown) → curățat și validat. **Fără client (None) → fallback:** toate atributele „nementionat".

Contractul JSON pe care îl cerem LLM-ului:
```json
{
  "an": {"valoare": 2008, "text": "2008"},
  "stare": {"treapta": 4, "text": "renovat 2021"},
  "finisaj": {"treapta": 4, "text": "finisaje de lux"},
  "incalzire": {"categorie": "centrala_gaz", "text": "centrala proprie pe gaz"},
  "teren": {"valoare": null, "text": null},
  "secundare": [{"nume": "tamplarie", "stare": "diferit", "valoare_gasita": "lemn stratificat"}]
}
```

- [ ] **Step 1: Scrie testul care eșuează (cu client fals — fără rețea)**

`tests/test_discovery_extractor.py`:
```python
from decimal import Decimal

from evaluare.discovery.extractor import (
    parse_atribute_secundare, extrage_atribute,
)


def test_parse_atribute_secundare():
    linii = "tamplarie: termopan\ngaraj: da\npanouri solare"
    rez = parse_atribute_secundare(linii)
    assert rez == [("tamplarie", "termopan"), ("garaj", "da"), ("panouri solare", None)]


class FakeClient:
    def __init__(self, raspuns):
        self.raspuns = raspuns
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        return self.raspuns


def test_extrage_atribute_din_json():
    raspuns = '''```json
    {"an": {"valoare": 2008, "text": "2008"},
     "stare": {"treapta": 4, "text": "renovat 2021"},
     "finisaj": {"treapta": 4, "text": "lux"},
     "incalzire": {"categorie": "centrala_gaz", "text": "centrala pe gaz"},
     "teren": {"valoare": null, "text": null},
     "secundare": [{"nume": "tamplarie", "stare": "diferit", "valoare_gasita": "lemn"}]}
    ```'''
    client = FakeClient(raspuns)
    ext = extrage_atribute("text anunt...", [("tamplarie", "termopan")], client=client)
    assert ext.profile.an == 2008
    assert ext.profile.stare == 4
    assert ext.profile.incalzire == "centrala_gaz"
    assert ext.profile.teren is None
    assert ext.profile.texte["stare"] == "renovat 2021"
    assert ext.secundare[0].nume == "tamplarie"
    assert ext.secundare[0].stare == "diferit"
    assert ext.secundare[0].valoare_gasita == "lemn"


def test_extrage_atribute_fara_client_fallback():
    ext = extrage_atribute("text", [("garaj", None)], client=None)
    assert ext.profile.an is None
    assert ext.profile.stare is None
    # atributele secundare fara client -> nementionat
    assert ext.secundare[0].stare == "nementionat"


def test_extrage_atribute_json_invalid_degradeaza():
    client = FakeClient("nu e json")
    ext = extrage_atribute("text", [], client=client)
    assert ext.profile.an is None      # degradare grațioasă, nu excepție
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_discovery_extractor.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează `extractor.py`**

`src/evaluare/discovery/extractor.py`:
```python
"""Extracția atributelor dintr-un anunț, cu LLM (injectabil) — DOAR din text furnizat.

Niciodată căutare/generare: LLM-ul primește descrierea reală și extrage; ce nu apare → nementionat.
"""
from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Optional

from evaluare.ai.narrative import NarrativeClient
from evaluare.discovery.profiles import CandidateProfile
from evaluare.discovery.results import CandidateExtraction, SecondaryAttributeResult

SYSTEM_EXTRACT = (
    "Esti un extractor de date. Extragi informatii DOAR din textul anuntului primit; "
    "nu inventezi si nu cauti in alta parte. Pentru ce nu apare in text, intorci null / "
    "«nementionat». Raspunzi EXCLUSIV cu JSON valid, fara text in plus."
)


def parse_atribute_secundare(text: str) -> list[tuple[str, Optional[str]]]:
    """Parsează textul (un atribut pe linie, „nume: valoare_dorită") în perechi."""
    rezultat: list[tuple[str, Optional[str]]] = []
    for linie in (text or "").splitlines():
        linie = linie.strip()
        if not linie:
            continue
        if ":" in linie:
            nume, val = linie.split(":", 1)
            rezultat.append((nume.strip(), val.strip() or None))
        else:
            rezultat.append((linie, None))
    return rezultat


def _curata_json(text: str) -> str:
    """Scoate eventualele fence-uri markdown din raspunsul LLM."""
    m = re.search(r"\{.*\}", text, re.DOTALL)
    return m.group(0) if m else text


def _to_decimal(value) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ValueError, ArithmeticError):
        return None


def _build_profile(data: dict) -> CandidateProfile:
    def nod(key):
        n = data.get(key)
        return n if isinstance(n, dict) else {}
    an = nod("an").get("valoare")
    stare = nod("stare").get("treapta")
    finisaj = nod("finisaj").get("treapta")
    incalzire = nod("incalzire").get("categorie")
    teren = _to_decimal(nod("teren").get("valoare"))
    texte = {}
    for name in ["an", "stare", "finisaj", "incalzire", "teren"]:
        t = nod(name).get("text")
        if t:
            texte[name] = str(t)
    return CandidateProfile(
        an=int(an) if an is not None else None,
        stare=int(stare) if stare is not None else None,
        finisaj=int(finisaj) if finisaj is not None else None,
        incalzire=incalzire, teren=teren, texte=texte,
    )


def _fallback(atribute_secundare) -> CandidateExtraction:
    secundare = [SecondaryAttributeResult(nume=n, stare="nementionat")
                 for n, _ in atribute_secundare]
    return CandidateExtraction(profile=CandidateProfile(), secundare=secundare)


def extrage_atribute(
    descriere: str,
    atribute_secundare: list[tuple[str, Optional[str]]],
    client: Optional[NarrativeClient],
) -> CandidateExtraction:
    """Extrage atributele primare + starea celor secundare din descrierea anuntului."""
    if client is None:
        return _fallback(atribute_secundare)

    lista_sec = "; ".join(
        f"{n} (dorit: {v})" if v else n for n, v in atribute_secundare
    ) or "(niciunul)"
    user = (
        "Text anunt:\n" + descriere + "\n\n"
        "Extrage atributele primare: an (numar), stare (treapta 1-5: 1=degradata..5=noua), "
        "finisaj (treapta 1-4: 1=modest..4=lux), incalzire (categorie ex. centrala_gaz, "
        "centrala_lemn, pompa_caldura, sobe), teren (mp). Pentru fiecare da {valoare/treapta/"
        "categorie, text} sau null daca nu apare.\n"
        f"Atribute secundare de verificat: {lista_sec}. Pentru fiecare intoarce "
        "{nume, stare: potrivit/diferit/nementionat, valoare_gasita}.\n"
        "Raspunde cu JSON conform schemei."
    )
    try:
        raw = client.complete(SYSTEM_EXTRACT, user)
        data = json.loads(_curata_json(raw))
    except (ValueError, TypeError):
        return _fallback(atribute_secundare)

    profile = _build_profile(data)
    secundare = []
    for item in data.get("secundare", []):
        if not isinstance(item, dict):
            continue
        stare = item.get("stare")
        if stare not in ("potrivit", "diferit", "nementionat"):
            stare = "nementionat"
        secundare.append(SecondaryAttributeResult(
            nume=item.get("nume", ""), stare=stare,
            valoare_gasita=item.get("valoare_gasita"),
        ))
    return CandidateExtraction(profile=profile, secundare=secundare)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_discovery_extractor.py -v`
Expected: PASS (4 teste).

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/extractor.py evaluare-anevar/tests/test_discovery_extractor.py
git commit -m "feat: extractor atribute LLM (injectabil, JSON validat, fallback)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Metodologia (pentru tabelul UI)

### Task 3: `metodologie()` în `scoring.py`

**Files:**
- Modify: `src/evaluare/discovery/scoring.py`
- Test: `tests/test_discovery_metodologie.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_discovery_metodologie.py`:
```python
from evaluare.discovery.scoring import metodologie


def test_metodologie_are_5_atribute_cu_formula_pondere_cota():
    m = metodologie()
    assert len(m) == 5
    an = m[0]
    assert an["atribut"] == "An"
    assert an["pondere"] == 5
    assert an["cota"] == "33%"
    assert "25" in an["formula"]
    # suma cotelor ~ 100%
    assert {r["atribut"] for r in m} == {"An", "Stare", "Finisaj", "Încălzire", "Teren"}
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_discovery_metodologie.py -v`
Expected: FAIL cu `ImportError: cannot import name 'metodologie'`.

- [ ] **Step 3: Adaugă `metodologie()` în `scoring.py`**

La finalul `src/evaluare/discovery/scoring.py`, adaugă:
```python
def metodologie() -> list[dict]:
    """Descrie metodologia de scoring pentru afișare (tabel UI, înainte de rezultate)."""
    total = sum(PONDERI.values())  # 15
    randuri = [
        ("An", "an", "min(|an_subiect − an_anunt| / 25, 1)"),
        ("Stare", "stare", "|treapta_subiect − treapta_anunt| / 4  (5 trepte)"),
        ("Finisaj", "finisaj", "|treapta_subiect − treapta_anunt| / 3  (4 trepte)"),
        ("Încălzire", "incalzire", "0 (aceeasi) / 0.5 (aceeasi familie) / 1 (diferita)"),
        ("Teren", "teren", "min(|teren_subiect − teren_anunt| / teren_subiect, 1)"),
    ]
    out = []
    for i, (eticheta, cheie, formula) in enumerate(randuri, start=1):
        p = PONDERI[cheie]
        out.append({
            "nr": i, "atribut": eticheta, "pondere": p,
            "cota": f"{round(100 * p / total)}%", "formula": formula,
        })
    return out
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_discovery_metodologie.py -v`
Expected: PASS (1 test). Verifică și că suita scoring rămâne verde:
`python -m pytest tests/test_discovery_scoring.py -q`.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/scoring.py evaluare-anevar/tests/test_discovery_metodologie.py
git commit -m "feat: metodologie() pentru tabelul de scoring din UI"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Orchestratorul

### Task 4: `discovery/orchestrator.py`

**Files:**
- Create: `src/evaluare/discovery/orchestrator.py`
- Test: `tests/test_discovery_orchestrator.py`

**Context de design:** `descopera(...)` leagă tot: caută anunțuri → pentru fiecare descarcă pagina →
parser (preț/suprafață) → extrage descrierea → LLM extrage atribute → scorează → asamblează
`CandidateResult` → rankează descrescător după relevanță. Fetcher + client injectabili.

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_discovery_orchestrator.py`:
```python
from decimal import Decimal
from pathlib import Path

from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.orchestrator import extrage_descriere, descopera

FIXTURES = Path(__file__).parent / "fixtures"


def test_extrage_descriere_include_text():
    html = "<html><head><title>Casa</title></head><body><p>Finisaje de lux, 4 camere.</p></body></html>"
    txt = extrage_descriere(html)
    assert "Finisaje de lux" in txt


def test_descopera_pipeline_complet():
    search_html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    listing_html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")

    def fetcher(url):
        if "/oferta/" in url:
            return listing_html
        return search_html

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},'
                    '"stare":{"treapta":4,"text":"renovat"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":400,"text":"400"},"secundare":[]}')

    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    rez = descopera("imobiliare", judet="ilfov", localitate="otopeni", subiect=subiect,
                    atribute_secundare=[], fetcher=fetcher, client=FakeClient(),
                    max_candidati=5)
    assert len(rez) == 3          # 3 anunturi /oferta/ in fixtura de cautare
    assert all(r.breakdown.relevanta > 0 for r in rez)
    # rankate descrescator
    relev = [r.breakdown.relevanta for r in rez]
    assert relev == sorted(relev, reverse=True)
    # pretul/suprafata extrase din pagina de anunt
    assert rez[0].pret == Decimal("249900")
    assert rez[0].suprafata == Decimal("130")
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_discovery_orchestrator.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează `orchestrator.py`**

`src/evaluare/discovery/orchestrator.py`:
```python
"""Orchestratorul descoperirii: search → scrape → parse → extract → score → rank."""
from __future__ import annotations

from typing import Callable, Optional

from bs4 import BeautifulSoup

from evaluare.ai.narrative import NarrativeClient
from evaluare.importers.url_parser import fetch_html, parse_listing_html
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.portal_search import cauta_anunturi
from evaluare.discovery.extractor import extrage_atribute
from evaluare.discovery.scoring import scor_candidat
from evaluare.discovery.results import CandidateResult


def extrage_descriere(html: str, max_caractere: int = 4000) -> str:
    """Extrage un text reprezentativ al anuntului (titlu + meta + corp), trunchiat."""
    soup = BeautifulSoup(html, "html.parser")
    parti: list[str] = []
    t = soup.find("title")
    if t and t.get_text():
        parti.append(t.get_text(strip=True))
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        parti.append(md["content"])
    parti.append(soup.get_text(" ", strip=True)[:max_caractere])
    return " ".join(parti)


def descopera(
    portal: str, judet: str, localitate: str, subiect: SubjectProfile,
    atribute_secundare: list, fetcher: Callable[[str], str] = fetch_html,
    client: Optional[NarrativeClient] = None, max_candidati: int = 8,
) -> list[CandidateResult]:
    """Pipeline complet de descoperire. Întoarce candidați rankați după relevanță."""
    urls = cauta_anunturi(portal, judet, localitate, fetcher=fetcher)[:max_candidati]
    rezultate: list[CandidateResult] = []
    for url in urls:
        try:
            html = fetcher(url)
        except Exception:
            continue
        parsed = parse_listing_html(html, sursa_url=url)
        descriere = extrage_descriere(html)
        extraction = extrage_atribute(descriere, atribute_secundare, client=client)
        breakdown = scor_candidat(subiect, extraction.profile)
        rezultate.append(CandidateResult(
            url=url, titlu=parsed.titlu, pret=parsed.pret, suprafata=parsed.suprafata,
            breakdown=breakdown, secundare=extraction.secundare,
        ))
    rezultate.sort(key=lambda r: r.breakdown.relevanta, reverse=True)
    return rezultate
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_discovery_orchestrator.py -v`
Expected: PASS (2 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/orchestrator.py evaluare-anevar/tests/test_discovery_orchestrator.py
git commit -m "feat: orchestrator descoperire (search->scrape->parse->extract->score->rank)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — Endpoint web + pagina UI

### Task 5: `POST /api/descopera`, `GET /descoperire`, `descoperire.html`

**Files:**
- Modify: `src/evaluare/web/app.py`
- Create: `src/evaluare/web/templates/descoperire.html`
- Test: `tests/test_web_descopera.py`

**Context de design:** endpoint-ul folosește `fetcher` și `client` deja injectate în `create_app`.
Întoarce `{metodologie, candidati}`. Pagina afișează tabelul de metodologie ÎNAINTE de candidați.

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_web_descopera.py`:
```python
from pathlib import Path

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.web.app import create_app

FIXTURES = Path(__file__).parent / "fixtures"


def _app(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    search_html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    listing_html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")

    def fetcher(url):
        return listing_html if "/oferta/" in url else search_html

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},'
                    '"stare":{"treapta":4,"text":"renovat"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":400,"text":"400"},"secundare":[]}')

    return create_app(storage=storage, client=FakeClient(), fetcher=fetcher)


def test_post_descopera_returns_metodologie_and_candidati(tmp_path):
    client = TestClient(_app(tmp_path))
    payload = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
               "subiect": {"an": 2013, "stare": 3, "finisaj": 4,
                           "incalzire": "centrala_gaz", "teren": "500"},
               "atribute_secundare": [], "max_candidati": 5}
    resp = client.post("/api/descopera", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["metodologie"]) == 5
    assert len(data["candidati"]) == 3
    c0 = data["candidati"][0]
    assert "relevanta" in c0 and "explicatie" in c0 and "pret" in c0


def test_descoperire_page_has_methodology_before_results(tmp_path):
    client = TestClient(_app(tmp_path))
    resp = client.get("/descoperire")
    assert resp.status_code == 200
    body = resp.text
    assert "Metodologie" in body
    assert 'id="metodologie"' in body
    assert 'id="rezultate"' in body
    # tabelul de metodologie apare ÎNAINTE de containerul de rezultate
    assert body.index('id="metodologie"') < body.index('id="rezultate"')
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_web_descopera.py -v`
Expected: FAIL (endpoint/rută inexistente).

- [ ] **Step 3a: Adaugă în `app.py` modelul de cerere, importurile și rutele**

În `src/evaluare/web/app.py`, adaugă importurile (lângă celelalte):
```python
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.orchestrator import descopera
from evaluare.discovery.scoring import metodologie
```
Adaugă modelul (la nivel de modul, lângă `ImportUrlRequest`):
```python
class DescoperaRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str
    subiect: SubjectProfile
    atribute_secundare: list[str] = []
    max_candidati: int = 8
```
Adaugă rutele în `create_app`, înainte de `return app`:
```python
    @app.post("/api/descopera")
    def descopera_endpoint(req: DescoperaRequest) -> dict:
        from evaluare.discovery.extractor import parse_atribute_secundare
        sec = parse_atribute_secundare("\n".join(req.atribute_secundare))
        rez = descopera(req.portal, req.judet, req.localitate, req.subiect, sec,
                        fetcher=fetcher, client=client, max_candidati=req.max_candidati)
        candidati = []
        for r in rez:
            candidati.append({
                "url": r.url, "titlu": r.titlu,
                "pret": str(r.pret) if r.pret is not None else None,
                "suprafata": str(r.suprafata) if r.suprafata is not None else None,
                "relevanta": r.breakdown.relevanta,
                "incredere_scazuta": r.breakdown.incredere_scazuta,
                "explicatie": r.breakdown.explicatie,
                "atribute": [a.model_dump() for a in r.breakdown.atribute],
                "secundare": [s.model_dump() for s in r.secundare],
            })
        return {"metodologie": metodologie(), "candidati": candidati}

    @app.get("/descoperire", response_class=HTMLResponse)
    def pagina_descoperire(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "descoperire.html", {})
```

- [ ] **Step 3b: Creează pagina `descoperire.html`**

`src/evaluare/web/templates/descoperire.html`:
```html
<!DOCTYPE html>
<html lang="ro">
<head><meta charset="utf-8"><title>Descoperire comparabile</title>
<style>
 body{font-family:Arial,sans-serif;max-width:1000px;margin:20px auto;line-height:1.5}
 table{border-collapse:collapse;margin:10px 0}
 th,td{border:1px solid #ccc;padding:4px 8px;font-size:0.9em}
 .candidat{border:1px solid #ddd;padding:10px;margin:10px 0}
 .hint{color:#666;font-size:0.85em}
 .alerta{color:#b30000}
</style></head>
<body>
<h1>Descoperire comparabile</h1>
<form id="f">
  Portal: <select name="portal"><option value="imobiliare">imobiliare.ro</option>
    <option value="storia">storia.ro</option></select>
  Judet: <input name="judet" value="ilfov"> Localitate: <input name="localitate" value="otopeni"><br>
  <b>Casa subiect:</b> An <input name="an" value="2013" size="5">
   Stare(1-5) <input name="stare" value="3" size="3">
   Finisaj(1-4) <input name="finisaj" value="4" size="3">
   Incalzire <input name="incalzire" value="centrala_gaz" size="14">
   Teren mp <input name="teren" value="500" size="6"><br>
  Atribute secundare (unul pe linie, „nume: valoare"):<br>
  <textarea name="secundare" rows="3" cols="40" placeholder="tamplarie: termopan"></textarea><br>
  <button type="submit">Caută comparabile</button>
</form>

<!-- Tabelul de metodologie: ÎNAINTE de rezultate -->
<div id="metodologie"></div>
<h2>Rezultate</h2>
<div id="rezultate"></div>

<script>
function randMetodologie(m){
  let h = '<h2>Metodologie scoring</h2><table><tr><th>#</th><th>Atribut</th>'
        + '<th>Pondere</th><th>Cota</th><th>Formula d</th></tr>';
  m.forEach(r => h += `<tr><td>${r.nr}</td><td>${r.atribut}</td><td>${r.pondere}</td>`
                    + `<td>${r.cota}</td><td><code>${r.formula}</code></td></tr>`);
  h += '</table><p class="hint">Relevanță = 100 × (1 − Σ(pondere×d)/Σ(ponderi cunoscute)); '
     + 'atributele „nementionat" sunt excluse.</p>';
  return h;
}
function randCandidat(c){
  let attr = '<table><tr><th>Atribut</th><th>Valoare găsită</th><th>d</th>'
           + '<th>pondere</th><th>contribuție</th></tr>';
  c.atribute.forEach(a => attr += `<tr><td>${a.nume}</td>`
     + `<td>${a.valoare_candidat ?? '➖ nementionat'}</td>`
     + `<td>${a.d ?? '—'}</td><td>${a.pondere}</td>`
     + `<td>${a.contributie ?? '(exclus)'}</td></tr>`);
  attr += '</table>';
  let sec = c.secundare.map(s => `${s.nume}: ${s.stare}`
     + (s.valoare_gasita ? ` („${s.valoare_gasita}")` : '')).join(' · ');
  let avert = c.incredere_scazuta ? '<span class="alerta"> (date insuficiente)</span>' : '';
  return `<div class="candidat">
    <label><input type="checkbox" class="bif" data-pret="${c.pret||''}" data-supr="${c.suprafata||''}">
      <b>Relevanță ${c.relevanta}%</b>${avert} — ${c.pret||'?'} / ${c.suprafata||'?'} mp</label><br>
    <a href="${c.url}" target="_blank">${c.titlu||c.url}</a>
    <p class="hint">${c.explicatie}</p>
    ${attr}
    ${sec ? '<p class="hint">Secundare: '+sec+'</p>' : ''}
  </div>`;
}
document.getElementById('f').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const d = Object.fromEntries(new FormData(e.target).entries());
  const payload = {portal:d.portal, judet:d.judet, localitate:d.localitate,
    subiect:{an:parseInt(d.an)||null, stare:parseInt(d.stare)||null,
      finisaj:parseInt(d.finisaj)||null, incalzire:d.incalzire||null, teren:d.teren||null},
    atribute_secundare:(d.secundare||'').split('\n').filter(Boolean), max_candidati:8};
  const r = await fetch('/api/descopera',{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const res = await r.json();
  document.getElementById('metodologie').innerHTML = randMetodologie(res.metodologie);
  document.getElementById('rezultate').innerHTML =
    res.candidati.map(randCandidat).join('')
    + '<button id="copiaza">Copiază comparabilele bifate (pret;suprafata)</button><pre id="out"></pre>';
  document.getElementById('copiaza').addEventListener('click', ()=>{
    const linii = [...document.querySelectorAll('.bif:checked')]
      .map(b => b.dataset.pret + ';' + b.dataset.supr);
    document.getElementById('out').textContent = linii.join('\n');
  });
});
</script>
</body></html>
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_web_descopera.py -v`
Expected: PASS (2 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/web/app.py evaluare-anevar/src/evaluare/web/templates/descoperire.html evaluare-anevar/tests/test_web_descopera.py
git commit -m "feat: endpoint /api/descopera + pagina UI (metodologie inainte de candidati)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 5 — Verificare finală

### Task 6: Suită completă + rebuild .exe

- [ ] **Step 1: Rulează toată suita**

Run: `python -m pytest -q`
Expected: toate testele trec (toate planurile).

- [ ] **Step 2: Reconstruiește executabilul cu noul modul**

Run (din `evaluare-anevar/`): `python -m PyInstaller --noconfirm --clean evaluare-anevar.spec`
Expected: `dist/evaluare-anevar.exe` reconstruit. (Asigură-te că niciun proces nu blochează exe-ul.)

- [ ] **Step 3: Commit final (dacă a rămas ceva)**
```bash
git status
git add -A && git commit -m "chore: rebuild exe cu modulul de descoperire complet" || echo "nimic de comis"
```

---

## Recapitulare acoperire

| Cerință | Task |
|---|---|
| Extracție atribute cu LLM (text→treaptă, din descriere reală) | Task 2 |
| Atribute secundare (3 stări + valoare găsită) | Task 1, 2 |
| Metodologia pentru tabelul UI | Task 3 |
| Orchestrator complet (search→scrape→parse→extract→score→rank) | Task 4 |
| Endpoint `POST /api/descopera` | Task 5 |
| Pagina UI: tabel metodologie ÎNAINTE de candidați + breakdown + bife | Task 5 |
| Integrare cu grila (copiere comparabile bifate → `pret;suprafata`) | Task 5 (buton „Copiază") |

**Integrarea cu calculul (spec 7.5):** candidații bifați produc linii `pret;suprafata` care se
lipesc în textarea „comparabile" din formularul de evaluare existent → grila de comparație. (O
integrare directă, fără copy-paste, e o îmbunătățire ulterioară de UX.)
