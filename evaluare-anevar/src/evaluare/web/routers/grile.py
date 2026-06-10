"""Grile de comparabile: teren, casa, chirii + pagina /grila."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

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

_BANI = Decimal("0.01")
# Input degenerat (valori subnormale / uriase ~1e308 -> overflow la quantize/Decimal) -> 422 clar, nu 500.
_DETALIU_INVALID = "Valoare numerica invalida sau in afara intervalului calculabil: {e}"


def _bani(v: Decimal) -> str:
    """Valoarea de afisare rotunjita la bani — media top-N (M2) poate avea multe zecimale; fara asta
    ele ajung brute in raspunsul API. (Motorul ramane exact: rotunjim doar la marginea de iesire.)"""
    return str(v.quantize(_BANI, rounding=ROUND_HALF_UP))


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/grila-teren")
    def grila_teren(req: GrilaTerenRequest) -> dict:
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)   # acelasi config ca /calcul
        try:
            r = evaluate_land(req.comparabile, req.suprafata_subiect, cfg)
            return {
                "preturi_mp_corectate": [str(p) for p in r.preturi_mp_corectate],
                "ajustari_brute": [str(b) for b in r.ajustari_brute],
                "ajustari_nete": [str(n) for n in r.ajustari_nete],
                "index_selectat": r.index_selectat,
                "indici_mediati": r.indici_mediati,
                "pret_mp_ales": _bani(r.pret_mp_ales),   # rata €/mp mediata (M2) -> rotunjita la bani in API
                "valoare_teren": _bani(r.valoare_teren),
            }
        except (ValueError, ArithmeticError) as e:   # ArithmeticError: input degenerat (subnormal/urias)
            raise HTTPException(status_code=422, detail=_DETALIU_INVALID.format(e=e)) from e

    @router.post("/api/grila-casa")
    def grila_casa(req: GrilaCasaRequest) -> dict:
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)   # acelasi config ca /calcul (M2/M1)
        try:
            r = evaluate_market(req.comparabile, req.suprafata_subiect, cfg)
            return {
                "preturi_unitare_corectate": [str(p) for p in r.preturi_unitare_corectate],
                "ajustari_brute": [str(b) for b in r.ajustari_brute],
                "ajustari_nete": [str(n) for n in r.ajustari_nete],
                "index_selectat": r.index_selectat,
                "indici_mediati": r.indici_mediati,
                "valoare_piata": _bani(r.valoare_piata),
            }
        except (ValueError, ArithmeticError) as e:
            raise HTTPException(status_code=422, detail=_DETALIU_INVALID.format(e=e)) from e

    @router.post("/api/grila-chirii")
    def grila_chirii(req: GrilaChiriiRequest) -> dict:
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)   # acelasi config ca /calcul (M2)
        try:
            r = evalueaza_chirie(req.comparabile, req.suprafata_subiect, cfg)
            return {
                "chirii_mp_corectate": [str(p) for p in r.chirii_mp_corectate],
                "ajustari_brute": [str(b) for b in r.ajustari_brute],
                "ajustari_nete": [str(n) for n in r.ajustari_nete],
                "index_selectat": r.index_selectat,
                "indici_mediati": r.indici_mediati,
                # Rotunjim TOATE iesirile monetare la bani: chirie_lunara/vbp sunt deja quantizate engine-side,
                # dar chirie_mp_aleasa (rata €/mp mediata M2) iesea cu multe zecimale; _bani pe toate =
                # consistent + robust (valorile ajung in wizard via localStorage 'vbp_din_grila').
                "chirie_mp_aleasa": _bani(r.chirie_mp_aleasa),
                "chirie_lunara": _bani(r.chirie_lunara),
                "venit_brut_potential": _bani(r.venit_brut_potential),
            }
        except (ValueError, ArithmeticError) as e:
            raise HTTPException(status_code=422, detail=_DETALIU_INVALID.format(e=e)) from e

    @router.get("/grila", response_class=HTMLResponse)
    def pagina_grila(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "grila.html", {})

    return router
