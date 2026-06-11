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


class SpyClient:
    """Capteaza payload-ul `user` trimis la complete() (pentru verificarea anonimizarii)."""

    def __init__(self, raspuns):
        self.raspuns = raspuns
        self.user_primit = None

    def complete(self, system, user):
        self.user_primit = user
        return self.raspuns


def test_extrage_zona_mascheaza_pii_inainte_de_ai():
    # F-SEC-1: CNP/tel/email scapate in adresa libera trebuie mascate inainte de trimiterea la AI.
    client = SpyClient('{"judet": "ilfov", "localitate": "otopeni"}')
    adresa = "Str. Exemplu 10, Otopeni, Ilfov, proprietar 1960101410016, tel 0721234567, x@y.ro"
    extrage_zona(adresa, client=client)
    assert "1960101410016" not in client.user_primit
    assert "0721234567" not in client.user_primit
    assert "x@y.ro" not in client.user_primit
    assert "[REDACTAT-CNP]" in client.user_primit
    assert "[REDACTAT-TEL]" in client.user_primit
    assert "[REDACTAT-EMAIL]" in client.user_primit
    # zona corecta inca extrasa (localitatea/judetul nu sunt afectate de mascare)
    assert "Otopeni" in client.user_primit
