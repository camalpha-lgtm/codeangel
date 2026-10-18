# build-loop contract — read before running any build-* skill

<!-- Shared by build-loop (coordinator) and every stage skill. Self-contained: stage skills may run in a subagent with no conversation history. Managed by codeangel: change it in the codeangel repo, then `codeangel update`. -->

## State
- Config = `.codeangel/codeangel.toml`: `project` (name, base_branch, ticket_pattern, spec_dir, doc_map), `tracker.refine_ticket` (default true), `runtime.python`, `[[areas]]` (name, path, preset).
- TICKET = tracker ID matching `project.ticket_pattern` (e.g. `ABC-123`). Spec = `<project.spec_dir>/<TICKET>.md` — the ONLY progress record; spec beats memory.
- Map = `.codeangel/skills/build-loop/references/stages.toml`: per stage → `owner` skill, `entry`, `produces` (artefacts), legal exits, required checks. Read your stage's block before acting.
- `T` = `<runtime.python> .codeangel/skills/build-loop/scripts/transition.py` (any cwd inside the repo; Python ≥ 3.11):
  | command | use |
  |---|---|
  | `T status <TICKET>` | stage, attempt, legal exits + which checks still fail — run FIRST |
  | `T go <TICKET> <status> [--note "…"]` | the ONLY way to change stage; REFUSED (exit 1) if illegal or checks fail → fix what it lists |
  | `T log <TICKET> "<event>"` | record an event without a stage change |
  | `T docs <TICKET>` | docs the change must update (doc map) vs `## Docs impact` — the V8 gate |
  | `T evidence <TICKET>` | create the git-ignored evidence dir and print it (VERIFY, first) |
  | `T proof <TICKET> [--into FILE]` | render `## Evidence`, each text artefact inline, as the PR's `## Proof` block (REVIEW) |
  | `T show [STAGE]` | print the map |
  | `T init <TICKET> …` | create the spec (build-plan only) |
- Never hand-edit frontmatter `stage` / `last_status` / `attempt` / `mode` / `blocked_*` / `updated`; never write `## Log`.

## Stage guard
Stage skills: `T status <TICKET>` first. Stage ≠ the one you own → change nothing; return `<skill> <TICKET>: ticket is at <stage>`.

## Repo rules
Root `AGENTS.md` → `AGENTS.md` of every area the ticket touches (`[[areas]]` in the config) → the `docs/ai` + `docs/learnings` files their routers name.

## Gates
Each area's `AGENTS.md` → `## Done` lists its gates (lint / format on changed files, schema drift, full test suite, …); its `docs/ai/commands.md` says how to run them. Baseline = the same gates on the untouched base; VERIFY compares against it. An area without a gate for something (e.g. no schema) skips that check — say so in the report.

## Docs move with code
The PR that changes behaviour, structure, commands, deps, or setup also updates every doc that describes it — `README.md`, any `AGENTS.md`, `docs/ai/*`, learnings. `project.doc_map` (default `docs/ai/doc-map.toml`) says which docs describe which paths; `T docs` applies it; VERIFY refuses to pass until each mapped doc is updated or marked unchanged with a reason. A doc you notice is wrong (even unmapped) → fix it in the same change and list it in `## Docs impact`.

## Tools
- Tracker (Linear): the Linear MCP (tool names contain `linear`: `get_issue`, `list_comments`, `save_comment`, `save_issue`). Never an API client: no API key, no raw HTTP calls. No Linear MCP → ask the user to paste the ticket.
- Pull requests (GitHub): the GitHub MCP (tool names contain `github`) for finding, creating and updating a PR, reading its state and checks, marking it ready, rerunning failed jobs, reading failure logs, and listing merged PRs. Name the operation, not an exact tool: tool names differ between server versions.
- `gh` is the fallback when the GitHub MCP is unavailable, and the only tool for waits that need no judgement: `gh pr checks --watch` and `scripts/await_merge.py` make no model call per poll, where an MCP call per poll would.
- `codeangel init` installs both servers in `.mcp.json` (Claude Code) and `.cursor/mcp.json` (Cursor); the user signs in to each in the host.

## Evidence
Proof that a change works, gathered at VERIFY (V9) and shown in the PR. PLAN writes each AC as user behaviour and tags it `[proof: api|ui|cli|none — reason]`. VERIFY exercises the running system once per AC and records `## Evidence` (`| AC | kind | proof | note |`), artefacts in `<project.spec_dir>/evidence/<TICKET>/` (`ac-<n>-<kind>.txt|png`). Artefacts are local files, never committed: `T evidence <TICKET>` creates that directory with a `.gitignore` that ignores everything in it, and `evidence_recorded` refuses a tracked artefact or an unignored directory. REVIEW renders `## Proof` into the PR body with `T proof`, which puts the content of each text artefact in the description itself (no links to repository files). Every captured row needs a text artefact; a screenshot is optional and is only noted as kept locally.
- Each area's `docs/ai/evidence.md` holds the recipe: start · seed · auth · capture. Throwaway data only; auth is generated for the run, never a real account, never committed.
- Credentials, session ids, tokens, and cookies appear as `<redacted>` (the `evidence_recorded` check scans the section and text artefacts for credential-looking values).
- `not captured: <reason>` is the honest answer when the environment cannot show it; faked, edited, or reused proof is a violation.

## Tracker status
Linear tickets only; best-effort, never blocks (a failure is one log line). The coordinator makes both moves, not the stage skills:
- STARTUP sets the ticket to In Progress before PLAN, unless it is already started, Done or Canceled.
- After DONE, with the PR open and ready, `scripts/await_merge.py <pr>` waits for the merge (polls `gh pr view` every 5 min, up to 2 h, no model calls); exit 0 merged → set Done, 1 closed, 2 `gh` failing, 3 timeout → status unchanged, tell the user.

## Never
Weaken, delete, skip, or disable a test to pass VERIFY · edit AC to fit the code (use `## Plan amendments`) · add lint ignores to silence findings you caused · `--no-verify` · fake, hand-edit, or reuse evidence · force-push · commit to the base branch · merge the PR · call paid / external APIs or run data-mutating jobs unless the ticket requires it.

## Stop
Blocking question · needed change out of scope · CI wait > 30 min · required tool missing and not installable · workspace can't be aligned safely → `T go <TICKET> blocked --note "<blocker + exactly what the user must do>"` and return. Can't reach the user (e.g. running as a subagent) → same.

## Return
End with one line: `<skill> <TICKET>: <from> → <to> [<status>] — <one-line summary>`.
