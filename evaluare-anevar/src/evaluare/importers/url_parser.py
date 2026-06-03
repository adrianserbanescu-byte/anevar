"""Import comparabile dintr-un anunt online (scraping direct).

AVERTISMENT: scraping-ul direct poate incalca Termenii si Conditiile site-urilor
si se poate strica la schimbari de layout. Folosit pe raspunderea evaluatorului.
Parserul prefera datele structurate schema.org (stabile) si degradeaza gratios.
"""
from __future__ import annotations

import json
import re
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
    suprafata: Optional[Decimal] = None         # suprafata casei (construita/utila)
    suprafata_teren: Optional[Decimal] = None   # suprafata terenului, daca e in date structurate
    titlu: str = ""
    sursa_url: str = ""
    # caracteristici structurate (din __NEXT_DATA__ storia: target/characteristics)
    an: Optional[int] = None                    # anul constructiei
    incalzire: Optional[str] = None             # normalizat: centrala_gaz, sobe, ...
    material: Optional[str] = None              # lemn, caramida, beton, bca, ...
    tip_cladire: Optional[str] = None           # casa individuala / insiruita ...
    stare_text: Optional[str] = None            # stare normalizata (din construction_status)
    nr_camere: Optional[int] = None
    etaje: Optional[str] = None                 # ex. un nivel


def _to_decimal(value) -> Optional[Decimal]:
    """Pentru valori din date structurate (JSON-LD): '.' = zecimale (format international)."""
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def _to_decimal_ro(value) -> Optional[Decimal]:
    """Pentru numere din TEXT de afisare romanesc: '.' = separator de mii, ',' = zecimale.

    Ex.: '1.910' -> 1910 ; '351,46' -> 351.46.
    """
    if value is None:
        return None
    s = str(value).strip().replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
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


def _din_nextdata(soup) -> tuple:
    """Cauta pret si suprafata in blobul __NEXT_DATA__ (Next.js).

    Acopera structuri reale: imobiliare (key=="surface") si storia (caracteristica
    cu label=="area" -> suprafata casei; "terrain_area" e terenul, ignorat).
    """
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return None, None, None, None
    raw = tag.get_text()
    if not raw:
        return None, None, None, None
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return None, None, None, None
    pret = moneda = supr = teren = None
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "price" in node and isinstance(node["price"], dict):
                pret = pret or _to_decimal(node["price"].get("value"))
                moneda = moneda or node["price"].get("currency")
            # imobiliare: {key: "surface", value: "130"}; storia characteristics: {key: "m", value: "220"}
            if node.get("key") in ("surface", "m"):
                supr = supr or _to_decimal(node.get("value"))
            if node.get("key") == "terrain_area" and node.get("value") is not None:
                teren = teren or _to_decimal(node.get("value"))
            # storia: {label: "area", values: ["220"]} = casa; "terrain_area" = teren
            lbl = node.get("label")
            if lbl == "area" and isinstance(node.get("values"), list) and node["values"]:
                supr = supr or _to_decimal(node["values"][0])
            if lbl == "terrain_area" and isinstance(node.get("values"), list) and node["values"]:
                teren = teren or _to_decimal(node["values"][0])
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return pret, moneda, supr, teren


_HEATING = {"gas": "centrala_gaz", "urban": "termoficare", "electrical": "electrica",
            "tiles": "sobe", "stove": "sobe", "boiler": "centrala_proprie", "biomass": "biomasa"}
_MATERIAL = {"wood": "lemn", "brick": "caramida", "concrete": "beton", "bricks": "caramida",
             "cellular_concrete": "bca", "reinforced_concrete": "beton_armat"}
_TIP_CLADIRE = {"detached": "casa individuala", "semi_detached": "casa cuplata",
                "terraced": "casa insiruita", "house": "casa"}
_FLOORS = {"one_floor": "un nivel", "ground_floor": "parter", "two_floors": "doua niveluri",
           "three_floors": "trei niveluri"}
_STARE = {"ready_to_use": "buna / locuibila", "to_completion": "in curs de finalizare",
          "to_renovation": "necesita renovare"}


def _to_int(value) -> Optional[int]:
    try:
        return int(str(value).strip())
    except (ValueError, TypeError):
        return None


def _caracteristici_storia(soup) -> dict:
    """Extrage caracteristici structurate din __NEXT_DATA__ (storia: dict `target`).

    Acopera: anul constructiei, incalzire, material, tip cladire, stare, nr. camere, etaje.
    Returneaza un dict cu cheile gasite (normalizate in romana).
    """
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag:
        return {}
    raw = tag.get_text()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}

    def primul(v):
        return v[0] if isinstance(v, list) and v else v

    out: dict = {}
    stack = [data]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            # dict-ul `target` din storia contine cheile cu majuscula
            if "Build_year" in node and "an" not in out:
                an = _to_int(node.get("Build_year"))
                if an:
                    out["an"] = an
            if "Heating_types" in node and "incalzire" not in out:
                h = primul(node.get("Heating_types"))
                if h:
                    out["incalzire"] = _HEATING.get(str(h), str(h))
            if "Building_material" in node and "material" not in out:
                m = primul(node.get("Building_material"))
                if m:
                    out["material"] = _MATERIAL.get(str(m), str(m))
            if "Building_type" in node and "tip_cladire" not in out:
                t = primul(node.get("Building_type"))
                if t:
                    out["tip_cladire"] = _TIP_CLADIRE.get(str(t), str(t))
            if "Construction_status" in node and "stare_text" not in out:
                s = primul(node.get("Construction_status"))
                if s:
                    out["stare_text"] = _STARE.get(str(s), str(s))
            if "Rooms_num" in node and "nr_camere" not in out:
                c = _to_int(primul(node.get("Rooms_num")))
                if c:
                    out["nr_camere"] = c
            if "Floors_num" in node and "etaje" not in out:
                f = primul(node.get("Floors_num"))
                if f:
                    out["etaje"] = _FLOORS.get(str(f), str(f))
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return out


