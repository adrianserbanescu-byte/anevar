"""Teste pentru configurarea jurnalizarii."""
from __future__ import annotations

import logging

from evaluare import logging_setup
from evaluare.ingestie.ocr import extrage_text


def test_configure_logging_scrie_fisier(tmp_path, monkeypatch):
    # forteaza re-configurarea intr-un director temporar
    monkeypatch.setattr(logging_setup, "_configured", False)
    root = logging.getLogger()
    handlere_initiale = list(root.handlers)
    try:
        logging_setup.configure_logging(log_dir=tmp_path)
        log = logging_setup.get_logger("test.evaluare")
        log.info("mesaj de test")
        for h in root.handlers:
            h.flush()
        fisier = tmp_path / "evaluare-anevar.log"
        assert fisier.exists()
        assert "mesaj de test" in fisier.read_text(encoding="utf-8")
    finally:
        # curata handlerele adaugate ca sa nu afecteze alte teste
        for h in list(root.handlers):
            if h not in handlere_initiale:
                root.removeHandler(h)
                h.close()
        logging_setup._configured = False


def test_extrage_text_logheaza_si_nu_arunca_la_pdf_invalid(caplog):
    # bytes care nu sunt PDF -> pypdf arunca -> extrage_text prinde, logheaza, intoarce ""
    with caplog.at_level(logging.WARNING):
        rezultat = extrage_text(b"nu sunt un pdf valid")
    assert rezultat == ""
    assert any("PDF" in r.message for r in caplog.records)
