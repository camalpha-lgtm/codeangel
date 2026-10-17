from __future__ import annotations

from pathlib import Path

from support import PYTHON, VAR_RE, run, text_files

from codeangel.install.lockfile import Lockfile
from codeangel.install.tree import PAYLOAD, PayloadTree


class TestInit:
    def test_installs_managed_scaffold_and_shims(self, project: Path):
        assert (project / ".agents/skills/build-loop/SKILL.md").is_file()
        assert (project / ".agents/skills/build-loop/references/stages.toml").is_file()
        assert (project / ".agents/sync-shims.py").is_file()
        assert (project / ".claude/skills/build-plan/SKILL.md").is_file()
        assert (project / ".claude/agents/build-verifier.md").is_file()
        assert "my-app" in (project / "AGENTS.md").read_text(encoding="utf-8")
        assert 'name = "my-app"' in (project / ".agents/codeangel.toml").read_text(encoding="utf-8")
        assert (project / ".gitignore").is_file()

    def test_lock_covers_every_managed_file(self, project: Path):
        locked = set(Lockfile(project).load())
        shipped = {PayloadTree.install_path(rel).as_posix() for rel in PAYLOAD.managed.files()}

        assert locked == shipped

    def test_no_unresolved_template_variables(self, project: Path):
        leftovers = [
            path.relative_to(project).as_posix()
            for path in text_files(project)
            if VAR_RE.search(path.read_text(encoding="utf-8"))
        ]

        assert leftovers == []

    def test_refuses_to_reinitialise(self, project: Path):
        assert run(project, "init", "--name", "my-app", "--python", PYTHON) == 2

    def test_project_files_are_never_overwritten(self, tmp_path: Path):
        root = tmp_path / "existing"
        root.mkdir()
        (root / "README.md").write_text("mine\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("mine too\n", encoding="utf-8")

        assert run(root, "init", "--name", "existing", "--python", PYTHON) == 0

        assert (root / "README.md").read_text(encoding="utf-8") == "mine\n"
        assert (root / "AGENTS.md").read_text(encoding="utf-8") == "mine too\n"
