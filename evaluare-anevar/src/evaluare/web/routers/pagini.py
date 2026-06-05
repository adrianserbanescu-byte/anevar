"""Pagini HTML generale: index (wizard), formular clasic, wizard."""
from __future__ import annotations

import time

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from evaluare import __version__
from evaluare.web.deps import Deps


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()
    pornit_la = time.time()

    @router.get("/api/status")
    def status() -> dict:
        """Stare aplicație: versiune + uptime. Folosit de popup-ul extensiei pentru ping."""
        return {
            "ok": True,
            "versiune": __version__,
            "uptime_secunde": round(time.time() - pornit_la, 1),
            "anunturi_in_coada": len(d.storage.listeaza_anunturi_importate()),
        }

    @router.get("/", response_class=HTMLResponse)
    def pagina_index(request: Request) -> HTMLResponse:
        # Pagina principala = wizard-ul ghidat pas-cu-pas.
        return d.templates.TemplateResponse(request, "wizard.html", {})

    @router.get("/formular", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        # Formularul monolit (toate campurile pe o pagina), alternativa la wizard.
        return d.templates.TemplateResponse(request, "form.html", {})

    @router.get("/wizard", response_class=HTMLResponse)
    def pagina_wizard(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "wizard.html", {})

    return router
