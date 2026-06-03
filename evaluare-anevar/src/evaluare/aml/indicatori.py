"""Indicatori de suspiciune specifici evaluarii (HCD 58/2023 art. 6(10)).

Orice indicator activ = motiv de analiza si, dupa caz, propunere de RTS (raport tranzactie
suspecta) catre persoana responsabila / ONPCSB (Legea art. 6; HCD 58 art. 7).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Indicator(BaseModel):
    cheie: str
    text: str
    temei: str = "HCD 58/2023 art. 6(10)"


# Cei 10 indicatori, in ordinea din HCD 58 art. 6(10).
INDICATORI: list[Indicator] = [
    Indicator(cheie="graba_excesiva",
              text="Comportament suspect: grabă excesivă a clientului."),
    Indicator(cheie="presiune_documente_insuficiente",
              text="Presiuni pentru întocmirea raportului fără documente suficiente."),
    Indicator(cheie="nemultumire_nejustificata",
              text="Nemulțumire nejustificată a clientului."),
    Indicator(cheie="presiune_valoare_predeterminata",
              text="Presiuni pentru obținerea unei anumite valori și/sau opinii."),
    Indicator(cheie="scop_nedefinit",
              text="Nedefinirea scopului concret al evaluării."),
    Indicator(cheie="pep_implicat",
              text="Persoane expuse public (PEP) implicate în operațiunile juridice legate de evaluare."),
    Indicator(cheie="istoric_atipic_tranzactionare",
              text="Istoric atipic de mare al tranzacționării bunului într-o perioadă scurtă."),
    Indicator(cheie="tranzactii_in_dezacord_cu_piata",
              text="Tranzacții anterioare (vânzări/închirieri) în total dezacord cu piața, nejustificate."),
    Indicator(cheie="drepturi_litigioase",
              text="Existența unor drepturi litigioase în legătură cu activul evaluat."),
    Indicator(cheie="antecedente_penale",
              text="Antecedente penale ale persoanelor implicate."),
]

_CHEI = [i.cheie for i in INDICATORI]


class SemnaleIndicatori(BaseModel):
    """Bifele evaluatorului pentru cei 10 indicatori (implicit toate False)."""

    graba_excesiva: bool = False
    presiune_documente_insuficiente: bool = False
    nemultumire_nejustificata: bool = False
    presiune_valoare_predeterminata: bool = False
    scop_nedefinit: bool = False
    pep_implicat: bool = False
    istoric_atipic_tranzactionare: bool = False
    tranzactii_in_dezacord_cu_piata: bool = False
    drepturi_litigioase: bool = False
    antecedente_penale: bool = False
    # observatii libere ale evaluatorului
    observatii: str = ""

    model_config = {"extra": "forbid"}


def evalueaza_indicatori(semnale: SemnaleIndicatori) -> list[Indicator]:
    """Returneaza indicatorii activi (bifati), in ordinea din catalog."""
    activi = {c for c in _CHEI if getattr(semnale, c)}
    return [i for i in INDICATORI if i.cheie in activi]


def propune_rts(semnale: SemnaleIndicatori) -> bool:
    """Daca exista cel putin un indicator activ => se propune analiza/RTS (HCD 58 art. 7)."""
    return any(getattr(semnale, c) for c in _CHEI)
