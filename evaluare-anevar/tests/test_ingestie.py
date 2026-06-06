from decimal import Decimal

from evaluare.ingestie.extractoare import (
    _num,
    extrage_cf,
    extrage_cpe,
    extrage_plan,
    extrage_releveu,
)
from evaluare.ingestie.ocr import extrage_text
from evaluare.ingestie.vlm import extrage_campuri_vlm


def test_num_format_ro():
    assert _num("700") == Decimal("700")
    assert _num("180,5") == Decimal("180.5")
    assert _num("1.910") == Decimal("1910")        # punct = mii
    assert _num("xyz") is None


def test_text_din_pdf_digital_bytes():
    # PDF digital real (creat cu fitz) -> text extras direct, fără OCR
    import fitz

    from evaluare.ingestie.ocr import text_din_pdf
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "Suprafata utila 120 mp")
    data = doc.tobytes()
    doc.close()
    assert "120" in text_din_pdf(data)
    assert "120" in extrage_text(data)              # happy-path prin extrage_text


def test_extrage_text_cade_pe_ocr_la_pdf_invalid():
    # PDF nevalid -> text_din_pdf aruncă -> rulează ocr_fn injectat
    assert extrage_text(b"nu e pdf", ocr_fn=lambda s: "TEXT OCR REZERVA") == "TEXT OCR REZERVA"


def test_extrage_text_ocr_esuat_returneaza_gol():
    def ocr_bad(s):
        raise RuntimeError("ocr indisponibil")
    assert extrage_text(b"nu e pdf", ocr_fn=ocr_bad) == ""


def test_extrage_cf():
    text = ("Extras de carte funciara nr. 20145, localitatea Breaza. "
            "Numar cadastral: 20144. Suprafata de 700 mp. "
            "Proprietar: Andrei Popescu. Foaia C: fara sarcini.")
    d = extrage_cf(text)
    assert d.carte_funciara == "20145"
    assert d.numar_cadastral == "20144"
    assert d.suprafata == Decimal("700")
    assert any("Andrei Popescu" in p for p in d.proprietari)
    assert d.sarcini and "fara sarcini" in d.sarcini.lower()


def test_extrage_releveu():
    text = "Releveu. Suprafata utila: 180 mp. Suprafata construita: 100 mp. Regim de inaltime: P+2E+M."
    d = extrage_releveu(text)
    assert d.arie_utila == Decimal("180")
    assert d.arie_construita == Decimal("100")
    assert d.regim_inaltime == "P+2E+M"


def test_extrage_plan():
    d = extrage_plan("Plan de amplasament. Suprafata teren: 700 mp. Deschidere: 30 m la strada.")
    assert d.suprafata_teren == Decimal("700")
    assert d.deschidere == Decimal("30")
    d2 = extrage_plan("Teren cu S = 1.910 mp, intravilan.")
    assert d2.suprafata_teren == Decimal("1910")


def test_extrage_cpe():
    d = extrage_cpe("Certificat de performanta energetica. Clasa energetica: B. Consum 120 kWh/mp/an.")
    assert d.clasa_energetica == "B"
    assert d.consum == Decimal("120")


def test_ocr_fallback_pe_scanuri():
    # PDF invalid -> text_din_pdf esueaza/gol -> se foloseste ocr_fn injectat
    apelat = {"da": False}

    def fals_ocr(sursa):
        apelat["da"] = True
        return "Suprafata teren: 500 mp"

    text = extrage_text(b"not-a-real-pdf", ocr_fn=fals_ocr)
    assert apelat["da"] is True
    assert "500" in text


def test_vlm_injectabil():
    class FakeVlm:
        def extrage(self, continut, instructiune):
            return '{"arie_utila": 180}'

    assert extrage_campuri_vlm("text", "extrage", FakeVlm()) == {"arie_utila": 180}
    assert extrage_campuri_vlm("text", "extrage", None) is None
    # raspuns invalid -> None
    class BadVlm:
        def extrage(self, c, i):
            return "nu e json"
    assert extrage_campuri_vlm("text", "extrage", BadVlm()) is None
