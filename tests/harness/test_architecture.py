from __future__ import annotations

import ast
from pathlib import Path

SOURCE = Path("src/codeangel")
COMMANDS = {"init", "add", "update", "sync", "doctor", "presets", "version"}


def source_files() -> list[Path]:
    return sorted(
        path for path in SOURCE.rglob("*.py") if "payload" not in path.parts and path.is_file()
    )


def parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"))


class TestObjectOrientedDesign:
    def test_only_main_is_a_module_level_function(self):
        offenders = []
        for path in source_files():
            for node in parse(path).body:
                if (
                    isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name != "main"
                ):
                    offenders.append(f"{path.as_posix()}:{node.name}")
        assert offenders == []

    def test_modules_stay_under_300_lines(self):
        offenders = [
            f"{path.as_posix()}:{len(path.read_text(encoding='utf-8').splitlines())}"
            for path in source_files()
            if len(path.read_text(encoding="utf-8").splitlines()) > 300
        ]
        assert offenders == []

    def test_functions_stay_under_40_lines(self):
        offenders = []
        for path in source_files():
            for node in ast.walk(parse(path)):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or not node.body:
                    continue
                length = node.end_lineno - node.body[0].lineno + 1
                if length > 40:
                    offenders.append(f"{path.as_posix()}:{node.name}:{length}")
        assert offenders == []

    def test_every_sub_command_has_a_command_class(self):
        from codeangel.commands import CommandRegistry
        from codeangel.commands.base import Command

        registry = CommandRegistry().by_name()
        assert set(registry) == COMMANDS
        assert all(isinstance(command, Command) for command in registry.values())


class TestTestLayout:
    def test_test_files_hold_at_most_two_test_classes(self):
        offenders = []
        for path in sorted(Path("tests").rglob("test_*.py")):
            classes = [
                node.name
                for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
                if isinstance(node, ast.ClassDef) and node.name.startswith("Test")
            ]
            if len(classes) > 2:
                offenders.append(f"{path.as_posix()}:{','.join(classes)}")
        assert offenders == []

    def test_legacy_monolithic_test_file_is_gone(self):
        assert not Path("tests/test_cli.py").exists()
