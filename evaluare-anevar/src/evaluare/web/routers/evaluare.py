"""Dosare de evaluare: creare, citire, raport .docx, audit + pagina de rezultat."""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.report.generator import genereaza_raport
from evaluare.web.deps import DOCX_MIME, Deps
from evaluare.web.format import fmt_numar


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/evaluare")
    def creeaza_evaluare(inp: EvaluationInput) -> dict:
        from evaluare.audit.validare_x import valideaza_incrucisat
        ctx = construieste_context(inp, client=d.client)
        eid = d.storage.save(ctx)
        alerte = [a.model_dump() for a in valideaza(inp)]
        alerte += [a.model_dump() for a in valideaza_incrucisat(ctx)]  # validare incrucisata (audit)
        return {
            "id": eid,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
            "alerte": alerte,
        }

    @router.get("/api/evaluare/{eid}")
    def citeste_evaluare(eid: int) -> dict:
        try:
            ctx = d.storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.") from None
        return {
            "id": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        }

    @router.get("/api/evaluare/{eid}/raport.docx")
    def descarca_raport(eid: int, demo: int = 0) -> FileResponse:
        try:
            ctx = d.storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.") from None
        # ?demo=1 -> raport cu note de provenienta (calculat/extras/AI/exemplu/placeholder)
        sufix = "_demo" if demo else ""
        out = Path(tempfile.gettempdir()) / f"raport_{eid}{sufix}.docx"
        genereaza_raport(ctx, out, adnotari=bool(demo))
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"raport_{eid}{sufix}.docx")

    @router.get("/api/evaluare/{eid}/audit.txt")
    def audit_dosar(eid: int):
        from fastapi.responses import PlainTextResponse

        from evaluare.audit.jurnal import JurnalAudit
        from evaluare.audit.raport_audit import text_audit
        from evaluare.audit.snapshot import snapshot
        from evaluare.audit.validare_x import valideaza_incrucisat
        try:
            ctx = d.storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.") from None
        j = JurnalAudit()
        j.inregistreaza("identificare", {"adresa": ctx.meta.adresa,
                                         "cadastral": ctx.meta.numar_cadastral, "scop": ctx.meta.scop})
        j.inregistreaza("input_proprietate", {"hash": snapshot({
            "land": ctx.land.model_dump(mode="json"),
            "building": ctx.building.model_dump(mode="json")})["hash"]})
        j.inregistreaza("comparabile", {"casa": len(ctx.comparables),
                                        "teren": len(ctx.land_comparables)})
        if ctx.market_result is not None:
            j.inregistreaza("rezultat_piata", {"valoare": str(ctx.market_result.valoare_piata)})
        if ctx.cost_result is not None:
            j.inregistreaza("rezultat_cost", {"valoare": str(ctx.cost_result.valoare_cost)})
        if ctx.land_result is not None:
            j.inregistreaza("rezultat_teren", {"valoare": str(ctx.land_result.valoare_teren)})
        j.inregistreaza("valoare_finala", {"valoare": str(ctx.reconciled.valoare_finala),
                                           "metoda": ctx.reconciled.metoda_selectata})
        for issue in valideaza_incrucisat(ctx):
            j.inregistreaza("validare_incrucisata", {"nivel": issue.nivel, "mesaj": issue.mesaj})
        return PlainTextResponse(text_audit(j))

    @router.get("/evaluare/{eid}", response_class=HTMLResponse)
    def pagina_rezultat(request: Request, eid: int) -> HTMLResponse:
        try:
            ctx = d.storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.") from None
        val = ctx.reconciled.valoare_finala
        moneda = (ctx.meta.moneda or "LEI").upper()
        curs = ctx.meta.curs_valutar
        echiv = None
        if curs:
            if moneda == "LEI":
                echiv = fmt_numar(val / curs) + " EUR"
            elif moneda == "EUR":
                echiv = fmt_numar(val * curs) + " LEI"
        return d.templates.TemplateResponse(request, "result.html", {
            "eid": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_fmt": fmt_numar(val),
            "moneda": moneda,
            "echiv": echiv,
            "metoda": ctx.reconciled.metoda_selectata,
        })

    return router
