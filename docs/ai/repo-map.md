# repo map

<!-- When: locating code, deciding which area owns a change, planning a change that spans areas. -->

| path | what | guide |
|---|---|---|
| `src/codeangel/` | CLI package grouped into `commands`, `doctor`, `install`, `io`, and `project` | `AGENTS.md` |
| `tests/` | `cli`, `install`, `io`, `project`, `harness`, and `support`; at most two test classes per file | `docs/ai/code-standards.md` |
| `docs/ai/code-standards.md` | object-oriented design, no comments, size limits, gates | `AGENTS.md` |
| `README.md` | human entry point: what it is, quick start, how to drive agents | `docs/ai/agent-docs.md` |
| `docs/ai/` | cross-cutting agent reference; `doc-map.toml` = which docs describe which code | this dir |
| `docs/learnings/` | cross-cutting learnings + index of every area's learnings | `docs/learnings/README.md` |
| `docs/specs/<TICKET>.md` | build-loop spec + progress log, one per ticket | `.codeangel/skills/build-loop/SKILL.md` |
| `docs/specs/evidence/<TICKET>/` | proof the verifier captures per acceptance criterion (transcripts, screenshots); local and git-ignored, never committed to the PR branch; screenshots and videos are published to the branch `evidence/<TICKET>` and shown in the PR description | `.codeangel/skills/build-verify/SKILL.md` |
| `.codeangel/` | `codeangel.toml` (project config) · `skills/` (canonical agent skills) · `sync-shims.py` | `docs/ai/agent-docs.md` → Skills |
| `.mcp.json`, `.cursor/mcp.json` | MCP servers (Linear, GitHub) for Claude Code · Cursor; installed and kept current by codeangel | `docs/ai/agent-docs.md` → Skills |
| `.claude/skills/`, `.claude/agents/` | GENERATED Claude Code skill shims · Claude subagents | `docs/ai/agent-docs.md` → Skills |
| `.github/workflows/` | CI | `docs/ai/git-workflow.md` |
| `.github/scripts/` | CI helper scripts (`bump_version.py`: release version bump and tag) | `docs/ai/git-workflow.md` |
<!-- codeangel:areas — `codeangel add <preset> <path>` inserts rows above this line -->

## Area shape (same everywhere)
`<area>/AGENTS.md` (router + always-rules + `## Done` gates) · `<area>/docs/ai/<topic>.md` (curated reference) · `<area>/docs/learnings/<topic>.md` (gotchas from real work). Rules: `docs/ai/agent-docs.md`.

## Cross-area changes
A client needs a new / changed API → API area first (schema + service + tests + its route table), then the client. One ticket may touch several areas: follow every touched area's AGENTS.md and pass every area's `## Done` gates.
