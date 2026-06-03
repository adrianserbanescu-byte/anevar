"""Extragere text din documente. PDF digital -> text direct (fitz); scanuri -> OCR injectabil."""
from __future__ import annotations

from typing import Callable, Optional, Union

Sursa = Union[str, bytes, bytearray]


def text_din_pdf(sursa: Sursa) -> str:
    """Textul incorporat dintr-un PDF digital (extras CF, CPE sunt de obicei digitale)."""
    import fitz  # PyMuPDF

    if isinstance(sursa, (bytes, bytearray)):
        doc = fitz.open(stream=bytes(sursa), filetype="pdf")
    else:
        doc = fitz.open(str(sursa))
    try:
        return "\n".join(pagina.get_text() for pagina in doc)
    finally:
        doc.close()


def extrage_text(sursa: Sursa, ocr_fn: Optional[Callable[[Sursa], str]] = None) -> str:
    """Text din PDF; daca PDF-ul e scanat (text gol) si `ocr_fn` e dat, ruleaza OCR-ul injectat.

    `ocr_fn` e injectabil (ex. pytesseract sau un OCR cloud) → modulul ramane fara dependenta dura.
    """
    try:
        text = text_din_pdf(sursa)
    except Exception:
        text = ""
    if len(text.strip()) < 20 and ocr_fn is not None:
        try:
            text = ocr_fn(sursa)
        except Exception:
            pass
    return text
