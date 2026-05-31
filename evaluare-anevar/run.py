"""Punct de intrare pentru executabilul impachetat (PyInstaller).

Porneste serverul local si deschide browserul. Echivalent cu `python -m evaluare`,
dar ca script de sine statator pe care PyInstaller il poate impacheta.
"""
from __future__ import annotations

from evaluare.__main__ import main

if __name__ == "__main__":
    main()
