"""Modelele Pydantic pentru corpurile cererilor HTTP (request bodies)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from evaluare.aml.validare_data import verifica_an_plauzibil
from evaluare.discovery.profiles import SubjectProfile
from evaluare.models.comparable import Comparable, LandComparable, RentComparable


def _data_iso(v: str) -> str:
    """Valideaza ca `v` e o data ISO yyyy-mm-dd cu an plauzibil. Altfel ValueError -> 422 clar
    (nu 500 downstream, cand date.fromisoformat ar crapa pe '' / format invalid, sau cand un an
    absurd ca 9999 ar depasi limita lui date() in aritmetica de reevaluare)."""
    try:
        d = date.fromisoformat(str(v).strip())
    except (ValueError, TypeError) as e:
        raise ValueError("Data trebuie sa fie o data valida in format yyyy-mm-dd.") from e
    verifica_an_plauzibil(d)
    return v


class ImportUrlRequest(BaseModel):
    url: str


class ImportAnuntRequest(BaseModel):
    """Trimis de extensia de browser: HTML-ul paginii deschise manual + URL-ul ei."""
    html: str
    url: str = ""


class StergeAnuntRequest(BaseModel):
    """Sterge un singur anunt din coada de import, dupa URL-ul sursa."""
    url: str


class RedenumesteRequest(BaseModel):
    """Redenumirea unui dosar salvat."""
    nume: str


class ContRequest(BaseModel):
    """Crearea contului local (UI nou)."""
    nume: str
    legitimatie: str
    format_dosar: list[str] = []


class DosarNouRequest(BaseModel):
    """Crearea unui dosar nou (UI nou): câmpurile wizard inițiale."""
    wizard: dict = {}


class ImportDocxRequest(BaseModel):
    """Import «dosarul tău» dintr-un raport .docx (UI nou): fișier ca data-URL base64."""
    nume_fisier: str
    continut: str               # data-URL base64 (.docx)


class FeedbackRequest(BaseModel):
    """Feedback de la tester/evaluator (salvat local, offline)."""
    mesaj: str = ""
    sentiment: str = ""
    pagina: str = ""
    url: str = ""
    tester: str = ""


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
    max_candidati: int = 20             # default ridicat (era 8); configurabil din request (control UI)


# N4 (audit nealiniat-consistenta): suprafata subiect <=0 era respinsa de /api/grila-chirii (engine
# evalueaza_chirie ridica ValueError -> 422) dar acceptata tacut de grila-casa (suprafata ignorata) si
# grila-teren (producea valoare_teren <=0). Aliniem la comportamentul STRICT (chirii) prin gard la
# nivel de schema -> 422 consistent pentru toate 3 grilele inainte de a ajunge in motor.
class GrilaTerenRequest(BaseModel):
    suprafata_subiect: Decimal = Field(gt=0)
    comparabile: list[LandComparable]


class GrilaCasaRequest(BaseModel):
    suprafata_subiect: Decimal = Field(gt=0)
    comparabile: list[Comparable]


class GrilaChiriiRequest(BaseModel):
    suprafata_subiect: Decimal = Field(gt=0)
    comparabile: list[RentComparable]


class DescoperaRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str
    subiect: SubjectProfile
    atribute_secundare: list[str] = []
    max_candidati: int = 20             # default ridicat (era 8); configurabil din request (control UI)
    tip_activ: str | None = None        # categoria proprietatii (ex. "apartament") -> model de scoring per categorie


class ConfigPonderiRequest(BaseModel):
    """Ponderi editate de evaluator (D1), per categorie: {"<categorie>": {"<atribut>": <numar>}}."""

    ponderi: dict[str, dict[str, float]]


class AmlEvaluareRequest(BaseModel):
    tip_entitate: str = "PFA"            # PFA | PJ (entitatea evaluator)
    azi: str                             # data evaluarii (yyyy-mm-dd)
    client_pf: dict | None = None
    client_pj: dict | None = None
    semnale_risc: dict | None = None
    semnale_indicatori: dict | None = None

    @field_validator("azi")
    @classmethod
    def _azi_data_valida(cls, v: str) -> str:   # azi e obligatorie + trebuie data valida (nu '' -> 500)
        return _data_iso(v)


class AmlDocRequest(BaseModel):
    tip_entitate: str = "PFA"
    azi: str | None = None
    client_pf: dict | None = None
    client_pj: dict | None = None
    semnale_risc: dict | None = None
    semnale_indicatori: dict | None = None
    persoana_desemnata: dict | None = None

    @field_validator("azi")
    @classmethod
    def _azi_data_valida(cls, v: str | None) -> str | None:   # None/'' OK (endpoint are fallback);
        return _data_iso(v) if v else v                       # daca e dat non-gol, trebuie data valida
    rtn: dict | None = None           # {suma_eur, data_tranzactie, descriere}
    rts: dict | None = None           # {motiv, data_inregistrare, indicatori}
