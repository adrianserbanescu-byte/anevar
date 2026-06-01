"""Genereaza src/evaluare/data/judete_localitati.json din sursa publica (rulat manual)."""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evaluare.localitati import slugify  # noqa: E402

SURSA = ("https://raw.githubusercontent.com/virgil-av/"
         "judet-oras-localitati-romania/master/judete.json")
IESIRE = (Path(__file__).resolve().parents[1] / "src" / "evaluare" / "data"
          / "judete_localitati.json")


def main() -> None:
    raw = urllib.request.urlopen(SURSA, timeout=30).read()
    data = json.loads(raw)
    judete = []
    localitati = {}
    for j in data["judete"]:
        jslug = slugify(j["nume"])
        judete.append({"nume": j["nume"], "slug": jslug})
        vazute = set()
        lista = []
        for loc in j.get("localitati", []):
            slug = slugify(loc["nume"])
            if slug and slug not in vazute:
                vazute.add(slug)
                lista.append({"nume": loc["nume"], "slug": slug})
        localitati[jslug] = sorted(lista, key=lambda x: x["nume"])
    judete.sort(key=lambda x: x["nume"])
    IESIRE.parent.mkdir(parents=True, exist_ok=True)
    with open(IESIRE, "w", encoding="utf-8") as f:
        json.dump({"judete": judete, "localitati": localitati}, f,
                  ensure_ascii=False, indent=0)
    total = sum(len(v) for v in localitati.values())
    print(f"Scris {len(judete)} judete, {total} localitati -> {IESIRE}")


if __name__ == "__main__":
    main()
