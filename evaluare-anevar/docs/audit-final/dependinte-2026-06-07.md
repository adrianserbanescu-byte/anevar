# Audit dependențe — 2026-06-07

**Proiect:** evaluare-anevar (Python). **Unealtă:** `pip-audit 2.10.0` (OSV/PyPI advisory DB).
**Stare finală:** ✅ **No known vulnerabilities found.**

## Constatări inițiale (8 vulnerabilități în 3 pachete) + acțiune
| Pachet | Versiune | Avizuri | Livrat în .exe? | Acțiune |
|--------|----------|---------|-----------------|---------|
| **urllib3** | 2.6.3 → **2.7.0** | PYSEC-2026-141 (header-leak la redirect cross-origin), PYSEC-2026-142 (DoS decompresie) | **DA** (tranzitiv via `requests`) | actualizat + **pin `>=2.7.0,<3`** în pyproject |
| **idna** | 3.13 → **3.18** | CVE-2026-45409 (DoS la `idna.encode` pe input lung) | **DA** (tranzitiv via `requests`) | actualizat + **pin `>=3.15`** în pyproject |
| **pip** | 25.0.1 → latest | 5 CVE (path-traversal extracție wheel/tar, console_scripts etc.) | **NU** (PyInstaller nu bundle-ază pip) | actualizat pe stația de dev (igienă; nu e risc de produs) |

## Note
- Cele 2 vulnerabilități **relevante pentru produs** (urllib3, idna) sunt tranzitive prin `requests` și
  efectiv livrate în `.exe` — rezolvate prin actualizare + prag de securitate fixat în `pyproject.toml`
  (ca să nu regreseze la un build viitor). Reconstruit `.exe` ca să livreze versiunile fixe.
- urllib3 PYSEC-2026-141 (header-leak la redirect) e relevant fiindcă aplicația face fetch pe URL-uri
  (descoperire/import-url); aplicația folosește API-ul de nivel înalt `requests`, dar fixul închide riscul.
- `pip` = risc de supply-chain pe stația de dev (la instalarea de pachete), nu în produsul livrat.
- După actualizare: **517 teste + 92 e2e verzi** (idna/urllib3 minore, fără breaking).

## Recomandare
Rulează `python -m pip_audit` periodic (ex. înainte de fiecare build de lansare). Pin-urile din
`pyproject.toml` (Pillow, urllib3, idna) țin pragul de securitate.
