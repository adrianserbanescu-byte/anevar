"""Raport real pe subiectul din Breaza de Sus (date extrase din anunt) + 3 comparabile reale.

Subiect + preturile/suprafetele comparabilelor = REALE (extrase de aplicatie).
Ajustarile din grile + grila de teren + costurile unitare = EXEMPLU (de confirmat de evaluator).
Output: docs/exemplu-raport-breaza.docx
"""
from __future__ import annotations

import base64
import os
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
env = Path(__file__).resolve().parents[1] / ".env"
if env.exists():
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.config import Settings
from evaluare.importers.url_parser import fetch_html, parse_listing_html
from evaluare.models.comparable import Adjustment, Comparable, LandComparable
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.report.generator import genereaza_raport


def adj(el, val, etapa="proprietate", tip="procentuala"):
    return Adjustment(element=el, tip=tip, valoare=Decimal(str(val)), etapa=etapa)


def foto(path):
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


# --- Subiect (extras din anunt storia, confirmat la inspectie) ---
SUBIECT_ACD = Decimal("220")
SUBIECT_AU = Decimal("180")
SUBIECT_TEREN = Decimal("700")
RATA_ARIE = Decimal("650")    # EUR/mp utili (ajustare arie utila) - EXEMPLU
RATA_TEREN = Decimal("40")    # EUR/mp teren (ajustare suprafata teren) - EXEMPLU

URLS = [
    "https://www.imobiliare.ro/oferta/casa-individuala-de-vanzare-breaza-mobilata-6-camere-275474743",
    "https://www.imobiliare.ro/oferta/casa-individuala-de-vanzare-breaza-gura-beliei-5-camere-275567511",
    "https://www.imobiliare.ro/oferta/casa-individuala-de-vanzare-breaza-6-camere-49309493",
]

comparabile = []
print("Comparabile reale extrase:")
for u in URLS:
    p = parse_listing_html(fetch_html(u), u)
    supr = p.suprafata or SUBIECT_ACD
    teren = p.suprafata_teren or SUBIECT_TEREN
    # ajustari EXEMPLU: negociere + arie utila (EUR) + teren (EUR) + localizare
    d_arie = (SUBIECT_ACD - supr) * RATA_ARIE          # comp mai mare -> negativ
    d_teren = (SUBIECT_TEREN - teren) * RATA_TEREN      # comp cu teren mai mic -> pozitiv
    a = [adj("Negociere", "-0.05", "tranzactie"),
         adj("Arie utila (EUR/mp x delta)", str(d_arie), tip="valorica"),
         adj("Suprafata teren (EUR/mp x delta)", str(d_teren), tip="valorica"),
         adj("Localizare", "-0.03")]
    comparabile.append(Comparable(sursa=u, pret=p.pret, suprafata=supr, adjustments=a))
    print(f"  {p.pret} EUR | casa {supr} mp | teren {teren} mp | an {p.an} | {u.split('/')[-1]}")

# --- Grila de teren (EXEMPLU - de inlocuit cu anunturi reale de teren) ---
land_comparables = [
    LandComparable(pret_mp=Decimal("48"), suprafata=Decimal("650"), localizare="Breaza, intravilan",
                   adjustments=[adj("Oferta-Tranzactie", "-0.05", "tranzactie"),
                                adj("Suprafata", "-0.03"), adj("Deschidere", "0.03")]),
    LandComparable(pret_mp=Decimal("55"), suprafata=Decimal("800"), localizare="Breaza, zona centrala",
                   adjustments=[adj("Oferta-Tranzactie", "-0.05", "tranzactie"),
                                adj("Localizare", "-0.05"), adj("Suprafata", "-0.05")]),
    LandComparable(pret_mp=Decimal("40"), suprafata=Decimal("700"), localizare="Breaza de Sus",
                   adjustments=[adj("Oferta-Tranzactie", "-0.05", "tranzactie"),
                                adj("Localizare", "0.04")]),
]

meta = EvaluationMeta(
    client_nume="Client demonstrativ", client_tip="Persoana fizica",
    beneficiar="Banca Comerciala Exemplu S.A.", proprietar="Client demonstrativ",
    adresa="Breaza de Sus, jud. Prahova", numar_cadastral="2xxxx (demo)",
    carte_funciara="CF xxxxx Breaza (demo)", scop="Garantarea creditului ipotecar",
    tip_valoare="Valoarea de piață (SEV 102)",
    data_evaluarii="2026-05-25", data_raportului="2026-05-27", data_inspectiei="2026-05-23",
    valabilitate="6 luni", evaluator_nume="[Nume evaluator autorizat ANEVAR]",
    evaluator_legitimatie="[nr. legitimatie]", moneda="EUR", curs_valutar=Decimal("4.9750"),
)
land = LandData(suprafata=SUBIECT_TEREN, categorie="intravilan",
                utilitati=["apă curentă", "energie electrică", "gaze naturale", "canalizare"],
                restrictii_urbanism="teren intravilan; POT max. 35%, CUT max. 0,9 (de confirmat prin Certificat de Urbanism)",
                acces="drum public asfaltat")
building = BuildingData(
    au=SUBIECT_AU, acd=SUBIECT_ACD, an_referinta=2026,
    elements=[
        CostElement(element="Structura beton + pereti tip sandwich, inchideri", cod="C.1", um="mp",
                    cantitate=SUBIECT_ACD, cost_unitar=Decimal("470"), an_pif=2010),
        CostElement(element="Finisaje, instalatii, incalzire centrala gaz", cod="C.2", um="mp",
                    cantitate=SUBIECT_ACD, cost_unitar=Decimal("360"), an_pif=2010),
    ],
    depreciation_points=[DepreciationPoint(varsta=5, depreciere=Decimal("0.05")),
                         DepreciationPoint(varsta=15, depreciere=Decimal("0.16")),
                         DepreciationPoint(varsta=30, depreciere=Decimal("0.35"))],
)

demo = Path(os.environ["TEMP"]) / "demo"
photos = [foto(demo / "fata.png"), foto(demo / "curte.png")] if (demo / "fata.png").exists() else []

inp = EvaluationInput(meta=meta, land=land, building=building, comparables=comparabile,
                      land_comparables=land_comparables, metoda="piata", photos=photos)
client = Settings.from_env().narrative_client()
print("Narativ AI:", type(client).__name__ if client else "fallback")
ctx = construieste_context(inp, client=client)
print("Valoare teren (grila):", ctx.land_result.valoare_teren)
print("Valoare cost (CIN+teren):", ctx.cost_result.valoare_cost)
print("Valoare piata (total ales):", ctx.market_result.valoare_piata)
print("Valoare finala:", ctx.reconciled.valoare_finala, "| alocare constructii:", ctx.alocare_constructii)
out = Path(__file__).resolve().parents[2] / "docs" / "exemplu-raport-breaza.docx"
genereaza_raport(ctx, out, adnotari=True)   # raport de review -> cu note de provenienta
print("Raport scris:", out)
