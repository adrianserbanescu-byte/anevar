"""Loops de validare: blocheaza propagarea erorilor sau alerteaza evaluatorul."""
from __future__ import annotations

from decimal import Decimal
from statistics import median
from typing import Literal

from pydantic import BaseModel

from evaluare.engine.market import ajustare_bruta, pret_unitar_brut
from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.comparable import Comparable
from evaluare.models.property import BuildingData, LandData

Nivel = Literal["blocheaza", "alerteaza"]

# Praguri default (alias la config) — valorile efective vin din MetodologieConfig (M5, configurabil).
LIMITA_AJUSTARE_BRUTA = IMPLICIT.limita_ajustare_bruta
PRAG_OUTLIER = IMPLICIT.prag_outlier   # deviatie relativa fata de mediana
MIN_COMPARABILE = IMPLICIT.min_comparabile


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
    if (building.etaj is not None and building.nr_niveluri_bloc is not None
            and building.etaj > building.nr_niveluri_bloc):
        issues.append(Issue(nivel="blocheaza",
                            mesaj="Etajul nu poate depasi numarul de niveluri ale blocului."))
    return issues


def valideaza_comparabile(comparables: list[Comparable],
                          cfg: MetodologieConfig = IMPLICIT) -> list[Issue]:
    """Valideaza numarul, outlierii si limitele de ajustare ale comparabilelor (praguri din config — M5)."""
    issues: list[Issue] = []
    if len(comparables) < cfg.min_comparabile:
        issues.append(Issue(
            nivel="blocheaza",
            mesaj=f"Sunt necesare minimum {cfg.min_comparabile} comparabile (gasite: {len(comparables)}).",
        ))
        return issues

    preturi = [pret_unitar_brut(c) for c in comparables]
    med = Decimal(str(median([float(p) for p in preturi])))
    if med > 0:
        for i, p in enumerate(preturi):
            deviatie = abs(p - med) / med
            if deviatie > cfg.prag_outlier:
                issues.append(Issue(
                    nivel="alerteaza",
                    mesaj=f"Comparabilul {i} este outlier (deviatie {deviatie:.0%} fata de mediana).",
                ))

    for i, c in enumerate(comparables):
        g = ajustare_bruta(c)
        if g > cfg.limita_ajustare_bruta:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=f"Comparabilul {i}: ajustare bruta {g:.0%} depaseste limita de {cfg.limita_ajustare_bruta:.0%}.",
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
