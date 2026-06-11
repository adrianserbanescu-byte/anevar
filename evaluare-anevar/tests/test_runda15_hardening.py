"""Regresie RUNDA 15 (hardening robustete, DoS): 4 findings prin Field(max_length=...).

Fix-uri aditive, backward-compatible (valorile normale trec; peste plafon -> ValidationError/422):

F-15-1 (MEDIUM, DoS): `meta.riscuri_fizice` lista nemarginita -> N paragrafe in docx
  (fiecare eticheta = un paragraf serializat XML in python-docx). Fix: max_length=30.
F-15-2 (MEDIUM, DoS): plafon `beneficiari_reali=1000` rezidual prea mare -> 1000 BR x mii
  intrari liste oficiale x SequenceMatcher O(n*m) = minute de CPU. Fix: max_length=200.
F-15-3 (LOW): `cod_postal` / `certificat_energetic` string-uri nemarginite -> balonare
  payload/docx. Fix: max_length=12 / max_length=120.
F-15-4 (LOW): `SemnaleIndicatori.observatii` + `RiscIdentificat.observatie` string-uri
  nemarginite (intra in raspuns/docx ca atare). Fix: max_length=2000 pe ambele.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from evaluare.aml.indicatori import SemnaleIndicatori
from evaluare.aml.models import BeneficiarReal, ClientPJ
from evaluare.esg import RiscIdentificat
from evaluare.models.meta import EvaluationMeta


def _meta(**kw) -> dict:
    return dict(
        client_nume="Ion Popescu",
        adresa="Str. Exemplu nr. 1",
        numar_cadastral="123456",
        carte_funciara="CF123456",
        evaluator_nume="Maria Ionescu",
        evaluator_legitimatie="19567",
        data_evaluarii="2026-01-16",
        data_raportului="2026-01-16",
        **kw,
    )


# ---------------------------------------------------------------- F-15-1 riscuri_fizice marginit
def test_riscuri_fizice_lista_uriasa_respinsa_422():
    with pytest.raises(ValidationError):
        EvaluationMeta(**_meta(riscuri_fizice=["x"] * 200_000))


def test_riscuri_fizice_peste_30_respins():
    with pytest.raises(ValidationError):
        EvaluationMeta(**_meta(riscuri_fizice=["x"] * 31))


def test_riscuri_fizice_in_limita_ok():
    # 8 riscuri reale din catalog + cateva libere — sub plafonul de 30.
    riscuri = ["inundabilitate", "seismic", "alunecari_teren", "incendii"]
    m = EvaluationMeta(**_meta(riscuri_fizice=riscuri))
    assert m.riscuri_fizice == riscuri


def test_riscuri_fizice_exact_30_ok():
    riscuri = [f"risc{i}" for i in range(30)]
    m = EvaluationMeta(**_meta(riscuri_fizice=riscuri))
    assert len(m.riscuri_fizice) == 30


# ---------------------------------------------------------------- F-15-2 beneficiari_reali <=200
def test_beneficiari_reali_peste_200_respins():
    br = [BeneficiarReal(nume="A", prenume="B") for _ in range(201)]
    with pytest.raises(ValidationError):
        ClientPJ(denumire="ACME", beneficiari_reali=br)


def test_beneficiari_reali_in_limita_ok():
    br = [BeneficiarReal(nume="A", prenume="B") for _ in range(10)]
    c = ClientPJ(denumire="ACME", beneficiari_reali=br)
    assert len(c.beneficiari_reali) == 10


def test_beneficiari_reali_exact_200_ok():
    br = [BeneficiarReal(nume="A", prenume="B") for _ in range(200)]
    c = ClientPJ(denumire="ACME", beneficiari_reali=br)
    assert len(c.beneficiari_reali) == 200


# ---------------------------------------------------------------- F-15-3 cod_postal / CPE marginite
def test_cod_postal_uria_respins_422():
    with pytest.raises(ValidationError):
        EvaluationMeta(**_meta(cod_postal="9" * 10_000))


def test_certificat_energetic_uria_respins_422():
    with pytest.raises(ValidationError):
        EvaluationMeta(**_meta(certificat_energetic="A" * 10_000))


def test_cod_postal_si_cpe_normale_ok():
    m = EvaluationMeta(**_meta(cod_postal="010101", certificat_energetic="Clasa B"))
    assert m.cod_postal == "010101"
    assert m.certificat_energetic == "Clasa B"


# ---------------------------------------------------------------- F-15-4 observatii / observatie
def test_semnale_observatii_uriase_respinse_422():
    with pytest.raises(ValidationError):
        SemnaleIndicatori(observatii="x" * 100_000)


def test_risc_identificat_observatie_uriasa_respinsa_422():
    with pytest.raises(ValidationError):
        RiscIdentificat(cheie="inundatii", observatie="x" * 100_000)


def test_observatii_normale_ok():
    s = SemnaleIndicatori(observatii="Client cu comportament normal, fara semnale.")
    assert s.observatii.startswith("Client")
    r = RiscIdentificat(cheie="inundatii", observatie="Informatie preluata din extras INHGA.")
    assert r.observatie.startswith("Informatie")
