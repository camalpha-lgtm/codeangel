from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

from codeangel.cli import main

PYTHON = f'"{sys.executable}"' if " " in sys.executable else sys.executable
VAR_RE = re.compile(r"\{\{[a-z_]+\}\}")
OLD_FOLDER = "." + "agents"
TRANSITION = ".codeangel/skills/build-loop/scripts/transition.py"
AWAIT_MERGE = ".codeangel/skills/build-loop/scripts/await_merge.py"


def run(root: Path, *args: str) -> int:
    return main(["-C", str(root), *args])


def text_files(root: Path) -> list[Path]:
    skip = {".git", "node_modules"}
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not skip & set(path.parts) and path.suffix not in {".png", ".pyc"}
    ]


def load_script(root: Path, relative: str):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, root / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def load_transition(root: Path):
    return load_script(root, TRANSITION)


def transition(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / TRANSITION), *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
