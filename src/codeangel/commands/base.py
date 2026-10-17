import argparse


class Command:
    name = ""
    help = ""

    def configure(self, parser: argparse.ArgumentParser) -> None:
        return None

    def execute(self, args: argparse.Namespace) -> int:
        raise NotImplementedError(self.name)
