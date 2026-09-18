# -*- coding: utf-8 -*-
"""condition-gates — Bedingungen als nachprüfbare, sessionübergreifende Gates.

Nutzt ein vorhandenes Gedächtnis (USMC), wenn eines da ist, und speichert sonst selbst
in einer eigenen SQLite-Datei. Siehe store.open_store().
"""
from .core import GateBook, GateError
from .store import DROPPED, MET, OPEN, Gate, SqliteStore, UsmcStore, open_store

__version__ = "0.1.2"
__all__ = ["GateBook", "GateError", "Gate", "open_store", "UsmcStore", "SqliteStore",
           "OPEN", "MET", "DROPPED", "__version__"]
