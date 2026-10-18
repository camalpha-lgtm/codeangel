---
ticket: CAM-16
title: Keep build-loop proof out of git; show it only in the PR description
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-16/keep-build-loop-proof-out-of-git-show-it-only-in-the-pr
branch: camerondhobbs/cam-16-keep-build-loop-proof-out-of-git-show-it-only-in-the-pr
base_sha: ec2cb550abcbf7d6e99b877c37c07d1d07129358
pr: https://github.com/camalpha-lgtm/codeangel/pull/6
stage: REVIEW  # managed by transition.py — see stages.toml
last_status: pass  # exit status that entered the current stage
attempt: 1   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-18T01:43Z
updated: 2026-10-18T02:06Z
---

# CAM-16: Keep build-loop proof out of git; show it only in the PR description

## Ticket
**Title:** Working changes/evidence to not persist files (refined in Linear to: Keep build-loop proof out of git; show it only in the PR description)

Files should not be added to git. Just their content of proof of acceptance criteria should be in github description, they should not go into the file repository.

## Acceptance criteria
- [x] AC-1: When the verifier prepares evidence for a ticket (`T evidence <ticket>`), the evidence directory is created and git ignores everything in it, so `git status --porcelain` shows nothing for artefacts written there and `git add -A` stages none of them. [proof: cli]
- [x] AC-2: `T go <ticket> pass` is refused when an evidence artefact is tracked or staged in git, or the evidence directory is not git-ignored, and says how to fix it. [proof: cli]
- [x] AC-3: `T proof <ticket> [--into <body-file>]` renders the `## Proof` block with the content of each text artefact inline (fenced, first 60 lines), with no links to files in the repository and no `--repo` / `--sha` needed; running it again replaces only the marked block. [proof: cli]
- [x] AC-4: A screenshot cannot go into the PR description, so a captured proof row must include at least one text artefact; `T go <ticket> pass` is refused for an image-only row and names the AC; the Proof block marks an image as kept locally and not committed. [proof: cli]
- [x] AC-5: (implied) Re-running `T proof --into` where the artefacts are gone (a fresh checkout) leaves the existing Proof block in the body unchanged instead of replacing it with empty warnings. [proof: cli]
- [x] AC-6: The stage skills tell agents the new flow: build-verify writes artefacts via `T evidence`, a text capture per captured row, and never commits them; build-review no longer adds the evidence directory to the commit and builds the PR body from `T proof` alone. [proof: none — skill text, asserted by tests]
- [x] AC-7: (implied) A merged ticket's worktree can still be cleaned up: a new project's `.codeangel/codeangel.toml` lists `evidence/` among the disposable ignored files, and so does this repo's. [proof: cli]
- [x] AC-8: (implied) This repo's installed copy of the harness is current (`codeangel update` ran) and managed files stay project-agnostic. [proof: cli]
- [x] AC-9: (user feedback) The `## Proof` block in the PR is minimal: per AC one bold line with a one-sentence title, the row note, and each text artefact as a collapsed excerpt of at most 10 lines; the verify and review skills ask for equally short notes and PR bodies. [proof: cli]

