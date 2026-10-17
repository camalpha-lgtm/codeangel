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


def run(root: Path, *args: str) -> int:
    return main(["-C", str(root), *args])


def text_files(root: Path) -> list[Path]:
    skip = {".git", "node_modules"}
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and not skip & set(path.parts) and path.suffix not in {".png", ".pyc"}
    ]


def load_transition(root: Path):
    spec = importlib.util.spec_from_file_location("transition", root / TRANSITION)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def transition(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / TRANSITION), *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
