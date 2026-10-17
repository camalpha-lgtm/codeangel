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

## Never
Weaken, delete, skip, or disable a test to pass VERIFY · edit AC to fit the code (use `## Plan amendments`) · add lint ignores to silence findings you caused · `--no-verify` · force-push · commit to the base branch · merge the PR · call paid / external APIs or run data-mutating jobs unless the ticket requires it.

## Stop
Blocking question · needed change out of scope · CI wait > 30 min · required tool missing and not installable · workspace can't be aligned safely → `T go <TICKET> blocked --note "<blocker + exactly what the user must do>"` and return. Can't reach the user (e.g. running as a subagent) → same.

## Return
End with one line: `<skill> <TICKET>: <from> → <to> [<status>] — <one-line summary>`.
