"""Loops de validare: blocheaza propagarea erorilor sau alerteaza evaluatorul."""
from __future__ import annotations

from decimal import Decimal
from statistics import median
from typing import Literal

from pydantic import BaseModel

from evaluare.models.property import BuildingData, LandData
from evaluare.models.comparable import Comparable
from evaluare.engine.market import pret_unitar_brut, ajustare_bruta

Nivel = Literal["blocheaza", "alerteaza"]

LIMITA_AJUSTARE_BRUTA = Decimal("0.25")
PRAG_OUTLIER = Decimal("0.50")   # deviatie relativa fata de mediana
MIN_COMPARABILE = 3


class Issue(BaseModel):
    """O problema de validare."""

    nivel: Nivel
    mesaj: str


def valideaza_proprietate(land: LandData, building: BuildingData) -> list[Issue]:
    """Valideaza datele fizice/cadastrale ale proprietatii."""
    issues: list[Issue] = []
    if land.suprafata <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Suprafata terenului trebuie sa fie > 0."))
    if building.au <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Aria utila (Au) trebuie sa fie > 0."))
    if building.acd <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Aria construita desfasurata (Acd) trebuie sa fie > 0."))
    if building.au > building.acd:
        issues.append(Issue(nivel="blocheaza", mesaj="Au nu poate depasi Acd."))
    return issues


def valideaza_comparabile(comparables: list[Comparable]) -> list[Issue]:
    """Valideaza numarul, outlierii si limitele de ajustare ale comparabilelor."""
    issues: list[Issue] = []
    if len(comparables) < MIN_COMPARABILE:
        issues.append(Issue(
            nivel="blocheaza",
            mesaj=f"Sunt necesare minimum {MIN_COMPARABILE} comparabile (gasite: {len(comparables)}).",
        ))
        return issues

    preturi = [pret_unitar_brut(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        for i, p in enumerate(preturi):
            deviatie = abs(p - med) / med
            if deviatie > PRAG_OUTLIER:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=f"Comparabilul {i} este outlier (deviatie {deviatie:.0%} fata de mediana).",
                ))

    for i, c in enumerate(comparables):
        if ajustare_bruta(c) > LIMITA_AJUSTARE_BRUTA:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=f"Comparabilul {i}: ajustare bruta {ajustare_bruta(c):.0%} depaseste limita de {LIMITA_AJUSTARE_BRUTA:.0%}.",
            ))
    return issues


def valideaza_depreciere(building: BuildingData) -> list[Issue]:
    """Cere justificare pentru deprecierea functionala/externa nenula."""
    issues: list[Issue] = []
    are_depreciere = (
        building.functional_depreciation > 0 or building.external_depreciation > 0
    )
    if are_depreciere and not building.justificare_depreciere.strip():
        issues.append(Issue(
            nivel="blocheaza",
            mesaj="Deprecierea functionala/externa nenula necesita justificare scrisa.",
        ))
    return issues


def valideaza_profil(profil) -> list[Issue]:
    """Avertismente de consistenta a profilului de evaluare."""
    issues: list[Issue] = []
    if not profil.abordari_aplicabile:
        issues.append(Issue(nivel="blocheaza",
                            mesaj="Profilul nu are nicio abordare aplicabila."))
    for cheie in profil.ponderi:
        if cheie not in profil.abordari_aplicabile:
            issues.append(Issue(nivel="alerteaza",
                                mesaj=f"Ponderea {cheie} nu corespunde unei abordari aplicabile."))
    return issues
