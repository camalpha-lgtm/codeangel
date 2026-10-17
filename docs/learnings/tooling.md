# tooling (cross-cutting)

<!-- When: git, gh, worktree, or agent-host trouble. Area tooling (package managers, linters): <area>/docs/learnings/tooling.md. -->

- **Verify a fresh worktree's base against `origin/main`: `git fetch --prune origin && git rev-list --count HEAD..origin/main`.** — agent hosts can branch new worktrees from a stale remote-tracking ref (seen: T3 Code branching from a deleted `origin/master` while `origin/main` was ahead). build-loop STARTUP fast-forwards fresh branches. src: codeangel seed
- **`git worktree remove` (no `--force`) succeeds when only ignored files remain and deletes them; it refuses on untracked or modified files.** — ignored generated data (downloads, generated media, `.env`) is silently destroyed → inspect `git status --porcelain --ignored` first; worktree-cleanup only removes what `[worktrees] disposable` allows. src: codeangel seed
- **Don't commit symlinks.** — Git for Windows defaults to `core.symlinks=false` and native symlinks need Developer Mode; a committed symlink checks out as a one-line text file. Skills use generated shims instead (`docs/ai/agent-docs.md` → Skills). src: codeangel seed
