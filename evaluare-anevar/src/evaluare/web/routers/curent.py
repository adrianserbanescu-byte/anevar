"""UI-ul NOU (versiunea curentă, output-first): cont local + ÎNCEPE + workspace dosar.

Refolosește API-ul existent (calcul/raport) dar stochează dosarele pe FOLDERE (dosare_fs),
nu în SQLite. Vezi docs/specs/1-ui-output-first.md.
"""
from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from evaluare import cont as cont_mod
from evaluare import dosare_fs as fs
from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.report.generator import genereaza_raport
from evaluare.report.pdf import PdfIndisponibil
from evaluare.web.deps import DOCX_MIME, Deps
from evaluare.web.schemas import ContRequest, DosarNouRequest, ImportDocxRequest


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    def _context(inp: EvaluationInput):
        """Construiește contextul; erorile de date (ex. depreciere goală la cost) → 422 clar, nu 500."""
        try:
            return construieste_context(inp, client=d.client)
        except ValueError as e:
            raise HTTPException(422, f"Date insuficiente sau invalide pentru calcul: {e}") from e

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
        import os
        from evaluare.master_config import CAMPURI_NUME_DOSAR
        cont = cont_mod.incarca_cont()
        diff = fs.diff() if cont else {"existente": [], "noi": [], "disparute": []}
        # Flag commercial: pe build offline = False (ascunde teasere comerciale per decizia #15).
        # Setezi env var ANEVAR_COMMERCIAL_BUILD=1 când construiești varianta cu gateway online (§B.7).
        commercial_build = os.environ.get("ANEVAR_COMMERCIAL_BUILD") == "1"
        return d.templates.TemplateResponse(request, "curent/incepe.html",
            {"cont": cont, "diff": diff, "campuri": CAMPURI_NUME_DOSAR,
             "commercial_build": commercial_build})

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
        if len(payload) > 35_000_000:            # ~26 MB după decodare — limită anti-DoS
            raise HTTPException(413, "Fișier prea mare (limită ~25 MB).")
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
            wizard = extrage_din_docx(tmp)   # robust: docx ilizibil -> degradează la parsarea numelui
            uid = fs.creeaza(cont["legitimatie"], cont["nume"], wizard,
                             format_dosar=cont.get("format_dosar"))
            fs.adauga_versiune_docx(uid, tmp, tip="import")   # atașează raportul sursă (nu „asumat")
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
        ctx = _context(inp)
        return {
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
            "alerte": [a.model_dump() for a in valideaza(inp)],
        }

    @router.post("/api/dosar/{uid}/audit.txt")
    def audit_dosar(uid: str, inp: EvaluationInput):
        """Urma de audit (jurnal hash + validare încrucișată) pt fluxul pe foldere (fără SQLite)."""
        from fastapi.responses import PlainTextResponse

        from evaluare.audit.jurnal import JurnalAudit
        from evaluare.audit.raport_audit import text_audit
        from evaluare.audit.snapshot import snapshot
        from evaluare.audit.validare_x import valideaza_incrucisat
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        ctx = _context(inp)
        j = JurnalAudit()
        j.inregistreaza("identificare", {"adresa": ctx.meta.adresa,
                                         "cadastral": ctx.meta.numar_cadastral, "scop": ctx.meta.scop})
        j.inregistreaza("input_proprietate", {"hash": snapshot({
            "land": ctx.land.model_dump(mode="json"),
            "building": ctx.building.model_dump(mode="json")})["hash"]})
        j.inregistreaza("comparabile", {"casa": len(ctx.comparables), "teren": len(ctx.land_comparables)})
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
        for v in fs.verifica_integritate(uid):   # ADR-003: integritatea versiunilor .docx asumate
            j.inregistreaza("integritate_versiune", {"fisier": v["fisier"], "asumat_la": v["la"],
                                                     "tip": v["tip"], "integru": v["ok"]})
        return PlainTextResponse(text_audit(j))

    @router.post("/api/dosar/{uid}/raport.docx")
    def genereaza(uid: str, inp: EvaluationInput, adnotari: int = 0, fmt: str = "docx") -> FileResponse:
        """Generează raportul. `fmt` ∈ {docx (implicit), pdf, ambele}. PDF necesită LibreOffice/Word local."""
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        ctx = _context(inp)
        tmp = Path(tempfile.gettempdir())
        out = tmp / f"raport_{uid}.docx"
        genereaza_raport(ctx, out, adnotari=bool(adnotari))   # adnotări = note de proveniență (review)
        fs.adauga_versiune_docx(uid, out)              # versiune .docx persistentă (canonică) în folderul dosarului
        from starlette.background import BackgroundTask

        def _sterge(*cai):   # igienă PII: copiile temporare se șterg după trimitere
            return BackgroundTask(lambda: [Path(c).unlink(missing_ok=True) for c in cai])

        nume = f"raport_{uid[:8]}"
        formate = (fmt or "docx").lower()
        if formate == "docx":
            return FileResponse(str(out), media_type=DOCX_MIME, filename=f"{nume}.docx",
                                background=_sterge(out))
        # pdf / ambele -> conversie cu convertorul de pe stația evaluatorului (LibreOffice/Word)
        try:
            pdf = d.pdf_converter(out)
        except PdfIndisponibil as e:
            out.unlink(missing_ok=True)
            raise HTTPException(422, "PDF indisponibil pe această stație: instalează LibreOffice "
                                "(gratuit) sau Microsoft Word. Documentul .docx a fost generat și "
                                "salvat ca versiune în dosar.") from e
        if formate == "pdf":
            return FileResponse(str(pdf), media_type="application/pdf", filename=f"{nume}.pdf",
                                background=_sterge(out, pdf))
        zpath = tmp / f"raport_{uid}.zip"   # „ambele" -> arhivă cu .docx + .pdf
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(out, f"{nume}.docx")
            z.write(pdf, f"{nume}.pdf")
        return FileResponse(str(zpath), media_type="application/zip", filename=f"{nume}.zip",
                            background=_sterge(out, pdf, zpath))

    @router.post("/api/dosar/{uid}/incarca-submis")
    def incarca_submis(uid: str, req: ImportDocxRequest) -> dict:
        """ADR-003 (trigger #3, decizia Adi #10): încarcă un .docx SUBMIS (raport finalizat returnat de
        bancă/client) în dosar → versiune cu hash de integritate + marchează identitatea ca asumată."""
        import base64
        import shutil
        import uuid as _uuid
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        payload = req.continut.split(",", 1)[1] if req.continut.startswith("data:") else req.continut
        if len(payload) > 35_000_000:
            raise HTTPException(413, "Fișier prea mare (limită ~25 MB).")
        try:
            raw = base64.b64decode(payload, validate=True)
        except Exception:
            raise HTTPException(400, "Conținut fișier invalid.") from None
        tmpdir = Path(tempfile.gettempdir()) / f"anevar-submis-{_uuid.uuid4().hex}"
        tmpdir.mkdir(parents=True, exist_ok=True)
        try:
            tmp = tmpdir / (Path(req.nume_fisier).name or "submis.docx")
            tmp.write_bytes(raw)
            versiune = fs.adauga_versiune_docx(uid, tmp, tip="submis")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
        return {"versiune": versiune, "asumat_la": fs.incarca(uid).get("asumat_la")}

    @router.get("/api/__sentinel_build__")
    def _sentinel_build() -> dict:
        return {"v": "adr-build-2026-06-07"}

    @router.get("/api/backup-dosare.zip")
    def backup_dosare():
        """Backup: arhivează TOATE dosarele (folderul OUTPUT_DIR/dosare) într-un .zip descărcabil."""
        import io
        import zipfile

        from fastapi.responses import StreamingResponse
        baza = fs.baza()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            if baza.exists():
                for p in baza.rglob("*"):
                    if p.is_file():
                        z.write(p, p.relative_to(baza.parent))
        buf.seek(0)
        return StreamingResponse(buf, media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=backup-dosare.zip"})

    return router
