# AGENTS.md — codeangel

<!-- Agent-facing. Budget ≤ 50 lines. -->

codeangel is a Python CLI (stdlib only, Python ≥ 3.11) that installs an agent-agnostic AI setup — skills, an enforced build-loop state machine, agent docs — into other repos. Humans: `README.md`.

## Layout
| path | what |
|---|---|
| `src/codeangel/` | packages `commands`, `doctor`, `install`, `io`, `project`; `cli.py` is `main` |
| `src/codeangel/payload/managed/` | files installed into projects and kept current by `update` (skills, `sync-shims.py`, `build-verifier`, `docs/ai/agent-docs.md`, the MCP configs `.mcp.json` and `.cursor/mcp.json`) |
| `src/codeangel/payload/scaffold/` | project-owned files created once at `init` (AGENTS.md, README, docs, config, CI) |
| `src/codeangel/payload/presets/<name>/` | one area preset: `_preset.toml` (metadata), `_doc-map.toml` (rules appended to the project doc map), `_root/` (files for the repo root, e.g. CI), the rest installs inside the area dir |
| `tests/` | `cli`, `install`, `io`, `project`, `harness`, `support` |

## Payload rules
- A path part `dot_x` installs as `.x`; `{{name}}` (lowercase identifier) in a path or file is a template variable: `project_name`, `project_package`, `base_branch`, `python`, `python_toml`, `codeangel_version`, and for presets `area`, `area_name`, plus `[vars]`.
- `managed/` is project-agnostic: no framework, package manager, or product names (a test enforces it). Project specifics belong in `.codeangel/codeangel.toml` or an area's `AGENTS.md` → `## Done`.
- Skills follow the Agent Skills spec; harness-only frontmatter goes in `metadata` as `claude-<field>`; `sync-shims.py` turns that into the Claude shim.
- Editing a managed file changes what `codeangel update` ships. Projects keep local edits; they get the new version as `<file>.codeangel-new`.
- Presets name only their own stack. Verify every preset's commands by running them in a generated project before shipping.

## Commands
- Setup: `uv sync` (creates `.venv`, installs the `dev` group). Run everything through `uv run`.
- Tests: `uv run pytest` (stdlib + pytest only; tests set up projects under `tmp_path`).
- Lint / format: `uv run ruff check src tests && uv run ruff format src tests` (the payload's `presets/` are excluded).
- Try it: `uv run codeangel -C <dir> doctor`.

## Code standards
Object-oriented design for all code. No single-line comments, multi-line comments, or docstrings. Detail: `docs/ai/code-standards.md`.

## Version
`codeangel.__version__` is the version (`pyproject.toml` reads it). Release: bump that value, tag `vX.Y.Z`.

## Done
Tests pass · ruff clean · standards tests pass · a preset change was exercised in a generated project (`init` → `add` → the area's own gates) · README / this file updated if commands, layout, or payload rules changed.
