import pytest

import evaluare.indice_anevar as ia
from evaluare.indice_anevar import (
    _ANUAL_2021_T2,
    _ORASE_OFFLINE,
    _TRIM_2021_T2,
    _parse,
    _tabel_offline,
    indice_anevar,
)

_HTML = """<html><body><script>
google.charts.load("current", {"packages":["corechart"]});
function drawChart() {
  var data2 = google.visualization.arrayToDataTable([
  ["Municipiu", "Brasov", "Bucuresti", "Cluj-Napoca"],
  ["Q1-Q2/2025", 3.5, 2.1, -0.4],
  ["Q2-Q3/2025", +1.2, 0.8, 4.6],
  ["Q3-Q4/2025", 0.6, 2.7, 4.6],
  ]);
}
</script></body></html>"""


@pytest.fixture(autouse=True)
def _indice_cache_curat():
    """Izoleaza cache-ul indicelui live intre teste."""
    ia._goleste_cache()
    yield
    ia._goleste_cache()


def test_parse_indice_orase_si_perioade():
    d = _parse(_HTML)
    assert d["orase"] == ["Brasov", "Bucuresti", "Cluj-Napoca"]
    assert len(d["perioade"]) == 3
    assert d["perioade"][0]["perioada"] == "Q1-Q2/2025"
    assert d["perioade"][0]["valori"]["Brasov"] == 3.5
    assert d["perioade"][1]["valori"]["Cluj-Napoca"] == 4.6   # +-prefix curatat


def test_indice_anevar_cu_fetcher_injectat():
    d = indice_anevar(fetcher=lambda u: _HTML)
    assert "Bucuresti" in d["orase"]
    assert d["perioade"][-1]["perioada"] == "Q3-Q4/2025"


def test_parse_fara_date_returneaza_gol():
    assert _parse("<html><body>nimic</body></html>") == {"orase": [], "perioade": []}


# --- Fallback offline (gap B2-IND-OFF) ----------------------------------------------------------

def test_tabel_offline_forma_si_valori():
    d = _tabel_offline()
    assert d["offline"] is True
    assert d["sursa"]  # exista o atributie a sursei
    # cele 11 mari orase monitorizate
    assert len(d["orase"]) == 11
    assert "Cluj-Napoca" in d["orase"] and "Bucuresti" in d["orase"]
    # doua perioade: evolutie trimestriala + anuala
    assert [p["perioada"] for p in d["perioade"]] == ["Q1-Q2/2021", "Q2-2020 → Q2-2021"]
    # valori-cheie din raport (T2 2021)
    trim = d["perioade"][0]["valori"]
    anual = d["perioade"][1]["valori"]
    assert trim["Craiova"] == 4.8        # cel mai mare avans trimestrial
    assert trim["Bucuresti"] == 4.0
    assert anual["Brasov"] == 10.1       # singura crestere anuala de doua cifre
    assert anual["Timisoara"] == 2.8     # cea mai mica crestere anuala
    # fiecare oras are valoare in ambele perioade
    for oras in d["orase"]:
        assert oras in trim and oras in anual


def test_offline_acopera_toate_orasele():
    # consistenta interna a tabelelor sursa
    assert set(_TRIM_2021_T2) == set(_ORASE_OFFLINE)
    assert set(_ANUAL_2021_T2) == set(_ORASE_OFFLINE)


def test_indice_anevar_fallback_cand_fetcher_arunca():
    def fetcher_offline(_url):
        raise OSError("fara retea")

    d = indice_anevar(fetcher=fetcher_offline)
    assert d.get("offline") is True
    assert d["perioade"][0]["valori"]["Craiova"] == 4.8


def test_indice_anevar_fallback_cand_pagina_goala():
    # pagina raspunde, dar fara tabelul Google Charts asteptat -> offline
    d = indice_anevar(fetcher=lambda u: "<html><body>schimbat layout</body></html>")
    assert d.get("offline") is True
    assert "Brasov" in d["orase"]


def test_indice_anevar_live_ramane_neschimbat_backward_compat():
    # cand pagina live e valida, NU se activeaza fallback-ul (backward-compatible)
    d = indice_anevar(fetcher=lambda u: _HTML)
    assert "offline" not in d
    assert d["orase"] == ["Brasov", "Bucuresti", "Cluj-Napoca"]


def test_fetcher_injectat_e_apelat_o_data():
    # asiguram ca fetcher injectat e respectat (o singura descarcare) inainte de fallback
    called = {"n": 0}

    def fetcher(_url):
        called["n"] += 1
        return "<html></html>"

    d = indice_anevar(fetcher=fetcher)
    assert called["n"] == 1
    assert d.get("offline") is True


# --- PERF-3: cache TTL pe calea de retea reala -------------------------------------------------

def test_indice_cacheaza_calea_reala(monkeypatch):
    # calea reala foloseste `fetch_html` (fetcher implicit None) -> rezultatul live e cacheat:
    # doua apeluri, o singura descarcare.
    apeluri = {"n": 0}

    def fals_fetch_html(_url):
        apeluri["n"] += 1
        return _HTML

    monkeypatch.setattr(ia, "fetch_html", fals_fetch_html)
    d1 = indice_anevar()
    d2 = indice_anevar()
    assert d1["orase"] == ["Brasov", "Bucuresti", "Cluj-Napoca"]
    assert d2["orase"] == ["Brasov", "Bucuresti", "Cluj-Napoca"]
    assert apeluri["n"] == 1   # al doilea apel vine din cache


def test_indice_cache_expira_dupa_ttl(monkeypatch):
    apeluri = {"n": 0}

    def fals_fetch_html(_url):
        apeluri["n"] += 1
        return _HTML

    ceas = {"t": 5000.0}
    monkeypatch.setattr(ia, "fetch_html", fals_fetch_html)
    monkeypatch.setattr(ia.time, "monotonic", lambda: ceas["t"])
    indice_anevar()
    assert apeluri["n"] == 1
    ceas["t"] += ia._TTL_INDICE_SEC + 1
    indice_anevar()
    assert apeluri["n"] == 2


def test_indice_fallback_offline_nu_se_cacheaza(monkeypatch):
    # cand pagina live e goala -> fallback offline, NESTOCAT: un fetch ulterior (cu date live)
    # trebuie sa poata reveni la datele live.
    stare = {"html": "<html><body>schimbat layout</body></html>"}

    def fals_fetch_html(_url):
        return stare["html"]

    monkeypatch.setattr(ia, "fetch_html", fals_fetch_html)
    d_off = indice_anevar()
    assert d_off.get("offline") is True
    # acum pagina revine cu date live -> NU trebuie servit fallback-ul din cache
    stare["html"] = _HTML
    d_live = indice_anevar()
    assert "offline" not in d_live
    assert d_live["orase"] == ["Brasov", "Bucuresti", "Cluj-Napoca"]


def test_indice_fetcher_injectat_ocoleste_cache():
    # fetcher injectat (≠ fetch_html) -> fiecare apel descarca, fara cache.
    apeluri = {"n": 0}

    def fetcher(_url):
        apeluri["n"] += 1
        return _HTML

    indice_anevar(fetcher=fetcher)
    indice_anevar(fetcher=fetcher)
    assert apeluri["n"] == 2


def test_indice_goleste_cache(monkeypatch):
    apeluri = {"n": 0}

    def fals_fetch_html(_url):
        apeluri["n"] += 1
        return _HTML

    monkeypatch.setattr(ia, "fetch_html", fals_fetch_html)
    indice_anevar()
    ia._goleste_cache()
    indice_anevar()
    assert apeluri["n"] == 2
