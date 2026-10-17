---
ticket: CAM-7
title: Automatically update Linear ticket on build-loop progress
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-7/automatically-update-linear-ticket-on-build-loop-progress
branch: camerondhobbs/cam-7-automatically-update-linear-ticket-on-build-loop-progress
base_sha: 7288c1846d631fc421e9fd741b46238b3d593852
pr:
stage: IMPLEMENT  # managed by transition.py — see stages.toml
last_status: planned  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-17T15:27Z
updated: 2026-10-17T15:28Z
---

# CAM-7: Automatically update Linear ticket on build-loop progress

## Ticket
**Title:** Automatically update linear ticket on build-loop progress

Should automatically set it to in progress as it starts planning, when it's merged in (poll github in review stage maybe? after marking ready for review) it should be marked as done. can have a timeout of 2 hours on the polling. Do not recall the skill, just poll every 5 mins in review stage using github CLI, i dont want to pay loads of money on LLM invocations

Comments: none.

Refined by build-loop STARTUP (Linear description rewritten with Summary / Context / Acceptance criteria / Out of scope / Open questions; the original is kept as a Linear comment). Title kept apart from the capitalised "Linear".

## Acceptance criteria
- [ ] AC-1: When build-loop starts a new ticket whose tracker is Linear and whose status is not already started, completed or canceled, STARTUP sets the Linear ticket to In Progress (`save_issue` `state`, or the API fallback) before the PLAN stage runs; a failure is logged and never blocks.
- [ ] AC-2: After the ticket reaches DONE with a ready (non-draft) PR, the build-loop coordinator runs `.codeangel/skills/build-loop/scripts/await_merge.py <pr>` once; the script polls `gh pr view <pr> --json state` every 300 s by default and makes no model call between polls (the skill is not re-invoked).
- [ ] AC-3: When the script sees the PR `MERGED` it exits 0 immediately, and the coordinator then sets the Linear ticket to Done (`save_issue` `state`, or the API fallback).
- [ ] AC-4: When the PR is still open after the timeout (7200 s by default) the script exits 3 and the coordinator leaves the Linear status unchanged and says so in the final report.
- [ ] AC-5: When the PR is `CLOSED` without merging the script exits 1 and the coordinator leaves the Linear status unchanged and says so in the final report. (implied)
- [ ] AC-6: When `gh` fails 3 polls in a row the script exits 2 with the error instead of polling on, and the coordinator leaves the Linear status unchanged. (implied)

## Out of scope
- Other Linear transitions (In Review, Canceled, Blocked) and Linear comments about progress; only In Progress at planning start and Done on merge.
- Changing how or when the PR is created, linked or marked ready, or adding a stage or exit to `stages.toml` / `transition.py` (the watch runs after DONE, so the state machine and spec are untouched).
- Merging the PR (build-loop never merges), or recording the merge in the spec (a commit after DONE would land on a merged branch).
- A `[tracker]` config switch for the status sync, per-project poll intervals, or T3 Code `watch_pull_request` (it wakes the model, which is the cost the ticket wants to avoid).
- Updating the status of tickets that were not started through build-loop, and the `.egg-info` worktree-cleanup skip seen at STARTUP.

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/scripts/await_merge.py | create | the poller: class-based, stdlib, `gh pr view` every 300 s up to 7200 s, exit 0 merged / 1 closed / 2 gh failing or usage / 3 timeout |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/SKILL.md | modify | STARTUP step 3c (In Progress), MERGE WATCH section (run the script, Done on merge), Modes row for DONE, final report line |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/contract.md | modify | Tracker status section: the two status moves, the script and its exit codes, never block |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | build-loop paragraph mentions the tracker status sync and `await_merge.py` |
| docs/ai/agent-docs.md | modify | installed copy refreshed by `codeangel update` |
| .codeangel/skills/build-loop/scripts/await_merge.py | create | installed copy of the payload script |
| .codeangel/skills/build-loop/SKILL.md | modify | installed copy of the payload skill |
| .codeangel/skills/build-loop/references/contract.md | modify | installed copy of the payload contract |
| .codeangel/codeangel.lock.json | modify | hashes and the new file entry refreshed by `codeangel update` |
| README.md | modify | build-loop bullet: keeps the Linear ticket In Progress → Done |
| tests/cli/test_merge_watch.py | create | poller behaviour and the build-loop instructions |
| tests/support/__init__.py | modify | `AWAIT_MERGE` path constant |
| docs/specs/CAM-7.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_merge_watch.py::TestBuildLoopInstructions::test_startup_sets_in_progress_before_planning | AC-1 | build-loop SKILL.md STARTUP has a step that calls `save_issue` with `In Progress`, skips started / Done / Canceled tickets, never blocks, and sits before the Dispatch section |
| tests/cli/test_merge_watch.py::TestBuildLoopInstructions::test_merge_watch_runs_the_script_and_never_recalls_the_skill | AC-2 | build-loop SKILL.md MERGE WATCH names `scripts/await_merge.py`, says the polling needs no model call, and runs only for a ready PR after DONE |
| tests/cli/test_merge_watch.py::TestBuildLoopInstructions::test_merge_outcomes_map_to_linear_status | AC-3, AC-4, AC-5, AC-6 | SKILL.md sets Done on exit 0 and leaves the status unchanged and reports it for 1 / 2 / 3 |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_defaults_poll_every_five_minutes_for_two_hours | AC-2, AC-4 | default interval 300 s and timeout 7200 s |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_asks_github_cli_for_the_pr_state | AC-2 | the subprocess command is `gh pr view <pr> --json state` and nothing else |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_exits_zero_as_soon_as_the_pr_is_merged | AC-3 | OPEN, OPEN, MERGED → exit 0 after 2 sleeps of the interval |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_exits_three_when_still_open_at_the_timeout | AC-4 | an always-OPEN PR → exit 3, total slept time equals the timeout, no further polls |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_exits_one_when_the_pr_is_closed_unmerged | AC-5 | CLOSED → exit 1 immediately |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_exits_two_after_three_consecutive_gh_failures | AC-6 | 2 failures then MERGED → exit 0; 3 failures in a row → exit 2 |
| tests/cli/test_merge_watch.py::TestMergeWatcher::test_script_is_installed_into_projects | AC-2 | after `init` the script exists at `.codeangel/skills/build-loop/scripts/await_merge.py` and loads |

