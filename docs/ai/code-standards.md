# code standards

<!-- When: writing or reviewing codeangel Python, tests, or the harness. -->

- Object-oriented design under `src/codeangel/` except `payload/`: one class per responsibility, one command class per CLI sub-command, and no module-level function except `main`. Test helpers and pytest fixtures may be module-level functions.
- No single-line comments, no multi-line comments, and no docstrings under `src/codeangel/` (payload excluded) or `tests/`.
- Under `src/codeangel/` except `payload/`: no module over 300 lines, and no function or method body over 40 lines. No test file with more than two test classes. Shipped payload scripts are outside these size rules.
- `codeangel.__version__` is the only version. `pyproject.toml` derives its version from that attribute.
- Ruff enforces complexity (`C90`), branch count (`PLR0912`), statement count (`PLR0915`), and commented-out code (`ERA`).
- Gates: `uv run pytest` and `uv run ruff check src tests && uv run ruff format src tests`.
