# TODO — condition-gates

## Aktueller Prüfstand

Stand 2026-09-18 · Version 0.1.2 · 24 Tests bestanden · Multi-OS CI-Matrix, Ruff und `compileall` sauber.

## Erledigt

- [x] **2026-09-18 (Pfad A — CI-Matrix, PEP 621 Standardisation, SBOM & Governance):**
  - Multi-OS GitHub Actions CI-Matrix (`.github/workflows/ci.yml`) für Ubuntu und Windows über Python 3.10, 3.11, 3.12 und 3.13 mit Concurrency-Guards, Least-Privilege-Rechten (`contents: read`) und 15-Minuten-Timeout.
  - Lifecycle-Workflows `.github/workflows/stale.yml` und `.github/workflows/welcome.yml` hinzugefügt.
  - Sicherheitsrichtlinie `SECURITY.md` mit 48h Response SLA, 5-Tage-Triage und Architektur-Invarianten angelegt.
  - Software Bill of Materials & Lizenzinventar `THIRD_PARTY_LICENSES.md` mit 0-Abhängigkeiten-Zertifizierung und System-Invarianten-Mapping (`INV-GATE-01..08`, `INV-LOCAL-01..10`) erstellt.
  - `pyproject.toml` auf PEP 621 mit Python 3.13 Classifier, license-files, erweiterten URLs und Pytest-Härtung aktualisiert.
  - `.gitignore` gegen Multi-Host-Cloud-Sync-Konflikte, Lock-Dateien und Cache-Artefakte gehärtet.
  - Vertragstest-Suite in `tests/test_metadata.py` erweitert (Gesamtsuite von 17 auf 24 Tests gewachsen, 100% grün).
  - Version einheitlich auf 0.1.2 gehoben (`__init__.py`, `pyproject.toml`, `ellmos-module.v2.json`, `llms.txt`, `CHANGELOG.md`).
- [x] **2026-08-14 (P-006 Sprachzug — Stufe 1 Core erreicht, DE+EN):**
  - Primärfassungswechsel: das bisherige deutsche `README.md` liegt jetzt als `README_de.md`
    (umbenannt, nicht kopiert), `README.md` ist die englische 1:1-Übersetzung.
  - Parität gemessen: 9/9 Überschriften, 10/10 Tabellenzeilen, 3/3 Codeblöcke, 2/2 Bullets;
    alle 20 Inline-Code-Spans sowie Flags, Unterbefehle und `CONDITION_GATES_*`-Variablen
    byte-identisch. Übersetzt wurden nur Prosa und Platzhaltertexte (`<bedingung>` → `<condition>`).
  - Language-Switcher gespiegelt in beiden Fassungen.
  - Verweise geprüft: `pyproject.toml` (`readme = "README.md"`) bleibt maschinenlesbar auf der
    englischen Fassung; `ellmos-module.v2.json` hat kein `docs`/`readme`-Feld; Skill `condition`,
    `modules.catalog.json`, `.MODULES/ARCHITECTURE.md` und `.MODULES/README.md` nennen das Modul,
    verweisen aber nicht auf die README — kein Verweis war umzubiegen.
- [x] **2026-07-26 (v0.1.1 Maintenance & Health Check):**
  - Standardisiertes `pyproject.toml` (PEP 621) angelegt.
  - Vollständige Pytest-Suite `tests/test_condition_gates.py` erstellt (7/7 passed).
  - SQLite-Verbindungsverwaltung in `store.py` für saubere Handles gehärtet.
  - Deutsche User-Facing CLI-Texte & Fehlermeldungen auf UTF-8 Umlaute vereinheitlicht.
  - Anbieterneutraler USMC-Standard-Akteur `condition-gates` statt `claude-code`;
    explizite Anbieter-/Agenten-IDs bleiben über `CONDITION_GATES_AGENT` möglich.
- [x] **2026-07-25 (v0.1.0 Init):**
  - Storage-Abstraktion: USMC erkennen und nutzen, sonst eigene SQLite anlegen (`store.py`)
  - Gate-Lebenszyklus mit erzwungener Evidenz beim Schließen (`core.py`)
  - CLI inkl. `doctor` (zeigt erkanntes Backend), Exit-Codes 0/1/2
  - Starter mit absolutem Pfad (`gates.py`) — aufrufbar ohne Installation
  - Manifest + Katalogeintrag (`build_catalog.py` grün, über `module_resolver` auflösbar)
  - Skill `condition` auf das Modul umgestellt (Skill = Wrapper, keine Runtime mehr)

## Später (keine Priorität)

