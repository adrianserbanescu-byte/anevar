"""Teste property-based (Hypothesis) COMPLEMENTARE pe functiile NUMERICE ale motorului.

Fisier NOU, separat de `test_property_engine.py` (nu se suprapune cu el): acopera functii si
proprietati ne-acoperite acolo — depreciere (interpolare/clamp/CIB/VCP), derivarea ratei de
capitalizare (vanzare-inchiriere / comparabile / build-up), valoare terminala (Gordon / exit-cap),
DCF (monotonie in rata, liniaritate), teren rezidual, reconciliere (normalizare ponderi, convexitate,
extreme) si MONOTONIA grilei de piata/teren (pret comparabil mai mare -> valoare mai mare).

Proprietatile verificate (rezumat in raport):
  - fara exceptii neprinse pe input valid-dar-extrem (sau DOAR ValueError-ul documentat);
  - monotonii evidente (ceteris paribus): pret comparabil ↑ -> valoare ↑; rata ↑ -> valoare ↓;
  - invarianti (depreciere in [0,1]; VCP in [varsta_min, varsta_max]; valori >= 0 unde se cere;
    valoare ponderata in [min,max] al valorilor; ponderi normalizate => medie convexa);
  - idempotenta / determinism;
  - clamp corect sub/peste limitele tabelului de depreciere.

Daca Hypothesis NU e disponibil, se cade pe variante parametrizate clasice cu input-uri extreme
(acelasi set de proprietati, esantion finit ales adversarial).
"""
from __future__ import annotations

from decimal import Decimal, getcontext

import pytest

# Precizie generoasa: motorul lucreaza pe Decimal; nu vrem InvalidOperation pe lanturi lungi.
getcontext().prec = 60

from evaluare.engine.abordari import RezultatAbordare  # noqa: E402
from evaluare.engine.cost import (  # noqa: E402
    compute_cib,
    compute_cin,
    compute_vcp,
    interpolate_depreciation,
)
from evaluare.engine.land import (  # noqa: E402
    DateTerenRezidual,
    evaluate_land,
    teren_rezidual,
)
from evaluare.engine.market import evaluate_market, pret_total_corectat  # noqa: E402
from evaluare.engine.metodologie import MetodologieConfig  # noqa: E402
from evaluare.engine.reconciliation import reconcile_profil  # noqa: E402
from evaluare.engine.venit import (  # noqa: E402
    DateVenit,
    evalueaza_dcf,
    evalueaza_venit,
    rata_build_up,
    rata_din_comparabile,
    rata_din_vanzare_inchiriere,
    valideaza_rata_actualizare,
    valideaza_rata_capitalizare,
    valoare_terminala_exit_cap,
    valoare_terminala_gordon,
)
from evaluare.models.comparable import Comparable, LandComparable  # noqa: E402
from evaluare.models.property import CostElement, DepreciationPoint  # noqa: E402

_N1 = MetodologieConfig(nr_comparabile_medie=1)

# --------------------------------------------------------------------------- #
# Detectie Hypothesis: daca lipseste, _given/_st devin shim-uri care produc teste
# parametrizate clasice cu input-uri extreme (acelasi set de proprietati).
# --------------------------------------------------------------------------- #
try:
    from hypothesis import example, given, settings  # noqa: E402
    from hypothesis import strategies as st  # noqa: E402

    HAS_HYPOTHESIS = True
except ImportError:  # pragma: no cover - mediul nostru ARE hypothesis 6.x; ramura e plasa de siguranta
    HAS_HYPOTHESIS = False


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de constructie
# ─────────────────────────────────────────────────────────────────────────────
def _comp(pret, supr, adjs=None):
    return Comparable(pret=Decimal(str(pret)), suprafata=Decimal(str(supr)),
                      adjustments=adjs or [])


def _teren(pret_mp, supr, adjs=None):
    return LandComparable(pret_mp=Decimal(str(pret_mp)), suprafata=Decimal(str(supr)),
                          adjustments=adjs or [])


def _D(x):
    return Decimal(str(x))