## Out of scope
- Deleting or rewriting evidence already committed by CAM-13 (`docs/specs/evidence/CAM-13/`) or its spec rows.
- Hosting screenshots anywhere (image upload to GitHub, Linear, or another service); images stay local only.
- Changing which ACs need proof, the `[proof: …]` tags, the V9 failure conditions, or credential scanning.
- Editing a project's own `.gitignore` or the disposable list of projects that already exist (`update` never touches project-owned files; they add `evidence/` by hand).
- Bumping `codeangel.__version__`.

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/scripts/transition.py | modify | `T evidence`; ignore + tracked checks and text-capture rule in `evidence_recorded`; inline-only `T proof` that keeps an existing block when artefacts are gone |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/stages.toml | modify | VERIFY produces / `evidence_recorded` text: untracked artefacts, a text capture per row |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/contract.md | modify | Evidence rules: untracked, `T evidence`, `T proof` without repo / sha |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/assets/spec-template.md | modify | `## Evidence` comment: untracked artefacts, text capture |
| src/codeangel/payload/managed/dot_codeangel/skills/build-verify/SKILL.md | modify | `T evidence` first; text capture per row; scope audit no longer lists the evidence dir |
| src/codeangel/payload/managed/dot_codeangel/skills/build-review/SKILL.md | modify | commit excludes evidence; PR body proof from `T proof` only |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | build-loop summary: evidence is local, content shown in the PR |
| src/codeangel/payload/presets/django-drf/docs/ai/evidence.md | modify | ui capture also writes a text file; artefacts are untracked |
| src/codeangel/payload/presets/expo/docs/ai/evidence.md | modify | same |
| src/codeangel/payload/scaffold/dot_codeangel/codeangel.toml | modify | `evidence/` in `[worktrees] disposable` |
| .codeangel/codeangel.toml | modify | same, for this repo |
| tests/support/evidence.py | modify | artefact helper prepares the ignored evidence dir |
| tests/cli/test_build_loop_evidence.py | modify | AC-4 tests; existing rows carry a text capture |
| tests/cli/test_build_loop_evidence_ignored.py | create | AC-1, AC-2 tests (the existing file already holds two test classes) |
| tests/cli/test_build_loop_proof.py | modify | AC-3, AC-5 tests; inline rendering |
| tests/harness/test_evidence_payload.py | modify | AC-6, AC-7 payload text |
| .codeangel/ (incl. codeangel.lock.json), .claude/ , docs/ai/agent-docs.md | modify | this repo's installed copy, refreshed by `codeangel update` (AC-8) |
| docs/ai/repo-map.md | modify | evidence row: local, untracked |
| docs/specs/CAM-16.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_build_loop_evidence_ignored.py::TestEvidenceIgnored::test_prepare_creates_an_ignoring_dir | AC-1 | `prepare_evidence` creates the dir with a `.gitignore` of `*`; in a real git repo `git status --porcelain` and `git add -A` show no artefact |
| tests/cli/test_build_loop_evidence_ignored.py::TestEvidenceIgnored::test_evidence_command_prints_the_dir | AC-1 | `T evidence ABC-1` exits 0 and prints the repo-relative dir |
| tests/cli/test_build_loop_evidence_ignored.py::TestEvidenceIgnored::test_unignored_dir_is_refused | AC-2 | artefacts present but no `.gitignore` → problem naming `T evidence` |
| tests/cli/test_build_loop_evidence_ignored.py::TestEvidenceIgnored::test_tracked_artefact_is_refused | AC-2 | an artefact added with `git add -f` → problem naming it |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_image_only_row_is_refused | AC-4 | a row of only a `.png` → problem naming the AC and asking for a text capture |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_text_plus_image_row_is_accepted | AC-4 | text + png row → no problems |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_shows_text_inline_without_repo_links | AC-3, AC-4 | text inline in a fence, no `github.com` / `blob` link, image marked local, warnings kept |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_splicing_replaces_only_the_marked_block | AC-3 | a second render replaces only the marked block |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_proof_command_writes_into_a_body_file | AC-3 | `T proof ABC-1 --into FILE` (no `--repo` / `--sha`) writes the block |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_missing_artefacts_keep_the_existing_block | AC-5 | artefacts deleted, existing block present → body unchanged; no block yet → warning rendered |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_verify_defines_v9_for_every_proof_kind | AC-6 | V9 text names `T evidence`, the text capture, untracked artefacts |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_review_does_not_commit_evidence_and_renders_the_proof_section | AC-6 | review text: `T proof <TICKET> --into`, no evidence path in the commit step, no `--sha` |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_worktree_cleanup_treats_evidence_as_disposable | AC-7 | the scaffold toml and this repo's toml list `evidence/` |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_repo_installed_copy_is_current | AC-8 | this repo's `.codeangel/` copies of transition.py, the build-verify / build-review skills and contract.md equal the payload |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_stays_short | AC-9 | a 70-line artefact shows 10 lines in a `<details>` block, a long AC title is cut to its first sentence, the whole one-AC section ≤ 30 lines |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_skills_ask_for_a_minimal_proof | AC-9 | build-verify and build-review texts ask for ≤ 10 lines and short notes / bodies |