- [ ] **Stack-Komposition für Dritte** [U 2026-07-25]: Ein `ellmos.stack.v2`-Manifest, das
      `condition-gates` mit einem Speicher- und einem Lock-Baustein bündelt, wäre nur relevant,
      wenn das Modul **auf GitHub für andere** bereitgestellt wird — also für Leute, die den
      Verbund ohne vorhandenes Gedächtnis und ohne Locker nachbauen. **Auf diesem System nicht
      nötig:** USMC und `lock-master` sind installiert und laufen; der Stack würde nur
      zusammenstecken, was ohnehin da ist. Ein erster Anlauf wurde am 2026-07-25 bewusst wieder
      zurückgenommen (inkl. der dafür angelegten Rollen `gating.default`/`locks.default` in
      `composition.rules.json`) — die Registry wird nicht für einen ungenutzten Stack erweitert.
      Bei einer Veröffentlichung wieder aufgreifen.
- [ ] Nebenläufigkeitsschutz: erst wenn echter Parallelbetrieb auftritt, dann über `lock-master`
      (`control.locks`), nicht als Eigenbau im Modul.
- [ ] Optionaler MCP-Adapter (`surfaces: mcp-adapter`), falls Gates auch fremden Agenten ohne
      CLI-Zugriff offenstehen sollen.

## TASKWRITER-Review 2026-09-05

Presentation `af350720-ef8e-4c2c-807f-01b098abb078`; gelesen wurden README.md,
README_de.md, TODO.md, pyproject.toml, PRIVATE.txt, LICENSE,
ellmos-module.v2.json, gates.py, alle fünf Paketmodule und die Testsuite.
`main` war sauber und exakt auf `origin/main` (`2c48a7f`). Das Repository ist
laut `PRIVATE.txt` und Live-Remote privat; Public Release, Package-Publish,
Commit und Push waren nicht Teil dieses Reviews.

`pytest -q` meldete 8 passed, `compileall` lief ohne Fehler. `ruff check .`
schlug mit drei F401-Befunden fehl. Ein CLI-Smoke mit SQLite zeigte außerdem,
dass `list --json` kein Backend ausweist und `drop` ein bereits erfülltes Gate
noch akzeptiert. `condition_gates.__version__` ist 0.1.0, während Paket und
Manifest 0.1.1 ausweisen.

### Neue, formalisierte Aufgaben

- [x] **TASKPLAN 201 — Lint-Baseline repariert und Versionsmetadaten angeglichen**
      (high, easy, local). Drei ungenutzte Imports entfernen/klären, den
      Runtime-Versionswert synchronisieren und die veraltete 7/7-Statuszahl
      erst nach neuer Messung aktualisieren.
- [ ] **TASKPLAN 202 — Gate-Zustandsübergänge terminal und Zeitstempel
      zonenbewusst machen** (high, medium, local). Nur offene Gates dürfen
      einmal geschlossen oder verworfen werden; neue Zeitstempel müssen
      UTC-ISO-8601 mit Offset tragen.
- [x] **TASKPLAN 203 — Backend-Nachweis in allen CLI-Ausgaben und JSON stabil
      gemacht** (medium, easy, local). Plain- und JSON-Ausgaben nennen das
      Backend jetzt durchgängig; die READMEs dokumentieren den getrennten
      `meta`-Bereich und gültige Shell-Assignments.
- [ ] **TASKPLAN 204 — USMC-Transportargumente und Gate-Inhalte verlustfrei
      absichern** (high, medium, local). Shell-/argv-Verhalten und die
      pipe-separierte Freitextkodierung brauchen Mock-/Round-trip-Belege, ohne
      SQLite-Fallback oder PRIVATE-Gate zu ändern.

### Offene Entscheidungen

- Für TASKPLAN 202 ist eine Reopen-Funktion ausdrücklich nicht vorgesehen und
  würde eine separate Nutzerentscheidung erfordern.
- TASKPLAN 204 braucht die tatsächlich unterstützte USMC-CLI-Signatur; ohne
  erreichbares USMC bleibt die Prüfung auf Mock- und SQLite-Evidenz begrenzt.

### Review-Log

- Keine Aufgabe ausgeführt; keine Veröffentlichung, Registrierung, Löschung,
  Commit- oder Push-Aktion autorisiert.
- Taskplan-Register synchronisiert: IDs 201–204; alle mit Ergebnis, Quelle,
  Herleitung, Abnahme, Verifikation, Abhängigkeiten/Blocker, Aufwand, Scope und
  Prioritätsbegründung.

### TASKSOLVER-Abschluss 2026-09-05

- TASKPLAN 201 und 203 lokal umgesetzt; PRIVATE.txt blieb unverändert.
- Verifiziert: 10 Tests, Ruff, `compileall`, Versionsgleichstand 0.1.1,
  Plain-/JSON-Smokes mit SQLite sowie DE/EN-Parität und UTF-8.
- Kein Release, Package-Publish oder Push.
