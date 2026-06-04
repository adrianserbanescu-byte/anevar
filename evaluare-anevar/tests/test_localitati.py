from evaluare.localitati import judete, localitati, slugify


def test_slugify_normalizeaza():
    assert slugify("Ilfov") == "ilfov"
    assert slugify("Alba Iulia") == "alba-iulia"
    assert slugify("Baia de Arieş") == "baia-de-aries"
    assert slugify("Ceru-Băcăinţi") == "ceru-bacainti"
    assert slugify("Sfântu Gheorghe") == "sfantu-gheorghe"


def test_judete_returneaza_42():
    j = judete()
    assert len(j) == 42
    assert all("nume" in x and "slug" in x for x in j)
    nume = [x["nume"] for x in j]
    assert nume == sorted(nume)
    assert any(x["slug"] == "ilfov" for x in j)


def test_localitati_pentru_judet():
    loc = localitati("ilfov")
    assert len(loc) > 0
    assert all("nume" in x and "slug" in x for x in loc)
    assert any(x["slug"] == "otopeni" for x in loc)


def test_localitati_judet_inexistent_lista_goala():
    assert localitati("xxx") == []
