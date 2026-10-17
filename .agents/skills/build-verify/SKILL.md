---
name: build-verify
description: Stage VERIFY of build-loop for a ticket — an independent verifier runs checks V1–V8 (lint, schema drift, full suite against baseline, planned tests, acceptance-criteria audit, scope, hygiene, docs in sync) and records PASS or FAIL in the ticket's spec without touching code. Run by the build-loop coordinator (in an isolated subagent where supported), or directly for a ticket whose spec is at VERIFY.
metadata:
  claude-argument-hint: "<TICKET>"
  claude-context: fork
  claude-agent: build-verifier
  claude-background: "false"
---

# build-verify — stage VERIFY (independent verifier)

Read first: `.agents/skills/build-loop/references/contract.md`. Stage block: `T show VERIFY`.
Guard: `T status <TICKET>` = VERIFY; else return per contract.

## Independence
- You judge the work against the SPEC, not the implementer's intent. Assume nothing passes until you have seen it pass.
- Edit ONLY the ticket's spec (report + AC ticks). Never modify code, tests, or migrations; never commit or push.
- A lint / format fixer modifies files → V1 = FAIL ("IMPLEMENT left unformatted changes"); leave the fixer output in place.

## Checks — EVERY check, EVERY attempt; gates per touched area (its `AGENTS.md` → `## Done`), relative to `## Baseline`
CHANGED = `git diff --name-only <base_sha>` + `git ls-files --others --exclude-standard`.
| id | check | how | pass when |
|---|---|---|---|
| V1 | lint / format | each area's lint / format gate on its CHANGED files | exit 0 and no file modified (changed files fully clean, incl. old findings inside them) |
| V2 | schema drift | each area's drift check (if it has a schema) | no drift beyond baseline; every changed model has its migration |
| V3 | full suite | each area's full test command | runs (no collection / build errors); failing set ⊆ baseline failures; none is a test this ticket added / modified |
| V4 | planned tests | run every Test plan id | all exist + pass |
| V5 | AC audit | per AC read the implementation AND its test(s); the test must assert the AC's observable outcome (not just "200 / renders") | every AC has evidence `AC-n: <test id>; <file>:<line>` |
| V6 | scope audit | `git status --porcelain` + `git diff --name-only <base_sha>` | changed ⊆ Affected files + spec; no Out-of-scope item done |
| V7 | hygiene | read the full `git diff <base_sha>` | no debug output / breakpoints, commented-out code, bare TODOs, secrets, absolute or machine-specific paths, unrelated churn; area AGENTS.md "Always" rules + `docs/ai` conventions hold; the project's code standards (`docs/ai/code-standards.md`) hold |
| V8 | docs in sync | `T docs <TICKET>`; then read every `updated` doc against the code (regenerate any generated table it names, e.g. a route list, and compare; run documented commands) and spot-check that `unchanged` reasons are true | `docs_synced` ✓ and every doc you read is accurate for the new code |

## Record + exit
1. Append `### Attempt <attempt+1> — PASS|FAIL` under `## Verify reports` (attempt from `T status`): one line per V; per FAIL a ≤ 20-line output excerpt, root cause, and the fix you expect from IMPLEMENT. On PASS include the V5 evidence lines.
2. FAIL → `T go <TICKET> fail --note "<V ids>: <root cause>"` → IMPLEMENT, +1 attempt; the cap auto-blocks. A wrong or missing doc is a V8 FAIL like any other.
3. PASS → tick every AC `- [x]` → `T go <TICKET> pass` (→ REVIEW; build-review commits).
4. Return per contract.
