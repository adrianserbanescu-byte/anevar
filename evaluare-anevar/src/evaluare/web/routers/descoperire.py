"""Descoperire comparabile din portaluri: casa + teren, pagina /descoperire."""
from __future__ import annotations

import math

import requests
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from evaluare.discovery import ponderi_store
from evaluare.discovery.orchestrator import descopera
from evaluare.discovery.ponderi import AXA_ATRIBUT, AXE, PONDERI_PER_CATEGORIE, fuzioneaza_override
from evaluare.discovery.scoring import metodologie
from evaluare.geo import coordonate, distanta_km, localitate_din_url
from evaluare.importers.url_parser import parse_listing_html
from evaluare.logging_setup import get_logger
from evaluare.web.deps import Deps
from evaluare.web.schemas import (
    ConfigPonderiRequest,
    DescoperaRequest,
    DescoperaTerenRequest,
    ImportAnuntRequest,
    StergeAnuntRequest,
)

log = get_logger(__name__)


def _geo_campuri(url: str, judet: str, localitate_cautata: str,
                 subiect: tuple[float, float] | None) -> dict:
    """lat/lng + distanta fata de subiect pt un anunt (harta P1.3 + afisaj 'la X km de subiect').

    Localitatea anuntului = detectata din slug-ul URL-ului (cautarea pe judet aduce localitati
    diferite); fallback pe localitatea cautata. Fara coordonate -> None (harta omite gratios)."""
    loc = localitate_din_url(url, judet) or localitate_cautata
    c = coordonate(judet, loc)
    if c is None:
        return {"lat": None, "lng": None, "distanta_km": None}
    dist = round(distanta_km(subiect[0], subiect[1], c[0], c[1]), 1) if subiect else None
    return {"lat": c[0], "lng": c[1], "distanta_km": dist}


