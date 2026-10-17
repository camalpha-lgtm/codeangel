"""End-to-end tests of the codeangel CLI against throwaway projects."""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from codeangel import cli

PAYLOAD = Path(cli.__file__).parent / "payload"
VAR_RE = re.compile(r"\{\{[a-z_]+\}\}")
PYTHON = f'"{sys.executable}"' if " " in sys.executable else sys.executable


def run(root: Path, *args: str) -> int:
    return cli.main(["-C", str(root), *args])


def text_files(root: Path) -> list[Path]:
    skip = {".git", "node_modules"}
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not skip & set(path.parts) and path.suffix not in {".png", ".pyc"}
    ]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "my-app"
    root.mkdir()
    assert run(root, "init", "--name", "my-app", "--python", PYTHON) == 0
    return root


@pytest.fixture
def backend_project(project: Path) -> Path:
    assert run(project, "add", "django-drf", "backend") == 0
    return project


def load_transition(root: Path):
    spec = importlib.util.spec_from_file_location("transition", root / cli.TRANSITION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        locked = set(cli.load_lock(project))
        shipped = {cli.target_path(rel).as_posix() for rel in cli.payload_files(cli.MANAGED)}

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


class TestAdd:
    def test_django_drf_creates_a_runnable_skeleton_and_wires_docs(self, backend_project: Path):
        root = backend_project

        for expected in [
            "backend/manage.py",
            "backend/my_app/settings.py",
            "backend/my_app/urls.py",
            "backend/core/base_test.py",
            "backend/AGENTS.md",
            "backend/docs/ai/architecture.md",
            "backend/.pre-commit-config.yaml",
            ".github/workflows/backend.yml",
        ]:
            assert (root / expected).is_file(), expected
        assert "my_app.urls" in (root / "backend/my_app/settings.py").read_text(encoding="utf-8")
        assert "| backend |" in (root / "AGENTS.md").read_text(encoding="utf-8")
        assert "`backend/`" in (root / "README.md").read_text(encoding="utf-8")
        assert "`backend/`" in (root / "docs/ai/repo-map.md").read_text(encoding="utf-8")
        assert "backend.yml" in (root / "docs/ai/git-workflow.md").read_text(encoding="utf-8")
        assert "codeangel:preset django-drf backend" in (root / "docs/ai/doc-map.toml").read_text(
            encoding="utf-8"
        )
        assert 'path = "backend"' in (root / ".agents/codeangel.toml").read_text(encoding="utf-8")

    def test_no_unresolved_template_variables(self, backend_project: Path):
        leftovers = [
            path.relative_to(backend_project).as_posix()
            for path in text_files(backend_project)
            if VAR_RE.search(path.read_text(encoding="utf-8"))
        ]

        assert leftovers == []

    def test_is_idempotent(self, backend_project: Path):
        tracked = [
            "AGENTS.md",
            "README.md",
            "docs/ai/repo-map.md",
            "docs/ai/doc-map.toml",
            "docs/ai/git-workflow.md",
            ".agents/codeangel.toml",
        ]
        before = {name: (backend_project / name).read_text(encoding="utf-8") for name in tracked}

        assert run(backend_project, "add", "django-drf", "backend") == 0

        after = {name: (backend_project / name).read_text(encoding="utf-8") for name in tracked}
        assert after == before

    def test_never_overwrites_existing_area_files(self, project: Path):
        (project / "backend").mkdir()
        (project / "backend/AGENTS.md").write_text("custom\n", encoding="utf-8")

        assert run(project, "add", "django-drf", "backend") == 0

        assert (project / "backend/AGENTS.md").read_text(encoding="utf-8") == "custom\n"

    def test_unknown_preset_is_an_error(self, project: Path):
        assert run(project, "add", "no-such-preset", "x") == 2

    def test_expo_requires_an_existing_app(self, project: Path):
        assert run(project, "add", "expo", "frontend") == 2

        (project / "frontend").mkdir()
        (project / "frontend/package.json").write_text("{}\n", encoding="utf-8")
        assert run(project, "add", "expo", "frontend") == 0
        assert (project / "frontend/AGENTS.md").is_file()
        assert (project / ".github/workflows/frontend.yml").is_file()

    def test_requires_an_initialised_project(self, tmp_path: Path):
        assert run(tmp_path, "add", "django-drf", "backend") == 2

    def test_doc_map_stays_valid_toml_with_two_areas(self, backend_project: Path):
        import tomllib

        (backend_project / "frontend").mkdir()
        (backend_project / "frontend/package.json").write_text("{}\n", encoding="utf-8")
        assert run(backend_project, "add", "expo", "frontend") == 0

        rules = tomllib.loads(
            (backend_project / "docs/ai/doc-map.toml").read_text(encoding="utf-8")
        )["rule"]
        assert any("backend/" in rule["paths"][0] for rule in rules)
        assert any("frontend/" in rule["paths"][0] for rule in rules)


class TestUpdate:
    @pytest.fixture
    def newer_payload(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        managed = tmp_path / "newer-managed"
        shutil.copytree(cli.MANAGED, managed)
        monkeypatch.setattr(cli, "MANAGED", managed)
        return managed

    def test_unchanged_payload_is_a_no_op(self, project: Path):
        before = cli.load_lock(project)

        assert run(project, "update") == 0

        assert cli.load_lock(project) == before

    def test_refreshes_files_the_user_has_not_touched(self, project: Path, newer_payload: Path):
        shipped = newer_payload / "dot_agents/skills/build-plan/SKILL.md"
        shipped.write_text(shipped.read_text(encoding="utf-8") + "\nNEW RULE\n", encoding="utf-8")

        assert run(project, "update") == 0

        local = project / ".agents/skills/build-plan/SKILL.md"
        assert "NEW RULE" in local.read_text(encoding="utf-8")
        assert cli.load_lock(project)[".agents/skills/build-plan/SKILL.md"] == cli.digest(
            local.read_bytes()
        )

    def test_never_overwrites_local_edits(self, project: Path, newer_payload: Path):
        local = project / ".agents/skills/build-plan/SKILL.md"
        local.write_text(local.read_text(encoding="utf-8") + "\nMY TWEAK\n", encoding="utf-8")
        shipped = newer_payload / "dot_agents/skills/build-plan/SKILL.md"
        shipped.write_text(shipped.read_text(encoding="utf-8") + "\nNEW RULE\n", encoding="utf-8")

        assert run(project, "update") == 0

        assert "MY TWEAK" in local.read_text(encoding="utf-8")
        assert "NEW RULE" not in local.read_text(encoding="utf-8")
        proposal = local.with_name("SKILL.md" + cli.NEW_SUFFIX)
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
        assert not local.with_name("SKILL.md" + cli.NEW_SUFFIX).exists()

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


class TestSyncAndDoctor:
    def test_sync_check_detects_and_fixes_drift(self, project: Path):
        skill = project / ".agents/skills/build-learn/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "description: Stage", "description: Edited stage", 1
            ),
            encoding="utf-8",
        )

        assert run(project, "sync", "--check") == 1
        assert run(project, "sync") == 0
        assert run(project, "sync", "--check") == 0

    def test_doctor_passes_on_a_fresh_project(self, backend_project: Path):
        assert run(backend_project, "doctor") == 0

    def test_doctor_flags_a_deleted_managed_file(self, project: Path):
        (project / ".agents/skills/build-verify/SKILL.md").unlink()

        assert run(project, "doctor") == 1

    def test_doctor_flags_a_doc_map_pointing_at_a_missing_doc(self, project: Path):
        doc_map = project / "docs/ai/doc-map.toml"
        doc_map.write_text(
            doc_map.read_text(encoding="utf-8")
            + '\n[[rule]]\npaths = ["x/*"]\ndocs = ["docs/ai/nope.md"]\nwhy = "x"\n',
            encoding="utf-8",
        )

        assert run(project, "doctor") == 1


