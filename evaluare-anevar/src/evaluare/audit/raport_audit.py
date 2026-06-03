"""Export al urmei de audit (fisier separat, NU in raportul clientului)."""
from __future__ import annotations

from pathlib import Path

from evaluare.audit.jurnal import JurnalAudit


def text_audit(jurnal: JurnalAudit) -> str:
    """Reprezentare text a urmei de audit, cu verdictul de integritate."""
    integritate = "OK" if jurnal.verifica() else "ALTERATA"
    linii = [f"URMA DE AUDIT — integritate lant: {integritate}",
             f"Numar evenimente: {len(jurnal.evenimente)}", ""]
    for ev in jurnal.evenimente:
        linii.append(f"#{ev.index} [{ev.timestamp}] {ev.tip}: {ev.detalii}  (hash {ev.hash[:12]}…)")
    return "\n".join(linii)


def scrie_audit(jurnal: JurnalAudit, output_path: Path | str) -> Path:
    """Scrie urma de audit intr-un fisier .txt separat. Returneaza calea."""
    output_path = Path(output_path)
    output_path.write_text(text_audit(jurnal), encoding="utf-8")
    return output_path
