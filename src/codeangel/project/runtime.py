import os
import subprocess
import sys


class PythonRuntime:
    def ok(self, command: str) -> bool:
        check = '-c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"'
        try:
            result = subprocess.run(
                f"{command} {check}", shell=True, capture_output=True, timeout=30
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        return result.returncode == 0

    def detect(self) -> str:
        candidates = ["py -3.13", "py -3.12", "py -3.11"] if os.name == "nt" else []
        for command in candidates + ["python3", "python"]:
            if self.ok(command):
                return command
        if " " in sys.executable:
            return f'"{sys.executable}"'
        return sys.executable
