---
ticket: CAM-6
title: Refactor cli.py into modular OO code and version the repo for pinning
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-6/refactor-clipy-into-modular-oo-code-and-version-the-repo-for-pinning
branch: camerondhobbs/cam-6-refactor-clipy-code-make-sure-repo-versioned
base_sha: 4b2f760e3be33d8f9d44e1288b3252b0d4ee7d83
pr:
stage: REVIEW  # managed by transition.py — see stages.toml
last_status: unblocked  # exit status that entered the current stage
attempt: 2   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-17T11:09Z
updated: 2026-10-17T13:40Z
---

# CAM-6: Refactor cli.py into modular OO code and version the repo for pinning

## Ticket
**Title:** Refactor cli.py code, make sure repo versioned

Refactor cli.py code so it follows design patterns for object orientated programming. Can you update my AGENTS.md also so that it will always follow object orientated design patterns. Also disallow any code comments (multi/doc string and single line). Also update the tests to match the new file structure. Generally don't want too many test classes in a single file. Want good modularity and readableness of code, update harness to specify these things, and make it as deterministic as possible for good coding practices. Make sure repository is also versioned correctly so version can be locked in child projects

Comments: none.

Refined by build-loop STARTUP (Linear title/description rewritten; original kept as a Linear comment): title "Refactor cli.py into modular OO code and version the repo for pinning".

## Acceptance criteria
- [x] AC-1: `src/codeangel/cli.py` no longer holds the logic: it is a thin entry (argument parser + `main`) that dispatches to one `Command` class per sub-command (`init`, `add`, `update`, `sync`, `doctor`, `presets`, `version`); the logic lives in cohesive single-responsibility classes in separate modules (payload, templating, project/config, lock file, managed-file installer, shim sync, preset installer, doctor checks). Under `src/codeangel/` the only module-level function is `main`; no module exceeds 300 lines and no function exceeds 40 lines.
- [x] AC-2: Root `AGENTS.md` states that all code must follow object-oriented design patterns (and points at `docs/ai/code-standards.md`, which spells out the rules).
- [x] AC-3: Root `AGENTS.md` / `docs/ai/code-standards.md` disallow code comments of every kind (single-line, multi-line, docstrings), and no Python file under `src/codeangel/` (excluding `payload/`) or `tests/` contains a comment token or a docstring; a test fails on any.
- [x] AC-4: `tests/test_cli.py` is replaced by test files that mirror the new source layout (shared fixtures in `conftest.py` / one helper module), and no test file defines more than 2 test classes; a test enforces this.
- [x] AC-5: The harness carries the standards: the scaffold ships `docs/ai/code-standards.md` (OO design, no comments, small modules and test files, deterministic gates) and routes to it from its `AGENTS.md`; the managed `build-implement` skill requires following the project's code standards and `build-verify` V7 checks them; `docs/ai/agent-docs.md` documents where standards live; ruff is configured with complexity / statement-count / commented-out-code rules so the standards are tool-enforced where a tool can enforce them.
- [x] AC-6: The repository has one source of truth for its version (`codeangel.__version__`; `pyproject.toml` derives it dynamically) that a test keeps consistent with the `codeangel version` output and a SemVer pattern, and the README documents how a child project locks a version: install a release tag (`uv tool install git+https://github.com/camalpha-lgtm/codeangel@vX.Y.Z`), the recorded `[codeangel] version` in `.agents/codeangel.toml`, `codeangel doctor` warning on mismatch, and the release procedure (bump, tag `vX.Y.Z`) in `AGENTS.md`.
- [x] AC-7: CLI behaviour is unchanged (implied): every pre-existing end-to-end test passes with assertions unchanged (only moved / re-homed), and `init` → `add django-drf` → `doctor` still works on a generated project.

