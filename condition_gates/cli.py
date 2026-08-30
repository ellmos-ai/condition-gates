# -*- coding: utf-8 -*-
"""Kommandozeile des Moduls condition-gates.

    python -m condition_gates list [--all] [--json]
    python -m condition_gates open "<bedingung>" --blocks "<...>" --proof "<...>" [--id gX]
    python -m condition_gates meet <gate-id> --evidence "<Belegtext>"
    python -m condition_gates drop <gate-id> --reason "<...>"
    python -m condition_gates doctor

Exit-Codes: 0 ok · 1 fachlicher Fehler (z. B. fehlende Evidenz) · 2 Gate nicht gefunden.
Jede Ausgabe nennt das aktive Backend — es darf nie unklar sein, wo die Gates liegen.
"""
from __future__ import annotations

import argparse
import json
import sys

from .core import GateBook, GateError
from .store import OPEN, SqliteStore, UsmcStore, open_store


def _book(a) -> GateBook:
    return GateBook(store=open_store(backend=getattr(a, "backend", None),
                                     db_path=getattr(a, "db", None)))


def cmd_list(a) -> int:
    book = _book(a)
    gates = book.list(include_closed=a.all)
    if a.json:
        print(json.dumps([dict(g) for g in gates], ensure_ascii=False, indent=2))
        return 0
    print("Speicher: {}".format(book.store.describe()))
    if not gates:
        print("Keine {}Gates.".format("" if a.all else "offenen "))
        return 0
    for g in gates:
        print(g)
        for label, key in (("blockiert", "blocks"), ("beleg via", "proof"),
                           ("evidenz", "evidence"), ("grund", "reason")):
            if g.get(key):
                print("     {:<10} {}".format(label + ":", g[key]))
    offen = sum(1 for g in gates if g["status"] == OPEN)
    print("\n{} Gate(s), davon {} offen.".format(len(gates), offen))
    return 0


def cmd_open(a) -> int:
    book = _book(a)
    g = book.open(a.condition, blocks=a.blocks, proof=a.proof, gate_id=a.id)
    print("Speicher: {}".format(book.store.describe()))
    print("Gate {} gesetzt: {}".format(g["gate_id"], g["condition"]))
    print("  blockiert: {}".format(g["blocks"] or "(nicht angegeben)"))
    if g["proof"]:
        print("  beleg via: {}".format(g["proof"]))
    else:
        print("  beleg via: OFFEN - ohne Belegweg kann dieses Gate nie geschlossen werden.")
    return 0


def cmd_meet(a) -> int:
    book = _book(a)
    g = book.meet(a.gate_id, a.evidence)
    print("Gate {} ERFÜLLT.".format(g["gate_id"]))
    print("  war:     {}".format(g["condition"]))
    print("  evidenz: {}".format(g["evidence"]))
    if g["blocks"]:
        print("  => jetzt freigegeben: {}".format(g["blocks"]))
    return 0


def cmd_drop(a) -> int:
    book = _book(a)
    g = book.drop(a.gate_id, a.reason)
    print("Gate {} VERWORFEN: {}".format(g["gate_id"], g["reason"]))
    return 0


def cmd_doctor(a) -> int:
    print("usmc-CLI auffindbar : {}".format("ja" if UsmcStore.available() else "nein"))
    print("sqlite-Fallback     : immer verfügbar (stdlib)")
    store = open_store(backend=getattr(a, "backend", None), db_path=getattr(a, "db", None))
    print("aktives Backend     : {}".format(store.describe()))
    gates = GateBook(store=store).all()
    print("Gates gesamt        : {} (davon offen: {})".format(
        len(gates), sum(1 for g in gates.values() if g.is_open)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="condition_gates",
                                description="Gates: Bedingungen, die Teilschritte sperren, bis sie belegt erfüllt sind.")
    p.add_argument("--backend", choices=["auto", "usmc", "sqlite"], default=None,
                   help="Speicher erzwingen (Default: auto - USMC wenn vorhanden, sonst SQLite)")
    p.add_argument("--db", default=None, help="Pfad zur SQLite-Datei (nur Backend sqlite)")
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="Gates anzeigen (Default: nur offene)")
    pl.add_argument("--all", action="store_true", help="auch erfüllte/verworfene")
    pl.add_argument("--json", action="store_true", help="maschinenlesbar")
    pl.set_defaults(func=cmd_list)

    po = sub.add_parser("open", help="neues Gate setzen")
    po.add_argument("condition")
    po.add_argument("--blocks", "-b", default="", help="was dadurch blockiert ist")
    po.add_argument("--proof", "-p", default="", help="womit die Bedingung belegt wird")
    po.add_argument("--id", default="", help="eigene Gate-ID (sonst g1, g2, ...)")
    po.set_defaults(func=cmd_open)

    pm = sub.add_parser("meet", help="Gate als erfüllt schließen (Evidenz Pflicht)")
    pm.add_argument("gate_id")
    pm.add_argument("--evidence", "-e", default="", help="Belegtext aus der Werkzeugabfrage")
    pm.set_defaults(func=cmd_meet)

    pd = sub.add_parser("drop", help="Gate verwerfen (hinfällig geworden)")
    pd.add_argument("gate_id")
    pd.add_argument("--reason", "-r", default="")
    pd.set_defaults(func=cmd_drop)

    pdoc = sub.add_parser("doctor", help="Backend-Erkennung und Bestand prüfen")
    pdoc.set_defaults(func=cmd_doctor)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return a.func(a)
    except GateError as e:
        sys.stderr.write("{}\n".format(e))
        return 2 if "nicht gefunden" in str(e) else 1
    except RuntimeError as e:
        sys.stderr.write("Fehler: {}\n".format(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