## Docs impact
<!-- `T docs <TICKET>` lists docs mapped from the change (docs/ai/doc-map.toml). One row per doc; status updated or unchanged; unchanged needs a reason. Nothing maps → "- none: <why>". -->
| doc | status | note |
|---|---|---|
| docs/ai/repo-map.md | updated | the `docs/specs/evidence/<TICKET>/` row says the artefacts are local and untracked |
| docs/ai/agent-docs.md | updated | build-loop summary: evidence stays local, its content is shown in the PR (installed copy of the managed doc) |
| README.md | unchanged | its build-loop bullet describes the loop, not where evidence is stored |
| AGENTS.md | unchanged | no command, layout or payload-rule change |
| docs/ai/code-standards.md | unchanged | no new standard |

## Risks / open questions
- [non-blocking] A screenshot cannot be shown in the PR (GitHub offers no API to attach an image without committing it); the verifier must also capture text for each row, which for a pure-visual AC (layout, colour) can only describe the screen. Accepted: the ticket asks for content in the description, not files.
- [non-blocking] Evidence lives only in the worktree that ran VERIFY and is deleted when the merged worktree is cleaned up; a later `T proof` in another checkout cannot rebuild it (AC-5 keeps the old block in that case).
- [non-blocking] Existing projects keep their own `[worktrees] disposable` list; until they add `evidence/`, worktree-cleanup skips a merged worktree that still holds evidence and lists it.
- [non-blocking] Evidence from CAM-13 stays tracked (out of scope), so the "no tracked artefact" check only looks at the current ticket's directory.

## Baseline
- base_sha: ec2cb550abcbf7d6e99b877c37c07d1d07129358
- gates: `uv run pytest` → exit 0; 111 passed, 0 failed; `uv run ruff check src tests` → exit 0; `uv run ruff format --check src tests` → exit 0 (74 files formatted)
- known failures: none
- lint debt: none
- schema drift: n/a (no schema)

## Plan amendments
- 2026-10-18 IMPLEMENT: ignore tests moved to a new file tests/cli/test_build_loop_evidence_ignored.py and the text-capture tests stay in TestEvidenceGate — code standards allow at most two test classes per file. Test ids updated; AC unchanged.
- 2026-10-18 REVIEW: user asked for a much shorter PR proof (screenshots / video welcome, text minimal) → added AC-9 and re-entered IMPLEMENT via ci_red_code. Screenshots stay unembeddable without committing a file, so they remain a local note.

