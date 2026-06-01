from decimal import Decimal

from evaluare.discovery.extractor import (
    parse_atribute_secundare, extrage_atribute,
)


def test_parse_atribute_secundare():
    linii = "tamplarie: termopan\ngaraj: da\npanouri solare"
    rez = parse_atribute_secundare(linii)
    assert rez == [("tamplarie", "termopan"), ("garaj", "da"), ("panouri solare", None)]


class FakeClient:
    def __init__(self, raspuns):
        self.raspuns = raspuns
        self.calls = []

    def complete(self, system, user):
        self.calls.append((system, user))
        return self.raspuns


def test_extrage_atribute_din_json():
    raspuns = '''```json
    {"an": {"valoare": 2008, "text": "2008"},
     "stare": {"treapta": 4, "text": "renovat 2021"},
     "finisaj": {"treapta": 4, "text": "lux"},
     "incalzire": {"categorie": "centrala_gaz", "text": "centrala pe gaz"},
     "teren": {"valoare": null, "text": null},
     "secundare": [{"nume": "tamplarie", "stare": "diferit", "valoare_gasita": "lemn"}]}
    ```'''
    client = FakeClient(raspuns)
    ext = extrage_atribute("text anunt...", [("tamplarie", "termopan")], client=client)
    assert ext.profile.an == 2008
    assert ext.profile.stare == 4
    assert ext.profile.incalzire == "centrala_gaz"
    assert ext.profile.teren is None
    assert ext.profile.texte["stare"] == "renovat 2021"
    assert ext.secundare[0].nume == "tamplarie"
    assert ext.secundare[0].stare == "diferit"
    assert ext.secundare[0].valoare_gasita == "lemn"


def test_extrage_atribute_fara_client_fallback():
    ext = extrage_atribute("text", [("garaj", None)], client=None)
    assert ext.profile.an is None
    assert ext.profile.stare is None
    assert ext.secundare[0].stare == "nementionat"


def test_extrage_atribute_json_invalid_degradeaza():
    client = FakeClient("nu e json")
    ext = extrage_atribute("text", [], client=client)
    assert ext.profile.an is None      # degradare grațioasă, nu excepție
