"""Registrul de evidenta a rapoartelor de evaluare (Procedura de arhivare ANEVAR §6).

Pagina + export CSV/XLSX cu cele ~13 campuri cerute de §6. Randurile se deriva din dosarele de pe
disc (`registru.registru`), deci registrul nu se poate desincroniza de dosare.

Actiunea „pregateste pentru BIG" (GEV 520 §7): dintr-un dosar construieste payload-ul Buletinului
Informativ al Garantiilor (`big.construieste_payload_big`) + ruleaza checklist-ul de campuri minime
(`big.valideaza_campuri_minime`) ca sa arate ce LIPSESTE inainte de inregistrarea manuala in BIG.
"""
from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from pydantic import ValidationError

from evaluare import big
from evaluare import dosare_fs as fs
from evaluare.registru import registru as reg
from evaluare.web.deps import Deps

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _g(wizard: dict, *chei: str) -> str | None:
    """Prima valoare ne-goala dintre `chei` (toleranta la variante de denumire). None daca lipsesc toate."""
    for c in chei:
        v = wizard.get(c)
        if v not in (None, "", []):
            return str(v).strip()
    return None


def _pozitiv(v: object) -> object | None:
    """Pasa `v` mai departe DOAR daca se converteste la un numar strict pozitiv; altfel None.

    Campurile BIG `suprafata`/`valoare_piata` au `Field(gt=0)`. O valoare <=0 (ex. `"0"`, `"-5"`,
    `"0.0"`) ar declansa `ValidationError` (subclasa de `ValueError`) la construirea modelului si ar
    darama pagina `/registru` + endpoint-ul. Tratam o astfel de valoare ca LIPSA (None), ca sa apara
    in checklist-ul de lipsuri, nu sa arunce. Valorile ne-numerice raman neschimbate (BIG `_dec()` le
    converteste tolerant la None oricum)."""
    if v is None:
        return None
    try:
        if Decimal(str(v)) > 0:
            return v
    except (ArithmeticError, ValueError, TypeError):
        return v          # ne-numeric -> lasa BIG._dec() sa-l reduca tolerant la None
    return None           # numeric, dar <=0 -> trateaza ca lipsa


