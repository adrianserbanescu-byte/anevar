"""Motor de risc AML: factori ponderati -> scor -> categorie + nivel de masuri.

Reguli HARD (Legea art. 17(1)): anumite semnale forteaza automat categoria „sporit" (EDD),
indiferent de scor. PEP efectiv = PEP sau in primele 12 luni de la incetarea functiei (art. 3(6)).

Scopul evaluarii (Ghidul de evaluare a riscurilor SB/FT, cap. 2) este un factor de risc de
sine statator pe dimensiunea „produs/serviciu": lichidare/insolventa/executare silita si vanzare
pe piata libera ridica riscul (subevaluare/supraevaluare frauduloasa); garantare credit bancar,
impozitare si raportare financiara il scad (DD dublata de banca / scop fiscal cu risc redus).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from evaluare.aml.constante import PERIOADA_POST_PEP_LUNI
from evaluare.aml.models import (
    CategorieRisc,
    ClientPF,
    ClientPJ,
    EvaluareRisc,
    FactorRisc,
    NivelMasuri,
    StatutPEP,
)

# Cate luni inainte trebuie reevaluata relatia, pe categorie de risc (politica interna uzuala).
_LUNI_REEVALUARE = {"redus": 36, "standard": 24, "sporit": 12}

# Scopul/tipul evaluarii (Ghidul SB/FT, cap. 2). Domeniul app-ului = garantare_credit.
ScopEvaluare = Literal[
    "garantare_credit",            # banca dubleaza DD -> risc redus (atentie la presiunea „valoare mare")
    "impozitare",                  # scop fiscal -> risc redus
    "raportare_financiara",        # raportare contabila -> risc redus
    "vanzare_piata",               # vanzare/cumparare piata libera -> risc mai mare
    "mna",                         # fuziuni & achizitii -> risc
    "lichidare_insolventa_executare",  # lichidare/insolventa/executare silita -> risc (subevaluare)
]

# Maparea scopului pe factorul „produs/serviciu" (1=coboara, 3=ridica, None=neutru).
_SCOP_FACTOR: dict[str, int] = {
    "garantare_credit": 1,
    "impozitare": 1,
    "raportare_financiara": 1,
    "vanzare_piata": 3,
    "mna": 3,
    "lichidare_insolventa_executare": 3,
}


class Semnale(BaseModel):
    """Semnale de risc culese de evaluator pentru o relatie (toate optionale, implicit neutru)."""

    # factori care scad riscul
    client_cunoscut: bool = False
    tranzactie_uzuala: bool = False
    canal_fata_in_fata: bool = False
    tara_risc_redus: bool = False
    # factori / reguli HARD care forteaza „sporit"
    tara_risc_inalt: bool = False          # tara terta cu risc inalt (CE) / necooperanta
    pe_lista_sanctiuni: bool = False
    tranzactie_complexa: bool = False      # complexa / neobisnuit de mare / fara scop economic
    canal_la_distanta: bool = False        # relatie fara prezenta fizica (art. 17(2))
    # scopul/tipul evaluarii ca factor de risc (Ghidul SB/FT, cap. 2) — optional, implicit neutru
    scop: ScopEvaluare | None = None


def _luni_intre(d1: str, d2: str) -> int:
    """Numar aproximativ de luni intregi intre d1 si d2 (ISO yyyy-mm-dd), d2 >= d1."""
    a = date.fromisoformat(d1)
    b = date.fromisoformat(d2)
    luni = (b.year - a.year) * 12 + (b.month - a.month)
    if b.day < a.day:
        luni -= 1
    return luni


def pep_efectiv(statut: StatutPEP, azi: str) -> bool:
    """PEP relevant: titular activ sau in primele 12 luni de la incetare (Legea art. 3(6))."""
    if not statut.este_pep:
        return False
    if statut.data_incetare_functie is None:
        return True
    return _luni_intre(statut.data_incetare_functie, azi) < PERIOADA_POST_PEP_LUNI


def nivel_masuri(categorie: CategorieRisc) -> NivelMasuri:
    """Mapare categorie -> nivel masuri de cunoastere (Legea art. 16/17; Norme art. 12(4))."""
    masuri: dict[CategorieRisc, NivelMasuri] = {
        "redus": "simplificate", "standard": "standard", "sporit": "suplimentare",
    }
    return masuri[categorie]


def _adauga_luni(d: str, luni: int) -> str:
    base = date.fromisoformat(d)
    luni_total = base.month - 1 + luni
    an = base.year + luni_total // 12
    luna = luni_total % 12 + 1
    # ziua: ramane aceeasi (toate datele de reevaluare cad pe zile <= 28 in practica)
    zi = min(base.day, 28)
    return date(an, luna, zi).isoformat()


def _client_pep_efectiv(client, azi: str) -> bool:
    if isinstance(client, ClientPF) and pep_efectiv(client.pep, azi):
        return True
    if isinstance(client, ClientPJ):
        for br in client.beneficiari_reali:
            if pep_efectiv(br.pep, azi):
                return True
    return False


def _beneficiar_real_lipsa(client) -> bool:
    """PJ fara beneficiar real identificat = factor de risc (Legea art. 4/art. 17; Planul I.3).

    „Lipsa" = niciun beneficiar real consultat in registrul central. O lista goala sau cu BR
    nedovediti (fara `consultat_registru_central`) este un semnal de alarma (Ghidul SB/FT, cap. 3).
    Aici doar ridicam factorul „client" (aditiv, om-in-bucla); nu fortam categoria „sporit".
    """
    if not isinstance(client, ClientPJ):
        return False
    return not any(br.consultat_registru_central for br in client.beneficiari_reali)


def _factor_produs(semnale: Semnale) -> int:
    """Factorul „produs/serviciu": combina tranzactia (uzuala/complexa) cu scopul evaluarii.

    Precedenta: orice semnal care ridica (tranzactie complexa SAU scop cu risc) -> 3; altfel,
    daca exista un semnal care coboara (tranzactie uzuala SAU scop cu risc redus) -> 1; restul 2.
    Aditiv si compatibil cu vechiul comportament (cand `scop is None`, ramane tranzactia).
    """
    scop_factor = _SCOP_FACTOR.get(semnale.scop) if semnale.scop else None
    ridica = semnale.tranzactie_complexa or scop_factor == 3
    coboara = semnale.tranzactie_uzuala or scop_factor == 1
    if ridica:
        return 3
    if coboara:
        return 1
    return 2


def evalueaza_risc(client, semnale: Semnale | None = None, *, azi: str) -> EvaluareRisc:
    """Calculeaza categoria de risc a relatiei (Norme art. 12-14) + reguli HARD (Legea art. 17)."""
    semnale = semnale or Semnale()

    br_lipsa = _beneficiar_real_lipsa(client)

    # ---- factor: client (1=redus,2=standard,3=sporit) ----
    # BR neidentificat la PJ ridica factorul (semnal de alarma — Legea art. 4/art. 17; Planul I.3),
    # dar nu forteaza „sporit": decizia ramane la evaluator (om-in-bucla).
    if _client_pep_efectiv(client, azi) or semnale.pe_lista_sanctiuni or br_lipsa:
        f_client = 3
    elif semnale.client_cunoscut:
        f_client = 1
    else:
        f_client = 2

    # ---- factor: produs/serviciu (tranzactia + scopul evaluarii) ----
    f_produs = _factor_produs(semnale)

    # ---- factor: canal de distributie ----
    if semnale.canal_la_distanta:
        f_canal = 3
    elif semnale.canal_fata_in_fata:
        f_canal = 1
    else:
        f_canal = 2

    # ---- factor: geografic ----
    if semnale.tara_risc_inalt:
        f_geo = 3
    elif semnale.tara_risc_redus:
        f_geo = 1
    else:
        f_geo = 2

    factori = [
        FactorRisc(nume="client", valoare=f_client, pondere=2),
        FactorRisc(nume="produs_serviciu", valoare=f_produs, pondere=1),
        FactorRisc(nume="canal", valoare=f_canal, pondere=1),
        FactorRisc(nume="geografic", valoare=f_geo, pondere=2),
    ]
    pondere_totala = sum(f.pondere for f in factori)
    scor = Decimal(sum(f.valoare * f.pondere for f in factori)) / Decimal(pondere_totala)

    # ---- reguli HARD: forteaza sporit (Legea art. 17(1)) ----
    motive: list[str] = []
    if _client_pep_efectiv(client, azi):
        motive.append("PEP efectiv (titular sau în primele 12 luni de la încetare) — art. 17(1)(c)")
    if semnale.pe_lista_sanctiuni:
        motive.append("Persoană pe listă de sancțiuni")
    if semnale.tara_risc_inalt:
        motive.append("Țară terță cu risc înalt / necooperantă — art. 17(1)")
    if semnale.tranzactie_complexa:
        motive.append("Tranzacție complexă / neobișnuit de mare / fără scop economic aparent — art. 17(1)")
    if semnale.canal_la_distanta:
        motive.append("Relație de afaceri fără prezență fizică — art. 17(2)")

    # ---- categorie ----
    if motive:
        categorie: CategorieRisc = "sporit"
    elif scor <= Decimal("1.4"):
        categorie = "redus"
    elif scor >= Decimal("2.2"):
        categorie = "sporit"
    else:
        categorie = "standard"

    # BR neidentificat la PJ: ridica factorul (mai sus), iar daca relatia ajunge „sporit"
    # documentam si acest motiv (aditiv — nu forteaza singur categoria).
    if br_lipsa and categorie == "sporit":
        motive.append(
            "Beneficiar real neidentificat la PJ (neconsultat în registrul central) "
            "— Legea art. 4/art. 17; Planul I.3"
        )

    return EvaluareRisc(
        factori=factori,
        scor=scor,
        categorie=categorie,
        nivel_masuri=nivel_masuri(categorie),
        motive_sporit=motive,
        data=azi,
        data_reevaluare=_adauga_luni(azi, _LUNI_REEVALUARE[categorie]),
    )
