---
ticket: CAM-18
title: Bump codeangel version automatically in CI so child projects can pin and update it
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-18/bump-codeangel-version-automatically-in-ci-so-child-projects
branch: camerondhobbs/cam-18-bump-codeangel-version-automatically-in-ci-so-child-projects
base_sha: ec2cb550abcbf7d6e99b877c37c07d1d07129358
pr:
stage: IMPLEMENT  # managed by transition.py — see stages.toml
last_status: planned  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-18T02:00Z
updated: 2026-10-18T02:02Z
---

# CAM-18: Bump codeangel version automatically in CI so child projects can pin and update it

## Ticket
**Add proper version control** (original title, CAM-18)

Versions should be bumped automatically by CI instead of having just 1 version, so that they can be installed in my project with fixed versioning! And I can update codeangel properly in child projects

(No comments on the ticket. Refined by build-loop: "Bump codeangel version automatically in CI so child projects can pin and update it".)

## Acceptance criteria
- [ ] AC-1: A maintainer merges a pull request to `main` and CI releases a new version with no manual edit: the workflow runs `python .github/scripts/bump_version.py --release`, which raises `codeangel.__version__` by one patch step (`0.1.0` → `0.1.1`), or one minor / major step when the merged PR carries the label `release:minor` / `release:major`, and prints the new version. [proof: cli]
- [ ] AC-2: Each release is a distinct fixed version a child project can pin: the release commit holds the bumped `__version__`, and an annotated tag `vX.Y.Z` points at it (plus a GitHub release). Running `uv tool install git+<repo>@vX.Y.Z` and then `codeangel version` prints exactly `codeangel X.Y.Z`; a second release gets a different tag and version. [proof: cli]
- [ ] AC-3: In a child project recorded at an older codeangel version (`[codeangel] version` in `.codeangel/codeangel.toml`), `codeangel doctor` warns the CLI is newer, and `codeangel update` brings the recorded version (config and lock) to the installed release; `doctor` then shows no version warning. [proof: cli]
- [ ] AC-4: A release run cannot loop or double-release (implied): the workflow skips pushes whose head commit is a `Release vX.Y.Z` commit, runs one release at a time, and the script refuses a tag that already exists. [proof: cli]
- [ ] AC-5: The docs describe the automated process (implied): `README.md` and `AGENTS.md` say CI bumps and tags on merge to `main`, how to pin a release tag, and how to raise the minor / major level; no doc tells a maintainer to bump the version by hand. [proof: none — documentation only, checked by a test and read in review]

## Out of scope
- Changing what `codeangel update` installs or how it merges managed files (AC-3 only confirms the existing version stamping).
- Publishing to PyPI or any package index; installs stay `git+https://...@vX.Y.Z`.
- Generating a changelog or release notes beyond GitHub's auto-generated notes.
- Deriving the version from tags at build time (setuptools-scm); `codeangel.__version__` stays the single version.
- Version-bump CI for child projects (generated project workflows).

