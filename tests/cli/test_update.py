from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from support import run

from codeangel.install.lockfile import Lockfile
from codeangel.install.managed import ManagedInstaller
from codeangel.install.tree import PAYLOAD, PayloadTree
from codeangel.io.files import ContentDigest


class TestUpdate:
    @pytest.fixture
    def newer_payload(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        managed = tmp_path / "newer-managed"
        shutil.copytree(PAYLOAD.managed.base, managed)
        monkeypatch.setattr(PAYLOAD, "managed", PayloadTree(managed))
        return managed

    def test_unchanged_payload_is_a_no_op(self, project: Path):
        before = Lockfile(project).load()

        assert run(project, "update") == 0

        assert Lockfile(project).load() == before

    def test_refreshes_files_the_user_has_not_touched(self, project: Path, newer_payload: Path):
        shipped = newer_payload / "dot_agents/skills/build-plan/SKILL.md"
        shipped.write_text(shipped.read_text(encoding="utf-8") + "\nNEW RULE\n", encoding="utf-8")

        assert run(project, "update") == 0

        local = project / ".agents/skills/build-plan/SKILL.md"
        assert "NEW RULE" in local.read_text(encoding="utf-8")
        assert Lockfile(project).load()[
            ".agents/skills/build-plan/SKILL.md"
        ] == ContentDigest().hexdigest(local.read_bytes())

    def test_never_overwrites_local_edits(self, project: Path, newer_payload: Path):
        local = project / ".agents/skills/build-plan/SKILL.md"
        local.write_text(local.read_text(encoding="utf-8") + "\nMY TWEAK\n", encoding="utf-8")
        shipped = newer_payload / "dot_agents/skills/build-plan/SKILL.md"
        shipped.write_text(shipped.read_text(encoding="utf-8") + "\nNEW RULE\n", encoding="utf-8")

        assert run(project, "update") == 0

        assert "MY TWEAK" in local.read_text(encoding="utf-8")
        assert "NEW RULE" not in local.read_text(encoding="utf-8")
        proposal = local.with_name("SKILL.md" + ManagedInstaller.NEW_SUFFIX)
        assert "NEW RULE" in proposal.read_text(encoding="utf-8")

    def test_force_overwrites_and_clears_the_proposal(self, project: Path, newer_payload: Path):
        local = project / ".agents/skills/build-plan/SKILL.md"
        local.write_text(local.read_text(encoding="utf-8") + "\nMY TWEAK\n", encoding="utf-8")
        shipped = newer_payload / "dot_agents/skills/build-plan/SKILL.md"
        shipped.write_text(shipped.read_text(encoding="utf-8") + "\nNEW RULE\n", encoding="utf-8")
        assert run(project, "update") == 0

        assert run(project, "update", "--force") == 0

        assert "MY TWEAK" not in local.read_text(encoding="utf-8")
        assert "NEW RULE" in local.read_text(encoding="utf-8")
        assert not local.with_name("SKILL.md" + ManagedInstaller.NEW_SUFFIX).exists()

    def test_removes_files_no_longer_shipped_unless_edited(
        self, project: Path, newer_payload: Path
    ):
        (newer_payload / "dot_agents/skills/worktree-cleanup/SKILL.md").unlink()
        (newer_payload / "dot_claude/agents/build-verifier.md").unlink()
        edited = project / ".claude/agents/build-verifier.md"
        edited.write_text(edited.read_text(encoding="utf-8") + "\nmine\n", encoding="utf-8")

        assert run(project, "update") == 0

        assert not (project / ".agents/skills/worktree-cleanup/SKILL.md").exists()
        assert edited.exists()

    def test_leaves_project_owned_files_alone(self, project: Path):
        agents = project / "AGENTS.md"
        agents.write_text("customised\n", encoding="utf-8")

        assert run(project, "update") == 0

        assert agents.read_text(encoding="utf-8") == "customised\n"
