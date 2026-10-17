from codeangel.commands.add import AddCommand
from codeangel.commands.base import Command
from codeangel.commands.doctor import DoctorCommand
from codeangel.commands.init import InitCommand
from codeangel.commands.presets import PresetsCommand
from codeangel.commands.sync import SyncCommand
from codeangel.commands.update import UpdateCommand
from codeangel.commands.version import VersionCommand


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: list[Command] = [
            InitCommand(),
            AddCommand(),
            UpdateCommand(),
            SyncCommand(),
            DoctorCommand(),
            PresetsCommand(),
            VersionCommand(),
        ]

    def all(self) -> list[Command]:
        return list(self._commands)

    def by_name(self) -> dict[str, Command]:
        return {command.name: command for command in self._commands}
