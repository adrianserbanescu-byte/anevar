"""Pagini HTML generale: index (wizard), formular clasic, wizard."""
from __future__ import annotations

import csv
import io
import time

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from evaluare import __version__
from evaluare.web.deps import Deps
from evaluare.web.schemas import FeedbackRequest


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

    @router.get("/", response_class=HTMLResponse)
    def pagina_index(request: Request) -> HTMLResponse:
        # Pagina principala = wizard-ul ghidat pas-cu-pas.
        return d.templates.TemplateResponse(request, "wizard.html", {})

    @router.get("/formular", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        # Formularul monolit (toate campurile pe o pagina), alternativa la wizard.
        return d.templates.TemplateResponse(request, "form.html", {})

    @router.get("/wizard", response_class=HTMLResponse)
    def pagina_wizard(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "wizard.html", {})

    # ── Feedback de la testeri (local, offline; opțional și Google Forms din widget) ──
    @router.post("/api/feedback")
    def trimite_feedback(req: FeedbackRequest) -> dict:
        if not req.mesaj.strip() and not req.sentiment.strip():
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="Scrie un mesaj sau alege o reacție.")
        total = d.storage.adauga_feedback(req.model_dump())
        return {"ok": True, "total": total}

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
