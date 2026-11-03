from __future__ import annotations

import subprocess
from pathlib import Path

from codeangel.install.tree import PAYLOAD
from support import load_transition

SKILLS = PAYLOAD.managed.base / "dot_codeangel/skills"


def read(relative: str) -> str:
    return (SKILLS / relative).read_text(encoding="utf-8")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return result.stdout.strip()


class Repo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.loaded = load_transition(root)
        git(root, "init", "-q")
        (root / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "base")
        self.base = git(root, "rev-parse", "HEAD")

    def write(self, relative: str, text: str = "x\n") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def spec(self, affected: list[str], amendments: str = "") -> object:
        rows = "".join(f"| {cell} | modify | why |\n" for cell in affected)
        return self.loaded.Spec(
            f"---\nbase_sha: {self.base}\n---\n\n## Affected files\n"
            f"| path | change | why |\n|---|---|---|\n{rows}\n## Plan amendments\n{amendments}\n"
        )

    def scope(self, affected: list[str], amendments: str = "") -> list[str]:
        return self.loaded.check_scope_within_affected(self.spec(affected, amendments), "")
