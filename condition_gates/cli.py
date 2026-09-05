# -*- coding: utf-8 -*-
"""Kommandozeile des Moduls condition-gates.

    python -m condition_gates list [--all] [--json]
    python -m condition_gates open "<bedingung>" --blocks "<...>" --proof "<...>" [--id gX] [--json]
    python -m condition_gates meet <gate-id> --evidence "<Belegtext>" [--json]
    python -m condition_gates drop <gate-id> --reason "<...>" [--json]
    python -m condition_gates doctor [--json]

Exit-Codes: 0 ok · 1 fachlicher Fehler (z. B. fehlende Evidenz) · 2 Gate nicht gefunden.
Jede Ausgabe nennt das aktive Backend — es darf nie unklar sein, wo die Gates liegen.
"""
from __future__ import annotations

import argparse
import json
import sys

from .core import GateBook, GateError
from .store import OPEN, UsmcStore, open_store


def _book(a) -> GateBook:
    book = getattr(a, "_book", None)
    if book is None:
        book = GateBook(store=open_store(backend=getattr(a, "backend", None),
                                         db_path=getattr(a, "db", None)))
        a._book = book
    return book


def _backend_meta(store) -> dict:
    return {"backend": store.name, "backend_description": store.describe()}


def _json_document(store, **payload) -> str:
    return json.dumps({"meta": _backend_meta(store), **payload}, ensure_ascii=False, indent=2)


def _backend_line(store) -> str:
    return "Backend: {} — {}".format(store.name, store.describe())


def cmd_list(a) -> int:
    book = _book(a)
    gates = book.list(include_closed=a.all)
    if a.json:
        print(_json_document(book.store, gates=[dict(g) for g in gates]))
        return 0
    print(_backend_line(book.store))
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
    if a.json:
        print(_json_document(book.store, gate=dict(g)))
        return 0
    print(_backend_line(book.store))
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
    if a.json:
        print(_json_document(book.store, gate=dict(g)))
        return 0
    print(_backend_line(book.store))
    print("Gate {} ERFÜLLT.".format(g["gate_id"]))
    print("  war:     {}".format(g["condition"]))
    print("  evidenz: {}".format(g["evidence"]))
    if g["blocks"]:
        print("  => jetzt freigegeben: {}".format(g["blocks"]))
    return 0


def cmd_drop(a) -> int:
    book = _book(a)
    g = book.drop(a.gate_id, a.reason)
    if a.json:
        print(_json_document(book.store, gate=dict(g)))
        return 0
    print(_backend_line(book.store))
    print("Gate {} VERWORFEN: {}".format(g["gate_id"], g["reason"]))
    return 0


def cmd_doctor(a) -> int:
    usmc_available = UsmcStore.available()
    book = _book(a)
    gates = book.all()
    diagnostics = {
        "usmc_available": usmc_available,
        "sqlite_available": True,
        "gate_count": len(gates),
        "open_count": sum(1 for g in gates.values() if g.is_open),
    }
    if a.json:
        print(_json_document(book.store, diagnostics=diagnostics))
        return 0
    print(_backend_line(book.store))
    print("usmc-CLI auffindbar : {}".format("ja" if usmc_available else "nein"))
    print("sqlite-Fallback     : immer verfügbar (stdlib)")
    print("Gates gesamt        : {} (davon offen: {})".format(
        diagnostics["gate_count"], diagnostics["open_count"]))
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
    po.add_argument("--json", action="store_true", help="maschinenlesbar")
    po.set_defaults(func=cmd_open)

    pm = sub.add_parser("meet", help="Gate als erfüllt schließen (Evidenz Pflicht)")
    pm.add_argument("gate_id")
    pm.add_argument("--evidence", "-e", default="", help="Belegtext aus der Werkzeugabfrage")
    pm.add_argument("--json", action="store_true", help="maschinenlesbar")
    pm.set_defaults(func=cmd_meet)

    pd = sub.add_parser("drop", help="Gate verwerfen (hinfällig geworden)")
    pd.add_argument("gate_id")
    pd.add_argument("--reason", "-r", default="")
    pd.add_argument("--json", action="store_true", help="maschinenlesbar")
    pd.set_defaults(func=cmd_drop)

    pdoc = sub.add_parser("doctor", help="Backend-Erkennung und Bestand prüfen")
    pdoc.add_argument("--json", action="store_true", help="maschinenlesbar")
    pdoc.set_defaults(func=cmd_doctor)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    try:
        return a.func(a)
    except GateError as e:
        book = getattr(a, "_book", None)
        if book is not None and getattr(a, "json", False):
            sys.stderr.write(_json_document(book.store, error={"message": str(e)}) + "\n")
        else:
            if book is not None:
                sys.stderr.write(_backend_line(book.store) + "\n")
            sys.stderr.write("{}\n".format(e))
        return 2 if "nicht gefunden" in str(e) else 1
    except RuntimeError as e:
        sys.stderr.write("Fehler: {}\n".format(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
