---
ticket: CAM-19
title: Show screenshots and videos as proof in the PR description
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-19/show-screenshots-and-videos-as-proof-in-the-pr-description
branch: camerondhobbs/cam-19-show-screenshots-and-videos-as-proof-in-the-pr-description
base_sha: 840c4b691bebbbfb149ab907b22d447f3d6e8e14
pr:
stage: IMPLEMENT  # managed by transition.py — see stages.toml
last_status: planned  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-18T09:28Z
updated: 2026-10-18T09:29Z
---

# CAM-19: Show screenshots and videos as proof in the PR description

## Ticket
**Title:** Ac4 is not right (user feedback on CAM-16 / PR #6); refined in Linear to: Show screenshots and videos as proof in the PR description

> Ac4 is not right. I still like to see screenshots and videos of evidence in PR description. I just hope they aren't commited. If they have to be though that is fine. I need screenshots and video evidence.

Follow-up to CAM-16, stacked on its branch (PR #6 is open and unmerged; CAM-16 is DONE and cannot be reopened). CAM-16's AC-4 said images cannot go in the PR description and required a text capture beside every screenshot.

## Acceptance criteria
- [ ] AC-1: `T publish <ticket>` pushes the screenshots and videos in the ticket's evidence directory to the branch `evidence/<ticket>` on origin and prints the commit sha; it never touches the checked-out branch, the index or the working tree (`git status` and `HEAD` are the same before and after), and a second run adds a commit on top of the first (a fast-forward). [proof: cli]
- [ ] AC-2: The media is not part of the pull request: after `T publish`, the PR branch's tree contains no evidence file, and the media exists only on `evidence/<ticket>`. [proof: cli]
- [ ] AC-3: `T proof <ticket> --repo OWNER/REPO --sha SHA [--into FILE]` shows each screenshot inline in the `## Proof` block as an image pinned to SHA, and each video as a `▶ name` link pinned to SHA with any `.gif` / `.png` preview of it inline; the block contains no `<video>` tag (GitHub strips it for repository files); the rest stays minimal (one line per AC, excerpts of at most 6 lines in one collapsed block). [proof: cli]
- [ ] AC-4: A proof row made only of a screenshot or only of a video passes `T go <ticket> pass`; a text capture is no longer required (this replaces CAM-16's AC-4). [proof: cli]
- [ ] AC-5: (implied) Without `--repo` / `--sha`, or for media that was never published, `T proof` shows each screenshot or video as one short "kept locally" line and exits 0, so the PR body stays short. [proof: cli]
- [ ] AC-6: (implied) `T publish` with no screenshot or video does nothing and exits 0; a file over 50 MB is refused and named. [proof: cli]
- [ ] AC-7: The stage skills tell agents the flow: build-verify captures screenshots and videos (a short video, an optional `.gif` preview) and keeps them uncommitted; build-review runs `T publish` before `T proof --repo --sha` and keeps the PR branch free of media. [proof: none — skill text, asserted by tests]
- [ ] AC-8: (implied) This repo's installed copy of the harness is current (`codeangel update` ran) and managed files stay project-agnostic. [proof: cli]

## Out of scope
- Capturing screenshots and videos (the per-area recipes in `docs/ai/evidence.md` only get a note that videos are allowed); no recorder dependency in codeangel.
- Deleting evidence CAM-13 already committed, or deleting `evidence/<ticket>` branches after merge.
- Credential scanning of images and videos (the verifier is told to check them by eye; only text artefacts are scanned).
- Changing which ACs need proof, V9 failure conditions, or the minimal text layout from CAM-16.
- Embedding `<video>` players (not rendered by GitHub for repository files).

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/scripts/transition.py | modify | `T publish`; media rendering by SHA; drop the text-capture rule; video suffixes |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/stages.toml | modify | `evidence_recorded` text: no text-capture rule, media allowed |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/contract.md | modify | Evidence rules + `T publish` / `T proof` rows |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/assets/spec-template.md | modify | `## Evidence` comment |
| src/codeangel/payload/managed/dot_codeangel/skills/build-verify/SKILL.md | modify | capture screenshots / videos; drop the text-capture rule |
| src/codeangel/payload/managed/dot_codeangel/skills/build-review/SKILL.md | modify | `T publish` then `T proof --repo --sha` |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | build-loop summary: media is published to `evidence/<TICKET>` |
| src/codeangel/payload/presets/django-drf/docs/ai/evidence.md | modify | UI proof is the screenshot; videos allowed |
| src/codeangel/payload/presets/expo/docs/ai/evidence.md | modify | same |
| tests/cli/test_build_loop_publish.py | create | AC-1, AC-2, AC-6 tests |
| tests/cli/test_build_loop_proof.py | modify | AC-3, AC-5 tests |
| tests/cli/test_build_loop_evidence.py | modify | AC-4 tests (image-only / video-only rows pass) |
| tests/harness/test_evidence_payload.py | modify | AC-7 payload text |
| .codeangel/ (incl. codeangel.lock.json), .claude/ , docs/ai/agent-docs.md | modify | this repo's installed copy, refreshed by `codeangel update` (AC-8) |
| docs/ai/repo-map.md | modify | evidence row: media published to `evidence/<TICKET>` |
| docs/learnings/process.md | modify | drop the now-wrong "screenshots cannot be embedded" claim |
| docs/specs/CAM-19.md | modify | this spec |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_build_loop_publish.py::TestPublish::test_media_lands_on_the_evidence_branch | AC-1 | after `publish_evidence` the origin has `evidence/ABC-1` holding the png and mp4 under `ABC-1/` and the call returns its sha |
| tests/cli/test_build_loop_publish.py::TestPublish::test_checkout_is_left_untouched | AC-1 | `HEAD`, `git status --porcelain` and the index are identical before and after |
| tests/cli/test_build_loop_publish.py::TestPublish::test_second_publish_fast_forwards | AC-1 | the second sha has the first as its parent and the push needs no force |
| tests/cli/test_build_loop_publish.py::TestPublish::test_pr_branch_tree_has_no_media | AC-2 | `git ls-tree -r HEAD` lists no evidence file after publishing; the branch tree on origin lists only the media |
| tests/cli/test_build_loop_publish.py::TestPublish::test_publish_command_prints_the_sha | AC-1 | `T publish ABC-1` exits 0 and prints a 40-hex sha |
| tests/cli/test_build_loop_publish.py::TestPublishLimits::test_no_media_is_a_noop | AC-6 | text-only evidence → exit 0, nothing pushed |
| tests/cli/test_build_loop_publish.py::TestPublishLimits::test_oversized_media_is_refused | AC-6 | a file over the limit → refused, file named, nothing pushed |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_published_screenshot_is_shown_inline | AC-3 | `![..](https://github.com/o/r/blob/SHA/ABC-1/ac-1-ui.png?raw=true)` appears under its AC line |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_published_video_is_a_link_with_a_preview | AC-3 | `▶ ac-1-ui.mp4` link pinned to SHA, the `.gif` inline, no `<video>` tag, section stays short |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_unpublished_media_is_a_local_note | AC-5 | without repo / sha: one "kept locally" line per file, no github link |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_proof_command_accepts_repo_and_sha | AC-3 | `T proof --repo --sha --into` exits 0 and writes the image link |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_image_only_row_is_accepted | AC-4 | a png-only row → no problems |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_video_only_row_is_accepted | AC-4 | an mp4-only row → no problems |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_skills_describe_screenshots_videos_and_publishing | AC-7 | verify: screenshots, videos, `.gif`, uncommitted; review: `T publish` before `T proof`, `--repo`, `--sha` |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_repo_installed_copy_is_current | AC-8 | the installed copies equal the payload |

## Docs impact
<!-- `T docs <TICKET>` lists docs mapped from the change (docs/ai/doc-map.toml). One row per doc; status updated or unchanged; unchanged needs a reason. Nothing maps → "- none: <why>". -->
| doc | status | note |
|---|---|---|
| docs/ai/repo-map.md | updated | the `docs/specs/evidence/<TICKET>/` row says media is published to `evidence/<TICKET>` for the PR |
| docs/ai/agent-docs.md | updated | build-loop summary: media is published to `evidence/<TICKET>`, never committed to the PR branch (installed copy of the managed doc) |
| docs/learnings/process.md | updated | the CAM-16 lesson claiming screenshots cannot be embedded is now wrong |
| README.md | unchanged | its build-loop bullet describes the loop, not where evidence is stored |
| AGENTS.md | unchanged | no command, layout or payload-rule change |
| docs/ai/code-standards.md | unchanged | no new standard |

## Risks / open questions
- [non-blocking] Stacked on PR #6: this branch starts from CAM-16's head and its PR targets the CAM-16 branch. If PR #6 merges first (squash), GitHub retargets this PR to main; the diff may need a rebase onto main then (ask before rebasing).
- [non-blocking] `evidence/<ticket>` is a branch in the repository, so the media does live in git history of the repo (not in the PR diff or base). The user accepted this.
- [non-blocking] `<video>` is stripped by GitHub for repository files (checked with POST /markdown); videos are a link (opens the browser player) and a `.gif` preview shows inline. A private repository requires the viewer to be signed in to see inline images.
- [non-blocking] The REVIEW wait for CI of PR #6 and the merge watch for CAM-16 ended without a merge; nothing here depends on its merge.
- [non-blocking] Preset commands are unchanged (text notes only); no preset command needs re-running in a generated project beyond the existing payload tests.

## Baseline
- base_sha: 840c4b691bebbbfb149ab907b22d447f3d6e8e14 (head of CAM-16's branch; stacked)
- gates: `uv run pytest` → exit 0; 123 passed, 0 failed; `uv run ruff check src tests` → exit 0; `uv run ruff format --check src tests` → exit 0 (75 files formatted)
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
<!-- Written by VERIFY: one row per AC. kind = api | ui | cli | none. proof = comma-separated artefact paths under <spec_dir>/evidence/<TICKET>/ (git-ignored, never committed; at least one text file per row), or `not captured: <reason>`, or `n/a: <reason>` (kind none only). -->
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
- 2026-10-18T09:28Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-19-show-screenshots-and-videos-as-proof-in-the-pr-description, base=840c4b691b
- 2026-10-18T09:29Z PLAN → IMPLEMENT [planned] attempt=0/5
