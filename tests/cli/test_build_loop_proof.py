from __future__ import annotations

from pathlib import Path

import pytest
from support import transition
from support.evidence import EvidenceProject

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8


class TestProofRendering:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        return EvidenceProject(project)

    def spec(self, evidence: EvidenceProject):
        shot = evidence.artefact("ac-1-ui.png", PNG)
        page = evidence.artefact("ac-1-ui.txt", "heading: Orders\nrows: 3\n")
        text = evidence.artefact("ac-2-api.txt", "GET /orders\nHTTP/1.1 200 OK\n")
        return evidence.spec(
            [
                "- [x] AC-1: A user sees the order list [proof: ui]",
                "- [x] AC-2: A client lists orders [proof: api]",
                "- [x] AC-3: A user exports orders [proof: cli]",
            ],
            [
                f"| AC-1 | ui | {shot}, {page} | the list page |",
                f"| AC-2 | api | {text} | 200 with orders |",
                "| AC-3 | cli | not captured: no export command yet | - |",
            ],
        )

    def init_ticket(self, project: Path) -> Path:
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
        evidence = EvidenceProject(project)
        spec_file = project / "docs/specs/ABC-1.md"
        proof = evidence.artefact("ac-1-cli.txt", "$ run\nok\n")
        text = spec_file.read_text(encoding="utf-8")
        text = text.replace(
            "- [ ] AC-1: <what a user does and sees: screen / endpoint / command + input → observable result> [proof: api|ui|cli|none — reason]",
            "- [x] AC-1: A user runs it [proof: cli]",
        ).replace(
            "| AC-1 | <api, ui, cli or none> | <docs/specs/evidence/<TICKET>/ac-1-api.txt> | <what the proof shows> |",
            f"| AC-1 | cli | {proof} | it works |",
        )
        spec_file.write_text(text, encoding="utf-8")
        return evidence.home()

    def test_section_shows_text_inline_without_repo_links(self, evidence: EvidenceProject):
        section = evidence.module.render_proof(self.spec(evidence))

        assert "HTTP/1.1 200 OK" in section
        assert "heading: Orders" in section
        assert "```text" in section
        assert "<details>" in section
        assert "github.com" not in section
        assert "blob" not in section
        assert "![" not in section
        assert "`ac-1-ui.png` — screenshot kept locally, not committed" in section
        assert (
            "- ⚠ **AC-3** — A user exports orders — not captured (cli): no export command yet"
            in section
        )
        assert "2 of 3 criteria have captured proof" in section
        assert "- ✅ **AC-1** — A user sees the order list — the list page" in section
        assert section.count("<details>") == 1
        assert "[proof:" not in section

    def test_section_stays_short(self, evidence: EvidenceProject):
        long_title = "A user opens the page and sees every order. " + "It keeps going. " * 30
        big = evidence.artefact("ac-1-cli.txt", "".join(f"line {n}\n" for n in range(70)))
        spec = evidence.spec(
            [f"- [x] AC-1: {long_title} [proof: cli]"],
            [f"| AC-1 | cli | {big} | one note |"],
        )

        section = evidence.module.render_proof(spec)

        assert "line 5" in section
        assert "line 6" not in section
        assert "64 more lines" in section
        assert "It keeps going. It keeps going." not in section
        assert len(section.splitlines()) <= 24
        assert section.splitlines().index("<details><summary>Output excerpts</summary>") <= 8
        assert max(len(line) for line in section.splitlines()) <= 160

    def media_spec(self, evidence: EvidenceProject):
        shot = evidence.artefact("ac-1-ui.png", PNG)
        clip = evidence.artefact("ac-1-ui.mp4", b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 16)
        preview = evidence.artefact("ac-1-ui.gif", b"GIF89a" + b"\x00" * 16)
        return evidence.spec(
            ["- [x] AC-1: A user sees the order list [proof: ui]"],
            [f"| AC-1 | ui | {shot}, {clip}, {preview} | the list page |"],
        )

    def test_published_screenshot_is_shown_inline(self, evidence: EvidenceProject):
        section = evidence.module.render_proof(self.media_spec(evidence), "owner/repo", "0123abcd")

        base = "https://github.com/owner/repo/blob/0123abcd/ABC-1"
        lines = section.splitlines()
        item = lines.index(next(line for line in lines if line.startswith("- ✅ **AC-1**")))
        assert f"![ac-1-ui.png]({base}/ac-1-ui.png?raw=true)" in "\n".join(lines[item : item + 8])

    def test_published_video_is_a_link_with_a_preview(self, evidence: EvidenceProject):
        section = evidence.module.render_proof(self.media_spec(evidence), "owner/repo", "0123abcd")

        base = "https://github.com/owner/repo/blob/0123abcd/ABC-1"
        assert f"[▶ ac-1-ui.mp4]({base}/ac-1-ui.mp4?raw=true)" in section
        assert f"![ac-1-ui.gif]({base}/ac-1-ui.gif?raw=true)" in section
        assert "<video" not in section
        assert len(section.splitlines()) <= 16

    def test_unpublished_media_is_a_local_note(self, evidence: EvidenceProject):
        section = evidence.module.render_proof(self.media_spec(evidence))

        assert "`ac-1-ui.png` — screenshot kept locally, not committed" in section
        assert "`ac-1-ui.mp4` — video kept locally, not committed" in section
        assert "github.com" not in section
        assert "![" not in section

    def test_proof_command_accepts_repo_and_sha(self, project: Path):
        TestProofRendering.init_ticket(self, project)
        evidence = EvidenceProject(project)
        shot = evidence.artefact("ac-1-ui.png", PNG)
        spec_file = project / "docs/specs/ABC-1.md"
        text = spec_file.read_text(encoding="utf-8").replace(
            "ac-1-cli.txt |", f"ac-1-cli.txt, {shot} |"
        )
        spec_file.write_text(text, encoding="utf-8")
        body = project / "body.md"
        body.write_text("## Summary\nHello\n", encoding="utf-8")

        result = transition(
            project,
            "proof",
            "ABC-1",
            "--repo",
            "owner/repo",
            "--sha",
            "0123abcd",
            "--into",
            str(body),
        )

        assert result.returncode == 0, result.stdout
        assert "/blob/0123abcd/ABC-1/ac-1-ui.png?raw=true" in body.read_text(encoding="utf-8")

    def test_note_keeps_its_leading_backtick(self, evidence: EvidenceProject):
        proof = evidence.artefact("ac-1-cli.txt", "ok\n")
        spec = evidence.spec(
            ["- [x] AC-1: a [proof: cli]"], [f"| AC-1 | cli | {proof} | `T proof` works |"]
        )

        assert "— `T proof` works" in evidence.module.render_proof(spec)

    def test_splicing_replaces_only_the_marked_block(self, evidence: EvidenceProject):
        module = evidence.module
        spec = self.spec(evidence)
        first = module.render_proof(spec)
        evidence.artefact("ac-2-api.txt", "GET /orders\nHTTP/1.1 201 Created\n")
        second = module.render_proof(spec)
        body = "## Summary\nSomething\n\n" + first + "\n## Out of scope\nNothing\n"

        updated = module.splice_proof(body, second)

        assert "200 OK" not in updated
        assert "201 Created" in updated
        assert updated.startswith("## Summary\nSomething")
        assert updated.rstrip().endswith("## Out of scope\nNothing")
        assert updated.count(module.PROOF_BEGIN) == 1

    def test_proof_command_writes_into_a_body_file(self, project: Path):
        self.init_ticket(project)
        body = project / "body.md"
        body.write_text("## Summary\nHello\n", encoding="utf-8")

        result = transition(project, "proof", "ABC-1", "--into", str(body))

        assert result.returncode == 0, result.stdout
        written = body.read_text(encoding="utf-8")
        assert written.startswith("## Summary\nHello")
        assert "## Proof" in written
        assert "$ run" in written

    def test_missing_artefacts_keep_the_existing_block(self, project: Path):
        home = self.init_ticket(project)
        body = project / "body.md"
        body.write_text("## Summary\nHello\n", encoding="utf-8")
        transition(project, "proof", "ABC-1", "--into", str(body))
        before = body.read_text(encoding="utf-8")
        (home / "ac-1-cli.txt").unlink()

        kept = transition(project, "proof", "ABC-1", "--into", str(body))

        assert kept.returncode == 0, kept.stdout
        assert body.read_text(encoding="utf-8") == before
        assert "kept the existing Proof block" in kept.stdout

        fresh = project / "fresh.md"
        fresh.write_text("## Summary\nHello\n", encoding="utf-8")
        transition(project, "proof", "ABC-1", "--into", str(fresh))
        assert "no longer available" in fresh.read_text(encoding="utf-8")