## Verify reports
### Attempt 1 — PASS
- V1 lint/format: PASS `uv run ruff check src tests` exit 0; `ruff format --check src tests` exit 0 (75 files formatted), nothing modified
- V2 migrations: PASS n/a, no schema in any area
- V3 full suite: PASS `uv run pytest` 120 passed, 0 failed (baseline 111 passed, 0 failed); no failures
- V4 planned tests: PASS all 14 Test plan ids exist and pass (14 passed in a targeted run)
- V5 AC audit: PASS
  - AC-1: tests/cli/test_build_loop_evidence_ignored.py::TestEvidenceIgnored::test_prepare_creates_an_ignoring_dir; tests/cli/test_build_loop_evidence_ignored.py:24 (+ test_evidence_command_prints_the_dir :36)
  - AC-2: tests/cli/test_build_loop_evidence_ignored.py::TestEvidenceIgnored::test_unignored_dir_is_refused; tests/cli/test_build_loop_evidence_ignored.py:43 (+ test_tracked_artefact_is_refused :54)
  - AC-3: tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_shows_text_inline_without_repo_links; tests/cli/test_build_loop_proof.py:62 (+ test_splicing_replaces_only_the_marked_block :77, test_proof_command_writes_into_a_body_file :93)
  - AC-4: tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_image_only_row_is_refused; tests/cli/test_build_loop_evidence.py:118 (+ test_text_plus_image_row_is_accepted :128; image note asserted at tests/cli/test_build_loop_proof.py:62)
  - AC-5: tests/cli/test_build_loop_proof.py::TestProofRendering::test_missing_artefacts_keep_the_existing_block; tests/cli/test_build_loop_proof.py:106
  - AC-6: tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_review_does_not_commit_evidence_and_renders_the_proof_section; tests/harness/test_evidence_payload.py:46 (+ test_verify_defines_v9_for_every_proof_kind :19)
  - AC-7: tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_worktree_cleanup_treats_evidence_as_disposable; tests/harness/test_evidence_payload.py:57
  - AC-8: tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_repo_installed_copy_is_current; tests/harness/test_evidence_payload.py:66 (all seven installed managed files also diffed identical to the payload)
- V6 scope audit: PASS every changed file is in Affected files or is the spec; `.claude/` shims unchanged (no SKILL frontmatter change); evidence dir is git-ignored, absent from `git status`, none tracked or staged; no Out-of-scope item done (CAM-13 evidence untouched, version not bumped)
- V7 hygiene: PASS no debug output, commented-out code, TODOs, secrets, or machine-specific paths in the diff or the artefacts; payload stays project-agnostic (standards tests pass). Non-blocking nit: tests/cli/test_build_loop_evidence.py:129-130 repeats the same `shot = evidence.artefact("ac-1-ui.png", PNG)` line (harmless duplicate; REVIEW may drop one)
- V8 docs in sync: PASS `T docs CAM-16` docs_synced ready; docs/ai/repo-map.md and docs/ai/agent-docs.md read against the code and accurate; README.md and AGENTS.md unchanged reasons hold (no command, layout or payload-rule change)
- V9 evidence: PASS AC-1, AC-2, AC-3, AC-4, AC-5, AC-7, AC-8 captured from a throwaway `codeangel init` project (git repo, spec DEMO-1) and this repo; AC-6 n/a (skill text). `T docs`/`evidence_recorded` preview ready.
- Failure excerpt / root cause / next action: none. Note: `codeangel doctor` warns that `docs/ai/evidence.md` is missing for the agent-docs reference; this warning predates the ticket and is not in scope.

### Attempt 2 — PASS
- V1 lint/format: PASS `uv run ruff check src tests` exit 0; `ruff format --check src tests` exit 0 (75 files formatted), nothing modified
- V2 migrations: PASS n/a, no schema in any area
- V3 full suite: PASS `uv run pytest` 122 passed, 0 failed (baseline 111 passed, 0 failed); no failures
- V4 planned tests: PASS all 16 Test plan ids exist and pass (incl. the two AC-9 tests, 2 passed in a targeted run)
- V5 AC audit: PASS
  - AC-1 to AC-8: unchanged since Attempt 1 apart from the proof renderer; evidence lines as in Attempt 1 (tests re-run in the full suite)
  - AC-9: tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_stays_short; tests/cli/test_build_loop_proof.py:78 (asserts 10 lines kept, `60 more lines`, long title cut to its first sentence, whole section <= 30 lines, lines <= 160 chars) (+ tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_skills_ask_for_a_minimal_proof :57; tests/cli/test_build_loop_proof.py:62 asserts `<details>` and the bold `**AC-1 — ...**` line)
  - note: AC-3 still says "first 60 lines"; AC-9 (user feedback, later) lowers that to 10 and the implementation follows AC-9. Treated as superseded, not a failure.
