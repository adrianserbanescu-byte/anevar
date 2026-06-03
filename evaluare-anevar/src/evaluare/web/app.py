"""Aplicatia web FastAPI: API JSON pentru evaluare + descarcare raport."""
from __future__ import annotations

import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from evaluare.assembler import EvaluationInput, construieste_context, valideaza
from evaluare.models.comparable import Comparable, LandComparable
from evaluare.engine.land import evaluate_land
from evaluare.engine.market import evaluate_market
from evaluare.ai.narrative import NarrativeClient
from evaluare.db.storage import Storage
from evaluare.importers.url_parser import fetch_html, import_from_url
from evaluare.report.generator import genereaza_raport
from evaluare.discovery.profiles import SubjectProfile
from evaluare.discovery.orchestrator import descopera
from evaluare.discovery.scoring import metodologie
from evaluare.localitati import judete as _judete, localitati as _localitati
from evaluare.zona import extrage_zona

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class ImportUrlRequest(BaseModel):
    url: str


class ZonaRequest(BaseModel):
    adresa: str


class IngestieRequest(BaseModel):
    tip: str               # cf | releveu | plan | cpe
    continut: str          # data-URL base64 (PDF)


class DescoperaTerenRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str = ""
    suprafata_subiect: Optional[Decimal] = None
    max_candidati: int = 8


class GrilaTerenRequest(BaseModel):
    suprafata_subiect: Decimal
    comparabile: list[LandComparable]


class GrilaCasaRequest(BaseModel):
    suprafata_subiect: Decimal
    comparabile: list[Comparable]


class DescoperaRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str
    subiect: SubjectProfile
    atribute_secundare: list[str] = []
    max_candidati: int = 8


