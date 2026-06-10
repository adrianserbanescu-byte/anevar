"""Regresie seam UI<->motor (finding C-HIGH, re-audit adversarial): grilele din dosar.html TREBUIE
sa imparta ajustarile PROCENTUALE la 100 inainte de a le trimite la /api/grila-* (ca grila.html L208).

Bug original: headerele de coloana ziceau '%' dar codul trimitea valoarea RAW -> un '5' tastat de
evaluator devenea +500% (nu +5%) => valoare de piata/teren/chirie 100x gresita + alerta prudentiala
M2 (prag 25%) declansata fals (orice 5 > 0.25). Engine-ul asteapta FRACTII (0.05 = 5%), exact ce
trimite grila.html standalone. dosar.html aliniat: procentuala -> parseFloat(v)/100; valorica = brut.

Test de caracterizare pe template (frontend JS nu e acoperit de suita Python). C adauga separat un
test E2E Playwright in lane-ul webapp-testing.
"""
import re
from pathlib import Path

DOSAR = Path(__file__).resolve().parent.parent / "src" / "evaluare" / "web" / "templates" / "curent" / "dosar.html"


def _push_bloc(cls: str) -> str:
    html = DOSAR.read_text(encoding="utf-8")
    m = re.search(re.escape(cls) + r".{0,500}?aj\.push\((.*?)\);", html, re.S)
    assert m, f"blocul aj.push pentru {cls} nu a fost gasit in dosar.html"
    return m.group(1)


def test_cele_3_grile_impart_procentuala_la_100():
    # casa (.g-aj), teren (.gt-aj), chirii (.gc-aj): fara /100 ar reveni bug-ul 100x.
    for cls in (".g-aj", ".gt-aj", ".gc-aj"):
        bloc = _push_bloc(cls)
        assert "/100" in bloc, f"grila {cls} NU imparte procentuala la 100: {bloc[:140]}"


def test_grilele_cu_valorica_raman_conditionale_pe_tip():
    # casa + chirii au elemente 'valorica' (lei) care NU se impart -> push conditional pe e.tip.
    for cls in (".g-aj", ".gc-aj"):
        bloc = _push_bloc(cls)
        assert "procentuala" in bloc, f"{cls} trebuie conditional pe tip (valorica ramane bruta)"


def test_hint_grila_nu_mai_contrazice_headerul_procent():
    # hint-urile ziceau 'fracție 0,05' in timp ce headerele de coloana zic '%' -> contradictie.
    # Acum aliniate la conventia '% puncte' (5 = +5%), consistent cu grila.html.
    html = DOSAR.read_text(encoding="utf-8")
    assert "fracție 0,05" not in html, "hint contradictoriu 'fracție 0,05' inca prezent (headerele zic '%')"
