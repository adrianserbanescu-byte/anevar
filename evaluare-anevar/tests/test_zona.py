from evaluare.zona import extrage_zona


class FakeClient:
    def __init__(self, raspuns):
        self.raspuns = raspuns
    def complete(self, system, user):
        return self.raspuns


def test_extrage_zona_cu_llm():
    client = FakeClient('{"judet": "ilfov", "localitate": "otopeni"}')
    judet, localitate = extrage_zona("Str. Exemplu nr. 10, Otopeni, Ilfov", client=client)
    assert judet == "ilfov"
    assert localitate == "otopeni"


def test_extrage_zona_fallback_fara_client():
    judet, localitate = extrage_zona("Str. Exemplu 10, Otopeni, Ilfov", client=None)
    assert judet == "ilfov"
    assert localitate == "otopeni"


def test_extrage_zona_fallback_o_singura_parte():
    judet, localitate = extrage_zona("Otopeni", client=None)
    assert localitate == "otopeni"
    assert judet is None


def test_extrage_zona_llm_json_invalid_degradeaza():
    client = FakeClient("nu e json")
    judet, localitate = extrage_zona("Str X, Otopeni, Ilfov", client=client)
    assert localitate == "otopeni"
