"""Extragere text din documente. PDF digital -> text direct (pypdf); scanuri -> OCR injectabil."""
from __future__ import annotations

import io
from collections.abc import Callable

from evaluare.logging_setup import get_logger

Sursa = str | bytes | bytearray

log = get_logger(__name__)


def text_din_pdf(sursa: Sursa) -> str:
    """Textul incorporat dintr-un PDF digital (extras CF, CPE sunt de obicei digitale).

    pypdf (licență BSD) înlocuiește PyMuPDF (AGPL/comercial Artifex) ca să nu blocheze distribuția
    comercială a .exe-ului — vezi auditul de licențe (D, runda 2). Extragerea de text e suficientă
    aici; scanurile (text gol) rămân pe `ocr_fn` injectabil în `extrage_text`.
    """
    from pypdf import PdfReader

    flux = io.BytesIO(bytes(sursa)) if isinstance(sursa, (bytes, bytearray)) else str(sursa)
    return "\n".join((pagina.extract_text() or "") for pagina in PdfReader(flux).pages)


def extrage_text(sursa: Sursa, ocr_fn: Callable[[Sursa], str] | None = None) -> str:
    """Text din PDF; daca PDF-ul e scanat (text gol) si `ocr_fn` e dat, ruleaza OCR-ul injectat.

    `ocr_fn` e injectabil (ex. pytesseract sau un OCR cloud) → modulul ramane fara dependenta dura.
    """
    try:
        text = text_din_pdf(sursa)
    except Exception as e:
        log.warning("Extragere text PDF esuata, incerc OCR daca e disponibil: %s", e)
        text = ""
    if len(text.strip()) < 20 and ocr_fn is not None:
        try:
            text = ocr_fn(sursa)
        except Exception as e:
            log.warning("OCR injectat a esuat: %s", e)
    return text
