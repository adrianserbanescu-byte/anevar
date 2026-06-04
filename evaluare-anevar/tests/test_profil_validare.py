from decimal import Decimal

from evaluare.engine.validation import valideaza_profil
from evaluare.profil import CASA_TEREN_GARANTARE, ProfilEvaluare


def test_profil_implicit_fara_avertismente():
    assert valideaza_profil(CASA_TEREN_GARANTARE) == []


def test_pondere_pe_abordare_neaplicabila():
    p = ProfilEvaluare(abordari_aplicabile=["cost"], ponderi={"venit": Decimal("1")})
    issues = valideaza_profil(p)
    assert len(issues) >= 1
    assert any("venit" in i.mesaj for i in issues)


def test_abordari_goale():
    p = ProfilEvaluare(abordari_aplicabile=[])
    issues = valideaza_profil(p)
    assert any(i.nivel == "blocheaza" for i in issues)
