# Descoperire comparabile — nucleu (scoring + scraping) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Nucleul determinist și testabil al modulului de descoperire: modele de profil, **motorul de scoring care își produce singur explicația** (formula cu numere — înțeleasă fără a citi spec-ul), parserul de anunț întărit și scraper-ul de căutare pe portal.

**Architecture:** Pachet nou `evaluare.discovery`: `profiles.py` (datele subiectului + candidatului + breakdown-ul scorului), `scoring.py` (dissimilaritate ponderată, tratarea „nementionat", flag de încredere, **string de explicație auto-conținut**), `portal_search.py` (construiește URL de căutare + extrage URL-urile anunțurilor). Plus întărirea `importers/url_parser.py` (preț/suprafață din `__NEXT_DATA__`/og/titlu). Totul determinist, testat offline pe fixturi.

**Tech Stack:** Python 3.11+, Pydantic v2, beautifulsoup4, pytest. Fără dependențe noi.

**Spec sursă:** `docs/superpowers/specs/2026-05-31-descoperire-comparabile-design.md` (secțiunile 4 parser, 5.3 scoring). **Depinde de:** Planurile 1-4. Branch: `feature/nucleu-calcul`.

**Cerință cheie:** rezultatul scorului trebuie **înțeles fără spec** → motorul produce un câmp
`explicatie` cu formula exactă și numerele; UI-ul (plan ulterior) doar îl afișează.

**Rămâne pentru planul următor:** extracția atributelor cu LLM (din descrierea reală), orchestratorul
(search → scrape → parse → extract → score → rank), endpoint-ul web și pagina UI de descoperire.

---

## Structura de fișiere

```
evaluare-anevar/
├── src/evaluare/
│   ├── discovery/
│   │   ├── __init__.py             # NOU
│   │   ├── profiles.py             # NOU: SubjectProfile, CandidateProfile, breakdown
│   │   ├── scoring.py              # NOU: dissimilaritate + relevanta + explicatie
│   │   └── portal_search.py        # NOU: build URL cautare + extrage URL anunturi
│   └── importers/url_parser.py     # MODIFICAT: fallback __NEXT_DATA__/og/titlu
└── tests/
    ├── fixtures/
    │   ├── imobiliare_search.html  # NOU: pagina de cautare (linkuri /oferta/)
    │   └── imobiliare_listing_nextdata.html  # NOU: anunt cu __NEXT_DATA__/og/titlu
    ├── test_discovery_profiles.py  # NOU
    ├── test_discovery_scoring.py   # NOU (exemplul 86% din spec)
    ├── test_portal_search.py       # NOU
    └── test_url_parser_hardened.py # NOU
```

---

## Phase 1 — Modele de profil

### Task 1: `discovery/profiles.py`

**Files:**
- Create: `src/evaluare/discovery/__init__.py`  (empty)
- Create: `src/evaluare/discovery/profiles.py`
- Test: `tests/test_discovery_profiles.py`

- [ ] **Step 1: Scrie testul care eșuează**

`tests/test_discovery_profiles.py`:
```python
from decimal import Decimal

from evaluare.discovery.profiles import (
    SubjectProfile,
    CandidateProfile,
    AttributeBreakdown,
    ScoreBreakdown,
)


def test_subject_profile_optional_fields():
    s = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                       teren=Decimal("500"))
    assert s.an == 2013
    assert s.teren == Decimal("500")
    s2 = SubjectProfile()
    assert s2.an is None


def test_candidate_profile_holds_raw_texts():
    c = CandidateProfile(an=2008, stare=4, finisaj=4, incalzire="centrala_gaz",
                         teren=None, texte={"an": "2008", "stare": "renovat 2021"})
    assert c.an == 2008
    assert c.teren is None
    assert c.texte["stare"] == "renovat 2021"


def test_breakdown_structures():
    ab = AttributeBreakdown(nume="An", valoare_subiect="2013", valoare_candidat="2008",
                            d=0.2, pondere=5, contributie=1.0, cunoscut=True)
    assert ab.contributie == 1.0
    sb = ScoreBreakdown(relevanta=86, dissimilaritate=0.143, atribute=[ab],
                        atribute_cunoscute=4, incredere_scazuta=False,
                        explicatie="Relevanță 86% = ...")
    assert sb.relevanta == 86
    assert sb.atribute[0].nume == "An"
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_discovery_profiles.py -v`
Expected: FAIL cu `ModuleNotFoundError: No module named 'evaluare.discovery'`.

- [ ] **Step 3: Implementează modelele**

`src/evaluare/discovery/__init__.py` — empty file.

`src/evaluare/discovery/profiles.py`:
```python
"""Modele pentru descoperirea comparabilelor: profiluri si breakdown de scor."""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class SubjectProfile(BaseModel):
    """Atributele primare ale casei evaluate (normalizate pentru scoring)."""

    an: Optional[int] = None                # an constructie
    stare: Optional[int] = None             # treapta 1-5 (1=degradata .. 5=noua)
    finisaj: Optional[int] = None           # treapta 1-4 (1=modest .. 4=lux)
    incalzire: Optional[str] = None         # categorie normalizata (ex. "centrala_gaz")
    teren: Optional[Decimal] = None         # mp


class CandidateProfile(BaseModel):
    """Atributele primare extrase pentru un candidat + textul brut gasit (dovada)."""

    an: Optional[int] = None
    stare: Optional[int] = None
    finisaj: Optional[int] = None
    incalzire: Optional[str] = None
    teren: Optional[Decimal] = None
    texte: dict[str, str] = Field(default_factory=dict)   # ex {"an": "2008"}


class AttributeBreakdown(BaseModel):
    """Detalierea unui atribut in scor (pentru afisare auditabila)."""

    nume: str
    valoare_subiect: Optional[str] = None
    valoare_candidat: Optional[str] = None      # textul brut gasit in anunt
    d: Optional[float] = None                   # dissimilaritate [0,1]; None daca necunoscut
    pondere: int = 0
    contributie: Optional[float] = None         # pondere * d; None daca necunoscut
    cunoscut: bool = True


class ScoreBreakdown(BaseModel):
    """Rezultatul complet al scorarii unui candidat."""

    relevanta: int                              # 0-100
    dissimilaritate: float
    atribute: list[AttributeBreakdown]
    atribute_cunoscute: int
    incredere_scazuta: bool
    explicatie: str                             # formula exacta cu numere (auto-continuta)
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_discovery_profiles.py -v`
Expected: PASS (3 teste).

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/__init__.py evaluare-anevar/src/evaluare/discovery/profiles.py evaluare-anevar/tests/test_discovery_profiles.py
git commit -m "feat: modele profil descoperire (subiect, candidat, breakdown scor)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 2 — Motorul de scoring (cu explicație auto-conținută)

### Task 2: `discovery/scoring.py`

**Files:**
- Create: `src/evaluare/discovery/scoring.py`
- Test: `tests/test_discovery_scoring.py`

**Context de design:** reproduce exact secțiunea 5.3 din spec. Ponderi: an=5, stare=4, finisaj=3,
încălzire=2, teren=1. Atributele „nementionat" (None) se exclud din numitor. `≥3/5` lipsă →
`incredere_scazuta=True`. Câmpul `explicatie` conține formula EXACTĂ cu numerele, ca rezultatul să
fie înțeles **fără** spec.

- [ ] **Step 1: Scrie testul care eșuează (inclusiv exemplul 86% din spec)**

`tests/test_discovery_scoring.py`:
```python
from decimal import Decimal

from evaluare.discovery.profiles import SubjectProfile, CandidateProfile
from evaluare.discovery.scoring import (
    d_an, d_stare, d_finisaj, d_incalzire, d_teren, PONDERI, scor_candidat,
)


def test_d_an():
    assert d_an(2013, 2008) == 0.2
    assert d_an(2013, 2013) == 0.0
    assert d_an(2013, 1900) == 1.0      # cap la 1


def test_d_stare_si_finisaj():
    assert d_stare(3, 4) == 0.25        # |3-4|/4
    assert d_finisaj(2, 4) == round(2/3, 4)


def test_d_incalzire():
    assert d_incalzire("centrala_gaz", "centrala_gaz") == 0.0
    assert d_incalzire("centrala_gaz", "centrala_lemn") == 0.5   # aceeasi familie
    assert d_incalzire("centrala_gaz", "sobe") == 1.0


def test_d_teren():
    assert d_teren(Decimal("500"), Decimal("450")) == 0.1
    assert d_teren(Decimal("500"), Decimal("0")) == 1.0


def test_ponderi():
    assert PONDERI == {"an": 5, "stare": 4, "finisaj": 3, "incalzire": 2, "teren": 1}


def test_scor_candidat_exemplul_din_spec_86():
    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    candidat = CandidateProfile(an=2008, stare=4, finisaj=4, incalzire="centrala_gaz",
                                teren=None,
                                texte={"an": "2008", "stare": "renovat 2021",
                                       "finisaj": "lux", "incalzire": "centrala gaz"})
    b = scor_candidat(subiect, candidat)
    assert b.relevanta == 86
    assert b.atribute_cunoscute == 4
    assert b.incredere_scazuta is False
    # terenul (nementionat) e exclus
    teren = next(a for a in b.atribute if a.nume == "Teren")
    assert teren.cunoscut is False
    assert teren.contributie is None
    # explicatia contine formula cu numerele, inteligibila fara spec
    assert "86%" in b.explicatie
    assert "5×0.20" in b.explicatie or "5*0.20" in b.explicatie
    assert "(5+4+3+2)" in b.explicatie


def test_incredere_scazuta_cand_3_din_5_lipsesc():
    subiect = SubjectProfile(an=2013, stare=3, finisaj=4, incalzire="centrala_gaz",
                             teren=Decimal("500"))
    candidat = CandidateProfile(an=2008, stare=4)   # finisaj, incalzire, teren lipsesc
    b = scor_candidat(subiect, candidat)
    assert b.incredere_scazuta is True
    assert b.atribute_cunoscute == 2
```

- [ ] **Step 2: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_discovery_scoring.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 3: Implementează `scoring.py`**

`src/evaluare/discovery/scoring.py`:
```python
"""Scoringul de similaritate pentru descoperirea comparabilelor (vezi spec 5.3).

Produce un ScoreBreakdown cu un camp `explicatie` auto-continut (formula cu numere),
astfel incat rezultatul sa fie inteles fara a citi specificatia.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from evaluare.discovery.profiles import (
    SubjectProfile, CandidateProfile, AttributeBreakdown, ScoreBreakdown,
)

# Ponderi dupa prioritatea atributelor (spec 5.3). De calibrat ulterior.
PONDERI = {"an": 5, "stare": 4, "finisaj": 3, "incalzire": 2, "teren": 1}

PRAG_AN = 25                 # ani peste care diferenta e maxima
TREPTE_STARE = 4             # 5 trepte -> diferenta maxima 4
TREPTE_FINISAJ = 3           # 4 trepte -> diferenta maxima 3
PRAG_INCREDERE_LIPSA = 3     # >= 3 atribute lipsa -> incredere scazuta


def d_an(s: int, c: int) -> float:
    return min(abs(s - c) / PRAG_AN, 1.0)


def d_stare(s: int, c: int) -> float:
    return min(abs(s - c) / TREPTE_STARE, 1.0)


def d_finisaj(s: int, c: int) -> float:
    return round(min(abs(s - c) / TREPTE_FINISAJ, 1.0), 4)


def d_incalzire(s: str, c: str) -> float:
    if s == c:
        return 0.0
    # aceeasi familie (ex. "centrala_*") -> 0.5
    fam_s = s.split("_")[0] if s else ""
    fam_c = c.split("_")[0] if c else ""
    if fam_s and fam_s == fam_c:
        return 0.5
    return 1.0


def d_teren(s: Decimal, c: Decimal) -> float:
    if s == 0:
        return 1.0
    return min(float(abs(s - c) / s), 1.0)


def _d_pentru(nume: str, sv, cv) -> Optional[float]:
    """Calculeaza d pentru un atribut daca ambele valori sunt cunoscute."""
    if sv is None or cv is None:
        return None
    if nume == "an":
        return d_an(sv, cv)
    if nume == "stare":
        return d_stare(sv, cv)
    if nume == "finisaj":
        return d_finisaj(sv, cv)
    if nume == "incalzire":
        return d_incalzire(sv, cv)
    if nume == "teren":
        return d_teren(sv, cv)
    raise ValueError(f"Atribut necunoscut: {nume}")


_ETICHETE = {"an": "An", "stare": "Stare", "finisaj": "Finisaj",
             "incalzire": "Încălzire", "teren": "Teren"}


def scor_candidat(subiect: SubjectProfile, candidat: CandidateProfile) -> ScoreBreakdown:
    """Scoreaza un candidat fata de subiect; intoarce breakdown + explicatie."""
    atribute: list[AttributeBreakdown] = []
    suma_contributii = 0.0
    suma_ponderi = 0
    termeni_formula: list[str] = []          # ex. "5×0.20"
    ponderi_formula: list[str] = []          # ex. "5"
    necunoscute = 0

    for nume in ["an", "stare", "finisaj", "incalzire", "teren"]:
        sv = getattr(subiect, nume)
        cv = getattr(candidat, nume)
        pondere = PONDERI[nume]
        d = _d_pentru(nume, sv, cv)
        valoare_candidat = candidat.texte.get(nume) or (str(cv) if cv is not None else None)
        valoare_subiect = str(sv) if sv is not None else None
        if d is None:
            necunoscute += 1
            atribute.append(AttributeBreakdown(
                nume=_ETICHETE[nume], valoare_subiect=valoare_subiect,
                valoare_candidat=valoare_candidat, d=None, pondere=pondere,
                contributie=None, cunoscut=False,
            ))
            continue
        contributie = pondere * d
        suma_contributii += contributie
        suma_ponderi += pondere
        termeni_formula.append(f"{pondere}×{d:.2f}")
        ponderi_formula.append(str(pondere))
        atribute.append(AttributeBreakdown(
            nume=_ETICHETE[nume], valoare_subiect=valoare_subiect,
            valoare_candidat=valoare_candidat, d=round(d, 4), pondere=pondere,
            contributie=round(contributie, 4), cunoscut=True,
        ))

    if suma_ponderi == 0:
        dissim = 1.0
    else:
        dissim = suma_contributii / suma_ponderi
    relevanta = round(100 * (1 - dissim))
    cunoscute = 5 - necunoscute
    incredere_scazuta = necunoscute >= PRAG_INCREDERE_LIPSA

    numarator = " + ".join(termeni_formula) if termeni_formula else "0"
    numitor = "+".join(ponderi_formula) if ponderi_formula else "1"
    excluse = [_ETICHETE[n] for n in ["an", "stare", "finisaj", "incalzire", "teren"]
               if getattr(subiect, n) is None or getattr(candidat, n) is None]
    nota_excluse = (f" {', '.join(excluse)}: nementionat (exclus din calcul)."
                    if excluse else "")
    explicatie = (
        f"Relevanță {relevanta}% = 100 × (1 − ({numarator}) / ({numitor})) "
        f"= 100 × (1 − {dissim:.3f}).{nota_excluse}"
    )

    return ScoreBreakdown(
        relevanta=relevanta, dissimilaritate=round(dissim, 4), atribute=atribute,
        atribute_cunoscute=cunoscute, incredere_scazuta=incredere_scazuta,
        explicatie=explicatie,
    )
```

- [ ] **Step 4: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_discovery_scoring.py -v`
Expected: PASS (7 teste). Exemplul reproduce relevanța 86% și explicația cu formula.

- [ ] **Step 5: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/scoring.py evaluare-anevar/tests/test_discovery_scoring.py
git commit -m "feat: motor scoring descoperire (dissimilaritate ponderata + explicatie auto-continuta)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 3 — Parser întărit

### Task 3: extinde `importers/url_parser.py` cu fallback-uri

**Files:**
- Modify: `src/evaluare/importers/url_parser.py`
- Create: `tests/fixtures/imobiliare_listing_nextdata.html`
- Test: `tests/test_url_parser_hardened.py`

**Context de design:** parserul actual citește doar JSON-LD. Îl extindem cu fallback-uri, în ordine,
până găsește valoarea: (1) JSON-LD, (2) `__NEXT_DATA__` (JSON Next.js), (3) og:meta, (4) regex pe
titlu/text. NU modifica testele existente din `tests/test_url_parser.py` — funcția trebuie să rămână
compatibilă (fixturile vechi cu JSON-LD trec în continuare).

- [ ] **Step 1: Creează fixtura (anunț fără JSON-LD util, cu __NEXT_DATA__ + og + titlu)**

`tests/fixtures/imobiliare_listing_nextdata.html`:
```html
<!DOCTYPE html>
<html lang="ro"><head><meta charset="utf-8">
<title>Casă 130 mp cu 4 camere în Otopeni preț 249.900 EUR</title>
<meta property="og:title" content="Casă 4 camere Otopeni - 249.900 EUR">
<script id="__NEXT_DATA__" type="application/json">
{"props":{"pageProps":{"offer":{"price":{"value":249900,"currency":"EUR"},
 "characteristics":[{"key":"surface","value":"130"}]}}}}
</script>
</head><body><h1>Casă 4 camere</h1><p>Suprafață utilă 130 mp, finisaje moderne.</p></body></html>
```

- [ ] **Step 2: Scrie testul care eșuează**

`tests/test_url_parser_hardened.py`:
```python
from decimal import Decimal
from pathlib import Path

from evaluare.importers.url_parser import parse_listing_html

FIXTURES = Path(__file__).parent / "fixtures"


def test_extracts_from_nextdata_and_title():
    html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://imobiliare.ro/oferta/x")
    assert parsed.pret == Decimal("249900")
    assert parsed.moneda == "EUR"
    assert parsed.suprafata == Decimal("130")


def test_jsonld_still_works():
    # fixtura veche cu JSON-LD trebuie sa functioneze in continuare
    html = (FIXTURES / "imobiliare_listing.html").read_text(encoding="utf-8")
    parsed = parse_listing_html(html, sursa_url="https://imobiliare.ro/x")
    assert parsed.pret == Decimal("250000")
    assert parsed.suprafata == Decimal("180")


def test_title_regex_fallback_for_surface():
    html = "<html><head><title>Vila 220 mp Pipera 500000 EUR</title></head><body></body></html>"
    parsed = parse_listing_html(html)
    assert parsed.suprafata == Decimal("220")
    assert parsed.pret == Decimal("500000")
```

- [ ] **Step 3: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_url_parser_hardened.py -v`
Expected: FAIL (pret/suprafata None — parserul actual nu citește __NEXT_DATA__/titlu).

- [ ] **Step 4: Întărește parserul**

În `src/evaluare/importers/url_parser.py`, adaugă `import re` la importuri și înlocuiește funcția
`parse_listing_html` cu versiunea de mai jos (păstrează restul fișierului neschimbat):
```python
def _din_nextdata(soup) -> tuple:
    """Cauta pret si suprafata in blobul __NEXT_DATA__ (Next.js)."""
    import json as _json
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None, None, None
    try:
        data = _json.loads(tag.string)
    except (ValueError, TypeError):
        return None, None, None
    pret = moneda = supr = None
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "price" in node and isinstance(node["price"], dict):
                pret = pret or _to_decimal(node["price"].get("value"))
                moneda = moneda or node["price"].get("currency")
            if node.get("key") == "surface":
                supr = supr or _to_decimal(node.get("value"))
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return pret, moneda, supr


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata; incearca, in ordine: JSON-LD, __NEXT_DATA__,
    og:meta, regex pe titlu."""
    soup = BeautifulSoup(html, "html.parser")
    pret = moneda = suprafata = None

    # 1) JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        for node in _iter_nodes(data):
            offers = node.get("offers")
            if isinstance(offers, dict) and pret is None and "price" in offers:
                pret = _to_decimal(offers.get("price"))
                moneda = moneda or offers.get("priceCurrency")
            if pret is None and node.get("@type") == "Offer" and "price" in node:
                pret = _to_decimal(node.get("price"))
                moneda = moneda or node.get("priceCurrency")
            floor = node.get("floorSize")
            if suprafata is None and isinstance(floor, dict):
                suprafata = _to_decimal(floor.get("value"))

    # 2) __NEXT_DATA__
    if pret is None or suprafata is None:
        p2, m2, s2 = _din_nextdata(soup)
        pret = pret or p2
        moneda = moneda or m2
        suprafata = suprafata or s2

    titlu = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        titlu = title_tag.string.strip()

    # 3) og:meta + 4) regex pe titlu, pentru ce a ramas
    text_cautare = titlu
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        text_cautare += " " + og["content"]
    if suprafata is None:
        m = re.search(r"(\d+(?:[.,]\d+)?)\s*mp", text_cautare, re.IGNORECASE)
        if m:
            suprafata = _to_decimal(m.group(1))
    if pret is None:
        m = re.search(r"(\d[\d.\s]{3,})\s*(eur|euro|€|lei)", text_cautare, re.IGNORECASE)
        if m:
            pret = _to_decimal(m.group(1).replace(".", "").replace(" ", ""))
            moneda = moneda or m.group(2).upper().replace("EURO", "EUR").replace("€", "EUR")

    return ParsedListing(pret=pret, moneda=moneda, suprafata=suprafata,
                         titlu=titlu, sursa_url=sursa_url)
```

- [ ] **Step 5: Rulează testele (noi + vechi)**

Run: `python -m pytest tests/test_url_parser_hardened.py tests/test_url_parser.py -v`
Expected: PASS (toate — noile fallback-uri + cele 6 existente JSON-LD). Apoi suita completă
`python -m pytest -q` → toate verzi.

- [ ] **Step 6: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/importers/url_parser.py evaluare-anevar/tests/fixtures/imobiliare_listing_nextdata.html evaluare-anevar/tests/test_url_parser_hardened.py
git commit -m "feat: parser intarit (fallback __NEXT_DATA__ / og / regex titlu)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 4 — Scraper de căutare pe portal

### Task 4: `discovery/portal_search.py`

**Files:**
- Create: `src/evaluare/discovery/portal_search.py`
- Create: `tests/fixtures/imobiliare_search.html`
- Test: `tests/test_portal_search.py`

**Context de design:** construiește URL-ul de căutare pentru o zonă și extrage URL-urile anunțurilor
individuale (linkuri `/oferta/...`) dintr-o pagină de căutare. Fetcher injectabil (testare offline).

- [ ] **Step 1: Creează fixtura (pagină de căutare cu linkuri /oferta/)**

`tests/fixtures/imobiliare_search.html`:
```html
<!DOCTYPE html>
<html lang="ro"><head><title>Case Otopeni</title></head><body>
<a href="/oferta/casa-de-vanzare-otopeni-central-4-camere-275239748">Casa 1</a>
<a href="/oferta/duplex-de-vanzare-otopeni-odai-5-camere-272318001">Duplex</a>
<a href="https://www.imobiliare.ro/oferta/vila-otopeni-252237634">Vila</a>
<a href="/vanzare-case-vile/judetul-ilfov/otopeni?page=2">pagina 2</a>
<a href="/agentii">Agentii</a>
</body></html>
```

- [ ] **Step 2: Scrie testul care eșuează**

`tests/test_portal_search.py`:
```python
from pathlib import Path

from evaluare.discovery.portal_search import (
    build_search_url, extract_listing_urls, cauta_anunturi,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_build_search_url_imobiliare():
    url = build_search_url("imobiliare", judet="ilfov", localitate="otopeni")
    assert "imobiliare.ro" in url
    assert "ilfov" in url and "otopeni" in url


def test_extract_listing_urls_keeps_only_oferta_pages():
    html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    urls = extract_listing_urls(html, baza="https://www.imobiliare.ro")
    # doar cele 3 /oferta/, absolutizate, fara paginare/agentii
    assert len(urls) == 3
    assert all("/oferta/" in u for u in urls)
    assert all(u.startswith("https://www.imobiliare.ro/oferta/") for u in urls)


def test_cauta_anunturi_uses_injected_fetcher():
    html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    urls = cauta_anunturi("imobiliare", judet="ilfov", localitate="otopeni",
                          fetcher=lambda u: html)
    assert len(urls) == 3
```

- [ ] **Step 3: Rulează ca să confirmi eșecul**

Run: `python -m pytest tests/test_portal_search.py -v`
Expected: FAIL cu `ModuleNotFoundError`.

- [ ] **Step 4: Implementează `portal_search.py`**

`src/evaluare/discovery/portal_search.py`:
```python
"""Cautare anunturi pe portal: construieste URL de cautare + extrage URL-uri de anunt.

AVERTISMENT: scraping direct - poate incalca ToS si se poate strica la schimbari de layout.
"""
from __future__ import annotations

import re
from typing import Callable
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from evaluare.importers.url_parser import fetch_html

BAZE = {
    "imobiliare": "https://www.imobiliare.ro",
    "storia": "https://www.storia.ro",
}


def build_search_url(portal: str, judet: str, localitate: str) -> str:
    """Construieste URL-ul paginii de cautare pentru case+teren intr-o zona."""
    judet = judet.strip().lower()
    localitate = localitate.strip().lower()
    if portal == "imobiliare":
        return f"{BAZE['imobiliare']}/vanzare-case-vile/judetul-{judet}/{localitate}"
    if portal == "storia":
        return f"{BAZE['storia']}/ro/rezultate/vanzare/casa/{judet}/{localitate}"
    raise ValueError(f"Portal necunoscut: {portal}")


def extract_listing_urls(html: str, baza: str) -> list[str]:
    """Extrage URL-urile anunturilor individuale (linkuri /oferta/) dintr-o pagina de cautare."""
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    vazute = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"/oferta/", href):
            absolut = urljoin(baza + "/", href)
            if absolut not in vazute:
                vazute.add(absolut)
                urls.append(absolut)
    return urls


def cauta_anunturi(
    portal: str, judet: str, localitate: str,
    fetcher: Callable[[str], str] = fetch_html,
) -> list[str]:
    """Descarca pagina de cautare si intoarce URL-urile anunturilor. Fetcher injectabil."""
    url = build_search_url(portal, judet, localitate)
    html = fetcher(url)
    return extract_listing_urls(html, baza=BAZE[portal])
```

- [ ] **Step 5: Rulează ca să confirmi că trece**

Run: `python -m pytest tests/test_portal_search.py -v`
Expected: PASS (3 teste). Apoi suita completă `python -m pytest -q` → toate verzi.

- [ ] **Step 6: Commit (din repo root)**
```bash
git add evaluare-anevar/src/evaluare/discovery/portal_search.py evaluare-anevar/tests/fixtures/imobiliare_search.html evaluare-anevar/tests/test_portal_search.py
git commit -m "feat: scraper cautare portal (build URL + extrage URL-uri anunturi)"
```
Nu `--no-verify`. Dacă semnarea eșuează: `git -c commit.gpgsign=false commit ...`. Termină cu:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## Phase 5 — Verificare finală

### Task 5: Suită completă

- [ ] **Step 1: Rulează toată suita**

Run: `python -m pytest -q`
Expected: toate testele trec (planurile anterioare + nucleul de descoperire).

- [ ] **Step 2: Confirmă explicația auto-conținută**

Run: `python -m pytest tests/test_discovery_scoring.py::test_scor_candidat_exemplul_din_spec_86 -v`
Expected: PASS — relevanța 86% + explicația cu formula exactă (înțeleasă fără spec).

- [ ] **Step 3: Commit final (dacă a rămas ceva)**
```bash
git status
git add -A && git commit -m "test: verificare nucleu descoperire" || echo "nimic de comis"
```

---

## Recapitulare acoperire spec

| Cerință spec | Task |
|---|---|
| Atribute primare normalizate (subiect + candidat) | Task 1 |
| Scoring: dissimilaritate per atribut (formule 5.3) | Task 2 |
| Combinare ponderată + tratare „nementionat" + flag încredere | Task 2 |
| **Explicație auto-conținută (înțeleasă fără spec)** | Task 2 |
| Parser întărit (__NEXT_DATA__/og/titlu) | Task 3 |
| Scraper căutare portal (URL-uri anunțuri) | Task 4 |

**Rămâne (plan următor):**
- Extracția atributelor cu LLM (din descrierea reală → `CandidateProfile`, inclusiv maparea
  text→treaptă pentru stare/finisaj și categoria de încălzire).
- Orchestratorul complet (search → scrape → parse → extract → score → rank).
- Endpoint web `POST /api/descopera`.
- **Pagina UI de descoperire**, cu, în ordine: (1) **tabelul de metodologie** (spec 5.4) — fiecare
  atribut cu formula exactă, ponderea și cota — afișat O dată, ÎNAINTE de rezultate; (2) lista
  candidaților cu bife, fiecare cu relevanța, breakdown-ul per atribut și câmpul `explicatie`.
- **Integrarea cu modulul de calcul** (spec 7.5): candidații bifați → `to_comparable()` (existent)
  → lista `comparables` din formular/`EvaluationInput` → grila existentă. `SubjectProfile` se
  pre-completează din `BuildingData`/`LandData` deja introduse.
