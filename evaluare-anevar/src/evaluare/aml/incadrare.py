"""Incadrarea evaluatorului: cine are/nu are obligatii (persoana desemnata, audit independent)."""
from __future__ import annotations

from decimal import Decimal

from evaluare.aml.constante import (
    PRAG_AUDIT_ACTIVE_LEI, PRAG_AUDIT_CA_LEI, PRAG_AUDIT_SALARIATI,
)


def necesita_persoana_desemnata(tip_entitate: str) -> bool:
    """PFA / persoana fizica NU au obligatia (Norme art. 7; Legea art. 23(4)). Societatea — da."""
    return tip_entitate.upper() not in ("PFA", "PF", "PERSOANA_FIZICA", "INDEPENDENT")


def necesita_audit_independent(active_lei, ca_lei, salariati: int) -> bool:
    """Obligatoriu daca se depasesc cel putin 2 din 3 praguri (Norme art. 9)."""
    depasiri = 0
    if active_lei is not None and Decimal(str(active_lei)) > PRAG_AUDIT_ACTIVE_LEI:
        depasiri += 1
    if ca_lei is not None and Decimal(str(ca_lei)) > PRAG_AUDIT_CA_LEI:
        depasiri += 1
    if salariati is not None and salariati > PRAG_AUDIT_SALARIATI:
        depasiri += 1
    return depasiri >= 2
