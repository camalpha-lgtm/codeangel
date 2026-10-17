# agent docs — how this documentation system works

<!-- When: adding or editing any AGENTS.md, docs/ai/*, */docs/learnings/*, README.md, skills, or subagents. Audience: agents — optimise for tokens + retrieval, not prose. Managed by codeangel: change it in the codeangel repo, then `codeangel update`. -->

## Layers — one set per area (repo root + each `[[areas]]` in `.codeangel/codeangel.toml`)
| layer | holds | loaded | budget |
|---|---|---|---|
| `<area>/AGENTS.md` | one-line scope · router table · "Always" rules nearly every task in the area needs · `## Done` gates | root: always; area: on entering it | ≤ 50 lines |
| `<area>/docs/ai/<topic>.md` | curated, prescriptive reference: how things are + how to do them | when a router row matches | ≤ 150 lines, then split |
| `<area>/docs/learnings/<topic>.md` | evidence-backed gotchas from real work (format below) | when a router or index row matches | ≤ ~60 bullets, then split |
| `README.md` (root) | HUMAN entry point: what it is, quick start, how to drive agents — concise prose allowed; no agent-only detail | humans; agents when setup / layout / agent workflow changes | ≤ ~60 lines |

## Rules
- Every `docs/ai` file has a row in its area AGENTS.md router; every learnings file has a row in `docs/learnings/README.md` (root index) or its area's learnings README. No row = invisible.
- Each file opens with `# <topic>` + `<!-- When: … -->` naming the trigger that should load it.
- Paths are always repo-relative (`<area>/docs/ai/commands.md`), never relative to the file.
- One fact, one home: link instead of duplicating. Area facts live in the area; cross-cutting facts at root.
- Only verified facts (checked against code or by running the command); label anything unverified.
- Dense: tables + bullets, imperative mood, no narrative.

## Learnings — format + filing
One bullet = one lesson: `- **<rule: imperative, specific>** — <why: cause / evidence>. src: <TICKET | commit sha | file | YYYY-MM-DD>`
Domain files may add `## Known issues` (verify before relying; delete when fixed): `- <defect> — <impact / fix hint>. src: …`
- Admit only: non-obvious + reusable + verified (observed, not guessed). Reject: ticket narrative, anything already in an AGENTS.md or `docs/ai`, anything obvious from a quick code read.
- Most specific area + topic file wins. Grep every learnings dir first → update / merge instead of adding a near-duplicate.
- Proven wrong or stale → fix or delete in the same change. Known issue fixed → delete it. Code area deleted → delete its learnings.
- New file → index row (+ router row). Became a standing rule → promote (below), delete the learning.

## Docs move with code
- Any change that alters what a doc says updates that doc in the SAME change — code, docs, and learnings ship together.
- `project.doc_map` (default `docs/ai/doc-map.toml`) maps code globs → docs that describe them. build-loop applies it: PLAN lists `## Docs impact` (`T docs`), IMPLEMENT updates the docs, VERIFY (V8, check `docs_synced`) refuses to pass until every mapped doc is `updated` or `unchanged` + reason, LEARN adds a rule whenever a doc went stale unnoticed.
- New doc that describes code → add a doc-map rule for it. New area → add rules pointing at its docs (`codeangel add` does this for presets).

## Promotion / demotion
learning (observed gotcha) → area `docs/ai/<topic>.md` once it is a standing rule (delete the learning) → area AGENTS.md "Always" only if nearly every task in the area needs it. AGENTS.md over budget → move content down a layer. Stale → fix or delete in the same change that proves it.

## Managed vs project-owned (codeangel)
| owner | files | change how |
|---|---|---|
| codeangel (managed, hashes in `.codeangel/codeangel.lock.json`) | `.codeangel/skills/{build-*,worktree-cleanup}/**`, `.codeangel/sync-shims.py`, `.claude/agents/build-verifier.md`, this file | in the codeangel repo → `codeangel update` (locally edited managed files are never overwritten; the new version lands as `<file>.codeangel-new`) |
| generated | `.claude/skills/*/SKILL.md` shims | never by hand → `<runtime.python> .codeangel/sync-shims.py` (or `codeangel sync`) |
| project | `AGENTS.md` files, other `docs/ai/*`, the doc map, learnings, `README.md`, `.codeangel/codeangel.toml`, project-specific skills | edit freely; `codeangel` scaffolds them once and never touches them again |

## Skills — agent-agnostic source, generated harness shims
- Canonical: `.codeangel/skills/<name>/SKILL.md` (+ `scripts/`, `references/`, `assets/`) per the [Agent Skills spec](https://agentskills.io/specification); Codex + Cursor read it natively.
- Claude Code reads only `.claude/skills/` → each canonical skill gets a generated shim (Claude-only frontmatter + "read the canonical file"). CI runs `sync-shims.py --check`.
- Frontmatter: only spec keys (`name` = directory name, `description` ≤ 1024 chars, `license`, `compatibility`, `metadata`, `allowed-tools`). Harness-only fields go in `metadata` as `claude-<field>` (`claude-argument-hint`, `claude-context: fork`, `claude-agent`, `claude-background`).
- No symlinks: Git for Windows defaults to `core.symlinks=false`, so a committed symlink checks out as a one-line text file; shims also carry harness-only fields symlinks can't.
- Skill bodies are self-contained: repo-relative paths, never assume conversation history (a skill may run in a subagent).
- Project-specific skill → `.codeangel/skills/<name>/` (unmanaged) → run the shim sync → commit both.

## Code standards
The rule lives in the root `AGENTS.md`. The detail lives in `docs/ai/code-standards.md`. `build-implement` follows those standards. `build-verify` V7 checks them. Where a tool can enforce a standard, the project's linter config does, and the same change updates that config.

## Build loop = coordinator + stage skills
`build-loop` coordinates (startup, modes, dispatch); one skill per stage (`build-plan`, `build-implement`, `build-verify`, `build-review`, `build-learn`) owns that stage's procedure. Shared rules: `.codeangel/skills/build-loop/references/contract.md`; stage → owner, exits, checks, artefacts: `.codeangel/skills/build-loop/references/stages.toml` (enforced by `.codeangel/skills/build-loop/scripts/transition.py`). For Linear tickets, `build-loop` also moves the ticket to In Progress at startup and to Done once the PR merges; it waits for the merge with `.codeangel/skills/build-loop/scripts/await_merge.py`, which polls GitHub without model calls. Project specifics come from `.codeangel/codeangel.toml` and each area's `AGENTS.md` → `## Done`.
Subagents only where isolation pays: `build-verify` runs as `build-verifier` (fresh context, judges the spec not the author, edits only the spec). Other stages stay inline — they talk to the user (plan approval), end the turn to wait on CI (review), or need continuity. To isolate another stage: add `claude-context: fork` + `claude-agent` to its metadata, add a `.claude/agents/` definition, re-sync.
