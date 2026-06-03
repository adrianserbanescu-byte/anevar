"""Snapshot reproductibil al unui obiect (input sau rezultat) + hash de integritate."""
from __future__ import annotations

import hashlib
import json


def snapshot(obj) -> dict:
    """Serializeaza determinist un model/dict si calculeaza hash-ul (reproducibilitate)."""
    data = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else obj
    text = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
    return {"continut": text, "hash": hashlib.sha256(text.encode("utf-8")).hexdigest()}
