---
name: build-review
description: Stage REVIEW of build-loop for a ticket — commits the verified work, pushes, opens or updates a draft PR, waits for CI, marks the PR ready when green, and routes CI failures (baseline, flaky, code) per the state machine. Run by the build-loop coordinator, or directly for a ticket whose spec is at REVIEW.
metadata:
  claude-argument-hint: "<TICKET>"
---

# build-review — stage REVIEW

Read first: `.codeangel/skills/build-loop/references/contract.md`. Stage block: `T show REVIEW`.
Guard: `T status <TICKET>` = REVIEW; else return per contract.
Entry: latest `### Attempt` is PASS. Tools: GitHub MCP (tool names contain `github`) for the PR operations below; `gh` for the CI wait and as fallback (`references/contract.md` → Tools). No GitHub MCP and `gh auth status` fails → `T go <TICKET> blocked --note "enable the GitHub MCP (.mcp.json / .cursor/mcp.json) or install the GitHub CLI (https://cli.github.com) and run gh auth login"`.
BASE = `project.base_branch` from `.codeangel/codeangel.toml`.

1. **Commit** (tree dirty): `git add <Affected files> <spec> && git commit -m "<TICKET>: <imperative summary>"`. Then `git status --porcelain` must be empty.
2. **Branch check**: `git branch --show-current` == spec `branch`; differs (host auto-rename) → `git branch -m <spec branch>`.
3. **Push**: `git push -u origin HEAD`.
4. **PR**: spec `pr` empty and no PR exists for the branch (GitHub MCP: search / list PRs by head branch) → create a draft PR with the GitHub MCP: base `<BASE>`, head = the branch, title `<TICKET>: <title>`, body below. Body: ticket link · Summary · Acceptance criteria (checklist + evidence) · Out of scope · Docs updated (from `## Docs impact`) · Verification (V1–V8, attempts used) · Baseline failures still present · `Spec: <spec path>` · attribution lines your harness requires. Write the URL to frontmatter `pr` and `## Review`. PR exists → push only.
   T3 Code: `link_pull_request` available → call it with the PR URL.
5. **Wait for CI** on the pushed head:
   - T3 Code: `watch_pull_request` available → call it → `T go <TICKET> waiting_ci` → return "waiting on CI" and END THE TURN; on wake the coordinator re-dispatches here, continue at 6.
   - Else `gh pr checks <pr> --watch --interval 30` with the max tool timeout; rerun on tool timeout. This wait stays on `gh`: it makes no model call per poll, where one MCP call per poll would.
   - "no checks reported" → retry up to 3 min (registration lag); still none → `T go <TICKET> blocked --note "no CI checks on PR"`.
   - Total wait > 30 min → `T go <TICKET> blocked --note …`.
6. **Result** — record each run as `<run id> <sha> <conclusion>` under `## Review` → CI runs, then exactly one exit:
   | CI outcome | action | exit |
   |---|---|---|
   | all green | mark the PR ready (GitHub MCP) | `T go <TICKET> ci_green` → LEARN |
   | only baseline failures | keep draft | `T go <TICKET> ci_red_baseline --note "<checks>"` → LEARN |
   | infra / flaky (network, runner, cache; passes locally) | rerun the failed jobs (GitHub MCP) | `T go <TICKET> ci_flaky --note "<why>"` → back to 5 (once per REVIEW entry) |
   | code / env failure | excerpt: list the branch's latest workflow runs, then read the failed job's log, last ~80 lines (GitHub MCP) | `T go <TICKET> ci_red_code --note "<job>: <root cause>"` → IMPLEMENT (the loop comes back here; same PR) |
7. Return per contract.
