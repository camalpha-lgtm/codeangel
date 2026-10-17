---
ticket: CAM-8
title: Install default Cursor and Claude MCP configs into child projects
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-8/install-default-cursor-and-claude-mcp-configs-into-child-projects
branch: camerondhobbs/cam-8-install-default-cursor-and-claude-mcp-configs-into-child
base_sha: c3b9736dcb3e3eedd1aacb078ca722b3480e9c5d
pr:
stage: REVIEW  # managed by transition.py — see stages.toml
last_status: pass  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-17T15:55Z
updated: 2026-10-17T16:00Z
---

# CAM-8: Install default Cursor and Claude MCP configs into child projects

## Ticket
**Title:** Package mcp configs for child projects to use

Mcp configs should automatically be installed with codeangel for cursor and claude. so on fresh projects there is no need to configure them each time. can just install at a default level, thats completely ok

Also update build-loop so it knows to use github mcp and linear mcp instead of api clients, for its operations

Comments: none.

Refined by build-loop STARTUP (Linear title and description rewritten with Summary / Context / Acceptance criteria / Out of scope / Open questions; the original is kept as a Linear comment).

## Acceptance criteria
- [x] AC-1: `codeangel init` installs `.mcp.json` (Claude Code) and `.cursor/mcp.json` (Cursor) into the child project; each is valid JSON whose `mcpServers` declare a `linear` and a `github` remote server, and neither holds a token, key or `headers` entry.
- [x] AC-2: `codeangel update` creates either config when it is missing and keeps both under the managed-file rules: a locally edited config is never overwritten, and the new version lands as `<file>.codeangel-new`.
- [x] AC-3: build-loop uses the Linear MCP for tracker reads and writes and the GitHub MCP for pull-request operations (find / create, check state, mark ready, rerun, failure logs, list merged PRs); the shipped skills, contract, spec template and `transition.py` carry no API-client path (`LINEAR_API_KEY`, `curl`, GraphQL, `issueUpdate`, the `linear-api` source).
- [x] AC-4: The waits that need no judgement stay on `gh` (`gh pr checks --watch`, `await_merge.py`) because an MCP call per poll costs model tokens; the skills say so, and name `gh` as the fallback when the GitHub MCP is unavailable.
- [x] AC-5: The docs that describe the installed layout and build-loop tooling (README.md, `AGENTS.md`, `docs/ai/agent-docs.md`, `docs/ai/repo-map.md`, `docs/ai/git-workflow.md`, their scaffold templates, and the doc maps) name the two MCP configs and the MCP-first rule.

