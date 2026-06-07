"""Conversie raport .docx -> .pdf folosind un convertor de pe stația evaluatorului.

Aplicația generează NATIV `.docx` (python-docx, editabil). PDF-ul e OPȚIONAL și necesită un
convertor instalat local: **LibreOffice** (recomandat, gratuit, headless) sau **Microsoft Word**.
Nu se bundle-ază niciun motor PDF în `.exe` (ar dubla mărimea). Dacă niciun convertor nu e
prezent, se ridică `PdfIndisponibil` cu mesaj clar — userul primește oricum `.docx`.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


class PdfIndisponibil(RuntimeError):
    """Niciun convertor PDF (LibreOffice/Word) nu e disponibil pe această stație."""


def _gaseste_soffice() -> str | None:
    """Caută executabilul LibreOffice (PATH + locații uzuale Windows/Linux/macOS)."""
    pe_path = shutil.which("soffice") or shutil.which("soffice.exe")
    if pe_path:
        return pe_path
    candidati = (
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/usr/bin/soffice", "/usr/lib/libreoffice/program/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    )
    return next((c for c in candidati if Path(c).exists()), None)


def _via_soffice(docx: Path, soffice: str) -> Path:
    # Profil izolat: nu intră în conflict cu o instanță LibreOffice deschisă de user.
    profil = Path(tempfile.gettempdir()) / "anevar-lo-profile"
    subprocess.run(
        [soffice, f"-env:UserInstallation=file:///{profil.as_posix()}",
         "--headless", "--convert-to", "pdf", "--outdir", str(docx.parent), str(docx)],
        check=True, capture_output=True, timeout=120,
    )
    pdf = docx.with_suffix(".pdf")
    if not pdf.exists():
        raise PdfIndisponibil("LibreOffice nu a produs PDF.")
    return pdf


def _via_word(docx: Path) -> Path:
    # Best-effort: necesită Microsoft Word + pywin32 (nebundle-at; merge doar dacă sunt instalate).
    try:
        import pythoncom  # type: ignore
        from win32com import client  # type: ignore
    except ImportError as e:
        raise PdfIndisponibil("Microsoft Word (COM) indisponibil.") from e
    pdf = docx.with_suffix(".pdf")
    pythoncom.CoInitialize()
    word = client.Dispatch("Word.Application")
    try:
        doc = word.Documents.Open(str(docx))
        doc.SaveAs(str(pdf), FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()
        pythoncom.CoUninitialize()
    if not pdf.exists():
        raise PdfIndisponibil("Word nu a produs PDF.")
    return pdf


def docx_to_pdf(docx: Path) -> Path:
    """Convertește `.docx` -> `.pdf`. LibreOffice întâi (headless), apoi Word.

    Ridică `PdfIndisponibil` dacă niciun convertor nu e găsit sau conversia eșuează.
    """
    docx = Path(docx)
    soffice = _gaseste_soffice()
    if soffice:
        try:
            return _via_soffice(docx, soffice)
        except (subprocess.SubprocessError, OSError) as e:
            raise PdfIndisponibil(f"Conversia LibreOffice a eșuat: {e}") from e
    return _via_word(docx)
