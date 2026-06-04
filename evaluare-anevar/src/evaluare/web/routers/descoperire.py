"""Descoperire comparabile din portaluri: casa + teren, pagina /descoperire."""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from evaluare.discovery.orchestrator import descopera
from evaluare.discovery.scoring import metodologie
from evaluare.web.deps import Deps
from evaluare.web.schemas import DescoperaRequest, DescoperaTerenRequest


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/descopera")
    def descopera_endpoint(req: DescoperaRequest) -> dict:
        from evaluare.discovery.extractor import parse_atribute_secundare
        sec = parse_atribute_secundare("\n".join(req.atribute_secundare))
        rez = descopera(req.portal, req.judet, req.localitate, req.subiect, sec,
                        fetcher=d.fetcher, client=d.client, max_candidati=req.max_candidati)
        candidati = []
        for r in rez:
            candidati.append({
                "url": r.url, "titlu": r.titlu,
                "pret": str(r.pret) if r.pret is not None else None,
                "suprafata": str(r.suprafata) if r.suprafata is not None else None,
                "teren": str(r.teren) if r.teren is not None else None,
                "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
                "relevanta": r.breakdown.relevanta,
                "incredere_scazuta": r.breakdown.incredere_scazuta,
                "explicatie": r.breakdown.explicatie,
                "atribute": [a.model_dump() for a in r.breakdown.atribute],
                "secundare": [s.model_dump() for s in r.secundare],
            })
        return {"metodologie": metodologie(), "candidati": candidati}

    @router.post("/api/descopera-teren")
    def descopera_teren_endpoint(req: DescoperaTerenRequest) -> dict:
        from evaluare.discovery.orchestrator import descopera_teren
        rez = descopera_teren(req.portal, req.judet, req.localitate, req.suprafata_subiect,
                              fetcher=d.fetcher, max_candidati=req.max_candidati)
        return {"candidati": [{
            "url": r.url, "titlu": r.titlu,
            "pret": str(r.pret) if r.pret is not None else None,
            "suprafata": str(r.suprafata) if r.suprafata is not None else None,
            "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
            "relevanta": r.relevanta, "nota": r.nota,
        } for r in rez]}

    @router.get("/descoperire", response_class=HTMLResponse)
    def pagina_descoperire(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "descoperire.html", {})

    return router
