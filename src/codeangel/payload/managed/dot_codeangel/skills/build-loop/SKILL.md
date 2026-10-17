---
name: build-loop
description: Coordinates ticket delivery for this repo — startup (worktree cleanup, ticket fetch from Linear and refinement of its title / description / acceptance criteria / out of scope, branch alignment), then dispatches the stage skills build-plan → build-implement → build-verify → build-review → build-learn over an enforced state machine, all state in a per-ticket spec file. Modes plan (stop after planning for approval, resume later) and immediate (run straight to done). Use when asked to build, implement, plan, work on, pick up, approve, or resume a ticket (ID like ABC-123).
metadata:
  claude-argument-hint: "<TICKET-ID> [plan|immediate]"
---

# build-loop — coordinator

Input: TICKET (upper-case it) + optional MODE (`plan` | `immediate`), from the invocation arguments or the user's message. No TICKET → ask, stop.
Read first: `references/contract.md` (shared rules, config, `T` commands). State machine: `references/stages.toml`. Spec template: `assets/spec-template.md`.
BASE = `project.base_branch` from `.codeangel/codeangel.toml` (default `main`).

## Modes
| invocation | spec stage | do |
|---|---|---|
| `plan`, or no mode | none | STARTUP → dispatch (PLAN ends at AWAITING_APPROVAL) |
| `immediate` | none | STARTUP → dispatch until DONE, no pause |
| no mode / `immediate` / user says approve, go, resume | AWAITING_APPROVAL | apply feedback in the message to the spec (+ `## Plan amendments`) → `T go <TICKET> approved` (mode := immediate) → dispatch |
| `plan` + feedback | AWAITING_APPROVAL | `T go <TICKET> revise --note "<feedback>"` → dispatch (build-plan revises, ends at AWAITING_APPROVAL) |
| any | PLAN…LEARN | STARTUP steps 1, 4–6 → dispatch |
| any | BLOCKED | user resolved `blocked_reason`? → `T go <TICKET> unblocked --note "<resolution>"` → dispatch; else restate the blocker, stop |
| any | DONE / CANCELLED | report status, stop |
| user abandons the ticket | any | `T go <TICKET> cancelled --note "<why>"` |

## STARTUP — coordinator only, in order (spec may not exist yet)
1. **Cleanup (best-effort)**: follow `.codeangel/skills/worktree-cleanup/SKILL.md`. Never blocks; keep its one-line summary for the final report.
2. **Spec**: the ticket's spec exists on this branch or on `origin/<ticket branch>` → read it; MODE + its stage pick the §Modes row. Its `branch` is TARGET.
3. **Ticket** (new spec only) — first source that works:
   1. Linear MCP (tool names contain `linear`): `get_issue` with `id` = TICKET and `fields` [title, description, url, status, labels, gitBranchName]; comments via `list_comments`. Suggested branch = `gitBranchName`.
   2. `LINEAR_API_KEY` set → `curl -s https://api.linear.app/graphql -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" -d '{"query":"{ issue(id: \"<TICKET>\") { identifier title description url branchName state { name } labels { nodes { name } } comments { nodes { body } } } }"}'`
   3. Another tracker MCP / CLI the user named → same fields.
   4. Else ask the user to paste title + description (+ branch name); stop. Never invent requirements.
   TARGET = the tracker's suggested branch name; none → `<ticket-lowercase>-<title-slug>`.
