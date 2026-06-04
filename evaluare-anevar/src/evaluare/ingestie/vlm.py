"""Strat vision-language (VLM) injectabil — plasa de siguranta pentru ce nu prinde regex-ul.

Clientul e injectabil (ca NarrativeClient/fetcher): modulul ramane testabil offline, fara o
dependenta dura de un anumit furnizor. GDPR: textul trimis catre VLM trebuie anonimizat in
prealabil (reutilizeaza report/anonymizer), apoi demascat local.
"""
from __future__ import annotations

import json
from typing import Protocol


class VlmClient(Protocol):
    """Interfata minima a unui client vision-language."""

    def extrage(self, continut: str, instructiune: str) -> str:
        ...


def extrage_campuri_vlm(
    continut: str, instructiune: str, client: VlmClient | None
) -> dict | None:
    """Cere VLM-ului campuri structurate (JSON). None daca nu exista client sau raspunsul e invalid."""
    if client is None:
        return None
    try:
        raspuns = client.extrage(continut, instructiune)
        return json.loads(raspuns)
    except (ValueError, TypeError):
        return None
