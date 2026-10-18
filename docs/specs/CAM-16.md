---
ticket: CAM-16
title: Keep build-loop proof out of git; show it only in the PR description
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-16/keep-build-loop-proof-out-of-git-show-it-only-in-the-pr
branch: camerondhobbs/cam-16-keep-build-loop-proof-out-of-git-show-it-only-in-the-pr
base_sha: ec2cb550abcbf7d6e99b877c37c07d1d07129358
pr:
stage: IMPLEMENT  # managed by transition.py — see stages.toml
last_status: planned  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-18T01:43Z
updated: 2026-10-18T01:45Z
---

# CAM-16: Keep build-loop proof out of git; show it only in the PR description

## Ticket
**Title:** Working changes/evidence to not persist files (refined in Linear to: Keep build-loop proof out of git; show it only in the PR description)

Files should not be added to git. Just their content of proof of acceptance criteria should be in github description, they should not go into the file repository.

## Acceptance criteria
- [ ] AC-1: When the verifier prepares evidence for a ticket (`T evidence <ticket>`), the evidence directory is created and git ignores everything in it, so `git status --porcelain` shows nothing for artefacts written there and `git add -A` stages none of them. [proof: cli]
- [ ] AC-2: `T go <ticket> pass` is refused when an evidence artefact is tracked or staged in git, or the evidence directory is not git-ignored, and says how to fix it. [proof: cli]
- [ ] AC-3: `T proof <ticket> [--into <body-file>]` renders the `## Proof` block with the content of each text artefact inline (fenced, first 60 lines), with no links to files in the repository and no `--repo` / `--sha` needed; running it again replaces only the marked block. [proof: cli]
- [ ] AC-4: A screenshot cannot go into the PR description, so a captured proof row must include at least one text artefact; `T go <ticket> pass` is refused for an image-only row and names the AC; the Proof block marks an image as kept locally and not committed. [proof: cli]
- [ ] AC-5: (implied) Re-running `T proof --into` where the artefacts are gone (a fresh checkout) leaves the existing Proof block in the body unchanged instead of replacing it with empty warnings. [proof: cli]
- [ ] AC-6: The stage skills tell agents the new flow: build-verify writes artefacts via `T evidence`, a text capture per captured row, and never commits them; build-review no longer adds the evidence directory to the commit and builds the PR body from `T proof` alone. [proof: none — skill text, asserted by tests]
- [ ] AC-7: (implied) A merged ticket's worktree can still be cleaned up: a new project's `.codeangel/codeangel.toml` lists `evidence/` among the disposable ignored files, and so does this repo's. [proof: cli]
- [ ] AC-8: (implied) This repo's installed copy of the harness is current (`codeangel update` ran) and managed files stay project-agnostic. [proof: cli]

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
| tests/cli/test_build_loop_evidence.py | modify | AC-1, AC-2, AC-4 tests; text-capture rule |
| tests/cli/test_build_loop_proof.py | modify | AC-3, AC-5 tests; inline rendering |
| tests/harness/test_evidence_payload.py | modify | AC-6, AC-7 payload text |
| .codeangel/ , .claude/ , docs/ai/agent-docs.md | modify | this repo's installed copy, refreshed by `codeangel update` (AC-8) |
| docs/ai/repo-map.md | modify | evidence row: local, untracked |
| docs/specs/CAM-16.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_build_loop_evidence.py::TestEvidenceIgnored::test_prepare_creates_an_ignoring_dir | AC-1 | `prepare_evidence` creates the dir with a `.gitignore` of `*`; in a real git repo `git status --porcelain` and `git add -A` show no artefact |
| tests/cli/test_build_loop_evidence.py::TestEvidenceIgnored::test_evidence_command_prints_the_dir | AC-1 | `T evidence ABC-1` exits 0 and prints the repo-relative dir |
| tests/cli/test_build_loop_evidence.py::TestEvidenceIgnored::test_unignored_dir_is_refused | AC-2 | artefacts present but no `.gitignore` → problem naming `T evidence` |
| tests/cli/test_build_loop_evidence.py::TestEvidenceIgnored::test_tracked_artefact_is_refused | AC-2 | an artefact added with `git add -f` → problem naming it |
| tests/cli/test_build_loop_evidence.py::TestEvidenceRecorded::test_image_only_row_is_refused | AC-4 | a row of only a `.png` → problem naming the AC and asking for a text capture |
| tests/cli/test_build_loop_evidence.py::TestEvidenceRecorded::test_text_plus_image_row_is_accepted | AC-4 | text + png row → no problems |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_shows_text_inline_without_repo_links | AC-3, AC-4 | text inline in a fence, no `github.com` / `blob` link, image marked local, warnings kept |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_splicing_replaces_only_the_marked_block | AC-3 | a second render replaces only the marked block |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_proof_command_writes_into_a_body_file | AC-3 | `T proof ABC-1 --into FILE` (no `--repo` / `--sha`) writes the block |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_missing_artefacts_keep_the_existing_block | AC-5 | artefacts deleted, existing block present → body unchanged; no block yet → warning rendered |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_verify_defines_v9_for_every_proof_kind | AC-6 | V9 text names `T evidence`, the text capture, untracked artefacts |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_review_does_not_commit_evidence_and_renders_the_proof_section | AC-6 | review text: `T proof <TICKET> --into`, no evidence path in the commit step, no `--sha` |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_worktree_cleanup_treats_evidence_as_disposable | AC-7 | the scaffold toml and this repo's toml list `evidence/` |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_repo_installed_copy_is_current | AC-8 | this repo's `.codeangel/` copies of transition.py, the build-verify / build-review skills and contract.md equal the payload |

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
<!-- - <UTC time> <what changed> — <why> -->

## Verify reports
<!--
### Attempt 1 — PASS|FAIL
- V1 lint/format: PASS|FAIL <detail>
- V2 migrations: PASS|FAIL
- V3 full suite: PASS|FAIL <n passed, m failed; failures ⊆ baseline?>
- V4 planned tests: PASS|FAIL
- V5 AC audit: PASS|FAIL
  - AC-1: <test node id>; <file>:<line>
- V6 scope audit: PASS|FAIL
- V7 hygiene: PASS|FAIL
- V8 docs in sync: PASS|FAIL
- V9 evidence: PASS|FAIL <rows captured / not captured>
- Failure excerpt / root cause / next action: <...>
-->

## Evidence
<!-- Written by VERIFY: one row per AC. kind = api | ui | cli | none. proof = comma-separated artefact paths under <spec_dir>/evidence/<TICKET>/, or `not captured: <reason>`, or `n/a: <reason>` (kind none only). -->
| AC | kind | proof | note |
|---|---|---|---|
| AC-1 | <api, ui, cli or none> | <docs/specs/evidence/<TICKET>/ac-1-api.txt> | <what the proof shows> |

## Review
- PR: <url>
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
- 2026-10-18T01:43Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-16-keep-build-loop-proof-out-of-git-show-it-only-in-the-pr, base=ec2cb550ab
- 2026-10-18T01:45Z PLAN → IMPLEMENT [planned] attempt=0/5
