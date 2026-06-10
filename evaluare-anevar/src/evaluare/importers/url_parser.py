"""Import comparabile dintr-un anunt online (scraping direct).

AVERTISMENT: scraping-ul direct poate incalca Termenii si Conditiile site-urilor
si se poate strica la schimbari de layout. Folosit pe raspunderea evaluatorului.
Parserul prefera datele structurate schema.org (stabile) si degradeaza gratios.
"""
from __future__ import annotations

import ipaddress
import json
import re
import socket
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin, urlparse

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

    pret: Decimal | None = None
    moneda: str | None = None
    suprafata: Decimal | None = None         # suprafata casei (construita/utila)
    suprafata_teren: Decimal | None = None   # suprafata terenului, daca e in date structurate
    titlu: str = ""
    sursa_url: str = ""
    # caracteristici structurate (din __NEXT_DATA__ storia: target/characteristics)
    an: int | None = None                    # anul constructiei
    incalzire: str | None = None             # normalizat: centrala_gaz, sobe, ...
    material: str | None = None              # lemn, caramida, beton, bca, ...
    tip_cladire: str | None = None           # casa individuala / insiruita ...
    stare_text: str | None = None            # stare normalizata (din construction_status)
    nr_camere: int | None = None
    etaje: str | None = None                 # ex. un nivel
    poza: str | None = None                  # URL imagine reprezentativa (og:image) - pt carduri UI
    pagina_lista: bool = False               # pagina pare listă/căutare, nu un anunț individual


def _to_decimal(value) -> Decimal | None:
    """Pentru valori din date structurate (JSON-LD): '.' = zecimale (format international)."""
    if value is None:
        return None
    try:
        return Decimal(str(value).replace(" ", "").replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


def _to_decimal_ro(value) -> Decimal | None:
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


def _to_int(value) -> int | None:
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


# Tipare de pagină de LISTĂ/căutare (NU anunț individual). Un URL trunchiat/expirat
# redirectează adesea la o pagină de rezultate, de unde s-ar extrage tăcut prețul unui
# anunț promovat nelegat de subiect — de evitat (evaluatorul ar primi un comparabil greșit).
_RE_PAGINA_LISTA = re.compile(
    r"vezi\s+[\d.\s]+\s*anun|"          # og:description „Vezi 84602 anunțuri…"
    r"anun[țţt]uri\s+de\s+v[âa]nzare|"   # „anunțuri de vânzare"
    r"rezultate(le)?\s+(ale\s+)?c[ăa]ut[ăa]rii|"
    r"(apartamente|case|terenuri|garsoniere|vile|imobile)\s+de\s+v[âa]nzare\s*\|",
    re.IGNORECASE)


def _pare_pagina_lista(text: str) -> bool:
    """True dacă titlul/descrierea arată a pagină de listă/căutare, nu anunț individual."""
    return bool(_RE_PAGINA_LISTA.search(text or ""))


def parse_listing_html(html: str, sursa_url: str = "") -> ParsedListing:
    """Extrage pret, moneda si suprafata; incearca, in ordine: JSON-LD (recursiv),
    __NEXT_DATA__, og:meta + regex pe titlu/descriere."""
    soup = BeautifulSoup(html, "html.parser")
    pret: Decimal | None = None
    moneda: str | None = None
    suprafata: Decimal | None = None
    suprafata_teren: Decimal | None = None

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
            text_cautare += " " + str(og["content"])
    # imagine reprezentativa pt carduri (og:image, fallback twitter:image)
    poza = None
    for cheie, val in (("property", "og:image"), ("name", "twitter:image")):
        tag = soup.find("meta", attrs={cheie: val})
        if tag and tag.get("content"):
            poza = str(tag["content"]).strip() or None
            if poza:
                break
    if suprafata is None:
        # „N mp" e suprafața TERENULUI dacă „teren" e eticheta dinainte („teren: 2000 mp")
        # sau urmează imediat după unitate („2000mp Teren") — NU o confunda cu suprafața casei
        # (ex. OLX „Casă cu 2000mp Teren"). Atenție: fereastra „după" e mică, ca să nu prindă
        # eticheta câmpului următor („120 mp  Suprafață teren: 300").
        for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*mp\b", text_cautare, re.IGNORECASE):
            inainte = text_cautare[max(0, m.start() - 12):m.start()].lower()
            dupa = text_cautare[m.end():m.end() + 8].lower()
            e_teren = "teren" in inainte or re.match(r"\s*\.?\s*teren", dupa)
            if e_teren:
                if suprafata_teren is None:
                    suprafata_teren = _to_decimal(m.group(1))
                continue
            suprafata = _to_decimal(m.group(1))
            break
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
                         etaje=car.get("etaje"), poza=poza,
                         pagina_lista=_pare_pagina_lista(text_cautare))


def to_comparable(parsed: ParsedListing) -> Comparable:
    """Construieste un Comparable dintr-un ParsedListing (cere pret + suprafata)."""
    if parsed.pagina_lista:
        raise ValueError(
            "URL-ul pare o pagină de listă/căutare, nu un anunt individual; "
            "verifica linkul (valoarea ar fi a unui anunt nelegat)."
        )
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


def _url_public_sigur(url: str) -> bool:
    """Anti-SSRF: True doar pentru http(s) către un host care rezolvă la IP PUBLIC.
    Blochează loopback/privat/link-local (127.0.0.1, 10/8, 192.168, 169.254.169.254 etc.)."""
    try:
        p = urlparse(url)
    except ValueError:
        return False
    if p.scheme not in ("http", "https") or not p.hostname:
        return False
    try:
        infos = socket.getaddrinfo(p.hostname, p.port or (443 if p.scheme == "https" else 80))
    except OSError:
        return False
    for *_, sockaddr in infos:
        ip = ipaddress.ip_address(sockaddr[0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
                or ip.is_multicast or ip.is_unspecified):
            return False
    return True


_MAX_REDIRECTURI = 5


def fetch_html(url: str) -> str:
    """Descarca HTML-ul unui anunt (live). Nu se foloseste in teste.

    Urmareste redirecturile MANUAL, re-validand FIECARE hop cu `_url_public_sigur` (anti-SSRF):
    `allow_redirects=True` ar urma un 302 de la un URL public catre o adresa INTERNA (127.0.0.1 /
    169.254.169.254 metadata / retea privata) fara re-verificare -> bypass clasic al gardei. (Audit motor.)
    """
    for _ in range(_MAX_REDIRECTURI + 1):
        if not _url_public_sigur(url):
            raise ValueError(
                "URL respins: sunt permise doar adrese web publice http(s) (protecție anti-SSRF)."
            )
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15, allow_redirects=False)
        if resp.is_redirect and resp.headers.get("Location"):   # re-valideaza tinta la urmatoarea iteratie
            url = urljoin(url, resp.headers["Location"])
            continue
        resp.raise_for_status()
        return resp.text
    raise ValueError("Prea multe redirecturi — anuntul nu a putut fi descarcat in siguranta.")


def import_from_url(
    url: str, fetcher: Callable[[str], str] = fetch_html
) -> ParsedListing:
    """Descarca si parseaza un anunt. Fetcher injectabil pentru testare offline."""
    html = fetcher(url)
    return parse_listing_html(html, sursa_url=url)
