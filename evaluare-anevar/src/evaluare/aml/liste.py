"""Liste externe injectabile pentru screening AML (sanctiuni / PEP-functii / tari).

Datele sunt liste OFICIALE care se reimprospateaza manual din surse externe (UE/ONU sanctiuni,
ANI pentru functii PEP, ONPCSB tari necooperante, CE tari terte cu risc inalt). Modulul nu face
apeluri automate — incarca din fisiere locale JSON sau din liste injectate, deci functioneaza
offline si e testabil. Screening tolerant (fara diacritice + similaritate) => „posibila potrivire,
verifica manual" (niciodata o decizie automata).
"""
from __future__ import annotations

import json
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from pydantic import BaseModel

_DATA_DIR = Path(__file__).parent / "data"
_PRAG_SIMILARITATE = 0.86
# Plafon defensiv pentru intrarile comparate cu SequenceMatcher (O(n*m)): nume reale sunt scurte,
# dar `screening` poate primi un `nume` arbitrar (nu doar din modele marginite) -> trunchiem ca sa
# nu transformam o comparare intr-un DoS de CPU (~10s la 500K caractere).
_MAX_LEN_COMPARARE = 256


class Potrivire(BaseModel):
    """O posibila potrivire la screening — necesita verificare umana."""

    lista: str
    intrare: str
    scor: float
    nota: str = "Posibilă potrivire — verificați manual sursa oficială."


class Liste(BaseModel):
    """Containerul de liste, cu data de actualizare. Reimprospatare manuala din surse oficiale."""

    actualizat: str | None = None
    sanctiuni: list[str] = []
    pep_functii: list[str] = []
    tari_risc_inalt: list[str] = []
    tari_necooperante: list[str] = []


def _norm(s: str) -> str:
    """Lowercase fara diacritice, spatii normalizate."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(s.lower().split())


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(
        None, _norm(a)[:_MAX_LEN_COMPARARE], _norm(b)[:_MAX_LEN_COMPARARE]
    ).ratio()


def incarca_liste(dir_date: Path | None = None) -> Liste:
    """Incarca listele din `<dir>/liste.json`; daca lipseste, returneaza liste goale."""
    dir_date = dir_date or _DATA_DIR
    cale = Path(dir_date) / "liste.json"
    if not cale.exists():
        return Liste()
    return Liste(**json.loads(cale.read_text(encoding="utf-8")))


def screening(nume: str, liste: Liste, prag: float = _PRAG_SIMILARITATE) -> list[Potrivire]:
    """Cauta `nume` in listele de sanctiuni si PEP (tolerant). Returneaza posibile potriviri."""
    rez: list[Potrivire] = []
    if not nume or not nume.strip():
        return rez
    for eticheta, intrari in (("sancțiuni", liste.sanctiuni), ("PEP", liste.pep_functii)):
        for intrare in intrari:
            scor = _similar(nume, intrare)
            if scor >= prag:
                rez.append(Potrivire(lista=eticheta, intrare=intrare, scor=round(scor, 3)))
    rez.sort(key=lambda p: p.scor, reverse=True)
    return rez


def este_tara_risc(tara: str, liste: Liste) -> dict:
    """Verifica daca tara apare pe listele de risc inalt / necooperante (potrivire toleranta)."""
    def _pe_lista(intrari: list[str]) -> bool:
        return any(_similar(tara, x) >= _PRAG_SIMILARITATE for x in intrari)

    return {
        "risc_inalt": _pe_lista(liste.tari_risc_inalt),
        "necooperanta": _pe_lista(liste.tari_necooperante),
    }
