"""UI-ul NOU (versiunea curentă, output-first): cont local + ÎNCEPE + workspace dosar.

Refolosește API-ul existent (calcul/raport) dar stochează dosarele pe FOLDERE (dosare_fs),
nu în SQLite. Vezi docs/specs/1-ui-output-first.md.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from evaluare import cont as cont_mod
from evaluare import dosare_fs as fs
from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.report.generator import genereaza_raport
from evaluare.web.deps import DOCX_MIME, Deps
from evaluare.web.schemas import ContRequest, DosarNouRequest, ImportDocxRequest


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    # ── Cont ─────────────────────────────────────────────────────────────────────
    @router.get("/cont", response_class=HTMLResponse)
    def pagina_cont(request: Request) -> HTMLResponse:
        from evaluare.master_config import CAMPURI_NUME_DOSAR
        return d.templates.TemplateResponse(request, "curent/cont.html",
            {"cont": cont_mod.incarca_cont(), "campuri": CAMPURI_NUME_DOSAR})

    @router.post("/api/cont")
    def creeaza_cont(req: ContRequest) -> dict:
        if not req.nume.strip() or not req.legitimatie.strip():
            raise HTTPException(422, "Nume și legitimație obligatorii.")
        return cont_mod.salveaza_cont(req.nume, req.legitimatie, req.format_dosar or None)

    # ── ÎNCEPE (homepage) ────────────────────────────────────────────────────────
    @router.get("/incepe", response_class=HTMLResponse)
    def pagina_incepe(request: Request) -> HTMLResponse:
        cont = cont_mod.incarca_cont()
        diff = fs.diff() if cont else {"existente": [], "noi": [], "disparute": []}
        return d.templates.TemplateResponse(request, "curent/incepe.html",
            {"cont": cont, "diff": diff})

    # ── Dosar (workspace) ────────────────────────────────────────────────────────
    @router.post("/api/dosar")
    def creeaza_dosar(req: DosarNouRequest) -> dict:
        cont = cont_mod.incarca_cont()
        if cont is None:
            raise HTTPException(403, "Creează întâi un cont.")
        uid = fs.creeaza(cont["legitimatie"], cont["nume"], req.wizard,
                         format_dosar=cont.get("format_dosar"))
        return {"uuid": uid}

    @router.post("/api/dosar/import-docx")
    def import_docx(req: ImportDocxRequest) -> dict:
        """Importă un raport .docx ca dosar nou: pre-completează câmpurile + atașează fișierul."""
        import base64
        import shutil
        import uuid as _uuid

        from evaluare.importers.docx_dosar import extrage_din_docx
        cont = cont_mod.incarca_cont()
        if cont is None:
            raise HTTPException(403, "Creează întâi un cont.")
        payload = req.continut.split(",", 1)[1] if req.continut.startswith("data:") else req.continut
        try:
            raw = base64.b64decode(payload, validate=True)
        except Exception:
            raise HTTPException(400, "Conținut fișier invalid.") from None
        # director temporar UNIC per import: evită coliziuni + `.name` taie orice path traversal,
        # iar numele original e păstrat (extrage_din_docx parsează identitatea DIN numele fișierului).
        tmpdir = Path(tempfile.gettempdir()) / f"anevar-import-{_uuid.uuid4().hex}"
        tmpdir.mkdir(parents=True, exist_ok=True)
        try:
            tmp = tmpdir / (Path(req.nume_fisier).name or "import.docx")
            tmp.write_bytes(raw)
            wizard = extrage_din_docx(tmp)
            uid = fs.creeaza(cont["legitimatie"], cont["nume"], wizard,
                             format_dosar=cont.get("format_dosar"))
            fs.adauga_versiune_docx(uid, tmp)          # atașează raportul sursă
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        return {"uuid": uid, "wizard": wizard}

    @router.get("/dosar/{uid}", response_class=HTMLResponse)
    def pagina_dosar(request: Request, uid: str) -> HTMLResponse:
        try:
            dosar = fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        return d.templates.TemplateResponse(request, "curent/dosar.html",
            {"dosar": dosar, "cont": cont_mod.incarca_cont()})

    @router.get("/api/dosar/{uid}")
    def citeste_dosar(uid: str) -> dict:
        try:
            return fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None

    @router.post("/api/dosar/{uid}/salveaza")
    def salveaza_dosar(uid: str, wizard: dict) -> dict:
        try:
            fs.salveaza_wizard(uid, wizard)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        return {"ok": True}

    @router.post("/api/dosar/{uid}/sterge")
    def sterge_dosar(uid: str) -> dict:
        fs.sterge(uid)
        return {"ok": True}

    @router.post("/api/dosar/{uid}/scoate-din-index")
    def scoate_din_index(uid: str) -> dict:
        """Scoate un dosar DISPĂRUT (folder șters de pe disc) din indexul «ultima vedere»."""
        fs.sterge_din_index(uid)
        return {"ok": True}

    @router.post("/api/dosar/{uid}/calcul")
    def calcul(uid: str, inp: EvaluationInput) -> dict:
        """Calcul fără persistență în SQLite (dosarele noi se salvează pe foldere, nu în baza veche).

        UI-ul nou folosea /api/evaluare, care scria un rând orfan în SQLite la FIECARE «Calculează».
        """
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        ctx = construieste_context(inp, client=d.client)
        return {
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
            "alerte": [a.model_dump() for a in valideaza(inp)],
        }

    @router.post("/api/dosar/{uid}/raport.docx")
    def genereaza(uid: str, inp: EvaluationInput) -> FileResponse:
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        ctx = construieste_context(inp, client=d.client)
        out = Path(tempfile.gettempdir()) / f"raport_{uid}.docx"
        genereaza_raport(ctx, out, adnotari=False)
        fs.adauga_versiune_docx(uid, out)              # versiune în folderul dosarului
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"raport_{uid[:8]}.docx")

    return router
