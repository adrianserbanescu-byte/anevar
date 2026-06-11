"""Stocarea pe foldere (sursa de adevăr) + contul local."""
from __future__ import annotations

import pytest


@pytest.fixture
def baza(tmp_path, monkeypatch):
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "date"))
    return tmp_path


def _wizard(**extra):
    w = {"scop": "garantare", "tip_proprietate": "casa", "nume_client": "Pop",
         "id_client": "D001", "au": "100", "acd": "120"}
    w.update(extra)
    return w


def test_versiune_inregistreaza_integritate_si_asumare(baza):
    # ADR-003: fiecare versiune .docx primește hash + moment; prima generare setează asumat_la.
    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Evaluator", _wizard())
    src = baza / "r.docx"
    src.write_bytes(b"PK raport versiunea 1")
    fs.adauga_versiune_docx(uid, src, tip="generat")
    d = fs.incarca(uid)
    assert d.get("asumat_la")                       # prima generare = asumare
    assert len(d["versiuni"]) == 1
    v = d["versiuni"][0]
    assert v["tip"] == "generat" and len(v["hash"]) == 64
    assert fs.verifica_integritate(uid)[0]["ok"] is True   # integru la început


def test_verifica_integritate_detecteaza_alterarea(baza):
    # ADR-003: dacă fișierul .docx asumat e modificat ulterior, hash-ul nu mai corespunde (tamper-evidence).
    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Evaluator", _wizard())
    src = baza / "r.docx"
    src.write_bytes(b"continut original asumat")
    nume = fs.adauga_versiune_docx(uid, src, tip="generat")
    (fs.baza() / uid / nume).write_bytes(b"continut ALTERAT dupa asumare")
    rez = fs.verifica_integritate(uid)
    assert rez[0]["exista"] is True and rez[0]["ok"] is False


def test_lock_identitate_dupa_asumare(baza):
    # ADR-003: după asumare, identitatea e read-only; câmpurile tehnice rămân editabile.
    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    assert fs.este_blocat(fs.incarca(uid)) is False            # neasumat -> editabil
    src = baza / "r.docx"
    src.write_bytes(b"raport")
    fs.adauga_versiune_docx(uid, src, tip="generat")           # asumare
    assert fs.este_blocat(fs.incarca(uid)) is True
    fs.salveaza_wizard(uid, dict(_wizard(), nume_client="ALTUL", au="999"))
    d = fs.incarca(uid)
    assert d["wizard"]["nume_client"] == "Pop"                 # identitate ÎNGHEȚATĂ
    assert d["wizard"]["au"] == "999"                          # tehnicul s-a actualizat


def test_salveaza_wizard_recalc_nume_gol_apoi_completat(baza):
    # Bug Adi 2026-06-09: un dosar creat GOL ramanea blocat pe „?_?_?"; acum salveaza_wizard
    # recalculeaza MEREU numele -> dupa completarea identitatii, „?" dispare. (#7 coverage cod nou.)
    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", {})                       # gol -> nume cu „?"
    assert "?" in fs.incarca(uid)["nume"]
    d = fs.salveaza_wizard(uid, _wizard())                 # completat -> recalculat, fara „?"
    assert "?" not in d["nume"]
    assert fs.incarca(uid)["nume"] == d["nume"]            # persistat pe disc


def test_deblocheaza_cere_motiv_si_logheaza(baza):
    # ADR-003: de-lock typo necesită motiv + intră în audit; re-generarea re-blochează.
    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    src = baza / "r.docx"
    src.write_bytes(b"raport")
    fs.adauga_versiune_docx(uid, src, tip="generat")
    with pytest.raises(ValueError):
        fs.deblocheaza(uid, "   ")                             # motiv gol -> refuzat
    fs.deblocheaza(uid, "typo în nume: Ppop -> Pop")
    d = fs.incarca(uid)
    assert fs.este_blocat(d) is False and d["deblocari"][0]["motiv"].startswith("typo")
    fs.salveaza_wizard(uid, dict(_wizard(), nume_client="Popa"))
    assert fs.incarca(uid)["wizard"]["nume_client"] == "Popa"  # editabil după de-lock
    fs.adauga_versiune_docx(uid, src, tip="generat")           # re-asumare -> re-blochează
    assert fs.este_blocat(fs.incarca(uid)) is True


