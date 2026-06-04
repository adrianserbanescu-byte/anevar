"""ProfilEvaluare — sursa de adevăr a unei evaluări (tip activ, scop, tip valoare, abordări, ghid)."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

TipActiv = Literal["casa", "teren", "apartament", "comercial", "industrial", "agricol", "special"]
Scop = Literal["garantare_credit", "raportare_financiara", "asigurare", "impozitare",
               "vanzare", "litigii", "expropriere", "aport"]
TipValoare = Literal["piata", "investitie", "justa", "lichidare", "asigurare", "chirie"]
Abordare = Literal["cost", "comparatie", "venit"]
Ghid = Literal["GEV_520", "GEV_630", "GEV_500", "none"]


class ProfilEvaluare(BaseModel):
    """Configurarea unei evaluări: ce tip, în ce scop, ce valoare, ce abordări, ce ghid."""

    tip_activ: TipActiv = "casa"
    scop: Scop = "garantare_credit"
    tip_valoare: TipValoare = "piata"
    abordari_aplicabile: list[Abordare] = Field(default_factory=lambda: ["cost", "comparatie"])
    ponderi: dict[str, Decimal] = Field(default_factory=dict)
    ghid: Ghid = "GEV_520"


# Profil predefinit = comportamentul actual al aplicației.
CASA_TEREN_GARANTARE = ProfilEvaluare(
    tip_activ="casa", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["cost", "comparatie"], ghid="GEV_520",
)

APARTAMENT_GARANTARE = ProfilEvaluare(
    tip_activ="apartament", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["comparatie", "cost"], ghid="GEV_520",
)

COMERCIAL_INCHIRIAT = ProfilEvaluare(
    tip_activ="comercial", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["venit", "comparatie"], ghid="GEV_630",
)
