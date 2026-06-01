"""Aplicatia web FastAPI: API JSON pentru evaluare + descarcare raport."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.importers.url_parser import fetch_html, import_from_url
from evaluare.report.generator import genereaza_raport
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.orchestrator import descopera
from evaluare.discovery.scoring import metodologie
from evaluare.localitati import judete as _judete, localitati as _localitati
from evaluare.zona import extrage_zona

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class ImportUrlRequest(BaseModel):
    url: str


class ZonaRequest(BaseModel):
    adresa: str


class DescoperaRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str
    subiect: SubjectProfile
    atribute_secundare: list[str] = []
    max_candidati: int = 8


def create_app(storage: Storage, client: Optional[NarrativeClient],
               fetcher: Callable[[str], str] = fetch_html) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    app = FastAPI(title="Evaluare ANEVAR")
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

    @app.post("/api/evaluare")
    def creeaza_evaluare(inp: EvaluationInput) -> dict:
        ctx = construieste_context(inp, client=client)
        eid = storage.save(ctx)
        alerte = [a.model_dump() for a in valideaza(inp)]
        return {
            "id": eid,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
            "alerte": alerte,
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
    def pagina_index(request: Request) -> HTMLResponse:
        # Pagina principala = wizard-ul ghidat pas-cu-pas.
        return templates.TemplateResponse(request, "wizard.html", {})

    @app.get("/formular", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        # Formularul monolit (toate campurile pe o pagina), alternativa la wizard.
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

    @app.post("/api/descopera")
    def descopera_endpoint(req: DescoperaRequest) -> dict:
        from evaluare.discovery.extractor import parse_atribute_secundare
        sec = parse_atribute_secundare("\n".join(req.atribute_secundare))
        rez = descopera(req.portal, req.judet, req.localitate, req.subiect, sec,
                        fetcher=fetcher, client=client, max_candidati=req.max_candidati)
        candidati = []
        for r in rez:
            candidati.append({
                "url": r.url, "titlu": r.titlu,
                "pret": str(r.pret) if r.pret is not None else None,
                "suprafata": str(r.suprafata) if r.suprafata is not None else None,
                "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
                "relevanta": r.breakdown.relevanta,
                "incredere_scazuta": r.breakdown.incredere_scazuta,
                "explicatie": r.breakdown.explicatie,
                "atribute": [a.model_dump() for a in r.breakdown.atribute],
                "secundare": [s.model_dump() for s in r.secundare],
            })
        return {"metodologie": metodologie(), "candidati": candidati}

    @app.get("/descoperire", response_class=HTMLResponse)
    def pagina_descoperire(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "descoperire.html", {})

    @app.post("/api/zona")
    def deriva_zona(req: ZonaRequest) -> dict:
        judet, localitate = extrage_zona(req.adresa, client=client)
        return {"judet": judet, "localitate": localitate}

    @app.get("/wizard", response_class=HTMLResponse)
    def pagina_wizard(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "wizard.html", {})

    @app.get("/api/localitati")
    def lista_localitati() -> dict:
        judete = _judete()
        return {"judete": judete,
                "localitati": {j["slug"]: _localitati(j["slug"]) for j in judete}}

    return app
