---
name: build-verify
description: Stage VERIFY of build-loop for a ticket — an independent verifier runs checks V1–V9 (cheap checks first: lint, schema drift, planned tests, acceptance-criteria audit, scope, hygiene, docs in sync; then the full suite and evidence from the running system) and records PASS or FAIL in the ticket's spec without touching code. Run by the build-loop coordinator (in an isolated subagent where supported), or directly for a ticket whose spec is at VERIFY.
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

## Order and cost — cheap checks first, so a failing attempt stays cheap
Gates per touched area (its `AGENTS.md` → `## Done`). CHANGED = `git diff --name-only <base_sha>` + `git ls-files --others --exclude-standard`.
1. **Tier 1, static and targeted** (seconds to a few minutes): V6, V1, V2, V7, V8, V5, V4. Run all of them and record every FAIL.
2. **Tier 2, expensive**: V3 (the full suite) and V9 (the running system). Run them ONLY when every Tier 1 check passed. Any Tier 1 FAIL → do not start V3 or V9: record them as `not run: fix Tier 1 first` and fail the attempt. IMPLEMENT changes the code anyway, so a suite or evidence run now would be stale on arrival.
3. **Re-attempt** (attempt ≥ 1): run `T delta <TICKET>` first. It lists the files changed since the last attempt. Re-run V1, V2, V4, V6 and V8 in full (cheap), but audit V5 and V7 only on the delta files and the ACs they touch; carry the other V5 lines forward verbatim, marked `unchanged since attempt N`. V9: see Evidence. A re-run is not an excuse to skip anything: an empty delta with an earlier FAIL means IMPLEMENT changed nothing → FAIL again with that as the root cause.
4. **Baseline is read, not stored.** `## Baseline` only says what CI showed on `base_sha`. A failure counts as baseline only when proven: the base's CI run failed the same check, or that single test id fails on a clean checkout of `base_sha` (`git worktree add --detach <scratch> <base_sha>`, run only that id with the area's environment, remove the worktree). Write the proof into `proven lazily` in `## Baseline`. Unproven → it is this ticket's failure.

## Checks
| id | check | how | pass when |
|---|---|---|---|
| V1 | lint / format | each area's lint / format gate on its CHANGED files | exit 0 and no file modified (changed files fully clean, incl. old findings inside them) |
| V2 | schema drift | each area's drift check (if it has a schema) | no drift beyond baseline; every changed model has its migration |
| V3 | full suite (Tier 2) | each area's full test command | runs (no collection / build errors); every failure proven baseline (above); none is a test this ticket added / modified |
| V4 | planned tests | run every Test plan id | all exist + pass |
| V5 | AC audit | per AC read the implementation AND its test(s); the test must assert the AC's observable outcome (not just "200 / renders") | every AC has evidence `AC-n: <test id>; <file>:<line>` |
| V6 | scope audit | `T scope <TICKET>` (it lists changed files outside Affected files, ignored Affected files and unmapped docs) + `git status --porcelain` | changed ⊆ Affected files + spec (evidence is git-ignored and never appears; a tracked or staged evidence file is a FAIL); no Out-of-scope item done |
| V7 | hygiene | read the full `git diff <base_sha>` | no debug output / breakpoints, commented-out code, bare TODOs, secrets (also in the evidence artefacts), absolute or machine-specific paths, unrelated churn; area AGENTS.md "Always" rules + `docs/ai` conventions hold; the project's code standards (`docs/ai/code-standards.md`) hold |
| V8 | docs in sync | `T docs <TICKET>`; then read every `updated` doc against the code (regenerate any generated table it names, e.g. a route list, and compare; run documented commands) and spot-check that `unchanged` reasons are true | `docs_synced` ✓ and every doc you read is accurate for the new code |
| V9 | evidence (Tier 2) | run the procedure below | `evidence_recorded` ✓ (preview: `T status`) and every artefact shows its AC's behaviour the way a user meets it |

