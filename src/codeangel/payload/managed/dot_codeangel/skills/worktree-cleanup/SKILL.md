---
name: worktree-cleanup
description: Remove local git worktrees whose GitHub PRs (authored by the current user) are merged — the checkout, per-area environments (e.g. virtualenvs), the local branch, and the linked T3 thread (archived). Guarded; never forces. Use when asked to clean up / prune worktrees or free disk space; build-loop runs it automatically at startup.
---

# worktree-cleanup

Deletes only what is provably merged AND disposable. Any guard fails → skip that worktree, report why. Never `--force`. Best-effort: errors skip one worktree, never abort the caller.
Config (`.codeangel/codeangel.toml`): `[worktrees] disposable` (ignored-file patterns safe to delete) and each `[[areas]] pre_remove` (commands run before removal; `{worktree}` = the worktree path).

## 1. Inputs
- `gh auth status` fails → output `worktree-cleanup skipped: gh unavailable`, stop.
- `git fetch --prune origin`
- PRS = `gh pr list --author @me --state merged --limit 100 --json number,url,headRefName,headRefOid`
- WTS = `git worktree list --porcelain` → path, HEAD, branch, `locked`. First entry = main worktree.

## 2. Candidates
Worktree whose branch == some PRS `headRefName`. Exclude: the main worktree; the current one (`git rev-parse --show-toplevel`); detached HEAD; the base branch / `main` / `master`; `locked`.

## 3. Guards — ALL must pass
| id | check | pass |
|---|---|---|
| G1 nothing unmerged | `git -C <wt> rev-parse HEAD` vs PR `headRefOid` | equal, or `git -C <wt> rev-list --count <headRefOid>..HEAD` == 0 |
| G2 no uncommitted work | `git -C <wt> status --porcelain` | empty |
| G3 only disposable ignored files | `git -C <wt> status --porcelain --ignored` → `!!` entries | each matches a `[worktrees] disposable` pattern. Anything else (generated data, downloads, `.env*`, media) may be valuable → skip and list them |
| G4 not in use | T3 Code tools available: `t3_thread_list` with statuses preparing/queued/starting/running/waiting | no thread whose `linkedPullRequest` url == PR url |

## 4. Remove — per candidate, in this order
1. Area cleanup: run every `[[areas]] pre_remove` command with `{worktree}` = `<wt>` (e.g. removing a path-keyed virtualenv). Must precede step 3 — such tools key environments by project path. Note sizes first (`du -sh`) for the report.
2. `du -sh <wt>` for the report.
3. `git worktree remove <wt>` (no `--force`; ignored files are deleted with it). "Permission denied" / "Directory not empty" → a process (IDE, server, shell) holds files → report, skip; do not force.
4. `git branch -D <branch>` (`-D` needed for squash merges; G1 proved nothing is unmerged).
5. T3 Code tools available: thread whose `linkedPullRequest` url == PR url → `t3_thread_organize` action `archive` (reversible; its worktree is gone).
After all candidates: `git worktree prune`.

NEVER: delete remote branches; touch the main worktree; remove worktrees of open or closed-unmerged PRs; delete outside `git worktree remove` / configured `pre_remove` commands (no `rm -rf`).

## 5. Report — one block
```
worktree-cleanup: removed <n>, freed ~<MB>, skipped <m>
  removed  <path> · <branch> · PR #<n> · ~<MB>
  skipped  <path> · <branch> · <guard / reason>
```
No candidates → `worktree-cleanup: nothing to clean`.
