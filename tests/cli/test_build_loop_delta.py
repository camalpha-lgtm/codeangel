from __future__ import annotations

from pathlib import Path

import pytest
from support import transition
from support.repo import Repo, git, read


@pytest.fixture
def repo(project: Path) -> Repo:
    return Repo(project)


class TestDelta:
    def init_ticket(self, repo: Repo, tree: str = "") -> Path:
        result = transition(
            repo.root,
            "init",
            "ABC-1",
            "--mode",
            "immediate",
            "--title",
            "t",
            "--branch",
            "b",
            "--base-sha",
            repo.base,
        )
        assert result.returncode == 0, result.stdout
        path = repo.root / "docs/specs/ABC-1.md"
        if tree:
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "verified_tree:", f"verified_tree: {tree}"
                ),
                encoding="utf-8",
            )
        return path

    def test_delta_without_an_earlier_attempt_says_audit_everything(self, repo: Repo):
        self.init_ticket(repo)

        result = transition(repo.root, "delta", "ABC-1")

        assert result.returncode == 0, result.stdout
        assert "audit everything" in result.stdout

    def test_delta_lists_only_what_changed_since_the_last_attempt(self, repo: Repo):
        repo.write("src/a.py")
        self.init_ticket(repo, repo.loaded.working_tree_hash())
        repo.write("src/a.py", "changed\n")
        repo.write("src/new.py")

        result = transition(repo.root, "delta", "ABC-1")

        assert "2 file(s) changed" in result.stdout
        assert "src/a.py" in result.stdout
        assert "src/new.py" in result.stdout

    def test_delta_is_empty_when_nothing_changed(self, repo: Repo):
        repo.write("src/a.py")
        self.init_ticket(repo, repo.loaded.working_tree_hash())

        result = transition(repo.root, "delta", "ABC-1")

        assert "0 file(s) changed" in result.stdout

    def test_the_template_carries_the_verified_tree_key(self):
        assert "\nverified_tree:" in read("build-loop/assets/spec-template.md")


class TestBase:
    def test_base_moves_to_the_merge_base_with_the_base_branch(self, repo: Repo):
        result = transition(
            repo.root,
            "init",
            "ABC-1",
            "--mode",
            "immediate",
            "--title",
            "t",
            "--branch",
            "b",
            "--base-sha",
            "0000000",
        )
        assert result.returncode == 0, result.stdout
        branch = repo.loaded.PROJECT.get("base_branch", "main")
        git(repo.root, "update-ref", f"refs/remotes/origin/{branch}", repo.base)

        moved = transition(repo.root, "base", "ABC-1")

        assert moved.returncode == 0, moved.stdout
        spec = (repo.root / "docs/specs/ABC-1.md").read_text(encoding="utf-8")
        assert f"base_sha: {repo.base}" in spec