class TestBuildLoopScript:
    def transition(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / cli.TRANSITION), *args],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def init_ticket(self, root: Path, ticket: str = "ABC-1") -> subprocess.CompletedProcess[str]:
        return self.transition(
            root,
            "init",
            ticket,
            "--mode",
            "plan",
            "--title",
            "t",
            "--branch",
            "b",
            "--base-sha",
            "abc",
        )

    def test_map_loads_in_an_installed_project(self, project: Path):
        result = self.transition(project, "show")

        assert result.returncode == 0, result.stdout

    def test_specs_land_in_the_configured_spec_dir(self, project: Path):
        config = project / ".agents/codeangel.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'spec_dir = "docs/specs"', 'spec_dir = "work/specs"'
            ),
            encoding="utf-8",
        )

        result = self.init_ticket(project)

        assert result.returncode == 0, result.stdout
        assert (project / "work/specs/ABC-1.md").is_file()

    def test_ticket_pattern_comes_from_config(self, project: Path):
        config = project / ".agents/codeangel.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("'^[A-Z][A-Z0-9]+-\\d+$'", "'^FF-\\d+$'"),
            encoding="utf-8",
        )

        assert self.init_ticket(project, "ABC-1").returncode == 2
        assert self.init_ticket(project, "FF-1").returncode == 0

    def test_planned_tests_resolve_under_area_paths(self, backend_project: Path):
        tests = backend_project / "backend/orders/tests"
        tests.mkdir(parents=True)
        (tests / "test_orders_api.py").write_text(
            "class TestOrderList:\n    def test_returns_orders(self):\n        pass\n",
            encoding="utf-8",
        )
        transition = load_transition(backend_project)

        def problems(node_id: str) -> list[str]:
            spec = transition.Spec(
                "---\nticket: ABC-1\n---\n\n## Test plan\n| id | covers | asserts |\n|---|---|---|\n"
                f"| {node_id} | AC-1 | x |\n"
            )
            return transition.check_planned_tests_exist(spec, "")

        assert problems("orders/tests/test_orders_api.py::TestOrderList::test_returns_orders") == []
        assert problems("orders/tests/test_orders_api.py::TestOrderList::test_missing")
        assert problems("orders/tests/test_nope.py::TestX::test_y")


class TestPayload:
    def test_managed_files_are_project_agnostic(self):
        banned = re.compile(
            r"poetry|prek|pytest|\bruff\b|actually|backend/|makemigrations|azure", re.I
        )
        offenders = []
        for path in (PAYLOAD / "managed").rglob("*"):
            if path.is_file() and banned.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(PAYLOAD).as_posix())

        assert offenders == []

    def test_presets_are_listed(self, capsys: pytest.CaptureFixture[str]):
        assert cli.main(["presets"]) == 0

        out = capsys.readouterr().out
        assert "django-drf" in out
        assert "expo" in out
        assert "ninja" not in out.lower()

    def test_presets_do_not_mention_django_ninja(self):
        offenders = [
            path.relative_to(PAYLOAD).as_posix()
            for path in (PAYLOAD / "presets").rglob("*")
            if path.is_file() and "ninja" in path.read_text(encoding="utf-8").lower()
        ]

        assert offenders == []
