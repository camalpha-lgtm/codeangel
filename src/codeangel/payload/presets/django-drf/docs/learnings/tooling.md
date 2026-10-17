# {{area_name}} tooling

<!-- When: poetry, prek, ruff, or env trouble in {{area}}/. Git / worktree / gh: docs/learnings/tooling.md. -->

- **Each git worktree needs its own poetry venv: `poetry env use <python3.12 exe>` → `poetry install`.** — poetry keys venvs by project path, so a fresh worktree has none; if the machine default `python` is too old, poetry refuses ("unable to find a compatible version"). src: codeangel seed
- **`manage.py check` (the prek django hook) never detects schema drift → also run `makemigrations --check --dry-run`.** — src: codeangel seed
- **prek only sees files under `{{area}}/`.** — its config lives in `{{area}}/.pre-commit-config.yaml`; docs elsewhere are covered by build-loop's doc hygiene check. src: codeangel seed
- **The prek ruff hooks run `poetry run ruff`, so hooks and the CLI share one version.** — a pre-commit-managed ruff pinned in the config can drift from the poetry-locked one and report different findings. src: codeangel seed
- **`poetry -C <worktree>/{{area}} env remove --all` before deleting a worktree.** — the venv name hashes the project path; once the dir is gone the venv is orphaned in poetry's cache. worktree-cleanup runs this via `[[areas]] pre_remove`. src: codeangel seed
- **Keep CI's poetry version equal to the local one (`.github/workflows/{{area_name}}.yml`).** — the lock-file format differs between poetry major versions. src: codeangel seed
