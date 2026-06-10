"""Audit a11y (accessibility) cu axe-core pe paginile critice.

Injectează axe-core (v4.x) într-o sesiune Playwright headless, navighează pe ~12 pagini
cheie ale aplicației și colectează violările WCAG. Gate-ul (cerinta A): ZERO violări de
nivel CRITICAL. Severitățile minor/moderate/serious sunt raportate dar nu blochează.

Folosire:
    python scripts/_check_a11y.py                            # contra http://127.0.0.1:8765
    python scripts/_check_a11y.py http://127.0.0.1:8000      # contra alt server
    python scripts/_check_a11y.py --json                     # raport JSON pe stdout
    python scripts/_check_a11y.py --pagini /,/incepe         # subset de pagini (CSV)

Exit code = numărul de **violări CRITICAL** (0 = gate verde; >0 = blocant).

Owner: D (Rol 2, dispatch A #2). NU modifică șabloanele Jinja (ramân ale autorilor lor);
script-ul DOAR auditează + raportează. Integrare în CI = decizia A (chromium e cost
mai mare în CI; local rulează imediat).
"""
from __future__ import annotations

import contextlib
import json
import sys

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

PAGINI = [                                  # ~12 pagini critice (cele care vede evaluatorul cel mai des)
    "/", "/incepe", "/dosare", "/setari", "/documente",
    "/wizard", "/grila", "/descoperire", "/flux", "/feedback",
    "/aml", "/cont",
]


def filtreaza_critice(violari: list[dict]) -> tuple[int, dict]:
    """Numără violările pe severități; returnează (nr_critical, sumar)."""
    sumar = {"critical": 0, "serious": 0, "moderate": 0, "minor": 0}
    for v in violari:
        sumar[v.get("impact") or "minor"] = sumar.get(v.get("impact") or "minor", 0) + 1
    return sumar["critical"], sumar


def auditeaza(base: str, pagini: list[str], json_mode: bool) -> int:
    rezultate: list[dict] = []
    n_critice_total = 0
    axe = Axe()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        for ruta in pagini:
            pg = ctx.new_page()
            url = base.rstrip("/") + ruta
            try:
                pg.goto(url, timeout=10_000, wait_until="domcontentloaded")
                rez = axe.run(pg)
                viol = rez.response.get("violations", [])
                n_critice, sumar = filtreaza_critice(viol)
                rezultate.append({"ruta": ruta, "url": url, "ok": True,
                                  "violations_count": len(viol), "critical": n_critice,
                                  "sumar": sumar, "violations": viol})
                n_critice_total += n_critice
                if not json_mode:
                    print(f"  {'✓' if n_critice == 0 else '✗'} {ruta:<14}  "
                          f"crit={sumar['critical']:>2} ser={sumar['serious']:>2} "
                          f"mod={sumar['moderate']:>2} min={sumar['minor']:>2}")
            except Exception as e:                                       # noqa: BLE001
                rezultate.append({"ruta": ruta, "url": url, "ok": False, "eroare": str(e)})
                if not json_mode:
                    print(f"  ! {ruta:<14}  EROARE: {e}")
            finally:
                with contextlib.suppress(Exception):
                    pg.close()
        browser.close()
    if json_mode:
        print(json.dumps({"base": base, "pagini": len(pagini),
                          "critice_total": n_critice_total, "rezultate": rezultate},
                         ensure_ascii=False, indent=2))
    else:
        print(f"\n=== {n_critice_total} violare(i) CRITICAL pe {len(pagini)} pagini ===")
        if n_critice_total == 0:
            print("✓ Gate a11y OK — zero violări critice.")
        else:
            for r in rezultate:
                if r.get("critical", 0) > 0:
                    print(f"  - {r['ruta']}: {r['critical']} CRITICAL")
                    for v in r.get("violations", []):
                        if v.get("impact") == "critical":
                            print(f"      · {v.get('id')}: {v.get('help', '')}")
    return n_critice_total


def main(argv: list[str]) -> int:
    json_mode = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    pagini = PAGINI
    if "--pagini" in argv:
        i = argv.index("--pagini")
        pagini = [p.strip() for p in argv[i + 1].split(",") if p.strip()]
        argv = argv[:i] + argv[i + 2:]
    base = argv[0] if argv else "http://127.0.0.1:8765"
    return auditeaza(base, pagini, json_mode)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