def create_app(storage: Storage, client: Optional[NarrativeClient],
               fetcher: Callable[[str], str] = fetch_html) -> FastAPI:
    """Construieste aplicatia cu storage si client AI injectate."""
    app = FastAPI(title="Evaluare ANEVAR")
    templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

    @app.post("/api/evaluare")
    def creeaza_evaluare(inp: EvaluationInput) -> dict:
        from evaluare.audit.validare_x import valideaza_incrucisat
        ctx = construieste_context(inp, client=client)
        eid = storage.save(ctx)
        alerte = [a.model_dump() for a in valideaza(inp)]
        alerte += [a.model_dump() for a in valideaza_incrucisat(ctx)]  # validare incrucisata (audit)
        return {
            "id": eid,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
            "alerte": alerte,
        }

    @app.get("/api/evaluare/{eid}")
    def citeste_evaluare(eid: int) -> dict:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        return {
            "id": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        }

    @app.get("/api/evaluare/{eid}/raport.docx")
    def descarca_raport(eid: int, demo: int = 0) -> FileResponse:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        # ?demo=1 -> raport cu note de provenienta (calculat/extras/AI/exemplu/placeholder)
        sufix = "_demo" if demo else ""
        out = Path(tempfile.gettempdir()) / f"raport_{eid}{sufix}.docx"
        genereaza_raport(ctx, out, adnotari=bool(demo))
        return FileResponse(str(out), media_type=DOCX_MIME, filename=f"raport_{eid}{sufix}.docx")

    @app.get("/api/evaluare/{eid}/audit.txt")
    def audit_dosar(eid: int):
        from fastapi.responses import PlainTextResponse
        from evaluare.audit.jurnal import JurnalAudit
        from evaluare.audit.snapshot import snapshot
        from evaluare.audit.validare_x import valideaza_incrucisat
        from evaluare.audit.raport_audit import text_audit
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
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

    @app.get("/", response_class=HTMLResponse)
    def pagina_index(request: Request) -> HTMLResponse:
        # Pagina principala = wizard-ul ghidat pas-cu-pas.
        return templates.TemplateResponse(request, "wizard.html", {})

    @app.get("/formular", response_class=HTMLResponse)
    def pagina_formular(request: Request) -> HTMLResponse:
        # Formularul monolit (toate campurile pe o pagina), alternativa la wizard.
        return templates.TemplateResponse(request, "form.html", {})

    @app.get("/evaluare/{eid}", response_class=HTMLResponse)
    def pagina_rezultat(request: Request, eid: int) -> HTMLResponse:
        try:
            ctx = storage.load(eid)
        except KeyError:
            raise HTTPException(status_code=404, detail="Dosar inexistent.")
        return templates.TemplateResponse(request, "result.html", {
            "eid": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_finala": str(ctx.reconciled.valoare_finala),
            "metoda": ctx.reconciled.metoda_selectata,
        })

    @app.post("/api/import-url")
    def importa_url(req: ImportUrlRequest) -> dict:
        parsed = import_from_url(req.url, fetcher=fetcher)
        return {
            "pret": str(parsed.pret) if parsed.pret is not None else None,
            "moneda": parsed.moneda,
            "suprafata": str(parsed.suprafata) if parsed.suprafata is not None else None,
            "suprafata_teren": str(parsed.suprafata_teren) if parsed.suprafata_teren is not None else None,
            "titlu": parsed.titlu,
            "sursa_url": parsed.sursa_url,
            "an": parsed.an,
            "incalzire": parsed.incalzire,
            "material": parsed.material,
            "tip_cladire": parsed.tip_cladire,
            "stare_text": parsed.stare_text,
            "nr_camere": parsed.nr_camere,
            "etaje": parsed.etaje,
        }

    @app.post("/api/descopera")
    def descopera_endpoint(req: DescoperaRequest) -> dict:
        from evaluare.discovery.extractor import parse_atribute_secundare
        sec = parse_atribute_secundare("\n".join(req.atribute_secundare))
        rez = descopera(req.portal, req.judet, req.localitate, req.subiect, sec,
                        fetcher=fetcher, client=client, max_candidati=req.max_candidati)
        candidati = []
        for r in rez:
            candidati.append({
                "url": r.url, "titlu": r.titlu,
                "pret": str(r.pret) if r.pret is not None else None,
                "suprafata": str(r.suprafata) if r.suprafata is not None else None,
                "teren": str(r.teren) if r.teren is not None else None,
                "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
                "relevanta": r.breakdown.relevanta,
                "incredere_scazuta": r.breakdown.incredere_scazuta,
                "explicatie": r.breakdown.explicatie,
                "atribute": [a.model_dump() for a in r.breakdown.atribute],
                "secundare": [s.model_dump() for s in r.secundare],
            })
        return {"metodologie": metodologie(), "candidati": candidati}

    @app.post("/api/descopera-teren")
    def descopera_teren_endpoint(req: DescoperaTerenRequest) -> dict:
        from evaluare.discovery.orchestrator import descopera_teren
        rez = descopera_teren(req.portal, req.judet, req.localitate, req.suprafata_subiect,
                              fetcher=fetcher, max_candidati=req.max_candidati)
        return {"candidati": [{
            "url": r.url, "titlu": r.titlu,
            "pret": str(r.pret) if r.pret is not None else None,
            "suprafata": str(r.suprafata) if r.suprafata is not None else None,
            "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
            "relevanta": r.relevanta, "nota": r.nota,
        } for r in rez]}

    @app.get("/descoperire", response_class=HTMLResponse)
    def pagina_descoperire(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "descoperire.html", {})

    @app.post("/api/ingestie")
    def ingestie_endpoint(req: IngestieRequest) -> dict:
        import base64
        from evaluare.ingestie.ocr import extrage_text
        from evaluare.ingestie import extractoare
        extractor = {
            "cf": extractoare.extrage_cf, "releveu": extractoare.extrage_releveu,
            "plan": extractoare.extrage_plan, "cpe": extractoare.extrage_cpe,
        }.get(req.tip)
        if extractor is None:
            raise HTTPException(status_code=400, detail="Tip document necunoscut (cf/releveu/plan/cpe).")
        payload = req.continut.split(",", 1)[1] if req.continut.startswith("data:") else req.continut
        try:
            raw = base64.b64decode(payload, validate=True)
        except Exception:
            raise HTTPException(status_code=400, detail="Continut document invalid.")
        text = extrage_text(raw)
        return extractor(text).model_dump(mode="json")

    @app.post("/api/zona")
    def deriva_zona(req: ZonaRequest) -> dict:
        judet, localitate = extrage_zona(req.adresa, client=client)
        return {"judet": judet, "localitate": localitate}

    @app.get("/wizard", response_class=HTMLResponse)
    def pagina_wizard(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "wizard.html", {})

    @app.get("/api/curs-bnr")
    def curs_bnr_endpoint(moneda: str = "EUR") -> dict:
        from evaluare.curs_bnr import curs_bnr
        try:
            r = curs_bnr(moneda)
        except Exception:
            raise HTTPException(status_code=502, detail="Cursul BNR nu a putut fi preluat.")
        if r is None:
            raise HTTPException(status_code=404, detail=f"Valuta {moneda} nu e in lista BNR.")
        return {"moneda": r["moneda"], "curs": str(r["curs"]), "data": r["data"]}

    @app.get("/api/localitati")
    def lista_localitati() -> dict:
        judete = _judete()
        return {"judete": judete,
                "localitati": {j["slug"]: _localitati(j["slug"]) for j in judete}}

    @app.post("/api/grila-teren")
    def grila_teren(req: GrilaTerenRequest) -> dict:
        r = evaluate_land(req.comparabile, req.suprafata_subiect)
        return {
            "preturi_mp_corectate": [str(p) for p in r.preturi_mp_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "ajustari_nete": [str(n) for n in r.ajustari_nete],
            "index_selectat": r.index_selectat,
            "pret_mp_ales": str(r.pret_mp_ales),
            "valoare_teren": str(r.valoare_teren),
        }

    @app.post("/api/grila-casa")
    def grila_casa(req: GrilaCasaRequest) -> dict:
        r = evaluate_market(req.comparabile, req.suprafata_subiect)
        return {
            "preturi_unitare_corectate": [str(p) for p in r.preturi_unitare_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "ajustari_nete": [str(n) for n in r.ajustari_nete],
            "index_selectat": r.index_selectat,
            "valoare_piata": str(r.valoare_piata),
        }

    @app.get("/grila", response_class=HTMLResponse)
    def pagina_grila(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "grila.html", {})

    return app
