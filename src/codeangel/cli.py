import argparse
import sys

from codeangel.commands import CommandRegistry
from codeangel.io.errors import CodeangelError

DESCRIPTION = """codeangel — install and maintain an agent-agnostic AI software factory in any repo.

  codeangel init    [--name N] [--base-branch B] [--python CMD] [--force]
  codeangel add     <preset> <area-path> [--name N] [--var key=value ...]
  codeangel update  [--force]
  codeangel sync    [--check]
  codeangel doctor
  codeangel presets
  codeangel version

Global: -C <dir> runs as if started in <dir>. Exit codes: 0 ok, 1 problems found, 2 usage error.
"""


class Application:
    def run(self, argv: list[str] | None = None) -> int:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        try:
            args = self._parser().parse_args(argv)
            return args.handler.execute(args)
        except CodeangelError as error:
            print(f"error: {error}")
            return 2

    def _parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="codeangel",
            description=DESCRIPTION,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "-C", dest="directory", default=".", help="run as if started in this dir"
        )
        commands = parser.add_subparsers(dest="command", required=True)
        for command in CommandRegistry().all():
            sub = commands.add_parser(command.name, help=command.help)
            command.configure(sub)
            sub.set_defaults(handler=command)
        return parser


def main(argv: list[str] | None = None) -> int:
    return Application().run(argv)


if __name__ == "__main__":
    sys.exit(main())