## Out of scope
- Changing CLI commands, flags, exit codes or user-visible output of `init`, `add`, `update`, `sync`, `doctor`, `presets`, `version`.
- Changing preset contents or stacks (`django-drf`, `expo`) and their commands.
- Rewriting or stripping comments in shipped payload code (`transition.py`, `sync-shims.py`, preset skeleton Python): it ships to child projects and is a separate change.
- Creating or pushing the `v0.1.0` git tag, publishing to PyPI, or bumping the version: the maintainer releases after merge.
- Adding a codeangel CI workflow that runs the tests / lint (tool-enforced locally via `uv run pytest` and ruff only).

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/cli.py | modify | shrink to argument-parser factory + `main`; dispatch to command classes; no comments / docstrings |
| src/codeangel/io/errors.py | create | `CodeangelError` |
| src/codeangel/install/tree.py | create | `PayloadTree` / `Payload`: payload roots, file listing, `dot_x` → `.x` path mapping |
| src/codeangel/io/templating.py | create | `TemplateRenderer`: `{{var}}` substitution, missing-variable error |
| src/codeangel/io/files.py | create | `TextFile` (LF writer) and `ContentDigest` (CRLF-normalised sha256) |
| src/codeangel/project/runtime.py | create | `PythonRuntime`: version probe, interpreter detection |
| src/codeangel/project/model.py | create | `Project`: root discovery, config loading, template variables, `package_name` |
| src/codeangel/install/lockfile.py | create | `Lockfile`: load / save managed-file hashes |
| src/codeangel/install/managed.py | create | `ManagedInstaller` + `InstallStatus`: created / unchanged / updated / conflict policy |
| src/codeangel/install/shims.py | create | `ShimSynchroniser`: runs `.agents/sync-shims.py` |
| src/codeangel/install/rows.py | create | `RowInserter`: marker-based row insertion into docs |
| src/codeangel/install/presets.py | create | `Preset` / `PresetCatalog`: preset metadata, variables, requirements |
| src/codeangel/install/installer.py | create | `PresetInstaller`: adoption, file copy, doc-map fragment, router rows, config block |
| src/codeangel/doctor/checks.py | create | `DoctorCheck` base + one class per check, `DoctorReport` |
| src/codeangel/io/__init__.py | create | `io` package marker |
| src/codeangel/project/__init__.py | create | `project` package marker |
| src/codeangel/install/__init__.py | create | `install` package marker |
| src/codeangel/doctor/__init__.py | create | `doctor` package marker |
| src/codeangel/commands/__init__.py | create | package marker + `CommandRegistry` |
| src/codeangel/commands/base.py | create | `Command` abstract base |
| src/codeangel/commands/init.py | create | `InitCommand` |
| src/codeangel/commands/add.py | create | `AddCommand` |
| src/codeangel/commands/update.py | create | `UpdateCommand` |
| src/codeangel/commands/sync.py | create | `SyncCommand` |
| src/codeangel/commands/doctor.py | create | `DoctorCommand` |
| src/codeangel/commands/presets.py | create | `PresetsCommand` |
| src/codeangel/commands/version.py | create | `VersionCommand` |
| src/codeangel/__init__.py | modify | stays the single source of the version; drop docstring |
| src/codeangel/__main__.py | modify | unchanged behaviour; keep comment-free |
| pyproject.toml | modify | dynamic version from `codeangel.__version__`; ruff rules C901 / PLR0912 / PLR0915 / ERA + mccabe limit; pytest `pythonpath` for test helpers |
| uv.lock | modify | only if uv re-locks after the pyproject change |
| tests/test_cli.py | delete | replaced by the split files below |
| tests/conftest.py | create | shared fixtures (`project`, `backend_project`, payload patching) |
| tests/support/__init__.py | create | shared helpers (`run`, `text_files`, `load_transition`, `PYTHON`) |
| tests/cli/test_init.py | create | `TestInit` (moved) |
| tests/cli/test_add.py | create | `TestAdd` (moved) |
| tests/cli/test_update.py | create | `TestUpdate` (moved) |
| tests/cli/test_sync.py | create | `TestSync` (moved from `TestSyncAndDoctor`) |
| tests/cli/test_doctor.py | create | `TestDoctor` (moved from `TestSyncAndDoctor`) |
| tests/cli/test_build_loop_script.py | create | `TestBuildLoopScript` (moved) |
| tests/harness/test_payload.py | create | `TestPayload` (moved) + `TestHarnessStandards` |
| tests/io/test_templating.py | create | `TestTemplateRenderer` unit tests |
| tests/install/test_payload_tree.py | create | `TestPayloadTree` unit tests |
| tests/install/test_managed_installer.py | create | `TestManagedInstaller` unit tests |
| tests/project/test_project.py | create | `TestProject` unit tests |
| tests/harness/test_code_style.py | create | `TestNoComments`, `TestRuffConfig`: no comments / docstrings, ruff rules present |
| tests/harness/test_architecture.py | create | `TestObjectOrientedDesign`, `TestTestLayout`: free-function, module-size, function-size, test-class-count limits |
| tests/cli/test_versioning.py | create | `TestVersioning`: single version source, SemVer, README pinning docs |
| AGENTS.md | modify | Layout table (new modules / tests), `## Code standards` (OO, no comments, limits), versioning + release procedure, Done gate adds standards tests |
| docs/ai/code-standards.md | create | codeangel's own standards: OO design patterns, no comments, size limits, deterministic gates |
| docs/ai/repo-map.md | modify | rows for `src/codeangel/`, `tests/`, `docs/ai/code-standards.md` |
| docs/ai/doc-map.toml | modify | rules mapping `src/codeangel/**/*.py`, `tests/*`, `pyproject.toml` to AGENTS.md / README.md / code-standards.md |
| README.md | modify | "Pin a version" section, develop section (layout of code + tests, standards) |
| src/codeangel/payload/scaffold/docs/ai/code-standards.md | create | project-owned code-standards doc for child projects (language-agnostic defaults) |
| src/codeangel/payload/scaffold/AGENTS.md | modify | router row + one Always line pointing at `docs/ai/code-standards.md` (stay ≤ 50 lines) |
| src/codeangel/payload/managed/dot_agents/skills/build-implement/SKILL.md | modify | follow the project's code standards while implementing |
| src/codeangel/payload/managed/dot_agents/skills/build-verify/SKILL.md | modify | V7 hygiene checks the project's code standards |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | document that code standards live in root `AGENTS.md` + `docs/ai/code-standards.md` and how gates enforce them |
| .agents/skills/build-implement/SKILL.md | modify | installed copy refreshed by `codeangel update` |
| .agents/skills/build-verify/SKILL.md | modify | installed copy refreshed by `codeangel update` |
| docs/ai/agent-docs.md | modify | installed copy refreshed by `codeangel update` |
| .agents/codeangel.lock.json | modify | managed-file hashes after `codeangel update` |
| .claude/skills/build-implement/SKILL.md | modify | regenerated shim (`sync-shims.py`) if the skill body / frontmatter changed |
| .claude/skills/build-verify/SKILL.md | modify | regenerated shim (`sync-shims.py`) if the skill body / frontmatter changed |
| docs/specs/CAM-6.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/harness/test_architecture.py::TestObjectOrientedDesign::test_only_main_is_a_module_level_function | AC-1 | AST of every `src/codeangel/**/*.py` (excluding `payload/`) has no module-level `def` other than `main` |
| tests/harness/test_architecture.py::TestObjectOrientedDesign::test_modules_stay_under_300_lines | AC-1 | no source module exceeds 300 lines |
| tests/harness/test_architecture.py::TestObjectOrientedDesign::test_functions_stay_under_40_lines | AC-1 | no function / method body exceeds 40 lines |
| tests/harness/test_architecture.py::TestObjectOrientedDesign::test_every_sub_command_has_a_command_class | AC-1 | `CommandRegistry` exposes one `Command` subclass per sub-command name |
| tests/harness/test_architecture.py::TestTestLayout::test_test_files_hold_at_most_two_test_classes | AC-4 | no `tests/**/test_*.py` defines more than 2 `Test*` classes |
| tests/harness/test_architecture.py::TestTestLayout::test_legacy_monolithic_test_file_is_gone | AC-4 | `tests/test_cli.py` does not exist |
| tests/harness/test_code_style.py::TestNoComments::test_source_has_no_comments_or_docstrings | AC-3 | tokenize / ast over `src/codeangel/**/*.py` (excluding `payload/`) finds no COMMENT token and no docstring |
| tests/harness/test_code_style.py::TestNoComments::test_tests_have_no_comments_or_docstrings | AC-3 | same scan over `tests/**/*.py` finds none |
| tests/harness/test_code_style.py::TestNoComments::test_detector_flags_comments_and_docstrings | AC-3 | the scanner reports a `# x` comment and a function / module / class docstring in sample source (so the gate cannot pass vacuously) |
| tests/harness/test_code_style.py::TestRuffConfig::test_enforces_complexity_and_dead_code_rules | AC-5 | `pyproject.toml` ruff `select` contains `C90`, `PLR0912`, `PLR0915`, `ERA` |
| tests/harness/test_payload.py::TestHarnessStandards::test_agents_md_requires_object_oriented_design | AC-2 | root `AGENTS.md` mentions object-oriented design patterns and links `docs/ai/code-standards.md` |
| tests/harness/test_payload.py::TestHarnessStandards::test_code_standards_doc_forbids_all_comment_kinds | AC-3 | `docs/ai/code-standards.md` forbids single-line comments, multi-line comments and docstrings |
| tests/harness/test_payload.py::TestHarnessStandards::test_scaffold_ships_code_standards_and_routes_to_it | AC-5 | a freshly `init`ed project has `docs/ai/code-standards.md` and its `AGENTS.md` router names it, `AGENTS.md` ≤ 50 lines |
| tests/harness/test_payload.py::TestHarnessStandards::test_build_stages_reference_code_standards | AC-5 | managed `build-implement` and `build-verify` skills name the code standards; the payload stays project-agnostic |
| tests/cli/test_versioning.py::TestVersioning::test_version_is_semver | AC-6 | `codeangel.__version__` matches `MAJOR.MINOR.PATCH` |
| tests/cli/test_versioning.py::TestVersioning::test_pyproject_derives_version_from_package | AC-6 | `pyproject.toml` has `dynamic = ["version"]`, no static `version`, and `tool.setuptools.dynamic.version.attr = "codeangel.__version__"` |
| tests/cli/test_versioning.py::TestVersioning::test_version_command_prints_package_version | AC-6 | `codeangel version` prints `codeangel <__version__>` and exits 0 |
| tests/cli/test_versioning.py::TestVersioning::test_project_config_records_the_installed_version | AC-6 | after `init` and `update`, `[codeangel] version` in `.agents/codeangel.toml` and the lock file equal `__version__` |
| tests/cli/test_versioning.py::TestVersioning::test_readme_documents_pinning_to_a_release_tag | AC-6 | README contains the `@v` pin install command and AGENTS.md documents the release procedure (`vX.Y.Z` tag) |
| tests/io/test_templating.py::TestTemplateRenderer::test_substitutes_known_variables | AC-1 | `{{a}}` replaced with its value |
| tests/io/test_templating.py::TestTemplateRenderer::test_unknown_variable_raises_codeangel_error | AC-1 | missing variable → `CodeangelError` naming it and the location |
| tests/install/test_payload_tree.py::TestPayloadTree::test_dot_prefixed_parts_install_as_hidden_paths | AC-1 | `dot_agents/x` → `.agents/x` |
| tests/install/test_payload_tree.py::TestPayloadTree::test_files_skip_bytecode_caches | AC-1 | `__pycache__` entries are not listed, result is sorted |
| tests/install/test_managed_installer.py::TestManagedInstaller::test_creates_missing_file | AC-1 | status `created`, hash returned |
| tests/install/test_managed_installer.py::TestManagedInstaller::test_locally_edited_file_becomes_a_new_proposal | AC-1 | status `conflict`, `.codeangel-new` written, original untouched, locked hash kept |
| tests/install/test_managed_installer.py::TestManagedInstaller::test_force_overwrites_a_conflict | AC-1 | status `updated`, content replaced |
| tests/project/test_project.py::TestProject::test_find_root_walks_up_to_the_config | AC-1 | `Project.discover` from a subdir returns the dir holding `.agents/codeangel.toml` |
| tests/project/test_project.py::TestProject::test_missing_config_is_a_codeangel_error | AC-1 | no config anywhere → `CodeangelError` mentioning `codeangel init` |
| tests/project/test_project.py::TestProject::test_package_name_is_a_valid_identifier | AC-1 | `"9 My-App"` → `p_9_my_app` |
| tests/cli/test_init.py::TestInit::test_lock_covers_every_managed_file | AC-7 | moved test: lock file lists exactly the shipped managed files |
| tests/cli/test_init.py::TestInit::test_project_files_are_never_overwritten | AC-7 | moved test: existing README / AGENTS.md survive `init` |
| tests/cli/test_add.py::TestAdd::test_django_drf_creates_a_runnable_skeleton_and_wires_docs | AC-7 | moved test: `add django-drf` output files and doc wiring unchanged |
| tests/cli/test_add.py::TestAdd::test_expo_adopts_the_generators_agents_md | AC-7 | moved test: adoption flow unchanged, `doctor` still 0 |
| tests/cli/test_update.py::TestUpdate::test_never_overwrites_local_edits | AC-7 | moved test: local edit kept, proposal written |
| tests/cli/test_doctor.py::TestDoctor::test_doctor_passes_on_a_fresh_project | AC-7 | moved test: `doctor` exits 0 on `init` + `add django-drf` |
| tests/cli/test_sync.py::TestSync::test_sync_check_detects_and_fixes_drift | AC-7 | moved test: `sync --check` 1 → `sync` 0 → `sync --check` 0 |

