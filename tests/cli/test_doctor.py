from __future__ import annotations

from pathlib import Path

from support import run


class TestDoctor:
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
