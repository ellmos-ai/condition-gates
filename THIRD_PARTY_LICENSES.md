# Third-Party Licenses & Software Inventory

- **Project:** `condition-gates`
- **License:** [MIT License](LICENSE)
- **Audit Date:** 2026-09-18
- **Repository:** [ellmos-ai/condition-gates](https://github.com/ellmos-ai/condition-gates)
- **Umbrella Collective:** [open-bricks](https://github.com/open-bricks)

---

## Runtime Architecture & Dependencies

`condition-gates` is engineered as a **zero-dependency, local-first gating library and CLI for autonomous AI agents and orchestration pipelines**. It enforces empirical proof paths before sub-steps can proceed, persisting gates across session lifecycles without any cloud dependencies.

### Mandatory Runtime Dependencies

`condition-gates` maintains a **zero external runtime dependency footprint** (`dependencies = []`). The entire runtime execution relies strictly on the official Python Standard Library:

| Package / Module | Version Spec | License | Type | Purpose |
|---|---|---|---|---|
| *Python Standard Library* | `>=3.10` | PSF-2.0 | Built-in | Core runtime: `argparse`, `dataclasses`, `datetime`, `json`, `os`, `pathlib`, `re`, `shutil`, `sqlite3`, `subprocess`, `sys`, `typing` |

All state persistence is handled entirely via Python's built-in `sqlite3` driver (or USMC when present). Zero third-party telemetry, tracking, or external network egress calls are made.

### Development & Test Tooling

The following tools are utilized exclusively for offline automated testing, code quality auditing, packaging, and linting:

| Package / Tool | Version Spec | License | Scope | Purpose |
|---|---|---|---|---|
| [pytest](https://pytest.org/) | `>=7.0` | MIT | `[dev]` | Automated unit, contract, and metadata test runner |
| [ruff](https://github.com/astral-sh/ruff) | `>=0.1.0` | MIT OR Apache-2.0 | `[dev]` | High-performance Python code style and lint enforcement |
| [setuptools](https://github.com/pypa/setuptools) | `>=68.0` | MIT | `[build-system]` | Standard packaging and build backend |
| [wheel](https://github.com/pypa/wheel) | `>=0.40` | MIT | `[build-system]` | Standard built-package distribution format |

---

## Zero-Copyleft Guarantee & Unprivileged Execution

- **Zero-Copyleft Guarantee:** All runtime code and development dependencies are governed strictly by permissive, business-friendly open-source licenses (MIT, Apache-2.0, PSF-2.0). The codebase contains **zero** GPL, AGPL, or viral copyleft components.
- **Unprivileged User-Mode Operation (`RunAsInvoker`):** All CLI commands, SQLite transactions, and state queries execute purely within unprivileged user space. No administrative rights, root elevation, sudo, or UAC prompts are ever required.

---

## Governance & Runtime Invariants

`condition-gates` strictly enforces domain-specific gating invariants and foundational system invariants:

### Gating Invariants (INV-GATE-01 .. INV-GATE-08)

| Invariant | Scope | Guarantee |
|---|---|---|
| `INV-GATE-01` | **Session-Independent Persistence** | Gates survive session boundaries, process termination, and pipeline aborts via USMC memory or standalone SQLite. |
| `INV-GATE-02` | **Fail-Closed Evidence Requirement** | `meet()` strictly requires empirical proof text; empty or whitespace proof is rejected fail-closed. |
| `INV-GATE-03` | **Append-Only Audit Stream** | State changes are recorded as append-only event records, preserving complete historical lineage. |
| `INV-GATE-04` | **Provider-Neutral Standard Actor** | Default actor ID is `condition-gates` rather than vendor-specific names, supporting configurable agent IDs. |
| `INV-GATE-05` | **Structured JSON Metadata Separation** | CLI `--json` output cleanly separates backend diagnostics (`meta`) from domain payload (`gate`, `gates`). |
| `INV-GATE-06` | **Zero Network Egress** | All persistence and querying remain 100% local; no external HTTP, telemetry, or cloud calls. |
| `INV-GATE-07` | **Unprivileged User Execution (`RunAsInvoker`)** | All operations operate within normal user privileges without elevated access. |
| `INV-GATE-08` | **Direct Launcher Portability** | Root `gates.py` enables immediate execution from arbitrary directories without prior pip installation. |

### System & Governance Invariants (INV-LOCAL-01 .. INV-SLA-10)

| Invariant | Category | Description |
|---|---|---|
| `INV-LOCAL-01` | Local-First & Zero-Egress | 100% offline-ready operations persisting to local storage; zero telemetry or external network calls. |
| `INV-UNPRIV-02` | Unprivileged User Mode (`RunAsInvoker`) | All CLI commands, API calls, and background routines operate strictly in unprivileged user space. |
| `INV-SQLITE-03` | ACID Storage Resiliency | Resilient multi-session concurrency via SQLite transactions or USMC shared state. |
| `INV-SCHEMA-04` | Backward-Compatible Evolution | Idempotent schema design ensuring seamless backward compatibility across versions. |
| `INV-BOUND-05` | Deterministic Memory Limits | Predictable event footprints preventing unbounded memory or storage growth. |
| `INV-FILTER-06` | Fail-Closed Validation | Input sanitation rejecting blank conditions, empty evidence, and invalid state transitions. |
| `INV-LANG-07` | Bilingual Documentation Parity | Complete 1:1 parity between English and German documentation, with stable English CLI tokens. |
| `INV-ISOL-08` | Strict State Isolation | Local state databases reside strictly in user-home app directories, isolated from git repos. |
| `INV-AUDIT-09` | Complete SPDX Audit Transparency | 100% Python standard library at runtime; zero mandatory external runtime dependencies and zero copyleft risks. |
| `INV-SLA-10` | Cross-Platform Parity & SLA | Consistent behavior across Windows, Linux, and macOS with committed 48h response / 5-day triage security SLA. |

---

## License Texts & Attribution

### MIT License (`condition-gates`, `pytest`, `setuptools`, `wheel`)

```
MIT License

Copyright (c) 2026 Lukas Geiger / ellmos-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Python Software Foundation License Version 2 (`Python Standard Library`)

```
1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and
the Individual or Organization ("Licensee") accessing and otherwise using this
software ("Python") in source or binary form and its associated documentation.

2. Subject to the terms and conditions of this License Agreement, PSF hereby
grants Licensee a nonexclusive, royalty-free, world-wide license to reproduce,
analyze, test, perform and/or display publicly, prepare derivative works, distribute,
and otherwise use Python alone or in any derivative version, provided, however, that
PSF's License Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001-2026
Python Software Foundation; All Rights Reserved" are included in Python alone or in
any derivative version prepared by Licensee.
```

### Apache License Version 2.0 (`ruff`)

```
Copyright (c) Astral Software Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
