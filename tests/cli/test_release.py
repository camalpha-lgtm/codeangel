from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".github/scripts/bump_version.py"
VERSION_FILE = "src/codeangel/__init__.py"
INITIAL = '__version__ = "0.1.0"\n\nOTHER = "keep me"\n'


class ReleaseRepo:
    def __init__(self, path: Path) -> None:
        self.path = path

    def git(self, *args: str) -> str:
        done = subprocess.run(
            ["git", *args],
            cwd=self.path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return done.stdout.strip()

    def create(self) -> ReleaseRepo:
        self.path.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "tester")
        self.git("config", "user.email", "tester@example.com")
        self.git("config", "core.autocrlf", "false")
        target = self.path / VERSION_FILE
        target.parent.mkdir(parents=True)
        target.write_text(INITIAL, encoding="utf-8")
        self.git("add", VERSION_FILE)
        self.git("commit", "-q", "-m", "initial")
        return self

    def bump(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.path,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def text(self) -> str:
        return (self.path / VERSION_FILE).read_text(encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> ReleaseRepo:
    return ReleaseRepo(tmp_path / "repo").create()


class TestBumpVersion:
    def test_defaults_to_a_patch_bump(self, repo: ReleaseRepo):
        done = repo.bump()

        assert done.returncode == 0, done.stderr
        assert done.stdout.strip() == "0.1.1"
        assert '__version__ = "0.1.1"' in repo.text()

    def test_release_labels_pick_minor_and_major(self, repo: ReleaseRepo):
        assert repo.bump("--labels", "bug,release:minor").stdout.strip() == "0.2.0"
        assert repo.bump("--labels", "release:minor,release:major").stdout.strip() == "1.0.0"
        assert repo.bump("--labels", "").stdout.strip() == "1.0.1"

    def test_rewrites_only_the_version_line(self, repo: ReleaseRepo):
        repo.bump()

        assert repo.text() == INITIAL.replace("0.1.0", "0.1.1")
        assert repo.git("status", "--porcelain") == f"M {VERSION_FILE}"


class TestRelease:
    def test_release_commits_and_tags_the_bump(self, repo: ReleaseRepo):
        done = repo.bump("--release")

        assert done.returncode == 0, done.stderr
        assert done.stdout.strip() == "0.1.1"
        assert repo.git("log", "-1", "--format=%s") == "Release v0.1.1"
        assert repo.git("tag", "--list") == "v0.1.1"
        assert repo.git("cat-file", "-t", "v0.1.1") == "tag"
        assert repo.git("rev-parse", "v0.1.1^{commit}") == repo.git("rev-parse", "HEAD")
        assert '__version__ = "0.1.1"' in repo.git("show", f"v0.1.1:{VERSION_FILE}")
        assert repo.git("status", "--porcelain") == ""

    def test_second_release_gets_a_distinct_tag(self, repo: ReleaseRepo):
        repo.bump("--release")
        repo.bump("--release")

        assert repo.git("tag", "--list").split() == ["v0.1.1", "v0.1.2"]
        assert repo.git("rev-parse", "v0.1.1") != repo.git("rev-parse", "v0.1.2")

    def test_existing_tag_is_refused(self, repo: ReleaseRepo):
        repo.git("tag", "v0.1.1")
        head = repo.git("rev-parse", "HEAD")

        done = repo.bump("--release")

        assert done.returncode != 0
        assert "v0.1.1" in done.stderr
        assert repo.text() == INITIAL
        assert repo.git("rev-parse", "HEAD") == head
