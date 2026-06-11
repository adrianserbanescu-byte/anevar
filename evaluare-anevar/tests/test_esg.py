"""ESG / riscuri fizice in evaluarea pentru garantarea imprumutului (gap S-5 / G1).

Verifica modulul `evaluare.esg`: catalogul celor 8 riscuri fizice (textual din PdV ANEVAR), generarea
secțiunii ESG (MENȚIONARE, nu cuantificare) și checklist-ul «ai verificat riscurile fizice?».

Invariantul critic al poziției ANEVAR: NU se cuantifica / NU se ierarhizeaza — modulul nu trebuie sa
produca scoruri, probabilitați sau clasamente.
"""
from __future__ import annotations

import pytest

from evaluare.esg import (
    AUTORITATI_SURSA,
    CATALOG_RISCURI_FIZICE,
    DISCLAIMER_COMPETENTA,
    ElementChecklistEsg,
    RiscFizic,
    RiscIdentificat,
    checklist_riscuri_fizice,
    chei_riscuri,
    descriere_sursa,
    genereaza_sectiune_esg,
    risc,
    riscuri_neverificate,
    toate_verificate,
)

# Cheile celor 8 riscuri fizice, in ordinea din PdV ANEVAR (textual).
_CHEI_ASTEPTATE = [
    "cutremure",
    "alunecari_teren",
    "falie_surpare",
    "activitate_vulcanica",
    "furtuni_extreme",
    "inundatii",
    "grindina_precipitatii",
    "incendii",
]


# ── Catalogul celor 8 riscuri fizice ──────────────────────────────────────────
def test_catalog_are_exact_opt_riscuri():
    assert len(CATALOG_RISCURI_FIZICE) == 8


def test_catalog_cheile_si_ordinea_sunt_cele_din_pdv():
    assert chei_riscuri() == _CHEI_ASTEPTATE


def test_fiecare_risc_are_denumire_descriere_si_cel_putin_o_sursa():
    for rf in CATALOG_RISCURI_FIZICE:
        assert rf.denumire.strip()
        assert rf.descriere.strip()
        assert rf.surse_recomandate, f"riscul {rf.cheie} nu are sursa recomandata"


def test_sursele_recomandate_exista_in_nomenclatorul_de_autoritati():
    for rf in CATALOG_RISCURI_FIZICE:
        for s in rf.surse_recomandate:
            assert s in AUTORITATI_SURSA, f"sursa necunoscuta «{s}» la riscul {rf.cheie}"


def test_nomenclatorul_contine_cele_cinci_autoritati_nominale_plus_asigurator():
    assert {"ISU", "ANM", "INHGA", "MMAP", "ISC", "asigurator"} <= set(AUTORITATI_SURSA)


def test_risc_lookup_pe_cheie():
    rf = risc("cutremure")
    assert isinstance(rf, RiscFizic)
    assert rf.denumire == "Cutremure"
    assert risc("inexistent") is None


def test_descriere_sursa_intoarce_denumirea_completa():
    assert descriere_sursa("ISU") == "Inspectoratul pentru Situații de Urgența"
    # cheie necunoscuta -> intoarce cheia in clar (fail-soft)
    assert descriere_sursa("XYZ") == "XYZ"


# ── Generarea secțiunii ESG (menționare, nu cuantificare) ─────────────────────
def test_sectiune_fara_riscuri_mentioneaza_lipsa_si_include_disclaimerul():
    txt = genereaza_sectiune_esg()
    assert "nu au fost semnalate riscuri fizice" in txt
    assert DISCLAIMER_COMPETENTA in txt


def test_sectiune_se_incheie_intotdeauna_cu_disclaimerul():
    txt_gol = genereaza_sectiune_esg([])
    txt_plin = genereaza_sectiune_esg([RiscIdentificat(cheie="cutremure")])
    assert txt_gol.endswith(DISCLAIMER_COMPETENTA)
    assert txt_plin.endswith(DISCLAIMER_COMPETENTA)


def test_risc_cu_document_furnizat_preia_sursa_ca_atare():
    ri = RiscIdentificat(
        cheie="inundatii",
        document_furnizat=True,
        sursa="INHGA",
        observatie="Amplasament in afara zonei inundabile conform hartii de hazard.",
    )
    txt = genereaza_sectiune_esg([ri])
    assert "Inundații și revarsari ale apelor" in txt
    assert "preluata ca atare" in txt
    assert "Institutul Național de Hidrologie și Gospodarire a Apelor" in txt
    assert "Amplasament in afara zonei inundabile" in txt


def test_risc_fara_document_se_mentioneaza_fara_cuantificare():
    ri = RiscIdentificat(cheie="cutremure", document_furnizat=False)
    txt = genereaza_sectiune_esg([ri])
    assert "Cutremure" in txt
    assert "nu au fost puse la dispoziția evaluatorului documente oficiale" in txt
    assert "fara cuantificare" in txt


def test_risc_cu_document_dar_fara_sursa_nu_afiseaza_eticheta_sursa():
    # Mutation guard: detaliul „ (sursa: ...)" se adaugă DOAR dacă eticheta sursei e nevidă
    # (`if eticheta`). Cu sursă goală nu apare paranteza, dar rămâne mențiunea „preluata ca atare".
    ri = RiscIdentificat(cheie="cutremure", document_furnizat=True, sursa="")
    txt = genereaza_sectiune_esg([ri])
    linie = next(ln for ln in txt.split("\n\n") if ln.startswith("- Cutremure"))
    assert "preluata ca atare" in linie
    assert "(sursa:" not in linie


