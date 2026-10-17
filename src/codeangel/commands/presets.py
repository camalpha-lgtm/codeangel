import argparse

from codeangel.commands.base import Command
from codeangel.install.presets import PresetCatalog
from codeangel.install.tree import PAYLOAD


class PresetsCommand(Command):
    name = "presets"
    help = "list area presets"

    def execute(self, args: argparse.Namespace) -> int:
        del args
        for preset in PresetCatalog(PAYLOAD.presets).listed():
            print(f"{preset.name:<14} {preset.meta.get('description', '')}")
        return 0
