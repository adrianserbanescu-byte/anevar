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
Ghid = Literal["GEV_520", "GEV_630", "GEV_500", "SEV_450", "none"]


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

INDUSTRIAL = ProfilEvaluare(
    tip_activ="industrial", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["cost", "venit", "comparatie"], ghid="GEV_630",
)

AGRICOL = ProfilEvaluare(
    tip_activ="agricol", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["comparatie"], ghid="GEV_630",
)

RAPORTARE_FINANCIARA = ProfilEvaluare(
    tip_activ="comercial", scop="raportare_financiara", tip_valoare="justa",
    abordari_aplicabile=["venit", "comparatie", "cost"], ghid="GEV_500",
)
ASIGURARE = ProfilEvaluare(
    # SEV 450 (ed. 2025) = standardul specific evaluarii costurilor in scop de asigurare. Valoarea de
    # asigurare = costul de RECONSTRUCTIE (cost de inlocuire BRUT, NEdeprecat), nu cost net (GEV 630).
    tip_activ="casa", scop="asigurare", tip_valoare="asigurare",
    abordari_aplicabile=["cost"], ghid="SEV_450",
)
IMPOZITARE = ProfilEvaluare(
    tip_activ="casa", scop="impozitare", tip_valoare="piata",
    abordari_aplicabile=["comparatie", "cost"], ghid="GEV_630",
)
LITIGII = ProfilEvaluare(
    tip_activ="casa", scop="litigii", tip_valoare="piata",
    abordari_aplicabile=["comparatie", "cost"], ghid="GEV_630",
)

SPECIAL = ProfilEvaluare(
    tip_activ="special", scop="garantare_credit", tip_valoare="piata",
    abordari_aplicabile=["venit", "comparatie", "cost"], ghid="GEV_630",
)


class SectiuniTip(BaseModel):
    """Ce sectiuni de raport sunt UNICE / aplicabile pentru un tip de imobil (structura livrabilului).

    Sursa: docs/SEV-2025-cerinte-per-tip-imobil.md (matricea „ce e UNIC per tip"). Decuplam STRUCTURA
    raportului (ce sectiuni apar) de DATELE prezente: un raport de teren nu trebuie sa contina sectiunea
    de constructie chiar daca, accidental, ar exista elemente de cost in input. Flag-urile aici sunt
    ADITIVE — `True` = comportamentul implicit (se randeaza daca exista date); `False` = se omite
    explicit pentru tipul respectiv.
    """

    # Sectiunile de constructie (tabel cost de inlocuire + linia descriptiva a constructiei).
    # False pentru teren liber / agricol (nu exista constructie de evaluat).
    constructie: bool = True
    # Grila de teren STANDALONE + alocarea valorii teren/constructie. False pentru apartament
    # (terenul = cota indiviza netranzacționabila, NU se aloca separat — GEV 630 §118.a).
    teren_standalone: bool = True
    # Nota „cota parte indiviza din teren" in locul terenului in proprietate exclusiva (apartament).
    nota_cota_indiviza: bool = False
    # Venitul ca abordare PRINCIPALA (comercial / generator de venit) — marcaj proeminent in raport.
    venit_principal: bool = False
    # Permite tabelul de cost (abordarea prin cost). False = se omite explicit pentru tipul respectiv
    # (ex. comercial — costul de regula NU se aplica, GEV 232 §11). True = comportamentul actual
    # (se randeaza data-driven, daca exista elemente de cost). NB: distinct de `constructie`, care
    # acopera si linia descriptiva a constructiei la teren/agricol.
    abordare_cost: bool = True


# Maparea tip de imobil -> structura sectiunilor de raport. Tipurile neenumerate (sau profilul
# implicit/necunoscut) cad pe `SectiuniTip()` = comportamentul actual (toate sectiunile, data-driven).
SECTIUNI_PER_TIP: dict[str, SectiuniTip] = {
    # Casa: piata + cost (construcție + teren). Toate sectiunile — comportamentul actual.
    "casa": SectiuniTip(),
    # Apartament: piata principala; FARA teren standalone (cota indiviza), cu nota explicativa.
    "apartament": SectiuniTip(teren_standalone=False, nota_cota_indiviza=True),
    # Teren liber: doar analiza terenului; FARA constructie / cost de inlocuire constructie.
    "teren": SectiuniTip(constructie=False),
    # Agricol: comparatie pe teren; FARA constructie.
    "agricol": SectiuniTip(constructie=False),
    # Comercial: venit = abordarea PRINCIPALA (proeminenta in raport); costul de regula NU se aplica.
    "comercial": SectiuniTip(venit_principal=True, abordare_cost=False),
    # Industrial / special: toate sectiunile (piata/cost/venit dupa caz) — comportamentul actual.
    "industrial": SectiuniTip(),
    "special": SectiuniTip(),
}


def sectiuni_pentru_tip(tip: str | None) -> SectiuniTip:
    """Structura de sectiuni pentru un tip de imobil. Tip necunoscut/absent -> implicit (toate)."""
    return SECTIUNI_PER_TIP.get(tip or "", SectiuniTip())
