"""Pagini HTML generale: index (wizard), formular clasic, wizard."""
from __future__ import annotations

import csv
import io
import os
import time
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response

from evaluare import __version__
from evaluare.logging_setup import get_logger
from evaluare.web.deps import Deps
from evaluare.web.schemas import FeedbackRequest

log = get_logger(__name__)


def _fisier_feedback() -> Path:
    """Fișierul CSV de feedback, LÂNGĂ executabil (parent-ul OUTPUT_DIR), per zi.

    În .exe, __main__ setează OUTPUT_DIR = <folder-exe>/date -> fișierul ajunge în
    folderul exe-ului (ușor de găsit/trimis). În dezvoltare, lângă directorul curent.
    """
    out = os.environ.get("OUTPUT_DIR")
    baza = Path(out).resolve().parent if out else Path.cwd()
    return baza / ("feedback-" + datetime.now().strftime("%Y-%m-%d") + ".csv")


def _scrie_feedback_fisier(fb: FeedbackRequest) -> str:
    """Adaugă o linie în fișierul CSV de feedback de lângă exe. Returnează numele fișierului."""
    f = _fisier_feedback()
    try:
        f.parent.mkdir(parents=True, exist_ok=True)
        nou = not f.exists()
        with f.open("a", encoding="utf-8-sig", newline="") as fh:
            w = csv.writer(fh)
            if nou:
                w.writerow(["data", "pagina", "reactie", "mesaj", "tester", "url"])
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fb.pagina,
                        fb.sentiment, fb.mesaj, fb.tester, fb.url])
    except OSError as e:                                    # disc plin/permisiuni -> nu blocăm
        log.warning("Nu pot scrie fișierul de feedback (%s): %s", f, e)
    return f.name


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()
    pornit_la = time.time()

    @router.get("/api/status")
    def status() -> dict:
        """Stare aplicație: versiune + uptime. Folosit de popup-ul extensiei pentru ping."""
        return {
            "ok": True,
            "versiune": __version__,
            "uptime_secunde": round(time.time() - pornit_la, 1),
            "anunturi_in_coada": len(d.storage.listeaza_anunturi_importate()),
        }

    @router.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        # Siglă casă-pe-albastru (SVG inline) — evită 404-ul de favicon pe toate paginile.
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect width="24" height="24" rx="4" fill="#1f3a5f"/>'
            '<path d="M5 11.5 12 6l7 5.5V19H5z" fill="none" stroke="#f3efe5" '
            'stroke-width="1.5" stroke-linejoin="round"/>'
            '<path d="M10 19v-4h4v4" fill="none" stroke="#f3efe5" stroke-width="1.5"/></svg>'
        )
        return Response(content=svg, media_type="image/svg+xml",
                        headers={"Cache-Control": "public, max-age=86400"})

    @router.get("/", include_in_schema=False)
    def pagina_index() -> RedirectResponse:
        # Logica de start (decizie Adi 2026-06-08): prima oara -> definirea userului (/cont);
        # daca userul e deja definit -> direct in workspace (/incepe). Alegerea de interfata: /alege.
        from evaluare import cont as cont_mod
        tinta = "/incepe" if cont_mod.incarca_cont() is not None else "/cont"
        return RedirectResponse(tinta)

    @router.get("/alege", response_class=HTMLResponse)
    def pagina_alege(request: Request) -> HTMLResponse:
        # Alegerea interfetei (UI nou: Flux livrabile vs Homepage nou). Mutata de pe „/" (acum redirect).
        return d.templates.TemplateResponse(request, "index.html", {})

    @router.get("/documente", response_class=HTMLResponse)
    def pagina_documente(request: Request) -> HTMLResponse:
        from itertools import groupby

        from evaluare import documente as docs
        lista = docs.listeaza()
        grupuri = {k: list(v) for k, v in groupby(lista, key=lambda d: d["categorie"])}
        return d.templates.TemplateResponse(request, "documente.html",
            {"documente": lista, "grupuri": grupuri})

    @router.get("/documente/{slug}", response_class=HTMLResponse)
    def pagina_document(request: Request, slug: str) -> HTMLResponse:
        from fastapi import HTTPException

        from evaluare import documente as docs
        try:
            meta, continut = docs.incarca(slug)
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail=f"Documentul „{slug}” nu există (cod 404). Vezi lista completă la /documente.",
            ) from None
        return d.templates.TemplateResponse(request, "document.html",
            {"meta": meta, "continut": continut})

    @router.get("/formular", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        # Formularul monolit (toate campurile pe o pagina), alternativa la wizard.
        return d.templates.TemplateResponse(request, "form.html", {})

    @router.get("/wizard", response_class=HTMLResponse)
    def pagina_wizard(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "wizard.html", {})

    @router.get("/flux-livrabile", response_class=HTMLResponse)
    def pagina_flux_livrabile(request: Request) -> HTMLResponse:
        """Hartă de proces: ce livrabile produce un dosar, pe 3 niveluri legale (firmă/client/eveniment)."""
        return d.templates.TemplateResponse(request, "flux_livrabile.html", {})

    @router.get("/dosare", response_class=HTMLResponse)
    def pagina_dosare(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "dosare.html",
            {"dosare": d.storage.list()})

    # ── Feedback de la testeri (local, offline; opțional și Google Forms din widget) ──
    @router.post("/api/feedback")
    def trimite_feedback(req: FeedbackRequest) -> dict:
        if not req.mesaj.strip() and not req.sentiment.strip():
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="Scrie un mesaj sau alege o reacție.")
        total = d.storage.adauga_feedback(req.model_dump())
        fisier = _scrie_feedback_fisier(req)               # și ca fișier lângă exe
        return {"ok": True, "total": total, "fisier": fisier}

    @router.get("/api/feedback")
    def lista_feedback() -> dict:
        return {"feedback": d.storage.listeaza_feedback()}

    @router.get("/api/feedback.csv")
    def feedback_csv() -> PlainTextResponse:
        rows = d.storage.listeaza_feedback()
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "data", "pagina", "url", "reactie", "mesaj", "tester"])
        for r in rows:
            w.writerow([r["id"], r["creat_la"], r["pagina"], r["url"],
                        r["sentiment"], r["mesaj"], r["tester"]])
        return PlainTextResponse(buf.getvalue(), media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=feedback.csv"})

    @router.get("/feedback", response_class=HTMLResponse)
    def pagina_feedback(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "feedback_list.html",
            {"feedback": d.storage.listeaza_feedback()})

    return router
