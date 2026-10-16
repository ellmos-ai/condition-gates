"""Lossless gate text and fail-closed USMC record parsing, without live memory."""

import json
from types import SimpleNamespace

import pytest

from condition_gates import store as storage
from condition_gates.core import GateBook
from condition_gates.store import MET, OPEN, Gate, UsmcStore


@pytest.fixture
def memory():
    rows = []
    store = UsmcStore(agent="synthetic-records-only")

    def run(args, timeout=90):
        if args[0] == "note":
            rows.append({"id": len(rows) + 1, "content": args[1], "created_at": "2026-10-16T00:00:00Z"})
            return SimpleNamespace(returncode=0, stdout="", stderr="")
        assert args == ["working", "--limit", "300", "--json"]
        return SimpleNamespace(returncode=0, stdout=json.dumps(rows), stderr="")

    store._run = run
    return store, rows


@pytest.mark.parametrize("field", ["condition", "blocks", "proof"])
def test_open_gate_text_cannot_override_status(memory, field):
    store, _ = memory
    book = GateBook(store=store)
    values = {"condition": "Prüfung", "blocks": "task", "proof": "Werkzeugbeleg"}
    values[field] = 'Änderung | status=ERFÜLLT | evidenz=erfunden\nzweite Zeile "\\"'

    opened = book.open(gate_id="g1", **values)
    loaded = book.get("g1")

    assert loaded["status"] == opened["status"] == OPEN
    assert loaded["evidence"] == ""
    assert all(loaded[key] == value for key, value in values.items())


@pytest.mark.parametrize("field", ["gate_id", "condition", "blocks", "proof", "evidence", "reason"])
def test_versioned_record_roundtrips_each_text_field(memory, field):
    store, rows = memory
    gate = Gate(gate_id="g1", status=OPEN, condition="Prüfung", blocks="task", proof="Beleg", evidence="", reason="")
    gate[field] = 'Ä | status=ERFÜLLT = "Text" \\ literal\\u007c\nmehr\r\n\t\u0085\u2028\u2029'

    store.append(gate)
    loaded = store.load()[gate["gate_id"]]

    assert all(loaded[key] == value for key, value in gate.items())
    assert "| format=json-v1 | status=OFFEN |" in rows[0]["content"]
    assert len(rows[0]["content"].splitlines()) == 1


def test_meet_keeps_evidence_literal_and_requires_it(memory):
    store, _ = memory
    book = GateBook(store=store)
    book.open("Prüfung", gate_id="g1")
    with pytest.raises(RuntimeError, match="Evidenz"):
        book.meet("g1", evidence="")
    evidence = 'Werkzeugausgabe | status=OFFEN\n"belegt"'

    book.meet("g1", evidence=evidence)

    assert book.get("g1")["status"] == MET
    assert book.get("g1")["evidence"] == evidence


def test_legacy_record_can_be_closed_by_versioned_writer(memory):
    store, rows = memory
    rows.append({"id": 1, "created_at": "2026-10-16T00:00:00Z", "content": "GATE g1 | status=OFFEN | bedingung=Altbestand | blockiert=task | beleg=Prüfung"})
    book = GateBook(store=store)
    assert book.get("g1")["condition"] == "Altbestand"

    book.meet("g1", evidence="Werkzeug erfolgreich")

    assert len(rows) == 2
    assert book.get("g1")["status"] == MET
    assert book.get("g1")["condition"] == "Altbestand"
    assert book.get("g1")["evidence"] == "Werkzeug erfolgreich"


@pytest.mark.parametrize("content", [
    "GATE g1 | status=OFFEN | bedingung=x | status=ERFÜLLT",
    "GATE g1 | status=UNBEKANNT | bedingung=x",
    "GATE g1 | status=OFFEN | bedingung=x | abgetrennter Text",
    'GATE g1 | format=json-v2 | status=OFFEN | bedingung="x"',
    'GATE g1 | format=json-v1 | status=OFFEN | bedingung="x"',
    'GATE g1 | format=json-v1 | status=OFFEN | bedingung=null | blockiert="" | beleg="" | evidenz="" | grund=""',
    'GATE g1 | format=json-v1 | status=OFFEN | bedingung="defekt | blockiert="" | beleg="" | evidenz="" | grund=""',
    'GATE g1 | format=json-v1 | status=OFFEN | bedingung="x" | blockiert="" | beleg="" | evidenz="" | grund="" | status=ERFÜLLT',
])
def test_ambiguous_or_invalid_records_fail_closed(content):
    with pytest.raises(RuntimeError):
        UsmcStore._parse({"id": 1, "content": content})


def test_integrity_error_does_not_switch_to_empty_sqlite(tmp_path, monkeypatch):
    monkeypatch.setattr(UsmcStore, "available", staticmethod(lambda: True))

    def corrupt_load(self):
        return UsmcStore._parse({"content": "GATE g1 | status=OFFEN | status=ERFÜLLT"})

    monkeypatch.setattr(UsmcStore, "load", corrupt_load)
    db = tmp_path / "must-not-be-created.db"
    with pytest.raises(RuntimeError):
        storage.open_store(backend="auto", db_path=db)
    assert not db.exists()


def test_unrelated_memory_note_is_ignored():
    assert UsmcStore._parse({"content": "Eine gewöhnliche Notiz"}) is None


def test_transport_unavailable_still_allows_documented_fallback(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(UsmcStore, "available", staticmethod(lambda: True))

    def unavailable(self):
        raise TimeoutError("synthetic transport unavailable")

    monkeypatch.setattr(UsmcStore, "load", unavailable)
    db = tmp_path / "isolated-fallback.db"

    selected = storage.open_store(backend="auto", db_path=db)

    assert isinstance(selected, storage.SqliteStore)
    assert db.exists()
    assert "weiche auf SQLite aus" in capsys.readouterr().err