## Out of scope
- Per-project or per-user MCP customisation (user-level `~/.cursor/mcp.json`, `claude mcp add` scopes) and MCP servers beyond Linear and GitHub.
- Storing, prompting for or provisioning credentials: both servers authenticate through OAuth in the host, so the configs carry no secret.
- Changing the build-loop state machine (stages, exits, checks); only the wording of `entry` / `when` strings in `stages.toml` and the `--source` choices in `transition.py` change.
- Rewriting `await_merge.py` to use an MCP (it is a no-model-call poller by design, CAM-7) and the `.egg-info` worktree-cleanup skip seen at STARTUP.
- A `codeangel doctor` check for the MCP configs.

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/payload/managed/dot_mcp.json | create | Claude Code project config: `linear` and `github` remote servers (`type: http`) |
| src/codeangel/payload/managed/dot_cursor/mcp.json | create | Cursor project config: the same two servers in Cursor's `url` form |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/SKILL.md | modify | Linear MCP only (drop the curl / GraphQL / `issueUpdate` paths), GitHub MCP for the tools check and the merge-watch PR check, a one-line tooling rule |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/contract.md | modify | new `## Tools` section: MCP-first, no API clients, `gh` only for no-judgement waits and as fallback; Tracker status wording |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/stages.toml | modify | REVIEW `entry` / `produces` / `when` strings stop naming `gh` commands |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/assets/spec-template.md | modify | `source` comment loses `linear-api` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/scripts/transition.py | modify | `--source` choices lose `linear-api` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-plan/SKILL.md | modify | `--source` list loses `linear-api` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-review/SKILL.md | modify | GitHub MCP for PR find / create / ready / rerun / failure logs; `gh pr checks --watch` stays as the blocking wait; `gh` fallback |
| src/codeangel/payload/managed/dot_codeangel/skills/worktree-cleanup/SKILL.md | modify | merged-PR list through the GitHub MCP, `gh` fallback |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | managed-files table gains the two configs; build-loop paragraph names the MCP-first rule |
| src/codeangel/payload/scaffold/docs/ai/git-workflow.md | modify | PR prerequisite: GitHub MCP authorised, `gh` for CI wait and merge watch |
| src/codeangel/payload/scaffold/docs/ai/repo-map.md | modify | row for `.mcp.json`, `.cursor/mcp.json` |
| src/codeangel/payload/scaffold/docs/ai/doc-map.toml | modify | the `.codeangel/*` rule also covers `.mcp.json` and `.cursor/*` |
| .mcp.json | create | installed copy (this repo dogfoods its payload) |
| .cursor/mcp.json | create | installed copy |
| .codeangel/skills/build-loop/SKILL.md | modify | installed copy |
| .codeangel/skills/build-loop/references/contract.md | modify | installed copy |
| .codeangel/skills/build-loop/references/stages.toml | modify | installed copy |
| .codeangel/skills/build-loop/assets/spec-template.md | modify | installed copy |
| .codeangel/skills/build-loop/scripts/transition.py | modify | installed copy |
| .codeangel/skills/build-plan/SKILL.md | modify | installed copy |
| .codeangel/skills/build-review/SKILL.md | modify | installed copy |
| .codeangel/skills/worktree-cleanup/SKILL.md | modify | installed copy |
| docs/ai/agent-docs.md | modify | installed copy of the managed doc |
| .codeangel/codeangel.lock.json | modify | hashes and the two new entries, refreshed by `codeangel update` |
| README.md | modify | what-is-managed table and the build-loop bullet name the MCP configs |
| AGENTS.md | modify | Layout row for `payload/managed/` lists the MCP configs |
| docs/ai/repo-map.md | modify | row for `.mcp.json`, `.cursor/mcp.json` |
| docs/ai/git-workflow.md | modify | PR prerequisite wording |
| docs/ai/doc-map.toml | modify | the `.codeangel/*` rule also covers `.mcp.json` and `.cursor/*` |
| tests/cli/test_mcp_configs.py | create | init installs the configs; build-loop MCP-first instructions |
| tests/cli/test_mcp_docs.py | create | docs and doc maps name the MCP configs (split out: three test classes in one file break the two-class limit) |
| tests/cli/test_update.py | modify | update recreates a missing config and keeps an edited one |
| tests/harness/test_payload.py | modify | the lockfile-prefix assertion also allows `.mcp.json` and `.cursor/` |
| docs/specs/CAM-8.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_mcp_configs.py::TestMcpConfigs::test_init_installs_both_configs | AC-1 | after `init`, `.mcp.json` and `.cursor/mcp.json` exist, parse as JSON, and each `mcpServers` has `linear` and `github` with an `https://` `url` |
| tests/cli/test_mcp_configs.py::TestMcpConfigs::test_claude_servers_declare_the_http_transport | AC-1 | every server in `.mcp.json` has `type == "http"` |
| tests/cli/test_mcp_configs.py::TestMcpConfigs::test_configs_carry_no_credentials | AC-1 | no server entry has `headers`, `env` or `args`, and the file text has no `Bearer`, `token` or `key` |
| tests/cli/test_mcp_configs.py::TestMcpConfigs::test_configs_are_in_the_lockfile | AC-1, AC-2 | both paths are keys of the lockfile after `init` |
| tests/cli/test_update.py::TestUpdate::test_update_recreates_a_missing_mcp_config | AC-2 | delete `.mcp.json`, run `update` → exit 0 and the file is back, identical to the payload |
| tests/cli/test_update.py::TestUpdate::test_update_keeps_an_edited_mcp_config | AC-2 | add a server to `.cursor/mcp.json`, ship a newer payload copy, `update` → edit kept, `mcp.json.codeangel-new` holds the new version |
| tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_no_shipped_build_loop_file_has_an_api_client_path | AC-3 | none of the managed build-loop files, `build-plan`, `build-review`, `worktree-cleanup` match `LINEAR_API_KEY`, `curl`, `graphql`, `issueUpdate`, `linear-api` (case-insensitive) |
| tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_contract_declares_mcp_first_tools | AC-3, AC-4 | `contract.md` has a `## Tools` section naming the Linear MCP and the GitHub MCP, and `gh` as fallback |
| tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_review_uses_the_github_mcp_for_pull_requests | AC-3 | `build-review` SKILL names the GitHub MCP and has none of `gh pr create`, `gh pr ready`, `gh run rerun`, `gh run view`, `gh run list` |
| tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_cleanup_lists_merged_prs_through_the_github_mcp | AC-3 | `worktree-cleanup` SKILL names the GitHub MCP and no longer calls `gh pr list` |
| tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_blocking_waits_stay_on_gh | AC-4 | `build-review` keeps `gh pr checks` with `--watch`; `build-loop` SKILL still runs `scripts/await_merge.py`; both say why (no model call per poll) |
| tests/cli/test_mcp_docs.py::TestDocs::test_docs_name_the_mcp_configs | AC-5 | README.md, AGENTS.md, `docs/ai/agent-docs.md`, `docs/ai/repo-map.md`, `docs/ai/git-workflow.md`, the managed `agent-docs.md` and the scaffold `repo-map.md` / `git-workflow.md` each mention `.mcp.json` or `.cursor/mcp.json` |
| tests/cli/test_mcp_docs.py::TestDocs::test_doc_maps_flag_mcp_config_changes | AC-5 | the repo's and the scaffold's `doc-map.toml` have a rule whose `paths` include `.mcp.json` and `.cursor/*` |
| tests/harness/test_payload.py::TestPayload::test_repo_uses_codeangel_folder_not_agents | AC-1 | existing test, prefix list widened: every lockfile key starts with `.codeangel/`, `.claude/`, `.cursor/`, `.mcp.json` or `docs/` |

