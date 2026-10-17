# AGENTS.md — {{project_name}}

<!-- Agent-facing, always loaded. Budget ≤ 50 lines: routing + rules for EVERY task. Detail → docs/ai/ and area AGENTS.md. How these docs work: docs/ai/agent-docs.md. -->

{{project_name}} — TODO: one line on what this product is and for whom. All paths are repo-relative.

## Load order
root `AGENTS.md` → `AGENTS.md` of every area you touch → only the `docs/ai/` + `docs/learnings/` files their routers name. Never read everything upfront. Inside an area its AGENTS.md wins; the user beats all.

## Areas — read the area's AGENTS.md before working in it
| area | path | guide |
|---|---|---|
<!-- codeangel:areas — `codeangel add <preset> <path>` inserts rows above this line -->

## Router
| when | read |
|---|---|
| ticket ID (`ABC-123`) or build / plan / approve / resume a ticket | `.agents/skills/build-loop/SKILL.md` — follow it exactly |
| clean up worktrees, free disk | `.agents/skills/worktree-cleanup/SKILL.md` |
| where something lives, which area owns it, cross-area changes | `docs/ai/repo-map.md` |
| what to build, product scope | `docs/ai/product.md` |
| branches, commits, PRs, CI, worktrees | `docs/ai/git-workflow.md` |
| git / gh / worktree trouble | `docs/learnings/tooling.md` |
| recording a lesson; finding any area's learnings | `docs/learnings/README.md` |
| which docs a change must update | `docs/ai/doc-map.toml` |
| editing AGENTS.md, `docs/ai/`, learnings, skills, subagents | `docs/ai/agent-docs.md` |
| code standards for this repo | `docs/ai/code-standards.md` |

## Always
- Read code before changing it; match surrounding patterns; no drive-by refactors, renames, or fixes outside the task.
- Ticket conflicts with the code or the docs → ask.
- Never commit to `{{base_branch}}`, merge, force-push, or `--no-verify`. Commit / push / open PRs only when the user or build-loop asks.
- No secrets in code (env only). Never call paid / external APIs or run data-mutating jobs unless the task requires it.
- Docs move with code: a change that alters what `README.md`, any `AGENTS.md`, or `docs/ai/*` says updates that doc in the same change (`docs/ai/doc-map.toml`). Spot a stale doc → fix it.
- Follow `docs/ai/code-standards.md`.
- Done = the touched areas' `## Done` gates pass + docs in sync + non-obvious lessons filed per `docs/ai/agent-docs.md`.
