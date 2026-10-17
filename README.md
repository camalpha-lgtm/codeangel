# codeangel

An agent-agnostic AI software factory you install into any repo. One command gives a project:

- **Skills** in the open [Agent Skills](https://agentskills.io/specification) format (`.agents/skills/`), readable by Claude Code, Cursor and Codex: a `build-loop` coordinator plus one skill per stage (`build-plan`, `build-implement`, `build-verify`, `build-review`, `build-learn`) and `worktree-cleanup`.
- **An enforced build loop.** A state machine (`stages.toml` + `transition.py`) takes a ticket from plan to implement to verify to review to learn. It refuses illegal moves and unmet checks, and `plan` / `immediate` modes let you approve a plan before any code is written. Verification runs in an isolated subagent.
- **Self-maintaining agent docs.** Small `AGENTS.md` routers per area, `docs/ai/` reference, learnings, and a doc map so docs are updated in the same PR as the code they describe — the loop refuses to pass verification otherwise.
- **Presets** for common areas: `django-drf` (Django + Django REST Framework API) and `expo` (React Native).

codeangel is a package manager for this setup, not a runtime dependency: everything it installs is copied into your repo, so agents, teammates and CI work without codeangel installed.

## Install

Python 3.11+, installed with [uv](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/camalpha-lgtm/codeangel   # the `codeangel` command, on PATH
uv tool install /path/to/codeangel                               # or from a local checkout
uvx --from git+https://github.com/camalpha-lgtm/codeangel codeangel init   # or run once, no install
uv tool upgrade codeangel                                        # later
# developing codeangel itself:
uv sync && uv run pytest
```

## Start a project

```bash
mkdir my-app && cd my-app && git init
codeangel init --name my-app            # skills, scripts, AGENTS.md routers, docs scaffold
codeangel add django-drf backend        # Django + DRF skeleton, docs, gates, CI workflow
npx create-expo-app@latest frontend --template blank-typescript
codeangel add expo frontend             # docs, gates, CI workflow for the Expo app
codeangel doctor                        # validate the whole setup
```

Then fill the `TODO`s in `AGENTS.md` and `docs/ai/product.md`, and drive tickets with `/build-loop ABC-123 plan` (Claude Code) or by asking any agent to run the `build-loop` skill.

## Commands

| command | does |
|---|---|
| `codeangel init [--name N] [--base-branch B] [--python CMD]` | install managed files, scaffold project-owned docs, generate Claude shims |
| `codeangel add <preset> <path>` | add an area: files, doc-map rules, router rows, CI workflow, config entry (idempotent) |
| `codeangel update [--force]` | refresh managed files; a locally edited file is never overwritten — the new version lands next to it as `<file>.codeangel-new` |
| `codeangel sync [--check]` | regenerate the Claude Code skill shims from `.agents/skills/` |
| `codeangel doctor` | check config, lock, shims, state machine, doc map, doc links, `AGENTS.md` size |
| `codeangel presets` | list presets |

## What is managed and what is yours

| owner | files | change how |
|---|---|---|
| managed (hashes in `.agents/codeangel.lock.json`) | `.agents/skills/{build-*,worktree-cleanup}/**`, `.agents/sync-shims.py`, `.claude/agents/build-verifier.md`, `docs/ai/agent-docs.md` | in this repo, then `codeangel update` |
| generated | `.claude/skills/*/SKILL.md` | `codeangel sync` |
| project-owned | `AGENTS.md` files, other `docs/ai/*`, doc map, learnings, `README.md`, `.agents/codeangel.toml`, CI workflows | edit freely; created once, never touched again |

Project settings live in `.agents/codeangel.toml` (ticket pattern, spec dir, runtime Python, areas). Skills read each area's `AGENTS.md` → `## Done` for its gates, so they work for any stack.

## Develop codeangel

```bash
uv sync && uv run pytest
```

The shipped files live in `src/codeangel/payload/`: `managed/`, `scaffold/` and `presets/<name>/`. `dot_x` in a payload path installs as `.x`, and `{{name}}` in a path or file is a template variable. See `AGENTS.md`.
