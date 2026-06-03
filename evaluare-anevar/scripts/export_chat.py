"""Exporta transcriptul de chat verbatim (user + raspunsuri text) in docs/log_complet.md.

Citeste fisierele .jsonl ale sesiunii, extrage mesajele in ordine cronologica, redacteaza secretele
(chei API) si scrie un Markdown. Idempotent — regenereaza tot fisierul la fiecare rulare (deci poate
fi rulat orar pentru a include discutiile noi).
"""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

PROJ = Path(r"C:/Users/adyse/.claude/projects/C--Users-adyse-anevar")
OUT = Path(__file__).resolve().parents[2] / "log_complet.md"

# Redactare secrete (nu se scriu chei in clar in fisierul comis).
_SECRETE = [
    (re.compile(r"pplx-[A-Za-z0-9]{20,}"), "pplx-[REDACTAT]"),
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}"), "sk-ant-[REDACTAT]"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "sk-[REDACTAT]"),
]


def _redacteaza(s: str) -> str:
    for rx, repl in _SECRETE:
        s = rx.sub(repl, s)
    return s


def _text_din_continut(content) -> str:
    """Extrage doar textul vizibil in chat (fara thinking / tool_use / tool_result)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parti = []
        for bloc in content:
            if isinstance(bloc, dict) and bloc.get("type") == "text":
                parti.append(bloc.get("text", ""))
        return "\n".join(parti)
    return ""


def _curata_user(text: str) -> str:
    """Scoate blocurile injectate de harness (system-reminder, command-*, caveat) din mesajul user."""
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S)
    text = re.sub(r"<command-[a-z]+>.*?</command-[a-z]+>", "", text, flags=re.S)
    text = re.sub(r"<local-command-stdout>.*?</local-command-stdout>", "", text, flags=re.S)
    return text.strip()


def colecteaza() -> list[dict]:
    mesaje: dict[str, dict] = {}
    for cale in glob.glob(str(PROJ / "*.jsonl")):
        with open(cale, encoding="utf-8") as f:
            for linie in f:
                try:
                    o = json.loads(linie)
                except (ValueError, TypeError):
                    continue
                t = o.get("type")
                if t not in ("user", "assistant"):
                    continue
                m = o.get("message")
                if not isinstance(m, dict):
                    continue
                text = _text_din_continut(m.get("content"))
                if t == "user":
                    text = _curata_user(text)
                text = text.strip()
                if not text:
                    continue
                uuid = o.get("uuid") or f"{o.get('timestamp')}-{t}-{hash(text) & 0xffffff}"
                mesaje[uuid] = {"rol": t, "ts": o.get("timestamp", ""), "text": text}
    return sorted(mesaje.values(), key=lambda x: x["ts"])


def scrie(mesaje: list[dict]) -> None:
    linii = [
        "# Log complet (verbatim) — sesiune proiect evaluare ANEVAR",
        "",
        "> Transcript brut al conversatiei (mesaje user + raspunsurile text ale asistentului), in",
        "> ordine cronologica, fara procesare/rezumare. Generat din fisierele de sesiune .jsonl de",
        "> `evaluare-anevar/scripts/export_chat.py`. Secretele (chei API) sunt redactate. Se",
        "> regenereaza la fiecare rulare (actualizare orara). Pentru sinteza, vezi `log.md`.",
        "",
        f"**Mesaje:** {len(mesaje)}.",
        "",
        "---",
        "",
    ]
    for m in mesaje:
        eticheta = "User" if m["rol"] == "user" else "Assistant"
        ts = m["ts"][:19].replace("T", " ")
        linii.append(f"## {eticheta}  ·  {ts}")
        linii.append("")
        linii.append(_redacteaza(m["text"]))
        linii.append("")
    OUT.write_text("\n".join(linii), encoding="utf-8")
    print(f"scris {OUT} — {len(mesaje)} mesaje, {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    scrie(colecteaza())
