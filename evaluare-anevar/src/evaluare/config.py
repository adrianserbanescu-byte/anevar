"""Configurarea aplicatiei: incarcarea .env si activarea clientului AI."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from evaluare.ai.narrative import AnthropicNarrativeClient, NarrativeClient


def load_env_file(path: Path | str = ".env") -> None:
    """Incarca variabile dintr-un fisier .env in os.environ (nu suprascrie existente)."""
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


class Settings:
    """Setarile efective ale aplicatiei, citite din mediu."""

    def __init__(self, api_key: Optional[str], model: str, output_dir: Path, db_path: Path):
        self.api_key = api_key
        self.model = model
        self.output_dir = output_dir
        self.db_path = db_path

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.environ.get("ANTHROPIC_API_KEY") or None
        model = os.environ.get("NARRATIVE_MODEL", "claude-sonnet-4-6")
        output_dir = Path(os.environ.get("OUTPUT_DIR", "date"))
        db_path = Path(os.environ.get("DB_PATH", "date/evaluari.db"))
        return cls(api_key=api_key, model=model, output_dir=output_dir, db_path=db_path)

    def narrative_client(self) -> Optional[NarrativeClient]:
        """Clientul AI daca exista cheie; altfel None (fallback fara AI)."""
        if not self.api_key:
            return None
        return AnthropicNarrativeClient(api_key=self.api_key, model=self.model)
