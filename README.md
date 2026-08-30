# condition-gates

<p align="center"><strong>English</strong> · <a href="README_de.md">Deutsch</a></p>

Conditions as **gates**: a sub-step stays blocked until its condition is **proven** met by a
tool query. Gates survive the end of a session and an abort.

Family: `.ORCHESTRATION` · Type: `library` (CLI + Python API) · Consumer: Skill `condition`

Canonical source: private repository `https://github.com/ellmos-ai/condition-gates`.
This does not authorize a public release.

## Purpose

Conditions written in prose get lost. "Only use swarm-ai from 6 a.m." sits on line 40 of an
assignment, the agent reads it at 3 a.m., starts working and remembers nothing of it at 6 a.m.
This module turns that into a named object with a lifecycle — and enforces a proof when it is
closed.

## Storage: detect it, otherwise create it

Two backends behind one interface, selected automatically:

| Backend | when | where |
|---|---|---|
| **USMC** | if the `usmc` CLI is present **and reachable** | shared working memory under the vendor-neutral default actor `condition-gates` |
| **SQLite** | otherwise — fallback without any foreign dependency | `~/.condition-gates/gates.db`, file and table are created on demand |

The fallback is silent on purpose: a missing USMC is not an error but a host without that
service. If USMC is installed but broken, that is reported on stderr and evaded anyway — a
broken store must not halt the work. Every output states which backend won; `doctor` shows it
explicitly.

Anything can be forced:

```
CONDITION_GATES_BACKEND = auto | usmc | sqlite
CONDITION_GATES_DB      = <path>       (sqlite only)
CONDITION_GATES_AGENT   = <agent-id>   (USMC only; default: condition-gates)
```

## Append-only

A status change appends a **new** record instead of altering the old one; per gate ID the most
recent one applies. With USMC this is enforced (individual working entries cannot be deleted),
with the SQLite backend it is deliberately kept the same — that way both behave identically and
the history including its evidence stays readable.

## CLI

```bash
python -m condition_gates doctor                     # backend detection + inventory
python -m condition_gates list [--all] [--json]      # default: open ones only
python -m condition_gates open "<condition>" --blocks "<what is blocked>" --proof "<proof path>"
python -m condition_gates meet <id> --evidence "<proof text from the tool query>"
python -m condition_gates drop <id> --reason "<why it is moot>"
```

Exit codes: `0` ok · `1` domain error (e.g. missing evidence) · `2` gate not found.

## Python

```python
from condition_gates import GateBook
book = GateBook()                      # backend automatic
g = book.open("system time >= 06:00", blocks="report-job", proof="time-probe")
[x for x in book.list() if x.is_open]
book.meet(g["gate_id"], "time-probe: 06:16 Europe/Berlin")
```

## Evidence requirement

`meet()` without evidence fails — that is intentional and the actual value of the module. A gate
that counts as met without being checked is worse than no gate at all: it creates trust in an
order that was never kept. What qualifies as proof is decided by the caller (time via
`fc_get_time`, files via `fc_list_directory`, repository state via `git` …); the module only
enforces that one is named at all. Which time, file or version control tool delivers the proof
is decided by the respective agent or host.

## Delimitation from the lock system

`lock-master` already knows a **condition lock** (`lock_create.py --condition
--release-condition "…"`). That is something different, and the separation is intentional:

| | `lock-master --condition` | `condition-gates` |
|---|---|---|
| Whom does it hold up? | **other** agents and systems | **myself** — my own sub-step |
| Subject | a directory / work area | a sub-goal within an assignment |
| Condition | free text, read by humans | translated into checkable form, with a named proof path |
| Resolution | lock file is removed | `meet` with evidence from a tool query |

They complement each other: if a gate should additionally keep **others** away, `lock-master` is
called for that — it is not rebuilt here.

## Limits

- The module does **not check conditions itself**. It manages them. The checking and the behaviour
  on open gates (reordering, resolving blockers, putting them to sleep) is described by the skill `condition`.
- **Concurrency is not this module's business.** Two processes writing at the same time could
  advance the same gate twice. A dedicated locking mechanism, however, explicitly does **not** belong
  in an encapsulated module: on this system one has long been present and running with `lock-master`
  (`control.locks`) — if parallel operation becomes relevant, it is called directly
  (`lock_create.py <dir> --scope gates`), not rebuilt here. That is why `control.locks` is in the
  manifest under `optional`: a capability this module uses when it is there, and does not bring
  along itself.

  A stack composition is not needed for that on this system — both building blocks are installed.
  One would only make sense once somebody wants to rebuild the assembly **from the outside**, without
  existing memory and without a locker.
