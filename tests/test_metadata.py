# -*- coding: utf-8 -*-
"""Vertragstests für Repository-Metadaten, Bilinguale READMEs, Invarianten und Diagramme."""

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import condition_gates

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_metadata_completeness():
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.is_file(), "pyproject.toml muss existieren"

    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    project = data.get("project", {})

    assert project.get("name") == "condition-gates"
    lic = project.get("license")
    assert lic == "MIT" or (isinstance(lic, dict) and lic.get("text") == "MIT")
    assert project.get("requires-python") == ">=3.10"

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Documentation" in urls
    assert "Repository" in urls
    assert "Issues" in urls
    assert "Changelog" in urls
    assert "Security" in urls
    assert "Third-Party Licenses" in urls
    assert "Organization" in urls
    assert "Umbrella" in urls
    assert "Marketing Log" not in urls
    assert "LLM Ready" in urls

    assert "condition-gates" in project.get("scripts", {})


def test_version_parity():
    pkg_version = condition_gates.__version__

    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    assert data["project"]["version"] == pkg_version

    manifest_file = REPO_ROOT / "ellmos-module.v2.json"
    if manifest_file.is_file():
        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        assert manifest_data.get("version") == pkg_version


def test_readme_bilingual_files_and_badges():
    en_readme = REPO_ROOT / "README.md"
    de_readme = REPO_ROOT / "README_de.md"

    assert en_readme.is_file(), "README.md muss existieren"
    assert de_readme.is_file(), "README_de.md muss existieren"

    en_text = en_readme.read_text(encoding="utf-8")
    de_text = de_readme.read_text(encoding="utf-8")

    # Beide READMEs müssen wechselseitig verlinkt sein
    assert "README_de.md" in en_text
    assert "README.md" in de_text

    # Shields.io Badges
    assert "img.shields.io/badge/python" in en_text
    assert "img.shields.io/badge/license" in en_text
    assert "img.shields.io/badge/tests" in en_text
    assert "img.shields.io/badge/code%20style-ruff" in en_text

    assert "img.shields.io/badge/python" in de_text
    assert "img.shields.io/badge/license" in de_text
    assert "img.shields.io/badge/tests" in de_text
    assert "img.shields.io/badge/code%20style-ruff" in de_text


def test_mermaid_diagrams_present_and_strictly_quoted():
    """Prüft, ob Architektur- und Sequenzdiagramme vorhanden und HOOK-BANNER-ASSET-01 konform sind."""
    en_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_text = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for lang, text in [("EN", en_text), ("DE", de_text)]:
        assert "```mermaid" in text, f"{lang} README muss Mermaid-Blöcke enthalten"
        assert "flowchart TD" in text or "graph TD" in text, f"{lang} README muss Flowchart enthalten"
        assert "sequenceDiagram" in text, f"{lang} README muss sequenceDiagram enthalten"
        assert "autonumber" in text, f"{lang} sequenceDiagram muss autonumber nutzen"

        # Edge label quoting check: -->|label|
        edge_matches = re.findall(r"(?:--+>|<-+>|-\.-+>|==+>)\|([^|\r\n]+)\|", text)
        for label in edge_matches:
            stripped = label.strip()
            # Sonderzeichen wie ()[]{}<>: verlangen striktes Quoting in doppelten Anführungszeichen
            if any(c in stripped for c in "()[]{}<>&:"):
                assert stripped.startswith('"') and stripped.endswith('"'), (
                    f"In {lang} README ist Kantenbeschriftung {stripped!r} nicht in doppelte Anführungszeichen gesetzt!"
                )


def test_governance_invariants_documented():
    en_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    de_text = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    invariants = [
        "INV-GATE-01",
        "INV-GATE-02",
        "INV-GATE-03",
        "INV-GATE-04",
        "INV-GATE-05",
        "INV-GATE-06",
        "INV-GATE-07",
        "INV-GATE-08",
    ]

    for inv in invariants:
        assert inv in en_text, f"{inv} fehlt in README.md"
        assert inv in de_text, f"{inv} fehlt in README_de.md"


