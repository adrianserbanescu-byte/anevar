"""Aplicatia web FastAPI: compune routerele pe domenii (vezi ADR-001)."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.importers.url_parser import fetch_html
from evaluare.report.pdf import docx_to_pdf
from evaluare.web.deps import Deps
from evaluare.web.routers import aml, curent, descoperire, evaluare, grile, pagini, piata


def _build_data() -> str:
    """Data buildului = mtime-ul exe-ului PyInstaller (`sys.executable`). În dev (nefreezat): 'dev'."""
    import sys
    if getattr(sys, "frozen", False):
        from datetime import datetime
        try:
            return datetime.fromtimestamp(Path(sys.executable).stat().st_mtime).strftime("%d.%m.%Y %H:%M")
        except OSError:
            return ""
    return "dev"


def create_app(storage: Storage, client: NarrativeClient | None,
               fetcher: Callable[[str], str] = fetch_html,
               pdf_converter: Callable[[Path], Path] = docx_to_pdf) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    from fastapi.middleware.cors import CORSMiddleware
    from starlette.responses import PlainTextResponse

    from evaluare import __version__
    app = FastAPI(title="Evaluare ANEVAR")

    # Gardă anti DNS-rebinding / cross-site: aplicația locală acceptă DOAR Host local.
    # Un site vizitat (evil.com) care rezolvă la 127.0.0.1 ar trimite Host: evil.com -> respins,
    # deci nu poate șterge dosare / exfiltra PII prin API-ul local. „testserver" = host-ul TestClient.
    _HOSTURI_LOCALE = {"127.0.0.1", "localhost", "::1", "testserver"}

    @app.middleware("http")
    async def doar_host_local(request, call_next):
        host = (request.headers.get("host") or "127.0.0.1").rsplit(":", 1)[0].strip("[]")
        if host not in _HOSTURI_LOCALE:
            return PlainTextResponse("Acces respins: aplicația acceptă doar conexiuni locale.",
                                     status_code=403)
        # CSRF (audit SEC-3): la metode mutante, un site străin din browser trimite Origin: evil.com.
        # Origin local sau extensie de browser = ok; lipsa Origin (ne-browser / same-origin) = ok.
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin and not origin.startswith(("chrome-extension://", "moz-extension://")):
                from urllib.parse import urlsplit
                if urlsplit(origin).hostname not in _HOSTURI_LOCALE:
                    return PlainTextResponse("Acces respins: cerere cross-site blocată (CSRF).",
                                             status_code=403)
        resp = await call_next(request)
        # No-STORE pe paginile HTML: după un deploy, browserul ia INSTANT versiunea nouă, fără niciun
        # hard-refresh (no-cache singur lăsa uneori pagina veche în memoria browserului / bfcache).
        # Asset-urile statice (CSS/JS) rămân cacheabile (nu primesc acest header).
        if "text/html" in (resp.headers.get("content-type") or ""):
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            resp.headers["Pragma"] = "no-cache"
        return resp

    # Permite extensiei de browser sa POST-eze pe /api/import-anunt (aplicatie locala).
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"chrome-extension://.*|moz-extension://.*",
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
    templates.env.globals["versiune"] = __version__
    templates.env.globals["build_data"] = _build_data()
    deps = Deps(storage=storage, client=client, fetcher=fetcher, templates=templates,
                pdf_converter=pdf_converter)

    for modul in (evaluare, grile, descoperire, piata, aml, curent, pagini):
        app.include_router(modul.build_router(deps))

    return app
