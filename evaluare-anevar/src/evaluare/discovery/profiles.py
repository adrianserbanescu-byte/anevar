"""Modele pentru descoperirea comparabilelor: profiluri si breakdown de scor."""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SubjectProfile(BaseModel):
    """Atributele primare ale proprietatii evaluate (normalizate pentru scoring)."""

    suprafata_construita: Decimal | None = None   # mp (suprafata casei, ex. Acd)
    an: int | None = None                # an constructie
    stare: int | None = None             # treapta 1-5 (1=degradata .. 5=noua)
    finisaj: int | None = None           # treapta 1-4 (1=modest .. 4=lux)
    incalzire: str | None = None         # categorie normalizata (ex. "centrala_gaz")
    teren: Decimal | None = None         # mp (suprafata teren)
    nr_camere: int | None = None         # numar de camere (driver major la apartament)
    etaj: int | None = None              # etajul (apartament); 0 = parter. Extras din anunt (url_parser).
    segment: str | None = None           # sub-segment/tip de piață al subiectului (pt. bonus de match exact)


class CandidateProfile(BaseModel):
    """Atributele primare extrase pentru un candidat + textul brut gasit (dovada)."""

    suprafata_construita: Decimal | None = None   # mp (din anunt, via parser)
    an: int | None = None
    stare: int | None = None
    finisaj: int | None = None
    incalzire: str | None = None
    teren: Decimal | None = None
    nr_camere: int | None = None
    etaj: int | None = None
    texte: dict[str, str] = Field(default_factory=dict)   # ex {"an": "2008"}
    # ── Semnale metodologice ADITIVE (recență/proximitate/segment) — vezi `scoring.py`. ──────────
    # Toate sunt OPȚIONALE (None = necunoscut → niciun efect asupra scorului = backward-compatible).
    # Operaționalizează garda G7 (recență 3–6 luni / proximitate <1 km — articole-piata-2 §1.3) ca
    # AJUSTARE de relevanță, NU ca atribut din formulă. Praguri = EURISTICI (SEV nu le fixează).
    vechime_zile: int | None = None      # zilele de la data anunțului/tranzacției (recența)
    distanta_km: float | None = None     # distanța față de subiect (km), când există geocoding
    segment: str | None = None           # sub-segment/tip de piață al candidatului (ex. "rezidential_premium")


class AttributeBreakdown(BaseModel):
    """Detalierea unui atribut in scor (pentru afisare auditabila)."""

    nume: str
    valoare_subiect: str | None = None
    valoare_candidat: str | None = None      # textul brut gasit in anunt
    d: float | None = None                   # dissimilaritate [0,1]; None daca necunoscut
    pondere: float = 0                        # tolereaza float (ponderi editate); afisarea ramane intreaga
    contributie: float | None = None         # pondere * d; None daca necunoscut
    cunoscut: bool = True


class ScoreBreakdown(BaseModel):
    """Rezultatul complet al scorarii unui candidat."""

    relevanta: int                              # 0-100 (DUPA ajustarile de recenta/proximitate/segment)
    dissimilaritate: float
    atribute: list[AttributeBreakdown]
    atribute_cunoscute: int
    incredere_scazuta: bool
    explicatie: str                             # formula exacta cu numere (auto-continuta)
    # Scor descompus pe axe pentru radarul D2 (Locatie/Fizic/Calitate/Functional); None = axa fara date.
    axe: dict[str, int | None] = Field(default_factory=dict)
    # Relevanța pe atribute, ÎNAINTE de ajustarile metodologice (recenta/proximitate/segment).
    # Egala cu `relevanta` cand nu exista niciun semnal de ajustare → backward-compatible.
    relevanta_atribute: int | None = None
    # Ajustari aplicate (lista de etichete scurte, ex. ["recență −12%", "proximitate −8%"]); goala cand nu e cazul.
    ajustari: list[str] = Field(default_factory=list)
