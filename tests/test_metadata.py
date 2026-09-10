# -*- coding: utf-8 -*-
"""Vertragstests für Repository-Metadaten, Bilinguale READMEs, Invarianten und Diagramme."""

import json
import re
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
    assert project.get("version") == condition_gates.__version__
    assert project.get("license", {}).get("text") == "MIT"
    assert project.get("requires-python") == ">=3.10"

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Repository" in urls
    assert "Issues" in urls
    assert "Changelog" in urls
    assert "Organization" in urls
    assert "Umbrella" in urls
    assert "Marketing Log" in urls

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

    mktg_file = REPO_ROOT / "MARKETING-LOG.txt"
    assert mktg_file.is_file(), "MARKETING-LOG.txt muss im Repository-Root existieren"
    mktg_text = mktg_file.read_text(encoding="utf-8")
    assert "Personas" in mktg_text
    assert "Keywords" in mktg_text


def test_private_repository_guard_intact():
    private_file = REPO_ROOT / "PRIVATE.txt"
    assert private_file.is_file(), "PRIVATE.txt muss existieren"
    content = private_file.read_text(encoding="utf-8")
    assert "GATE: closed" in content
    assert "SCOPE: private-repository" in content
