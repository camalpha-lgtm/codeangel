import argparse

from codeangel.commands.base import Command
from codeangel.install.installer import PresetInstaller


class AddCommand(Command):
    name = "add"
    help = "add an area from a preset"

    def configure(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("preset")
        parser.add_argument("path", help="area directory, repo-relative (e.g. backend)")
        parser.add_argument("--name", help="area name (default: last path segment)")
        parser.add_argument("--var", action="append", help="template variable override key=value")

    def execute(self, args: argparse.Namespace) -> int:
        return PresetInstaller().install(
            args.directory, args.preset, args.path, args.name, args.var
        )
