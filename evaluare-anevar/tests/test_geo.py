"""Geocoding offline (tabel bundle-uit) + haversine + detectia localitatii din URL (dispatch harta+distanta)."""
from evaluare.geo import coordonate, distanta_km, localitate_din_url


def test_coordonate_localitati_cunoscute():
    # tabelul bundle-uit acopera localitatile din judete_localitati.json (slug SAU nume cu diacritice)
    c = coordonate("cluj", "cluj-napoca")
    assert c is not None and 46 < c[0] < 47.5 and 23 < c[1] < 24.5
    assert coordonate("ilfov", "otopeni") is not None
    assert coordonate("Brăila", "Brăila") is not None      # numele cu diacritice se pliaza la slug
    assert coordonate("cluj", "localitate-inexistenta-xyz") is None
    assert coordonate("", "") is None


def test_distanta_km_haversine():
    # Bucuresti (Sector 1; orasul e impartit pe sectoare in tabel) -> Cluj-Napoca ~ 320-330 km
    b, cj = coordonate("bucuresti", "sector-1"), coordonate("cluj", "cluj-napoca")
    assert b is not None and cj is not None
    d = distanta_km(b[0], b[1], cj[0], cj[1])
    assert 300 < d < 350
    assert distanta_km(b[0], b[1], b[0], b[1]) == 0          # acelasi punct -> 0


def test_localitate_din_url_segment_si_cel_mai_lung_match():
    # slug-ul localitatii apare ca segment delimitat in URL-ul anuntului
    assert localitate_din_url("https://x.ro/oferta/casa-otopeni-123", "ilfov") == "otopeni"
    # match-ul mai LUNG castiga (abrud-sat vs abrud, ambele in Alba)
    assert localitate_din_url("https://x.ro/oferta/casa-abrud-sat-9", "alba") == "abrud-sat"
    assert localitate_din_url("https://x.ro/oferta/vila-abrud-9", "alba") == "abrud"
    # fara match / fara segment delimitat -> None (apelantul cade pe localitatea cautata)
    assert localitate_din_url("https://x.ro/oferta/proprietate-99", "ilfov") is None
