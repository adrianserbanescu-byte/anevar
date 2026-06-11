"""Registrul de evidenta a rapoartelor de evaluare (Procedura de arhivare ANEVAR §6).

Pagina + export CSV/XLSX cu cele ~13 campuri cerute de §6. Randurile se deriva din dosarele de pe
disc (`registru.registru`), deci registrul nu se poate desincroniza de dosare.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response

from evaluare.registru import registru as reg
from evaluare.web.deps import Deps

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.get("/registru", response_class=HTMLResponse)
    def pagina_registru(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "curent/registru.html",
            {"coloane": reg.COLOANE, "randuri": reg.randuri()})

    @router.get("/api/registru")
    def api_registru() -> dict:
        """Registrul ca JSON (coloane + randuri) — pentru integrari / verificare."""
        return {
            "coloane": [{"cheie": k, "eticheta": et} for k, et in reg.COLOANE],
            "randuri": reg.randuri(),
        }

    @router.get("/api/registru.csv")
    def registru_csv() -> PlainTextResponse:
        return PlainTextResponse(reg.csv_text(), media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=registru-rapoarte.csv"})

    @router.get("/api/registru.xlsx")
    def registru_xlsx() -> Response:
        return Response(reg.xlsx_bytes(), media_type=XLSX_MIME,
            headers={"Content-Disposition": "attachment; filename=registru-rapoarte.xlsx"})

    return router
