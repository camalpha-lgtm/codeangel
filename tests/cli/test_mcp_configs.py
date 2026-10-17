from __future__ import annotations

import json
import re
from pathlib import Path

from codeangel.install.lockfile import Lockfile
from codeangel.install.tree import PAYLOAD

ROOT = Path(__file__).resolve().parents[2]
CLAUDE_CONFIG = ".mcp.json"
CURSOR_CONFIG = ".cursor/mcp.json"
SKILLS = PAYLOAD.managed.base / "dot_codeangel/skills"
CONTRACT = SKILLS / "build-loop/references/contract.md"
REVIEW = SKILLS / "build-review/SKILL.md"
CLEANUP = SKILLS / "worktree-cleanup/SKILL.md"
LOOP = SKILLS / "build-loop/SKILL.md"


def servers(project: Path, relative: str) -> dict[str, dict]:
    return json.loads((project / relative).read_text(encoding="utf-8"))["mcpServers"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestMcpConfigs:
    def test_init_installs_both_configs(self, project: Path):
        for relative in (CLAUDE_CONFIG, CURSOR_CONFIG):
            declared = servers(project, relative)

            assert {"linear", "github"} <= set(declared), relative
            assert all(entry["url"].startswith("https://") for entry in declared.values())

    def test_claude_servers_declare_the_http_transport(self, project: Path):
        assert {entry["type"] for entry in servers(project, CLAUDE_CONFIG).values()} == {"http"}

    def test_configs_carry_no_credentials(self, project: Path):
        for relative in (CLAUDE_CONFIG, CURSOR_CONFIG):
            for entry in servers(project, relative).values():
                assert not {"headers", "env", "args"} & set(entry)
            text = (project / relative).read_text(encoding="utf-8").lower()
            assert not any(word in text for word in ("bearer", "token", "key"))

    def test_configs_are_in_the_lockfile(self, project: Path):
        locked = Lockfile(project).load()

        assert CLAUDE_CONFIG in locked
        assert CURSOR_CONFIG in locked


class TestBuildLoopTooling:
    def test_no_shipped_build_loop_file_has_an_api_client_path(self):
        banned = re.compile(r"LINEAR_API_KEY|\bcurl\b|graphql|issueUpdate|linear-api", re.I)
        offenders = [
            path.relative_to(SKILLS).as_posix()
            for path in SKILLS.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and banned.search(read(path))
        ]

        assert offenders == []

    def test_contract_declares_mcp_first_tools(self):
        match = re.search(r"^## Tools\n(.*?)(?=^## )", read(CONTRACT), re.S | re.M)

        assert match
        assert "Linear MCP" in match.group(1)
        assert "GitHub MCP" in match.group(1)
        assert "`gh`" in match.group(1)
        assert "fallback" in match.group(1)

    def test_review_uses_the_github_mcp_for_pull_requests(self):
        text = read(REVIEW)

        assert "GitHub MCP" in text
        for command in (
            "gh pr create",
            "gh pr ready",
            "gh run rerun",
            "gh run view",
            "gh run list",
        ):
            assert command not in text

    def test_cleanup_lists_merged_prs_through_the_github_mcp(self):
        text = read(CLEANUP)

        assert "GitHub MCP" in text
        assert "gh pr list" not in text

    def test_blocking_waits_stay_on_gh(self):
        review = read(REVIEW)

        assert "gh pr checks" in review
        assert "--watch" in review
        assert "no model call" in review
        assert "scripts/await_merge.py" in read(LOOP)
        assert "no model call" in read(LOOP)
