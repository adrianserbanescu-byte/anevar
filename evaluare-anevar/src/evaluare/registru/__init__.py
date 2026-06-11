"""Registrul de evidenta a rapoartelor de evaluare (Procedura de arhivare ANEVAR §6).

Pastrat INTENTIONAT gol: `dosare_fs` importa `registru.numar`, iar `registru.registru`
importa `dosare_fs`. Un `__init__` care ar importa `registru.registru` ar inchide bucla
(numar nu ar fi inca legat) — asa ca importurile se fac explicit pe submodule.
"""
