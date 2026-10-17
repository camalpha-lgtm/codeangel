from __future__ import annotations

from pathlib import Path

import pytest
from support import transition
from support.evidence import EvidenceProject

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


class TestProofPlanning:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        return EvidenceProject(project)

    def test_untagged_criterion_is_named(self, evidence: EvidenceProject):
        spec = evidence.spec(
            [
                "- [ ] AC-1: A user lists orders [proof: api]",
                "- [ ] AC-2: A user sees the list",
            ]
        )

        problems = evidence.planning_problems(spec)

        assert len(problems) == 1
        assert "AC-2" in problems[0]

    def test_every_tag_form_is_accepted(self, evidence: EvidenceProject):
        spec = evidence.spec(
            [
                "- [ ] AC-1: a [proof: api]",
                "- [ ] AC-2: b [proof: ui+api]",
                "- [ ] AC-3: c [proof: cli]",
                "- [ ] AC-4: d [proof: none — documentation only]",
            ]
        )

        assert evidence.planning_problems(spec) == []

    def test_none_needs_a_reason(self, evidence: EvidenceProject):
        spec = evidence.spec(["- [ ] AC-1: a [proof: none]"])

        assert evidence.planning_problems(spec)

    def test_template_placeholder_is_not_a_tag(self, evidence: EvidenceProject):
        spec = evidence.spec(["- [ ] AC-1: a [proof: api|ui|cli|none — reason]"])

        assert evidence.planning_problems(spec)

    def test_planned_exits_list_the_check(self, project: Path):
        result = transition(project, "show", "PLAN")

        assert result.stdout.count("ac_proof_planned") == 2


class TestEvidenceGate:
    @pytest.fixture
    def evidence(self, project: Path) -> EvidenceProject:
        return EvidenceProject(project)

    def test_missing_row_names_the_criterion(self, evidence: EvidenceProject):
        proof = evidence.artefact("ac-1-api.txt", "GET /orders\n200\n")
        spec = evidence.spec(
            ["- [x] AC-1: a [proof: api]", "- [x] AC-2: b [proof: cli]"],
            [f"| AC-1 | api | {proof} | lists orders |"],
        )

        assert evidence.problems(spec) == ["AC-2 has no row in §Evidence"]

    def test_proof_file_not_captured_and_n_a_rows_pass(self, evidence: EvidenceProject):
        shot = evidence.artefact("ac-1-ui.png", PNG)
        spec = evidence.spec(
            [
                "- [x] AC-1: a [proof: ui]",
                "- [x] AC-2: b [proof: cli]",
                "- [x] AC-3: c [proof: none — docs]",
            ],
            [
                f"| AC-1 | ui | {shot} | the list |",
                "| AC-2 | cli | not captured: no shell on the runner | - |",
                "| AC-3 | none | n/a: documentation only | - |",
            ],
        )

        assert evidence.problems(spec) == []

    def test_missing_empty_and_foreign_artefacts_are_refused(self, evidence: EvidenceProject):
        empty = evidence.artefact("ac-2-api.txt", "")
        spec = evidence.spec(
            [
                "- [x] AC-1: a [proof: api]",
                "- [x] AC-2: b [proof: api]",
                "- [x] AC-3: c [proof: api]",
            ],
            [
                "| AC-1 | api | docs/specs/evidence/ABC-1/gone.txt | x |",
                f"| AC-2 | api | {empty} | x |",
                "| AC-3 | api | README.md | x |",
            ],
        )

        problems = evidence.problems(spec)

        assert len(problems) == 3
        assert any("AC-2" in p and "empty" in p for p in problems)
        assert any("AC-3" in p and "not under" in p for p in problems)

    def test_planned_kind_cannot_be_downgraded_to_none(self, evidence: EvidenceProject):
        spec = evidence.spec(
            ["- [x] AC-1: a [proof: api]"],
            ["| AC-1 | none | n/a: skipped | - |"],
        )

        assert evidence.problems(spec)

    def test_every_planned_kind_needs_a_row(self, evidence: EvidenceProject):
        shot = evidence.artefact("ac-1-ui.png", PNG)
        spec = evidence.spec(
            ["- [x] AC-1: a [proof: ui+api]"],
            [f"| AC-1 | ui | {shot} | x |"],
        )

        assert evidence.problems(spec) == ["AC-1: planned api but §Evidence has no api row"]

    def test_credentials_in_artefacts_and_section_are_refused(self, evidence: EvidenceProject):
        leaked = evidence.artefact("ac-1-api.txt", "Cookie: sessionid=0123456789abcdef0123\n")
        spec = evidence.spec(
            ["- [x] AC-1: a [proof: api]"],
            [f"| AC-1 | api | {leaked} | Authorization: Bearer abcdefghijklmnop12345 |"],
        )

        problems = evidence.problems(spec)

        assert any("ac-1-api.txt" in p for p in problems)
        assert any("§Evidence" in p for p in problems)

    def test_redacted_values_are_accepted(self, evidence: EvidenceProject):
        clean = evidence.artefact(
            "ac-1-api.txt",
            "Cookie: sessionid=<redacted>\nAuthorization: Bearer <redacted>\npassword: required\n",
        )
        spec = evidence.spec(["- [x] AC-1: a [proof: api]"], [f"| AC-1 | api | {clean} | x |"])

        assert evidence.problems(spec) == []

    def test_verify_pass_exit_lists_the_check(self, project: Path):
        result = transition(project, "show", "VERIFY")

        assert "evidence_recorded" in result.stdout
