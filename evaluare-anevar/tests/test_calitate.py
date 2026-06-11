"""Verificarea interna a calitatii (QC) inainte de emiterea raportului (gap G-Q1).

Materializeaza recomandarea ANEVAR «Asigurarea calitatii» (elementul 5: verificare interna a
calitatii INAINTE de emitere) + SEV 100 par. 20. Checklist bifat automat din datele dosarului.
"""
from __future__ import annotations

from decimal import Decimal

from evaluare.assembler import EvaluationInput, construieste_context
from evaluare.calitate import (
    ElementCalitate,
    avertismente,
    blocaje,
    emisibil,
    verifica_calitate,
)

_META = {
    "client_nume": "Ion Pop", "adresa": "Str. Exemplu 1", "numar_cadastral": "777",
    "carte_funciara": "CF 777", "evaluator_nume": "Adi S", "evaluator_legitimatie": "8717",
    "data_evaluarii": "2026-01-16", "data_raportului": "2026-01-16",
}


def _input(meta_over: dict | None = None, **over) -> EvaluationInput:
    meta = dict(_META)
    if meta_over:
        meta.update(meta_over)
    base: dict = {
        "meta": meta,
        "land": {"suprafata": "500"},
        "building": {"au": "100", "acd": "120", "an_referinta": 2025,
                     "elements": [{"element": "S", "cod": "X", "um": "mp", "cantitate": "120",
                                   "cost_unitar": "2000", "an_pif": 2015}],
                     "depreciation_points": [{"varsta": 5, "depreciere": "0.05"}]},
        "valoare_teren": "100000", "metoda": "cost",
    }
    base.update(over)
    return EvaluationInput(**base)


def _ctx(meta_over: dict | None = None, **over):
    return construieste_context(_input(meta_over, **over), client=None)


def _by(checklist, cheie) -> ElementCalitate:
    return next(e for e in checklist if e.cheie == cheie)


# ── Structura checklist-ului ──────────────────────────────────────────────────
def test_checklist_acopera_elementele_minime():
    chei = {e.cheie for e in verifica_calitate(_ctx())}
    assert chei == {
        "comparabile_minime", "cmbu_concluzionat", "tip_valoare_sursa",
        "documente_anexate", "coerenta_moneda_data", "adecvare_scop",
        # aditiv, specifice garantarii (GEV 520 / CRR) — doar nivel ATENTIE
        "esg_riscuri_fizice", "valoare_prudenta_considerata",
    }


def test_fiecare_element_are_titlu_si_referinta():
    for e in verifica_calitate(_ctx()):
        assert e.titlu.strip() and e.referinta.strip()
        assert e.nivel in ("blocheaza", "alerteaza")


# ── Cazul valid (dosar de cost complet) ───────────────────────────────────────
def test_dosar_cost_valid_e_emisibil():
    chk = verifica_calitate(_ctx())
    assert emisibil(chk) is True
    assert blocaje(chk) == []


def test_dosar_cost_valid_semnaleaza_cmbu_si_documente_ca_avertismente():
    # offline (client=None) -> CMBU e placeholder; fara scanuri -> documente lipsesc. Ambele = avertizare,
    # NU blocaj (mirror «warn before», nu opri un dosar altfel valid).
    chk = verifica_calitate(_ctx())
    chei_avert = {e.cheie for e in avertismente(chk)}
    assert "cmbu_concluzionat" in chei_avert
    assert "documente_anexate" in chei_avert


# ── Element: minimum 3 comparabile ────────────────────────────────────────────
def test_comparabile_sub_minim_blocheaza_cand_piata_contribuie():
    chk = verifica_calitate(_ctx(metoda="piata", comparables=[
        {"pret": "100000", "suprafata": "100"},
        {"pret": "100000", "suprafata": "100"},
    ]))  # doar 2 < 3
    e = _by(chk, "comparabile_minime")
    assert e.trecut is False and e.nivel == "blocheaza"
    assert emisibil(chk) is False


def test_comparabile_neobligatorii_cand_piata_nu_contribuie():
    # metoda cost, fara grila de teren -> comparabilele nu sunt cerute (trecut, fara blocaj)
    e = _by(verifica_calitate(_ctx()), "comparabile_minime")
    assert e.trecut is True


def test_comparabile_teren_sub_minim_blocheaza():
    chk = verifica_calitate(_ctx(land_comparables=[
        {"pret_mp": "50", "suprafata": "700"},
        {"pret_mp": "55", "suprafata": "650"},
    ]))  # 2 comparabile de teren < 3
    e = _by(chk, "comparabile_minime")
    assert e.trecut is False and e.nivel == "blocheaza"


# ── Element: CMBU concluzionata ───────────────────────────────────────────────
def test_cmbu_placeholder_nu_trece():
    e = _by(verifica_calitate(_ctx()), "cmbu_concluzionat")
    assert e.trecut is False and e.nivel == "alerteaza"


def test_cmbu_completata_trece():
    ctx = _ctx()
    for s in ctx.narrative:
        if "CMBU" in s.capitol:
            s.text = ("Cea mai buna utilizare este cea rezidentiala existenta: permisa legal, "
                      "posibila fizic, fezabila financiar si maxim productiva.")
    e = _by(verifica_calitate(ctx), "cmbu_concluzionat")
    assert e.trecut is True


# ── Element: tip valoare + sursa ──────────────────────────────────────────────
def test_tip_valoare_implicit_citeaza_standardul():
    e = _by(verifica_calitate(_ctx()), "tip_valoare_sursa")
    assert e.trecut is True   # "Valoarea de piață (SEV 102)" citeaza SEV


