"""Modele de date AML: KYC, beneficiar real, PEP, evaluare de risc, dosar.

Toate campurile optionale unde legea permite „de completat de evaluator". Datele sunt sensibile
(GDPR) — raman local; niciun apel AI pe ele.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

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
    cnp: Optional[str] = None
    tip_act: Optional[TipAct] = None
    serie_act: Optional[str] = None
    nr_act: Optional[str] = None
    cetatenie: Optional[str] = None
    domiciliu: Optional[str] = None
    ocupatie: Optional[str] = None


class StatutPEP(BaseModel):
    """Statut de persoana expusa public — Legea art. 3."""

    este_pep: bool = False
    categorie: Optional[CategoriePEP] = None
    tip: Optional[TipPEP] = None
    data_incetare_functie: Optional[str] = None   # ISO; pentru calculul celor 12 luni


class BeneficiarReal(PersoanaFizica):
    """Beneficiar real — Legea art. 4. `procent` = cota de detinere/control."""

    procent: Optional[Decimal] = None
    tip_control: Optional[TipControlBR] = None
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
    cui: Optional[str] = None
    sediu: Optional[str] = None
    acte_constituire: Optional[str] = None
    reprezentant_legal: PersoanaFizica = Field(default_factory=PersoanaFizica)
    imputernicit: Optional[PersoanaFizica] = None
    document_imputernicire: Optional[str] = None
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
    data: Optional[str] = None
    data_reevaluare: Optional[str] = None


class DosarAML(BaseModel):
    """Dosarul AML al unei relatii de afaceri (separat de dosarul de evaluare)."""

    tip_entitate_evaluator: Literal["PJ", "PFA"] = "PFA"
    persoana_desemnata: Optional[str] = None
    client_pf: Optional[ClientPF] = None
    client_pj: Optional[ClientPJ] = None
    evaluare_risc: Optional[EvaluareRisc] = None
    indicatori_suspiciune: list[str] = Field(default_factory=list)
    data_creare: Optional[str] = None
    data_retentie: Optional[str] = None
