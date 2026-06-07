"""Config-API ponderi (D1) + axe de radar (D2) — contractul cerut de C, construit de B.

- scor pe axe (Locatie/Fizic/Calitate/Functional) in ScoreBreakdown.axe
- fuzioneaza_override + persistenta locala (ponderi_store)
- endpoint-uri GET/POST /api/descopera/config-ponderi + `axe` in /api/descopera
"""
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from evaluare.db.storage import Storage
from evaluare.discovery.ponderi import PONDERI_BAZA, fuzioneaza_override
from evaluare.discovery.ponderi_store import ponderi_efective, salveaza_override
from evaluare.discovery.profiles import CandidateProfile, SubjectProfile
from evaluare.discovery.scoring import scor_candidat
from evaluare.web.app import create_app

FIXTURES = Path(__file__).parent / "fixtures"


def _app(tmp_path):
    storage = Storage(tmp_path / "t.db")
    storage.init()
    search_html = (FIXTURES / "imobiliare_search.html").read_text(encoding="utf-8")
    listing_html = (FIXTURES / "imobiliare_listing_nextdata.html").read_text(encoding="utf-8")

    def fetcher(url):
        return listing_html if "/oferta/" in url else search_html

    class FakeClient:
        def complete(self, system, user):
            return ('{"an":{"valoare":2010,"text":"2010"},'
                    '"stare":{"treapta":4,"text":"renovat"},'
                    '"finisaj":{"treapta":4,"text":"lux"},'
                    '"incalzire":{"categorie":"centrala_gaz","text":"gaz"},'
                    '"teren":{"valoare":400,"text":"400"},"secundare":[]}')

    return create_app(storage=storage, client=FakeClient(), fetcher=fetcher)


# ── Axe de radar (D2) ──────────────────────────────────────────────────────────────────────
def test_axe_radar_potrivire_perfecta_casa():
    s = SubjectProfile(suprafata_construita=Decimal("120"), an=2013, stare=3, finisaj=4,
                       incalzire="centrala_gaz", teren=Decimal("500"))
    c = CandidateProfile(suprafata_construita=Decimal("120"), an=2013, stare=3, finisaj=4,
                         incalzire="centrala_gaz", teren=Decimal("500"))
    b = scor_candidat(s, c)
    assert set(b.axe) == {"locatie", "fizic", "calitate", "functional"}
    assert b.axe["locatie"] is None        # fara geocoding inca
    assert b.axe["fizic"] == 100 and b.axe["calitate"] == 100 and b.axe["functional"] == 100


def test_axa_calitate_scade_la_stare_finisaj_diferit():
    s = SubjectProfile(suprafata_construita=Decimal("120"), stare=1, finisaj=1)
    c = CandidateProfile(suprafata_construita=Decimal("120"), stare=5, finisaj=4)
    b = scor_candidat(s, c)
    assert b.axe["fizic"] == 100           # suprafata identica
    assert b.axe["calitate"] < 100         # stare/finisaj difera
    assert b.axe["locatie"] is None
    assert b.axe["functional"] is None     # casa fara incalzire/camere cunoscute aici


# ── Merge override + persistenta ───────────────────────────────────────────────────────────
def test_fuzioneaza_override_doar_chei_cunoscute():
    eff = fuzioneaza_override({"apartament": {"etaj": 9}, "necunoscut": {"x": 1},
                               "casa": {"bogus": 5, "an": 2}})
    assert eff["apartament"]["etaj"] == 9
    assert "necunoscut" not in eff
    assert "bogus" not in eff["casa"]
    assert eff["casa"]["an"] == 2
    assert eff["casa"]["suprafata_construita"] == 5   # neatins de override


def test_fuzioneaza_override_gol_sau_invalid():
    assert fuzioneaza_override(None)["casa"] == PONDERI_BAZA
    assert fuzioneaza_override({})["casa"] == PONDERI_BAZA
    assert fuzioneaza_override({"casa": {"an": True}})["casa"]["an"] == 5   # bool ignorat


def test_store_round_trip_si_cumulare(tmp_path):
    assert ponderi_efective(tmp_path)["casa"] == PONDERI_BAZA       # fara fisier -> default
    salveaza_override(tmp_path, {"apartament": {"etaj": 9}})
    salveaza_override(tmp_path, {"casa": {"teren": 3}})             # editare partiala cumuleaza
    eff = ponderi_efective(tmp_path)
    assert eff["apartament"]["etaj"] == 9 and eff["casa"]["teren"] == 3


# ── Endpoint-uri ───────────────────────────────────────────────────────────────────────────
def test_get_config_ponderi(tmp_path):
    data = TestClient(_app(tmp_path)).get("/api/descopera/config-ponderi").json()
    assert data["editabil"] is True
    assert data["ponderi"]["apartament"]["etaj"] == 5
    assert data["sume"]["casa"] == sum(PONDERI_BAZA.values())
    assert "locatie" in data["axe"]
    assert data["axa_atribut"]["stare"] == "calitate"


def test_post_config_ponderi_valid_persista(tmp_path):
    client = TestClient(_app(tmp_path))
    r = client.post("/api/descopera/config-ponderi", json={"ponderi": {"casa": {"teren": 5}}})
    assert r.status_code == 200 and r.json()["ok"] is True
    assert r.json()["ponderi"]["casa"]["teren"] == 5
    # persistat -> un GET ulterior reflecta
    assert client.get("/api/descopera/config-ponderi").json()["ponderi"]["casa"]["teren"] == 5


def test_post_config_ponderi_invalid_422(tmp_path):
    client = TestClient(_app(tmp_path))
    assert client.post("/api/descopera/config-ponderi",
                       json={"ponderi": {"inexistent": {"x": 1}}}).status_code == 422
    assert client.post("/api/descopera/config-ponderi",
                       json={"ponderi": {"casa": {"bogus": 1}}}).status_code == 422
    assert client.post("/api/descopera/config-ponderi",
                       json={"ponderi": {"casa": {"teren": -1}}}).status_code == 422
    # toate zero pe o categorie -> invalid
    z = dict.fromkeys(PONDERI_BAZA, 0)
    assert client.post("/api/descopera/config-ponderi",
                       json={"ponderi": {"casa": z}}).status_code == 422


def test_descopera_include_axe_pe_candidat(tmp_path):
    client = TestClient(_app(tmp_path))
    payload = {"portal": "imobiliare", "judet": "ilfov", "localitate": "otopeni",
               "subiect": {"an": 2013, "stare": 3, "finisaj": 4,
                           "incalzire": "centrala_gaz", "teren": "500"},
               "atribute_secundare": [], "max_candidati": 3}
    c0 = client.post("/api/descopera", json=payload).json()["candidati"][0]
    assert "axe" in c0
    assert set(c0["axe"]) == {"locatie", "fizic", "calitate", "functional"}
    assert c0["axe"]["locatie"] is None
