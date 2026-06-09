"""Grile de comparabile: teren, casa, chirii + pagina /grila."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from evaluare.engine import metodologie_store
from evaluare.engine.chirie import evalueaza_chirie
from evaluare.engine.land import evaluate_land
from evaluare.engine.market import evaluate_market
from evaluare.logging_setup import get_logger
from evaluare.web.deps import Deps
from evaluare.web.schemas import GrilaCasaRequest, GrilaChiriiRequest, GrilaTerenRequest

log = get_logger(__name__)


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/grila-teren")
    def grila_teren(req: GrilaTerenRequest) -> dict:
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)   # acelasi config ca /calcul
        try:
            r = evaluate_land(req.comparabile, req.suprafata_subiect, cfg)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        return {
            "preturi_mp_corectate": [str(p) for p in r.preturi_mp_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "ajustari_nete": [str(n) for n in r.ajustari_nete],
            "index_selectat": r.index_selectat,
            "pret_mp_ales": str(r.pret_mp_ales),
            "valoare_teren": str(r.valoare_teren),
        }

    @router.post("/api/grila-casa")
    def grila_casa(req: GrilaCasaRequest) -> dict:
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)   # acelasi config ca /calcul (M2/M1)
        try:
            r = evaluate_market(req.comparabile, req.suprafata_subiect, cfg)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        return {
            "preturi_unitare_corectate": [str(p) for p in r.preturi_unitare_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "ajustari_nete": [str(n) for n in r.ajustari_nete],
            "index_selectat": r.index_selectat,
            "valoare_piata": str(r.valoare_piata),
        }

    @router.post("/api/grila-chirii")
    def grila_chirii(req: GrilaChiriiRequest) -> dict:
        try:
            r = evalueaza_chirie(req.comparabile, req.suprafata_subiect)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        return {
            "chirii_mp_corectate": [str(p) for p in r.chirii_mp_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "ajustari_nete": [str(n) for n in r.ajustari_nete],
            "index_selectat": r.index_selectat,
            "chirie_mp_aleasa": str(r.chirie_mp_aleasa),
            "chirie_lunara": str(r.chirie_lunara),
            "venit_brut_potential": str(r.venit_brut_potential),
        }

    @router.get("/grila", response_class=HTMLResponse)
    def pagina_grila(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "grila.html", {})

    return router
