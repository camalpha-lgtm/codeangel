import json
from pathlib import Path

from codeangel import __version__
from codeangel.io.files import TextFile
from codeangel.project.model import Paths


class Lockfile:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / Paths.LOCK

    def load(self) -> dict[str, str]:
        if not self.path.is_file():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))["files"]

    def save(self, files: dict[str, str]) -> None:
        data = {"codeangel": __version__, "files": dict(sorted(files.items()))}
        TextFile().write(self.path, json.dumps(data, indent=2) + "\n")

    def read_document(self) -> dict[str, object]:
        if not self.path.is_file():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))