## Affected files
| path | change | why |
|---|---|---|
| .github/scripts/bump_version.py | create | object-oriented script: reads `__version__`, picks the level from labels, rewrites `src/codeangel/__init__.py`, with `--release` commits `Release vX.Y.Z` and creates the tag |
| .github/workflows/release.yml | create | on push to `main`: find the merged PR labels, run the script, push the commit and tag, create the GitHub release |
| tests/cli/test_release.py | create | tests the script in a throwaway git repo and the workflow's required wiring |
| tests/cli/test_versioning.py | modify | AC-3 doctor / update test and the docs assertions |
| docs/specs/CAM-18.md | modify | this spec |
| AGENTS.md | modify | `## Version`: CI bumps and tags; no manual bump |
| README.md | modify | Install / develop: releases are cut by CI, pin a tag, label for minor / major |
| docs/ai/code-standards.md | modify | `__version__` is bumped by CI, not by hand |
| docs/ai/git-workflow.md | modify | CI table row for `release.yml` and the label convention |
| docs/ai/repo-map.md | modify | `.github/scripts/` row |
| docs/ai/doc-map.toml | modify | map `.github/scripts/*` and the workflows to the git-workflow doc |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_release.py::TestBumpVersion::test_defaults_to_a_patch_bump | AC-1 | `0.1.0` becomes `0.1.1` in the file and on stdout |
| tests/cli/test_release.py::TestBumpVersion::test_release_labels_pick_minor_and_major | AC-1 | `release:minor` gives `0.2.0`, `release:major` gives `1.0.0`, major wins over minor |
| tests/cli/test_release.py::TestBumpVersion::test_rewrites_only_the_version_line | AC-1 | everything else in `__init__.py` is unchanged |
| tests/cli/test_release.py::TestRelease::test_release_commits_and_tags_the_bump | AC-2 | commit subject `Release v0.1.1`, annotated tag `v0.1.1` on it, tree holds the new version |
| tests/cli/test_release.py::TestRelease::test_second_release_gets_a_distinct_tag | AC-2 | two releases give `v0.1.1` and `v0.1.2` |
| tests/cli/test_release.py::TestRelease::test_existing_tag_is_refused | AC-4 | a pre-existing target tag exits non-zero and leaves the file and history unchanged |
| tests/cli/test_release.py::TestReleaseWorkflow::test_workflow_is_wired_for_main_releases | AC-1, AC-2, AC-4 | triggers on push to `main`, `contents: write`, checks out full history, skips `Release v` commits, one release at a time, runs the script, pushes the tag, creates the release |
| tests/cli/test_versioning.py::TestVersioning::test_update_moves_a_child_project_to_the_installed_version | AC-3 | old recorded version: doctor warns; after update config and lock equal `__version__` and the warning is gone |
| tests/cli/test_versioning.py::TestVersioning::test_docs_describe_the_automated_release | AC-5 | README and AGENTS.md mention the CI bump on merge, the labels, and pinning; AGENTS.md no longer says "bump that value" |

## Docs impact
| doc | status | note |
|---|---|---|
| AGENTS.md | updated | `## Version` now says CI bumps and tags |
| README.md | updated | install / develop sections describe automated releases and pinning |
| docs/ai/code-standards.md | updated | `__version__` is changed by CI only |
| docs/ai/git-workflow.md | updated | CI table gains `release.yml`; PR label convention |
| docs/ai/repo-map.md | updated | `.github/scripts/` row |

## Risks / open questions
- [non-blocking] Bump level (open question in the ticket): decided patch by default; the PR labels `release:minor` / `release:major` raise it. Revisit if the user prefers conventional-commit parsing.
- [non-blocking] Install method (open question): decided on git tags (`uv tool install git+https://github.com/camalpha-lgtm/codeangel@vX.Y.Z`), already the documented pin; no PyPI.
- [non-blocking] `release.yml` only runs on `main` after merge, so CI on the PR cannot exercise it. The script and its git steps are tested locally and in the tests; the workflow YAML is checked structurally. The first real release is the merge of this PR.
- [non-blocking] The release job pushes a commit and a tag straight to `main` (it runs as `github-actions[bot]`, not an agent). It needs `contents: write` and no branch protection on `main` (currently none); protection later would need a bypass for the bot.
- [non-blocking] Pushes by `GITHUB_TOKEN` do not retrigger workflows, so the release commit itself is not CI-tested; it only changes the version string.
- [non-blocking] STARTUP: the GitHub MCP is not authorized in this session; REVIEW and the CI wait use `gh` (authenticated).
- [non-blocking] STARTUP: worktree-cleanup skipped the CAM-8 worktree (uncommitted change in `.codeangel/codeangel.toml`).

## Baseline
- base_sha: ec2cb550abcbf7d6e99b877c37c07d1d07129358
- gates: `uv run pytest` → exit 0; 111 passed, 0 failed · `uv run ruff check src tests` → exit 0 · `uv run ruff format --check src tests` → exit 0 (74 files formatted)
- known failures: none
- lint debt: none
- schema drift: n/a (no schema in this repo)

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
- V9 evidence: PASS|FAIL <rows captured / not captured>
- Failure excerpt / root cause / next action: <...>
-->

## Evidence
<!-- Written by VERIFY: one row per AC. kind = api | ui | cli | none. proof = comma-separated artefact paths under <spec_dir>/evidence/<TICKET>/, or `not captured: <reason>`, or `n/a: <reason>` (kind none only). -->
| AC | kind | proof | note |
|---|---|---|---|
| AC-1 | <api, ui, cli or none> | <docs/specs/evidence/<TICKET>/ac-1-api.txt> | <what the proof shows> |

## Review
- PR: <url>
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
- 2026-10-18T02:00Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-18-bump-codeangel-version-automatically-in-ci-so-child-projects, base=ec2cb550ab
- 2026-10-18T02:02Z PLAN → IMPLEMENT [planned] attempt=0/5