## Docs impact
| doc | status | note |
|---|---|---|
| README.md | updated | Pin-a-version section (release-tag install) and the develop section's module / test layout |
| docs/ai/repo-map.md | updated | Rows for `src/codeangel/`, `tests/`, and `docs/ai/code-standards.md` |
| AGENTS.md | updated | Layout, code-standards pointer, version / release procedure, Done gate |
| docs/ai/code-standards.md | updated | New standards: OO design, no comments, size limits, deterministic gates |
| docs/ai/doc-map.toml | updated | Map `src/codeangel/**/*.py`, `tests/*`, and `pyproject.toml` to the docs that describe them |
| docs/ai/agent-docs.md | updated | Code standards live in root `AGENTS.md` and `docs/ai/code-standards.md`, enforced by the gates |
| docs/ai/git-workflow.md | unchanged | No workflow change; a codeangel CI workflow is out of scope |
| docs/ai/product.md | unchanged | What the product is does not change |
| docs/learnings/README.md | unchanged | No new learning in this plan |
| docs/learnings/tooling.md | unchanged | Existing worktree lesson still holds; this change does not alter it |

## Risks / open questions
- [non-blocking] REVIEW blocked: gh missing / unauthenticated. Install the GitHub CLI and authenticate before the review stage can open a PR.
- [non-blocking] Root `AGENTS.md` is 30 lines against a 50-line budget. Standards detail belongs in `docs/ai/code-standards.md` so `doctor` does not warn.
- [non-blocking] `README.md` is 65 lines against the ~60-line guide in `docs/ai/agent-docs.md`. The pin section has to stay short.
- [non-blocking] Managed skill text must stay free of product, framework, and package-manager names or the payload agnosticism test fails.
- [non-blocking] `src/codeangel/cli.py` is 567 lines; `cmd_add` and `cmd_doctor` are each well over 40 lines. The split has to preserve CLI output so the moved end-to-end tests still pass.

