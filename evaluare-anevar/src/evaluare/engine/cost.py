"""Abordarea prin cost: CIB segregat, Vcp, CIN si cele trei forme de depreciere.

Bazele evaluarii 2024 (abordarea prin cost) defineste trei forme de depreciere,
toate alimentand `compute_cin` ca fractii in [0, 1]:
  * fizica   — tabel de interpolare (`interpolate_depreciation`) SAU metoda liniara
               pe durata de viata (`depreciere_fizica_liniara`);
  * functionala — supradimensionare = (cost reproducere - cost inlocuire) / reproducere
               (`depreciere_functionala_supradimensionare`);
  * externa/economica — pierdere de utilitate / valoare de referinta
               (`depreciere_externa_din_pierdere`).
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from evaluare.models.property import BuildingData, CostElement, DepreciationPoint
from evaluare.models.results import CostResult


def compute_cib(elements: list[CostElement]) -> Decimal:
    """Cost de inlocuire brut = suma costurilor de nou ale elementelor."""
    return sum((el.cost_nou() for el in elements), Decimal("0"))


def compute_vcp(elements: list[CostElement], an_referinta: int) -> Decimal:
    """Varsta cronologica ponderata = sum(varsta_i * cost_i) / sum(cost_i)."""
    total_cost = compute_cib(elements)
    if total_cost == Decimal("0"):
        return Decimal("0")
    weighted = sum(
        (Decimal(el.varsta(an_referinta)) * el.cost_nou() for el in elements),
        Decimal("0"),
    )
    return weighted / total_cost


def interpolate_depreciation(
    vcp: Decimal, points: list[DepreciationPoint]
) -> Decimal:
    """Depreciere fizica prin interpolare liniara intre punctele tabelului.

    Dfn = D1 + (D2 - D1) / (V2 - V1) * (Vcp - V1)
    Sub/peste limitele tabelului se foloseste primul/ultimul punct (clamp).
    """
    if not points:
        raise ValueError("Tabelul de depreciere este gol.")
    ordered = sorted(points, key=lambda p: p.varsta)
    if vcp <= ordered[0].varsta:
        return ordered[0].depreciere
    if vcp >= ordered[-1].varsta:
        return ordered[-1].depreciere
    for low, high in zip(ordered, ordered[1:], strict=False):  # perechi consecutive (lungimi diferite intentionat)
        if low.varsta <= vcp <= high.varsta:
            v1, d1 = Decimal(low.varsta), low.depreciere
            v2, d2 = Decimal(high.varsta), high.depreciere
            return d1 + (d2 - d1) / (v2 - v1) * (vcp - v1)
    raise AssertionError("interpolare: caz logic neatins")


def depreciere_fizica_liniara(
    varsta: Decimal, durata_viata_totala: Decimal
) -> Decimal:
    """Depreciere fizica nerecuperabila prin metoda LINIARA pe durata de viata.

    Bazele evaluarii 2024 (cap. abordarea prin cost): deprecierea fizica
    nerecuperabila se cuantifica prin raportul dintre vechime si durata de viata
    fizica totala asteptata, restul fiind durata de viata ramasa.

        Dfn = varsta_efectiva / durata_viata_fizica_totala

    Alternativa la interpolarea pe tabel (`interpolate_depreciation`) — ambele
    intorc o fractie Dfn in [0, 1] care intra in `compute_cin`. `varsta` poate fi
    varsta cronologica (Vcp) sau varsta EFECTIVA (ajustata dupa inspectie: mai
    mica daca s-a renovat, mai mare daca nu s-a intretinut — brosura §675-679).
    """
    if durata_viata_totala <= Decimal("0"):
        raise ValueError("Durata de viata totala trebuie sa fie > 0.")
    if varsta < Decimal("0"):
        raise ValueError("Varsta nu poate fi negativa.")
    raport = varsta / durata_viata_totala
    # Clamp: o constructie care si-a depasit durata de viata e depreciata fizic 100%,
    # nu peste (un Dfn > 1 ar da CIN negativ in compute_cin).
    return min(raport, Decimal("1"))


def depreciere_functionala_supradimensionare(
    cost_reproducere: Decimal, cost_inlocuire: Decimal
) -> Decimal:
    """Depreciere FUNCTIONALA din supradimensionare (cheltuieli de capital excedentare).

    Bazele evaluarii 2024 §717-724: pentru supradimensionare (ex. hala cu inaltime
    excesiva), deprecierea functionala = diferenta dintre costul curent de
    REPRODUCERE (replica fidela, mai mare) si costul curent de INLOCUIRE (utilitate
    echivalenta, mai mic), exprimata ca FRACTIE din costul de reproducere:

        C_nf = (cost_reproducere - cost_inlocuire) / cost_reproducere

    Intoarce o fractie in [0, 1] direct utilizabila ca `functional_depreciation`
    (C_nf) in `compute_cin`. Daca cele doua costuri sunt egale (fara
    supradimensionare), rezulta 0.
    """
    if cost_reproducere <= Decimal("0"):
        raise ValueError("Costul de reproducere trebuie sa fie > 0.")
    if cost_inlocuire < Decimal("0"):
        raise ValueError("Costul de inlocuire nu poate fi negativ.")
    if cost_inlocuire > cost_reproducere:
        raise ValueError(
            "Costul de inlocuire (utilitate echivalenta) nu poate depasi costul de "
            "reproducere (replica) — supradimensionarea inseamna reproducere >= inlocuire."
        )
    return (cost_reproducere - cost_inlocuire) / cost_reproducere


def depreciere_externa_din_pierdere(
    pierdere_utilitate: Decimal, valoare_referinta: Decimal
) -> Decimal:
    """Depreciere ECONOMICA/EXTERNA ca fractie a pierderii de utilitate.

    Bazele evaluarii 2024 §742-753: deprecierea economica (externa) = pierderea de
    utilitate cauzata de factori economici sau de localizare, independenti de activ
    (deteriorarea localizarii, scaderea cererii, schimbari demografice/de mediu).
    Cuantificata ca raport intre pierderea de utilitate/valoare atribuibila acestor
    factori externi si o valoare de referinta (de obicei CIN dupa deprecierea fizica
    si functionala, sau valoarea contributorie a constructiei):

        C_ex = pierdere_utilitate / valoare_referinta

    Intoarce o fractie in [0, 1] utilizabila ca `external_depreciation` (C_ex) in
    `compute_cin`.
    """
    if valoare_referinta <= Decimal("0"):
        raise ValueError("Valoarea de referinta trebuie sa fie > 0.")
    if pierdere_utilitate < Decimal("0"):
        raise ValueError("Pierderea de utilitate nu poate fi negativa.")
    return min(pierdere_utilitate / valoare_referinta, Decimal("1"))


def compute_cin(
    cib: Decimal, dfn: Decimal, c_nf: Decimal, c_ex: Decimal
) -> Decimal:
    """Cost de inlocuire net = CIB * (1-Dfn) * (1-C_nf) * (1-C_ex).

    Cele trei forme de depreciere se aplica MULTIPLICATIV (in cascada), nu aditiv:
    deprecierea functionala si externa se aplica pe ce a ramas dupa deprecierea
    fizica. Fiecare argument este o fractie in [0, 1] — vezi `interpolate_depreciation`
    / `depreciere_fizica_liniara` (Dfn), `depreciere_functionala_supradimensionare`
    (C_nf) si `depreciere_externa_din_pierdere` (C_ex).
    """
    one = Decimal("1")
    return cib * (one - dfn) * (one - c_nf) * (one - c_ex)


def evaluate_cost(
    building: BuildingData, valoare_teren: Decimal | None = None
) -> CostResult:
    """Ruleaza abordarea prin cost completa pentru o constructie."""
    cib = compute_cib(building.elements)
    vcp = compute_vcp(building.elements, building.an_referinta)
    # Politica unica de rotunjire: interpolam deprecierea pe varsta EXACTA. Rotunjirea lui vcp la 0.01
    # INAINTE de interpolare introducea un mic efect de PRAG pe Dfn (vcp sare in trepte de 0.01 an).
    # vcp se rotunjeste DOAR pentru afisarea/raportarea valorii (CostResult.vcp), nu pentru calcul.
    # Doua metode de depreciere fizica (aditiv): TABEL de interpolare (implicit, daca exista puncte)
    # SAU metoda LINIARA pe durata de viata (daca nu exista puncte dar e data durata_viata_totala).
    if building.depreciation_points:
        dfn = interpolate_depreciation(vcp, building.depreciation_points)
    elif building.durata_viata_totala is not None:
        dfn = depreciere_fizica_liniara(vcp, building.durata_viata_totala)
    else:
        raise ValueError(
            "Abordarea prin cost necesita fie un tabel de depreciere "
            "(depreciation_points), fie durata_viata_totala pentru metoda liniara."
        )
    vcp = vcp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    cin = compute_cin(
        cib, dfn, building.functional_depreciation, building.external_depreciation
    )
    valoare_cost = None
    if valoare_teren is not None:
        valoare_cost = cin + valoare_teren
    return CostResult(
        valoare_teren=valoare_teren,
        cib=cib,
        vcp=vcp,
        depreciere_fizica=dfn,
        cin=cin,
        valoare_cost=valoare_cost,
    )
