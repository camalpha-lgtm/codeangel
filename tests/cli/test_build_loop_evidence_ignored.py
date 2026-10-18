from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from support import transition
from support.evidence import EvidenceProject


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=True
    )
    return result.stdout


class TestEvidenceIgnored:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        git(project, "init", "-q")
        return EvidenceProject(project)

    def test_prepare_creates_an_ignoring_dir(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-cli.txt", "$ run\nok\n")
        evidence.artefact("ac-1-ui.png", b"\x89PNG\r\n\x1a\n")
        before = git(evidence.root, "status", "--porcelain")

        git(evidence.root, "add", "-A")

        staged = git(evidence.root, "diff", "--cached", "--name-only")
        assert "evidence" not in before
        assert "evidence" not in staged
        assert (evidence.home() / ".gitignore").read_text(encoding="utf-8").strip() == "*"

    def test_evidence_command_prints_the_dir(self, project: Path):
        result = transition(project, "evidence", "ABC-1")

        assert result.returncode == 0, result.stdout
        assert result.stdout.strip().endswith("docs/specs/evidence/ABC-1")
        assert (project / "docs/specs/evidence/ABC-1/.gitignore").is_file()

    def test_unignored_dir_is_refused(self, evidence: EvidenceProject):
        proof = evidence.artefact("ac-1-api.txt", "GET /orders\n200\n")
        (evidence.home() / ".gitignore").unlink()
        spec = evidence.spec(["- [x] AC-1: a [proof: api]"], [f"| AC-1 | api | {proof} | x |"])

        problems = evidence.problems(spec)

        assert len(problems) == 1
        assert "not git-ignored" in problems[0]
        assert "T evidence ABC-1" in problems[0]

    def test_tracked_artefact_is_refused(self, evidence: EvidenceProject):
        proof = evidence.artefact("ac-1-api.txt", "GET /orders\n200\n")
        git(evidence.root, "add", "-f", proof)
        spec = evidence.spec(["- [x] AC-1: a [proof: api]"], [f"| AC-1 | api | {proof} | x |"])

        problems = evidence.problems(spec)

        assert len(problems) == 1
        assert proof in problems[0]
        assert "git rm --cached" in problems[0]
