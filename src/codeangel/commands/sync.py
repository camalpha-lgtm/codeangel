import argparse
from pathlib import Path

from codeangel.commands.base import Command
from codeangel.install.shims import ShimSynchroniser
from codeangel.project.model import Project


class SyncCommand(Command):
    name = "sync"
    help = "regenerate Claude Code skill shims"

    def configure(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--check", action="store_true", help="report drift, change nothing")

    def execute(self, args: argparse.Namespace) -> int:
        root = Project.discover(Path(args.directory).resolve()).root
        return ShimSynchroniser().run(root, args.check)
