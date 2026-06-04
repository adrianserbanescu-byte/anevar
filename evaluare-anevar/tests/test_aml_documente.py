"""Generatoare de documente AML (.docx) — verifica titlurile/campurile asteptate."""
from decimal import Decimal

import pytest

from evaluare.aml.documente import (
    genereaza_decizie_desemnare,
    genereaza_evaluare_risc,
    genereaza_fisa_kyc,
    genereaza_norme_interne,
    genereaza_rtn,
    genereaza_rts,
    salveaza,
)
from evaluare.aml.models import (
    BeneficiarReal,
    ClientPF,
    ClientPJ,
    EvaluareRisc,
    FactorRisc,
    PersoanaFizica,
    StatutPEP,
)
from evaluare.aml.raportare import RaportRTN, RaportRTS


def _text(doc) -> str:
    parti = [p.text for p in doc.paragraphs]
    for tab in doc.tables:
        for row in tab.rows:
            parti.extend(c.text for c in row.cells)
    return "\n".join(parti)


# --------------------------------------------------------------------------- #
# Norme interne — 7 capitole obligatorii (Norme art. 8(1) a-g)
# --------------------------------------------------------------------------- #
def test_norme_interne_au_7_capitole():
    doc = genereaza_norme_interne()
    t = _text(doc)
    assert "NORME INTERNE" in t.upper()
    for cuvant in ["raportare", "clientelei", "administrarea riscurilor",
                   "control intern", "protecția personalului", "avertizare", "instruire"]:
        assert cuvant.lower() in t.lower(), cuvant
    # clauze de antet
    assert "aprobat" in t.lower()
    assert "129/2019" in t


# --------------------------------------------------------------------------- #
# Evaluarea de risc
# --------------------------------------------------------------------------- #
def test_evaluare_risc_doc_contine_factori_si_categorie():
    er = EvaluareRisc(
        factori=[FactorRisc(nume="client", valoare=3, pondere=2)],
        scor=Decimal("2.5"), categorie="sporit", nivel_masuri="suplimentare",
        motive_sporit=["PEP efectiv"], data="2026-06-03", data_reevaluare="2027-06-03",
    )
    t = _text(genereaza_evaluare_risc(er))
    assert "EVALUARE" in t.upper() and "RISC" in t.upper()
    assert "sporit" in t.lower()
    assert "client" in t.lower()
    assert "PEP efectiv" in t


# --------------------------------------------------------------------------- #
# Decizie de desemnare — DOAR societate (Norme art. 7)
# --------------------------------------------------------------------------- #
def test_decizie_desemnare_societate():
    p = PersoanaFizica(nume="Ionescu", prenume="Ana", cnp="2900101000000")
    t = _text(genereaza_decizie_desemnare("PJ", p))
    assert "DECIZIE" in t.upper()
    assert "Ionescu" in t and "Ana" in t


def test_decizie_desemnare_pfa_refuzata():
    p = PersoanaFizica(nume="X", prenume="Y")
    with pytest.raises(ValueError):
        genereaza_decizie_desemnare("PFA", p)


# --------------------------------------------------------------------------- #
# Fisa KYC
# --------------------------------------------------------------------------- #
def test_fisa_kyc_pf():
    c = ClientPF(persoana=PersoanaFizica(nume="Popescu", prenume="Ion", cnp="1900101000000"),
                 pep=StatutPEP(este_pep=False))
    t = _text(genereaza_fisa_kyc(c, None))
    assert "KYC" in t.upper() or "CUNOAȘTERE" in t.upper()
    assert "Popescu" in t and "Ion" in t


def test_fisa_kyc_pj_listeaza_beneficiari_reali():
    c = ClientPJ(
        denumire="ACME SRL", cui="RO123",
        beneficiari_reali=[BeneficiarReal(nume="Mare", prenume="Vasile", procent=Decimal("0.55"))],
    )
    t = _text(genereaza_fisa_kyc(c, None))
    assert "ACME SRL" in t
    assert "Mare" in t and "Vasile" in t
    assert "55" in t  # procentul


# --------------------------------------------------------------------------- #
# RTN / RTS
# --------------------------------------------------------------------------- #
def test_rtn_doc():
    r = RaportRTN(suma_eur=Decimal("12000"), data_tranzactie="2026-06-03")
    t = _text(genereaza_rtn(r))
    assert "NUMERAR" in t.upper()
    assert "12000" in t.replace(".", "").replace(",", "") or "12.000" in t


def test_rts_doc_are_avertisment_tipping_off():
    r = RaportRTS(motiv="presiune pentru valoare predeterminată", data_inregistrare="2026-06-05",
                  indicatori=["presiune_valoare_predeterminata"])
    t = _text(genereaza_rts(r))
    assert "SUSPECT" in t.upper()
    assert "38" in t  # art. 38 tipping-off
    assert "divulg" in t.lower()


# --------------------------------------------------------------------------- #
# salveaza
# --------------------------------------------------------------------------- #
def test_salveaza_scrie_fisier(tmp_path):
    doc = genereaza_norme_interne()
    cale = salveaza(doc, tmp_path / "norme.docx")
    assert cale.exists() and cale.stat().st_size > 0
