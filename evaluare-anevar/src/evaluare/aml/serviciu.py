"""Serviciu AML: orchestreaza evaluarea unei relatii (risc + indicatori + screening + documente).

Pur (fara I/O de retea); datele KYC raman local. Returneaza un rezultat structurat pe care
endpoint-ul il expune evaluatorului (om-in-bucla).
"""
from __future__ import annotations

from evaluare.aml.incadrare import necesita_persoana_desemnata
from evaluare.aml.indicatori import SemnaleIndicatori, evalueaza_indicatori, propune_rts
from evaluare.aml.liste import Liste, screening
from evaluare.aml.models import ClientPF, ClientPJ, EvaluareRisc
from evaluare.aml.risc import Semnale, evalueaza_risc

Client = ClientPF | ClientPJ


def _nume_screening(client: Client) -> list[str]:
    nume: list[str] = []
    if isinstance(client, ClientPF):
        nume.append(f"{client.persoana.nume} {client.persoana.prenume}".strip())
    else:
        nume.append(client.denumire)
        if client.reprezentant_legal.nume:
            nume.append(f"{client.reprezentant_legal.nume} {client.reprezentant_legal.prenume}".strip())
        for br in client.beneficiari_reali:
            nume.append(f"{br.nume} {br.prenume}".strip())
    return [n for n in nume if n]


def evalueaza_relatie(
    tip_entitate: str,
    client: Client,
    *,
    azi: str,
    semnale_risc: Semnale | None = None,
    semnale_indicatori: SemnaleIndicatori | None = None,
    liste: Liste | None = None,
) -> dict:
    """Evalueaza o relatie de afaceri: categorie risc, indicatori, screening, documente necesare."""
    semnale_indicatori = semnale_indicatori or SemnaleIndicatori()

    evaluare: EvaluareRisc = evalueaza_risc(client, semnale_risc, azi=azi)
    indicatori = evalueaza_indicatori(semnale_indicatori)
    rts = propune_rts(semnale_indicatori)

    potriviri = []
    if liste is not None:
        for nume in _nume_screening(client):
            potriviri.extend(p.model_dump() for p in screening(nume, liste))

    documente = ["norme_interne", "evaluare_risc", "fisa_kyc"]
    if necesita_persoana_desemnata(tip_entitate):
        documente.append("decizie_desemnare")
    if rts:
        documente.append("rts")

    return {
        "evaluare_risc": evaluare.model_dump(mode="json"),
        "categorie": evaluare.categorie,
        "nivel_masuri": evaluare.nivel_masuri,
        "motive_sporit": evaluare.motive_sporit,
        "indicatori": [i.model_dump() for i in indicatori],
        "propune_rts": rts,
        "screening": potriviri,
        "necesita_persoana_desemnata": necesita_persoana_desemnata(tip_entitate),
        "documente_necesare": documente,
    }
