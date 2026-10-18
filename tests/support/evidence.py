from __future__ import annotations

from pathlib import Path

from support import load_transition

TABLE_HEAD = "| AC | kind | proof | note |\n|---|---|---|---|\n"


class EvidenceProject:
    def __init__(self, root: Path, ticket: str = "ABC-1") -> None:
        self.root = root
        self.ticket = ticket
        self.module = load_transition(root)

    def spec(self, criteria: list[str], rows: list[str] | None = None):
        text = (
            f"---\nticket: {self.ticket}\n---\n\n## Acceptance criteria\n"
            + "\n".join(criteria)
            + "\n\n## Evidence\n"
            + TABLE_HEAD
            + "\n".join(rows or [])
            + "\n"
        )
        return self.module.Spec(text)

    def artefact(self, name: str, content: str | bytes) -> str:
        path = self.module.prepare_evidence(self.ticket) / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path.relative_to(self.root).as_posix()

    def home(self) -> Path:
        return self.root / "docs/specs/evidence" / self.ticket

    def problems(self, spec) -> list[str]:
        return self.module.check_evidence_recorded(spec, "")

    def planning_problems(self, spec) -> list[str]:
        return self.module.check_ac_proof_planned(spec, "")
