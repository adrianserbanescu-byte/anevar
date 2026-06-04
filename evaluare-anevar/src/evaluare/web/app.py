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
from evaluare.models.comparable import Comparable, LandComparable, RentComparable
from evaluare.engine.land import evaluate_land
from evaluare.engine.market import evaluate_market
from evaluare.engine.chirie import evalueaza_chirie
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


def _fmt_numar(v: Decimal) -> str:
    """Format ro-RO cu 2 zecimale: mii separate cu '.', zecimale cu ','. Ex: 316000 -> '316.000,00'."""
    q = v.quantize(Decimal("0.01"))
    s = f"{q:,.2f}"                                  # en: 316,000.00
    return s.replace(",", "·").replace(".", ",").replace("·", ".")


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


class GrilaChiriiRequest(BaseModel):
    suprafata_subiect: Decimal
    comparabile: list[RentComparable]


class DescoperaRequest(BaseModel):
    portal: str = "imobiliare"
    judet: str
    localitate: str
    subiect: SubjectProfile
    atribute_secundare: list[str] = []
    max_candidati: int = 8


class AmlEvaluareRequest(BaseModel):
    tip_entitate: str = "PFA"            # PFA | PJ (entitatea evaluator)
    azi: str                             # data evaluarii (yyyy-mm-dd)
    client_pf: Optional[dict] = None
    client_pj: Optional[dict] = None
    semnale_risc: Optional[dict] = None
    semnale_indicatori: Optional[dict] = None