## Baseline
- base_sha: 4b2f760e3be33d8f9d44e1288b3252b0d4ee7d83
- gates: root (no `[[areas]]`; gates from root `AGENTS.md` `## Done`): `uv run pytest` → exit 0, 31 passed, 0 failed; `uv run ruff check src tests` → exit 0; `uv run ruff format --check src tests` → exit 0, 24 files already formatted. No collection or build errors.
- known failures: none
- lint debt: none
- schema drift: none: this repo has no schema or migrations

## Plan amendments
- 2026-10-17T12:35Z Ruff ignores C901 under `src/codeangel/payload/**` — `transition.py` is already over the complexity cap, and rewriting shipped payload scripts is out of scope.
- 2026-10-17T13:15Z Group the flat modules into `commands`, `doctor`, `install`, `io`, and `project`, and mirror that under `tests/`. The user rejected a single top-level pile of files. Behaviour and acceptance criteria stay the same; only paths move. The class-count scan uses `tests/**/test_*.py`.

## Verify reports
### Attempt 1 — FAIL
- V1 lint/format: PASS — `uv run ruff check src tests` exit 0; `uv run ruff format --check src tests` exit 0, 62 files already formatted, no file modified.
- V2 migrations: PASS — no schema or migrations in this repo (baseline: none).
- V3 full suite: PASS — `uv run pytest` 60 passed, 0 failed; baseline was 31 passed, 0 failed; no new failure; no ticket test failed.
- V4 planned tests: PASS — every Test plan node id exists and passed inside that suite.
- V5 AC audit: FAIL — AC-1 through AC-5 and AC-7 are asserted by their planned tests and match the code. AC-6 is not: the pinning test does not assert the recorded `[codeangel] version` or the doctor mismatch warning.
- V6 scope audit: PASS — changed and untracked paths ⊆ Affected files + this spec. Preset trees, payload scripts, CLI flags, and CI workflows were not changed. Moved end-to-end assertions match the baseline tests.
- V7 hygiene: FAIL — `docs/ai/code-standards.md` forbids every module-level function except `main` and every module over 300 lines, with no `payload/` exclusion. The diff adds module-level helpers under `tests/`, and shipped `transition.py` is 698 lines with two function bodies over 40 lines.
- V8 docs in sync: FAIL — `docs_synced` ✓. `docs/ai/repo-map.md` says one class per module; several modules define more than one. `docs/ai/code-standards.md` states size rules the tree does not meet. Unchanged reasons for git-workflow, product, and learnings hold. README pin command, AGENTS.md release line, and `VersionCheck` agree with each other.
- Failure excerpt / root cause / next action:
  - V5 `tests/test_versioning.py` only checks `codeangel@v` and `vX.Y.Z`:
    ```
    def test_readme_documents_pinning_to_a_release_tag(self):
        assert "codeangel@v" in readme
        assert "vX.Y.Z" in agents
    ```
    AC-6 also requires the README to document `[codeangel] version` in `.agents/codeangel.toml` and `codeangel doctor` warning on mismatch. Those sentences are in `README.md` and `VersionCheck` warns, but no test asserts them.
  - V7 `docs/ai/code-standards.md`: "no module-level function except `main`"; "No module over 300 lines. No function or method body over 40 lines." `tests/support.py` defines `run` and other helpers. `transition.py` is 698 lines; `main` and `cmd_go` bodies are 54 lines. Out of scope forbids rewriting that script. The architecture tests exclude `payload/`.
  - V8 `docs/ai/repo-map.md`: "`src/codeangel/` | CLI package: one class per module". `doctor_checks.py` defines 13 classes; `files.py`, `payload_tree.py`, `preset.py`, and `project.py` each define two. The spec puts those classes in those modules.
  - Next action: extend `test_readme_documents_pinning_to_a_release_tag` so it asserts the release-tag install command, the recorded `[codeangel] version`, and the doctor mismatch warning (and keep the `vX.Y.Z` release line). Scope the code-standards size and module-level-function rules to `src/codeangel/` excluding `payload/`, matching AC-1 and the architecture tests; leave `tests/support.py` helpers and pytest fixtures. Correct the repo-map row so it does not say one class per module. Do not rewrite payload scripts.