3b. **Refine the ticket** (new spec only; skip when `[tracker] refine_ticket = false` in the config, the source is not Linear, the ticket is Done / Canceled, or the description already contains `<!-- codeangel:refined -->`). Rewrite the tracker ticket so it reads well and states what "done" means. Best-effort: any failure → log one line, continue with the refined text in the spec only. Never blocks.
   1. **Draft** from the ticket text + comments only — restructure and clarify, never add requirements:
      - Title: one line, ≤ 80 chars, outcome-first, same meaning. Already clear → keep it verbatim.
      - Description, markdown, in this order (drop a section only when it would be empty):
        `## Summary` (1–3 sentences: what and why) · `## Context` (background, links, repro, constraints from the original) · `## Acceptance criteria` (`- [ ]` one observable, testable behaviour per line; behaviour the ticket states or clearly implies — nothing else) · `## Out of scope` (≥ 1 line: adjacent work the ticket does not ask for, or that the original excludes) · `## Open questions` (anything ambiguous or missing that changes the work — ask, don't guess).
      - Keep every link, image, code block, mention, number and name from the original. Don't drop information; move it under the right heading.
      - End the description with `<!-- codeangel:refined -->`.
   2. **Preserve the original** — first, post it as a comment on the ticket: `save_comment` (`issueId` = TICKET) body `Original ticket, before refinement

**Title:** <title>

<description verbatim>`. Comment not posted → do NOT overwrite; skip to the spec.
   3. **Write** — Linear MCP: `save_issue` (`id` = TICKET, `title`, `description`; change nothing else — not state, labels, assignee, priority). API: `issueUpdate` with `title` + `description` via the same GraphQL endpoint.
   4. Use the refined title as the ticket title from here on; hand build-plan the refined AC / out of scope as its starting draft, the Open questions as risks, and the ORIGINAL text as the verbatim ticket (§Ticket).
4. **Workspace alignment** — `git fetch --prune origin`; CUR = `git branch --show-current`; OWN = `git rev-list --count origin/<BASE>..HEAD`. Uncommitted changes not belonging to TICKET → stop. First matching case:
   | case | action |
   |---|---|
   | CUR == TARGET | ok |
   | TARGET is checked out in another worktree (`git worktree list --porcelain`) | stop: "<TICKET> lives in <path> — continue there" (never one branch in two worktrees) |
   | CUR is BASE / `main` / `master` (plain checkout) | `git switch TARGET` if it exists locally / on origin, else `git switch -c TARGET origin/<BASE>` |
   | OWN == 0 and CUR has no upstream (fresh agent / scratch worktree) | TARGET exists locally or on origin → `git switch TARGET`, then `git branch -d CUR`; else `git branch -m TARGET` |
   | else (CUR has own commits or is pushed) | stop, ask: renaming would orphan pushed work / an open PR |
   Base freshness: OWN == 0 and HEAD ≠ `origin/<BASE>` → `git merge --ff-only origin/<BASE>`. OWN > 0 and behind → tell build-plan to record a non-blocking risk; never rebase without asking.
   Some agent hosts (e.g. T3 Code) rename fresh worktree branches → build-review re-checks the branch name before every push.
5. **Env**: `<runtime.python> --version` is ≥ 3.11 (else fix `runtime.python` in the config — `T` needs it); each touched area's setup / health check from its `docs/ai/commands.md` passes, else set it up per that doc.
6. **Tools**: `gh auth status` fails → pass "REVIEW blocked: gh missing / unauthenticated" to build-plan as a non-blocking risk.

## Dispatch — repeat until a stop row
1. `T status <TICKET>` → stage S (new ticket: S = PLAN, no spec yet — build-plan runs `T init`).
2. Act on S:
   | S | owner | how |
   |---|---|---|
   | PLAN | `build-plan` | inline; pass MODE, original ticket text, refined title + AC + out of scope + open questions (if step 3b ran), TARGET, url, source, and STARTUP risks |
   | IMPLEMENT | `build-implement` | inline |
   | VERIFY | `build-verify` | ISOLATED: a fresh subagent that did not write the code (Claude Code: invoking the skill does this automatically; other harnesses: spawn a fresh subagent with the skill if possible, else inline) |
   | REVIEW | `build-review` | inline — may end the turn while waiting on CI |
   | LEARN | `build-learn` | inline |
   | AWAITING_APPROVAL | this skill | present the plan from the spec (AC, out of scope, affected files, test plan, docs impact, risks) → STOP, end turn |
   | BLOCKED | this skill | relay `blocked_reason` + what the user must do → STOP |
   | DONE / CANCELLED | this skill | final report → STOP |
3. Run a stage skill: invoke it as a skill with argument `<TICKET>` where your harness supports skills; otherwise read `.codeangel/skills/<owner>/SKILL.md` and follow it.
4. It returned → its return line says where the ticket went. It ended the turn on purpose (REVIEW waiting on CI) → end the turn too. Else → step 1.

## Final report — ≤ 15 lines
ticket · branch · PR URL + state (ready / draft + why) · AC met · verify attempts used · CI result · docs updated · learnings changed · follow-ups (out-of-scope items, baseline failures) · cleanup summary.
