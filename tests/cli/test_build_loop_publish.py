from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from support import transition
from support.evidence import EvidenceProject

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
MP4 = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 32


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8", check=True
    )
    return result.stdout.strip()


def make_repo(project: Path) -> Path:
    origin = project.parent / "origin.git"
    git(project.parent, "init", "-q", "--bare", str(origin))
    git(project, "init", "-q")
    git(project, "config", "user.email", "t@example.com")
    git(project, "config", "user.name", "t")
    git(project, "remote", "add", "origin", str(origin))
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "init")
    return origin


class TestPublish:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        self.origin = make_repo(project)
        return EvidenceProject(project)

    def test_media_lands_on_the_evidence_branch(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-ui.png", PNG)
        evidence.artefact("ac-1-ui.mp4", MP4)
        evidence.artefact("ac-1-ui.txt", "heading: Orders\n")

        sha = evidence.module.publish_evidence("ABC-1")

        assert sha == git(self.origin, "rev-parse", "evidence/ABC-1")
        listed = git(self.origin, "ls-tree", "-r", "--name-only", sha).splitlines()
        assert listed == ["ABC-1/ac-1-ui.mp4", "ABC-1/ac-1-ui.png"]

    def test_checkout_is_left_untouched(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-ui.png", PNG)
        before = (
            git(evidence.root, "rev-parse", "HEAD"),
            git(evidence.root, "status", "--porcelain"),
            git(evidence.root, "ls-files", "--stage"),
            git(evidence.root, "branch", "--show-current"),
        )

        evidence.module.publish_evidence("ABC-1")

        after = (
            git(evidence.root, "rev-parse", "HEAD"),
            git(evidence.root, "status", "--porcelain"),
            git(evidence.root, "ls-files", "--stage"),
            git(evidence.root, "branch", "--show-current"),
        )
        assert after == before

    def test_second_publish_fast_forwards(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-ui.png", PNG)
        first = evidence.module.publish_evidence("ABC-1")
        evidence.artefact("ac-2-ui.png", PNG + b"\x01")

        second = evidence.module.publish_evidence("ABC-1")

        assert second != first
        assert git(self.origin, "rev-parse", f"{second}^") == first
        assert git(self.origin, "rev-parse", "evidence/ABC-1") == second

    def test_pr_branch_tree_has_no_media(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-ui.png", PNG)
        evidence.artefact("ac-1-ui.mp4", MP4)

        evidence.module.publish_evidence("ABC-1")

        tracked = git(evidence.root, "ls-tree", "-r", "--name-only", "HEAD").splitlines()
        assert not [path for path in tracked if "evidence" in path]
        assert "evidence/ABC-1" not in git(evidence.root, "branch", "--list")

    def test_publish_command_prints_the_sha(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-ui.png", PNG)

        result = transition(evidence.root, "publish", "ABC-1")

        assert result.returncode == 0, result.stdout
        assert result.stdout.strip() == git(self.origin, "rev-parse", "evidence/ABC-1")
        assert len(result.stdout.strip()) == 40


class TestPublishLimits:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        self.origin = make_repo(project)
        return EvidenceProject(project)

    def test_no_media_is_a_noop(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-cli.txt", "ok\n")

        result = transition(evidence.root, "publish", "ABC-1")

        assert result.returncode == 0, result.stdout
        assert result.stdout.strip() == ""
        assert git(self.origin, "branch", "--list") == ""

    def test_oversized_media_is_refused(self, evidence: EvidenceProject):
        evidence.artefact("ac-1-ui.mp4", MP4)
        evidence.module.MEDIA_MAX_BYTES = 8

        with pytest.raises(evidence.module.Refused) as error:
            evidence.module.publish_evidence("ABC-1")

        assert "ac-1-ui.mp4" in str(error.value)
        assert git(self.origin, "branch", "--list") == ""
