"""Aplicatia web FastAPI: compune routerele pe domenii (vezi ADR-001)."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.importers.url_parser import fetch_html
from evaluare.web.deps import Deps
from evaluare.web.routers import aml, descoperire, evaluare, grile, pagini, piata


def create_app(storage: Storage, client: NarrativeClient | None,
               fetcher: Callable[[str], str] = fetch_html) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    from fastapi.middleware.cors import CORSMiddleware

    from evaluare import __version__
    app = FastAPI(title="Evaluare ANEVAR")
    # Permite extensiei de browser sa POST-eze pe /api/import-anunt (aplicatie locala).
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"chrome-extension://.*|moz-extension://.*",
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
    templates.env.globals["versiune"] = __version__
    deps = Deps(storage=storage, client=client, fetcher=fetcher, templates=templates)

    for modul in (evaluare, grile, descoperire, piata, aml, pagini):
        app.include_router(modul.build_router(deps))

    return app