### Attempt 2 — PASS
- V1 lint/format: PASS — `uv run ruff check src tests` exit 0; `uv run ruff format --check src tests` exit 0, 62 files already formatted, no file modified.
- V2 migrations: PASS — no schema or migrations in this repo (baseline: none).
- V3 full suite: PASS — `uv run pytest` 60 passed, 0 failed; baseline was 31 passed, 0 failed; no new failure; no ticket test failed.
- V4 planned tests: PASS — all 36 Test plan node ids collect and passed inside that suite.
- V5 AC audit: PASS
  - AC-1: `tests/test_architecture.py::TestObjectOrientedDesign::test_only_main_is_a_module_level_function`; `tests/test_architecture.py:21` (also `:32`, `:40`, `:51`); `src/codeangel/cli.py:49` dispatches `CommandRegistry`; unit outcomes in `tests/test_templating.py:10`, `tests/test_payload_tree.py:9`, `tests/test_managed_installer.py:10`, `tests/test_project.py:12`.
  - AC-2: `tests/test_payload.py::TestHarnessStandards::test_agents_md_requires_object_oriented_design`; `tests/test_payload.py:46`; `AGENTS.md:30`.
  - AC-3: `tests/test_code_style.py::TestNoComments::test_source_has_no_comments_or_docstrings`; `tests/test_code_style.py:57` (tests `:60`, detector `:63`); `tests/test_payload.py::TestHarnessStandards::test_code_standards_doc_forbids_all_comment_kinds`; `tests/test_payload.py:51`.
  - AC-4: `tests/test_architecture.py::TestTestLayout::test_test_files_hold_at_most_two_test_classes`; `tests/test_architecture.py:61`; legacy file `:73`.
  - AC-5: `tests/test_payload.py::TestHarnessStandards::test_scaffold_ships_code_standards_and_routes_to_it`; `tests/test_payload.py:57`; skills `:66`; `tests/test_code_style.py::TestRuffConfig::test_enforces_complexity_and_dead_code_rules`; `tests/test_code_style.py:69`.
  - AC-6: `tests/test_versioning.py::TestVersioning::test_readme_documents_pinning_to_a_release_tag`; `tests/test_versioning.py:41` (SemVer `:14`, dynamic version `:17`, CLI print `:23`, recorded version `:27`). `VersionCheck` warns when `[codeangel] version` disagrees (`src/codeangel/doctor_checks.py:34`).
  - AC-7: `tests/test_doctor.py::TestDoctor::test_doctor_passes_on_a_fresh_project`; `tests/test_doctor.py:9`. Moved end-to-end assertions match the baseline tests (imports and the removed comment only).