def build_router(d: Deps) -> APIRouter:
    router = APIRouter()

    @router.post("/api/descopera")
    def descopera_endpoint(req: DescoperaRequest) -> dict:
        from evaluare.discovery.extractor import parse_atribute_secundare
        sec = parse_atribute_secundare("\n".join(req.atribute_secundare))
        # ponderi EFECTIVE ale categoriei = default (ponderi.py) + override editat de evaluator
        efective = ponderi_store.ponderi_efective(d.storage.db_path.parent)
        ponderi_cat = efective.get(req.tip_activ or "casa") or efective["casa"]
        try:
            rez = descopera(req.portal, req.judet, req.localitate, req.subiect, sec,
                            fetcher=d.fetcher, client=d.client, max_candidati=req.max_candidati,
                            tip_activ=req.tip_activ, ponderi=ponderi_cat)
        except (requests.RequestException, ValueError, OSError) as e:
            raise HTTPException(502, "Portalul nu a răspuns sau conexiunea a eșuat. "
                                "Încearcă din nou sau adaugă comparabilele manual.") from e
        subiect_coord = coordonate(req.judet, req.localitate)   # geocoding offline (tabel bundle-uit)
        candidati = []
        for r in rez:
            candidati.append({
                "url": r.url, "titlu": r.titlu,
                "pret": str(r.pret) if r.pret is not None else None,
                "suprafata": str(r.suprafata) if r.suprafata is not None else None,
                "teren": str(r.teren) if r.teren is not None else None,
                "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
                "poza": r.poza,                  # URL imagine (og:image) pt cardurile UI; None daca lipseste
                "relevanta": r.breakdown.relevanta,
                "axe": r.breakdown.axe,          # scor pe axe pt radarul D2 (None = axa fara date)
                "incredere_scazuta": r.breakdown.incredere_scazuta,
                "explicatie": r.breakdown.explicatie,
                "atribute": [a.model_dump() for a in r.breakdown.atribute],
                "secundare": [s.model_dump() for s in r.secundare],
                **_geo_campuri(r.url, req.judet, req.localitate, subiect_coord),   # harta + distanta
            })
        return {"metodologie": metodologie(ponderi_cat), "candidati": candidati,
                "subiect_lat": subiect_coord[0] if subiect_coord else None,
                "subiect_lng": subiect_coord[1] if subiect_coord else None}

    @router.post("/api/descopera-teren")
    def descopera_teren_endpoint(req: DescoperaTerenRequest) -> dict:
        from evaluare.discovery.orchestrator import descopera_teren
        try:
            rez = descopera_teren(req.portal, req.judet, req.localitate, req.suprafata_subiect,
                                  fetcher=d.fetcher, max_candidati=req.max_candidati)
        except (requests.RequestException, ValueError, OSError) as e:
            raise HTTPException(502, "Portalul nu a răspuns sau conexiunea a eșuat. "
                                "Încearcă din nou sau adaugă comparabilele manual.") from e
        subiect_coord = coordonate(req.judet, req.localitate)
        return {"candidati": [{
            "url": r.url, "titlu": r.titlu,
            "pret": str(r.pret) if r.pret is not None else None,
            "suprafata": str(r.suprafata) if r.suprafata is not None else None,
            "pret_mp": str(r.pret_mp) if r.pret_mp is not None else None,
            "relevanta": r.relevanta, "nota": r.nota,
            **_geo_campuri(r.url, req.judet, req.localitate, subiect_coord),
        } for r in rez],
            "subiect_lat": subiect_coord[0] if subiect_coord else None,
            "subiect_lng": subiect_coord[1] if subiect_coord else None}

    @router.post("/api/import-anunt")
    def import_anunt(req: ImportAnuntRequest) -> dict:
        """Primește HTML-ul unei pagini de anunț (de la extensia de browser) și extrage atributele.

        Omul navighează manual; extensia trimite DOM-ul -> zero scraping automat. Vezi
        docs/spec-extensie-browser.md.
        """
        # Plasă de siguranță (ca geamănul /api/import-url): HTML ostil poate produce valori
        # implauzibile (ex. JSON-LD price=1e400 -> Decimal('Infinity')) care fac ParsedListing sa
        # ridice ValidationError (subclasa de ValueError) -> 422, nu 500 (RUNDA 9).
        try:
            p = parse_listing_html(req.html, sursa_url=req.url)
        except ValueError as e:
            raise HTTPException(422, "HTML-ul anunțului conține valori invalide sau implauzibile.") from e
        anunt = {
            "pret": str(p.pret) if p.pret is not None else None,
            "moneda": p.moneda,
            "suprafata": str(p.suprafata) if p.suprafata is not None else None,
            "suprafata_teren": str(p.suprafata_teren) if p.suprafata_teren is not None else None,
            "titlu": p.titlu, "sursa_url": p.sursa_url, "an": p.an,
            "incalzire": p.incalzire, "material": p.material, "tip_cladire": p.tip_cladire,
            "nr_camere": p.nr_camere,
            "_nota": "Preț din OFERTĂ — aplică ajustare ofertă→tranzacție (GEV 520 §4.3.4).",
        }
        # adaugă în coadă (persistent în SQLite) dacă are minim preț + suprafață
        in_coada = len(d.storage.listeaza_anunturi_importate())
        if anunt["pret"] and anunt["suprafata"]:
            in_coada = d.storage.adauga_anunt_importat(anunt)
        return {**anunt, "in_coada": in_coada}

    @router.get("/api/anunturi-importate")
    def anunturi_importate() -> dict:
        return {"anunturi": d.storage.listeaza_anunturi_importate()}

    @router.post("/api/anunturi-importate/sterge")
    def sterge_importate() -> dict:
        d.storage.sterge_anunturi_importate()
        return {"anunturi": []}

    @router.post("/api/anunturi-importate/sterge-unul")
    def sterge_un_anunt(req: StergeAnuntRequest) -> dict:
        d.storage.sterge_anunt_importat(req.url)
        return {"anunturi": d.storage.listeaza_anunturi_importate()}

    def _config_ponderi_payload() -> dict:
        efective = ponderi_store.ponderi_efective(d.storage.db_path.parent)
        return {
            "ponderi": efective,                                       # per categorie, valori efective
            "sume": {cat: sum(p.values()) for cat, p in efective.items()},   # pt normalizare UI (D1)
            "axe": AXE,                                                # ordinea axelor radarului (D2)
            "axa_atribut": AXA_ATRIBUT,                                # maparea atribut -> axa
            "editabil": True,
        }

    @router.get("/api/descopera/config-ponderi")
    def get_config_ponderi() -> dict:
        """Ponderile curente per categorie (default ponderi.py + override local) — contract D1 al lui C."""
        return _config_ponderi_payload()

    @router.post("/api/descopera/config-ponderi")
    def post_config_ponderi(req: ConfigPonderiRequest) -> dict:
        """Salveaza ponderile editate (D1). Valideaza: categorii/atribute cunoscute, valori finite,
        intregi, >= 0, iar suma EFECTIVA cumulata (override existent + aceasta editare) > 0 pe
        categorie; persista override-ul local. 422 cu mesaj daca e invalid (nu persista nimic)."""
        date_dir = d.storage.db_path.parent
        curat: dict[str, dict[str, int]] = {}
        for cat, ponderi in req.ponderi.items():
            if cat not in PONDERI_PER_CATEGORIE:
                raise HTTPException(422, f"Categorie necunoscută: {cat}")
            cunoscute = PONDERI_PER_CATEGORIE[cat]
            cat_curat: dict[str, int] = {}
            for atr, val in ponderi.items():
                if atr not in cunoscute:
                    raise HTTPException(422, f"Atribut necunoscut pentru {cat}: {atr}")
                if not math.isfinite(val):
                    raise HTTPException(422, f"Pondere invalidă (non-finită): {cat}.{atr}")
                if val < 0:
                    raise HTTPException(422, f"Pondere negativă: {cat}.{atr} = {val}")
                if val != int(val):
                    raise HTTPException(422, f"Ponderea trebuie să fie număr întreg: {cat}.{atr} = {val}")
                cat_curat[atr] = int(val)
            curat[cat] = cat_curat
        # Valideaza suma EFECTIVA cumulata (override existent + editarea curenta), nu doar defaults.
        simulat = {c: dict(p) for c, p in ponderi_store.incarca_override(date_dir).items()
                   if isinstance(p, dict)}
        for cat, vals in curat.items():
            simulat.setdefault(cat, {}).update(vals)
        efectiv = fuzioneaza_override(simulat)
        for cat in curat:
            if sum(efectiv[cat].values()) <= 0:
                raise HTTPException(
                    422, f"Ponderile efective ale categoriei '{cat}' ar însuma 0 (invalid).")
        ponderi_store.salveaza_override(date_dir, curat)
        return {"ok": True, **_config_ponderi_payload()}

    @router.get("/descoperire", response_class=HTMLResponse)
    def pagina_descoperire(request: Request) -> HTMLResponse:
        return d.templates.TemplateResponse(request, "descoperire.html", {})

    return router
