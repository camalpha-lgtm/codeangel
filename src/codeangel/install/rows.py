from pathlib import Path

from codeangel.io.files import TextFile


class RowInserter:
    def insert(self, root: Path, rel: str, row: str, marker: str) -> str:
        path = root / rel
        if not path.is_file():
            return f"skipped {rel}: missing"
        text = path.read_text(encoding="utf-8")
        if row in text:
            return f"kept {rel}: row present"
        return self._place(path, rel, row, marker, text)

    def _place(self, path: Path, rel: str, row: str, marker: str, text: str) -> str:
        lines = text.splitlines(keepends=True)
        index = next((i for i, line in enumerate(lines) if line.startswith(marker)), None)
        if index is None:
            return f"MANUAL {rel}: no `{marker}` marker — add: {row}"
        lines.insert(index, row + "\n")
        TextFile().write(path, "".join(lines))
        return f"row added to {rel}"