- V6 scope audit: PASS — changed and untracked paths ⊆ Affected files + this spec. Preset trees, payload scripts, CLI flags, and CI workflows were not changed. Help strings match the baseline parser.
- V7 hygiene: PASS — no debug output, breakpoints, commented-out code, bare TODOs, secrets, or machine-specific paths in the diff. `docs/ai/code-standards.md` scopes module-level functions and size limits to `src/codeangel/` excluding `payload/`, and allows test helpers. Architecture and comment tests pass on that tree. `C901` is ignored only under `payload/`, as the plan amendment records.
- V8 docs in sync: PASS — `docs_synced` ✓. README pin command, `[codeangel] version`, and the doctor mismatch warning match `VersionCheck`. `AGENTS.md` release line is `vX.Y.Z`. `docs/ai/repo-map.md` says related types share a module. `docs/ai/code-standards.md` matches the enforced scope. `docs/ai/agent-docs.md` matches the payload copy. Unchanged reasons for git-workflow, product, and learnings hold. `codeangel doctor` on this repo: 0 problems, 0 warnings.

### Attempt 2 — FAIL
- V1 lint/format: PASS — `uv run ruff check src tests` exit 0; `uv run ruff format --check src tests` exit 0, 66 files already formatted, no file modified.
- V2 migrations: PASS — no schema or migrations in this repo (baseline: none).
- V3 full suite: PASS — `uv run pytest` 60 passed, 0 failed; baseline was 31 passed, 0 failed; no new failure; no ticket test failed.
- V4 planned tests: PASS — all 36 Test plan node ids collect and passed inside that suite.
- V5 AC audit: PASS — AC-1 `tests/harness/test_architecture.py:21` (`cli.py:49` dispatches `CommandRegistry`); AC-2 `tests/harness/test_payload.py:46`; AC-3 `tests/harness/test_code_style.py:57` and `tests/harness/test_payload.py:51`; AC-4 `tests/harness/test_architecture.py:61`; AC-5 `tests/harness/test_payload.py:57` and `tests/harness/test_code_style.py:69`; AC-6 `tests/cli/test_versioning.py:41` (`VersionCheck` warns at `src/codeangel/doctor/checks.py:34`); AC-7 `tests/cli/test_doctor.py:9`. Moved assertions re-home helpers only (`Lockfile`, `ContentDigest`, `ManagedInstaller.NEW_SUFFIX`).
- V6 scope audit: PASS — changed and untracked paths ⊆ Affected files + this spec. Preset trees, payload scripts, CLI help strings, flags, and CI workflows were not changed. `.claude` shims still point at the canonical skills; `codeangel doctor` reports shims in sync.
- V7 hygiene: PASS — no debug output, breakpoints, commented-out code, bare TODOs, secrets, or machine-specific paths. `docs/ai/code-standards.md` scopes module-level functions and size limits to `src/codeangel/` excluding `payload/`, and allows test helpers. Architecture and comment tests pass. `C901` is ignored only under `payload/`, as the plan amendment records. `uv.lock` only drops the static package version.
- V8 docs in sync: FAIL — `docs_synced` ✓. Pin command, `[codeangel] version`, doctor mismatch warning, and `vX.Y.Z` match `VersionCheck` and `AGENTS.md`. `docs/ai/code-standards.md` matches the enforced scope. `docs/ai/agent-docs.md` matches the payload copy. Unchanged reasons for git-workflow, product, and learnings hold. `codeangel doctor` on this repo: 0 problems, 0 warnings. README and repo-map mis-state the test layout.
- Failure excerpt / root cause / next action:
  - V8 `README.md:66` and `docs/ai/repo-map.md:8`:
    ```
    Tests under `tests/` use the same package names.
    | `tests/` | test packages mirror that layout; at most two test classes per file |
    ```
    Source packages are `commands`, `doctor`, `install`, `io`, `project`. Test packages are `cli`, `install`, `io`, `project`, `harness`, and `support`. There is no `tests/commands` or `tests/doctor`.
  - Root cause: after the package regroup, those two docs still say the test tree copies the source package names.
  - Next action: name the real test packages in `README.md` and `docs/ai/repo-map.md`. Leave the directories as the affected-files table specifies (`tests/cli` for command tests, `tests/harness` for standards tests).

