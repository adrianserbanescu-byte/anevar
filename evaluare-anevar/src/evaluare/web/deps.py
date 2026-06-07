"""Dependentele partajate, injectate in routerele pe domenii (vezi ADR-001).

`Deps` pastreaza exact modelul de injectie de pana acum (storage/client/fetcher
captate prin closure de catre rute), doar ca le grupeaza intr-un singur obiect pe
care fiecare `build_*_router(d)` il primeste.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from fastapi.templating import Jinja2Templates

from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.report.pdf import docx_to_pdf

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@dataclass
class Deps:
    """Dependentele comune ale aplicatiei web."""

    storage: Storage
    client: NarrativeClient | None
    fetcher: Callable[[str], str]
    templates: Jinja2Templates
    # Convertor .docx -> .pdf (injectabil pentru teste); implicit LibreOffice/Word local.
    pdf_converter: Callable[[Path], Path] = field(default=docx_to_pdf)
