# git workflow

<!-- When: branching, committing, opening PRs, reading CI, managing worktrees. -->

## Branches
- Base all work on `origin/main`; verify a fresh worktree's base before trusting it (`docs/learnings/tooling.md`).
- Ticket branch = the tracker's suggested branch name (Linear `gitBranchName`); build-loop STARTUP aligns the worktree to it.
- One branch per worktree; never work one ticket from two worktrees.

## Commits
- Imperative, sentence case, ≤ 72 chars; ticket work prefixes `<TICKET>: `.
- Stage explicit paths, never `git add -A`. Never `--no-verify`.

## PRs
- Base `main`, title `<TICKET>: <title>` (trackers link on the ID). Open as draft; mark ready only when CI is green. Never merge, never force-push.
- Needs the GitHub MCP signed in (`.mcp.json` / `.cursor/mcp.json`, installed by `codeangel init`) and the GitHub CLI authenticated (`gh auth status`) for the CI wait and merge watch.

## CI — `.github/workflows/`
| workflow | runs |
|---|---|
| `agents.yml` | Claude skill shims in sync with `.codeangel/skills` (`python .codeangel/sync-shims.py --check`) |
<!-- codeangel:ci — `codeangel add` inserts a row per area workflow above this line; add other workflows by hand (the doc map flags this table when workflows change) -->

## Worktrees
- Agent hosts (T3 Code, Claude Code, Codex, Cursor) may create one worktree per task; each area's `<area>/docs/ai/commands.md` lists its per-worktree setup.
- Worktrees of merged PRs: `.codeangel/skills/worktree-cleanup/SKILL.md` (also runs at build-loop startup).
