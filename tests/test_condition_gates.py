# -*- coding: utf-8 -*-
"""Unit-Tests für das condition-gates Modul."""

import json
import tempfile
from pathlib import Path
import pytest

from condition_gates.core import GateBook, GateError
from condition_gates.store import (
    DEFAULT_USMC_AGENT,
    DROPPED,
    MET,
    OPEN,
    SqliteStore,
    UsmcStore,
    open_store,
)
from condition_gates.cli import main, build_parser


@pytest.fixture
def temp_db():
    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = tf.name
    tf.close()
    yield db_path
    try:
        Path(db_path).unlink(missing_ok=True)
    except PermissionError:
        pass


def test_sqlite_store_append_and_load(temp_db):
    store = SqliteStore(db_path=temp_db)
    book = GateBook(store=store)

    gate1 = book.open("Test condition 1", blocks="feature_a", proof="fc_get_time", gate_id="g1")
    assert gate1["gate_id"] == "g1"
    assert gate1["status"] == OPEN
    assert gate1["condition"] == "Test condition 1"

    all_gates = book.all()
    assert "g1" in all_gates
    assert all_gates["g1"].is_open is True


def test_sqlite_store_append_only_history(temp_db):
    store = SqliteStore(db_path=temp_db)
    book = GateBook(store=store)

    book.open("Test condition", blocks="task1", gate_id="g1")
    assert book.get("g1")["status"] == OPEN

    book.meet("g1", evidence="Check completed successfully")
    assert book.get("g1")["status"] == MET
    assert book.get("g1")["evidence"] == "Check completed successfully"

    # Ensure latest event wins
    open_gates = book.list(include_closed=False)
    assert len(open_gates) == 0

    all_gates = book.list(include_closed=True)
    assert len(all_gates) == 1
    assert all_gates[0]["status"] == MET


def test_gatebook_validation_and_errors(temp_db):
    store = SqliteStore(db_path=temp_db)
    book = GateBook(store=store)

    # Empty condition
    with pytest.raises(GateError, match="ohne Bedingung"):
        book.open("   ")

    # Duplicate gate ID
    book.open("Condition 1", gate_id="g1")
    with pytest.raises(GateError, match="existiert bereits"):
        book.open("Condition 2", gate_id="g1")

    # Non-existent gate
    with pytest.raises(GateError, match="nicht gefunden"):
        book.get("g999")

    # Meet without evidence
    with pytest.raises(GateError, match="ohne Evidenz"):
        book.meet("g1", evidence="  ")

    # Meet already met gate
    book.meet("g1", evidence="Evidence provided")
    with pytest.raises(GateError, match="bereits erfüllt"):
        book.meet("g1", evidence="New evidence")


def test_gatebook_drop(temp_db):
    store = SqliteStore(db_path=temp_db)
    book = GateBook(store=store)

    book.open("Condition drop", gate_id="g1")
    book.drop("g1", reason="No longer needed")

    gate = book.get("g1")
    assert gate["status"] == DROPPED
    assert gate["reason"] == "No longer needed"


def test_usmc_store_parse():
    entry = {
        "id": 42,
        "content": "GATE g5 | status=OFFEN | bedingung=Test bedingung | blockiert=swarm | beleg=fc_get_time",
        "created_at": "2026-07-26T12:00:00"
    }
    gate = UsmcStore._parse(entry)
    assert gate is not None
    assert gate["gate_id"] == "g5"
    assert gate["status"] == OPEN
    assert gate["condition"] == "Test bedingung"
    assert gate["blocks"] == "swarm"
    assert gate["proof"] == "fc_get_time"


def test_usmc_store_default_is_provider_neutral(monkeypatch):
    monkeypatch.delenv("CONDITION_GATES_AGENT", raising=False)
    assert UsmcStore().agent == DEFAULT_USMC_AGENT == "condition-gates"


def test_cli_commands(temp_db, capsys):
    # Doctor command
    ret = main(["--backend", "sqlite", "--db", temp_db, "doctor"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "sqlite-Fallback" in captured.out
    assert "immer verfügbar" in captured.out

    # Open gate
    ret = main(["--backend", "sqlite", "--db", temp_db, "open", "Bedingung 1", "--blocks", "task_x", "--proof", "tool_y", "--id", "g10"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Gate g10 gesetzt" in captured.out

    # List gates
    ret = main(["--backend", "sqlite", "--db", temp_db, "list"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "g10" in captured.out
    assert "offen" in captured.out

    # List JSON
    ret = main(["--backend", "sqlite", "--db", temp_db, "list", "--json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data) == 1
    assert data[0]["gate_id"] == "g10"

    # Meet gate
    ret = main(["--backend", "sqlite", "--db", temp_db, "meet", "g10", "--evidence", "Confirmed by tool_y"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Gate g10 ERFÜLLT" in captured.out

    # Drop gate (create g11 first)
    main(["--backend", "sqlite", "--db", temp_db, "open", "Bedingung 2", "--id", "g11"])
    ret = main(["--backend", "sqlite", "--db", temp_db, "drop", "g11", "--reason", "Test reason"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "Gate g11 VERWORFEN" in captured.out


def test_cli_exit_codes(temp_db):
    # Unknown gate meet -> exit code 2
    ret = main(["--backend", "sqlite", "--db", temp_db, "meet", "g999", "--evidence", "some evidence"])
    assert ret == 2

    # Validation error (meet without evidence) -> exit code 1
    main(["--backend", "sqlite", "--db", temp_db, "open", "Bedingung 3", "--id", "g12"])
    ret = main(["--backend", "sqlite", "--db", temp_db, "meet", "g12"])
    assert ret == 1
