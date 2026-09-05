# condition-gates

<p align="center"><a href="README.md">English</a> · <strong>Deutsch</strong></p>

Bedingungen als **Gates**: Ein Teilschritt bleibt gesperrt, bis seine Bedingung durch eine
Werkzeugabfrage **belegt** erfüllt ist. Gates überleben Session-Ende und Abbruch.

Familie: `.ORCHESTRATION` · Art: `library` (CLI + Python-API) · Konsument: Skill `condition`

Kanonische Quelle: privates Repository `https://github.com/ellmos-ai/condition-gates`.
Dies ist keine Freigabe für eine öffentliche Veröffentlichung.

## Wozu

Bedingungen in Fließtext gehen verloren. „Setz swarm-ai erst ab 6 Uhr ein" steht in Zeile 40 eines
Auftrags, der Agent liest es um 3 Uhr, arbeitet los und erinnert sich um 6 Uhr an nichts mehr.
Dieses Modul macht daraus ein benanntes Objekt mit Lebenszyklus — und erzwingt beim Schließen
einen Beleg.

## Speicher: erkennen, sonst selbst anlegen

Zwei Backends hinter einer Schnittstelle, Auswahl automatisch:

| Backend | wann | wo |
|---|---|---|
| **USMC** | wenn die `usmc`-CLI vorhanden **und erreichbar** ist | gemeinsames Working-Memory unter dem anbieterneutralen Standard-Akteur `condition-gates` |
| **SQLite** | sonst — Fallback ohne jede Fremdabhängigkeit | `~/.condition-gates/gates.db`, Datei und Tabelle werden bei Bedarf selbst angelegt |

Der Fallback ist absichtlich still: Ein fehlendes USMC ist kein Fehler, sondern ein Host ohne
diesen Dienst. Ist USMC zwar installiert, aber defekt, wird das auf stderr gemeldet und trotzdem
ausgewichen — ein kaputter Speicher darf die Arbeit nicht anhalten. Welches Backend gewonnen hat,
sagt jede Ausgabe; `doctor` zeigt es explizit.

Erzwingen lässt sich alles:

```
CONDITION_GATES_BACKEND=sqlite
CONDITION_GATES_DB=<path>       # sqlite only
CONDITION_GATES_AGENT=<agent-id>   # USMC only; default: condition-gates
```

## Append-only

Ein Statuswechsel hängt einen **neuen** Datensatz an, statt den alten zu ändern; pro Gate-ID gilt
der jüngste. Bei USMC ist das erzwungen (einzelne Working-Einträge lassen sich nicht löschen),
beim SQLite-Backend bewusst gleich gehalten — so verhalten sich beide identisch und die Historie
samt Evidenz bleibt lesbar.

## CLI

```bash
python -m condition_gates doctor [--json]            # backend detection + inventory
python -m condition_gates list [--all] [--json]      # default: open ones only
python -m condition_gates open "<condition>" --blocks "<what is blocked>" --proof "<proof path>" [--json]
python -m condition_gates meet <id> --evidence "<proof text from the tool query>" [--json]
python -m condition_gates drop <id> --reason "<why it is moot>" [--json]
```

Exit-Codes: `0` ok · `1` fachlicher Fehler (z. B. fehlende Evidenz) · `2` Gate nicht gefunden.

## Maschinenlesbare Ausgabe

Jeder Befehl akzeptiert `--json`. Die Backend-Metadaten stehen immer getrennt an derselben
Stelle; Befehlsdaten liegen unter `gates`, `gate`, `diagnostics` oder `error`:

```json
{
  "meta": {
    "backend": "sqlite",
    "backend_description": "SQLite (<path>)"
  },
  "gates": []
}
```

Erfolgreiches JSON wird nach stdout geschrieben; JSON-Fehler gehen nach stderr und behalten
die dokumentierten Exit-Codes bei.

## Python

```python
from condition_gates import GateBook
book = GateBook()                      # Backend automatisch
g = book.open("Systemzeit >= 06:00", blocks="report-job", proof="time-probe")
[x for x in book.list() if x.is_open]
book.meet(g["gate_id"], "time-probe: 06:16 Europe/Berlin")
```

## Evidenzpflicht

`meet()` ohne Evidenz schlägt fehl — das ist Absicht und der eigentliche Wert des Moduls. Ein Gate,
das ungeprüft als erfüllt gilt, ist schlimmer als gar keins: Es erzeugt Vertrauen in eine
Reihenfolge, die nie eingehalten wurde. Was als Beleg taugt, entscheidet der Aufrufer (Zeit via
`fc_get_time`, Dateien via `fc_list_directory`, Repo-Zustand via `git` …); das Modul erzwingt nur,
dass überhaupt einer genannt wird. Welches Zeit-, Datei- oder Versionskontrollwerkzeug den
Beleg liefert, entscheidet der jeweilige Agent oder Host.

## Abgrenzung zum Lock-System

`lock-master` kennt bereits einen **Condition-Lock** (`lock_create.py --condition
--release-condition "…"`). Das ist etwas anderes, und die Trennung ist beabsichtigt:

| | `lock-master --condition` | `condition-gates` |
|---|---|---|
| Wen hält es auf? | **andere** Agenten und Systeme | **mich selbst** — meinen eigenen Teilschritt |
| Gegenstand | ein Verzeichnis / Arbeitsbereich | ein Teilziel innerhalb eines Auftrags |
| Bedingung | Freitext, von Menschen gelesen | in prüfbare Form übersetzt, mit benanntem Belegweg |
| Auflösung | Lock-Datei wird entfernt | `meet` mit Evidenz aus einer Werkzeugabfrage |

Sie ergänzen sich: Soll ein Gate zusätzlich **andere** fernhalten, wird dafür `lock-master`
aufgerufen — nicht hier nachgebaut.

## Grenzen

- Das Modul **prüft Bedingungen nicht selbst**. Es verwaltet sie. Das Prüfen und das Verhalten bei
  offenen Gates (umsortieren, Blocker auflösen, schlafen legen) beschreibt der Skill `condition`.
- **Nebenläufigkeit ist nicht Sache dieses Moduls.** Zwei gleichzeitig schreibende Prozesse könnten
  dasselbe Gate doppelt fortschreiben. Ein eigener Sperrmechanismus gehört aber ausdrücklich **nicht**
  in ein gekapseltes Modul: Auf diesem System ist mit `lock-master` (`control.locks`) längst einer
  vorhanden und läuft — wird Parallelbetrieb relevant, wird er direkt aufgerufen
  (`lock_create.py <dir> --scope gates`), nicht hier nachgebaut. Deshalb steht `control.locks` im
  Manifest unter `optional`: eine Fähigkeit, die dieses Modul benutzt, wenn sie da ist, und nicht
  selbst mitbringt.

  Eine Stack-Komposition braucht es dafür auf diesem System nicht — beide Bausteine sind installiert.
  Sinnvoll wäre eine erst, wenn jemand den Verbund **von außen** nachbauen will, ohne vorhandenes
  Gedächtnis und ohne Locker.
