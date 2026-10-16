"""Exercise native USMC argument transport with a synthetic child, never live memory."""

import json
import subprocess
import sys

import pytest

from condition_gates.store import DROPPED, MET, OPEN, Gate, UsmcStore


@pytest.fixture
def fake_usmc(tmp_path, monkeypatch):
    record = tmp_path / "received.json"
    marker = tmp_path / "shell-marker.txt"
    child = tmp_path / "fake usmc.py"
    entry = {
        "id": 7,
        "content": "GATE g1 | status=OFFEN | bedingung=Prüfung | beleg=Nachweis",
        "created_at": "2026-10-16T00:00:00Z",
    }
    child.write_text(
        "import json, pathlib, sys\n"
        f"pathlib.Path({str(record)!r}).write_text(json.dumps(sys.argv[1:]), encoding='utf-8')\n"
        f"print(json.dumps({[entry]!r}) if 'working' in sys.argv else '{{}}')\n",
        encoding="utf-8",
    )
    real_run = subprocess.run
    calls = []

    def launch(command, **kwargs):
        # Replace only the executable with an argv-recording Python child. Preserve
        # production shell/encoding/timeout/creationflags behavior at the OS boundary.
        assert command[0] == "usmc"
        calls.append((command, kwargs.copy()))
        return real_run(
            [sys.executable, str(child), *command[1:]],
            cwd=tmp_path,
            input="",
            **kwargs,
        )

    monkeypatch.setattr("condition_gates.store.subprocess.run", launch)
    return record, marker, calls


@pytest.mark.parametrize("agent", ["test-agent", "Ärger mit Leerzeichen", "test&echo.PROBE>shell-marker.txt"])
def test_native_usmc_keeps_agent_and_arguments_literal(fake_usmc, agent):
    record, marker, calls = fake_usmc
    args = ["working", "--limit", "300", "--json"]

    result = UsmcStore(agent=agent)._run(args, timeout=7)

    assert result.returncode == 0, result.stderr
    assert json.loads(record.read_text(encoding="utf-8")) == ["--agent", agent, *args]
    assert not marker.exists()
    assert calls[0][1]["shell"] is False
    assert calls[0][1]["timeout"] == 7
    assert calls[0][1]["encoding"] == "utf-8"


def test_native_usmc_load_reaches_working_command(fake_usmc):
    record, marker, _ = fake_usmc

    gates = UsmcStore(agent="synthetic-agent").load()

    assert gates["g1"]["condition"] == "Prüfung"
    assert gates["g1"]["status"] == OPEN
    assert json.loads(record.read_text(encoding="utf-8")) == [
        "--agent", "synthetic-agent", "working", "--limit", "300", "--json"
    ]
    assert not marker.exists()


@pytest.mark.parametrize("status,priority,tag", [(OPEN, "7", "offen"), (MET, "5", "erfüllt"), (DROPPED, "3", "verworfen")])
def test_native_usmc_append_keeps_note_one_argument(fake_usmc, status, priority, tag):
    record, marker, _ = fake_usmc
    gate = Gate(
        gate_id="g1", status=status, condition='Prüfe "Datei" & <Ordner>',
        blocks="task", proof="Nachweis", evidence="a & b", reason="Grund",
    )

    UsmcStore(agent="synthetic-agent").append(gate)

    received = json.loads(record.read_text(encoding="utf-8"))
    assert received[:3] == ["--agent", "synthetic-agent", "note"]
    assert received[3] == (
        f'GATE g1 | format=json-v1 | status={status} | bedingung="Prüfe \\"Datei\\" & <Ordner>"'
        ' | blockiert="task" | beleg="Nachweis" | evidenz="a & b" | grund="Grund"'
    )
    assert received[4:] == ["--type", "loop", "--priority", priority, "--tags", f"gate,{tag},condition"]
    assert not marker.exists()
