"""Dependentele partajate, injectate in routerele pe domenii (vezi ADR-001).

`Deps` pastreaza exact modelul de injectie de pana acum (storage/client/fetcher
captate prin closure de catre rute), doar ca le grupeaza intr-un singur obiect pe
care fiecare `build_*_router(d)` il primeste.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from fastapi.templating import Jinja2Templates

from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@dataclass
class Deps:
    """Dependentele comune ale aplicatiei web."""

    storage: Storage
    client: NarrativeClient | None
    fetcher: Callable[[str], str]
    templates: Jinja2Templates
    # Coadă de import din extensia de browser (in-memory, per sesiune de aplicație).
    import_coada: list[dict] = field(default_factory=list)
