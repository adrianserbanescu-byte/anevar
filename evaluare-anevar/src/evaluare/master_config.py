"""Master config (administrare) — opțiuni definite de admin, aplicate per cont de user.

Hardcodat în app (parte din build). Pe termen lung, valorile alese de fiecare user vin din
DB-ul online de licențe (#4 — comercial); AICI e SURSA opțiunilor disponibile + valorile
IMPLICITE folosite de versiunea locală (Slice A) până la activarea conturilor.

Vezi docs/specs/1-ui-output-first.md (Slice A) și docs/specs/4-comercializare.md (Slice C).
"""
from __future__ import annotations

# ── Câmpuri disponibile pentru NUMELE unui dosar ─────────────────────────────────
# Userul își compune template-ul de nume din ele (la crearea contului — #4). Min 3 câmpuri.
# „id_client" = free-text la dosar NOU, needitabil ulterior, unic; la import se cere ID nou.
CAMPURI_NUME_DOSAR: dict[str, dict] = {
    "id_client":       {"eticheta": "ID client", "tip": "free_text_unic", "editabil_dupa_creare": False},
    "nume_client":     {"eticheta": "Nume client", "tip": "text"},
    "tip_proprietate": {"eticheta": "Tip proprietate", "tip": "enum"},
    "scop":            {"eticheta": "Scop lucrare", "tip": "enum"},
    "data_raport":     {"eticheta": "Data raport", "tip": "data"},
    "data_vizita":     {"eticheta": "Data vizită", "tip": "data"},
    "nume_evaluator":  {"eticheta": "Nume evaluator", "tip": "text"},
    "legitimatie":     {"eticheta": "Legitimație ANEVAR", "tip": "text"},
}

# Template IMPLICIT (Slice A / până userul alege la cont — #4).
TEMPLATE_NUME_IMPLICIT: list[str] = ["id_client", "nume_client", "tip_proprietate"]
NUME_DOSAR_MIN_CAMPURI = 3            # userul alege minim 3 câmpuri în template

# ── Câmpuri de cont (Slice C / #4) ───────────────────────────────────────────────
# Editabile DOAR de admin (din DB-ul online de licențe — nu de user, niciodată din app):
CAMPURI_CONT_DOAR_ADMIN: list[str] = ["email", "nume_complet", "legitimatie", "format_dosare"]
# Singurul pe care userul îl ALEGE (dintr-un dropdown) la crearea contului:
CAMPURI_CONT_ALESE_DE_USER: list[str] = ["format_dosare"]


def nume_dosar(template: list[str] | None, valori: dict[str, str]) -> str:
    """Compune numele unui dosar din template + valori. Lipsa unui câmp → marcaj „?".

    Ex.: nume_dosar(["id_client","nume_client","tip_proprietate"],
                    {"id_client":"D001","nume_client":"Pop","tip_proprietate":"casa"})
         -> "D001_Pop_casa"
    """
    template = template or TEMPLATE_NUME_IMPLICIT
    parti = [str(valori.get(c, "")).strip() or "?" for c in template]
    return "_".join(parti)
