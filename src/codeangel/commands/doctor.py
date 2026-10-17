import argparse
from pathlib import Path

from codeangel.commands.base import Command
from codeangel.doctor.checks import Doctor
from codeangel.project.model import Project


class DoctorCommand(Command):
    name = "doctor"
    help = "validate the whole setup"

    def execute(self, args: argparse.Namespace) -> int:
        project = Project.discover(Path(args.directory).resolve())
        return Doctor(project).run()
