"""Genereaza un raport demo (.docx) cu date fictive realiste, pentru pachetul de review.

Foloseste motoarele reale (teren 2 etape, casa pret total, cost CIN), narativ AI daca .env are
cheie, si doua fotografii placeholder. Output: docs/exemplu-raport-demo.docx.
"""
from __future__ import annotations

import base64
import os
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# incarca .env (cheia AI) manual
env = Path(__file__).resolve().parents[1] / ".env"
if env.exists():
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.config import Settings
from evaluare.models.comparable import Adjustment, Comparable, LandComparable
from evaluare.models.meta import EvaluationMeta
from evaluare.models.property import BuildingData, CostElement, DepreciationPoint, LandData
from evaluare.report.generator import genereaza_raport


def adj(element, valoare, etapa="proprietate", tip="procentuala"):
    return Adjustment(element=element, tip=tip, valoare=Decimal(str(valoare)), etapa=etapa)


def foto_data_url(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


meta = EvaluationMeta(
    client_nume="Andrei Popescu",
    client_tip="Persoana fizica",
    beneficiar="Banca Comerciala Exemplu S.A.",
    proprietar="Andrei Popescu",
    adresa="Str. Teilor nr. 14, Comarnic, jud. Prahova",
    numar_cadastral="20145",
    carte_funciara="CF 20145 Comarnic",
    scop="Garantarea creditului ipotecar",
    tip_valoare="Valoarea de piata (SEV 104)",
    data_evaluarii="2026-05-20",
    data_raportului="2026-05-22",
    data_inspectiei="2026-05-18",
    valabilitate="6 luni de la data raportului",
    evaluator_nume="ing. Gabriela Fratila",
    evaluator_legitimatie="14288",
    moneda="EUR",
    curs_valutar=Decimal("4.9750"),
)

land = LandData(suprafata=Decimal("600"), categorie="intravilan")

building = BuildingData(
    au=Decimal("128"), acd=Decimal("162"), an_referinta=2026,
    elements=[
        CostElement(element="Structura si inchideri (casa P+1)", cod="C.1", um="mp",
                    cantitate=Decimal("162"), cost_unitar=Decimal("520"), an_pif=2011),
        CostElement(element="Finisaje si instalatii", cod="C.2", um="mp",
                    cantitate=Decimal("162"), cost_unitar=Decimal("360"), an_pif=2011),
    ],
    depreciation_points=[
        DepreciationPoint(varsta=5, depreciere=Decimal("0.05")),
        DepreciationPoint(varsta=15, depreciere=Decimal("0.16")),
        DepreciationPoint(varsta=30, depreciere=Decimal("0.35")),
    ],
)

# Grila de teren (EUR/mp) — 3 comparabile, doua etape
land_comparables = [
    LandComparable(pret_mp=Decimal("58"), suprafata=Decimal("550"), localizare="Comarnic, zona centrala",
                   adjustments=[adj("Oferta-Tranzactie", "-0.05", "tranzactie"),
                                adj("Suprafata", "-0.03"), adj("Deschidere", "0.05")]),
    LandComparable(pret_mp=Decimal("64"), suprafata=Decimal("700"), localizare="Comarnic, Poiana",
                   adjustments=[adj("Oferta-Tranzactie", "-0.05", "tranzactie"),
                                adj("Localizare", "-0.07"), adj("Suprafata", "0.04"),
                                adj("Acces", "-0.05")]),
    LandComparable(pret_mp=Decimal("49"), suprafata=Decimal("600"), localizare="Comarnic, Ghiosesti",
                   adjustments=[adj("Oferta-Tranzactie", "-0.05", "tranzactie"),
                                adj("Localizare", "0.05"), adj("Deschidere", "0.03")]),
]

# Grila de casa (pret total EUR) — 3 comparabile, doua etape (cu arie utila ca ajustare valorica)
comparables = [
    Comparable(sursa="https://www.imobiliare.ro/exemplu-1", pret=Decimal("158000"),
               suprafata=Decimal("170"),
               adjustments=[adj("Negociere", "-0.05", "tranzactie"),
                            adj("Localizare", "-0.03"),
                            adj("Arie utila", "-12000", tip="valorica"),
                            adj("PIF / vechime", "0.04"), adj("Finisaje", "-0.03")]),
    Comparable(sursa="https://www.storia.ro/exemplu-2", pret=Decimal("142000"),
               suprafata=Decimal("150"),
               adjustments=[adj("Negociere", "-0.05", "tranzactie"),
                            adj("Localizare", "0.02"),
                            adj("Arie utila", "-6000", tip="valorica"),
                            adj("Finisaje", "0.03")]),
    Comparable(sursa="https://www.imobiliare.ro/exemplu-3", pret=Decimal("169000"),
               suprafata=Decimal("185"),
               adjustments=[adj("Negociere", "-0.05", "tranzactie"),
                            adj("Localizare", "-0.05"),
                            adj("Arie utila", "-18000", tip="valorica"),
                            adj("Curte", "-0.02"), adj("Sistem incalzire", "0.03")]),
]

fotodir = Path(os.environ["TEMP"]) / "demo"
photos = [foto_data_url(fotodir / "fata.png"), foto_data_url(fotodir / "curte.png")]

inp = EvaluationInput(
    meta=meta, land=land, building=building,
    comparables=comparables, land_comparables=land_comparables,
    metoda="piata", photos=photos,
)

client = Settings.from_env().narrative_client()
print("Narativ AI:", type(client).__name__ if client else "fallback (fara cheie)")
ctx = construieste_context(inp, client=client)

print("Valoare teren (grila):", ctx.land_result.valoare_teren if ctx.land_result else None)
print("Valoare prin cost (CIN+teren):", ctx.cost_result.valoare_cost if ctx.cost_result else None)
print("Valoare prin piata (total):", ctx.market_result.valoare_piata if ctx.market_result else None)
print("Valoare finala:", ctx.reconciled.valoare_finala)
print("Alocare constructii:", ctx.alocare_constructii)

out = Path(__file__).resolve().parents[2] / "docs" / "exemplu-raport-demo.docx"
genereaza_raport(ctx, out)
print("Raport scris:", out)
