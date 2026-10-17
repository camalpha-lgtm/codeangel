---
ticket: CAM-10
title: Rename the installed .agents folder to .codeangel
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-10/rename-the-installed-agents-folder-to-codeangel
branch: camerondhobbs/cam-10-rename-agents-to-codeangel
base_sha: 87a707d5c869eccdf432c835de1f311b82e0d979
pr:
stage: IMPLEMENT  # managed by transition.py — see stages.toml
last_status: planned  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-17T15:14Z
updated: 2026-10-17T15:15Z
---

# CAM-10: Rename the installed .agents folder to .codeangel

## Ticket
**Title:** Rename .agents to .codeangel

.agents should be a .codeangel folder that gets installed instead for children projects.

Also update it for the current codeangel repo in this PR too.

Comments: none.

Refined by build-loop STARTUP (Linear title/description rewritten; original kept as a Linear comment): title "Rename the installed .agents folder to .codeangel".

## Acceptance criteria
- [ ] AC-1: `codeangel init` installs the managed skills, `sync-shims.py`, `codeangel.toml` and `codeangel.lock.json` under `.codeangel/` in a child project and creates no `.agents/` folder; `add`, `update`, `sync` and `doctor` read and write only `.codeangel/` paths (payload sources are `dot_codeangel/`, the `dot_x` → `.x` mapping is unchanged).
- [ ] AC-2: This repo's own `.agents/` folder is renamed to `.codeangel/` in this PR: `.agents/` no longer exists, `.codeangel/` holds the config, lock file, skills and `sync-shims.py`, the lock file keys are `.codeangel/...` paths, the Claude shims under `.claude/skills/` are regenerated to point at `.codeangel/`, and `codeangel doctor` and `sync --check` pass on the repo.
- [ ] AC-3: No file under `src/`, `tests/`, `.codeangel/`, `.claude/`, `.github/`, `README.md`, `AGENTS.md` or `docs/ai/` names the old `.agents` folder or the `dot_agents` payload directory: every path, instruction, doc line, CI step and message points at `.codeangel`. `AGENTS.md` (the root agent-instructions file) and `.claude/agents/` are not renamed.
- [ ] AC-4: Tests, ruff check, ruff format check and the standards tests (`tests/harness`) pass (implied).