## Docs impact
<!-- `T docs <TICKET>` lists docs mapped from the change (docs/ai/doc-map.toml). One row per doc; status updated or unchanged; unchanged needs a reason. Nothing maps → "- none: <why>". -->
| doc | status | note |
|---|---|---|
| docs/ai/repo-map.md | updated | new row for the two MCP configs |
| README.md | updated | managed-files table and build-loop bullet name the configs and the MCP-first rule |
| AGENTS.md | updated | Layout row for `payload/managed/` lists the MCP configs |
| docs/ai/code-standards.md | unchanged | no standard changes; the new tests follow it (two classes max per file, no comments) |
| docs/ai/agent-docs.md | updated | installed copy of the managed doc, refreshed with `codeangel update` |
| docs/ai/git-workflow.md | updated | PR prerequisite is the GitHub MCP, with `gh` kept for the CI wait and merge watch |
| docs/ai/doc-map.toml | updated | the `.codeangel/*` rule also covers the MCP configs |
| docs/learnings/tooling.md | unchanged | no new gotcha known before implementation; LEARN decides |

## Risks / open questions
- [non-blocking] Open question from the ticket: should the GitHub MCP replace `gh` entirely? Decision: no. PR find / create / ready / rerun / failure logs / merged-PR listing move to the GitHub MCP. The blocking waits (`gh pr checks --watch`, `await_merge.py`) stay on `gh`: an MCP call per poll would cost model tokens (the cost CAM-7 avoided). `gh` is also the fallback when the GitHub MCP is not available.
- [non-blocking] Open question: which config locations count as "default level"? Decision: project level (`.mcp.json`, `.cursor/mcp.json`), the only level a repo can ship; the OAuth sign-in is the user's own.
- [non-blocking] Open question: keep an API fallback? Decision: no. Linear without the MCP → STARTUP asks the user to paste the ticket (existing step); GitHub without the MCP → `gh`.
- [non-blocking] OAuth against `https://api.githubcopilot.com/mcp/` and `https://mcp.linear.app/mcp` is host-dependent and cannot be exercised here (no Claude Code or Cursor session reads these files from a test). The URLs and the `type: http` (Claude) / `url` (Cursor) shapes come from the vendors' published setup; a web search could not confirm the Claude Code schema page, so the shapes are judged from the existing host MCP entries in this session. A token header was rejected: `${VAR}` expansion in remote headers is unreliable in Cursor and fails config parsing in Claude Code when the variable is unset.
- [non-blocking] Claude Code asks the user to approve project-scoped servers from `.mcp.json` on first use; a project that already defines `linear` or `github` at user level keeps its own definition winning. Documented in the README, not worked around.
- [non-blocking] GitHub MCP tool names differ across server versions; the skills name operations and say "tool names contain `github`", as the existing Linear instructions do, instead of pinning exact tool names.
- [non-blocking] Managed files must avoid the banned words in `test_managed_files_are_project_agnostic`; keep the new text neutral.
- [non-blocking] This repo gains project-scoped MCP servers of its own through dogfooding (`.mcp.json`, `.cursor/mcp.json`), duplicating whatever the contributor already has at user level; accepted.
- [non-blocking] STARTUP left three merged worktrees (CAM-6, CAM-7, CAM-10) because `src/codeangel.egg-info/` is not in `[worktrees] disposable`; unrelated, left alone.

