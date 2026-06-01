"""Aplicatia web FastAPI: API JSON pentru evaluare + descarcare raport."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.importers.url_parser import fetch_html, import_from_url
from evaluare.report.generator import genereaza_raport

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class ImportUrlRequest(BaseModel):
    url: str


def create_app(storage: Storage, client: Optional[NarrativeClient],
               fetcher: Callable[[str], str] = fetch_html) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    app = FastAPI(title="Evaluare ANEVAR")
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

    @app.post("/api/evaluare")
    def creeaza_evaluare(inp: EvaluationInput) -> dict:
        ctx = construieste_context(inp, client=client)
        eid = storage.save(ctx)
        return {
            "id": eid,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        }

    @app.get("/api/evaluare/{eid}")
    def citeste_evaluare(eid: int) -> dict:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        return {
            "id": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        }

    @app.get("/api/evaluare/{eid}/raport.docx")
    def descarca_raport(eid: int) -> FileResponse:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        out = Path(tempfile.gettempdir()) / f"raport_{eid}.docx"
        genereaza_raport(ctx, out)
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"raport_{eid}.docx")

    @app.get("/", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "form.html", {})

    @app.get("/evaluare/{eid}", response_class=HTMLResponse)
    def pagina_rezultat(request: Request, eid: int) -> HTMLResponse:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        return templates.TemplateResponse(request, "result.html", {
            "eid": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        })

    @app.post("/api/import-url")
    def importa_url(req: ImportUrlRequest) -> dict:
        parsed = import_from_url(req.url, fetcher=fetcher)
        return {
            "pret": str(parsed.pret) if parsed.pret is not None else None,
            "moneda": parsed.moneda,
            "suprafata": str(parsed.suprafata) if parsed.suprafata is not None else None,
            "titlu": parsed.titlu,
            "sursa_url": parsed.sursa_url,
        }

    return app
