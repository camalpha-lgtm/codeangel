# {{project_name}}

TODO: one paragraph — what this is and who it is for.

## Areas

| path | what | quick start |
|---|---|---|
<!-- codeangel:areas — `codeangel add <preset> <path>` inserts rows above this line -->

## Working with AI agents

Agents start at `AGENTS.md`, which routes them to each area's `AGENTS.md` and to reference docs in `docs/ai/`. The agent setup (skills, build loop, doc system) is managed by codeangel — `codeangel update` pulls improvements without touching project docs.

Ticket work runs through the build loop: plan → implement → verify → review → learn, tracked in `docs/specs/<TICKET>.md`.
- Claude Code: `/build-loop ABC-123 plan` (stop after the plan) or `/build-loop ABC-123 immediate` (run to a ready PR).
- Cursor / Codex: ask the agent to run the `build-loop` skill for the ticket (`.agents/skills/build-loop/`).

Docs move with code: a change that alters what a doc describes updates that doc in the same PR (`docs/ai/doc-map.toml`).
