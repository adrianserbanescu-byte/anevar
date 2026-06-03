"""Validare incrucisata finala (consistenta intre abordari, plauzibilitate)."""
from __future__ import annotations

from decimal import Decimal

from evaluare.engine.validation import Issue
from evaluare.models.report_context import ReportContext

# Peste acest prag, divergenta intre abordarea prin piata si cea prin cost merita semnalata.
PRAG_DIVERGENTA = Decimal("0.30")


def valideaza_incrucisat(ctx: ReportContext) -> list[Issue]:
    """Verificari de consistenta intre rezultate, inainte de finalizare."""
    issues: list[Issue] = []

    m = ctx.market_result.valoare_piata if ctx.market_result else None
    c = ctx.cost_result.valoare_cost if ctx.cost_result else None
    if m is not None and c is not None and max(m, c) > 0:
        div = abs(m - c) / max(m, c)
        if div > PRAG_DIVERGENTA:
            issues.append(Issue(
                nivel="alerteaza",
                mesaj=(f"Abordarile prin piata ({m}) si prin cost ({c}) diverg cu {div:.0%} "
                       f"(> {PRAG_DIVERGENTA:.0%}); justifica reconcilierea."),
            ))

    if ctx.alocare_constructii is not None and ctx.alocare_constructii < 0:
        issues.append(Issue(
            nivel="alerteaza",
            mesaj=("Valoarea alocata constructiilor este negativa (valoarea terenului depaseste "
                   "valoarea proprietatii) — verifica grila de teren."),
        ))

    if ctx.reconciled.valoare_finala <= 0:
        issues.append(Issue(nivel="blocheaza", mesaj="Valoarea finala estimata este <= 0."))

    return issues
