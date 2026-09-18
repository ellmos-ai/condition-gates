# Security Policy

## Supported Versions

Currently, only the `main` branch and latest releases are supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities (e.g. proof bypass, state injection, unauthorized file I/O) privately via
**GitHub Security Advisories** ("Report a vulnerability" on the Security tab of this repository).

Do NOT create public issues for security vulnerabilities.

### Service Level Agreement (SLA)
- **Initial Response:** Within **48 hours** of report submission.
- **Triage & Status Update:** Within **5 business days**.
- **Fix Delivery & Disclosure:** Coordinated release and security advisory publication upon patch verification.

## Data Privacy & Architectural Invariants

- **Local-First & Zero External Network Egress:** `condition-gates` operates entirely offline. It persists state strictly via USMC (if present) or local SQLite (`~/.condition-gates/gates.db`). No telemetry, analytics, or external API calls are made.
- **Unprivileged User Mode (`RunAsInvoker`):** The tool requires no administrative, root, or elevated privileges. All operations execute strictly within the user security context.
- **Fail-Closed Proof Enforcement:** Gates cannot be satisfied (`meet()`) without verifiable evidence from a tool query. Empty or whitespace-only evidence strings are rejected with deterministic error codes.
