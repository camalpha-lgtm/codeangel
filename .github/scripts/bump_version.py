from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class ReleaseError(Exception):
    pass


@dataclass(frozen=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int

    PATTERN = re.compile(r"(\d+)\.(\d+)\.(\d+)")

    @classmethod
    def parse(cls, text: str) -> SemanticVersion:
        match = cls.PATTERN.fullmatch(text)
        if match is None:
            raise ReleaseError(f"not a semantic version: {text!r}")
        return cls(*(int(part) for part in match.groups()))

    def bump(self, level: str) -> SemanticVersion:
        if level == "major":
            return SemanticVersion(self.major + 1, 0, 0)
        if level == "minor":
            return SemanticVersion(self.major, self.minor + 1, 0)
        return SemanticVersion(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


class ReleaseLevel:
    PREFIX = "release:"
    ORDER = ("major", "minor")

    def __init__(self, labels: str) -> None:
        self.names = {label.strip() for label in labels.split(",") if label.strip()}

    def pick(self) -> str:
        for level in self.ORDER:
            if f"{self.PREFIX}{level}" in self.names:
                return level
        return "patch"


class VersionFile:
    LINE = re.compile(r'(?m)^(__version__\s*=\s*")([^"]*)(")')

    def __init__(self, path: Path) -> None:
        self.path = path

    def current(self) -> SemanticVersion:
        match = self.LINE.search(self.path.read_text(encoding="utf-8"))
        if match is None:
            raise ReleaseError(f"no __version__ assignment in {self.path}")
        return SemanticVersion.parse(match.group(2))

    def write(self, version: SemanticVersion) -> None:
        text = self.path.read_text(encoding="utf-8")
        updated = self.LINE.sub(lambda match: f"{match.group(1)}{version}{match.group(3)}", text, 1)
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            handle.write(updated)


class Git:
    def run(self, *args: str) -> str:
        done = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8")
        if done.returncode != 0:
            raise ReleaseError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
        return done.stdout.strip()

    def has_tag(self, tag: str) -> bool:
        return tag in self.run("tag", "--list", tag).split()

    def commit_and_tag(self, path: Path, version: SemanticVersion) -> None:
        self.run("add", str(path))
        self.run("commit", "-m", f"Release v{version}")
        self.run("tag", "-a", f"v{version}", "-m", f"codeangel {version}")


class ReleaseJob:
    def __init__(self, version_file: VersionFile, labels: str, release: bool) -> None:
        self.version_file = version_file
        self.level = ReleaseLevel(labels).pick()
        self.release = release
        self.git = Git()

    def run(self) -> SemanticVersion:
        version = self.version_file.current().bump(self.level)
        if self.release and self.git.has_tag(f"v{version}"):
            raise ReleaseError(f"tag v{version} already exists")
        self.version_file.write(version)
        if self.release:
            self.git.commit_and_tag(self.version_file.path, version)
        return version


class BumpCommandLine:
    DEFAULT_FILE = "src/codeangel/__init__.py"

    def parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="bump codeangel.__version__")
        parser.add_argument("--file", default=self.DEFAULT_FILE)
        parser.add_argument("--labels", default="")
        parser.add_argument("--release", action="store_true")
        return parser

    def main(self, argv: list[str]) -> int:
        args = self.parser().parse_args(argv)
        job = ReleaseJob(VersionFile(Path(args.file)), args.labels, args.release)
        try:
            version = job.run()
        except ReleaseError as error:
            print(f"bump_version: {error}", file=sys.stderr)
            return 1
        print(version)
        return 0


if __name__ == "__main__":
    sys.exit(BumpCommandLine().main(sys.argv[1:]))
