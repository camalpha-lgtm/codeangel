---
name: build-implement
description: Stage IMPLEMENT of build-loop for a ticket — writes the planned tests first, then the code, strictly inside the spec's affected files, and updates the docs the change touches; on re-entry fixes the root cause from the latest verify report or CI failure. Run by the build-loop coordinator, or directly for a ticket whose spec is at IMPLEMENT.
metadata:
  claude-argument-hint: "<TICKET>"
---

# build-implement — stage IMPLEMENT

Read first: `.codeangel/skills/build-loop/references/contract.md`. Stage block: `T show IMPLEMENT`.
Guard: `T status <TICKET>` = IMPLEMENT; else return per contract.
Work list: spec `## Test plan` + `## Affected files`. Rules: the touched areas' `AGENTS.md` + `docs/ai` conventions, including the project's code standards (`docs/ai/code-standards.md`).

1. **Re-entry** (`last_status` = `fail` or `ci_red_code`): read the latest `### Attempt` in `## Verify reports` or the CI failure in `## Review` FIRST. Fix the root cause, not the symptom. Same check failed twice with the same signature → change approach (re-read code + learnings, revisit the design) instead of retrying the same fix.
2. **Tests first**: write the planned tests → run them → confirm each fails for the EXPECTED reason (assertion / status, not import, fixture, or build errors).
3. **Implement** until the targeted tests pass (the area's single-test command from its `docs/ai/commands.md`).
4. **Scope**: touch only `## Affected files`. Another file within the ticket's intent → add it + a `## Plan amendments` line. Outside the intent → don't; list it under `## Out of scope` as a follow-up.
5. **AC wrong or infeasible**: never edit an AC silently — `## Plan amendments` entry with the reason; changes user-visible behaviour → `T go <TICKET> blocked --note …`.
6. **Schema changed**: generate migrations with the area's command (read its dry-run first); never hand-write or edit existing migrations.
7. **Docs move with code**: update every `## Docs impact` row marked `updated` alongside the code (README.md, AGENTS.md files, `docs/ai/*`, learnings, generated tables such as route lists). Then `T docs <TICKET>`: docs the REAL diff maps to that have no row → add a row and update them (or mark `unchanged` + why). Skills changed → `<runtime.python> .codeangel/sync-shims.py`.
8. **Format**: run each touched area's lint / format gate on the changed files until clean. The verifier fails unformatted work.
9. **Exit**: `T go <TICKET> implemented` (checks every Test plan id resolves). Return per contract.