## Out of scope
- Migrating existing child projects that already have `.agents/` (moving the folder, rewriting their lock file); `update` does not detect or move it.
- Renaming `AGENTS.md`, `.claude/agents/`, the `agents.yml` workflow file name, the `AgentsBudgetCheck` doctor check, or any other non-`.agents/` use of the word "agents".
- Changing CLI commands, flags, exit codes, preset contents, or the state machine; bumping the version or tagging a release.

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/payload/managed/dot_agents/ | modify | `git mv` to `dot_codeangel/` (all 13 files: 7 skills, `sync-shims.py`, spec template, contract, stages) |
| src/codeangel/payload/managed/dot_codeangel/skills/build-implement/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-learn/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/contract.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/stages.toml | modify | `.agents` → `.codeangel` in comments |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/scripts/transition.py | modify | `CONFIG_PATH`, `SHIM_SYNC`, shim-drift glob, usage text, owner hint |
| src/codeangel/payload/managed/dot_codeangel/skills/build-plan/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-review/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-verify/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/skills/worktree-cleanup/SKILL.md | modify | `.agents` → `.codeangel` |
| src/codeangel/payload/managed/dot_codeangel/sync-shims.py | modify | `SOURCE`, marker, generated shim text, usage |
| src/codeangel/payload/managed/dot_claude/agents/build-verifier.md | modify | procedure paths |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | layout, managed-file table, skill paths |
| src/codeangel/payload/scaffold/dot_agents/codeangel.toml | modify | `git mv` to `dot_codeangel/codeangel.toml`; comment text |
| src/codeangel/payload/scaffold/AGENTS.md | modify | router rows |
| src/codeangel/payload/scaffold/README.md | modify | skill path |
| src/codeangel/payload/scaffold/docs/ai/doc-map.toml | modify | rule `paths` glob `.codeangel/*` |
| src/codeangel/payload/scaffold/docs/ai/git-workflow.md | modify | CI table + worktree-cleanup path |
| src/codeangel/payload/scaffold/docs/ai/repo-map.md | modify | folder row + build-loop path |
| src/codeangel/payload/scaffold/dot_github/workflows/agents.yml | modify | step name and `sync-shims.py` path |
| src/codeangel/project/model.py | modify | `CONFIG`, `LOCK`, `SYNC`, `TRANSITION` constants |
| src/codeangel/commands/init.py | modify | `--python` help text |
| .agents/ | modify | `git mv` to `.codeangel/` (config, lock, skills, `sync-shims.py`), then refreshed from the payload with `codeangel update` |
| .codeangel/codeangel.toml | modify | project config; comment text |
| .codeangel/codeangel.lock.json | modify | keys re-pointed at `.codeangel/...` and hashes refreshed |
| .codeangel/skills/ | modify | installed copy of the payload skills after `codeangel update` |
| .codeangel/sync-shims.py | modify | installed copy of the payload script |
| .claude/skills/build-implement/SKILL.md | modify | regenerated shim |
| .claude/skills/build-learn/SKILL.md | modify | regenerated shim |
| .claude/skills/build-loop/SKILL.md | modify | regenerated shim |
| .claude/skills/build-plan/SKILL.md | modify | regenerated shim |
| .claude/skills/build-review/SKILL.md | modify | regenerated shim |
| .claude/skills/build-verify/SKILL.md | modify | regenerated shim |
| .claude/skills/worktree-cleanup/SKILL.md | modify | regenerated shim |
| .claude/agents/build-verifier.md | modify | installed copy refreshed by `codeangel update` |
| .github/workflows/agents.yml | modify | step name and `sync-shims.py` path |
| AGENTS.md | modify | project-config path |
| README.md | modify | skills folder, managed / project-owned tables, config + lock paths, version pin text |
| docs/ai/agent-docs.md | modify | installed copy refreshed by `codeangel update` |
| docs/ai/doc-map.toml | modify | rule `paths` glob `.codeangel/*` |
| docs/ai/git-workflow.md | modify | CI table + worktree-cleanup path |
| docs/ai/product.md | modify | "root `.codeangel/` is an installed copy" |
| docs/ai/repo-map.md | modify | folder row + build-loop path |
| tests/support/__init__.py | modify | `TRANSITION` path |
| tests/cli/test_init.py | modify | `.codeangel` paths; new no-`.agents` test |
| tests/cli/test_add.py | modify | `.codeangel/codeangel.toml` |
| tests/cli/test_update.py | modify | `dot_codeangel` payload path, `.codeangel` project paths |
| tests/cli/test_sync.py | modify | skill path |
| tests/cli/test_doctor.py | modify | skill path |
| tests/cli/test_build_loop_script.py | modify | config path |
| tests/cli/test_versioning.py | modify | config + lock + README assertions |
| tests/project/test_project.py | modify | `.codeangel` folder for root discovery |
| tests/install/test_payload_tree.py | modify | `dot_codeangel/x` → `.codeangel/x` |
| tests/harness/test_payload.py | modify | `dot_codeangel` paths; new layout and no-reference tests |
| docs/specs/CAM-10.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_init.py::TestInit::test_installs_codeangel_folder_and_no_agents_folder | AC-1 | after `init`, `.codeangel/{codeangel.toml,codeangel.lock.json,sync-shims.py,skills/build-loop/SKILL.md}` exist and `.agents` does not |
| tests/cli/test_init.py::TestInit::test_installs_managed_scaffold_and_shims | AC-1 | managed files, scaffold and shims land under `.codeangel/` |
| tests/cli/test_init.py::TestInit::test_lock_covers_every_managed_file | AC-1 | lock file lists exactly the shipped managed files |
| tests/install/test_payload_tree.py::TestPayloadTree::test_dot_prefixed_parts_install_as_hidden_paths | AC-1 | `dot_codeangel/x` installs as `.codeangel/x` |
| tests/project/test_project.py::TestProject::test_find_root_walks_up_to_the_config | AC-1 | root discovery finds the dir holding `.codeangel/codeangel.toml` from a subdir |
| tests/cli/test_add.py::TestAdd::test_django_drf_creates_a_runnable_skeleton_and_wires_docs | AC-1 | `add` appends the area to `.codeangel/codeangel.toml` |
| tests/cli/test_update.py::TestUpdate::test_refreshes_files_the_user_has_not_touched | AC-1 | `update` refreshes `.codeangel/skills/...` from the `dot_codeangel` payload |
| tests/cli/test_update.py::TestUpdate::test_never_overwrites_local_edits | AC-1 | local edit under `.codeangel/` kept, `.codeangel-new` proposal written |
| tests/cli/test_sync.py::TestSync::test_sync_check_detects_and_fixes_drift | AC-1 | `sync --check` reads skills from `.codeangel/skills` |
| tests/cli/test_doctor.py::TestDoctor::test_doctor_flags_a_deleted_managed_file | AC-1 | deleting `.codeangel/skills/build-verify/SKILL.md` is reported |
| tests/cli/test_build_loop_script.py::TestBuildLoopScript::test_map_loads_in_an_installed_project | AC-1 | the installed `.codeangel/.../transition.py` loads its map |
| tests/cli/test_versioning.py::TestVersioning::test_project_config_records_the_installed_version | AC-1 | `[codeangel] version` in `.codeangel/codeangel.toml` and `.codeangel/codeangel.lock.json` equal `__version__` |
| tests/harness/test_payload.py::TestPayload::test_payload_ships_dot_codeangel_not_dot_agents | AC-1 | `payload/managed/dot_codeangel` and `payload/scaffold/dot_codeangel` exist; no `dot_agents` directory exists in the payload |
| tests/harness/test_payload.py::TestPayload::test_repo_uses_codeangel_folder_not_agents | AC-2 | repo root has `.codeangel/{codeangel.toml,codeangel.lock.json,sync-shims.py,skills}` and no `.agents`; every lock key starts with `.codeangel/`, `.claude/` or `docs/` |
| tests/harness/test_payload.py::TestPayload::test_no_file_references_the_old_agents_folder | AC-3 | regex scan of `src/`, `tests/`, `.codeangel/`, `.claude/`, `.github/`, `README.md`, `AGENTS.md`, `docs/ai/` finds no `.agents` path and no `dot_agents` (`AGENTS.md`, `.claude/agents/` do not match) |
| tests/harness/test_architecture.py::TestObjectOrientedDesign::test_only_main_is_a_module_level_function | AC-4 | standards tests still pass on the changed source |
| tests/harness/test_code_style.py::TestNoComments::test_source_has_no_comments_or_docstrings | AC-4 | edited source and tests stay comment- and docstring-free |

