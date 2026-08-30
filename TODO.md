# TODO — condition-gates

## Erledigt

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
