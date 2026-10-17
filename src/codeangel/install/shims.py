import subprocess
import sys
from pathlib import Path

from codeangel.project.model import Paths


class ShimSynchroniser:
    def run(self, root: Path, check: bool) -> int:
        command = [sys.executable, str(root / Paths.SYNC)]
        if check:
            command.append("--check")
        return subprocess.run(command, cwd=root).returncode

    def check_quiet(self, root: Path) -> int:
        return subprocess.run(
            [sys.executable, str(root / Paths.SYNC), "--check"],
            cwd=root,
            capture_output=True,
        ).returncode