## Docs impact
<!-- `T docs <TICKET>` lists docs mapped from the change (docs/ai/doc-map.toml). One row per doc; status updated or unchanged; unchanged needs a reason. Nothing maps → "- none: <why>". -->
| doc | status | note |
|---|---|---|
| README.md | updated | build-loop bullet gains the Linear status sync (In Progress at planning, Done on merge) |
| docs/ai/agent-docs.md | updated | installed copy of the managed doc, refreshed with `codeangel update` |
| docs/ai/repo-map.md | unchanged | the `.codeangel/` row describes folders (config, skills, shims), not the scripts inside a skill |
| AGENTS.md | unchanged | layout and payload rules do not name individual skill scripts; no command or rule changes |
| docs/ai/code-standards.md | unchanged | the payload script is outside the standards tests (`payload` is excluded); no standard changes |

## Risks / open questions
- [non-blocking] Ticket says "poll in review stage after marking ready"; REVIEW → LEARN pushes a learnings commit to the PR after it is marked ready, so a merge during the poll would strand that push. The watch therefore starts after LEARN → DONE (the PR is ready and final). Same cost profile (script only), same trigger (PR marked ready); only the start moves later.
- [non-blocking] Open question from the ticket: report or record a timeout? Decision: only in the final report; nothing is written to the spec (it would be a commit after DONE) or to Linear (the status must stay unchanged).
- [non-blocking] Open question from the ticket: PR closed without merge? Decision: script exits 1, Linear left unchanged, reported.
- [non-blocking] The poll runs as a background shell command with the harness's maximum timeout (7200 s). A harness that kills it at exactly 2 h is treated the same as exit 3 (timeout).
- [non-blocking] Linear's GitHub integration may already move merged tickets to Done; the coordinator sets Done only if the status is not already Done.
- [non-blocking] Managed files must avoid the banned words in `test_managed_files_are_project_agnostic` (test runner and linter names, "actually"); keep the new text neutral.
- [non-blocking] STARTUP left two merged worktrees (CAM-6, CAM-10) because `src/codeangel.egg-info/` is not in `[worktrees] disposable`; unrelated, left alone.

## Baseline
- base_sha: 7288c1846d631fc421e9fd741b46238b3d593852
- gates: root (no `[[areas]]`; gates from root `AGENTS.md` `## Done`): `uv run pytest` → exit 0, 64 passed, 0 failed; `uv run ruff check src tests` → exit 0; `uv run ruff format --check src tests` → exit 0, 66 files already formatted; `uv run python .codeangel/sync-shims.py --check` → exit 0 (shims in sync); `uv run codeangel -C . doctor` → 0 problems, 0 warnings. No collection or build errors.
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
- 2026-10-17T15:27Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-7-automatically-update-linear-ticket-on-build-loop-progress, base=7288c1846d
- 2026-10-17T15:28Z PLAN → IMPLEMENT [planned] attempt=0/5
