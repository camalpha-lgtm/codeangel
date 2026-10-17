from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

SOURCE = Path("src/codeangel")
SAMPLE = "\n".join(
    [
        '"""module doc"""',
        "class Box:",
        '    """class doc"""',
        "    def run(self):",
        '        """function doc"""',
        "        # x",
        "        return 1",
        "",
    ]
)


def comment_tokens(source: str) -> list[str]:
    reader = io.StringIO(source).readline
    return [
        token.string for token in tokenize.generate_tokens(reader) if token.type == tokenize.COMMENT
    ]


def docstring_sites(source: str) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if ast.get_docstring(node) is not None:
                found.append(type(node).__name__)
    return found


def python_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.py")
        if path.is_file() and "payload" not in path.parts and "__pycache__" not in path.parts
    )


def style_offenders(root: Path) -> list[str]:
    offenders = []
    for path in python_files(root):
        source = path.read_text(encoding="utf-8")
        if comment_tokens(source) or docstring_sites(source):
            offenders.append(path.as_posix())
    return offenders


class TestNoComments:
    def test_source_has_no_comments_or_docstrings(self):
        assert style_offenders(SOURCE) == []

    def test_tests_have_no_comments_or_docstrings(self):
        assert style_offenders(Path("tests")) == []

    def test_detector_flags_comments_and_docstrings(self):
        assert comment_tokens(SAMPLE) == ["# x"]
        assert set(docstring_sites(SAMPLE)) == {"Module", "ClassDef", "FunctionDef"}


class TestRuffConfig:
    def test_enforces_complexity_and_dead_code_rules(self):
        text = Path("pyproject.toml").read_text(encoding="utf-8")
        for code in ("C90", "PLR0912", "PLR0915", "ERA"):
            assert code in text
