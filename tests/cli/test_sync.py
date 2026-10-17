from __future__ import annotations

from pathlib import Path

from support import run


class TestSync:
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
