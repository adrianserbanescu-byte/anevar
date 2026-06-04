"""Modelele Pydantic pentru corpurile cererilor HTTP (request bodies)."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from evaluare.discovery.profiles import SubjectProfile
from evaluare.models.comparable import Comparable, LandComparable, RentComparable


class ImportUrlRequest(BaseModel):
    url: str


class ZonaRequest(BaseModel):
    adresa: str


class IngestieRequest(BaseModel):
    tip: str               # cf | releveu | plan | cpe
    continut: str          # data-URL base64 (PDF)


class DescoperaTerenRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str = ""
    suprafata_subiect: Decimal | None = None
    max_candidati: int = 8


class GrilaTerenRequest(BaseModel):
    suprafata_subiect: Decimal
    comparabile: list[LandComparable]


class GrilaCasaRequest(BaseModel):
    suprafata_subiect: Decimal
    comparabile: list[Comparable]


class GrilaChiriiRequest(BaseModel):
    suprafata_subiect: Decimal
    comparabile: list[RentComparable]


class DescoperaRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str
    subiect: SubjectProfile
    atribute_secundare: list[str] = []
    max_candidati: int = 8


class AmlEvaluareRequest(BaseModel):
    tip_entitate: str = "PFA"            # PFA | PJ (entitatea evaluator)
    azi: str                             # data evaluarii (yyyy-mm-dd)
    client_pf: dict | None = None
    client_pj: dict | None = None
    semnale_risc: dict | None = None
    semnale_indicatori: dict | None = None


class AmlDocRequest(BaseModel):
    tip_entitate: str = "PFA"
    azi: str | None = None
    client_pf: dict | None = None
    client_pj: dict | None = None
    semnale_risc: dict | None = None
    semnale_indicatori: dict | None = None
    persoana_desemnata: dict | None = None
    rtn: dict | None = None           # {suma_eur, data_tranzactie, descriere}
    rts: dict | None = None           # {motiv, data_inregistrare, indicatori}
