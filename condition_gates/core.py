# -*- coding: utf-8 -*-
"""Gate-Lebenszyklus: setzen, prüfen, schließen, verwerfen.

Die Regeln stehen hier und nicht in der CLI, damit ein Aufrufer (MCP-Adapter, anderer
Agent, Test) dieselbe Semantik bekommt wie die Kommandozeile.

Die wichtigste Regel ist die Evidenzpflicht beim Schließen: Ein Gate, das ungeprüft als
erfüllt gilt, ist schlimmer als gar keins — es erzeugt Vertrauen in eine Reihenfolge, die
nie eingehalten wurde. Deshalb ist `evidence` beim Schließen erzwungen, nicht empfohlen.
"""
from __future__ import annotations

from datetime import datetime

from .store import DROPPED, MET, OPEN, Gate, open_store


class GateError(RuntimeError):
    """Fachlicher Fehler (unbekanntes Gate, fehlende Evidenz) — kein Programmfehler."""


class GateBook:
    def __init__(self, store=None, **kw):
        self.store = store or open_store(**kw)

    # ---------------------------------------------------------------- lesen
    def all(self) -> dict:
        return self.store.load()

    def list(self, include_closed: bool = False) -> list:
        gates = [g for g in self.all().values() if include_closed or g.is_open]
        gates.sort(key=lambda g: (not g.is_open, g.get("created_at", "")))
        return gates

    def get(self, gate_id: str) -> Gate:
        gate = self.all().get(gate_id)
        if gate is None:
            known = ", ".join(sorted(self.all())) or "(keine)"
            raise GateError("Gate '{}' nicht gefunden. Vorhanden: {}".format(gate_id, known))
        return gate

    def next_id(self) -> str:
        existing = self.all()
        n = 1
        while "g{}".format(n) in existing:
            n += 1
        return "g{}".format(n)

    # -------------------------------------------------------------- schreiben
    def open(self, condition: str, blocks: str = "", proof: str = "", gate_id: str = "") -> Gate:
        condition = (condition or "").strip()
        if not condition:
            raise GateError("Ein Gate ohne Bedingung ist keins.")
        gid = (gate_id or "").strip() or self.next_id()
        if gid in self.all():
            raise GateError("Gate '{}' existiert bereits.".format(gid))
        gate = Gate(gate_id=gid, status=OPEN, condition=condition,
                    blocks=(blocks or "").strip(), proof=(proof or "").strip(),
                    evidence="", reason="",
                    created_at=datetime.now().isoformat(timespec="seconds"))
        self.store.append(gate)
        return gate

    def meet(self, gate_id: str, evidence: str) -> Gate:
        evidence = (evidence or "").strip()
        if not evidence:
            raise GateError("Ein Gate ohne Evidenz zu schließen ist genau der Fehler, den dieses "
                            "Modul verhindern soll. Belege die Bedingung mit einer Werkzeugabfrage.")
        gate = self.get(gate_id)
        if gate["status"] == MET:
            raise GateError("Gate '{}' ist bereits erfüllt.".format(gate_id))
        closed = Gate(gate)
        closed.update(status=MET, evidence=evidence,
                      created_at=datetime.now().isoformat(timespec="seconds"))
        self.store.append(closed)
        return closed

    def drop(self, gate_id: str, reason: str = "") -> Gate:
        gate = self.get(gate_id)
        dropped = Gate(gate)
        dropped.update(status=DROPPED, reason=(reason or "").strip() or "(kein Grund angegeben)",
                       created_at=datetime.now().isoformat(timespec="seconds"))
        self.store.append(dropped)
        return dropped