def test_tip_valoare_gol_blocheaza():
    chk = verifica_calitate(_ctx(meta_over={"tip_valoare": ""}))
    e = _by(chk, "tip_valoare_sursa")
    assert e.trecut is False and e.nivel == "blocheaza"
    assert emisibil(chk) is False


def test_tip_valoare_fara_sursa_doar_avertizeaza():
    chk = verifica_calitate(_ctx(meta_over={"tip_valoare": "Valoare de piata"}))
    e = _by(chk, "tip_valoare_sursa")
    assert e.trecut is False and e.nivel == "alerteaza"
    assert emisibil(chk) is True   # avertizare, nu blocaj


# ── Element: documente anexate ────────────────────────────────────────────────
def test_documente_lipsa_avertizeaza():
    e = _by(verifica_calitate(_ctx()), "documente_anexate")
    assert e.trecut is False and e.nivel == "alerteaza"


def test_documente_prezente_trec():
    doc = "data:application/pdf;base64,JVBERi0xLjQK"
    e = _by(verifica_calitate(_ctx(documente=[doc])), "documente_anexate")
    assert e.trecut is True


# ── Element: coerenta moneda + data ───────────────────────────────────────────
def test_data_raport_inainte_de_evaluare_blocheaza():
    chk = verifica_calitate(_ctx(meta_over={
        "data_evaluarii": "2026-02-10", "data_raportului": "2026-01-01"}))
    e = _by(chk, "coerenta_moneda_data")
    assert e.trecut is False and e.nivel == "blocheaza"
    assert emisibil(chk) is False


def test_moneda_necunoscuta_avertizeaza():
    chk = verifica_calitate(_ctx(meta_over={"moneda": "USD"}))
    e = _by(chk, "coerenta_moneda_data")
    assert e.trecut is False and e.nivel == "alerteaza"
    assert emisibil(chk) is True


def test_date_coerente_trec():
    e = _by(verifica_calitate(_ctx()), "coerenta_moneda_data")
    assert e.trecut is True


# ── Element: adecvarea concluziei la scop ─────────────────────────────────────
def test_adecvare_implicita_trece():
    e = _by(verifica_calitate(_ctx()), "adecvare_scop")
    assert e.trecut is True


def test_adecvare_metoda_in_afara_profilului_avertizeaza():
    ctx = _ctx()
    # profilul casa/garantare aplica doar cost+comparatie; fortam metoda "venit" -> nealiniere
    ctx.reconciled.metoda_selectata = "venit"
    e = _by(verifica_calitate(ctx), "adecvare_scop")
    assert e.trecut is False and e.nivel == "alerteaza"


def test_adecvare_valoare_nepozitiva_blocheaza():
    ctx = _ctx()
    ctx.reconciled.valoare_finala = Decimal("0")
    chk = verifica_calitate(ctx)
    e = _by(chk, "adecvare_scop")
    assert e.trecut is False and e.nivel == "blocheaza"
    assert emisibil(chk) is False


# ── Element: ESG / riscuri fizice (la garantare, GEV 520) ─────────────────────
def test_riscuri_fizice_lipsa_la_garantare_avertizeaza():
    # scop implicit = garantare; meta.riscuri_fizice gol -> atentie, NU blocaj
    chk = verifica_calitate(_ctx())
    e = _by(chk, "esg_riscuri_fizice")
    assert e.trecut is False and e.nivel == "alerteaza"
    assert emisibil(chk) is True


def test_riscuri_fizice_populate_trec():
    chk = verifica_calitate(_ctx(meta_over={"riscuri_fizice": ["inundabilitate", "seismic"]}))
    e = _by(chk, "esg_riscuri_fizice")
    assert e.trecut is True


def test_riscuri_fizice_neaplicabile_in_afara_garantarii():
    # scop "asigurare" -> profil ASIGURARE (scop != garantare_credit) -> verificarea trece (neaplicabil)
    e = _by(verifica_calitate(_ctx(scop="asigurare")), "esg_riscuri_fizice")
    assert e.trecut is True and e.nivel == "alerteaza"


# ── Element: valoare prudenta considerata (la garantare, CRR) ─────────────────
def test_valoare_prudenta_nota_la_garantare_e_atentie_nu_blocaj():
    chk = verifica_calitate(_ctx())
    e = _by(chk, "valoare_prudenta_considerata")
    assert e.nivel == "alerteaza"
    assert e.trecut is False        # nota/reminder optional la garantare
    assert emisibil(chk) is True    # niciodata blocant


def test_valoare_prudenta_neaplicabila_in_afara_garantarii():
    e = _by(verifica_calitate(_ctx(scop="asigurare")), "valoare_prudenta_considerata")
    assert e.trecut is True and e.nivel == "alerteaza"


def test_elementele_noi_nu_introduc_blocaje():
    # itemii aditivi (ESG + valoare prudenta) sunt mereu nivel ATENTIE — nu apar in blocaje
    chk = verifica_calitate(_ctx())
    chei_blocaje = {e.cheie for e in blocaje(chk)}
    assert "esg_riscuri_fizice" not in chei_blocaje
    assert "valoare_prudenta_considerata" not in chei_blocaje


# ── Helpers ───────────────────────────────────────────────────────────────────
def test_blocaje_si_avertismente_sunt_disjuncte():
    chk = verifica_calitate(_ctx(meta_over={"tip_valoare": ""}))
    b = blocaje(chk)
    a = avertismente(chk)
    assert all(e.nivel == "blocheaza" and not e.trecut for e in b)
    assert all(e.nivel == "alerteaza" and not e.trecut for e in a)
    assert not ({e.cheie for e in b} & {e.cheie for e in a})
    assert emisibil(chk) is (len(b) == 0)