- V6 scope audit: PASS changed files are all in Affected files or the spec; installed copies in `.codeangel/` match the payload apart from CR line endings and the lock hashes match; evidence dir git-ignored, none tracked or staged; no Out-of-scope item done
- V7 hygiene: PASS no debug output, commented-out code, TODOs, secrets, or machine-specific paths in the diff or the artefacts; no comments or docstrings added (standards tests pass)
- V8 docs in sync: PASS `T docs CAM-16` docs_synced ready; docs/ai/repo-map.md and agent-docs.md still accurate (the AC-9 change alters PR rendering only, no command, layout or rule); unchanged reasons hold
- V9 evidence: PASS AC-1..AC-5, AC-7..AC-9 re-captured in this attempt from a throwaway `codeangel init` git project (spec DEMO-1, forced to VERIFY to read the real gate output) and this repo; each artefact <= 10 lines; AC-6 n/a (skill text). The throwaway project was deleted.
- Failure excerpt / root cause / next action: none.

## Evidence
<!-- Written by VERIFY: one row per AC. kind = api | ui | cli | none. proof = comma-separated artefact paths under <spec_dir>/evidence/<TICKET>/, or `not captured: <reason>`, or `n/a: <reason>` (kind none only). -->
| AC | kind | proof | note |
|---|---|---|---|
| AC-1 | cli | docs/specs/evidence/CAM-16/ac-1-cli.txt | `T evidence` makes an ignoring dir; git status and `git add -A` show no artefact. |
| AC-2 | cli | docs/specs/evidence/CAM-16/ac-2-cli.txt | The pass gate refuses an unignored dir and a tracked artefact, with the fix. |
| AC-3 | cli | docs/specs/evidence/CAM-16/ac-3-cli.txt | `T proof --into` needs no repo or sha, has no repo links, and a rerun replaces only the block. |
| AC-4 | cli | docs/specs/evidence/CAM-16/ac-4-cli.txt | An image-only row is refused naming the AC; the png is noted as kept locally. |
| AC-5 | cli | docs/specs/evidence/CAM-16/ac-5-cli.txt | With artefacts gone the existing block is kept; with no block a warning is rendered. |
| AC-6 | none | n/a: skill text, asserted by tests | covered by the harness tests in V5 |
| AC-7 | cli | docs/specs/evidence/CAM-16/ac-7-cli.txt | `evidence/` is disposable in this repo and in a fresh `init` project. |
| AC-8 | cli | docs/specs/evidence/CAM-16/ac-8-cli.txt | Installed harness files equal the payload; tests pass and shims are in sync. |
| AC-9 | cli | docs/specs/evidence/CAM-16/ac-9-cli.txt | A 70-line artefact shows 10 lines collapsed, the long AC title is cut, the body is 45 lines for two ACs. |

## Review
- PR: https://github.com/camalpha-lgtm/codeangel/pull/6
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
- 2026-10-18T01:43Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-16-keep-build-loop-proof-out-of-git-show-it-only-in-the-pr, base=ec2cb550ab
- 2026-10-18T01:45Z PLAN → IMPLEMENT [planned] attempt=0/5
- 2026-10-18T01:51Z IMPLEMENT → VERIFY [implemented] attempt=0/5
- 2026-10-18T01:57Z VERIFY → REVIEW [pass] attempt=0/5
- 2026-10-18T01:57Z REVIEW → REVIEW [waiting_ci] attempt=0/5
- 2026-10-18T01:58Z REVIEW → IMPLEMENT [ci_red_code] attempt=1/5 — user feedback: PR proof must be minimal (short per-AC line, collapsed capped excerpt), not long transcripts
- 2026-10-18T02:01Z IMPLEMENT → VERIFY [implemented] attempt=1/5
- 2026-10-18T02:06Z VERIFY → REVIEW [pass] attempt=1/5
