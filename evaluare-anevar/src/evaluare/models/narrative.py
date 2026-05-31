"""Sectiuni de text narativ generate pentru raport."""
from __future__ import annotations

from pydantic import BaseModel


class NarrativeSection(BaseModel):
    """Un capitol de text narativ (titlu + continut)."""

    capitol: str
    text: str