def pregateste_big(dosar: dict) -> big.CampuriMinimeBIG:
    """Construieste campurile BIG dintr-un dosar (`dosar.json`), mapand snapshot-ul wizardului plat la
    structura asteptata de `big.construieste_payload_big`.

    Snapshot-ul wizardului e un dict PLAT (cheie = id-ul campului din formular). Identitatea
    evaluatorului vine de pe DOSAR (creator), iar numarul de identificare a raportului din `nr_lucrare`
    (Procedura §6/§11) — niciunul nu e in wizard. Valoarea de piata se cauta pe dosar (concluzia
    persistata, daca exista); cand lipseste, apare in checklist-ul de lipsuri (comportament corect:
    nu inventam o concluzie).
    """
    w = dosar.get("wizard", {}) or {}
    meta = {
        "beneficiar": _g(w, "beneficiar", "utilizator_desemnat"),
        "cod_bic": _g(w, "cod_bic"),
        "moneda": _g(w, "moneda") or "RON",
        "data_evaluarii": _g(w, "data_evaluarii"),
        "data_raportului": _g(w, "data_raportului"),
        # Identitatea evaluatorului = creatorul dosarului (membru titular ANEVAR), nu campuri din wizard.
        "evaluator_nume": dosar.get("creator_nume") or "",
        "evaluator_legitimatie": dosar.get("creator_legitimatie") or "",
        # Numarul de identificare a raportului = numarul de lucrare alocat la creare (Procedura §6/§11).
        "nr_lucrare": dosar.get("nr_lucrare"),
        # Concluzia (valoarea de piata) — persistata pe dosar daca un calcul a fost salvat; altfel lipsa.
        # `_pozitiv`: o valoare <=0 e tratata ca LIPSA (campul BIG e `gt=0`), nu ca eroare 500.
        "valoare_piata": _pozitiv(dosar.get("valoare_finala") or _g(w, "valoare_finala", "valoare_piata")),
    }
    profil = {"tip_activ": _g(w, "tip_proprietate")}
    localizare = {
        "cod_postal": _g(w, "cod_postal"),
        "judet": _g(w, "judet"),
        "localitate": _g(w, "localitate_alt", "localitate"),
        "strada": _g(w, "adresa_strada", "adresa"),
    }
    descriere = {
        # Suprafata raportata in BIG: terenul (`suprafata_teren`) sau, pt constructii, aria utila/desfasurata.
        # `_pozitiv`: o suprafata <=0 e tratata ca LIPSA (campul BIG e `gt=0`), nu ca eroare 500.
        "suprafata": _pozitiv(_g(w, "suprafata_teren", "suprafata", "acd", "au")),
        "um_suprafata": _g(w, "um_suprafata") or "mp",
        "an_constructie": _g(w, "an_referinta", "an_pif"),
    }
    return big.construieste_payload_big(
        meta=meta, profil=profil, localizare=localizare, descriere=descriere,
    )


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.get("/registru", response_class=HTMLResponse)
    def pagina_registru(request: Request) -> HTMLResponse:
        randuri = reg.randuri()
        # Pregatire BIG per rand: cate campuri minime lipsesc inainte de inregistrarea in BIG (GEV 520 §7).
        big_status: dict[str, dict] = {}
        for r in randuri:
            uid = r.get("uid")
            if not uid:
                continue
            try:
                campuri = pregateste_big(fs.incarca(uid))
            except KeyError:                     # dosar disparut intre listare si citire -> sarit
                continue
            except (ValidationError, ValueError):
                # dosar otravit (date care nu trec validarea BIG) -> marcheaza-l ca neGATA, NU darama
                # pagina pentru toti. `nr_lipsuri` = toate campurile obligatorii (echivalent „nimic util").
                big_status[uid] = {
                    "nr_lipsuri": len(big.CAMPURI_OBLIGATORII), "gata": False, "eroare": True,
                }
                continue
            lipsuri = big.valideaza_campuri_minime(campuri)
            big_status[uid] = {"nr_lipsuri": len(lipsuri), "gata": not lipsuri}
        return d.templates.TemplateResponse(request, "curent/registru.html",
            {"coloane": reg.COLOANE, "randuri": randuri, "big_status": big_status})

    @router.get("/api/registru")
    def api_registru() -> dict:
        """Registrul ca JSON (coloane + randuri) — pentru integrari / verificare."""
        return {
            "coloane": [{"cheie": k, "eticheta": et} for k, et in reg.COLOANE],
            "randuri": reg.randuri(),
        }

    @router.get("/api/registru.csv")
    def registru_csv() -> PlainTextResponse:
        return PlainTextResponse(reg.csv_text(), media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=registru-rapoarte.csv"})

    @router.get("/api/registru.xlsx")
    def registru_xlsx() -> Response:
        return Response(reg.xlsx_bytes(), media_type=XLSX_MIME,
            headers={"Content-Disposition": "attachment; filename=registru-rapoarte.xlsx"})

    @router.get("/api/dosar/{uid}/big")
    def pregateste_dosar_big(uid: str) -> dict:
        """Pregateste un dosar pentru BIG (GEV 520 §7): payload-ul Buletinului Informativ al
        Garantiilor + checklist-ul de campuri minime LIPSA inainte de inregistrarea manuala in portal.

        Raspuns JSON: `payload` (campurile minime BIG), `lipsuri` (etichetele campurilor inca negate),
        `gata` (True daca nu lipseste niciun camp minim). Datele raman LOCALE (niciun apel de retea/AI).
        """
        try:
            dosar = fs.incarca(uid)              # _cale() refuza uid non-UUID (anti path-traversal)
        except KeyError:
            raise HTTPException(404, "Dosar inexistent.") from None
        try:
            campuri = pregateste_big(dosar)
        except (ValidationError, ValueError) as e:
            # Date care nu trec validarea BIG (ex. ramase dupa o cale neacoperita de `_pozitiv`) ->
            # 422, nu 500: un dosar otravit nu trebuie sa darame endpoint-ul.
            raise HTTPException(422, "Dosar invalid pentru BIG.") from e
        lipsuri = big.valideaza_campuri_minime(campuri)
        return {
            "uid": uid,
            "nr_lucrare": dosar.get("nr_lucrare"),
            "payload": campuri.model_dump(mode="json"),
            "lipsuri": lipsuri,
            "gata": not lipsuri,
        }

    return router
