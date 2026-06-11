"""Garduri de protecție post-review LLM council (gălata A)."""
from __future__ import annotations

from evaluare.ai.narrative import filtreaza_pii_rezidual
from evaluare.aml.documente import genereaza_norme_interne


def test_filtru_pii_mascheaza_cnp_telefon_email():
    txt = "Contact 0722123456, CNP 1900101415011, mail ion.popescu@example.com."
    out = filtreaza_pii_rezidual(txt)
    assert "1900101415011" not in out and "[REDACTAT-CNP]" in out
    assert "0722123456" not in out and "[REDACTAT-TEL]" in out
    assert "ion.popescu@example.com" not in out and "[REDACTAT-EMAIL]" in out


def test_filtru_pii_nu_afecteaza_cifre_normale():
    # sume/suprafețe obișnuite nu trebuie atinse
    txt = "Valoare 135.267 EUR, suprafață 120 mp, an 2015."
    assert filtreaza_pii_rezidual(txt) == txt


def test_documente_aml_contin_disclaimer_juridic():
    import os
    import tempfile

    from evaluare.aml.documente import salveaza
    doc = genereaza_norme_interne()
    out = os.path.join(tempfile.gettempdir(), "_norme_test.docx")
    salveaza(doc, out)
    from docx import Document
    text = "\n".join(p.text for p in Document(out).paragraphs)
    assert "DRAFT GENERAT AUTOMAT" in text
    assert "art. 43/44/49" in text  # sancțiuni corecte: contravenții (43/44) + infracțiune SB (49)
    assert "art. 33" not in text  # regresie: art. 33 = solicitări info (15 zile), NU sancțiuni — vezi docs/conformitate/F-lege-norme-aml.md rând 33
    # disclaimer screening: reflectă realitatea (aplicația CHIAR face screening orientativ pe liste
    # locale), dar rezultatul = „posibilă potrivire" de verificat manual, NU o decizie automată
    assert "screening orientativ" in text
    assert "verificată manual" in text
    assert "NU efectuează verificări automate" not in text  # regresie: textul vechi era fals