def test_observatia_doar_spatii_nu_adauga_text_in_sectiune():
    # Mutation guard: observația se adaugă doar dacă `.strip()` e nevidă. O observație formată
    # doar din spații NU trebuie să introducă spațiu/text suplimentar; linia se încheie cu punct.
    ri = RiscIdentificat(cheie="inundatii", document_furnizat=True, sursa="INHGA", observatie="   ")
    txt = genereaza_sectiune_esg([ri])
    linie = next(ln for ln in txt.split("\n\n") if ln.startswith("- Inund"))
    assert linie.rstrip().endswith(".")
    assert "  ." not in linie  # fără spațiu dublu înainte de punctul final


def test_observatia_nevida_se_preia_ca_atare_in_sectiune():
    # Complementar: o observație reală e inclusă (apare după detaliul de sursă).
    ri = RiscIdentificat(
        cheie="incendii", document_furnizat=True, sursa="ISU",
        observatie="Distanță sigură față de sursele de incendiu.",
    )
    txt = genereaza_sectiune_esg([ri])
    assert "Distanță sigură față de sursele de incendiu." in txt


def test_sectiune_nu_contine_scoruri_sau_ierarhii():
    # Invariantul ANEVAR: NU se cuantifica. Niciun lexic de scor/probabilitate/ierarhie in CORPUL
    # secțiunii (per-risc). Disclaimerul foloseste legitim aceste cuvinte ca sa le NEGE («nu
    # ierarhizeaza», «excede ... scala de probabilitate»), deci il excludem din verificare.
    ri = [RiscIdentificat(cheie=c, document_furnizat=True, sursa="ANM") for c in chei_riscuri()]
    txt = genereaza_sectiune_esg(ri)
    corp = txt.replace(DISCLAIMER_COMPETENTA, "").lower()
    for interzis in ("scor", "probabilitate", "ierarhi", "clasament", "% ", "rang"):
        assert interzis not in corp, f"corpul ESG nu trebuie sa contina «{interzis}»"


def test_disclaimerul_afirma_necuantificarea_si_lipsa_competentei():
    d = DISCLAIMER_COMPETENTA.lower()
    assert "excede competențele" in d
    assert "nu ierarhizeaza" in d
    assert "in afara raportului de evaluare" in d


# ── Checklist «ai verificat riscurile fizice?» ────────────────────────────────
def test_checklist_are_un_punct_pentru_fiecare_din_cele_opt_riscuri():
    chk = checklist_riscuri_fizice()
    assert [e.cheie for e in chk] == _CHEI_ASTEPTATE
    assert all(isinstance(e, ElementChecklistEsg) for e in chk)


def test_checklist_gol_marcheaza_tot_neverificat():
    chk = checklist_riscuri_fizice()
    assert all(not e.verificat for e in chk)
    assert toate_verificate(chk) is False
    assert len(riscuri_neverificate(chk)) == 8


def test_checklist_marcheaza_riscul_identificat_ca_verificat():
    ri = RiscIdentificat(cheie="incendii", document_furnizat=True, sursa="ISU")
    chk = checklist_riscuri_fizice([ri])
    el = next(e for e in chk if e.cheie == "incendii")
    assert el.verificat is True
    assert el.document_furnizat is True
    assert el.sursa == "ISU"
    # celelalte raman neverificate
    assert len(riscuri_neverificate(chk)) == 7


def test_toate_verificate_cand_toate_cele_opt_sunt_identificate():
    ri = [RiscIdentificat(cheie=c) for c in chei_riscuri()]
    chk = checklist_riscuri_fizice(ri)
    assert toate_verificate(chk) is True
    assert riscuri_neverificate(chk) == []


def test_toate_verificate_este_false_la_verificare_partiala():
    # Mutation guard: toate_verificate folosește all(...), NU any(...). Cu o singură verificare
    # din 8, all() => False, any() => True. Fără acest caz parțial, mutantul all->any supraviețuiește.
    chk = checklist_riscuri_fizice([RiscIdentificat(cheie="cutremure")])
    assert toate_verificate(chk) is False
    # complementar: exact cele 7 rămase sunt neverificate (NU 0, NU 8)
    assert len(riscuri_neverificate(chk)) == 7


def test_riscuri_neverificate_returneaza_doar_cele_neverificate_la_verificare_partiala():
    # Mutation guard: filtrul folosește `not e.verificat`. Dacă `not` e scos, ar întoarce
    # riscurile VERIFICATE (1), nu cele neverificate (7).
    chk = checklist_riscuri_fizice([
        RiscIdentificat(cheie="cutremure"),
        RiscIdentificat(cheie="inundatii"),
    ])
    nev = riscuri_neverificate(chk)
    chei_nev = {e.cheie for e in nev}
    assert "cutremure" not in chei_nev
    assert "inundatii" not in chei_nev
    assert len(nev) == 6


def test_checklist_expune_sursele_recomandate_din_catalog():
    chk = checklist_riscuri_fizice()
    el = next(e for e in chk if e.cheie == "incendii")
    assert "ISU" in el.surse_recomandate


@pytest.mark.parametrize("cheie", _CHEI_ASTEPTATE)
def test_fiecare_risc_apare_in_sectiune_cand_e_identificat(cheie):
    rf = risc(cheie)
    assert rf is not None
    txt = genereaza_sectiune_esg([RiscIdentificat(cheie=cheie)])
    assert rf.denumire in txt
