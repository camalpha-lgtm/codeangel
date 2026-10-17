from __future__ import annotations

from pathlib import Path

from codeangel.install.tree import PAYLOAD

ROOT = Path(__file__).resolve().parents[2]
CLAUDE_CONFIG = ".mcp.json"
CURSOR_CONFIG = ".cursor/mcp.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestDocs:
    DOCS = (
        ROOT / "README.md",
        ROOT / "AGENTS.md",
        ROOT / "docs/ai/agent-docs.md",
        ROOT / "docs/ai/repo-map.md",
        ROOT / "docs/ai/git-workflow.md",
        PAYLOAD.managed.base / "docs/ai/agent-docs.md",
        PAYLOAD.scaffold.base / "docs/ai/repo-map.md",
        PAYLOAD.scaffold.base / "docs/ai/git-workflow.md",
    )
    DOC_MAPS = (ROOT / "docs/ai/doc-map.toml", PAYLOAD.scaffold.base / "docs/ai/doc-map.toml")

    def test_docs_name_the_mcp_configs(self):
        missing = [
            path.relative_to(ROOT).as_posix()
            for path in self.DOCS
            if CLAUDE_CONFIG not in read(path) and CURSOR_CONFIG not in read(path)
        ]

        assert missing == []

    def test_doc_maps_flag_mcp_config_changes(self):
        for path in self.DOC_MAPS:
            text = read(path)

            assert f'"{CLAUDE_CONFIG}"' in text, path
            assert '".cursor/*"' in text, path
