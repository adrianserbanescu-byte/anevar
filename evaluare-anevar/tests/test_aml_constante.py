"""Praguri si termene legale AML — verificare a valorilor cu articolul sursa."""
from decimal import Decimal

from evaluare.aml import constante as C
from evaluare.aml.incadrare import necesita_audit_independent, necesita_persoana_desemnata


def test_praguri_valori_legale():
    assert Decimal("0.25") == C.PRAG_BENEFICIAR_REAL        # art. 4(2)(a)(1)
    assert Decimal("10000") == C.PRAG_NUMERAR_EUR           # art. 7(1)
    assert Decimal("15000") == C.PRAG_TRANZ_OCAZIONALA_EUR  # art. 13(1)(b)(1)
    assert Decimal("15000") == C.PRAG_ANTIFRAGMENTARE_EUR   # art. 7(4)
    assert Decimal("1000") == C.PRAG_TRANSFER_FONDURI_EUR   # art. 13(1)(b)(2)


def test_termene_legale():
    assert C.PERIOADA_POST_PEP_LUNI == 12                   # art. 3(6)
    assert C.RETENTIE_ANI == 5                              # art. 21(1)
    assert C.RETENTIE_PRELUNGIRE_MAX_ANI == 5              # art. 21(3)
    assert C.TERMEN_RTN_ZILE_LUCRATOARE == 3                # art. 7(7)
    assert C.SUSPENDARE_ORE == 24                           # art. 8(3)


def test_persoana_desemnata_pfa_exceptat():
    # PFA / persoana fizica independenta — fara obligatie (Norme art. 7)
    assert necesita_persoana_desemnata("PFA") is False
    assert necesita_persoana_desemnata("PF") is False
    assert necesita_persoana_desemnata("persoana_fizica") is False
    # Societate — obligatie
    assert necesita_persoana_desemnata("PJ") is True
    assert necesita_persoana_desemnata("SRL") is True


def test_audit_independent_2_din_3():
    # zero praguri depasite
    assert necesita_audit_independent(1_000_000, 1_000_000, 5) is False
    # un singur prag depasit (active) — insuficient
    assert necesita_audit_independent(20_000_000, 1_000_000, 5) is False
    # doua praguri (active + CA) — obligatoriu
    assert necesita_audit_independent(20_000_000, 40_000_000, 5) is True
    # toate trei
    assert necesita_audit_independent(20_000_000, 40_000_000, 60) is True
    # CA + salariati, active mic
    assert necesita_audit_independent(1_000_000, 40_000_000, 60) is True


def test_audit_independent_accepta_none():
    assert necesita_audit_independent(None, None, 0) is False
    assert necesita_audit_independent(None, 40_000_000, 60) is True
