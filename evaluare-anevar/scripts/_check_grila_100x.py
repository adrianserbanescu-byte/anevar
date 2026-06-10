"""E2E Playwright — regresie COMPORTAMENTALA pt bug-ul 100x (seam UI<->motor, finding C-HIGH).

Complement la test_dosar_grila_procentuala.py (STATIC pe sursa). Aici conducem browserul real:
punem '5' intr-o ajustare PROCENTUALA in fiecare din cele 3 grile din workspace (casa/teren/chirii),
interceptam POST-ul catre /api/grila-* si verificam ca payload-ul ajunge la motor ca FRACTIE '0.05'
(nu '5'). Fara conversia /100 din compForm, '5' = +500% => valoare 100x gresita + alerta M2 falsa.

Frontend-ul JS nu e acoperit de pytest; testul static poate trece in timp ce cablarea formularului
se rupe — de-asta verificam COMPORTAMENTUL real (compForm -> fetch), nu doar sursa.

Inputurile grilelor sunt construite la incarcarea paginii (IIFE), deci exista chiar daca sub-panoul
e ascuns; le completam + declansam calculul prin JS (independent de vizibilitatea tab-ului — alte
teste acopera navigarea). Ruleaza pe server la BASE (implicit 127.0.0.1:8765; ANEVAR_E2E_BASE).
Iese 0 daca toate grilele prezente trimit 0.05; 1 altfel.
"""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get("ANEVAR_E2E_BASE", "http://127.0.0.1:8765")
H = {"Origin": BASE, "Referer": BASE + "/cont", "Content-Type": "application/json"}
rez = []


def check(nume, cond, detaliu=""):
    rez.append(bool(cond))
    print(("  OK  " if cond else " FAIL ") + nume + (f"  [{detaliu}]" if detaliu and not cond else ""))


# Umple, prin JS, suprafata subiect + 3 comparabile + '5' pe prima ajustare procentuala.
# Returneaza nr. de celule de ajustare procentuala completate (diagnostic).
FILL_JS = """
({supr, pret, sup, aj}) => {
  const q = s => document.querySelector(s);
  const e = q('#'+supr); if(!e) return -1; e.value='120';
  for(let i=0;i<3;i++){
    const pc=q('.'+pret+"[data-i='"+i+"']"); if(pc) pc.value='250000';
    const sc=q('.'+sup+"[data-i='"+i+"']");  if(sc) sc.value='120';
  }
  // prima ajustare PROCENTUALA: in dosar.html elementele valorice au tip 'valorica'; gasim un
  // data-e ale carui header NU contine 'lei' (=> procentuala '%'). Fallback: primul data-e.
  const cells=[...document.querySelectorAll('.'+aj+"[data-i='0']")];
  if(!cells.length) return 0;
  let target=cells[0];
  for(const c of cells){
    const th=c.closest('tr')?.querySelector('th');
    if(th && /%/.test(th.textContent) && !/lei/i.test(th.textContent)){ target=c; break; }
  }
  target.value='5';
  return cells.length;
}
"""


def _proc_vals(body):
    out = []
    for c in body.get("comparabile", []):
        for a in c.get("adjustments", []):
            if a.get("tip") == "procentuala":
                out.append(a.get("valoare"))
    return out


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context()
    ctx.request.post(BASE + "/api/cont", headers=H, data={
        "nume": "E2E QA", "legitimatie": "999",
        "format_dosar": ["client_nume", "tip_proprietate", "scop"]})
    uid = ctx.request.post(BASE + "/api/dosar", headers=H, data={"wizard": {}}).json()["uuid"]

    p = ctx.new_page()
    p.goto(BASE + "/dosar/" + uid)
    p.wait_for_load_state("networkidle")

    GRILE = [
        ("g-supr",  "g-pret",  "g-sup",  "g-aj",  "g-calc",  "/api/grila-casa"),
        ("gt-supr", "gt-pret", "gt-sup", "gt-aj", "gt-calc", "/api/grila-teren"),
        ("gc-supr", "gc-pret", "gc-sup", "gc-aj", "gc-calc", "/api/grila-chirii"),
    ]
    for supr, pret_c, sup_c, aj_c, calc, api in GRILE:
        nume = api.split("/")[-1]
        if not p.query_selector("#" + calc):
            check(f"{nume}: grila prezenta", False, "buton calc lipsa")
            continue
        n = p.evaluate(FILL_JS, {"supr": supr, "pret": pret_c, "sup": sup_c, "aj": aj_c})
        if n <= 0:
            check(f"{nume}: celule completate", False, f"fill ret={n}")
            continue
        try:
            with p.expect_request("**" + api, timeout=8000) as ri:
                p.eval_on_selector("#" + calc, "e => e.click()")
            body = ri.value.post_data_json or {}
        except Exception as ex:  # noqa: BLE001
            check(f"{nume}: request emis", False, str(ex)[:60])
            continue
        proc = _proc_vals(body)
        check(f"{nume}: '5' -> 0.05 in payload (anti 100x)",
              "0.05" in proc and "5" not in proc, f"procentuale trimise={proc}")

    p.close()
    b.close()

total, ok = len(rez), sum(rez)
print(f"\nE2E grila 100x: {ok}/{total} OK")
sys.exit(0 if ok == total and total > 0 else 1)