## Evidence (V9) — proof from the running system, once per AC
A passing unit test is not evidence: V9 shows the change working as a user meets it. EVIDENCE = `<project.spec_dir>/evidence/<TICKET>/`: local to this checkout and never committed to the PR branch — REVIEW publishes the screenshots and videos to the branch `evidence/<TICKET>` and the PR description shows them.
0. Run `T evidence <TICKET>` first: it creates EVIDENCE with a `.gitignore` that ignores everything in it. Write artefacts only there.
1. Read each touched area's `docs/ai/evidence.md` (start · seed · auth · capture). Missing → derive the steps from its `docs/ai/commands.md` and name the gap in the report.
   Build capture tooling once: any helper you have to write (a browser driver, a seed or request script, a video converter) goes in `EVIDENCE/tools/` and the next attempt reuses it instead of rebuilding it. List everything the recipe did not give you under `recipe gaps` in the report: LEARN files it into the area's `docs/ai/evidence.md`, so no later ticket rebuilds it.
2. Start the system on throwaway data (a temp database or directory — never shared, production, or personal data). Seed only what the ACs need. Authenticate with the recipe's reusable auth, generated for this run (a session, token, or user made by the area's seed step) — never a real account, never committed.
3. Per AC, by its `[proof: …]` kind:
   - `api`: send the requests the AC describes (plus the unauthenticated / forbidden case when the AC names it); save request line, status, and the relevant body → `ac-<n>-api.txt`.
   - `ui`: drive the screen or page to the state the AC describes (the browser tool your harness provides, or the recipe's capture command); save a screenshot → `ac-<n>-ui.png`. For a flow, also record a short video (`ac-<n>-ui.mp4` or `.webm`, ≤ 50 MB) and a small `.gif` preview of it (`ac-<n>-ui.gif`), which the PR shows inline. Look at every screenshot and video frame for credentials, personal data and absolute paths before keeping it.
   - `cli`: run the command the AC names; save command line, output, and exit code → `ac-<n>-cli.txt`.
   - `none`: no artefact; the row says `n/a: <reason>`.
   Several kinds → one row per kind. Reviewers want to see screenshots and videos: capture one for every `ui` AC. Keep the text minimal: a text artefact holds only the lines that show the behaviour (≤ 6; the PR shows the first 6 in one collapsed block) and each row's note is one short sentence.
4. Redact credentials, session ids, tokens, and cookies as `<redacted>` in every artefact; no absolute or machine-specific paths. `evidence_recorded` scans for credential-looking values and refuses them.
5. Stop every process you started; delete the throwaway data.
6. Write `## Evidence`: `| AC-n | kind | <artefact paths, comma-separated> | <what it shows> |`. Cannot capture it (no browser, no device, a prerequisite the ticket does not provide) → `not captured: <specific reason>`; the PR shows it as a warning. Never invent output, edit a captured artefact, or reuse another ticket's or another checkout's.
   Re-attempt: re-capture every AC that failed, that exercises a file in `T delta`, or whose artefact you cannot vouch for. An AC whose code is outside the delta keeps its artefact from the previous attempt of THIS ticket; its row note ends `carried from attempt <N>: nothing it exercises changed`.
7. V9 FAILs when: an AC could be exercised and was not · the evidence contradicts the AC (error shown, wrong state) · `evidence_recorded` refuses · a secret is in an artefact. An environmental `not captured` is not a FAIL.

## Record + exit
1. Append `### Attempt <attempt+1> — PASS|FAIL` under `## Verify reports` (attempt from `T status`): one line per V (V1–V9); per FAIL a ≤ 20-line output excerpt, root cause, and the fix you expect from IMPLEMENT; V3 / V9 skipped by the Tier 1 rule read `not run: fix Tier 1 first`. On PASS include the V5 evidence lines and any `recipe gaps`.
2. FAIL → `T go <TICKET> fail --note "<V ids>: <root cause>"` → IMPLEMENT, +1 attempt; the cap auto-blocks. A wrong or missing doc is a V8 FAIL like any other.
3. PASS → tick every AC `- [x]` → `T go <TICKET> pass` (→ REVIEW; build-review commits).
4. Return per contract.
