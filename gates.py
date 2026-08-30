# -*- coding: utf-8 -*-
"""Startdatei mit absolutem Pfad — aufrufbar von überall, ohne Installation.

    python "<modulpfad>/gates.py" list

`python -m condition_gates` setzt voraus, dass das Paket im Suchpfad liegt (Installation
oder passendes Arbeitsverzeichnis). Ein Skill ruft aber aus beliebigen Verzeichnissen auf,
deshalb dieser Einstieg: Er legt sein eigenes Verzeichnis auf den Suchpfad und delegiert.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from condition_gates.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
