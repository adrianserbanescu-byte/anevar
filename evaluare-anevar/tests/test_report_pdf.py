"""Teste pentru convertorul .docx -> .pdf (report/pdf.py)."""
from __future__ import annotations

import pytest
from docx import Document

from evaluare.report import pdf
from evaluare.report.pdf import PdfIndisponibil, _gaseste_soffice, docx_to_pdf


def _docx(tmp_path):
    d = tmp_path / "r.docx"
    doc = Document()
    doc.add_paragraph("Raport de test pentru conversie PDF.")
    doc.save(str(d))
    return d


def test_gaseste_soffice_intoarce_cale_sau_none():
    rez = _gaseste_soffice()
    assert rez is None or isinstance(rez, str)


@pytest.mark.skipif(_gaseste_soffice() is None, reason="LibreOffice indisponibil pe această stație")
def test_docx_to_pdf_real_cu_libreoffice(tmp_path):
    # cale reală: dacă soffice e prezent, conversia produce un PDF valid.
    out = docx_to_pdf(_docx(tmp_path))
    assert out.exists() and out.suffix == ".pdf"
    assert out.read_bytes()[:4] == b"%PDF"


def test_docx_to_pdf_indisponibil_ridica(monkeypatch, tmp_path):
    # fără LibreOffice și fără Word (pywin32) -> PdfIndisponibil clar, nu altă excepție.
    monkeypatch.setattr(pdf, "_gaseste_soffice", lambda: None)

    def _fara_word(_docx):
        raise PdfIndisponibil("Word indisponibil (test)")

    monkeypatch.setattr(pdf, "_via_word", _fara_word)
    with pytest.raises(PdfIndisponibil):
        docx_to_pdf(_docx(tmp_path))


def test_docx_to_pdf_soffice_esuat_ridica_indisponibil(monkeypatch, tmp_path):
    # dacă soffice e „găsit" dar conversia eșuează -> PdfIndisponibil (nu SubprocessError brut).
    import subprocess
    monkeypatch.setattr(pdf, "_gaseste_soffice", lambda: "soffice")

    def _boom(*a, **k):
        raise subprocess.SubprocessError("conversie eșuată (test)")

    monkeypatch.setattr(subprocess, "run", _boom)
    with pytest.raises(PdfIndisponibil):
        docx_to_pdf(_docx(tmp_path))
