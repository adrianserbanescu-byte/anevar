"""Datele administrative ale lucrarii de evaluare."""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class EvaluationMeta(BaseModel):
    """Identificarea lucrarii: client, scop, date, evaluator."""

    client_nume: str
    client_tip: str = "Persoana fizica"
    beneficiar: str = ""                 # banca finantatoare / utilizator desemnat
    # GEV 520 (2025, par. 77-78): tipul utilizatorului desemnat. 'creditor' (default) = garantare credit
    # -> raportul se inregistreaza in BIG. 'ANAF' = garantare la reesalonarea datoriilor -> NU se
    # inregistreaza in BIG. Conditioneaza textul de inregistrare BIG din raport (vezi report/generator).
    utilizator_desemnat: Literal["creditor", "ANAF"] = "creditor"
    proprietar: str | None = None     # daca difera de client
    adresa: str
    numar_cadastral: str
    carte_funciara: str
    tip_drept: str = "drept de proprietate deplină"   # dreptul evaluat (SEV 230 §40.1)
    act_proprietate: str | None = None                 # titlul (ex. contract vânzare nr/dată) — GEV 630 §16
    sarcini: str | None = None                         # ipoteci/servituți din CF (SEV 230 §140; critic la garantare)
    scop: str = "Garantarea creditului ipotecar"
    tip_valoare: str = "Valoarea de piață (SEV 102)"
    # Numarul de identificare a raportului = nr. de lucrare `AAAA/NNNN` (Procedura de arhivare §6/§11).
    # Alocat la crearea dosarului si stocat in dosar.json; injectat in meta de endpointul de raport
    # (autoritar server-side) si afisat pe coperta. Vezi registru/numar.py si registru/registru.py.
    nr_lucrare: str | None = None
    data_evaluarii: str                 # ISO sau text, ex. "2026-01-16"
    data_raportului: str
    data_predarii: str | None = None    # data predarii raportului catre client (registru §6)
    data_inspectiei: str | None = None
    # Verificarea interna a calitatii (Procedura §6 + SEV 100, anterioara predarii; control intern AML
    # la PJ — HCD 58 art. 5): cine a verificat raportul si cand. Intra in registru.
    verificator_intern_nume: str | None = None
    data_verificare_interna: str | None = None
    # Onorariul lucrarii (registru §6). Marginit >=0; gol -> necompletat. Decimal pentru consecventa cu
    # restul sumelor (acelasi tipar ca `curs_valutar`).
    onorariu: Decimal | None = Field(default=None, ge=0)
    inspectie_amploare: str | None = None     # interior+exterior / doar exterior / limitată (GEV 630 §24)
    inspectie_insotitor: str | None = None    # cine a însoțit la inspecție (§44)
    inspectie_observatii: str | None = None   # neconcordanțe scriptic↔faptic / limitări (§111.a.3)
    valabilitate: str | None = None
    evaluator_nume: str
    evaluator_legitimatie: str
    moneda: str = "LEI"
    # EUR -> LEI la data evaluarii. Marginit: un curs valutar real e >0 si mult sub 1e6; valori
    # extreme (ex. 1E-30) faceau quantize-ul din fmt_numar(val/curs) sa arunce InvalidOperation
    # (>1e26) -> 500 la /evaluare. gt=0/le=1e6 le respinge cu 422 inca de la /api/evaluare.
    curs_valutar: Decimal | None = Field(default=None, gt=0, le=1_000_000)
    # Codul postal al imobilului subiect. Necesar la inregistrarea raportului in BIG
    # (gap S-4). Optional (default None) -> backward-compatible cu lucrarile existente.
    cod_postal: str | None = None
    # Riscuri fizice identificate (ESG, GEV 520 §86-88, novatie 2025): lista de etichete
    # (ex. "inundabilitate", "seismic", "alunecari de teren"). Evaluatorul autorizat NU
    # are competenta de cuantificare — se enumera/semnaleaza (gap S-5 ESG). Lista goala
    # implicit -> neafectate constructiile existente.
    riscuri_fizice: list[str] = Field(default_factory=list)
    # Certificatul de performanta energetica (CPE): clasa energetica / referinta document
    # obligatoriu la garantare (GEV 520 §46, gap G7). Optional (default None).
    certificat_energetic: str | None = None
