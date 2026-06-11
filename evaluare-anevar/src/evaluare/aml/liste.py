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
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

from pydantic import BaseModel

_DATA_DIR = Path(__file__).parent / "data"
_PRAG_SIMILARITATE = 0.86
# Listele oficiale se reimprospateaza manual; peste acest prag le consideram potential expirate.
_ZILE_VALABILITATE_LISTE = 30
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


def avertisment_liste(liste: Liste, azi: str | None = None) -> str | None:
    """Semnaleaza cand listele de screening NU sunt utilizabile (evita un fals negativ tacut).

    `screening` consulta `sanctiuni` + `pep_functii`. Daca ambele sunt goale (ex.: `liste.json`
    lipseste -> `incarca_liste` intoarce liste goale) screening-ul da 0 potriviri *fara sa fi
    verificat nimic* — un evaluator poate crede ca „a verificat". La fel, liste fara data de
    actualizare ori mai vechi de ~30 de zile nu mai reflecta sursele oficiale. Returneaza None cand
    listele par utilizabile; altfel un mesaj orientativ (NU blocheaza fluxul — om-in-bucla).
    """
    if not liste.sanctiuni and not liste.pep_functii:
        return (
            "Liste de sancțiuni/PEP neîncărcate (goale) — screening neconcludent; reîmprospătați "
            "manual din sursele oficiale înainte de a vă baza pe rezultat."
        )
    if not liste.actualizat:
        return (
            "Listele de screening nu au dată de actualizare — vechime necunoscută; verificați "
            "reîmprospătarea din sursele oficiale."
        )
    if azi:
        try:
            zile = (date.fromisoformat(azi) - date.fromisoformat(liste.actualizat)).days
        except ValueError:
            return (
                "Data de actualizare a listelor de screening este invalidă — verificați "
                "reîmprospătarea din sursele oficiale."
            )
        if zile > _ZILE_VALABILITATE_LISTE:
            return (
                f"Liste de screening expirate (actualizate {liste.actualizat}, peste "
                f"{_ZILE_VALABILITATE_LISTE} de zile) — reîmprospătați din sursele oficiale; "
                "screening neconcludent."
            )
    return None
