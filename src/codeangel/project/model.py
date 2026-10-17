from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

from codeangel import __version__
from codeangel.io.errors import CodeangelError


class Paths:
    CONFIG = ".agents/codeangel.toml"
    LOCK = ".agents/codeangel.lock.json"
    SYNC = ".agents/sync-shims.py"
    TRANSITION = ".agents/skills/build-loop/scripts/transition.py"


class Project:
    def __init__(self, root: Path, config: dict[str, Any]) -> None:
        self.root = root
        self.config = config

    @classmethod
    def discover(cls, start: Path) -> Project:
        for directory in [start, *start.parents]:
            if (directory / Paths.CONFIG).is_file():
                return cls(directory, cls.read_config(directory))
        raise CodeangelError(
            f"no {Paths.CONFIG} in {start} or its parents — run `codeangel init` first"
        )

    @staticmethod
    def read_config(root: Path) -> dict[str, Any]:
        try:
            return tomllib.loads((root / Paths.CONFIG).read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as error:
            raise CodeangelError(f"{Paths.CONFIG}: {error}") from error

    @staticmethod
    def package_name(name: str) -> str:
        package = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "project"
        if package[0].isdigit():
            return f"p_{package}"
        return package

    def variables(self) -> dict[str, str]:
        project = self.config.get("project", {})
        name = project.get("name", "project")
        python = self.config.get("runtime", {}).get("python", "python3")
        return {
            "project_name": name,
            "project_package": self.package_name(name),
            "base_branch": project.get("base_branch", "main"),
            "python": python,
            "python_toml": json.dumps(python),
            "codeangel_version": __version__,
        }