### Attempt 3 — PASS
- V1 lint/format: PASS — `uv run ruff check src tests` exit 0; `uv run ruff format --check src tests` exit 0, 66 files already formatted, no file modified.
- V2 migrations: PASS — no schema or migrations in this repo (baseline: none).
- V3 full suite: PASS — `uv run pytest` 60 passed, 0 failed; baseline was 31 passed, 0 failed; no new failure; no ticket test failed.
- V4 planned tests: PASS — all 36 Test plan node ids exist and passed inside that suite.
- V5 AC audit: PASS
  - AC-1: `tests/harness/test_architecture.py::TestObjectOrientedDesign::test_only_main_is_a_module_level_function`; `tests/harness/test_architecture.py:21` (modules `:32`, functions `:40`, commands `:51`); `src/codeangel/cli.py:42` registers `CommandRegistry` and `:50` calls `Application.run`; unit outcomes in `tests/io/test_templating.py:10`, `tests/install/test_payload_tree.py:9`, `tests/install/test_managed_installer.py:10`, `tests/project/test_project.py:12`.
  - AC-2: `tests/harness/test_payload.py::TestHarnessStandards::test_agents_md_requires_object_oriented_design`; `tests/harness/test_payload.py:46`; `AGENTS.md:30`.
  - AC-3: `tests/harness/test_code_style.py::TestNoComments::test_source_has_no_comments_or_docstrings`; `tests/harness/test_code_style.py:57` (tests `:60`, detector `:63`); `tests/harness/test_payload.py::TestHarnessStandards::test_code_standards_doc_forbids_all_comment_kinds`; `tests/harness/test_payload.py:51`.
  - AC-4: `tests/harness/test_architecture.py::TestTestLayout::test_test_files_hold_at_most_two_test_classes`; `tests/harness/test_architecture.py:61`; legacy file `:73`.
  - AC-5: `tests/harness/test_payload.py::TestHarnessStandards::test_scaffold_ships_code_standards_and_routes_to_it`; `tests/harness/test_payload.py:57`; skills `:66`; `tests/harness/test_code_style.py::TestRuffConfig::test_enforces_complexity_and_dead_code_rules`; `tests/harness/test_code_style.py:69`.
  - AC-6: `tests/cli/test_versioning.py::TestVersioning::test_readme_documents_pinning_to_a_release_tag`; `tests/cli/test_versioning.py:41` (SemVer `:14`, dynamic version `:17`, CLI print `:23`, recorded version `:27`). `VersionCheck` warns when `[codeangel] version` disagrees (`src/codeangel/doctor/checks.py:34`).
  - AC-7: `tests/cli/test_doctor.py::TestDoctor::test_doctor_passes_on_a_fresh_project`; `tests/cli/test_doctor.py:9`. Moved end-to-end tests keep the baseline method names and assertions.
