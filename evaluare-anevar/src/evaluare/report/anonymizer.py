"""Anonimizarea datelor personale inainte de orice apel AI (GDPR).

Inlocuieste valorile sensibile cu marcaje (token-uri) inainte de trimitere si
le restaureaza dupa primirea textului. Cea mai lunga valoare se inlocuieste
prima, ca o valoare sa nu fie subsir al alteia.
"""
from __future__ import annotations

from pydantic import BaseModel

from evaluare.models.meta import EvaluationMeta


class Anonymizer(BaseModel):
    """Pereche de mapari real<->token pentru mascare/demascare."""

    real_to_token: dict[str, str]

    def mask(self, text: str) -> str:
        """Inlocuieste valorile reale cu token-uri (cele mai lungi intai)."""
        result = text
        for real in sorted(self.real_to_token, key=len, reverse=True):
            result = result.replace(real, self.real_to_token[real])
        return result

    def unmask(self, text: str) -> str:
        """Inlocuieste token-urile la loc cu valorile reale."""
        result = text
        for real, token in self.real_to_token.items():
            result = result.replace(token, real)
        return result


def build_anonymizer(meta: EvaluationMeta) -> Anonymizer:
    """Construieste anonimizatorul din datele personale ale lucrarii."""
    candidates = {
        meta.client_nume: "[CLIENT]",
        meta.beneficiar: "[BENEFICIAR]",     # banca/utilizator desemnat — scapase neanonimizat (audit GDPR/SAST)
        meta.adresa: "[ADRESA]",
        meta.numar_cadastral: "[CADASTRAL]",
        meta.carte_funciara: "[CF]",
        meta.evaluator_nume: "[EVALUATOR]",
    }
    real_to_token = {real: token for real, token in candidates.items() if real}
    return Anonymizer(real_to_token=real_to_token)
