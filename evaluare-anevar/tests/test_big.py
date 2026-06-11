"""Teste pentru modulul BIG (Baza Imobiliară de Garanții) — pregătirea datelor de export raport->BIG."""
from decimal import Decimal

import pytest

from evaluare.big import (
    CAMPURI_OBLIGATORII,
    CampuriMinimeBIG,
    RecipisaBIG,
    construieste_payload_big,
    emite_recipisa,
    emite_rectificativa,
    este_complet,
    genereaza_cod_unic,
    subtip_implicit,
    tip_proprietate_big,
    valideaza_campuri_minime,
)


# ── Nomenclatoare: mapare tip activ intern -> tip proprietate BIG ────────────────────────────────
def test_mapare_tip_activ_la_big():
    assert tip_proprietate_big("casa") == "rezidential"
    assert tip_proprietate_big("apartament") == "rezidential"
    assert tip_proprietate_big("teren") == "teren"
    assert tip_proprietate_big("comercial") == "comercial"
    assert tip_proprietate_big("industrial") == "industrial"
    assert tip_proprietate_big("agricol") == "agricol"
    assert tip_proprietate_big("special") == "special"


def test_mapare_tip_activ_normalizeaza_si_necunoscut():
    assert tip_proprietate_big("  CASA ") == "rezidential"
    assert tip_proprietate_big("inexistent") is None
    assert tip_proprietate_big("") is None


def test_subtip_implicit():
    assert subtip_implicit("apartament") == "Apartament în bloc"
    assert subtip_implicit("teren") == "Teren intravilan"
    assert subtip_implicit("necunoscut") is None


# ── Validarea câmpurilor minime ─────────────────────────────────────────────────────────────────
def _campuri_complete() -> CampuriMinimeBIG:
    return CampuriMinimeBIG(
        banca="Banca Transilvania",
        tip_proprietate="rezidential",
        subtip_proprietate="Apartament în bloc",
        cod_postal="400001",
        judet="cluj",
        localitate="cluj-napoca",
        suprafata=Decimal("65"),
        valoare_piata=Decimal("420000"),
        moneda="RON",
        data_evaluarii="2026-01-16",
        evaluator_nume="Ion Popescu",
        evaluator_legitimatie="12345",
        nr_raport="2026/0042",
    )


def test_campuri_complete_fara_lipsuri():
    c = _campuri_complete()
    assert valideaza_campuri_minime(c) == []
    assert este_complet(c) is True


def test_lipsa_campuri_minime_listate():
    c = CampuriMinimeBIG()  # totul gol
    lipsuri = valideaza_campuri_minime(c)
    # Toate câmpurile obligatorii trebuie raportate ca lipsă (moneda are default 'RON' => prezentă).
    assert "Banca / utilizatorul desemnat (creditorul)" in lipsuri
    assert "Valoarea de piață (concluzia evaluatorului)" in lipsuri
    assert "Codul poștal" in lipsuri
    assert este_complet(c) is False
    # moneda implicită 'RON' => NU apare la lipsuri
    assert "Moneda" not in lipsuri


def test_lipsa_doar_un_camp():
    c = _campuri_complete()
    c.valoare_piata = None
    lipsuri = valideaza_campuri_minime(c)
    assert lipsuri == ["Valoarea de piață (concluzia evaluatorului)"]


def test_camp_text_doar_spatii_e_lipsa():
    c = _campuri_complete()
    c.evaluator_nume = "   "
    assert "Numele evaluatorului" in valideaza_campuri_minime(c)


def test_toate_etichetele_obligatorii_acoperite():
    # fiecare cheie obligatorie e un câmp real pe model
    for cheie in CAMPURI_OBLIGATORII:
        assert hasattr(CampuriMinimeBIG(), cheie)


# ── Constrângeri de model ───────────────────────────────────────────────────────────────────────
def test_valoare_si_suprafata_trebuie_pozitive():
    with pytest.raises(ValueError):
        CampuriMinimeBIG(valoare_piata=Decimal("0"))
    with pytest.raises(ValueError):
        CampuriMinimeBIG(suprafata=Decimal("-1"))