## Baseline
- base_sha: c3b9736dcb3e3eedd1aacb078ca722b3480e9c5d
- gates: root (no `[[areas]]`; gates from root `AGENTS.md` `## Done`): `uv run pytest` → exit 0, 74 passed, 0 failed; `uv run ruff check src tests` → exit 0; `uv run ruff format --check src tests` → exit 0, 68 files already formatted; `uv run python .codeangel/sync-shims.py --check` → exit 0 (shims in sync); `uv run codeangel -C . doctor` → exit 0, 0 problems, 0 warnings. No collection or build errors.
- known failures: none
- lint debt: none
- schema drift: none: this repo has no schema or migrations

## Plan amendments
<!-- - <UTC time> <what changed> — <why> -->
- 2026-10-17T16:05Z TestDocs moved from tests/cli/test_mcp_configs.py to the new tests/cli/test_mcp_docs.py (test ids updated) — `test_test_files_hold_at_most_two_test_classes` allows two classes per file

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

### Attempt 1 — PASS
- V1 lint/format: PASS `ruff check src tests` exit 0; `ruff format --check src tests` exit 0 (70 files formatted, nothing modified); `sync-shims.py --check` exit 0; `codeangel doctor` 0 problems, 0 warnings.
- V2 migrations: PASS skipped: this repo has no schema or migrations (baseline: none).
- V3 full suite: PASS `uv run pytest` 87 passed, 0 failed (baseline 74 passed, 0 failed; +13 new tests); no collection errors; failures (none) within baseline (none).
- V4 planned tests: PASS all 14 planned ids exist and pass (29 passed across test_mcp_configs, test_mcp_docs, test_update, test_payload).
- V5 AC audit: PASS
  - AC-1: tests/cli/test_mcp_configs.py::TestMcpConfigs::test_init_installs_both_configs; tests/cli/test_mcp_configs.py:29 (also test_claude_servers_declare_the_http_transport :36, test_configs_carry_no_credentials :39, test_configs_are_in_the_lockfile :46)
  - AC-2: tests/cli/test_update.py::TestUpdate::test_update_recreates_a_missing_mcp_config; tests/cli/test_update.py:89 and ::test_update_keeps_an_edited_mcp_config; tests/cli/test_update.py:98 (edit kept, `.codeangel-new` holds the new version)
  - AC-3: tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_no_shipped_build_loop_file_has_an_api_client_path; tests/cli/test_mcp_configs.py:54 (also test_contract_declares_mcp_first_tools :64, test_review_uses_the_github_mcp_for_pull_requests :73, test_cleanup_lists_merged_prs_through_the_github_mcp :86); independent grep of .codeangel, src, README, docs/ai found no LINEAR_API_KEY / curl / graphql / issueUpdate / linear-api
  - AC-4: tests/cli/test_mcp_configs.py::TestBuildLoopTooling::test_blocking_waits_stay_on_gh; tests/cli/test_mcp_configs.py:92 (contract.md Tools section also names `gh` as fallback, :64)
  - AC-5: tests/cli/test_mcp_docs.py::TestDocs::test_docs_name_the_mcp_configs; tests/cli/test_mcp_docs.py:29 and ::test_doc_maps_flag_mcp_config_changes; tests/cli/test_mcp_docs.py:38
- V6 scope audit: PASS every changed or new file is in Affected files (or is the spec); no Out-of-scope item done (await_merge.py untouched, no doctor check, state machine unchanged). `.codeangel/codeangel.toml` shows modified in `git status` only by line-ending normalisation, not in `git diff --name-only <base_sha>`.
- V7 hygiene: PASS full diff read: no debug output, commented-out code, bare TODOs, secrets or machine paths; configs carry no headers/env/args; no comments or docstrings in new tests; installed copies equal payload copies (line endings aside); `codeangel update` reports managed files up to date and leaves the tree unchanged.
- V8 docs in sync: PASS `T docs CAM-8` docs_synced ready; README.md, AGENTS.md, docs/ai/repo-map.md, docs/ai/agent-docs.md, docs/ai/git-workflow.md and the scaffold copies and both doc maps read against the code: accurate; `unchanged` reasons (code-standards.md, learnings/tooling.md) hold.

## Review
- PR: <url>
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
- 2026-10-17T15:55Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-8-install-default-cursor-and-claude-mcp-configs-into-child, base=c3b9736dcb
- 2026-10-17T15:56Z PLAN → IMPLEMENT [planned] attempt=0/5
- 2026-10-17T15:58Z IMPLEMENT → VERIFY [implemented] attempt=0/5
- 2026-10-17T16:00Z VERIFY → REVIEW [pass] attempt=0/5
