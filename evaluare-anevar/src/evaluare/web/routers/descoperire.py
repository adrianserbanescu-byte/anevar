"""Descoperire comparabile din portaluri: casa + teren, pagina /descoperire."""
from __future__ import annotations

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from evaluare.discovery.orchestrator import descopera
from evaluare.discovery.scoring import metodologie
from evaluare.importers.url_parser import parse_listing_html
from evaluare.web.deps import Deps
from evaluare.web.schemas import (
    DescoperaRequest,
    DescoperaTerenRequest,
    ImportAnuntRequest,
    StergeAnuntRequest,
)


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/descopera")
    def descopera_endpoint(req: DescoperaRequest) -> dict:
        from evaluare.discovery.extractor import parse_atribute_secundare
        sec = parse_atribute_secundare("\n".join(req.atribute_secundare))
        try:
            rez = descopera(req.portal, req.judet, req.localitate, req.subiect, sec,
                            fetcher=d.fetcher, client=d.client, max_candidati=req.max_candidati)
        except (requests.RequestException, ValueError, OSError) as e:
            raise HTTPException(502, "Portalul nu a răspuns sau conexiunea a eșuat. "
                                "Încearcă din nou sau adaugă comparabilele manual.") from e
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
        try:
            rez = descopera_teren(req.portal, req.judet, req.localitate, req.suprafata_subiect,
                                  fetcher=d.fetcher, max_candidati=req.max_candidati)
        except (requests.RequestException, ValueError, OSError) as e:
            raise HTTPException(502, "Portalul nu a răspuns sau conexiunea a eșuat. "
                                "Încearcă din nou sau adaugă comparabilele manual.") from e
        return {"candidati": [{
            "url": r.url, "titlu": r.titlu,
            "pret": str(r.pret) if r.pret is not None else None,
            "suprafata": str(r.suprafata) if r.suprafata is not None else None,
            "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
            "relevanta": r.relevanta, "nota": r.nota,
        } for r in rez]}

    @router.post("/api/import-anunt")
    def import_anunt(req: ImportAnuntRequest) -> dict:
        """Primește HTML-ul unei pagini de anunț (de la extensia de browser) și extrage atributele.

        Omul navighează manual; extensia trimite DOM-ul -> zero scraping automat. Vezi
        docs/spec-extensie-browser.md.
        """
        p = parse_listing_html(req.html, sursa_url=req.url)
        anunt = {
            "pret": str(p.pret) if p.pret is not None else None,
            "moneda": p.moneda,
            "suprafata": str(p.suprafata) if p.suprafata is not None else None,
            "suprafata_teren": str(p.suprafata_teren) if p.suprafata_teren is not None else None,
            "titlu": p.titlu, "sursa_url": p.sursa_url, "an": p.an,
            "incalzire": p.incalzire, "material": p.material, "tip_cladire": p.tip_cladire,
            "nr_camere": p.nr_camere,
            "_nota": "Preț din OFERTĂ — aplică ajustare ofertă→tranzacție (GEV 520 §4.3.4).",
        }
        # adaugă în coadă (persistent în SQLite) dacă are minim preț + suprafață
        in_coada = len(d.storage.listeaza_anunturi_importate())
        if anunt["pret"] and anunt["suprafata"]:
            in_coada = d.storage.adauga_anunt_importat(anunt)
        return {**anunt, "in_coada": in_coada}

    @router.get("/api/anunturi-importate")
    def anunturi_importate() -> dict:
        return {"anunturi": d.storage.listeaza_anunturi_importate()}

    @router.post("/api/anunturi-importate/sterge")
    def sterge_importate() -> dict:
        d.storage.sterge_anunturi_importate()
        return {"anunturi": []}

    @router.post("/api/anunturi-importate/sterge-unul")
    def sterge_un_anunt(req: StergeAnuntRequest) -> dict:
        d.storage.sterge_anunt_importat(req.url)
        return {"anunturi": d.storage.listeaza_anunturi_importate()}

    @router.get("/descoperire", response_class=HTMLResponse)
    def pagina_descoperire(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "descoperire.html", {})

    return router
