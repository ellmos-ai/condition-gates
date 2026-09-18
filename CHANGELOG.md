# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-09-18

### Added
- **GitHub Actions CI Matrix**: Added `.github/workflows/ci.yml` supporting multi-OS (`ubuntu-latest`, `windows-latest`) across Python versions 3.10, 3.11, 3.12, and 3.13 with compileall, ruff linting, and pytest validation.
- **Workflow Lifecycle Automation**: Added `.github/workflows/stale.yml` (daily stale management) and `.github/workflows/welcome.yml` (contributor welcome) with least-privilege token permissions, explicit timeouts, and concurrency controls.
- **Security Policy (`SECURITY.md`)**: Documented supported version lifecycle (0.1.x), private vulnerability reporting procedure, 48-hour initial response SLA, 5-day triage commitment, and zero-network-egress invariants.
- **Software Bill of Materials (`THIRD_PARTY_LICENSES.md`)**: Certified zero external runtime dependencies (`dependencies = []`), PSF-2.0 and MIT licensing, `RunAsInvoker` unprivileged execution model, and mapping to `INV-GATE-01`..`08` and `INV-LOCAL-01`..`10`.
- **Extended Contract Testing**: Added automated contract tests in `tests/test_metadata.py` verifying CI workflows, gitignore safety patterns, PEP 621 Python 3.13 classifier declaration, standalone CLI launcher execution, and security/SBOM compliance.

### Changed
- **PEP 621 Standardisation**: Updated `pyproject.toml` with `Programming Language :: Python :: 3.13` classifier, `license-files` declaration, extended project URLs (`Documentation`, `Security`, `Third-Party Licenses`, `LLM Ready`), and pytest `minversion = "7.0"` with `norecursedirs`.
- **Gitignore Hardening**: Enhanced `.gitignore` with multi-host cloud-sync collision patterns (`*conflicted copy*`, `* (Kopie)*`, `* (Copy)*`, `*-ASUS*`, `*-LAPTOP*`, `*-WORKSTATION*`, etc.), lock system guards, and build artifact exclusions.
- **Synchronized Badges**: Updated test status badges in English and German README files.

## [0.1.1] - 2026-09-10

### Added
- **Bilingual Discoverability & README Architecture**: Full 1:1 parity between `README.md` (English) and `README_de.md` (German) with reciprocal language switchers.
- **Shields.io Badges**: Added badges for Python version (3.10+), MIT license, test pass rate, Ruff style, USMC/SQLite architecture, append-only storage, zero-network-egress security, fail-closed proof policy, llms.txt context, ellmos-ai ecosystem, open-bricks umbrella, and private repository status.
- **Interactive Mermaid Visuals**:
  - `flowchart TD` System Architecture visualizing runtime backend detection, dual-store paths, and fail-closed validation.
  - `sequenceDiagram` with `autonumber` and strictly quoted edge/action labels (in compliance with `HOOK-BANNER-ASSET-01`) illustrating the full gate lifecycle from `open` to `query_state` and `meet`.
- **Quick Navigation**: Standardized anchor links in both language editions.
- **Governance & Runtime Invariants**: Formalized 8 core system invariants (`INV-GATE-01` to `INV-GATE-08`).
- **Ecosystem Matrix**: Documented interconnections with sister repositories (`lock-master`, `hook-master`, `usmc`, `memoryhooker`, `system-gap-master`, `source-resolver`, `open-bricks`).
- **AI Context Integration**: Added root `llms.txt` for machine-assisted navigation.
- **Marketing & Discoverability Log**: Established `MARKETING-LOG.txt` covering target personas, SEO keywords, and future public-readiness recommendations.
- **Contract Test Suite**: Implemented `tests/test_metadata.py` to enforce metadata completeness, bilingual parity, invariant presence, and Mermaid diagram quoting.
- **Manifest**: Created `MANIFEST.in` ensuring all documentation, schemas, and context files are packaged.

### Changed
- Enhanced `pyproject.toml` with PEP 621 project URLs (Homepage, Repository, Issues, Changelog, Organization, Umbrella, Marketing Log) and optional development dependencies.

## [0.1.1] - 2026-09-05

### Fixed
- Fixed CLI output backend reporting consistency across plain text and JSON outputs (TASKPLAN 203).
- Cleaned unused imports and synchronized runtime version metadata (TASKPLAN 201).

## [0.1.0] - 2026-07-25

### Added
- Initial implementation of `condition-gates`.
- Dual storage backend abstraction (USMC memory actor with automatic fallback to standalone SQLite `~/.condition-gates/gates.db`).
- Gate lifecycle management enforcing empirical proof on `meet()`.
- CLI commands (`doctor`, `list`, `open`, `meet`, `drop`) with JSON support and deterministic exit codes.
- Direct module execution wrapper `gates.py`.
- ELLMOS module manifest `ellmos-module.v2.json`.