def test_context_and_marketing_artifacts():
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.is_file(), "llms.txt muss im Repository-Root existieren"
    llms_text = llms_file.read_text(encoding="utf-8")
    assert "condition-gates" in llms_text
    assert "GateBook" in llms_text

    # MARKETING-LOG.txt darf laut Policy niemals in Git getrackt sein
    proc = subprocess.run(
        ["git", "ls-files", "MARKETING-LOG.txt"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=False,
    )
    assert proc.stdout.strip() == "", "MARKETING-LOG.txt darf NICHT in Git getrackt sein!"


def test_private_repository_guard_intact():
    private_file = REPO_ROOT / "PRIVATE.txt"
    assert private_file.is_file(), "PRIVATE.txt muss existieren"
    content = private_file.read_text(encoding="utf-8")
    assert "GATE: closed" in content
    assert "SCOPE: private-repository" in content


def test_ci_workflow_presence_and_matrix():
    ci_file = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_file.is_file(), ".github/workflows/ci.yml muss existieren"
    content = ci_file.read_text(encoding="utf-8")

    assert "ubuntu-latest" in content
    assert "windows-latest" in content
    assert '"3.10"' in content
    assert '"3.11"' in content
    assert '"3.12"' in content
    assert '"3.13"' in content
    assert "actions/checkout@v4" in content
    assert "actions/setup-python@v5" in content
    assert "compileall" in content
    assert "ruff check" in content
    assert "pytest" in content


def test_stale_and_welcome_workflows():
    stale_file = REPO_ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_file.is_file(), ".github/workflows/stale.yml muss existieren"
    stale_content = stale_file.read_text(encoding="utf-8")
    assert "actions/stale@v9" in stale_content
    assert "cron:" in stale_content

    welcome_file = REPO_ROOT / ".github" / "workflows" / "welcome.yml"
    assert welcome_file.is_file(), ".github/workflows/welcome.yml muss existieren"
    welcome_content = welcome_file.read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in welcome_content


def test_gitignore_cloud_sync_and_lock_patterns():
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.is_file(), ".gitignore muss existieren"
    content = gitignore.read_text(encoding="utf-8")

    assert "*conflicted copy*" in content
    assert "*-ASUS*" in content
    assert "*-WORKSTATION*" in content
    assert "LOCK*.txt" in content
    assert "LOCK" in content
    assert "MARKETING-LOG.txt" in content


def test_pyproject_python_313_classifier_and_settings():
    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    classifiers = data.get("project", {}).get("classifiers", [])

    assert "Programming Language :: Python :: 3.13" in classifiers
    license_files = data.get("project", {}).get("license-files", [])
    assert "LICENSE" in license_files
    assert "THIRD_PARTY_LICENSES.md" in license_files

    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert pytest_opts.get("minversion") == "7.0"
    assert "norecursedirs" in pytest_opts


def test_security_policy_contract():
    sec_file = REPO_ROOT / "SECURITY.md"
    assert sec_file.is_file(), "SECURITY.md muss existieren"
    content = sec_file.read_text(encoding="utf-8")

    assert "Supported Versions" in content
    assert "0.1.x" in content
    assert "48 hours" in content
    assert "5 business days" in content
    assert "GitHub Security Advisories" in content


def test_third_party_licenses_contract():
    tpl_file = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert tpl_file.is_file(), "THIRD_PARTY_LICENSES.md muss existieren"
    content = tpl_file.read_text(encoding="utf-8")

    assert "dependencies = []" in content
    assert "Zero-Copyleft Guarantee" in content
    assert "RunAsInvoker" in content
    assert "INV-GATE-01" in content
    assert "INV-LOCAL-01" in content


def test_standalone_launcher_contract():
    launcher = REPO_ROOT / "gates.py"
    assert launcher.is_file(), "gates.py muss existieren"

    proc = subprocess.run(
        [sys.executable, str(launcher), "doctor", "--json"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, f"gates.py doctor fehlgeschlagen: {proc.stderr}"
    data = json.loads(proc.stdout)
    assert "meta" in data or "backend" in data or "status" in data
