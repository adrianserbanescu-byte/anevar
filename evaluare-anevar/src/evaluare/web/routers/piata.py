"""Instrumente de piata: import URL, ingestie documente, zona, curs BNR, indice ANEVAR, localitati."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from evaluare.importers.url_parser import import_from_url
from evaluare.localitati import judete as _judete
from evaluare.localitati import localitati as _localitati
from evaluare.logging_setup import get_logger
from evaluare.web.deps import Deps
from evaluare.web.schemas import ImportUrlRequest, IngestieRequest, ZonaRequest
from evaluare.zona import extrage_zona

log = get_logger(__name__)


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/import-url")
    def importa_url(req: ImportUrlRequest) -> dict:
        parsed = import_from_url(req.url, fetcher=d.fetcher)
        if parsed.pagina_lista:
            raise HTTPException(status_code=422, detail=(
                "Linkul pare o pagină de listă/căutare, nu un anunț individual. "
                "Deschide anunțul și copiază URL-ul lui."))
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

    @router.post("/api/ingestie")
    def ingestie_endpoint(req: IngestieRequest) -> dict:
        import base64

        from evaluare.ingestie import extractoare
        from evaluare.ingestie.ocr import extrage_text
        extractor = {
            "cf": extractoare.extrage_cf, "releveu": extractoare.extrage_releveu,
            "plan": extractoare.extrage_plan, "cpe": extractoare.extrage_cpe,
        }.get(req.tip)
        if extractor is None:
            raise HTTPException(status_code=400,
                detail="Tip de document necunoscut. Alege: cf, releveu, plan sau cpe.")
        payload = req.continut.split(",", 1)[1] if req.continut.startswith("data:") else req.continut
        if len(payload) > 35_000_000:            # ~26 MB după decodare — limită anti-DoS
            raise HTTPException(status_code=413, detail="Document prea mare (limită ~25 MB).")
        try:
            raw = base64.b64decode(payload, validate=True)
        except Exception:
            raise HTTPException(status_code=400,
                detail="Conținut document invalid. Încarcă un fișier PDF valid.") from None
        text = extrage_text(raw)
        return extractor(text).model_dump(mode="json")

    @router.post("/api/zona")
    def deriva_zona(req: ZonaRequest) -> dict:
        judet, localitate = extrage_zona(req.adresa, client=d.client)
        return {"judet": judet, "localitate": localitate}

    @router.get("/api/curs-bnr")
    def curs_bnr_endpoint(moneda: str = "EUR") -> dict:
        from evaluare.curs_bnr import curs_bnr
        try:
            r = curs_bnr(moneda)
        except Exception as e:
            log.warning("Curs BNR indisponibil (%s): %s", moneda, e)
            raise HTTPException(status_code=502,
                detail="Cursul BNR nu a putut fi preluat. Verifică conexiunea la internet.") from e
        if r is None:
            raise HTTPException(status_code=404, detail=f"Valuta {moneda} nu e in lista BNR.")
        return {"moneda": r["moneda"], "curs": str(r["curs"]), "data": r["data"]}

    @router.get("/api/indice-anevar")
    def indice_anevar_endpoint(ultimele: int = 6) -> dict:
        from evaluare.indice_anevar import indice_anevar
        try:
            dd = indice_anevar(fetcher=d.fetcher)
        except Exception as e:
            log.warning("Indice ANEVAR indisponibil: %s", e)
            raise HTTPException(status_code=502,
                detail="Indicele ANEVAR nu a putut fi preluat. Verifică conexiunea la internet.") from e
        dd["perioade"] = dd["perioade"][-max(1, ultimele):]
        return dd

    @router.get("/api/localitati")
    def lista_localitati() -> dict:
        judete = _judete()
        return {"judete": judete,
                "localitati": {j["slug"]: _localitati(j["slug"]) for j in judete}}

    return router