def test_cloneaza_dosar_nou_neasumat(baza):
    # ADR-003: clonarea face un dosar NOU neasumat cu munca tehnică; sursa rămâne asumată.
    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard(au="120"))
    src = baza / "r.docx"
    src.write_bytes(b"raport")
    fs.adauga_versiune_docx(uid, src, tip="generat")
    nou = fs.cloneaza(uid)
    dnou = fs.incarca(nou)
    assert nou != uid and dnou["wizard"]["au"] == "120"        # munca tehnică copiată
    assert fs.este_blocat(dnou) is False                       # noul dosar e editabil
    assert "asumat_la" not in dnou and not dnou.get("versiuni")
    assert fs.este_blocat(fs.incarca(uid)) is True             # sursa rămâne asumată


def test_lock_concurenta_si_curatare_orfane(baza):
    # ADR-003 item 7: lock de deschidere — alt token = concurent; eliberare; curățare orfane (> TTL).
    import os
    import time

    import evaluare.dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    assert fs.marcheaza_lock(uid, "tokA") is False        # prima deschidere: fără concurență
    assert fs.marcheaza_lock(uid, "tokB") is True         # altă fereastră (alt token, lock proaspăt)
    assert fs.marcheaza_lock(uid, "tokB") is False        # același token -> nu mai e concurent
    fs.elibereaza_lock(uid, "tokB")
    assert not (fs.baza() / uid / ".lock").exists()       # eliberat de deținător
    lock = fs.baza() / uid / ".lock"
    fs.marcheaza_lock(uid, "tokX")
    os.utime(lock, (time.time() - 200, time.time() - 200))  # îl fac orfan (> 90s TTL)
    assert fs.curata_lock_uri_orfane() == 1 and not lock.exists()


def test_listeaza_cache_mtime(baza):
    # Cache antete pe mtime: dosar neschimbat nu se recitește; dosar nou apare; cache corupt se reconstruiește.
    import evaluare.dosare_fs as fs
    u1 = fs.creeaza("L1", "Ev", _wizard())
    assert [d["uuid"] for d in fs.listeaza()] == [u1]
    assert (fs.baza() / "_cache_antete.json").exists()
    assert [d["uuid"] for d in fs.listeaza()] == [u1]          # cache hit, același rezultat
    u2 = fs.creeaza("L1", "Ev", _wizard(id_client="D2"))       # dosar nou NU e ascuns de cache
    assert {d["uuid"] for d in fs.listeaza()} == {u1, u2}
    (fs.baza() / "_cache_antete.json").unlink()                # cache șters -> reconstruire transparentă
    assert len({d["uuid"] for d in fs.listeaza()}) == 2


def test_cont_creare_si_incarcare(baza):
    from evaluare import cont
    assert cont.incarca_cont() is None
    c = cont.salveaza_cont("Adi S", "8717", ["id_client", "nume_client", "scop", "tip_proprietate"])
    assert c["nume"] == "Adi S" and c["legitimatie"] == "8717"
    assert cont.incarca_cont()["format_dosar"][0] == "id_client"


def test_creeaza_listeaza_incarca(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard(),
                     format_dosar=["id_client", "nume_client", "scop", "tip_proprietate"])
    lst = fs.listeaza()
    assert len(lst) == 1 and lst[0]["uuid"] == uid
    assert lst[0]["nume"] == "D001_Pop_garantare_casa"
    d = fs.incarca(uid)
    assert d["wizard"]["au"] == "100"
    assert d["identitate"]["scop"] == "garantare"
    assert d["creator_legitimatie"] == "8717"