- V6 scope audit: PASS — changed and untracked paths ⊆ Affected files + this spec. Preset trees, payload scripts, CLI help strings, flags, and CI workflows were not changed. `.claude` shims were not regenerated; `codeangel doctor` reports shims in sync.
- V7 hygiene: PASS — no debug output, breakpoints, commented-out code, bare TODOs, secrets, or machine-specific paths. `docs/ai/code-standards.md` scopes module-level functions and size limits to `src/codeangel/` excluding `payload/`, and allows test helpers. Architecture and comment tests pass. `C901` is ignored only under `payload/`, as the plan amendment records. `uv.lock` only drops the static package version.
- V8 docs in sync: PASS — `docs_synced` ✓. README, `AGENTS.md`, and `docs/ai/repo-map.md` name source packages `commands`, `doctor`, `install`, `io`, `project` and test packages `cli`, `install`, `io`, `project`, `harness`, `support`. Pin command, `[codeangel] version`, doctor mismatch warning, and `vX.Y.Z` match `VersionCheck` and `AGENTS.md`. `docs/ai/code-standards.md` matches the enforced scope. `docs/ai/agent-docs.md` matches the payload copy. Unchanged reasons for git-workflow, product, and learnings hold. `codeangel doctor` on this repo: 0 problems, 0 warnings.

## Review
- PR: <url>
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
- 2026-10-17T11:09Z STARTUP → PLAN [init] attempt=0/5 — mode=plan, branch=camerondhobbs/cam-6-refactor-clipy-code-make-sure-repo-versioned, base=4b2f760e3b
- 2026-10-17T12:15Z PLAN → AWAITING_APPROVAL [planned] attempt=0/5
- 2026-10-17T12:17Z AWAITING_APPROVAL → IMPLEMENT [approved] attempt=0/5
- 2026-10-17T12:31Z IMPLEMENT → VERIFY [implemented] attempt=0/5
- 2026-10-17T12:40Z VERIFY → IMPLEMENT [fail] attempt=1/5 — V5,V7,V8: AC-6 pinning test does not assert the recorded version or doctor mismatch warning; code-standards.md size and module-level-function rules are unscoped; repo-map claims one class per module
- 2026-10-17T12:41Z IMPLEMENT → VERIFY [implemented] attempt=1/5
- 2026-10-17T12:47Z VERIFY → REVIEW [pass] attempt=1/5
- 2026-10-17T12:47Z REVIEW → BLOCKED [blocked] attempt=1/5 — install the GitHub CLI (https://cli.github.com) and run gh auth login
- 2026-10-17T13:19Z BLOCKED → VERIFY [layout] attempt=1/5 — package layout replan is in the tree; user ordered verify before review
- 2026-10-17T13:24Z VERIFY → IMPLEMENT [fail] attempt=2/5 — V8: README and repo-map say test packages copy the source package names; tests are cli, install, io, project, harness, and support
- 2026-10-17T13:25Z IMPLEMENT → VERIFY [implemented] attempt=2/5
- 2026-10-17T13:29Z VERIFY → REVIEW [pass] attempt=2/5
- 2026-10-17T13:29Z REVIEW → BLOCKED [blocked] attempt=2/5 — install the GitHub CLI (https://cli.github.com) and run gh auth login
- 2026-10-17T13:40Z BLOCKED → REVIEW [unblocked] attempt=2/5 — gh auth login succeeded for camalpha-lgtm
