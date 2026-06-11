"""Aplicatia web FastAPI: compune routerele pe domenii (vezi ADR-001)."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.importers.url_parser import fetch_html
from evaluare.logging_setup import get_logger
from evaluare.web.deps import Deps
from evaluare.web.routers import (
    aml,
    curent,
    descoperire,
    evaluare,
    grile,
    pagini,
    piata,
    registru,
)

log = get_logger(__name__)


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
               fetcher: Callable[[str], str] = fetch_html) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    from fastapi.middleware.cors import CORSMiddleware
    from starlette.responses import PlainTextResponse

    from evaluare import __version__
    app = FastAPI(title="Evaluare ANEVAR")

    # M1 (audit user-journey): o validare Pydantic eșuată (ex. `numar_cadastral`/`carte_funciara` lipsă,
    # care-s obligatorii) întorcea un array Pydantic BRUT pe care UI-ul îl afișa evaluatorului ca
    # „[object Object]". Acest handler formatează ORICE 422 de validare într-un `detail` STRING citibil
    # în RO -> mesaj prietenos, nu cifrat. (Calea `_context()` rămâne pentru erorile de calcul/aritmetică.)
    from fastapi.exceptions import RequestValidationError
    from starlette.responses import JSONResponse

    @app.exception_handler(RequestValidationError)
    async def _eroare_validare(_request, exc):
        def _ro(e: dict) -> str:
            loc = [str(p) for p in e.get("loc", ()) if p != "body"]
            camp = ".".join(loc) or "date"
            return f"«{camp}»: {e.get('msg', 'valoare invalidă')}"
        detalii = "; ".join(_ro(e) for e in exc.errors())
        return JSONResponse(status_code=422,
                            content={"detail": f"Date invalide sau incomplete — {detalii}"})

    # Gardă anti DNS-rebinding / cross-site: aplicația locală acceptă DOAR Host local.
    # Un site vizitat (evil.com) care rezolvă la 127.0.0.1 ar trimite Host: evil.com -> respins,
    # deci nu poate șterge dosare / exfiltra PII prin API-ul local. „testserver" = host-ul TestClient.
    _HOSTURI_LOCALE = {"127.0.0.1", "localhost", "::1", "testserver"}

    @app.middleware("http")
    async def doar_host_local(request, call_next):
        host = (request.headers.get("host") or "127.0.0.1").rsplit(":", 1)[0].strip("[]")
        if host not in _HOSTURI_LOCALE:
            log.warning("Acces respins (host non-local, posibil sondaj): %s", host)
            return PlainTextResponse("Acces respins: aplicația acceptă doar conexiuni locale.",
                                     status_code=403)
        # CSRF (audit SEC-3): la metode mutante, un site străin din browser trimite Origin: evil.com.
        # Origin local sau extensie de browser = ok; lipsa Origin (ne-browser / same-origin) = ok.
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            origin = request.headers.get("origin")
            if origin and not origin.startswith(("chrome-extension://", "moz-extension://")):
                from urllib.parse import urlsplit
                if urlsplit(origin).hostname not in _HOSTURI_LOCALE:
                    log.warning("Acces respins (CSRF cross-site, posibil sondaj): %s", origin)
                    return PlainTextResponse("Acces respins: cerere cross-site blocată (CSRF).",
                                             status_code=403)
        # Plafon global de dimensiune corp (anti-DoS, RUNDA 11): un corp de zeci/sute de MB pe campuri
        # nemarginite (import-anunt.html, photos/documente, wizard dict) ar cauza OOM/hang la
        # deserializare. Upload-urile dedicate au deja garda 35MB pe payload; aici plafonam corpul brut.
        cl = request.headers.get("content-length")
        if cl and cl.isdigit() and int(cl) > 50_000_000:        # ~50 MB (peste max-ul legitim de upload)
            log.warning("Corp respins (prea mare, posibil DoS): %s bytes", cl)
            return PlainTextResponse("Corp prea mare (limită ~50 MB).", status_code=413)
        resp = await call_next(request)
        # Security headers (defense-in-depth, audit C/D): nosniff + anti-clickjacking + referrer +
        # permissions + CSP. CSP = al 4-lea strat anti-XSS peste escapeHtml/urlSafe/teste; permite
        # inline (app-ul are JS/CSS inline) + unpkg (MapLibre, pana la bundle-ul local) + https (tile harta).
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; "
            "img-src 'self' data: blob: https:; font-src 'self' data:; connect-src 'self' https:; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com")
        resp.headers["Server"] = "anevar"             # nu mai expune "uvicorn" (fingerprint, audit D)
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
    deps = Deps(storage=storage, client=client, fetcher=fetcher, templates=templates)

    for modul in (evaluare, grile, descoperire, piata, aml, curent, registru, pagini):
        app.include_router(modul.build_router(deps))

    return app
