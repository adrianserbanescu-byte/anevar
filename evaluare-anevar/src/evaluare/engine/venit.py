"""Abordarea prin venit — capitalizare directă (NOI ÷ rată de capitalizare).

Îmbogățit cu metodologia din articolele ANEVAR (Adrian Nicolescu, set `articole-piata-2`):
  - I-7: derivarea ratei de capitalizare din piață (cele 4 metode vânzare-închiriere /
    extracție din comparabile) + build-up (metoda deductivă) + validare de plauzibilitate +
    documentarea sursei ratei (cerut și de SEV 103 A20.34). Input-ul liber rămâne fallback.
  - I-8: defalcarea cheltuielilor de exploatare (OPEX) pe poziții (service charge) + distincția
    chirie brută vs. netă + nota „fond de rulment ≠ OPEX". Scalarul unic rămâne modul simplu.
  - I-19: valoarea terminală DCF prin formula Gordon (creștere perpetuă) și exit-cap
    (rată terminală), ca opțiuni; suma manuală rămâne fallback.

Toate adăugirile sunt ADITIVE și backward-compatible: comportamentul existent (scalar OPEX,
rată liberă, valoare reziduală manuală) este păstrat neschimbat.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, Field

from evaluare.engine.abordari import RezultatAbordare

_BANI = Decimal("0.01")
_ZERO = Decimal("0")
_UNU = Decimal("1")

# I-7 — interval de plauzibilitate pentru rata de capitalizare (fracție). În afara lui nu blochează
# (rămâne raționamentul evaluatorului), dar ridică o ALERTĂ — exact riscul din articolul-cheie
# „rata de capitalizare poate deforma valoarea de piață" (ex. 0,8 în loc de 0,08 → x10 deformare).
RATA_CAP_MIN = Decimal("0.02")
RATA_CAP_MAX = Decimal("0.15")


class DateVenit(BaseModel):
    """Intrările pentru capitalizarea directă (sume anuale; procente ca fracție [0,1])."""

    venit_brut_potential: Decimal = Field(ge=0)
    grad_neocupare: Decimal = Field(default=Decimal("0"), ge=0, lt=1)
    cheltuieli_exploatare: Decimal = Field(default=Decimal("0"), ge=0)
    rata_capitalizare: Decimal
    # I-7 — documentarea sursei/metodei ratei (SEV 103 A20.34). Opțional, backward-compatible.
    sursa_rata: str = ""


class RezultatVenit(BaseModel):
    noi: Decimal
    valoare: Decimal


class DateDCF(BaseModel):
    """Intrari DCF: fluxuri anuale + rata de actualizare + valoare reziduala."""

    # cap anti-DoS (RUNDA 11): evalueaza_dcf face factor**t in loop -> O(n^2) pe cifre Decimal;
    # un DCF imobiliar real are <50 perioade. 200 = generos, blocheaza blowup-ul de calcul.
    fluxuri: list[Decimal] = Field(max_length=200)
    rata_actualizare: Decimal
    valoare_reziduala: Decimal = Decimal("0")


# --------------------------------------------------------------------------- #
# I-8 — defalcarea cheltuielilor de exploatare (OPEX / service charge).
# Sursa: articol „Taxarea serviciilor si Managementul cladirilor".
# --------------------------------------------------------------------------- #
class CheltuieliExploatare(BaseModel):
    """Defalcarea OPEX pe poziții (service charge). Toate sumele = anuale, ≥ 0.

    Poziții din articolul „service charge" (clădire de birouri multi-chiriaș). Distincția
    cheie: aceste poziții sunt OPEX RECURENT (intră în NOI). `fond_rulment` (sinking fund /
    capital pentru lucrări viitoare) este capital, NU OPEX recurent — NU se capitalizează în
    NOI (vezi `total()`), dar e expus separat pentru transparența raportului.

    Metoda `total()` însumează DOAR OPEX-ul recurent → se mapează 1:1 pe scalarul
    `DateVenit.cheltuieli_exploatare` (mod simplu), păstrând backward-compatibilitatea.
    """

    taxe: Decimal = Field(default=_ZERO, ge=0)              # impozite/taxe pe proprietate
    asigurare: Decimal = Field(default=_ZERO, ge=0)
    administrare: Decimal = Field(default=_ZERO, ge=0)      # personal administrativ
    intretinere: Decimal = Field(default=_ZERO, ge=0)       # întreținere generală / curățenie
    utilitati: Decimal = Field(default=_ZERO, ge=0)         # electricitate, încălzire, apă, AC
    reparatii: Decimal = Field(default=_ZERO, ge=0)
    securitate: Decimal = Field(default=_ZERO, ge=0)        # securitate / supraveghere
    management: Decimal = Field(default=_ZERO, ge=0)        # taxă de management
    alte: Decimal = Field(default=_ZERO, ge=0)              # audit, lift, alte poziții
    # Capital, NU OPEX recurent — NU intră în NOI (articol: fond de rulment ≠ cheltuială de exploatare).
    fond_rulment: Decimal = Field(default=_ZERO, ge=0)

    def total(self) -> Decimal:
        """OPEX recurent (intră în NOI). Exclude `fond_rulment` (capital, nu cheltuială recurentă)."""
        return (
            self.taxe + self.asigurare + self.administrare + self.intretinere
            + self.utilitati + self.reparatii + self.securitate + self.management + self.alte
        )


# --------------------------------------------------------------------------- #
# I-7 — derivarea ratei de capitalizare din piață + build-up + validare de plauzibilitate.
# Sursa: articol „Rata de capitalizare poate deforma valoarea de piata".
# --------------------------------------------------------------------------- #
def rata_din_vanzare_inchiriere(pret: Decimal, chirie_neta: Decimal) -> Decimal:
    """Rata de capitalizare = chirie netă ÷ preț (relația castig/valoare).

    Acoperă cele 4 metode de derivare din articol — toate au aceeași formulă cap = venit/preț,
    diferă doar SURSA termenilor (vânzare-închiriere; chirii actuale vs. prețuri de vânzare;
    prețuri actuale vs. chirii estimate; chirii actuale vs. prețuri estimate). Exemplul din articol:
    preț 1.000.000, chirie netă 80.000 → 0,08 (8%).
    """
    if pret <= 0:
        raise ValueError("Prețul comparabilei trebuie să fie > 0 pentru derivarea ratei.")
    if chirie_neta < 0:
        raise ValueError("Chiria netă nu poate fi negativă.")
    return Decimal(chirie_neta) / Decimal(pret)


def rata_din_comparabile(perechi: list[tuple[Decimal, Decimal]]) -> Decimal:
    """Rata de capitalizare extrasă din mai multe perechi (preț, chirie netă) — media ratelor.

    Fiecare pereche produce o rată `chirie_netă/preț`; rezultatul = media aritmetică. Este
    „grila mică preț ↔ chirie netă" recomandată în articol (cap-rate extraction), care produce o
    rată susținută de piață, nu un input liber.
    """
    if not perechi:
        raise ValueError("Sunt necesare perechi (preț, chirie netă) pentru extracția ratei.")
    rate = [rata_din_vanzare_inchiriere(p, c) for p, c in perechi]
    return sum(rate, _ZERO) / Decimal(len(rate))


def rata_build_up(rata_fara_risc: Decimal, prima_risc: Decimal,
                  prima_nelichiditate: Decimal = _ZERO,
                  recuperare_capital: Decimal = _ZERO) -> Decimal:
    """Rata de capitalizare prin metoda deductivă / build-up (când nu există comparabile).

    Articol: se pleacă de la rata generală a profitului investițiilor (rată fără risc) → caz
    specific prin adăugarea primelor pentru riscul suplimentar față de investiții alternative.
    rata = rată_fără_risc + primă_risc + primă_nelichiditate + recuperare_capital.
    """
    componente = [rata_fara_risc, prima_risc, prima_nelichiditate, recuperare_capital]
    for c in componente:
        if c < 0:
            raise ValueError("Componentele build-up nu pot fi negative.")
    rata = sum((Decimal(c) for c in componente), _ZERO)
    if rata <= 0:
        raise ValueError("Rata build-up rezultată trebuie să fie > 0.")
    return rata


def valideaza_rata_capitalizare(
    rata: Decimal, minim: Decimal = RATA_CAP_MIN, maxim: Decimal = RATA_CAP_MAX,
) -> str | None:
    """Verifică plauzibilitatea ratei. Întoarce un mesaj de ALERTĂ dacă e în afara intervalului,
    altfel `None`. NU blochează (rămâne raționamentul evaluatorului) — doar semnalează riscul de
    deformare a valorii (articolul-cheie). Apel-tip: H... heuristic, analog M5.
    """
    if rata <= 0:
        return "Rata de capitalizare trebuie să fie > 0."
    if rata < minim:
        return (f"Rata de capitalizare {rata} este sub pragul de plauzibilitate {minim} "
                f"(verificați sursa; o rată prea mică supraevaluează proprietatea).")
    if rata > maxim:
        return (f"Rata de capitalizare {rata} este peste pragul de plauzibilitate {maxim} "
                f"(verificați sursa; posibil input EUR în loc de fracție, ex. 8 în loc de 0,08).")
    return None


def evalueaza_venit(d: DateVenit) -> RezultatVenit:
    """Valoare = (VBP − pierderi neocupare − cheltuieli) ÷ rată de capitalizare."""
    if d.rata_capitalizare <= 0:
        raise ValueError("Rata de capitalizare trebuie să fie > 0.")
    pierdere = d.venit_brut_potential * d.grad_neocupare
    venit_efectiv = d.venit_brut_potential - pierdere
    noi = (venit_efectiv - d.cheltuieli_exploatare).quantize(_BANI, rounding=ROUND_HALF_UP)
    if noi <= 0:
        raise ValueError(
            f"Venitul net din exploatare (NOI) rezultat este <= 0 ({noi}); "
            "verificati cheltuielile / gradul de neocupare fata de venitul brut."
        )
    valoare = (noi / d.rata_capitalizare).quantize(_BANI, rounding=ROUND_HALF_UP)
    return RezultatVenit(noi=noi, valoare=valoare)


def abordare_venit(d: DateVenit) -> RezultatAbordare:
    r = evalueaza_venit(d)
    detalii: dict = {"noi": str(r.noi)}
    alerta = valideaza_rata_capitalizare(d.rata_capitalizare)
    if alerta:
        detalii["alerta_rata"] = alerta
    if d.sursa_rata:
        detalii["sursa_rata"] = d.sursa_rata
    return RezultatAbordare(abordare="venit", valoare=r.valoare, detalii=detalii)


# --------------------------------------------------------------------------- #
# I-19 — valoarea terminală DCF (Gordon / exit-cap).
# Sursa: articol cap-rate (relația castig/valoare la baza ambelor).
# --------------------------------------------------------------------------- #
def valoare_terminala_gordon(noi_ultima_perioada: Decimal, rata_actualizare: Decimal,
                             crestere: Decimal) -> Decimal:
    """Valoarea terminală prin modelul Gordon (creștere perpetuă):
    VT = NOI_n × (1 + g) ÷ (r − g). Necesită r > g (altfel divergent / negativ).
    """
    if rata_actualizare <= crestere:
        raise ValueError(
            f"Modelul Gordon necesită rata de actualizare ({rata_actualizare}) > "
            f"rata de creștere ({crestere}); altfel valoarea terminală e divergentă/negativă."
        )
    if noi_ultima_perioada <= 0:
        raise ValueError("NOI-ul ultimei perioade trebuie să fie > 0 pentru valoarea terminală.")
    vt = Decimal(noi_ultima_perioada) * (_UNU + Decimal(crestere)) / (
        Decimal(rata_actualizare) - Decimal(crestere))
    return vt.quantize(_BANI, rounding=ROUND_HALF_UP)


def valoare_terminala_exit_cap(noi_an_urmator: Decimal, rata_terminala: Decimal) -> Decimal:
    """Valoarea terminală prin rata de capitalizare terminală (exit-cap):
    VT = NOI_{n+1} ÷ rată_terminală. NOI-ul de intrare = cel din primul an post-orizont.
    """
    if rata_terminala <= 0:
        raise ValueError("Rata terminală (exit-cap) trebuie să fie > 0.")
    if noi_an_urmator <= 0:
        raise ValueError("NOI-ul anului următor trebuie să fie > 0 pentru exit-cap.")
    vt = Decimal(noi_an_urmator) / Decimal(rata_terminala)
    return vt.quantize(_BANI, rounding=ROUND_HALF_UP)


def evalueaza_dcf(fluxuri: list[Decimal], rata_actualizare: Decimal,
                  valoare_reziduala: Decimal = Decimal("0")) -> Decimal:
    """Valoare prin actualizarea fluxurilor de numerar (DCF).

    value = Σ flux_t/(1+r)^t (t=1..n) + valoare_reziduala/(1+r)^n.

    `valoare_reziduala` poate fi:
      - sumă manuală (comportamentul istoric, fallback), SAU
      - rezultatul `valoare_terminala_gordon(...)` / `valoare_terminala_exit_cap(...)` (I-19).
    În toate cazurile e actualizată la prezent cu factorul perioadei finale.
    """
    if rata_actualizare <= 0:
        raise ValueError("Rata de actualizare trebuie să fie > 0.")
    if not fluxuri:
        raise ValueError("Sunt necesare fluxuri de numerar pentru DCF.")
    factor = Decimal("1") + rata_actualizare
    total = Decimal("0")
    for t, flux in enumerate(fluxuri, start=1):
        total += Decimal(flux) / (factor ** t)
    n = len(fluxuri)
    total += Decimal(valoare_reziduala) / (factor ** n)
    return total.quantize(_BANI, rounding=ROUND_HALF_UP)