class AmlDocRequest(BaseModel):
    tip_entitate: str = "PFA"
    azi: Optional[str] = None
    client_pf: Optional[dict] = None
    client_pj: Optional[dict] = None
    semnale_risc: Optional[dict] = None
    semnale_indicatori: Optional[dict] = None
    persoana_desemnata: Optional[dict] = None
    rtn: Optional[dict] = None           # {suma_eur, data_tranzactie, descriere}
    rts: Optional[dict] = None           # {motiv, data_inregistrare, indicatori}


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
        val = ctx.reconciled.valoare_finala
        moneda = (ctx.meta.moneda or "LEI").upper()
        curs = ctx.meta.curs_valutar
        echiv = None
        if curs:
            if moneda == "LEI":
                echiv = _fmt_numar(val / curs) + " EUR"
            elif moneda == "EUR":
                echiv = _fmt_numar(val * curs) + " LEI"
        return templates.TemplateResponse(request, "result.html", {
            "eid": eid,
            "client_nume": ctx.meta.client_nume,
            "valoare_fmt": _fmt_numar(val),
            "moneda": moneda,
            "echiv": echiv,
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

    @app.get("/api/indice-anevar")
    def indice_anevar_endpoint(ultimele: int = 6) -> dict:
        from evaluare.indice_anevar import indice_anevar
        try:
            d = indice_anevar(fetcher=fetcher)
        except Exception:
            raise HTTPException(status_code=502, detail="Indicele ANEVAR nu a putut fi preluat.")
        d["perioade"] = d["perioade"][-max(1, ultimele):]
        return d

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

    @app.post("/api/grila-chirii")
    def grila_chirii(req: GrilaChiriiRequest) -> dict:
        try:
            r = evalueaza_chirie(req.comparabile, req.suprafata_subiect)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        return {
            "chirii_mp_corectate": [str(p) for p in r.chirii_mp_corectate],
            "ajustari_brute": [str(b) for b in r.ajustari_brute],
            "ajustari_nete": [str(n) for n in r.ajustari_nete],
            "index_selectat": r.index_selectat,
            "chirie_mp_aleasa": str(r.chirie_mp_aleasa),
            "chirie_lunara": str(r.chirie_lunara),
            "venit_brut_potential": str(r.venit_brut_potential),
        }

    @app.get("/grila", response_class=HTMLResponse)
    def pagina_grila(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "grila.html", {})

    # ----------------------------------------------------------------------- #
    # Conformitate AML (Legea 129/2019). Datele KYC raman local; drafturile RTS/RTN
    # se pastreaza SEPARAT de dosarul de evaluare (tipping-off, art. 38).
    # ----------------------------------------------------------------------- #
    aml_dir = storage.db_path.parent / "aml_confidential"

    def _client_din(req) -> object:
        from evaluare.aml.models import ClientPF, ClientPJ
        if req.client_pj is not None:
            return ClientPJ(**req.client_pj)
        return ClientPF(**(req.client_pf or {}))

    @app.post("/api/aml/evalueaza")
    def aml_evalueaza(req: AmlEvaluareRequest) -> dict:
        from evaluare.aml.serviciu import evalueaza_relatie
        from evaluare.aml.risc import Semnale
        from evaluare.aml.indicatori import SemnaleIndicatori
        from evaluare.aml.liste import incarca_liste
        client = _client_din(req)
        return evalueaza_relatie(
            req.tip_entitate, client, azi=req.azi,
            semnale_risc=Semnale(**req.semnale_risc) if req.semnale_risc else None,
            semnale_indicatori=SemnaleIndicatori(**req.semnale_indicatori) if req.semnale_indicatori else None,
            liste=incarca_liste(),
        )

    def _doc_response(doc, nume: str):
        out = Path(tempfile.gettempdir()) / nume
        from evaluare.aml.documente import salveaza
        salveaza(doc, out)
        return FileResponse(str(out), media_type=DOCX_MIME, filename=nume)

    @app.post("/api/aml/norme-interne.docx")
    def aml_norme_interne(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_norme_interne
        return _doc_response(genereaza_norme_interne(), "aml_norme_interne.docx")

    @app.post("/api/aml/evaluare-risc.docx")
    def aml_evaluare_risc_doc(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_evaluare_risc
        from evaluare.aml.risc import Semnale, evalueaza_risc
        client = _client_din(req)
        er = evalueaza_risc(client, Semnale(**req.semnale_risc) if req.semnale_risc else None,
                            azi=req.azi or "2026-01-01")
        return _doc_response(genereaza_evaluare_risc(er), "aml_evaluare_risc.docx")

    @app.post("/api/aml/decizie.docx")
    def aml_decizie(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_decizie_desemnare
        from evaluare.aml.models import PersoanaFizica
        try:
            doc = genereaza_decizie_desemnare(
                req.tip_entitate, PersoanaFizica(**(req.persoana_desemnata or {})))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return _doc_response(doc, "aml_decizie_desemnare.docx")

    @app.post("/api/aml/fisa-kyc.docx")
    def aml_fisa_kyc(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_fisa_kyc
        return _doc_response(genereaza_fisa_kyc(_client_din(req), None), "aml_fisa_kyc.docx")

    @app.post("/api/aml/rtn.docx")
    def aml_rtn(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_rtn
        from evaluare.aml.raportare import RaportRTN
        from evaluare.aml.store import StoreAML
        if not req.rtn:
            raise HTTPException(status_code=400, detail="Lipsesc datele RTN.")
        raport = RaportRTN(**req.rtn)
        # persistat separat de dosar (tipping-off / retentie)
        StoreAML(aml_dir).salveaza("rtn", raport.model_dump(mode="json"), raport.data_tranzactie)
        return _doc_response(genereaza_rtn(raport), "aml_rtn.docx")

    @app.post("/api/aml/rts.docx")
    def aml_rts(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_rts
        from evaluare.aml.raportare import RaportRTS
        from evaluare.aml.store import StoreAML
        if not req.rts:
            raise HTTPException(status_code=400, detail="Lipsesc datele RTS.")
        raport = RaportRTS(**req.rts)
        StoreAML(aml_dir).salveaza("rts", raport.model_dump(mode="json"), raport.data_inregistrare)
        return _doc_response(genereaza_rts(raport), "aml_rts.docx")

    @app.get("/aml", response_class=HTMLResponse)
    def pagina_aml(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "aml.html", {})

    return app
