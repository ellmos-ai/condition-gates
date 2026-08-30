# -*- coding: utf-8 -*-
"""Speicher-Schicht für Gates: vorhandenes Gedächtnis nutzen, sonst selbst speichern.

Ein Gate ist wertlos, wenn es die Session nicht überlebt — „ab 06:00" muss um 04:00
gesetzt und um 06:15 noch auffindbar sein. Es darf aber auch nicht daran scheitern,
dass auf einem Host kein Gedächtnis-Dienst installiert ist. Deshalb zwei Backends
mit derselben Schnittstelle:

  * **UsmcStore** — nutzt die vorhandene USMC-Ablage (`usmc` CLI). Vorteil: Gates
    liegen dort, wo der übrige Prozess-State schon liegt, und andere Agenten sehen sie.
  * **SqliteStore** — Fallback ohne jede Fremdabhängigkeit (sqlite3 ist stdlib). Legt
    Datei und Tabelle bei Bedarf selbst an.

Die Auswahl passiert automatisch (`open_store()`), lässt sich aber erzwingen:
    CONDITION_GATES_BACKEND = auto | usmc | sqlite
    CONDITION_GATES_DB      = <pfad zur sqlite-datei>   (nur sqlite)
    CONDITION_GATES_AGENT   = <agent-id>                (nur usmc)

Beide Backends sind **append-only**: Ein Statuswechsel hängt einen neuen Datensatz an,
statt den alten zu ändern. Das ist bei USMC erzwungen (einzelne Working-Einträge lassen
sich nicht löschen) und beim SQLite-Backend bewusst gleich gehalten — so bleibt die
Historie samt Evidenz nachvollziehbar, und beide Backends verhalten sich identisch.
Pro Gate-ID gilt der jüngste Datensatz.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

OPEN, MET, DROPPED = "OFFEN", "ERFÜLLT", "VERWORFEN"
VALID_STATES = (OPEN, MET, DROPPED)
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
DEFAULT_USMC_AGENT = "condition-gates"


class Gate(dict):
    """Ein Gate als schlichtes Mapping — bewusst dict, damit es trivial serialisiert."""

    @property
    def is_open(self) -> bool:
        return self.get("status") == OPEN

    def __str__(self) -> str:
        mark = {OPEN: "[ ]", MET: "[x]", DROPPED: "[-]"}.get(self.get("status"), "[?]")
        return "{} {:<16} {}".format(mark, self.get("gate_id", "?"), self.get("condition", ""))


# --------------------------------------------------------------------------- USMC

class UsmcStore:
    """Gates im USMC-Working-Memory. Format bleibt menschenlesbar (eine Zeile)."""

    name = "usmc"

    def __init__(self, agent: str | None = None):
        self.agent = agent or os.environ.get("CONDITION_GATES_AGENT", DEFAULT_USMC_AGENT)

    @staticmethod
    def available() -> bool:
        return shutil.which("usmc") is not None

    def describe(self) -> str:
        return "USMC (agent={})".format(self.agent)

    def _run(self, args, timeout=90):
        return subprocess.run(["usmc", "--agent", self.agent] + args, capture_output=True,
                              text=True, encoding="utf-8", timeout=timeout,
                              shell=True, creationflags=NO_WINDOW)

    def append(self, gate: Gate) -> None:
        parts = ["GATE {}".format(gate["gate_id"]),
                 "status={}".format(gate["status"]),
                 "bedingung={}".format(gate.get("condition", "")),
                 "blockiert={}".format(gate.get("blocks", "")),
                 "beleg={}".format(gate.get("proof", ""))]
        if gate.get("evidence"):
            parts.append("evidenz={}".format(gate["evidence"]))
        if gate.get("reason"):
            parts.append("grund={}".format(gate["reason"]))
        prio = {OPEN: 7, MET: 5, DROPPED: 3}[gate["status"]]
        tag_state = {OPEN: "offen", MET: "erfüllt", DROPPED: "verworfen"}[gate["status"]]
        r = self._run(["note", " | ".join(parts), "--type", "loop", "--priority", str(prio),
                       "--tags", "gate,{},condition".format(tag_state)])
        if r.returncode != 0:
            raise RuntimeError("USMC-Schreiben fehlgeschlagen: {}".format((r.stderr or "").strip()[:300]))

    def load(self) -> dict:
        r = self._run(["working", "--limit", "300", "--json"])
        if r.returncode != 0:
            raise RuntimeError("USMC-Lesen fehlgeschlagen: {}".format((r.stderr or "").strip()[:300]))
        try:
            entries = json.loads(r.stdout or "[]")
        except ValueError as e:
            raise RuntimeError("USMC-Ausgabe nicht lesbar: {}".format(e))

        newest: dict[str, Gate] = {}
        for e in entries:
            g = self._parse(e)
            if not g:
                continue
            prev = newest.get(g["gate_id"])
            key = (g.get("created_at", ""), g.get("_row") or 0)
            if prev is None or key > (prev.get("created_at", ""), prev.get("_row") or 0):
                newest[g["gate_id"]] = g
        return newest

    @staticmethod
    def _parse(entry) -> Gate | None:
        content = entry.get("content") or ""
        m = re.match(r"GATE\s+(\S+)\s*\|", content)
        if not m:
            return None
        fields = {}
        for part in content.split("|")[1:]:
            if "=" in part:
                k, v = part.split("=", 1)
                fields[k.strip().lower()] = v.strip()
        return Gate(gate_id=m.group(1),
                    status=(fields.get("status") or OPEN).upper(),
                    condition=fields.get("bedingung", ""),
                    blocks=fields.get("blockiert", ""),
                    proof=fields.get("beleg", ""),
                    evidence=fields.get("evidenz", ""),
                    reason=fields.get("grund", ""),
                    created_at=entry.get("created_at", ""),
                    _row=entry.get("id"))


# ------------------------------------------------------------------------- SQLite

class SqliteStore:
    """Fallback ohne Fremdabhängigkeit. Legt Datei und Tabelle bei Bedarf selbst an."""

    name = "sqlite"

    def __init__(self, db_path: str | os.PathLike | None = None):
        raw = db_path or os.environ.get("CONDITION_GATES_DB")
        self.path = Path(raw).expanduser() if raw else Path.home() / ".condition-gates" / "gates.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    @staticmethod
    def available() -> bool:
        return True  # sqlite3 ist Teil der Standardbibliothek

    def describe(self) -> str:
        return "SQLite ({})".format(self.path)

    def _connect(self):
        con = sqlite3.connect(str(self.path), timeout=15)
        con.row_factory = sqlite3.Row
        return con

    def _ensure_schema(self) -> None:
        con = self._connect()
        try:
            con.execute("""
                CREATE TABLE IF NOT EXISTS gate_events (
                    row_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    gate_id    TEXT NOT NULL,
                    status     TEXT NOT NULL,
                    condition  TEXT NOT NULL DEFAULT '',
                    blocks     TEXT NOT NULL DEFAULT '',
                    proof      TEXT NOT NULL DEFAULT '',
                    evidence   TEXT NOT NULL DEFAULT '',
                    reason     TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )""")
            con.execute("CREATE INDEX IF NOT EXISTS idx_gate_events_gate ON gate_events(gate_id, row_id)")
            con.commit()
        finally:
            con.close()

    def append(self, gate: Gate) -> None:
        con = self._connect()
        try:
            con.execute(
                "INSERT INTO gate_events (gate_id,status,condition,blocks,proof,evidence,reason,created_at)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (gate["gate_id"], gate["status"], gate.get("condition", ""), gate.get("blocks", ""),
                 gate.get("proof", ""), gate.get("evidence", ""), gate.get("reason", ""),
                 gate.get("created_at") or datetime.now().isoformat(timespec="seconds")))
            con.commit()
        finally:
            con.close()

    def load(self) -> dict:
        con = self._connect()
        try:
            rows = con.execute(
                "SELECT * FROM gate_events WHERE row_id IN"
                " (SELECT MAX(row_id) FROM gate_events GROUP BY gate_id)").fetchall()
            return {r["gate_id"]: Gate(gate_id=r["gate_id"], status=r["status"], condition=r["condition"],
                                       blocks=r["blocks"], proof=r["proof"], evidence=r["evidence"],
                                       reason=r["reason"], created_at=r["created_at"], _row=r["row_id"])
                    for r in rows}
        finally:
            con.close()


# ------------------------------------------------------------------------ Auswahl

def open_store(backend: str | None = None, db_path=None, agent=None):
    """Wählt das Backend: erzwungen per Parameter/Env, sonst USMC wenn vorhanden.

    Der Fallback ist absichtlich still — ein fehlendes USMC ist kein Fehler, sondern
    ein Host ohne diesen Dienst. Welches Backend gewonnen hat, sagt `describe()`;
    die CLI zeigt es bei jedem Lauf an, damit nie unklar ist, wo Gates liegen.
    """
    choice = (backend or os.environ.get("CONDITION_GATES_BACKEND") or "auto").lower()
    if choice == "usmc":
        if not UsmcStore.available():
            raise RuntimeError("Backend 'usmc' erzwungen, aber die usmc-CLI ist nicht auffindbar.")
        return UsmcStore(agent=agent)
    if choice == "sqlite":
        return SqliteStore(db_path=db_path)
    if choice != "auto":
        raise RuntimeError("Unbekanntes Backend '{}'. Erlaubt: auto, usmc, sqlite.".format(choice))

    if UsmcStore.available():
        store = UsmcStore(agent=agent)
        try:
            store.load()          # Erreichbarkeit einmal echt prüfen, nicht nur die Datei
            return store
        except Exception as e:    # installiert, aber defekt/leer -> lieber sauber ausweichen
            sys.stderr.write("[condition-gates] USMC vorhanden, aber nicht nutzbar ({}); "
                             "weiche auf SQLite aus.\n".format(str(e)[:120]))
    return SqliteStore(db_path=db_path)
