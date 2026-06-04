from evaluare.indice_anevar import _parse, indice_anevar

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
