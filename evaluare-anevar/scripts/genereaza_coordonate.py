"""Genereaza data/coordonate_localitati.json din GeoNames (BUILD-TIME, o singura data).

App-ul e OFFLINE la runtime — tabelul de coordonate e bundle-uit; acest script ruleaza doar pe masina
de dev cand se reimprospateaza datele. Sursa: download.geonames.org/export/dump/RO.zip (CC-BY 4.0)
+ admin1CodesASCII.txt. Potrivire: slug(nume GeoNames) == slug(nume localitate) in acelasi judet;
la duplicate castiga populatia mai mare. Acopera ce se potriveste; localitatile fara match raman
fara coordonate (harta le omite gratios).

Usage: python scripts/genereaza_coordonate.py <RO.txt> <admin1.txt>
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

RO_TXT, ADMIN1_TXT = sys.argv[1], sys.argv[2]
DATA = Path(__file__).resolve().parent.parent / "src" / "evaluare" / "data"


def _slug(text: str) -> str:  # identic cu discovery.portal_search._slug (potrivire consistenta)
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = text.strip().lower()
    return re.sub(r"\s+", "-", text)


jl = json.loads((DATA / "judete_localitati.json").read_text(encoding="utf-8"))
judete_slugs = {j["slug"] for j in jl["judete"]}

# admin1: cod GeoNames (RO.XX) -> slug judet (prin numele ASCII; Bucuresti se potriveste direct)
admin1: dict[str, str] = {}
with open(ADMIN1_TXT, encoding="utf-8") as fh:
    linii_admin1 = fh.readlines()
for line in linii_admin1:
    if not line.startswith("RO."):
        continue
    cod, _nume, ascii_nume, _gid = line.rstrip("\n").split("\t")
    nume = re.sub(r"\s+county$", "", ascii_nume.strip(), flags=re.I)   # "Vaslui County" -> "Vaslui"
    if nume.lower() == "bucharest":                                    # exonim GeoNames
        nume = "Bucuresti"
    slug = _slug(nume)
    if slug in judete_slugs:
        admin1[cod.split(".")[1]] = slug
print(f"admin1 mapate: {len(admin1)}/42")

# GeoNames P (localitati populate): (judet_slug, slug_nume) -> (lat, lng, populatie)
geo: dict[tuple[str, str], tuple[float, float, int]] = {}
with open(RO_TXT, encoding="utf-8") as fh:
    linii_ro = fh.readlines()
for line in linii_ro:
    f = line.rstrip("\n").split("\t")
    if f[6] != "P" or f[8] != "RO":          # doar localitati populate din RO
        continue
    jslug = admin1.get(f[10])
    if jslug is None:
        continue
    lat, lng = float(f[4]), float(f[5])
    pop = int(f[14] or 0)
    # numele principal + asciiname + alternativele romanesti -> acelasi punct
    nume_cand = {f[1], f[2], *f[3].split(",")} if f[3] else {f[1], f[2]}
    for nume in nume_cand:
        s = _slug(nume)
        if not s:
            continue
        cheie = (jslug, s)
        if cheie not in geo or pop > geo[cheie][2]:   # duplicat -> populatia mai mare
            geo[cheie] = (lat, lng, pop)

# potrivire pe lista noastra de localitati
out: dict[str, dict[str, list[float]]] = {}
total = gasite = 0
for jslug, locs in jl["localitati"].items():
    for loc in locs:
        total += 1
        hit = geo.get((jslug, loc["slug"]))
        if hit:
            gasite += 1
            out.setdefault(jslug, {})[loc["slug"]] = [round(hit[0], 5), round(hit[1], 5)]

dest = DATA / "coordonate_localitati.json"
dest.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"acoperire: {gasite}/{total} localitati ({gasite / total:.0%}) -> {dest} "
      f"({dest.stat().st_size // 1024} KB)")
