"""Valoarea prudentă (valoarea de garanție) — CRR III / Reg. UE 575 art. 229 + 208 — gap B2-RV1/RV2.

Materializează o **bază de valoare DISTINCTĂ** de valoarea de piață, specifică **garantării creditului**,
introdusă de revizuirea CRR (Regulamentul UE 575, aplicabil de la 1 ian. 2025) — sursă internă:
`docs/analiza-anevar/batch2/00-SINTEZA-batch2.md` §C și `docs/analiza-anevar/batch2/revista-valoarea-arhiva.md`
§1.3 / GAP-RV1 / GAP-RV2 (revista «Valoarea» nr. 40, Q3 2023).

Poziția de fond (esențială pentru cum tratează app-ul această valoare):
  1. **Art. 229 — criterii prudente de evaluare la acordare:**
     (a) valoarea **NU ține seama de așteptările de creștere a prețului** (se elimină componenta speculativă);
     (b) valoarea **se ajustează** pentru potențialul ca prețul de piață curent să fie *cu mult peste valoarea
         sustenabilă* pe durata împrumutului (haircut de sustenabilitate);
     (c) valoarea **NU poate depăși valoarea de piață** dacă aceasta poate fi determinată.
  2. **Art. 208 — reevaluare periodică:** scop = diminuarea influenței ciclurilor de piață + reducerea
     elementelor speculative; mecanismul numeric (interpretare): valoarea de garanție =
     `min[ media valorilor de piață din anii precedenți ; valoarea de piață din anul curent ]` (plafonare).
  3. **Valoarea prudentă ≤ valoarea de piață** și **COEXISTĂ** cu ea — NU o înlocuiește. Valoarea de piață
     (SEV 102) rămâne baza de valoare a raportului; valoarea prudentă este o estimare ADIȚIONALĂ, pentru
     garantare, prezentată alături de valoarea de piață și raportată la ea.

REGULA DE PRUDENȚĂ a acestui modul (per `docs/.../revista-valoarea-arhiva.md` GAP-RV1 + MEMORY roadmap):
  interpretarea CRR este **neoficializată** în România. Modulul oferă STRUCTURA + un calcul TRANSPARENT și
  DOCUMENTAT (parametri expliciți, niciun automatism ascuns), dar valoarea prudentă **rămâne o opțiune
  asumată de evaluator**, nu un automatism impus. Modul PUR (logică + date), fără wiring în generator/UI.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from evaluare.money import pct, round_lei, to_money

# Referința normativă (pentru citare în raport / trasabilitate).
REFERINTA_CRR: str = "Regulamentul (UE) nr. 575/2013 (CRR), revizuit — art. 229 și art. 208"


class ParametriValoarePrudenta(BaseModel):
    """Parametrii prudențiali, expliciți și asumați de evaluator, pentru estimarea valorii prudente.

    Toți parametrii sunt **opționali** (cu valori implicite neutre = 0) și **documentați** — niciun
    automatism ascuns. Procentele se exprimă ca numere (ex. `5` = 5%), nu ca fracții.

    - `discount_crestere_pct`: eliminarea componentei de **creștere/speculative** din prețul curent
      (art. 229 lit. a — valoarea nu ține seama de așteptările de creștere a prețului).
    - `haircut_sustenabilitate_pct`: ajustarea de **sustenabilitate pe durata împrumutului** (art. 229 lit. b
      — potențialul ca prețul curent să fie cu mult peste valoarea sustenabilă pe termen lung).
    - `excludere_elemente_speculative`: sumă fixă (lei) exclusă explicit ca element speculativ izolabil
      (ex. supraevaluare punctuală identificată), peste discounturile procentuale.
    """

    discount_crestere_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    haircut_sustenabilitate_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    excludere_elemente_speculative: Decimal = Field(default=Decimal("0"), ge=0)


class RezultatValoarePrudenta(BaseModel):
    """Rezultatul estimării valorii prudente, raportat la valoarea de piață (bază distinctă).

    `valoare_prudenta` este GARANTAT ≤ `valoare_piata` (art. 229 lit. c — nu poate depăși valoarea de
    piață). Câmpurile de detaliu fac calculul **transparent** (auditabil) pentru raport.
    """

    valoare_piata: Decimal               # baza de pornire (valoarea de piață, SEV 102) — NU se modifică
    valoare_prudenta: Decimal            # estimarea prudentă (≤ valoare_piata) — bază de valoare distinctă
    reducere_totala: Decimal             # valoare_piata - valoare_prudenta (lei)
    reducere_pct: Decimal                # reducerea totală ca procent din valoarea de piață
    discount_crestere_lei: Decimal       # cuantumul eliminării componentei de creștere (art. 229 a)
    haircut_sustenabilitate_lei: Decimal  # cuantumul ajustării de sustenabilitate (art. 229 b)
    excludere_speculativa_lei: Decimal   # suma fixă exclusă ca element speculativ
    parametri: ParametriValoarePrudenta  # parametrii folosiți (trasabilitate)


def estimeaza_valoare_prudenta(
    valoare_piata: Decimal | float | int | str,
    parametri: ParametriValoarePrudenta | None = None,
) -> RezultatValoarePrudenta:
    """Estimează valoarea prudentă (valoarea de garanție) din valoarea de piață + parametri prudențiali.

    Mecanica (art. 229), aplicată secvențial pe valoarea de piață:
      1. **elimină componenta de creștere/speculative** (`discount_crestere_pct`) — lit. a;
      2. **aplică haircut-ul de sustenabilitate** (`haircut_sustenabilitate_pct`) pe valoarea rămasă — lit. b;
      3. **scade elementele speculative izolabile** (`excludere_elemente_speculative`, sumă fixă).
    Apoi **plafonează la valoarea de piață** (lit. c — nu poate depăși valoarea de piață) și la 0 (nu poate
    fi negativă). Cu parametri impliciți (toți 0) -> valoarea prudentă = valoarea de piață (caz neutru:
    evaluatorul nu a aplicat încă nicio ajustare prudențială).

    NU este un automatism normativ — parametrii sunt asumați de evaluator (interpretarea CRR neoficializată
    în RO). Rezultatul e o estimare ADIȚIONALĂ, prezentată alături de valoarea de piață, NU în locul ei.
    """
    parametri = parametri or ParametriValoarePrudenta()
    vp = to_money(valoare_piata)
    if vp < 0:
        raise ValueError("Valoarea de piață nu poate fi negativă.")

    # 1. eliminarea componentei de creștere/speculative (art. 229 a)
    discount_crestere = vp * pct(parametri.discount_crestere_pct)
    dupa_crestere = vp - discount_crestere

    # 2. haircut de sustenabilitate pe valoarea rămasă (art. 229 b)
    haircut = dupa_crestere * pct(parametri.haircut_sustenabilitate_pct)
    dupa_haircut = dupa_crestere - haircut

    # 3. excluderea elementelor speculative izolabile (sumă fixă)
    excludere = to_money(parametri.excludere_elemente_speculative)
    bruta = dupa_haircut - excludere

    # plafonare: 0 ≤ valoare_prudenta ≤ valoare_piata (art. 229 c)
    valoare_prudenta = min(max(bruta, Decimal("0")), vp)

    vp_r = round_lei(vp)
    valoare_prudenta_r = round_lei(valoare_prudenta)
    reducere = vp_r - valoare_prudenta_r
    reducere_pct = (
        (reducere / vp_r * Decimal("100")) if vp_r > 0 else Decimal("0")
    )

    return RezultatValoarePrudenta(
        valoare_piata=vp_r,
        valoare_prudenta=valoare_prudenta_r,
        reducere_totala=reducere,
        reducere_pct=reducere_pct,
        discount_crestere_lei=round_lei(discount_crestere),
        haircut_sustenabilitate_lei=round_lei(haircut),
        excludere_speculativa_lei=round_lei(excludere),
        parametri=parametri,
    )


def valoare_garantie_reevaluare(
    valoare_curenta: Decimal | float | int | str,
    valori_piata_anterioare: list[Decimal | float | int | str] | None = None,
) -> Decimal:
    """Valoarea de garanție la **reevaluare periodică** — formula art. 208 (plafonare prin medie istorică).

    `valoare_garantie = min[ media valorilor de piață din anii precedenți ; valoarea de piață curentă ]`.
    Scopul (art. 208): diminuarea influenței ciclurilor de piață + reducerea elementelor speculative —
    valoarea de garanție nu poate depăși media istorică (plafonare în piețe în creștere), dar urmează
    valoarea curentă când aceasta scade sub medie.

    Dacă nu există valori anterioare (prima evaluare) -> se întoarce valoarea curentă (nimic de plafonat).
    Interpretare **neoficializată** — de folosit ca opțiune documentată, nu automatism impus.
    """
    curenta = round_lei(to_money(valoare_curenta))
    if curenta < 0:
        raise ValueError("Valoarea curentă nu poate fi negativă.")
    anterioare = [to_money(v) for v in (valori_piata_anterioare or [])]
    if not anterioare:
        return curenta
    medie = round_lei(sum(anterioare, Decimal("0")) / Decimal(len(anterioare)))
    return min(medie, curenta)


# Textul explicativ standard pentru raport (ce este valoarea prudentă, de ce diferă de valoarea de piață,
# și clarificarea că NU înlocuiește valoarea de piață SEV). Folosit ca disclaimer/notă în secțiunea de
# garantare. Fidel poziției CRR art. 229 + 208 și GAP-RV1.
TEXT_EXPLICATIV_VALOARE_PRUDENTA: str = (
    "Valoarea prudentă (valoarea de garanție) este o bază de valoare DISTINCTĂ de valoarea de piață, "
    "estimată pentru scopul garantării creditului în conformitate cu criteriile prudente prevăzute de "
    f"{REFERINTA_CRR}. Spre deosebire de valoarea de piață, valoarea prudentă: (a) nu ține seama de "
    "așteptările de creștere a prețului; (b) se ajustează pentru potențialul ca prețul de piață curent "
    "să fie peste valoarea sustenabilă pe durata împrumutului; (c) nu poate depăși valoarea de piață. În "
    "consecință, valoarea prudentă este, de regulă, mai mică sau cel mult egală cu valoarea de piață. "
    "Această valoare NU înlocuiește valoarea de piață stabilită conform Standardelor de Evaluare a "
    "Bunurilor (SEV 102), ci se prezintă ALĂTURI de aceasta, exclusiv pentru evaluarea prudentă a "
    "garanției. Parametrii de ajustare au fost asumați de evaluatorul autorizat; interpretarea cerințelor "
    "CRR în acest scop nu este, la data raportului, oficializată printr-o metodologie unitară la nivel "
    "național, motiv pentru care estimarea are caracter orientativ și suportă revizuire."
)


def genereaza_nota_valoare_prudenta(rezultat: RezultatValoarePrudenta) -> str:
    """Textul de raport pentru valoarea prudentă: nota explicativă + cifrele estimării (transparent).

    Conține: (1) `TEXT_EXPLICATIV_VALOARE_PRUDENTA` (ce este + de ce diferă + că NU înlocuiește valoarea
    de piață SEV); (2) valoarea de piață de pornire și valoarea prudentă rezultată, cu reducerea aplicată.
    Returnează text simplu (paragrafe separate prin linie goală). Fără scoruri/ierarhii — doar cifre
    auditabile și justificare normativă.
    """
    cifre = (
        f"Valoare de piață (SEV 102): {rezultat.valoare_piata} lei. "
        f"Valoare prudentă estimată (de garanție): {rezultat.valoare_prudenta} lei "
        f"(reducere totală {rezultat.reducere_totala} lei, "
        f"{rezultat.reducere_pct.quantize(Decimal('0.1'))}% față de valoarea de piață)."
    )
    return "\n\n".join([TEXT_EXPLICATIV_VALOARE_PRUDENTA, cifre])
