"""Evaluarea terenului prin grila de comparatie directa (EUR/mp).

Metodologia reala GBF/ANEVAR are DOUA etape (validata pe 4 grile reale: Maneciu, Brasov,
Busteni, Breaza):
  1. Etapa de TRANZACTIE (oferta->tranzactie, drept, finantare, conditii vanzare, cheltuieli,
     conditiile pietei) — ajustarile se aplica SECVENTIAL (compus) -> pret de baza.
  2. Etapa de PROPRIETATE (caracteristici fizice/juridice) — ajustarile se aplica ADITIV pe
     pretul de baza: final = baza * (1 + suma % proprietate) + suma EUR proprietate.

Ajustarea bruta (criteriul de selectie) = suma valorilor absolute ale ajustarilor procentuale
din etapa de proprietate (etapa de tranzactie NU se contorizeaza). Comparabilul ales = cel cu
ajustare bruta minima. Valoarea terenului = pret/mp corectat ales * suprafata subiectului.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, Field

from evaluare.engine.metodologie import IMPLICIT, MetodologieConfig
from evaluare.models.comparable import Adjustment, LandComparable
from evaluare.models.results import LandResult

_UNU = Decimal("1")
_ZERO = Decimal("0")
_BANI = Decimal("0.01")


def _pret_baza_tranzactie(comp: LandComparable) -> Decimal:
    """Pretul dupa etapa de tranzactie (ajustari secventiale, compus)."""
    pret = comp.pret_mp
    for adj in comp.adjustments:
        if adj.etapa != "tranzactie":
            continue
        if adj.tip == "procentuala":
            pret = pret * (_UNU + adj.valoare)
        else:
            pret = pret + adj.valoare
    return pret


def pret_mp_corectat(comp: LandComparable) -> Decimal:
    """Pretul/mp corectat final: etapa de tranzactie (compus) + etapa de proprietate (aditiv)."""
    baza = _pret_baza_tranzactie(comp)
    suma_pct = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return baza * (_UNU + suma_pct) + suma_eur


def _eur_ca_fractie(comp: LandComparable) -> Decimal:
    """Ajustarile valorice (EUR) de proprietate, SUMATE ALGEBRIC (cu semn), ca fractie din baza.
    Pentru ajustarea NETA (suma cu semn)."""
    baza = _pret_baza_tranzactie(comp)
    suma_eur = sum((a.valoare for a in comp.adjustments
                    if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return suma_eur / baza if baza != 0 else _ZERO


def _eur_brut_fractie(comp: LandComparable) -> Decimal:
    """Ajustarile valorice (EUR) de proprietate, ABS-FIECARE-APOI-SUMA, ca fractie din baza.

    Pentru ajustarea BRUTA (criteriul de selectie) — la fel ca `market.ajustare_bruta`: ajustarile de
    semn opus NU se anuleaza (altfel un comparabil greu ajustat ar parea „cel mai usor" si ar fi ales gresit).
    """
    baza = _pret_baza_tranzactie(comp)
    suma = sum((abs(a.valoare) for a in comp.adjustments
                if a.etapa == "proprietate" and a.tip == "valorica"), _ZERO)
    return suma / baza if baza != 0 else _ZERO


def ajustare_bruta(comp: LandComparable, include_eur: bool = True) -> Decimal:
    """Ajustarea bruta de proprietate (criteriul de selectie): suma valorilor ABSOLUTE.

    Procentualele direct; cele VALORICE (EUR) abs-fiecare-apoi-suma / baza DOAR daca `include_eur`
    (M1, default True = CONSISTENT cu abordarea prin piata; False = doar procentuale, varianta veche).
    """
    g = sum((abs(a.valoare) for a in comp.adjustments
             if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    if include_eur:
        g += _eur_brut_fractie(comp)
    return g


def ajustare_neta(comp: LandComparable, include_eur: bool = True) -> Decimal:
    """Suma algebrica a ajustarilor de proprietate (procentuale + EUR/baza daca `include_eur`)."""
    n = sum((a.valoare for a in comp.adjustments
             if a.etapa == "proprietate" and a.tip == "procentuala"), _ZERO)
    if include_eur:
        n += _eur_ca_fractie(comp)
    return n


def evaluate_land(
    comparables: list[LandComparable], suprafata_subiect: Decimal,
    cfg: MetodologieConfig = IMPLICIT,
) -> LandResult:
    """Ruleaza grila de teren. Valoarea = MEDIA pretului/mp corectat al celor mai similare
    `cfg.nr_comparabile_medie` comparabile (M2; default = minimul legal). N=1 -> comparabilul unic.

    `cfg.teren_selectie_include_eur` (M1) decide daca selectia numara si ajustarile valorice (EUR).
    """
    if not comparables:
        raise ValueError("Sunt necesare comparabile de teren.")
    inc = cfg.teren_selectie_include_eur
    preturi = [pret_mp_corectat(c) for c in comparables]
    brute = [ajustare_bruta(c, inc) for c in comparables]
    nete = [ajustare_neta(c, inc) for c in comparables]
    ordine = sorted(range(len(comparables)), key=lambda i: brute[i])   # cele mai similare intai
    index = ordine[0]
    n = min(max(1, cfg.nr_comparabile_medie), len(comparables))
    pret_ales = sum((preturi[i] for i in ordine[:n]), _ZERO) / n       # media top-N €/mp (N=1 -> unic)
    valoare = pret_ales * suprafata_subiect
    return LandResult(
        preturi_mp_corectate=preturi, ajustari_brute=brute, ajustari_nete=nete,
        index_selectat=index, indici_mediati=sorted(ordine[:n]),   # comparabilele mediate (M2)
        pret_mp_ales=pret_ales, valoare_teren=valoare,
    )


# --------------------------------------------------------------------------- #
# I-11 — metoda REZIDUALĂ / a parcelării terenului (abordare opțională, ADITIVĂ).
# Sursa: articol „Rolul pretului in tranzactiile cu terenuri" (perspectiva dezvoltatorului) +
# SEV 233 / GEV 630 (terenuri dezvoltabile). Pentru un teren construibil, valoarea „pe lot"
# derivă din ce produce terenul: valoarea dezvoltării − costuri − profit dezvoltator.
# NU înlocuiește comparația EUR/mp; este o a doua metodă recunoscută, pe care evaluatorul o aplică
# când terenul e dezvoltabil. Funcția de comparație de mai sus rămâne neschimbată.
# --------------------------------------------------------------------------- #
class DateTerenRezidual(BaseModel):
    """Intrările metodei reziduale a terenului (toate sumele în aceeași monedă).

    Cele 5 întrebări ale dezvoltatorului din articol: ce/câte pot construi, la ce preț le vând,
    cât durează, care sunt costurile. Modelul le condensează în:
      - `nr_loturi` × `pret_lot` = valoarea brută a dezvoltării (GDV), SAU `valoare_dezvoltare`
        direct (când dezvoltarea nu e o simplă parcelare în loturi identice);
      - `costuri_dezvoltare` = costuri de construire/infrastructură/vânzare/finanțare;
      - `profit_dezvoltator` = marja cerută de dezvoltator (fracție din GDV SAU sumă fixă).
    Valoarea terenului = GDV − costuri − profit. Rezultat negativ → teren nefezabil pentru
    dezvoltarea propusă (semnalat ca eroare, nu valoare negativă falsă).
    """

    # Varianta „parcelare": nr. loturi × preț/lot. Lăsați 0 dacă dați `valoare_dezvoltare` direct.
    nr_loturi: int = Field(default=0, ge=0)
    pret_lot: Decimal = Field(default=_ZERO, ge=0)
    # Varianta directă: valoarea brută a dezvoltării (GDV). Ignorat dacă nr_loturi > 0.
    valoare_dezvoltare: Decimal = Field(default=_ZERO, ge=0)
    costuri_dezvoltare: Decimal = Field(default=_ZERO, ge=0)
    # Profitul dezvoltatorului: ca FRACȚIE din GDV (ex. 0.20 = 20%) SAU ca sumă fixă.
    profit_procent: Decimal = Field(default=_ZERO, ge=0)
    profit_suma: Decimal = Field(default=_ZERO, ge=0)

    def valoare_bruta_dezvoltare(self) -> Decimal:
        """GDV: nr_loturi × pret_lot dacă nr_loturi > 0, altfel `valoare_dezvoltare`."""
        if self.nr_loturi > 0:
            return Decimal(self.nr_loturi) * self.pret_lot
        return self.valoare_dezvoltare


class RezultatTerenRezidual(BaseModel):
    """Rezultatul metodei reziduale a terenului."""

    valoare_dezvoltare: Decimal      # GDV (valoarea brută a dezvoltării)
    costuri_dezvoltare: Decimal
    profit_dezvoltator: Decimal
    valoare_teren: Decimal


def teren_rezidual(d: DateTerenRezidual) -> RezultatTerenRezidual:
    """Valoare teren = GDV − costuri de dezvoltare − profit dezvoltator (metoda reziduală).

    Profitul dezvoltatorului = `profit_suma` + `profit_procent` × GDV (se pot combina sau folosi
    doar una). Ridică `ValueError` dacă GDV ≤ 0 (fără dezvoltare nu există reziduu) sau dacă
    valoarea terenului rezultată e ≤ 0 (dezvoltarea propusă nu lasă valoare reziduală terenului).
    """
    gdv = d.valoare_bruta_dezvoltare()
    if gdv <= 0:
        raise ValueError(
            "Valoarea brută a dezvoltării (GDV) trebuie să fie > 0; "
            "specificați nr_loturi × pret_lot sau valoare_dezvoltare."
        )
    profit = (d.profit_suma + d.profit_procent * gdv).quantize(_BANI, rounding=ROUND_HALF_UP)
    valoare = (gdv - d.costuri_dezvoltare - profit).quantize(_BANI, rounding=ROUND_HALF_UP)
    if valoare <= 0:
        raise ValueError(
            f"Valoarea reziduală a terenului rezultată este <= 0 ({valoare}); "
            "dezvoltarea propusă nu lasă valoare reziduală terenului "
            "(verificați GDV, costurile și profitul dezvoltatorului)."
        )
    return RezultatTerenRezidual(
        valoare_dezvoltare=gdv.quantize(_BANI, rounding=ROUND_HALF_UP),
        costuri_dezvoltare=d.costuri_dezvoltare.quantize(_BANI, rounding=ROUND_HALF_UP),
        profit_dezvoltator=profit,
        valoare_teren=valoare,
    )


# --------------------------------------------------------------------------- #
# G-N4 — TEREN AGRICOL: comparația vânzărilor cu ajustare pe NOTA DE BONITARE a solului.
#
# ATENȚIE — poziția ANEVAR (PdV „metoda comparației prin bonitare", reluată în SEV 2025
# GEV 630 §86): „metoda comparației prin bonitare" în sensul FORMULEI matematice
# (Decizia PMB 79/1992 + Dispozițiile PMB 421/1992, 191/1993, 827/1994), care derivă o
# valoare DIRECT dintr-un coeficient/grilă de bonitate, NU este o metodă de evaluare a
# terenurilor recunoscută — folosirea ei = abatere disciplinară sancționabilă. NU o
# implementăm și nu trebuie folosită.
#
# Ce face funcția de mai jos NU este acea formulă interzisă. Este metoda RECUNOSCUTĂ a
# comparației vânzărilor (GEV 630 §82–§83), în care nota de bonitare a solului intră DOAR
# ca ELEMENT DE COMPARAȚIE (alături de localizare, acces, suprafață, deschidere etc.,
# GEV 630 §90) — un factor de AJUSTARE între subiect și comparabil, nu un substitut de
# piață. Cu alte cuvinte: bonitarea ajustează prețul comparabilelor REALE de pe piață;
# nu produce valoarea în absența pieței.
#
# Limitări respectate (din PdV):
#   • Bonitarea = factor de comparație, NU formulă de valoare. Funcția produce o `Adjustment`
#     care se aplică în grila de comparație €/mp existentă; nu există „valoare din bonitate".
#   • Comparabilele rămân tranzacții/oferte reale de teren agricol (`LandComparable`). Dacă
#     nu există comparabile, metoda nu se aplică — nu se inventează valoare (vezi G-N5,
#     capitalizarea rentei funciare, ca alternativă §99, în afara acestui scope).
#   • ADITIV: comparația €/mp existentă (`evaluate_land`) rămâne NEATINSĂ. Această metodă
#     doar PRE-CALCULEAZĂ ajustarea de bonitare și o adaugă ca element de comparație.
# --------------------------------------------------------------------------- #

# Clasa de calitate / bonitate a solului în RO: 1..5, unde 1 = cea mai bună (`LandData.clasa_calitate`).
# Un sol de clasă mai bună (nr. mai mic) e mai productiv → mai scump pe piață. Ajustarea adusă unui
# comparabil îl aduce la calitatea SUBIECTULUI: dacă subiectul e MAI BUN ca solul comparabilului,
# prețul comparabilului se majorează (+), altfel se diminuează (−).
_CLASA_MIN = 1
_CLASA_MAX = 5


class AjustareBonitare(BaseModel):
    """Parametrii ajustării de bonitare a solului pentru un comparabil agricol.

    `procent_pe_clasa` = diferența procentuală de valoare estimată de evaluator între două
    clase de calitate succesive ale solului (ex. 0.08 = ~8% pe clasă), extrasă/justificată
    din piață — NU un coeficient impus de o grilă (acela ar fi metoda interzisă). Ajustarea
    pe comparabil = `procent_pe_clasa` × (clasa_comparabil − clasa_subiect), pentru că o clasă
    cu număr mai mare = sol mai slab. Plafonată ca să nu degenereze pe diferențe extreme.
    """

    procent_pe_clasa: Decimal = Field(default=Decimal("0.08"), ge=0, le=1)
    # Plafon (în valoare absolută) al ajustării totale de bonitare per comparabil. Apără contra
    # unei ajustări nerealiste (ex. 4 clase × procent mare) care ar contamina selecția.
    plafon: Decimal = Field(default=Decimal("0.40"), gt=0, le=1)


# Singleton de default (ca `IMPLICIT` pt MetodologieConfig) — evită apelul în argumentele implicite.
BONITARE_IMPLICIT = AjustareBonitare()


def _valideaza_clasa(clasa: int, eticheta: str) -> int:
    if not (_CLASA_MIN <= clasa <= _CLASA_MAX):
        raise ValueError(
            f"Clasa de calitate (bonitate) a solului {eticheta} trebuie să fie {_CLASA_MIN}..{_CLASA_MAX} "
            f"(1 = cea mai bună); primit: {clasa}."
        )
    return clasa


def ajustare_bonitare(
    clasa_subiect: int, clasa_comparabil: int, p: AjustareBonitare = BONITARE_IMPLICIT,
) -> Decimal:
    """Ajustarea procentuală de BONITARE adusă unui comparabil agricol (element de comparație).

    Adu comparabilul la calitatea solului subiectului: dacă subiectul e mai bun (clasă cu număr
    mai mic) decât comparabilul, prețul comparabilului se MAJOREAZĂ (+); invers, se diminuează (−).
    Valoare = clamp(procent_pe_clasa × (clasa_comparabil − clasa_subiect), ±plafon).
    NU este o valoare; e o corecție de comparație ce intră în grila €/mp existentă.
    """
    _valideaza_clasa(clasa_subiect, "subiectului")
    _valideaza_clasa(clasa_comparabil, "comparabilului")
    brut = p.procent_pe_clasa * Decimal(clasa_comparabil - clasa_subiect)
    if brut > p.plafon:
        return p.plafon
    if brut < -p.plafon:
        return -p.plafon
    return brut


def aplica_bonitare(
    comparables: list[LandComparable], clasa_subiect: int,
    clase_comparabile: list[int], p: AjustareBonitare = BONITARE_IMPLICIT,
) -> list[LandComparable]:
    """Întoarce COPII ale comparabilelor cu un `Adjustment` „Bonitare sol" adăugat (etapa
    proprietate, procentual), pregătite pentru `evaluate_land`. ADITIV: comparabilele primite
    NU sunt mutate; comparația €/mp rămâne intactă, doar capătă elementul de comparație bonitare.

    `clase_comparabile[i]` = clasa de calitate a solului comparabilului i (1..5). O ajustare de
    bonitare 0 (subiect și comparabil în aceeași clasă) NU se adaugă, ca să nu polueze grila.
    """
    if len(clase_comparabile) != len(comparables):
        raise ValueError(
            f"Numărul claselor de calitate ({len(clase_comparabile)}) trebuie să fie egal cu "
            f"numărul comparabilelor ({len(comparables)})."
        )
    _valideaza_clasa(clasa_subiect, "subiectului")
    rezultat: list[LandComparable] = []
    for comp, clasa_c in zip(comparables, clase_comparabile, strict=True):
        pct = ajustare_bonitare(clasa_subiect, clasa_c, p)
        adj = list(comp.adjustments)
        if pct != _ZERO:
            adj.append(Adjustment(
                element="Bonitare sol",
                tip="procentuala",
                valoare=pct,
                etapa="proprietate",
                justificare=(
                    f"Element de comparație (GEV 630 §90): clasă calitate sol comparabil {clasa_c} "
                    f"vs. subiect {clasa_subiect}. NU metoda comparației prin bonitare (formula PMB "
                    f"79/1992), interzisă de GEV 630 §86."
                ),
            ))
        rezultat.append(comp.model_copy(update={"adjustments": adj}))
    return rezultat


def evaluate_land_agricol(
    comparables: list[LandComparable], suprafata_subiect: Decimal,
    clasa_subiect: int, clase_comparabile: list[int],
    p: AjustareBonitare = BONITARE_IMPLICIT, cfg: MetodologieConfig = IMPLICIT,
) -> LandResult:
    """Comparația vânzărilor pentru teren AGRICOL, cu nota de bonitare a solului ca element de
    comparație. Pre-calculează ajustarea de bonitare (subiect vs. comparabil) și o adaugă în grila
    €/mp standard, apoi rulează `evaluate_land` neschimbat.

    Metodă RECUNOSCUTĂ (comparația vânzărilor, GEV 630 §82–§83), NU formula interzisă a „comparației
    prin bonitare" (GEV 630 §86). Aditivă față de `evaluate_land` — nu o înlocuiește.
    """
    cu_bonitare = aplica_bonitare(comparables, clasa_subiect, clase_comparabile, p)
    return evaluate_land(cu_bonitare, suprafata_subiect, cfg)
