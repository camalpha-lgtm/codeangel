---
name: build-plan
description: Stage PLAN of build-loop for a ticket — creates or revises the ticket's spec file — baseline of the untouched branch, research, acceptance criteria, out of scope, affected files, test plan, docs impact, risks. Run by the build-loop coordinator, or directly to (re)plan a ticket whose spec is at PLAN.
metadata:
  claude-argument-hint: "<TICKET>"
---

# build-plan — stage PLAN

Read first: `.codeangel/skills/build-loop/references/contract.md`. Stage block: `T show PLAN`.
Guard: new ticket (no spec) or `T status <TICKET>` = PLAN; else return per contract.
From the coordinator (new ticket): MODE, verbatim original ticket text, title, TARGET branch, url, source, STARTUP risks, and — when the coordinator refined the ticket — a draft of AC, out of scope and open questions.

1. **Init** (new spec only): `T init <TICKET> --mode <MODE> --title "<title>" --branch <TARGET> --base-sha $(git merge-base HEAD origin/<BASE>) --url <url> --source <linear-mcp|user-paste>`. Paste the original ticket verbatim under `## Ticket`.
2. **Research**: root `AGENTS.md` → each touched area's `AGENTS.md` → its `docs/ai` + `docs/learnings` files; read every file you'll change plus its tests.
3. **Baseline** on the untouched branch → `## Baseline`: run each touched area's `## Done` gates (commands in its `docs/ai/commands.md`) — record exit codes, test counts, failing test ids, collection / build errors, lint debt (read-only linters only: fixers would modify the tree), schema drift.
   Unusable baseline → `[blocking]` risk unless this ticket's scope fixes it: the test suite can't run · schema drift in an area whose models this ticket changes.
4. **Fill the spec** (artefacts: `T show PLAN` → produces):
   - Start from the coordinator's refined draft (if any): keep each AC / out-of-scope item that holds up against the code, fix or add the rest. Open questions → Risks.
   - Acceptance criteria: `- [ ] AC-n: …`, observable + testable (endpoint / screen / command + input → observable result or state change). Necessary-but-unstated (auth failures, missing objects, invalid input, isolation between users) → include, tag `(implied)`.
   - Out of scope: ≥ 1 item; name tempting adjacent work (known issues in learnings, baseline failures, refactors).
   - Affected files: every file to create / modify incl. tests, migrations, registrations, generated tables in docs — `create|modify` + why. Repo-relative paths.
   - Test plan: one row per test = `<file>::<test name>` as the area's test runner accepts it (file relative to the area dir) → AC ids → what it asserts. Every AC ≥ 1 test; every test ≥ 1 AC.
   - Docs impact: run `T docs <TICKET>` after filling Affected files → one row per mapped doc (`updated` if the change will alter what it says, else `unchanged` + why), plus any other doc the change will make stale (README.md, AGENTS.md files, `docs/ai/*`). Add every `updated` doc to Affected files too. Nothing maps → `- none: <why>`.
   - Risks / open questions: tag `[blocking]` / `[non-blocking]`, or `- none`. Include STARTUP risks.
   - Revising (entered via `revise`): apply the feedback from the last `[revise]` log note; record it under `## Plan amendments`.
   - Refined ticket (description contains `<!-- codeangel:refined -->`) and the final AC / out of scope differ from its `## Acceptance criteria` / `## Out of scope` → update those two sections in the tracker ticket (`save_issue`, replace only those sections; same rules as build-loop STARTUP 3b; best-effort, never blocks). The spec stays the source of truth.
5. **Exit**: `T go <TICKET> planned` (checks: plan complete, AC↔test mapping, no blocking risk). Unresolvable blocking item → `T go <TICKET> blocked --note …`. Then commit the spec locally: `git add <spec> && git commit -m "<TICKET>: Plan"`.
6. Return per contract (→ AWAITING_APPROVAL in plan mode, → IMPLEMENT in immediate mode).
