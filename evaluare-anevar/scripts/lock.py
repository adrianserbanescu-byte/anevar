"""Regenereaza requirements.lock = inchiderea exacta a dependentelor proiectului.

Pornind de la dependentele declarate in pyproject.toml (roots de mai jos),
traverseaza graful de dependente din mediul instalat si fixeaza fiecare pachet
la versiunea exacta instalata. Rezultatul e un lockfile curat (doar pachetele
proiectului, nu tot site-packages-ul global).

Folosire:
    python scripts/lock.py            # scrie requirements.lock
    python scripts/lock.py --check    # esueaza daca lockfile-ul nu e la zi (CI)
"""
from __future__ import annotations

import argparse
import importlib.metadata as M
import sys
from pathlib import Path

from packaging.requirements import Requirement

# Acelasi set ca [project].dependencies + [dev] din pyproject.toml.
ROOTS = [
    "pydantic", "python-docx", "anthropic", "fastapi", "uvicorn", "jinja2",
    "requests", "beautifulsoup4", "PyMuPDF", "Pillow", "pytest", "httpx", "ruff",
    "pytest-cov",
]
LOCK = Path(__file__).resolve().parent.parent / "requirements.lock"
HEADER = [
    "# requirements.lock - inchiderea exacta a dependentelor proiectului.",
    "# Reproduce build-ul .exe verificat:  pip install -r requirements.lock",
    "# Dezvoltare normala (intervale din pyproject):  pip install -e .[dev]",
    "# Regenerare dupa upgrade verificat:  python scripts/lock.py",
    "#",
]


def _norm(name: str) -> str:
    return name.lower().replace("_", "-")


def closure() -> dict[str, str]:
    seen: set[str] = set()
    out: dict[str, str] = {}
    stack = [_norm(r) for r in ROOTS]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        try:
            dist = M.distribution(name)
        except M.PackageNotFoundError:
            continue
        out[dist.metadata["Name"]] = dist.version
        for req_str in dist.requires or []:
            try:
                req = Requirement(req_str)
            except Exception:
                continue
            if req.marker is not None:
                try:
                    if not req.marker.evaluate({"extra": ""}):
                        continue
                except Exception:
                    pass
            stack.append(_norm(req.name))
    return out


def render() -> str:
    pkgs = closure()
    lines = list(HEADER)
    lines += [f"{n}=={pkgs[n]}" for n in sorted(pkgs, key=str.lower)]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="esueaza daca lockfile nu e la zi")
    args = ap.parse_args()
    content = render()
    if args.check:
        current = LOCK.read_text(encoding="utf-8") if LOCK.exists() else ""
        # comparam doar liniile cu pachete (ignoram data din header)
        def pins(text: str) -> list[str]:
            return sorted(ln for ln in text.splitlines() if ln and not ln.startswith("#"))
        if pins(current) != pins(content):
            print("requirements.lock nu e la zi. Ruleaza: python scripts/lock.py", file=sys.stderr)
            return 1
        print("requirements.lock e la zi.")
        return 0
    LOCK.write_text(content, encoding="utf-8")
    n = sum(1 for ln in content.splitlines() if ln and not ln.startswith("#"))
    print(f"scris {LOCK} - {n} pachete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