_STRUCTURA = {"beton armat": "beton_armat", "bca": "bca", "beton": "beton", "lemn": "lemn",
              "caramida": "caramida", "cărămidă": "caramida", "caramidă": "caramida",
              "zidarie": "zidarie", "zidărie": "zidarie", "metal": "metal",
              "prefabricate": "prefabricate", "sandwich": "panou_sandwich"}


def _caracteristici_imobiliare(body: str) -> dict:
    """Caracteristici structurate din corpul anuntului (imobiliare: perechi 'Eticheta: valoare').

    imobiliare e randat server-side: campurile apar ca text 'An constructie: 1996',
    'Structura rezistenta: BCA', 'Regim inaltime: D+P+M'. Tolerant la diacritice.
    """
    out: dict = {}
    m = re.search(r"An\s+construc[țt]ie\s*:?\s*(\d{4})", body, re.IGNORECASE)
    if m:
        an = _to_int(m.group(1))
        if an:
            out["an"] = an
    m = re.search(r"Structur[ăa]\s+rezisten[țt][ăa]\s*:?\s*([^|:\n]{2,40})", body, re.IGNORECASE)
    if m:
        s = m.group(1).strip().lower()
        for cheie, val in _STRUCTURA.items():
            if cheie in s:
                out["material"] = val
                break
    # regim inaltime: token fara spatii, ex. D+P+1E, P+2E+M, S+P+M
    m = re.search(r"Regim\s+[îi]n[ăa]l[țt]ime\s*:?\s*([SDP][A-Za-z0-9+]{1,16})", body, re.IGNORECASE)
    if m:
        out["etaje"] = m.group(1).strip()
    if re.search(r"central[ăa].{0,25}gaz|central[ăa]\s+termic", body, re.IGNORECASE):
        out["incalzire"] = "centrala_gaz"
    elif re.search(r"\bsobe\b", body, re.IGNORECASE):
        out["incalzire"] = "sobe"
    return out


def _cauta_in_jsonld(data) -> tuple:
    """Cautare recursiva in JSON-LD: pret (maximul = total), moneda, suprafata (floorSize).

    Robust la structuri reale: pretul poate fi sub Offer.priceSpecification.price, iar
    floorSize poate fi scalar (400) sau dict ({value: 400}).
    """
    preturi: list = []
    suprafete: list = []

    def walk(o):
        if isinstance(o, dict):
            if "price" in o:
                p = _to_decimal(o.get("price"))
                if p is not None and p > 0:
                    preturi.append((p, o.get("priceCurrency")))
            if "floorSize" in o:
                fs = o.get("floorSize")
                v = _to_decimal(fs.get("value")) if isinstance(fs, dict) else _to_decimal(fs)
                if v is not None and v > 0:
                    suprafete.append(v)
            for val in o.values():
                walk(val)
        elif isinstance(o, list):
            for val in o:
                walk(val)

    walk(data)
    pret = moneda = supr = None
    if preturi:
        pret, moneda = max(preturi, key=lambda x: x[0])   # totalul, nu pretul/mp
    if suprafete:
        supr = suprafete[0]                                # prima = cladirea (floorSize)
    return pret, moneda, supr


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata; incearca, in ordine: JSON-LD (recursiv),
    __NEXT_DATA__, og:meta + regex pe titlu/descriere."""
    soup = BeautifulSoup(html, "html.parser")
    pret: Optional[Decimal] = None
    moneda: Optional[str] = None
    suprafata: Optional[Decimal] = None
    suprafata_teren: Optional[Decimal] = None

    # 1) JSON-LD (recursiv, robust la nesting real: priceSpecification, floorSize scalar)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.get_text() or "")
        except (json.JSONDecodeError, TypeError, ValueError):
            continue
        p, m, s = _cauta_in_jsonld(data)
        pret = pret or p
        moneda = moneda or m
        suprafata = suprafata or s

    # 2) __NEXT_DATA__ (include suprafata terenului - storia)
    p2, m2, s2, t2 = _din_nextdata(soup)
    pret = pret or p2
    moneda = moneda or m2
    suprafata = suprafata or s2
    suprafata_teren = suprafata_teren or t2

    titlu = ""
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        titlu = title_tag.string.strip()

    # 3) og:meta (title + description) + regex, pentru ce a ramas
    text_cautare = titlu
    for prop in ("og:title", "og:description"):
        og = soup.find("meta", property=prop)
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

    body = soup.get_text(" ", strip=True)

    # 5) suprafata terenului din tabelul de caracteristici (imobiliare: "Sup. teren: 1.910 mp")
    if suprafata_teren is None:
        m = re.search(r"sup\w*\.?\s*teren\s*:?\s*([\d.,]+)\s*mp", body, re.IGNORECASE)
        if m:
            suprafata_teren = _to_decimal_ro(m.group(1))

    # 6) caracteristici structurate: storia (__NEXT_DATA__) cu prioritate, apoi imobiliare (body)
    car = _caracteristici_storia(soup)
    for cheie, val in _caracteristici_imobiliare(body).items():
        car.setdefault(cheie, val)

    return ParsedListing(pret=pret, moneda=moneda, suprafata=suprafata,
                         suprafata_teren=suprafata_teren, titlu=titlu, sursa_url=sursa_url,
                         an=car.get("an"), incalzire=car.get("incalzire"),
                         material=car.get("material"), tip_cladire=car.get("tip_cladire"),
                         stare_text=car.get("stare_text"), nr_camere=car.get("nr_camere"),
                         etaje=car.get("etaje"))


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
