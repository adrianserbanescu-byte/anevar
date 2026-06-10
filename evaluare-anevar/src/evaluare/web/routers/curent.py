"""UI-ul NOU (versiunea curentă, output-first): cont local + ÎNCEPE + workspace dosar.

Refolosește API-ul existent (calcul/raport) dar stochează dosarele pe FOLDERE (dosare_fs),
nu în SQLite. Vezi docs/specs/1-ui-output-first.md.
"""
from __future__ import annotations

import contextlib
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse

from evaluare import cont as cont_mod
from evaluare import dosare_fs as fs
from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.engine import metodologie_store
from evaluare.engine.metodologie import ca_dict
from evaluare.logging_setup import get_logger
from evaluare.report.generator import genereaza_raport
from evaluare.web.deps import DOCX_MIME, Deps
from evaluare.web.schemas import ContRequest, DosarNouRequest, ImportDocxRequest

log = get_logger(__name__)


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    def _metodologie_cfg():
        """Config de metodologie efectiv (default + override-ul evaluatorului persistat local)."""
        return metodologie_store.config_efectiv(d.storage.db_path.parent)

    def _context(inp: EvaluationInput):
        """Construiește contextul; erorile de date (ex. depreciere goală la cost) → 422 clar, nu 500."""
        try:
            return construieste_context(inp, client=d.client, cfg=_metodologie_cfg())
        except (ValueError, ArithmeticError) as e:   # ArithmeticError: ex. rotunjire degenerata -> 422, nu 500
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

    # ── Setări (vizualizare + editare cont, accesibil din nav; cerere Adi/batch) ──────
    @router.get("/setari", response_class=HTMLResponse)
    def pagina_setari(request: Request) -> HTMLResponse:
        from evaluare.master_config import CAMPURI_NUME_DOSAR
        return d.templates.TemplateResponse(request, "curent/setari.html",
            {"cont": cont_mod.incarca_cont(), "campuri": CAMPURI_NUME_DOSAR})

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
            log.warning("creeaza_dosar: cont absent")
            raise HTTPException(403, "Creează întâi un cont.")
        uid = fs.creeaza(cont["legitimatie"], cont["nume"], req.wizard,
                         format_dosar=cont.get("format_dosar"))
        # igiena PII (audit #9): logam legitimatia (ID profesional), nu numele evaluatorului
        log.info("dosar creat uid=%s creator_leg=%s", uid, cont.get("legitimatie", "?"))
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
        # `and "," in ...`: data-URL fara virgula ("data:") ramane intreg -> b64decode il respinge
        # (400 clar) in loc de IndexError pe [1] -> 500 (aceeasi clasa RUNDA 9 ca /api/ingestie).
        payload = (req.continut.split(",", 1)[1]
                   if req.continut.startswith("data:") and "," in req.continut else req.continut)
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
            {"dosar": dosar, "cont": cont_mod.incarca_cont(),
             "blocat": fs.este_blocat(dosar), "asumat_la": dosar.get("asumat_la")})

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
        try:
            fs.sterge(uid)                      # _cale() refuza uid non-UUID (anti path-traversal)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        log.info("dosar sters uid=%s", uid)
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
        # valideaza() era IN AFARA garzii _context -> date degenerate ridicau 500; o aducem sub
        # aceeasi protectie 422 (audit B). gt=0 pe comparabile prinde deja suprafata/pret=0 la parsare.
        try:
            alerte = [a.model_dump() for a in valideaza(inp, _metodologie_cfg())]
        except (ValueError, ArithmeticError) as e:
            raise HTTPException(422, f"Date insuficiente sau invalide pentru calcul: {e}") from e
        return {
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
            "alerte": alerte,
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
        for db in fs.incarca(uid).get("deblocari", []):   # ADR-003: deblocări de identitate (corecturi tipografice)
            j.inregistreaza("deblocare_identitate", {"la": db.get("la"), "motiv": db.get("motiv")})
        return PlainTextResponse(text_audit(j))

    @router.post("/api/dosar/{uid}/raport.docx")
    def genereaza(uid: str, inp: EvaluationInput, adnotari: int = 0) -> FileResponse:
        """Generează raportul .docx. App-ul NU mai produce PDF (decizie 2026-06-08): evaluatorul
        verifică documentul și îl exportă manual ca PDF — răspunderea versiunii finale e a lui.
        Convertorul docx→PDF rămâne în cod (report/pdf.py), dormant, dar nu mai e apelat de aici.

        Per decizia #14 (2026-06-07): Genereaza CERE Calcul reușit. _context() invocă
        construieste_context() — aceeași cale ca /api/dosar/{uid}/calcul. Date insuficiente → 422
        clar prin _context. Single source of truth: nu poți genera raport fără calcul valid.
        """
        try:
            fs.incarca(uid)
        except KeyError:
            log.warning("genereaza: dosar inexistent uid=%s", uid)
            raise HTTPException(404, "Dosar inexistent.") from None
        log.info("genereaza raport uid=%s adnotari=%s", uid, bool(adnotari))
        ctx = _context(inp)  # 422 daca calcul nu poate fi facut (decizia #14)
        # Enforce nivel="blocheaza" (re-audit I1): un raport SEMNABIL de garantare NU se genereaza daca
        # exista probleme BLOCANTE (ex. comparabil cu pret corectat <=0). In /calcul ramane advisory
        # (evaluatorul vede valoarea+alerta); aici, la documentul OFICIAL, se BLOCHEAZA generarea.
        try:
            blocante = [i for i in valideaza(inp, _metodologie_cfg()) if i.nivel == "blocheaza"]
        except (ValueError, ArithmeticError):
            blocante = []
        if blocante:
            raise HTTPException(422, "Raport blocat: corectati problemele blocante inainte de generare — "
                                + "; ".join(i.mesaj for i in blocante))
        tmp = Path(tempfile.gettempdir())
        tok = uuid.uuid4().hex[:8]          # token unic: evită coliziuni la generări concurente pe același dosar
        out = tmp / f"raport_{uid}_{tok}.docx"
        genereaza_raport(ctx, out, adnotari=bool(adnotari))   # adnotări = note de proveniență (review)
        fs.adauga_versiune_docx(uid, out)              # versiune .docx persistentă (canonică) în folderul dosarului
        from starlette.background import BackgroundTask

        def _sterge(*cai):   # igienă PII: copiile temporare se șterg după trimitere
            return BackgroundTask(lambda: [Path(c).unlink(missing_ok=True) for c in cai])

        nume = f"raport_{uid[:8]}"
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"{nume}.docx",
                            background=_sterge(out))

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

    @router.post("/api/dosar/{uid}/deblocheaza")
    def deblocheaza_dosar(uid: str, body: dict) -> dict:
        """ADR-003: deblochează identitatea pentru o corectură tipografică (motiv obligatoriu → Audit)."""
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        try:
            fs.deblocheaza(uid, str(body.get("motiv", "")))
        except ValueError as e:
            raise HTTPException(422, str(e)) from e
        return {"ok": True, "blocat": False}

    @router.post("/api/dosar/{uid}/cloneaza")
    def cloneaza_dosar(uid: str) -> dict:
        """ADR-003: clonează munca tehnică într-un dosar NOU (altă identitate); sursa rămâne asumată."""
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        return {"uuid": fs.cloneaza(uid)}

    @router.post("/api/dosar/{uid}/lock")
    def lock_dosar(uid: str, body: dict) -> dict:
        """ADR-003 (item 7): marchează deschiderea + detectează editarea concurentă. Întoarce {concurent}."""
        try:
            fs.incarca(uid)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        return {"concurent": fs.marcheaza_lock(uid, str(body.get("token", "")))}

    @router.post("/api/dosar/{uid}/unlock")
    def unlock_dosar(uid: str, body: dict) -> dict:
        """ADR-003 (item 7): eliberează lock-ul la închiderea ferestrei (best-effort, sendBeacon)."""
        with contextlib.suppress(KeyError):     # uid invalid/inexistent -> nimic de eliberat (best-effort)
            fs.elibereaza_lock(uid, str(body.get("token", "")))
        return {"ok": True}

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

    @router.get("/api/metodologie-config")
    def get_metodologie_config() -> dict:
        """Configul de metodologie efectiv (default + override evaluator) — opțiunile din auditul #3."""
        return {"config": ca_dict(_metodologie_cfg()), "editabil": True}

    @router.post("/api/metodologie-config")
    def post_metodologie_config(body: dict) -> dict:
        """Salvează opțiunile de metodologie editate de evaluator (M1/M3/M5/E1). Câmpurile necunoscute
        sau cu tip invalid sunt ignorate (cad pe default) — persistă local, ca override-ul de ponderi."""
        override = body.get("config", body) if isinstance(body, dict) else {}
        salvat = metodologie_store.salveaza_override(d.storage.db_path.parent, override)
        return {"ok": True, "config": salvat, "editabil": True}

    return router
