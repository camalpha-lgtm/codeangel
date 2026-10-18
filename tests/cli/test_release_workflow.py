from __future__ import annotations

from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/release.yml"


class TestReleaseWorkflow:
    @pytest.fixture
    def workflow(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_wired_for_main_releases(self, workflow: str):
        assert "branches: [main]" in workflow
        assert "contents: write" in workflow
        assert "fetch-depth: 0" in workflow
        assert "startsWith(github.event.head_commit.message, 'Release v')" in workflow
        assert "group: release" in workflow
        assert "cancel-in-progress: false" in workflow
        assert "python .github/scripts/bump_version.py --release" in workflow
        assert "git push origin main" in workflow
        assert "gh release create" in workflow
        assert "pull_request" not in workflow
