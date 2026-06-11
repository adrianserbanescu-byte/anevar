"""Conformitate AML (Legea 129/2019).

Datele KYC raman local; drafturile RTS/RTN se pastreaza SEPARAT de dosarul de
evaluare (tipping-off, art. 38).
"""
from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask

from evaluare.web.deps import DOCX_MIME, Deps
from evaluare.web.schemas import AmlDocRequest, AmlEvaluareRequest

if TYPE_CHECKING:
    from evaluare.aml.models import ClientPF, ClientPJ


def _construieste(factory, data, eticheta: str):
    """Construieste un model AML din dict-ul user RAW, convertind erorile de validare in 422 (nu 500).

    Tipare Model(**req.X): pydantic ValidationError (subclasa ValueError) pe campuri tipate gresit SAU
    TypeError pe kwargs neasteptate la dataclass-uri -> ar deveni 500 daca nu sunt prinse aici."""
    try:
        return factory(**(data or {}))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Date AML invalide pentru {eticheta}.") from e


def _client_din(req) -> ClientPF | ClientPJ:
    from evaluare.aml.models import ClientPF, ClientPJ
    if req.client_pj is not None:
        return _construieste(ClientPJ, req.client_pj, "client persoana juridica")
    return _construieste(ClientPF, req.client_pf, "client persoana fizica")


async def _corp_brut(request: Request) -> dict:
    """Corpul JSON brut al cererii ca dict (cu fallback {} la corp ne-dict/ne-JSON).

    FastAPI cacheaza body-ul, deci re-citirea aici (dupa parsarea modelului tipizat) e sigura.
    Folosit DOAR pentru campuri optionale aditive (scop/EDD) absente din schema stabila."""
    try:
        corp = await request.json()
    except (ValueError, UnicodeDecodeError):
        return {}
    return corp if isinstance(corp, dict) else {}


def _scop_si_edd(corp: dict) -> tuple[str | None, dict]:
    """Extrage scopul evaluarii (dosar/meta) + campurile EDD din corpul brut.

    Scopul poate veni direct (`scop`) sau dintr-un sub-obiect `meta`/`dosar` (`{"meta": {"scop": …}}`).
    Campurile EDD provin din DosarAML; absenta lor -> valori neutre (non-blocant)."""
    def _sub(cheie: str) -> dict:
        v = corp.get(cheie)
        return v if isinstance(v, dict) else {}

    meta = _sub("meta")
    dosar = _sub("dosar")
    edd_src = {**dosar, **_sub("edd"), **corp}  # corp are precedenta pe chei plate
    scop = corp.get("scop") or meta.get("scop") or dosar.get("scop")
    scop = scop if isinstance(scop, str) else None

    def _txt(cheie: str) -> str | None:
        v = edd_src.get(cheie)
        return v if isinstance(v, str) else None

    edd = {
        "sursa_fonduri": _txt("sursa_fonduri"),
        "sursa_avere": _txt("sursa_avere"),
        "aprobare_conducere_pep": bool(
            edd_src.get("aprobare_conducere_pep")
            or edd_src.get("aprobare_conducere_superioara_pep")
        ),
    }
    return scop, edd


