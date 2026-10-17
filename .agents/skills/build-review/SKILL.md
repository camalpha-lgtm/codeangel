---
name: build-review
description: Stage REVIEW of build-loop for a ticket — commits the verified work, pushes, opens or updates a draft PR, waits for CI, marks the PR ready when green, and routes CI failures (baseline, flaky, code) per the state machine. Run by the build-loop coordinator, or directly for a ticket whose spec is at REVIEW.
metadata:
  claude-argument-hint: "<TICKET>"
---

# build-review — stage REVIEW

Read first: `.agents/skills/build-loop/references/contract.md`. Stage block: `T show REVIEW`.
Guard: `T status <TICKET>` = REVIEW; else return per contract.
Entry: latest `### Attempt` is PASS. `gh auth status` fails → `T go <TICKET> blocked --note "install the GitHub CLI (https://cli.github.com) and run gh auth login"`.
BASE = `project.base_branch` from `.agents/codeangel.toml`.

1. **Commit** (tree dirty): `git add <Affected files> <spec> && git commit -m "<TICKET>: <imperative summary>"`. Then `git status --porcelain` must be empty.
2. **Branch check**: `git branch --show-current` == spec `branch`; differs (host auto-rename) → `git branch -m <spec branch>`.
3. **Push**: `git push -u origin HEAD`.
4. **PR**: spec `pr` empty and `gh pr view --json url` finds none → body to a temp file → `gh pr create --draft --base <BASE> --title "<TICKET>: <title>" --body-file <tmp>`. Body: ticket link · Summary · Acceptance criteria (checklist + evidence) · Out of scope · Docs updated (from `## Docs impact`) · Verification (V1–V8, attempts used) · Baseline failures still present · `Spec: <spec path>` · attribution lines your harness requires. Write the URL to frontmatter `pr` and `## Review`. PR exists → push only.
   T3 Code: `link_pull_request` available → call it with the PR URL.
5. **Wait for CI** on the pushed head:
   - T3 Code: `watch_pull_request` available → call it → `T go <TICKET> waiting_ci` → return "waiting on CI" and END THE TURN; on wake the coordinator re-dispatches here, continue at 6.
   - Else `gh pr checks <pr> --watch --interval 30` with the max tool timeout; rerun on tool timeout.
   - "no checks reported" → retry up to 3 min (registration lag); still none → `T go <TICKET> blocked --note "no CI checks on PR"`.
   - Total wait > 30 min → `T go <TICKET> blocked --note …`.
6. **Result** — record each run as `<run id> <sha> <conclusion>` under `## Review` → CI runs, then exactly one exit:
   | CI outcome | action | exit |
   |---|---|---|
   | all green | `gh pr ready <pr>` | `T go <TICKET> ci_green` → LEARN |
   | only baseline failures | keep draft | `T go <TICKET> ci_red_baseline --note "<checks>"` → LEARN |
   | infra / flaky (network, runner, cache; passes locally) | `gh run rerun <id> --failed` | `T go <TICKET> ci_flaky --note "<why>"` → back to 5 (once per REVIEW entry) |
   | code / env failure | excerpt: `gh run list --branch "$(git branch --show-current)" --limit 5 --json databaseId,conclusion,headSha,workflowName` → `gh run view <id> --log-failed \| tail -n 80` | `T go <TICKET> ci_red_code --note "<job>: <root cause>"` → IMPLEMENT (the loop comes back here; same PR) |
7. Return per contract.