# ═════════════════════════════════════════════════════════════════════════════
# RAMURA HYPOTHESIS
# ═════════════════════════════════════════════════════════════════════════════
if HAS_HYPOTHESIS:

    _preturi = st.decimals(min_value=Decimal("1"), max_value=Decimal("50000000"),
                           places=2, allow_nan=False, allow_infinity=False)
    _preturi_mp = st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000000"),
                              places=2, allow_nan=False, allow_infinity=False)
    _suprafete = st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100000"),
                             places=2, allow_nan=False, allow_infinity=False)
    _rate = st.decimals(min_value=Decimal("0.0001"), max_value=Decimal("0.99"),
                        places=4, allow_nan=False, allow_infinity=False)
    _fractii = st.decimals(min_value=Decimal("0"), max_value=Decimal("0.95"),
                           places=4, allow_nan=False, allow_infinity=False)

    # ── 1. Depreciere: interpolare in [0,1], clamp, monotonie ───────────────
    @st.composite
    def _tabel_depreciere(draw):
        """Tabel de depreciere VALID: varste distincte crescatoare, depreciere in [0,1]."""
        n = draw(st.integers(min_value=1, max_value=6))
        varste = draw(st.lists(st.integers(min_value=0, max_value=150),
                               min_size=n, max_size=n, unique=True))
        varste.sort()
        pts = []
        for v in varste:
            d = draw(st.decimals(min_value=Decimal("0"), max_value=Decimal("1"),
                                 places=4, allow_nan=False, allow_infinity=False))
            pts.append(DepreciationPoint(varsta=v, depreciere=d))
        return pts

    @given(_tabel_depreciere(),
           st.decimals(min_value=Decimal("-50"), max_value=Decimal("300"),
                       places=2, allow_nan=False, allow_infinity=False))
    @settings(max_examples=300, deadline=None)
    def test_prop_depreciere_in_zero_unu(pts, vcp):
        """interpolate_depreciation NU arunca pe vcp arbitrar; rezultatul ramane in [0,1] PRACTIC.

        Toleranta 1e-9 (istorica): inainte de fix formula de interpolare putea iesi cu ~1e-31 sub 0 /
        peste 1 din coada de precizie Decimal. Acum invariantul tine STRICT — vezi
        test_prop_depreciere_in_zero_unu_STRICT; toleranta de aici e doar o plasa de siguranta."""
        d = interpolate_depreciation(vcp, pts)
        assert Decimal("-1e-9") <= d <= Decimal("1") + Decimal("1e-9")

    @example(  # regresie DETERMINISTA (gasit de Hypothesis, redus): panta 0.0003/22 e ne-terminanta,
               # iar la nodul vcp=22 formula NEclampata dadea -1E-63 < 0. Dupa fix (clamp [0,1] +
               # scurtcircuit pe nod) rezultatul e EXACT 0. Forteaza cazul la FIECARE rulare.
        pts=[DepreciationPoint(varsta=0, depreciere=Decimal("0.0003")),
             DepreciationPoint(varsta=22, depreciere=Decimal("0")),
             DepreciationPoint(varsta=23, depreciere=Decimal("0"))],
        vcp=Decimal("22"))
    @given(_tabel_depreciere(),
           st.decimals(min_value=Decimal("-50"), max_value=Decimal("300"),
                       places=2, allow_nan=False, allow_infinity=False))
    @settings(max_examples=400, deadline=None)
    def test_prop_depreciere_in_zero_unu_STRICT(pts, vcp):
        """STRICT: deprecierea interpolata trebuie sa fie EXACT in [0,1], fara toleranta.

        Anterior xfail (BUG: interpolate_depreciation scotea ~1e-31/1e-63 in afara [0,1] din coada de
        precizie Decimal a formulei d1+(d2-d1)/(v2-v1)*(vcp-v1)). REPARAT: clamp [0,1] + scurtcircuit pe
        nod in interpolate_depreciation -> invariantul Dfn in [0,1] tine STRICT (exemplul determinist trece)."""
        d = interpolate_depreciation(vcp, pts)
        assert Decimal("0") <= d <= Decimal("1")

    @given(_tabel_depreciere())
    @settings(max_examples=200, deadline=None)
    def test_prop_depreciere_clamp_la_capete(pts):
        """Sub/peste limitele tabelului -> primul/ultimul punct (clamp exact)."""
        ordonate = sorted(pts, key=lambda p: p.varsta)
        vmin, vmax = ordonate[0], ordonate[-1]
        # mult sub minim -> deprecierea primului punct
        assert interpolate_depreciation(_D(vmin.varsta) - _D(10), pts) == vmin.depreciere
        # mult peste maxim -> deprecierea ultimului punct
        assert interpolate_depreciation(_D(vmax.varsta) + _D(10), pts) == vmax.depreciere

    @given(_tabel_depreciere())
    @settings(max_examples=150, deadline=None)
    def test_prop_depreciere_pe_noduri(pts):
        """In nodul de varsta, deprecierea interpolata = deprecierea tabulata (idempotenta pe noduri).

        Toleranta 1e-9: cand un nod e capatul-DREAPTA al unui interval, motorul evalueaza
        d1 + (d2-d1)/(v2-v1)*(v2-v1) in loc de a scurtcircuita la d2; (d2-d1)/(v2-v1) e o zecimala
        Decimal ne-terminanta, deci re-inmultirea cu (v2-v1) lasa un reziduu ~1e-60 (NU bug — valoarea
        e corecta pe ~60 cifre, iar productia rotunjeste downstream). Verificam egalitatea pe ~9 zecimale.
        """
        for p in pts:
            got = interpolate_depreciation(_D(p.varsta), pts)
            assert abs(got - p.depreciere) <= Decimal("1e-9")
            # invariant [0,1] doar PRACTIC (toleranta) — vezi xfail-ul strict de mai sus pentru bug.
            assert Decimal("-1e-9") <= got <= Decimal("1") + Decimal("1e-9")

    # ── 2. Depreciere MONOTONA (tabel crescator) -> Dfn(vcp) ne-descrescatoare ─
    @st.composite
    def _tabel_depreciere_monoton(draw):
        """Tabel cu depreciere NE-DESCRESCATOARE in varsta (cazul real: mai batran -> mai depreciat)."""
        n = draw(st.integers(min_value=2, max_value=6))
        varste = sorted(draw(st.lists(st.integers(min_value=0, max_value=150),
                                      min_size=n, max_size=n, unique=True)))
        pts, d_prev = [], Decimal("0")
        for v in varste:
            delta = draw(st.decimals(min_value=Decimal("0"), max_value=Decimal("0.3"),
                                     places=4, allow_nan=False, allow_infinity=False))
            d_prev = min(Decimal("1"), d_prev + delta)
            pts.append(DepreciationPoint(varsta=v, depreciere=d_prev))
        return pts

    @given(_tabel_depreciere_monoton(),
           st.decimals(min_value=Decimal("0"), max_value=Decimal("150"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0"), max_value=Decimal("150"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_depreciere_monotona_in_varsta(pts, v1, v2):
        """Tabel ne-descrescator => Dfn(varsta_mare) >= Dfn(varsta_mica)."""
        lo, hi = sorted([v1, v2])
        d_lo = interpolate_depreciation(lo, pts)
        d_hi = interpolate_depreciation(hi, pts)
        assert d_hi >= d_lo

    # ── 3. CIB / VCP: VCP in [varsta_min, varsta_max], CIB >= 0 ─────────────
    @st.composite
    def _elemente_cost(draw):
        n = draw(st.integers(min_value=1, max_value=5))
        els = []
        for _ in range(n):
            cant = draw(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10000"),
                                    places=2, allow_nan=False, allow_infinity=False))
            cu = draw(st.decimals(min_value=Decimal("0.01"), max_value=Decimal("100000"),
                                  places=2, allow_nan=False, allow_infinity=False))
            an_pif = draw(st.integers(min_value=1900, max_value=2025))
            els.append(CostElement(element="x", cod="C", um="mp", cantitate=cant,
                                   cost_unitar=cu, an_pif=an_pif))
        return els

    @given(_elemente_cost(), st.integers(min_value=2025, max_value=2100))
    @settings(max_examples=200, deadline=None)
    def test_prop_vcp_in_intervalul_varstelor(els, an_ref):
        """VCP (media ponderata a varstelor) e MEREU in [min varsta, max varsta] (costuri pozitive)."""
        vcp = compute_vcp(els, an_ref)
        varste = [_D(e.varsta(an_ref)) for e in els]
        assert min(varste) <= vcp <= max(varste)

    @given(_elemente_cost())
    @settings(max_examples=150, deadline=None)
    def test_prop_cib_pozitiv_si_aditiv(els):
        """CIB >= 0 si = suma costurilor de nou (aditivitate)."""
        cib = compute_cib(els)
        assert cib >= 0
        assert cib == sum((e.cost_nou() for e in els), Decimal("0"))

    @given(st.decimals(min_value=Decimal("1"), max_value=Decimal("10000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           _fractii, _fractii, _fractii, _fractii, _fractii, _fractii)
    @settings(max_examples=200, deadline=None)
    def test_prop_cin_monoton_descrescator_in_depreciere(cib, d1, c1, e1, dd, cc, ee):
        """CIN scade (sau ramane) cand ORICE depreciere creste (ceteris paribus); CIN in (0, CIB]."""
        cin1 = compute_cin(cib, d1, c1, e1)
        assert 0 < cin1 <= cib
        # crestem fiecare depreciere -> CIN nu poate creste
        cin_d = compute_cin(cib, min(d1 + dd, Decimal("0.99")), c1, e1)
        cin_c = compute_cin(cib, d1, min(c1 + cc, Decimal("0.99")), e1)
        cin_e = compute_cin(cib, d1, c1, min(e1 + ee, Decimal("0.99")))
        assert cin_d <= cin1
        assert cin_c <= cin1
        assert cin_e <= cin1

    # ── 4. Rata de capitalizare: derivare, build-up, plauzibilitate ─────────
    @given(_preturi, st.decimals(min_value=Decimal("0"), max_value=Decimal("5000000"),
                                 places=2, allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_rata_vanzare_inchiriere(pret, chirie):
        """cap = chirie/pret >= 0; chirie 0 -> rata 0; monoton crescator in chirie."""
        r = rata_din_vanzare_inchiriere(pret, chirie)
        assert r >= 0
        assert (r == 0) == (chirie == 0)
        r2 = rata_din_vanzare_inchiriere(pret, chirie + _D(1))
        assert r2 > r

    @given(st.lists(st.tuples(_preturi, st.decimals(min_value=Decimal("0"),
                                                    max_value=Decimal("5000000"), places=2,
                                                    allow_nan=False, allow_infinity=False)),
                    min_size=1, max_size=8))
    @settings(max_examples=150, deadline=None)
    def test_prop_rata_din_comparabile_in_interval(perechi):
        """Media ratelor extrase e in [min rata, max rata] al perechilor (medie aritmetica).

        Toleranta relativa 1e-50: cand ratele sunt zecimale Decimal ne-terminante (ex. 0,01/1,01),
        media (Σ/n) rotunjeste pe ultima cifra a preciziei (60) -> poate iesi cu ~1e-60 sub min sau
        peste max. Artefact de cuantizare Decimal pe egalitate exacta, NU bug de motor."""
        r = rata_din_comparabile(perechi)
        rate = [rata_din_vanzare_inchiriere(p, c) for p, c in perechi]
        tol = (max(rate) + Decimal("1e-30")) * Decimal("1e-50") + Decimal("1e-60")
        assert min(rate) - tol <= r <= max(rate) + tol
        assert r >= 0

    @given(_rate, _fractii, _fractii, _fractii)
    @settings(max_examples=200, deadline=None)
    def test_prop_build_up_suma_componente(rf, pr, pn, rc):
        """rata build-up = suma componentelor (>= fiecare componenta non-negativa); > 0."""
        r = rata_build_up(rf, pr, pn, rc)
        assert r == rf + pr + pn + rc
        assert r >= rf
        assert r > 0

    @given(st.decimals(min_value=Decimal("-5"), max_value=Decimal("5"), places=4,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_validari_rata_nu_arunca(rata):
        """Validatorii de plauzibilitate NU arunca pe orice Decimal finit; intorc str|None coerent."""
        for fn in (valideaza_rata_capitalizare, valideaza_rata_actualizare):
            out = fn(rata)
            assert out is None or isinstance(out, str)
            # rata in banda implicita -> None; in afara -> mesaj
        # in banda capitalizare [0.02,0.15] -> None
        if Decimal("0.02") <= rata <= Decimal("0.15"):
            assert valideaza_rata_capitalizare(rata) is None

    # ── 5. Venit: NOI/valoare, monotonie in rata SI in VBP ──────────────────
    @given(st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           _rate, _rate)
    @settings(max_examples=200, deadline=None)
    def test_prop_venit_monoton_in_rata(vbp, ra, rb):
        """Capitalizare directa: rata mai mare -> valoare mai mica (sau egala pe quantize); valoare > 0."""
        lo, hi = sorted([ra, rb])
        v_lo = evalueaza_venit(DateVenit(venit_brut_potential=vbp, rata_capitalizare=lo)).valoare
        v_hi = evalueaza_venit(DateVenit(venit_brut_potential=vbp, rata_capitalizare=hi)).valoare
        assert v_lo >= v_hi > 0

    @given(st.decimals(min_value=Decimal("1000"), max_value=Decimal("10000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("1"), max_value=Decimal("1000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           _rate)
    @settings(max_examples=200, deadline=None)
    def test_prop_venit_monoton_crescator_in_vbp(vbp, delta, rata):
        """VBP mai mare (ceteris paribus) -> NOI mai mare -> valoare mai mare (sau egala pe quantize)."""
        d1 = DateVenit(venit_brut_potential=vbp, rata_capitalizare=rata)
        d2 = DateVenit(venit_brut_potential=vbp + delta, rata_capitalizare=rata)
        v1 = evalueaza_venit(d1)
        v2 = evalueaza_venit(d2)
        assert v2.noi >= v1.noi
        assert v2.valoare >= v1.valoare

    # ── 6. Valoare terminala Gordon / exit-cap ──────────────────────────────
    @given(st.decimals(min_value=Decimal("1"), max_value=Decimal("10000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0.05"), max_value=Decimal("0.30"), places=4,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0"), max_value=Decimal("0.04"), places=4,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_gordon_pozitiv_si_monoton(noi, rata, g):
        """VT Gordon > 0 cand r > g; crescator in NOI."""
        vt = valoare_terminala_gordon(noi, rata, g)
        assert vt > 0
        vt2 = valoare_terminala_gordon(noi + _D(100), rata, g)
        assert vt2 >= vt

    @given(st.decimals(min_value=Decimal("1"), max_value=Decimal("10000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           _rate)
    @settings(max_examples=200, deadline=None)
    def test_prop_exit_cap_pozitiv_monoton_descrescator_in_rata(noi, rata):
        """VT exit-cap = NOI/rata > 0; rata mai mare -> VT mai mic (sau egal pe quantize)."""
        vt = valoare_terminala_exit_cap(noi, rata)
        assert vt > 0
        rata_mai_mare = min(rata + _D("0.05"), Decimal("0.99"))
        vt2 = valoare_terminala_exit_cap(noi, rata_mai_mare)
        assert vt2 <= vt

    # ── 7. DCF: pozitiv, monoton descrescator in rata, liniar in scalare ────
    _fluxuri = st.lists(st.decimals(min_value=Decimal("1"), max_value=Decimal("1000000"),
                                    places=2, allow_nan=False, allow_infinity=False),
                        min_size=1, max_size=30)

    @given(_fluxuri, _rate, _rate)
    @settings(max_examples=200, deadline=None)
    def test_prop_dcf_monoton_descrescator_in_rata(fluxuri, ra, rb):
        """DCF cu fluxuri pozitive: rata de actualizare mai mare -> valoare mai mica (sau egala pe quantize)."""
        lo, hi = sorted([ra, rb])
        v_lo = evalueaza_dcf(fluxuri, lo)
        v_hi = evalueaza_dcf(fluxuri, hi)
        assert v_lo > 0
        assert v_lo >= v_hi

    @given(_fluxuri, _rate, st.decimals(min_value=Decimal("0.01"), max_value=Decimal("1000"),
                                        places=2, allow_nan=False, allow_infinity=False))
    @settings(max_examples=150, deadline=None)
    def test_prop_dcf_liniar_in_scalare(fluxuri, rata, k):
        """DCF e LINIAR: scalez toate fluxurile cu k -> valoarea se scaleaza ~cu k.
        Σ (k·flux_t)/(1+r)^t = k·Σ flux_t/(1+r)^t.

        Toleranta SCALATA cu k: evalueaza_dcf rotunjeste rezultatul la cent INAINTE de scalare, deci
        eroarea de rotunjire (≤ 0,5 cent in v1) se amplifica cu k cand comparam cu v1·k. Marja =
        k·0,01 + 0,01 (NU divergenta de motor — artefact de cuantizare Decimal, ca in test_property_engine)."""
        v1 = evalueaza_dcf(fluxuri, rata)
        scalate = [f * k for f in fluxuri]
        v2 = evalueaza_dcf(scalate, rata)
        asteptat = (v1 * k).quantize(Decimal("0.01"))
        toleranta = (k * Decimal("0.01")).quantize(Decimal("0.01")) + Decimal("0.01")
        assert abs(v2 - asteptat) <= toleranta

    # ── 8. Teren rezidual: GDV - costuri - profit, monotonie ────────────────
    @given(st.decimals(min_value=Decimal("100000"), max_value=Decimal("100000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0"), max_value=Decimal("0.5"), places=4,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_teren_rezidual_descreste_cu_costurile(gdv, profit_pct):
        """Mai multe costuri de dezvoltare (ceteris paribus) -> valoare reziduala mai mica (sau eroare)."""
        # costuri mici ca sa ramana valoare reziduala pozitiva
        cost_mic = gdv * Decimal("0.1")
        cost_mare = gdv * Decimal("0.2")
        d1 = DateTerenRezidual(valoare_dezvoltare=gdv, costuri_dezvoltare=cost_mic,
                               profit_procent=profit_pct)
        d2 = DateTerenRezidual(valoare_dezvoltare=gdv, costuri_dezvoltare=cost_mare,
                               profit_procent=profit_pct)
        try:
            r1 = teren_rezidual(d1)
        except ValueError:
            return  # dezvoltare nefezabila chiar si la cost mic -> nimic de comparat
        assert r1.valoare_teren > 0
        try:
            r2 = teren_rezidual(d2)
        except ValueError:
            return  # cost mare -> nefezabil = consistent cu "mai mic"
        assert r2.valoare_teren <= r1.valoare_teren

    @given(st.integers(min_value=1, max_value=1000),
           st.decimals(min_value=Decimal("1000"), max_value=Decimal("5000000"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=150, deadline=None)
    def test_prop_teren_rezidual_gdv_din_loturi(nr_loturi, pret_lot):
        """GDV din parcelare = nr_loturi * pret_lot (aditiv); valoarea fara costuri/profit = GDV."""
        d = DateTerenRezidual(nr_loturi=nr_loturi, pret_lot=pret_lot)
        assert d.valoare_bruta_dezvoltare() == Decimal(nr_loturi) * pret_lot
        r = teren_rezidual(d)  # fara costuri/profit -> valoare = GDV
        assert r.valoare_teren == (Decimal(nr_loturi) * pret_lot).quantize(Decimal("0.01"))

    # ── 9. Grila de piata: MONOTONIE (pret comparabil mai mare -> valoare mai mare) ─
    @given(st.lists(_preturi, min_size=1, max_size=6),
           st.decimals(min_value=Decimal("10"), max_value=Decimal("2000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("1.01"), max_value=Decimal("100"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_piata_monotona_in_pret(preturi, supr, factor):
        """Ridic TOATE preturile comparabilelor cu factor>1 (fara ajustari) -> valoarea de piata creste."""
        comps = [_comp(p, supr) for p in preturi]
        ridicate = [_comp(p * factor, supr) for p in preturi]
        v1 = evaluate_market(comps).valoare_piata
        v2 = evaluate_market(ridicate).valoare_piata
        assert v2 > v1

    @given(st.lists(_preturi, min_size=1, max_size=6),
           st.decimals(min_value=Decimal("10"), max_value=Decimal("2000"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=150, deadline=None)
    def test_prop_piata_valoare_in_interval_si_pozitiva(preturi, supr):
        """Valoarea de piata (media top-N) e in [min,max] al preturilor corectate si > 0 (fara ajustari)."""
        comps = [_comp(p, supr) for p in preturi]
        r = evaluate_market(comps)
        corectate = [pret_total_corectat(c) for c in comps]
        assert min(corectate) <= r.valoare_piata <= max(corectate)
        assert r.valoare_piata > 0

    # ── 10. Grila de teren: monotonie in pret/mp si in suprafata subiect ────
    @given(st.lists(_preturi_mp, min_size=1, max_size=6),
           st.decimals(min_value=Decimal("1"), max_value=Decimal("100000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("1.01"), max_value=Decimal("50"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_teren_monoton_in_pret_mp(preturi_mp, supr_subiect, factor):
        """Pret/mp comparabil mai mare (toate, factor>1) -> valoare teren mai mare (ceteris paribus)."""
        comps = [_teren(p, Decimal("500")) for p in preturi_mp]
        ridicate = [_teren(p * factor, Decimal("500")) for p in preturi_mp]
        v1 = evaluate_land(comps, supr_subiect).valoare_teren
        v2 = evaluate_land(ridicate, supr_subiect).valoare_teren
        assert v2 > v1

    # ── 11. Reconciliere: normalizare ponderi, convexitate, extreme ─────────
    def _rez(abordare, valoare):
        return RezultatAbordare(abordare=abordare, valoare=Decimal(str(valoare)))

    @given(st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0.01"), max_value=Decimal("0.99"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_reconcile_convexa_ponderi_normalizate(v_p, v_c, w):
        """Ponderi care insumeaza 1 -> valoarea finala e in [min,max] al celor doua valori (medie convexa)."""
        rez = [_rez("comparatie", v_p), _rez("cost", v_c)]
        r = reconcile_profil(rez, primara="comparatie",
                             ponderi={"comparatie": w, "cost": Decimal("1") - w})
        lo, hi = sorted([_D(v_p).quantize(Decimal("0.01")), _D(v_c).quantize(Decimal("0.01"))])
        assert lo <= r.valoare_finala <= hi

    @given(st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0.1"), max_value=Decimal("10"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("0.1"), max_value=Decimal("10"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=200, deadline=None)
    def test_prop_reconcile_normalizare_pe_pondere_arbitrara(v_p, v_c, w1, w2):
        """reconcile_profil normalizeaza ponderile (imparte la suma) -> rezultat in [min,max] indiferent
        de scara ponderilor (w1,w2 ne-normalizate)."""
        rez = [_rez("comparatie", v_p), _rez("cost", v_c)]
        r = reconcile_profil(rez, primara="comparatie",
                             ponderi={"comparatie": w1, "cost": w2})
        lo, hi = sorted([_D(v_p).quantize(Decimal("0.01")), _D(v_c).quantize(Decimal("0.01"))])
        # toleranta 1 cent pe quantize-ul valorii finale
        assert lo - Decimal("0.01") <= r.valoare_finala <= hi + Decimal("0.01")

    @given(st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False),
           st.decimals(min_value=Decimal("1000"), max_value=Decimal("50000000"), places=2,
                       allow_nan=False, allow_infinity=False))
    @settings(max_examples=100, deadline=None)
    def test_prop_reconcile_idempotenta(v_p, v_c):
        """Determinism: aceeasi intrare -> aceeasi valoare finala."""
        rez = [_rez("comparatie", v_p), _rez("cost", v_c)]
        kw = {"primara": "comparatie", "ponderi": {"comparatie": _D("0.6"), "cost": _D("0.4")}}
        assert reconcile_profil(rez, **kw).valoare_finala == reconcile_profil(rez, **kw).valoare_finala


# ═════════════════════════════════════════════════════════════════════════════
# RAMURA FALLBACK (fara Hypothesis): parametrizate clasice cu input-uri EXTREME.
# Acelasi set de proprietati, esantion finit ales adversarial.
# ═════════════════════════════════════════════════════════════════════════════
if not HAS_HYPOTHESIS:  # pragma: no cover - mediul nostru are hypothesis

    _PTS = [DepreciationPoint(varsta=0, depreciere=Decimal("0")),
            DepreciationPoint(varsta=20, depreciere=Decimal("0.3")),
            DepreciationPoint(varsta=80, depreciere=Decimal("1"))]

    @pytest.mark.parametrize("vcp", ["-100", "0", "10", "20", "50", "80", "1000"])
    def test_fb_depreciere_in_zero_unu(vcp):
        d = interpolate_depreciation(_D(vcp), _PTS)
        assert Decimal("0") <= d <= Decimal("1")

    def test_fb_depreciere_clamp():
        assert interpolate_depreciation(_D("-50"), _PTS) == Decimal("0")
        assert interpolate_depreciation(_D("999"), _PTS) == Decimal("1")

    @pytest.mark.parametrize("cib", ["0.01", "1000", "99999999.99"])
    @pytest.mark.parametrize("d", ["0", "0.5", "0.99"])
    def test_fb_cin_in_interval(cib, d):
        cin = compute_cin(_D(cib), _D(d), _D(d), _D(d))
        assert 0 < cin <= _D(cib)

    @pytest.mark.parametrize("pret,chirie", [("1000000", "80000"), ("1", "0"), ("99999999", "1")])
    def test_fb_rata_vanzare(pret, chirie):
        r = rata_din_vanzare_inchiriere(_D(pret), _D(chirie))
        assert r >= 0

    @pytest.mark.parametrize("rata", ["0.0001", "0.02", "0.08", "0.15", "0.5", "8"])
    def test_fb_validari_rata_nu_arunca(rata):
        assert valideaza_rata_capitalizare(_D(rata)) is None or isinstance(
            valideaza_rata_capitalizare(_D(rata)), str)

    @pytest.mark.parametrize("vbp", ["1000", "1000000", "50000000"])
    @pytest.mark.parametrize("ra,rb", [("0.02", "0.15"), ("0.05", "0.10")])
    def test_fb_venit_monoton_in_rata(vbp, ra, rb):
        v_lo = evalueaza_venit(DateVenit(venit_brut_potential=_D(vbp), rata_capitalizare=_D(ra))).valoare
        v_hi = evalueaza_venit(DateVenit(venit_brut_potential=_D(vbp), rata_capitalizare=_D(rb))).valoare
        assert v_lo >= v_hi > 0

    @pytest.mark.parametrize("rata", ["0.001", "0.05", "0.30", "0.99"])
    def test_fb_dcf_pozitiv(rata):
        assert evalueaza_dcf([_D("1000"), _D("2000"), _D("3000")], _D(rata)) > 0

    @pytest.mark.parametrize("factor", ["1.01", "2", "100"])
    def test_fb_piata_monotona(factor):
        comps = [_comp("100000", "100"), _comp("200000", "120"), _comp("150000", "110")]
        ridicate = [_comp(_D("100000") * _D(factor), "100"),
                    _comp(_D("200000") * _D(factor), "120"),
                    _comp(_D("150000") * _D(factor), "110")]
        assert evaluate_market(ridicate).valoare_piata > evaluate_market(comps).valoare_piata

    @pytest.mark.parametrize("w", ["0.01", "0.5", "0.99"])
    def test_fb_reconcile_convexa(w):
        rez = [RezultatAbordare(abordare="comparatie", valoare=_D("300000")),
               RezultatAbordare(abordare="cost", valoare=_D("250000"))]
        r = reconcile_profil(rez, primara="comparatie",
                             ponderi={"comparatie": _D(w), "cost": Decimal("1") - _D(w)})
        assert _D("250000") <= r.valoare_finala <= _D("300000")