def _doc_response(doc, nume: str):
    # Igienă PII (F-SEC-2): documentele AML conțin CNP/nume/serie act. Scriem într-un fișier temp
    # cu token unic (nu nume predictibil, partajat) și îl ștergem după trimitere (BackgroundTask),
    # ca PII-ul să nu rămână pe disc în temp-ul mașinii — paritate cu raportul (curent.py).
    tok = uuid.uuid4().hex[:8]
    out = Path(tempfile.gettempdir()) / f"{Path(nume).stem}_{tok}{Path(nume).suffix}"
    from evaluare.aml.documente import salveaza
    salveaza(doc, out)
    return FileResponse(
        str(out), media_type=DOCX_MIME, filename=nume,
        background=BackgroundTask(lambda: out.unlink(missing_ok=True)),
    )


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()
    aml_dir = d.storage.db_path.parent / "aml_confidential"

    @router.post("/api/aml/evalueaza")
    async def aml_evalueaza(req: AmlEvaluareRequest, request: Request) -> dict:
        from evaluare.aml.indicatori import SemnaleIndicatori
        from evaluare.aml.liste import incarca_liste
        from evaluare.aml.risc import Semnale
        from evaluare.aml.serviciu import evalueaza_relatie
        client = _client_din(req)
        # Scopul evaluarii + campurile EDD nu sunt pe AmlEvaluareRequest (schema stabila); le citim
        # optional din corpul brut (dosar/meta) — aditiv si backward-compatible. Corp ne-dict / lipsa
        # cheilor -> valori neutre (None/False), comportament identic cu cel anterior.
        scop, edd = _scop_si_edd(await _corp_brut(request))
        return evalueaza_relatie(
            req.tip_entitate, client, azi=req.azi,
            semnale_risc=_construieste(Semnale, req.semnale_risc, "semnale de risc")
            if req.semnale_risc else None,
            semnale_indicatori=_construieste(SemnaleIndicatori, req.semnale_indicatori, "semnale indicatori")
            if req.semnale_indicatori else None,
            liste=incarca_liste(),
            scop=scop,
            sursa_fonduri=edd["sursa_fonduri"],
            sursa_avere=edd["sursa_avere"],
            aprobare_conducere_pep=edd["aprobare_conducere_pep"],
        )

    @router.post("/api/aml/norme-interne.docx")
    def aml_norme_interne(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_norme_interne
        return _doc_response(genereaza_norme_interne(), "aml_norme_interne.docx")

    @router.post("/api/aml/evaluare-risc.docx")
    def aml_evaluare_risc_doc(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_evaluare_risc
        from evaluare.aml.risc import Semnale, evalueaza_risc
        client = _client_din(req)
        er = evalueaza_risc(client,
                            _construieste(Semnale, req.semnale_risc, "semnale de risc")
                            if req.semnale_risc else None,
                            azi=req.azi or "2026-01-01")
        return _doc_response(genereaza_evaluare_risc(er), "aml_evaluare_risc.docx")

    @router.post("/api/aml/decizie.docx")
    def aml_decizie(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_decizie_desemnare
        from evaluare.aml.models import PersoanaFizica
        try:
            doc = genereaza_decizie_desemnare(
                req.tip_entitate, PersoanaFizica(**(req.persoana_desemnata or {})))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return _doc_response(doc, "aml_decizie_desemnare.docx")

    @router.post("/api/aml/fisa-kyc.docx")
    def aml_fisa_kyc(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_fisa_kyc
        return _doc_response(genereaza_fisa_kyc(_client_din(req), None), "aml_fisa_kyc.docx")

    @router.post("/api/aml/rtn.docx")
    def aml_rtn(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_rtn
        from evaluare.aml.raportare import RaportRTN
        from evaluare.aml.store import StoreAML
        if not req.rtn:
            raise HTTPException(status_code=400, detail="Lipsesc datele RTN.")
        raport = _construieste(RaportRTN, req.rtn, "raport RTN")
        # persistat separat de dosar (tipping-off / retentie)
        StoreAML(aml_dir).salveaza("rtn", raport.model_dump(mode="json"), raport.data_tranzactie)
        return _doc_response(genereaza_rtn(raport), "aml_rtn.docx")

    @router.post("/api/aml/rts.docx")
    def aml_rts(req: AmlDocRequest):
        from evaluare.aml.documente import genereaza_rts
        from evaluare.aml.raportare import RaportRTS
        from evaluare.aml.store import StoreAML
        if not req.rts:
            raise HTTPException(status_code=400, detail="Lipsesc datele RTS.")
        raport = _construieste(RaportRTS, req.rts, "raport RTS")
        StoreAML(aml_dir).salveaza("rts", raport.model_dump(mode="json"), raport.data_inregistrare)
        return _doc_response(genereaza_rts(raport), "aml_rts.docx")

    @router.post("/api/gdpr/politica.docx")
    def gdpr_politica(req: AmlDocRequest):
        from evaluare.gdpr.documente import genereaza_politica_gdpr
        return _doc_response(genereaza_politica_gdpr(), "gdpr_politica_prelucrare_MODEL.docx")

    @router.post("/api/gdpr/consimtamant.docx")
    def gdpr_consimtamant(req: AmlDocRequest):
        from evaluare.gdpr.documente import genereaza_consimtamant_gdpr
        return _doc_response(genereaza_consimtamant_gdpr(), "gdpr_acord_consimtamant_MODEL.docx")

    @router.get("/aml", response_class=HTMLResponse)
    def pagina_aml(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "aml.html", {})

    return router
