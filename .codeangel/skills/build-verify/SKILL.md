---
name: build-verify
description: Stage VERIFY of build-loop for a ticket — an independent verifier runs checks V1–V9 (lint, schema drift, full suite against baseline, planned tests, acceptance-criteria audit, scope, hygiene, docs in sync, evidence from the running system) and records PASS or FAIL in the ticket's spec without touching code. Run by the build-loop coordinator (in an isolated subagent where supported), or directly for a ticket whose spec is at VERIFY.
metadata:
  claude-argument-hint: "<TICKET>"
  claude-context: fork
  claude-agent: build-verifier
  claude-background: "false"
---

# build-verify — stage VERIFY (independent verifier)

Read first: `.codeangel/skills/build-loop/references/contract.md`. Stage block: `T show VERIFY`.
Guard: `T status <TICKET>` = VERIFY; else return per contract.

## Independence
- You judge the work against the SPEC, not the implementer's intent. Assume nothing passes until you have seen it pass.
- Edit ONLY the ticket's spec (report, AC ticks, `## Evidence`) and write evidence artefacts under `<project.spec_dir>/evidence/<TICKET>/` (git-ignored, never committed). Never modify code, tests, or migrations; never commit or push.
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
| V6 | scope audit | `git status --porcelain` + `git diff --name-only <base_sha>` | changed ⊆ Affected files + spec (evidence is git-ignored and never appears; a tracked or staged evidence file is a FAIL); no Out-of-scope item done |
| V7 | hygiene | read the full `git diff <base_sha>` | no debug output / breakpoints, commented-out code, bare TODOs, secrets (also in the evidence artefacts), absolute or machine-specific paths, unrelated churn; area AGENTS.md "Always" rules + `docs/ai` conventions hold; the project's code standards (`docs/ai/code-standards.md`) hold |
| V8 | docs in sync | `T docs <TICKET>`; then read every `updated` doc against the code (regenerate any generated table it names, e.g. a route list, and compare; run documented commands) and spot-check that `unchanged` reasons are true | `docs_synced` ✓ and every doc you read is accurate for the new code |
| V9 | evidence | run the procedure below | `evidence_recorded` ✓ (preview: `T status`) and every artefact shows its AC's behaviour the way a user meets it |

## Evidence (V9) — proof from the running system, once per AC
A passing unit test is not evidence: V9 shows the change working as a user meets it. EVIDENCE = `<project.spec_dir>/evidence/<TICKET>/`: local to this checkout and never committed — the PR description carries the content.
0. Run `T evidence <TICKET>` first: it creates EVIDENCE with a `.gitignore` that ignores everything in it. Write artefacts only there.
1. Read each touched area's `docs/ai/evidence.md` (start · seed · auth · capture). Missing → derive the steps from its `docs/ai/commands.md` and name the gap in the report.
2. Start the system on throwaway data (a temp database or directory — never shared, production, or personal data). Seed only what the ACs need. Authenticate with the recipe's reusable auth, generated for this run (a session, token, or user made by the area's seed step) — never a real account, never committed.
3. Per AC, by its `[proof: …]` kind:
   - `api`: send the requests the AC describes (plus the unauthenticated / forbidden case when the AC names it); save request line, status, and the relevant body → `ac-<n>-api.txt`.
   - `ui`: drive the screen or page to the state the AC describes (the browser tool your harness provides, or the recipe's capture command); save a text capture of the screen (visible text, URL, status; the recipe's capture command or the browser tool's snapshot) → `ac-<n>-ui.txt`; a screenshot `ac-<n>-ui.png` is optional and stays local.
   - `cli`: run the command the AC names; save command line, output, and exit code → `ac-<n>-cli.txt`.
   - `none`: no artefact; the row says `n/a: <reason>`.
   Several kinds → one row per kind. Every captured row needs a text capture: the PR description shows text (the first 60 lines), never images. Keep text proofs short.
4. Redact credentials, session ids, tokens, and cookies as `<redacted>` in every artefact; no absolute or machine-specific paths. `evidence_recorded` scans for credential-looking values and refuses them.
5. Stop every process you started; delete the throwaway data.
6. Write `## Evidence`: `| AC-n | kind | <artefact paths, comma-separated> | <what it shows> |`. Cannot capture it (no browser, no device, a prerequisite the ticket does not provide) → `not captured: <specific reason>`; the PR shows it as a warning. Never invent output, edit a captured artefact, or reuse another run's. A new attempt rewrites its artefacts and rows.
7. V9 FAILs when: an AC could be exercised and was not · the evidence contradicts the AC (error shown, wrong state) · `evidence_recorded` refuses · a secret is in an artefact. An environmental `not captured` is not a FAIL.

## Record + exit
1. Append `### Attempt <attempt+1> — PASS|FAIL` under `## Verify reports` (attempt from `T status`): one line per V (V1–V9); per FAIL a ≤ 20-line output excerpt, root cause, and the fix you expect from IMPLEMENT. On PASS include the V5 evidence lines.
2. FAIL → `T go <TICKET> fail --note "<V ids>: <root cause>"` → IMPLEMENT, +1 attempt; the cap auto-blocks. A wrong or missing doc is a V8 FAIL like any other.
3. PASS → tick every AC `- [x]` → `T go <TICKET> pass` (→ REVIEW; build-review commits).
4. Return per contract.
