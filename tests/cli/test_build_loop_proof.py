from __future__ import annotations

from pathlib import Path

import pytest
from support import transition
from support.evidence import EvidenceProject

SHA = "0123abcd"
REPO = "owner/repo"


class TestProofRendering:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        return EvidenceProject(project)

    def spec(self, evidence: EvidenceProject):
        shot = evidence.artefact("ac-1-ui.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)
        text = evidence.artefact("ac-2-api.txt", "GET /orders\nHTTP/1.1 200 OK\n")
        return evidence.spec(
            [
                "- [x] AC-1: A user sees the order list [proof: ui]",
                "- [x] AC-2: A client lists orders [proof: api]",
                "- [x] AC-3: A user exports orders [proof: cli]",
            ],
            [
                f"| AC-1 | ui | {shot} | the list page |",
                f"| AC-2 | api | {text} | 200 with orders |",
                "| AC-3 | cli | not captured: no export command yet | - |",
            ],
        )

    def test_section_shows_images_text_and_warnings(self, evidence: EvidenceProject):
        section = evidence.module.render_proof(self.spec(evidence), REPO, SHA)

        base = f"https://github.com/{REPO}/blob/{SHA}/docs/specs/evidence/ABC-1"
        assert f"![AC-1 ac-1-ui.png]({base}/ac-1-ui.png?raw=true)" in section
        assert "HTTP/1.1 200 OK" in section
        assert "```text" in section
        assert "⚠ **cli** not captured: no export command yet" in section
        assert "2 of 3 acceptance criteria have captured proof" in section
        assert "### AC-1 — A user sees the order list" in section
        assert "[proof:" not in section

    def test_splicing_replaces_only_the_marked_block(self, evidence: EvidenceProject):
        module = evidence.module
        first = module.render_proof(self.spec(evidence), REPO, "1111111")
        second = module.render_proof(self.spec(evidence), REPO, "2222222")
        body = "## Summary\nSomething\n\n" + first + "\n## Out of scope\nNothing\n"

        updated = module.splice_proof(body, second)

        assert "1111111" not in updated
        assert "2222222" in updated
        assert updated.startswith("## Summary\nSomething")
        assert updated.rstrip().endswith("## Out of scope\nNothing")
        assert updated.count(module.PROOF_BEGIN) == 1

    def test_proof_command_writes_into_a_body_file(self, project: Path):
        evidence = EvidenceProject(project)
        transition(
            project,
            "init",
            "ABC-1",
            "--mode",
            "plan",
            "--title",
            "t",
            "--branch",
            "b",
            "--base-sha",
            "abc",
        )
        spec_file = project / "docs/specs/ABC-1.md"
        text = spec_file.read_text(encoding="utf-8")
        proof = evidence.artefact("ac-1-cli.txt", "$ run\nok\n")
        text = text.replace(
            "- [ ] AC-1: <what a user does and sees: screen / endpoint / command + input → observable result> [proof: api|ui|cli|none — reason]",
            "- [x] AC-1: A user runs it [proof: cli]",
        ).replace(
            "| AC-1 | <api, ui, cli or none> | <docs/specs/evidence/<TICKET>/ac-1-api.txt> | <what the proof shows> |",
            f"| AC-1 | cli | {proof} | it works |",
        )
        spec_file.write_text(text, encoding="utf-8")
        body = project / "body.md"
        body.write_text("## Summary\nHello\n", encoding="utf-8")

        result = transition(
            project, "proof", "ABC-1", "--repo", REPO, "--sha", SHA, "--into", str(body)
        )

        assert result.returncode == 0, result.stdout
        written = body.read_text(encoding="utf-8")
        assert written.startswith("## Summary\nHello")
        assert "## Proof" in written
        assert "$ run" in written
