---
name: build-learn
description: Stage LEARN of build-loop for a ticket — turns the ticket's verify failures, CI failures, plan amendments, and surprises into durable learnings and doc fixes in the right area, tightens the doc map, then commits and pushes them to the PR. Run by the build-loop coordinator, or directly for a ticket whose spec is at LEARN.
metadata:
  claude-argument-hint: "<TICKET>"
---

# build-learn — stage LEARN

Read first: `.codeangel/skills/build-loop/references/contract.md`, `docs/ai/agent-docs.md` (layers, learnings format, promotion). Stage block: `T show LEARN`.
Guard: `T status <TICKET>` = LEARN; else return per contract.

1. **Harvest** from the spec: FAIL attempts + root causes, CI failures, plan amendments, surprises, anything you had to discover that the AGENTS.md files / `docs/ai` / learnings didn't say, docs that proved wrong.
2. **Filter**: keep only non-obvious + reusable + verified. Drop ticket narrative, anything already documented, anything obvious from a quick code read. Zero is valid → `none: <why>`.
3. **File** in the right AREA (`docs/learnings/` for cross-cutting, `<area>/docs/learnings/` otherwise; index: `docs/learnings/README.md`): grep every learnings dir first → update / merge instead of appending; fix or delete entries this ticket disproved; delete known issues it resolved. Wrong `docs/ai` fact → fix it there.
4. **Docs drift**: any doc that turned out wrong or stale during the ticket (README.md, any AGENTS.md, `docs/ai/*`) → fix it now. It went stale without a doc-map rule catching it → add or widen the rule in `project.doc_map` so the next change catches it.
5. **Promote / route** per `docs/ai/agent-docs.md`: standing rule → area `docs/ai/<topic>.md` (delete the learning); AGENTS.md "Always" only if nearly every task in the area needs it. New file → index row + router row.
6. **Record**: fill `## Learnings` (`<file>: <change>` per edit, or `none: <why>`) → `T go <TICKET> learned` (→ DONE).
7. **Ship**: changed docs end with a newline and carry no trailing whitespace. Commit `<TICKET>: Record learnings` (learnings, `docs/ai`, doc map, README.md, AGENTS.md files, spec; skills changed → re-run `<runtime.python> .codeangel/sync-shims.py`) → branch name == spec `branch` → push to the same PR.
8. T3 Code: the PR was watched with `watch_pull_request` → call `unwatch_pull_request`.
9. Return per contract (the coordinator writes the final report).
