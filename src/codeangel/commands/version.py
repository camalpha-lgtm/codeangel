import argparse

from codeangel import __version__
from codeangel.commands.base import Command


class VersionCommand(Command):
    name = "version"
    help = "print the version"

    def execute(self, args: argparse.Namespace) -> int:
        del args
        print(f"codeangel {__version__}")
        return 0