# ── Mapper: dosar/meta -> payload BIG ───────────────────────────────────────────────────────────
def test_construieste_payload_din_dosar_complet():
    meta = {
        "beneficiar": "Banca Transilvania",
        "moneda": "EUR",
        "data_evaluarii": "2026-01-16",
        "data_raportului": "2026-01-20",
        "evaluator_nume": "Ion Popescu",
        "evaluator_legitimatie": "12345",
        "nr_lucrare": "2026/0042",
    }
    profil = {"tip_activ": "apartament", "abordari_aplicabile": ["comparatie", "cost"]}
    localizare = {"cod_postal": "400001", "judet": "cluj", "localitate": "cluj-napoca",
                  "strada": "Memorandumului"}
    descriere = {"suprafata": "65", "utilitati": ["apa", "gaz"], "an_constructie": 1985}

    p = construieste_payload_big(
        meta=meta, profil=profil, localizare=localizare, descriere=descriere,
        valoare_finala=Decimal("420000"),
    )

    assert p.banca == "Banca Transilvania"
    assert p.tip_proprietate == "rezidential"
    assert p.subtip_proprietate == "Apartament în bloc"  # subtip implicit din tip activ
    assert p.cod_postal == "400001"
    assert p.judet == "cluj"
    assert p.suprafata == Decimal("65")
    assert p.utilitati == ["apa", "gaz"]
    assert p.valoare_piata == Decimal("420000")
    assert p.moneda == "EUR"
    assert p.abordare == "Comparație directă"   # prima abordare din profil, etichetată RO
    assert p.data_evaluarii == "2026-01-16"
    assert p.nr_raport == "2026/0042"
    assert este_complet(p) is True


def test_mapper_subtip_explicit_suprascrie_implicit():
    p = construieste_payload_big(
        profil={"tip_activ": "casa", "subtip_proprietate": "Vilă cu mansardă"},
    )
    assert p.subtip_proprietate == "Vilă cu mansardă"


def test_mapper_valoare_din_meta_daca_lipseste_explicit():
    p = construieste_payload_big(meta={"valoare_piata": "123456"})
    assert p.valoare_piata == Decimal("123456")


def test_mapper_dosar_gol_produce_lipsuri():
    p = construieste_payload_big()
    lipsuri = valideaza_campuri_minime(p)
    # un payload gol nu e complet — lipsesc toate câmpurile cheie
    assert "Banca / utilizatorul desemnat (creditorul)" in lipsuri
    assert "Tipul proprietății" in lipsuri
    assert este_complet(p) is False


def test_mapper_valoare_neparsabila_devine_none():
    p = construieste_payload_big(valoare_finala="abc")
    assert p.valoare_piata is None


# ── Recipisa: cod unic persistent, inițială, rectificativă, audit ───────────────────────────────
def test_cod_unic_determinist():
    c = _campuri_complete()
    cod1 = genereaza_cod_unic(c)
    cod2 = genereaza_cod_unic(c)
    assert cod1 == cod2                       # determinist (idempotent)
    assert cod1.startswith("BIG-12345-2026-0042-")


def test_cod_unic_difera_la_valoare_diferita():
    c1 = _campuri_complete()
    c2 = _campuri_complete()
    c2.valoare_piata = Decimal("999999")
    assert genereaza_cod_unic(c1) != genereaza_cod_unic(c2)


def test_emite_recipisa_initiala():
    c = _campuri_complete()
    r = emite_recipisa(c)
    assert isinstance(r, RecipisaBIG)
    assert r.tip == "initiala"
    assert r.cod_unic == genereaza_cod_unic(c)
    assert r.cod_unic_corectat is None
    assert r.nr_raport == "2026/0042"
    assert r.emisa_la                          # timestamp populat


def test_emite_recipisa_cu_cod_oficial():
    c = _campuri_complete()
    r = emite_recipisa(c, cod_unic="OFICIAL-BIG-777")
    assert r.cod_unic == "OFICIAL-BIG-777"


def test_emite_recipisa_incompleta_ridica_eroare():
    c = _campuri_complete()
    c.valoare_piata = None
    with pytest.raises(ValueError, match="câmpuri minime lipsă"):
        emite_recipisa(c)


def test_emite_rectificativa():
    c = _campuri_complete()
    initiala = emite_recipisa(c)
    # corectăm valoarea -> rectificativă pe baza codului unic al înregistrării inițiale
    c.valoare_piata = Decimal("430000")
    rect = emite_rectificativa(c, initiala.cod_unic)
    assert rect.tip == "rectificativa"
    assert rect.cod_unic_corectat == initiala.cod_unic
    # codul rectificativei diferă (valoarea s-a schimbat) — ambele rămân în „baza" (audit trail)
    assert rect.cod_unic != initiala.cod_unic


def test_rectificativa_fara_cod_corectat_ridica_eroare():
    c = _campuri_complete()
    with pytest.raises(ValueError, match="codul unic"):
        emite_rectificativa(c, "")


def test_rectificativa_incompleta_ridica_eroare():
    c = _campuri_complete()
    c.banca = ""
    with pytest.raises(ValueError, match="câmpuri minime lipsă"):
        emite_rectificativa(c, "BIG-vechi-001")
