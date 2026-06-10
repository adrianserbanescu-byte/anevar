"""Dosare de evaluare: creare, citire, raport .docx, audit + pagina de rezultat."""
from __future__ import annotations

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from evaluare.assembler import (
    EvaluationInput,
    construieste_context,
    valideaza,
    valideaza_din_context,
    valoare_imposibila,
)
from evaluare.logging_setup import get_logger
from evaluare.report.generator import genereaza_raport
from evaluare.web.deps import DOCX_MIME, Deps
from evaluare.web.format import fmt_numar
from evaluare.web.schemas import RedenumesteRequest

log = get_logger(__name__)


def _folder_dosar(eid: int) -> Path:
    """Folderul dedicat unui dosar (versiuni .docx), lângă datele aplicației."""
    out = os.environ.get("OUTPUT_DIR") or "date"
    return Path(out) / "dosare" / str(eid)


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/evaluare")
    def creeaza_evaluare(inp: EvaluationInput) -> dict:
        from evaluare.audit.validare_x import valideaza_incrucisat
        from evaluare.engine import metodologie_store
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)   # acelasi config ca UI-ul nou
        try:
            ctx = construieste_context(inp, client=d.client, cfg=cfg)
        except (ValueError, ArithmeticError) as e:
            raise HTTPException(422, f"Date insuficiente sau invalide pentru calcul: {e}") from e
        # NU persista o valoare matematic imposibila (finala <=0 / pret corectat <=0): decizia owner
        # 2026-06-10 — garda de valoare se aplica si la persistenta, nu doar la raport. Blocajele de
        # DATE raman advisory (returnate in `alerte`). Vezi assembler.valoare_imposibila.
        invalide = valoare_imposibila(ctx)
        if invalide:
            raise HTTPException(422, "Calcul invalid (valoare imposibila): "
                                + "; ".join(i.mesaj for i in invalide))
        eid = d.storage.save(ctx)
        alerte = [a.model_dump() for a in valideaza(inp, cfg)]
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
            raise HTTPException(
                status_code=404,
                detail="Dosarul nu există sau a fost șters (cod 404). Verifică ID-ul în lista de dosare la /dosare.",
            ) from None
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
            raise HTTPException(
                status_code=404,
                detail="Dosarul nu există sau a fost șters (cod 404). Verifică ID-ul în lista de dosare la /dosare.",
            ) from None
        # Documentul OFICIAL nu se genereaza pe date blocante — PARITATE cu endpointul nou
        # /api/dosar/{uid}/raport.docx (re-audit I1). Aici nu mai avem inputul brut (dosarul vine din
        # storage), deci rulam validatorii pe CONTEXT (valideaza_din_context) + validarea incrucisata
        # (ex. valoare finala <=0). Apara si dosarele LEGACY deja persistate cu valoare imposibila.
        from evaluare.audit.validare_x import valideaza_incrucisat
        from evaluare.engine import metodologie_store
        cfg = metodologie_store.config_efectiv(d.storage.db_path.parent)
        blocante = [i for i in valideaza_din_context(ctx, cfg) if i.nivel == "blocheaza"]
        blocante += [i for i in valideaza_incrucisat(ctx) if i.nivel == "blocheaza"]
        if blocante:
            raise HTTPException(422, "Raport blocat: corectati problemele blocante inainte de generare — "
                                + "; ".join(i.mesaj for i in blocante))
        # ?demo=1 -> raport cu note de provenienta (calculat/extras/AI/exemplu/placeholder)
        sufix = "_demo" if demo else ""
        out = Path(tempfile.gettempdir()) / f"raport_{eid}{sufix}.docx"
        genereaza_raport(ctx, out, adnotari=bool(demo))
        # Versionare: salvează o copie datată în folderul dosarului (doar raportul real).
        if not demo:
            folder = _folder_dosar(eid)
            try:
                folder.mkdir(parents=True, exist_ok=True)
                shutil.copy(out, folder / f"raport-{datetime.now():%Y%m%d-%H%M%S}.docx")
            except OSError:
                pass                                       # versionarea nu blochează descărcarea
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"raport_{eid}{sufix}.docx")

    @router.post("/api/evaluare/{eid}/redenumeste")
    def redenumeste_dosar(eid: int, req: RedenumesteRequest) -> dict:
        d.storage.redenumeste(eid, req.nume.strip() or "Dosar")
        return {"ok": True}

    @router.post("/api/evaluare/{eid}/snapshot")
    def salveaza_snapshot(eid: int, snapshot: dict) -> dict:
        d.storage.set_wizard_snapshot(eid, snapshot)
        return {"ok": True}

    @router.get("/api/evaluare/{eid}/dosar")
    def citeste_dosar(eid: int) -> dict:
        try:
            return d.storage.get_dosar(eid)
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Dosarul nu există (cod 404). Verifică ID-ul în lista de dosare la /dosare.",
            ) from None

    @router.post("/api/evaluare/{eid}/sterge")
    def sterge_dosar(eid: int) -> dict:
        d.storage.sterge(eid)
        shutil.rmtree(_folder_dosar(eid), ignore_errors=True)
        return {"ok": True}

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
            raise HTTPException(
                status_code=404,
                detail="Dosarul nu există sau a fost șters (cod 404). Verifică ID-ul în lista de dosare la /dosare.",
            ) from None
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

    @router.get("/api/backup.db")
    def descarca_backup() -> FileResponse:
        copie = d.storage.backup(Path(tempfile.gettempdir()) / "anevar_backup", keep=3)
        if copie is None:
            raise HTTPException(
                status_code=404,
                detail="Nu există încă dosare de salvat (cod 404). Creează unul la /incepe înainte de backup.",
            )
        return FileResponse(str(copie), media_type="application/octet-stream", filename=copie.name)

    @router.get("/evaluare/{eid}", response_class=HTMLResponse)
    def pagina_rezultat(request: Request, eid: int) -> HTMLResponse:
        try:
            ctx = d.storage.load(eid)
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail="Dosarul nu există sau a fost șters (cod 404). Verifică ID-ul în lista de dosare la /dosare.",
            ) from None
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
