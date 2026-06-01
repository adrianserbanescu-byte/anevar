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