def test_retentie_versiuni_docx(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    folder = fs.baza() / uid
    # pre-existente: 12 versiuni vechi (sortabile înaintea celei reale)
    for i in range(12):
        (folder / f"raport-2020{i:02d}01-000000-000000.docx").write_text("x", encoding="utf-8")
    sursa = baza / "nou.docx"
    sursa.write_text("raport nou", encoding="utf-8")
    fs.adauga_versiune_docx(uid, sursa)
    versiuni = list(folder.glob("raport-*.docx"))
    assert len(versiuni) == fs.PASTREAZA_VERSIUNI          # 10 (cele mai vechi șterse)


def test_salveaza_redenumeste_sterge(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    fs.salveaza_wizard(uid, _wizard(au="150"))
    assert fs.incarca(uid)["wizard"]["au"] == "150"
    fs.redenumeste(uid, "Dosar redenumit")
    assert fs.incarca(uid)["nume"] == "Dosar redenumit"
    fs.sterge(uid)
    assert fs.listeaza() == []


def test_diff_noi_existente_disparute(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    d1 = fs.diff()                                     # prima dată: e „nou"
    assert len(d1["noi"]) == 1 and d1["noi"][0]["uuid"] == uid
    d2 = fs.diff()                                     # a doua: e „existent"
    assert len(d2["existente"]) == 1 and d2["noi"] == []
    # „disparute" = folder șters EXTERN (în afara app-ului) → rămâne în index. App-sterge curăță
    # indexul (PII, re-audit G1), deci nu lasă „disparut"; simulăm dispariția EXTERNĂ cu rmtree direct.
    import shutil
    shutil.rmtree(fs.baza() / uid)
    d3 = fs.diff()                                     # dispărut extern → „dispărut"
    assert len(d3["disparute"]) == 1 and d3["disparute"][0]["uuid"] == uid


def test_sterge_curata_index_si_cache_pii(baza):
    # re-audit G1: app-sterge scoate dosarul (PII: nume client) din _index.json + _cache_antete.json
    # IMEDIAT, nu la următorul listeaza()/diff() (înainte rămânea PII tranzitoriu pe disc după ștergere).
    import json

    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    fs.listeaza()                                      # populează _cache_antete.json
    fs.diff()                                          # populează _index.json
    cf, idxf = fs.baza() / "_cache_antete.json", fs.baza() / "_index.json"
    assert uid in json.loads(cf.read_text(encoding="utf-8"))
    assert uid in json.loads(idxf.read_text(encoding="utf-8"))
    fs.sterge(uid)
    assert uid not in json.loads(cf.read_text(encoding="utf-8"))    # cache curățat imediat
    assert uid not in json.loads(idxf.read_text(encoding="utf-8"))  # index curățat imediat


def test_import_acelasi_user_adopta(baza, tmp_path):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    src = fs.baza() / uid
    r = fs.importa_folder(src, "8717", "Adi S")        # același evaluator
    assert r["e_nou"] is False and r["uuid"] == uid


def test_import_alt_user_devine_dosar_nou(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    src = fs.baza() / uid
    r = fs.importa_folder(src, "9999", "Alt Evaluator")  # alt evaluator
    assert r["e_nou"] is True and r["uuid"] != uid
    d = fs.incarca(r["uuid"])
    assert d["creator_legitimatie"] == "9999"


def test_import_folder_invalid_ridica(baza, tmp_path):
    from evaluare import dosare_fs as fs
    gol = tmp_path / "gol"
    gol.mkdir()
    with pytest.raises(ValueError):
        fs.importa_folder(gol, "8717", "Adi S")


# ── Candidați salvați din «Descoperă» (puși în așteptare per dosar) ───────────────
def _candidat(url="https://x.ro/anunt/1", **extra):
    c = {"url": url, "titlu": "Casa P+1", "pret": "120000", "suprafata": "100",
         "teren": "500", "pret_mp": "1200", "poza": "https://x.ro/p.jpg",
         "relevanta": 0.87, "localitate": "Sinaia", "distanta_km": 3.2}
    c.update(extra)
    return c


def test_candidati_salveaza_listeaza_persista(baza):
    # Candidatul salvat = dict-ul ÎNTREG din /api/descopera; persistat în folderul dosarului.
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    assert fs.listeaza_candidati_salvati(uid) == []
    lista = fs.salveaza_candidat(uid, _candidat())
    assert len(lista) == 1 and lista[0]["pret_mp"] == "1200" and lista[0]["distanta_km"] == 3.2
    # persistat pe disc + recitit identic
    assert (fs.baza() / uid / "candidati_salvati.json").exists()
    assert fs.listeaza_candidati_salvati(uid) == lista


def test_candidati_dedup_pe_url(baza):
    # Re-salvarea aceluiași url ÎNLOCUIEȘTE (date proaspete), nu duplică.
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    fs.salveaza_candidat(uid, _candidat(pret="120000"))
    fs.salveaza_candidat(uid, _candidat(pret="115000"))     # același url, preț nou
    lista = fs.listeaza_candidati_salvati(uid)
    assert len(lista) == 1 and lista[0]["pret"] == "115000"
    fs.salveaza_candidat(uid, _candidat(url="https://x.ro/anunt/2"))   # url nou -> al doilea
    assert len(fs.listeaza_candidati_salvati(uid)) == 2


def test_candidati_sterge_pe_url(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    fs.salveaza_candidat(uid, _candidat(url="https://x.ro/a"))
    fs.salveaza_candidat(uid, _candidat(url="https://x.ro/b"))
    ramase = fs.sterge_candidat_salvat(uid, "https://x.ro/a")
    assert [c["url"] for c in ramase] == ["https://x.ro/b"]
    # ștergerea unui url inexistent = no-op (nu crapă)
    assert len(fs.sterge_candidat_salvat(uid, "https://x.ro/zzz")) == 1


def test_candidat_fara_url_ridica(baza):
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    for rau in ({}, {"url": ""}, {"url": "   "}, {"titlu": "fără url"}):
        with pytest.raises(ValueError):
            fs.salveaza_candidat(uid, rau)
    with pytest.raises(ValueError):                          # ștergere fără url
        fs.sterge_candidat_salvat(uid, "")


def test_candidati_uid_invalid_ridica_keyerror(baza):
    # gard UUID (anti path-traversal) — uid non-UUID -> KeyError (404 la router)
    from evaluare import dosare_fs as fs
    for rau in ["..", "../..", "not-a-uuid", "/etc/passwd"]:
        with pytest.raises(KeyError):
            fs.listeaza_candidati_salvati(rau)
        with pytest.raises(KeyError):
            fs.salveaza_candidat(rau, _candidat())
        with pytest.raises(KeyError):
            fs.sterge_candidat_salvat(rau, "https://x.ro/a")


def test_candidati_dosar_inexistent_ridica(baza):
    # uid UUID-valid dar FĂRĂ dosar.json -> KeyError (nu creează folder fantomă cu candidați)
    import uuid as _uuid

    from evaluare import dosare_fs as fs
    with pytest.raises(KeyError):
        fs.salveaza_candidat(str(_uuid.uuid4()), _candidat())


def test_candidati_cap_maxim(baza):
    # plafon anti-DoS: lista nu crește nelimitat; cele mai recente rămân.
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    for i in range(fs.MAX_CANDIDATI_SALVATI + 25):
        fs.salveaza_candidat(uid, _candidat(url=f"https://x.ro/a/{i}"))
    lista = fs.listeaza_candidati_salvati(uid)
    assert len(lista) == fs.MAX_CANDIDATI_SALVATI
    assert lista[-1]["url"].endswith(f"/{fs.MAX_CANDIDATI_SALVATI + 24}")   # ultimul salvat e prezent


def test_candidati_json_corupt_degradeaza(baza):
    # robustețe: candidati_salvati.json corupt -> tratat ca listă goală (nu crapă la listare/salvare).
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("L1", "Ev", _wizard())
    (fs.baza() / uid / "candidati_salvati.json").write_text("{ corupt", encoding="utf-8")
    assert fs.listeaza_candidati_salvati(uid) == []
    assert len(fs.salveaza_candidat(uid, _candidat())) == 1   # salvarea repară fișierul


# ── Manifest formal: cele 4 secțiuni ANEVAR ale dosarului de lucru (I-16) ─────────
def test_manifest_sectiuni_structura_si_etichete(baza):
    # I-16: manifestul are FIX cele 4 secțiuni canonice ANEVAR, în ordine, cu etichete lizibile.
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    m = fs.manifest_dosar(uid)
    assert list(m["sectiuni"].keys()) == ["contractare", "info_client", "prelucrari", "raport"]
    assert [cod for cod, _ in fs.SECTIUNI_DOSAR] == list(m["sectiuni"].keys())
    for cod in m["sectiuni"]:
        assert m["sectiuni"][cod]["eticheta"]                  # fiecare secțiune are etichetă
        assert m["sectiuni"][cod]["n_fisiere"] == 0            # dosar gol -> nimic clasificat
    assert m["uuid"] == uid and m["nr_lucrare"]


def test_manifest_clasifica_continutul_pe_sectiuni(baza):
    # Conținutul real al folderului se proiectează pe secțiunea corectă (euristică pe nume).
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    folder = fs.baza() / uid
    (folder / "contract-evaluare.pdf").write_text("c", encoding="utf-8")          # contractare
    (folder / "extras-cf-12345.pdf").write_text("c", encoding="utf-8")            # info_client
    (folder / "fisa-kyc-client.docx").write_text("c", encoding="utf-8")           # info_client
    (folder / "grila-comparabile.xlsx").write_text("c", encoding="utf-8")         # prelucrari
    (folder / "atasament-oarecare.bin").write_text("c", encoding="utf-8")         # prelucrari (fallback)
    src = baza / "r.docx"
    src.write_bytes(b"raport final")
    fs.adauga_versiune_docx(uid, src, tip="generat")                              # raport
    m = fs.manifest_dosar(uid)
    nume = {cod: {f["fisier"] for f in m["sectiuni"][cod]["fisiere"]} for cod in m["sectiuni"]}
    assert "contract-evaluare.pdf" in nume["contractare"]
    assert {"extras-cf-12345.pdf", "fisa-kyc-client.docx"} <= nume["info_client"]
    assert {"grila-comparabile.xlsx", "atasament-oarecare.bin"} <= nume["prelucrari"]
    assert any(f.startswith("raport-") for f in nume["raport"])


def test_manifest_exclude_infrastructura(baza):
    # Fișierele de infrastructură (dosar.json, index, cache, lock, .tmp) NU sunt conținut de dosar.
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    folder = fs.baza() / uid
    fs.marcheaza_lock(uid, "tok")                          # creează .lock
    fs.listeaza()                                          # creează _cache_antete.json
    (folder / "dosar.json.tmp").write_text("x", encoding="utf-8")
    m = fs.manifest_dosar(uid)
    toate = [f["fisier"] for cod in m["sectiuni"] for f in m["sectiuni"][cod]["fisiere"]]
    for intern in ("dosar.json", ".lock", "_cache_antete.json", "dosar.json.tmp"):
        assert intern not in toate


def test_manifest_candidati_intra_la_prelucrari(baza):
    # Comparabilele salvate din «Descoperă» = informații de piață -> secțiunea «prelucrări».
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    fs.salveaza_candidat(uid, _candidat(url="https://x.ro/a"))
    fs.salveaza_candidat(uid, _candidat(url="https://x.ro/b"))
    m = fs.manifest_dosar(uid)
    comp = [f for f in m["sectiuni"]["prelucrari"]["fisiere"]
            if f.get("tip") == "comparabile_piata"]
    assert len(comp) == 1 and comp[0]["n_intrari"] == 2


def test_manifest_integritate_si_asumare(baza):
    # Manifestul include metadata de integritate (hash-uri reverificate) + starea de asumare/blocare.
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    assert fs.manifest_dosar(uid)["integritate"]["toate_ok"] is None   # fără versiuni încă
    src = baza / "r.docx"
    src.write_bytes(b"raport integru")
    nume = fs.adauga_versiune_docx(uid, src, tip="generat")
    m = fs.manifest_dosar(uid)
    assert m["integritate"]["asumat_la"] and m["integritate"]["blocat"] is True
    assert m["integritate"]["toate_ok"] is True
    # alterăm fișierul asumat -> integritatea pică (tamper-evidence reflectat în manifest)
    (fs.baza() / uid / nume).write_bytes(b"ALTERAT")
    assert fs.manifest_dosar(uid)["integritate"]["toate_ok"] is False


def test_manifest_retentie_5_ani(baza):
    # Nota de retenție: min. 5 ani, cu termen calculat din ancora (asumat_la/creat_la).
    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    src = baza / "r.docx"
    src.write_bytes(b"raport")
    fs.adauga_versiune_docx(uid, src, tip="generat")
    r = fs.manifest_dosar(uid)["retentie"]
    assert r["ani"] == fs.RETENTIE_ANI == 5
    assert "129/2019" in r["baza_legala"]
    # sterge_dupa = ancora + 5 ani (același prefix lună-zi, an +5)
    assert r["ancora"][:4] != r["sterge_dupa"][:4]
    assert int(r["sterge_dupa"][:4]) == int(r["ancora"][:4]) + 5


def test_manifest_uid_invalid_si_inexistent_ridica(baza):
    # gard UUID (anti path-traversal) + dosar inexistent -> KeyError (404 la router).
    import uuid as _uuid

    from evaluare import dosare_fs as fs
    for rau in ["..", "../..", "not-a-uuid", "/etc/passwd"]:
        with pytest.raises(KeyError):
            fs.manifest_dosar(rau)
    with pytest.raises(KeyError):                          # UUID valid dar fără dosar.json
        fs.manifest_dosar(str(_uuid.uuid4()))


# ── UJ-1: persistarea concluziei (valoarea de piață) pe dosar ──────────────────────
def test_salveaza_valoare_finala_persista_concluzia(baza):
    # UJ-1: concluzia calculată se scrie pe dosar (top-level), de unde o citește registrul/BIG.
    from decimal import Decimal

    from evaluare import dosare_fs as fs
    uid = fs.creeaza("8717", "Adi S", _wizard())
    assert "valoare_finala" not in fs.incarca(uid)         # necalculat încă -> niciun câmp
    fs.salveaza_valoare_finala(uid, Decimal("123456.78"))
    d = fs.incarca(uid)
    assert d["valoare_finala"] == "123456.78"               # stocat ca TEXT (ca restul concluziilor)
    assert d.get("valoare_finala_la") and d.get("modificat_la")
    # Aditiv: nu strică identitatea/wizardul existent.
    assert d["wizard"]["nume_client"] == "Pop"


def test_salveaza_valoare_finala_uid_invalid_ridica(baza):
    # gard UUID (anti path-traversal) — uid invalid -> KeyError (404 la router).
    from evaluare import dosare_fs as fs
    with pytest.raises(KeyError):
        fs.salveaza_valoare_finala("../evadare", "1000")
