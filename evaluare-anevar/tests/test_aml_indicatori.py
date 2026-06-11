"""Indicatori de suspiciune — checklist HCD 58 art. 6(10) + supliment piata imobiliara (ghid ONPCSB)."""
from evaluare.aml.indicatori import (
    INDICATORI,
    INDICATORI_GHID_IMOBILIAR,
    INDICATORI_HCD58,
    SemnaleIndicatori,
    evalueaza_indicatori,
    propune_rts,
)


def test_baza_are_10_indicatori_hcd58():
    assert len(INDICATORI_HCD58) == 10
    assert all(i.categorie == "hcd58_baza" for i in INDICATORI_HCD58)
    assert all(i.temei == "HCD 58/2023 art. 6(10)" for i in INDICATORI_HCD58)


def test_supliment_imobiliar_din_ghid():
    # exista indicatori suplimentari, specifici pietei imobiliare
    assert len(INDICATORI_GHID_IMOBILIAR) >= 10
    assert all(i.categorie == "ghid_imobiliar" for i in INDICATORI_GHID_IMOBILIAR)
    assert all("Ghid ONPCSB" in i.temei for i in INDICATORI_GHID_IMOBILIAR)


def test_catalog_complet_e_baza_plus_supliment():
    assert [*INDICATORI_HCD58, *INDICATORI_GHID_IMOBILIAR] == INDICATORI
    # fiecare are cheie, text si citat
    for ind in INDICATORI:
        assert ind.cheie and ind.text and ind.temei


def test_chei_unice_in_catalog():
    chei = [i.cheie for i in INDICATORI]
    assert len(chei) == len(set(chei))


def test_fiecare_cheie_are_camp_in_semnale():
    semnale = SemnaleIndicatori()
    for ind in INDICATORI:
        assert hasattr(semnale, ind.cheie)


def test_niciun_semnal_nicio_alerta():
    rez = evalueaza_indicatori(SemnaleIndicatori())
    assert rez == []
    assert propune_rts(SemnaleIndicatori()) is False


def test_presiune_valoare_predeterminata_alerteaza():
    s = SemnaleIndicatori(presiune_valoare_predeterminata=True)
    rez = evalueaza_indicatori(s)
    assert len(rez) == 1
    assert rez[0].cheie == "presiune_valoare_predeterminata"
    assert propune_rts(s) is True


def test_indicator_imobiliar_revanzari_alerteaza():
    s = SemnaleIndicatori(revanzari_rapide_pret_diferit=True)
    rez = evalueaza_indicatori(s)
    assert len(rez) == 1
    assert rez[0].cheie == "revanzari_rapide_pret_diferit"
    assert rez[0].categorie == "ghid_imobiliar"
    assert propune_rts(s) is True


def test_indicator_offshore_paravan_alerteaza():
    s = SemnaleIndicatori(structura_offshore_paravan=True)
    assert propune_rts(s) is True
    assert {i.cheie for i in evalueaza_indicatori(s)} == {"structura_offshore_paravan"}


def test_mai_multe_semnale_baza_si_imobiliar():
    s = SemnaleIndicatori(
        graba_excesiva=True,
        pep_implicat=True,
        onorariu_peste_piata=True,
        plati_numerar_atipice=True,
    )
    chei = {i.cheie for i in evalueaza_indicatori(s)}
    assert chei == {
        "graba_excesiva",
        "pep_implicat",
        "onorariu_peste_piata",
        "plati_numerar_atipice",
    }


def test_ordinea_pastreaza_baza_inaintea_suplimentului():
    s = SemnaleIndicatori(antecedente_penale=True, revanzari_rapide_pret_diferit=True)
    chei = [i.cheie for i in evalueaza_indicatori(s)]
    # cel de baza apare inaintea celui imobiliar (ordinea catalogului)
    assert chei == ["antecedente_penale", "revanzari_rapide_pret_diferit"]


def test_toate_semnalele_active():
    s = SemnaleIndicatori(**{i.cheie: True for i in INDICATORI})
    assert len(evalueaza_indicatori(s)) == len(INDICATORI)
    assert propune_rts(s) is True


def test_orice_indicator_unic_declanseaza_rts_si_e_intors_singur():
    # Mutation guard pentru `evalueaza_indicatori` + `propune_rts`: pentru FIECARE indicator din
    # catalog, bifat singur, funcția întoarce exact acel indicator și propune RTS. Dacă iterarea
    # peste `_CHEI` ar fi restrânsă (ex. doar baza, doar suplimentul, o feliere), un indicator ar
    # fi „mut" și mutantul ar supraviețui testelor punctuale existente.
    for ind in INDICATORI:
        s = SemnaleIndicatori(**{ind.cheie: True})
        rez = evalueaza_indicatori(s)
        assert [i.cheie for i in rez] == [ind.cheie], f"indicatorul {ind.cheie} nu e detectat singur"
        assert propune_rts(s) is True, f"indicatorul {ind.cheie} nu declanșează RTS"


def test_indicatorul_intors_pastreaza_temeiul_si_categoria_corecte():
    # Mutation guard: evalueaza_indicatori întoarce obiectele Indicator COMPLETE din catalog
    # (cu temei + categorie), nu doar cheile. Verificăm un indicator de bază și unul imobiliar.
    s = SemnaleIndicatori(scop_nedefinit=True, plati_numerar_atipice=True)
    dupa_cheie = {i.cheie: i for i in evalueaza_indicatori(s)}
    assert dupa_cheie["scop_nedefinit"].temei == "HCD 58/2023 art. 6(10)"
    assert dupa_cheie["scop_nedefinit"].categorie == "hcd58_baza"
    assert "Ghid ONPCSB" in dupa_cheie["plati_numerar_atipice"].temei
    assert dupa_cheie["plati_numerar_atipice"].categorie == "ghid_imobiliar"


def test_un_singur_semnal_dintre_multe_false_declanseaza_rts():
    # Mutation guard explicit pentru propune_rts (any, NU all): un singur True printre zeci de
    # False trebuie să dea True. Un mutant any->all ar întoarce False aici.
    s = SemnaleIndicatori(adresa_neclara=True)
    assert propune_rts(s) is True