## Docs impact
| doc | status | note |
|---|---|---|
| README.md | updated | skills folder, managed / project-owned tables, config + lock paths, version pin text |
| AGENTS.md | updated | project-config path in the payload rules |
| docs/ai/repo-map.md | updated | `.agents/` row becomes `.codeangel/`; build-loop path |
| docs/ai/agent-docs.md | updated | installed copy of the managed doc, refreshed with `codeangel update` |
| docs/ai/doc-map.toml | updated | rule glob `.agents/*` becomes `.codeangel/*` |
| docs/ai/git-workflow.md | updated | CI table and worktree-cleanup path |
| docs/ai/product.md | updated | "root `.agents/` is an installed copy" |
| docs/ai/code-standards.md | unchanged | standards text does not mention the folder |
| docs/learnings/tooling.md | unchanged | no existing entry names the folder; any new lesson is recorded in LEARN |

## Risks / open questions
- [non-blocking] Open question from the ticket: should `codeangel update` detect and move an existing `.agents/` in a child project? Treated as out of scope; existing child projects must `git mv .agents .codeangel` by hand and fix their lock keys. State this in the PR description.
- [non-blocking] Renaming the repo's own `.agents/` removes the paths the running build-loop scripts and skills use (`transition.py`, skills, the Claude shims). Do the repo rename last in IMPLEMENT, after payload, source and tests pass; afterwards call `T` through `.codeangel/skills/build-loop/scripts/transition.py`, regenerate the shims with `.codeangel/sync-shims.py`, and refresh the lock with `codeangel update` (re-key the lock paths first; use `--force` only if it reports conflicts on unedited files).
- [non-blocking] Skill and shim text in this session still names `.agents/...` until the shims are regenerated; stage skills invoked after the rename may need to be read from `.codeangel/skills/<name>/SKILL.md` directly.
- [non-blocking] `agents.yml` keeps its file name (out of scope); only its step name and script path change.
- [non-blocking] The managed payload must stay free of product, framework and package-manager names; `test_managed_files_are_project_agnostic` may flag the `codeangel` folder name. If so, scope the test's banned list rather than weakening it (the folder name is a codeangel convention) and record it under `## Plan amendments`.
- [non-blocking] `gh` is authenticated; base `origin/main` equals HEAD, so no rebase risk.

## Baseline
- base_sha: 87a707d5c869eccdf432c835de1f311b82e0d979
- gates: root (no `[[areas]]`; gates from root `AGENTS.md` `## Done`): `uv run pytest` → exit 0, 60 passed, 0 failed; `uv run ruff check src tests` → exit 0; `uv run ruff format --check src tests` → exit 0, 66 files already formatted; `uv run python .agents/sync-shims.py --check` → exit 0; `uv run codeangel -C . doctor` → 0 problems, 0 warnings. No collection or build errors.
- known failures: none
- lint debt: none
- schema drift: none: this repo has no schema or migrations

## Plan amendments
<!-- - <UTC time> <what changed> — <why> -->

## Verify reports
<!--
### Attempt 1 — PASS|FAIL
- V1 lint/format: PASS|FAIL <detail>
- V2 migrations: PASS|FAIL
- V3 full suite: PASS|FAIL <n passed, m failed; failures ⊆ baseline?>
- V4 planned tests: PASS|FAIL
- V5 AC audit: PASS|FAIL
  - AC-1: <test node id>; <file>:<line>
- V6 scope audit: PASS|FAIL
- V7 hygiene: PASS|FAIL
- V8 docs in sync: PASS|FAIL
- Failure excerpt / root cause / next action: <...>
-->

## Review
- PR: <url>
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
- 2026-10-17T15:14Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-10-rename-agents-to-codeangel, base=87a707d5c8
- 2026-10-17T15:15Z PLAN → IMPLEMENT [planned] attempt=0/5
