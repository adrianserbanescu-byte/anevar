"""Pagini HTML generale: index (wizard), formular clasic, wizard."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from evaluare.web.deps import Deps


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

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
