"""Modele de date AML: KYC, beneficiar real, PEP, evaluare de risc, dosar.

Toate campurile optionale unde legea permite „de completat de evaluator". Datele sunt sensibile
(GDPR) — raman local; niciun apel AI pe ele.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from evaluare.aml.validare_data import verifica_an_plauzibil

TipAct = Literal["CI", "pasaport", "permis_sedere"]
TipClient = Literal["PF", "PJ", "PJ_straina"]
TipControlBR = Literal["proprietate", "alte_mijloace", "senior_management"]
CategorieRisc = Literal["redus", "standard", "sporit"]
NivelMasuri = Literal["simplificate", "standard", "suplimentare"]
# Categorii functii publice importante — Legea art. 3(2) a)-h)
CategoriePEP = Literal[
    "sef_stat_guvern", "parlamentar", "conducere_partid", "magistrat_suprem",
    "curte_conturi_banca_centrala", "ambasador_militar", "conducere_intreprindere_stat",
    "conducere_organizatie_internationala",
]
TipPEP = Literal["titular", "membru_familie", "asociat_apropiat"]


class PersoanaFizica(BaseModel):
    """Date de identificare PF — Legea art. 15(1)(a); Norme art. 18(1)(a)."""

    nume: str = ""
    prenume: str = ""
    cnp: str | None = None
    tip_act: TipAct | None = None
    serie_act: str | None = None
    nr_act: str | None = None
    cetatenie: str | None = None
    domiciliu: str | None = None
    ocupatie: str | None = None


class StatutPEP(BaseModel):
    """Statut de persoana expusa public — Legea art. 3."""

    este_pep: bool = False
    categorie: CategoriePEP | None = None
    tip: TipPEP | None = None
    data_incetare_functie: str | None = None   # ISO; pentru calculul celor 12 luni

    @field_validator("data_incetare_functie")
    @classmethod
    def _valideaza_data_incetare(cls, v: str | None) -> str | None:
        # None / '' -> None (PEP curent, fara data de incetare). Non-gol -> trebuie data ISO valida,
        # altfel ValueError -> 422 (prin _construieste), nu 500 cand pep_efectiv -> _luni_intre crapa.
        if not v:
            return None
        try:
            d = date.fromisoformat(v.strip())
        except (ValueError, TypeError) as e:
            raise ValueError("data_incetare_functie trebuie sa fie o data ISO yyyy-mm-dd.") from e
        verifica_an_plauzibil(d)
        return v


class BeneficiarReal(PersoanaFizica):
    """Beneficiar real — Legea art. 4. `procent` = cota de detinere/control."""

    procent: Decimal | None = None
    tip_control: TipControlBR | None = None
    pep: StatutPEP = Field(default_factory=StatutPEP)
    consultat_registru_central: bool = False
    neconcordanta_registru: bool = False


class ClientPF(BaseModel):
    """Client persoana fizica."""

    tip: Literal["PF"] = "PF"
    persoana: PersoanaFizica = Field(default_factory=PersoanaFizica)
    pep: StatutPEP = Field(default_factory=StatutPEP)


class ClientPJ(BaseModel):
    """Client persoana juridica (sau PJ straina) — Legea art. 15(1)(b),(2)."""

    tip: Literal["PJ", "PJ_straina"] = "PJ"
    denumire: str = ""
    cui: str | None = None
    sediu: str | None = None
    acte_constituire: str | None = None
    reprezentant_legal: PersoanaFizica = Field(default_factory=PersoanaFizica)
    imputernicit: PersoanaFizica | None = None
    document_imputernicire: str | None = None
    traducere_legalizata: bool = False              # obligatoriu daca PJ straina (art. 15(2))
    beneficiari_reali: list[BeneficiarReal] = Field(default_factory=list)


class FactorRisc(BaseModel):
    """Un factor de risc cu valoarea (1=redus,2=standard,3=sporit) si ponderea — Norme art. 13."""

    nume: Literal["client", "produs_serviciu", "canal", "geografic"]
    valoare: int = 2
    pondere: int = 1


class EvaluareRisc(BaseModel):
    """Rezultatul evaluarii de risc a relatiei — Norme art. 12-14."""

    factori: list[FactorRisc] = Field(default_factory=list)
    scor: Decimal = Decimal("0")
    categorie: CategorieRisc = "standard"
    nivel_masuri: NivelMasuri = "standard"
    motive_sporit: list[str] = Field(default_factory=list)
    data: str | None = None
    data_reevaluare: str | None = None


class DosarAML(BaseModel):
    """Dosarul AML al unei relatii de afaceri (separat de dosarul de evaluare)."""

    tip_entitate_evaluator: Literal["PJ", "PFA"] = "PFA"
    persoana_desemnata: str | None = None
    client_pf: ClientPF | None = None
    client_pj: ClientPJ | None = None
    evaluare_risc: EvaluareRisc | None = None
    indicatori_suspiciune: list[str] = Field(default_factory=list)
    data_creare: str | None = None
    data_retentie: str | None = None
