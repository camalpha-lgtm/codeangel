from __future__ import annotations

import re
from pathlib import Path

import pytest
from support import PYTHON, run

from codeangel.cli import main
from codeangel.install.tree import PAYLOAD

ROOT = Path(__file__).resolve().parents[2]


class TestPayload:
    def test_managed_files_are_project_agnostic(self):
        banned = re.compile(
            r"poetry|prek|pytest|\bruff\b|actually|backend/|makemigrations|azure", re.I
        )
        offenders = []
        for path in PAYLOAD.managed.base.rglob("*"):
            if path.is_file() and banned.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(PAYLOAD.root).as_posix())

        assert offenders == []

    def test_presets_are_listed(self, capsys: pytest.CaptureFixture[str]):
        assert main(["presets"]) == 0

        out = capsys.readouterr().out
        assert "django-drf" in out
        assert "expo" in out
        assert "ninja" not in out.lower()

    def test_presets_do_not_mention_django_ninja(self):
        offenders = [
            path.relative_to(PAYLOAD.root).as_posix()
            for path in (PAYLOAD.presets).rglob("*")
            if path.is_file() and "ninja" in path.read_text(encoding="utf-8").lower()
        ]

        assert offenders == []


class TestHarnessStandards:
    def test_agents_md_requires_object_oriented_design(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "object-oriented" in text.lower()
        assert "docs/ai/code-standards.md" in text

    def test_code_standards_doc_forbids_all_comment_kinds(self):
        text = (ROOT / "docs/ai/code-standards.md").read_text(encoding="utf-8")
        assert "single-line" in text
        assert "multi-line" in text
        assert "docstring" in text

    def test_scaffold_ships_code_standards_and_routes_to_it(self, tmp_path: Path):
        root = tmp_path / "fresh"
        root.mkdir()
        assert run(root, "init", "--name", "fresh", "--python", PYTHON) == 0
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        assert (root / "docs/ai/code-standards.md").is_file()
        assert "docs/ai/code-standards.md" in agents
        assert len(agents.splitlines()) <= 50

    def test_build_stages_reference_code_standards(self):
        banned = re.compile(
            r"poetry|prek|pytest|\bruff\b|actually|backend/|makemigrations|azure", re.I
        )
        managed = PAYLOAD.managed.base
        implement = (managed / "dot_agents/skills/build-implement/SKILL.md").read_text(
            encoding="utf-8"
        )
        verify = (managed / "dot_agents/skills/build-verify/SKILL.md").read_text(encoding="utf-8")
        assert "code standards" in implement.lower()
        assert "code standards" in verify.lower()
        offenders = [
            path.relative_to(PAYLOAD.root).as_posix()
            for path in managed.rglob("*")
            if path.is_file() and banned.search(path.read_text(encoding="utf-8"))
        ]
        assert offenders == []
