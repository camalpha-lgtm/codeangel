---
ticket: CAM-13
title: Show proof of working changes in the PR description
mode: immediate   # plan | immediate — approval of a plan sets immediate
source: linear-mcp
url: https://linear.app/cam-h-personal/issue/CAM-13/show-proof-of-working-changes-in-the-pr-description
branch: camerondhobbs/cam-13-show-proof-in-pr-description
base_sha: 2ef7d3d4f7d6e1b28fb554607711a015a63a5c61
pr: https://github.com/camalpha-lgtm/codeangel/pull/5
stage: DONE  # managed by transition.py — see stages.toml
last_status: learned  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: 2026-10-17T20:17Z
updated: 2026-10-17T20:23Z
---

# CAM-13: Show proof of working changes in the PR description

## Ticket
**Title:** Show proof in PR description (refined in Linear to: Show proof of working changes in the PR description)

Update build-loop skill harness to gather evidence and proof of changes working. This can be browser or in app screenshots. Or some verification (in verify step) it has manually hit the APIs, or rendered pages or components. It can be a mixture of both since this is a monorepo. It also means data needs to be seeded correctly in a project to render some things, and bare in mind that APIs needs auth at times, so needs auth that is reusable. Include the screenshots or text under proof/evidence in GitHub PR description. I think this should happen in the verify step of the build loop. But open to your thoughts. Proof/evidence based on acceptance criteria is best. Acceptance criteria should mimic user behaviour or actual functionalitythat's what I care about.

This is the harness (codeangel) half of CAM-13. The consuming-project half (flipfather: `codeangel update` + its own evidence recipes and seeding helper) is tracked in the flipfather repo's `docs/specs/CAM-13.md` and ships as a second PR after this one merges.

Design: PLAN tags every AC `[proof: api|ui|cli|none — reason]` and writes AC as user behaviour. VERIFY gets a ninth check, V9: the independent verifier exercises the running system once per AC on throwaway data with generated auth, writes `## Evidence` (`| AC | kind | proof | note |`) and artefacts in `<spec_dir>/evidence/<TICKET>/`. Two new transition checks gate it: `ac_proof_planned` (PLAN exits) and `evidence_recorded` (VERIFY pass). REVIEW commits the artefacts and renders a `## Proof` block in the PR body with the new `T proof` command (text in fenced blocks, screenshots as commit-pinned `?raw=true` images, warnings for what was not captured). Per-area recipes (`docs/ai/evidence.md`: start, seed, auth, capture) are project-owned; the presets scaffold them, and the django-drf preset adds a dev-only session helper.

## Acceptance criteria
- [x] AC-1: A planner cannot leave an acceptance criterion without a proof plan: `T go <ticket> planned` is refused naming every AC that lacks a `[proof: api|ui|cli|none — reason]` tag (`none` needs a reason; the template placeholder is not a tag) and succeeds once all are tagged. [proof: cli]
- [x] AC-2: A verifier cannot pass a ticket without evidence: `T go <ticket> pass` is refused unless §Evidence has a row per AC, one row per planned kind, each pointing at existing non-empty files inside `<spec_dir>/evidence/<ticket>/` or giving `not captured: <reason>` (or `n/a: <reason>` for AC planned `none`); a planned api/ui/cli AC cannot be recorded as `none`. [proof: cli]
- [x] AC-3: (implied) Evidence cannot leak credentials: the same exit is refused when §Evidence or a text artefact contains a credential-looking value (`sessionid=…`, `password: …`, `Authorization: Bearer …`), and accepts the `<redacted>` form. [proof: cli]
- [x] AC-4: A reviewer sees the proof in the PR: `T proof <ticket> --repo owner/name --sha <sha> [--into <body-file>]` prints / splices a `## Proof` block showing, per AC, fenced text transcripts, screenshots as images pinned to the sha, and a warning for anything not captured; running it again replaces only the block between its markers. [proof: cli]
- [x] AC-5: The stage skills tell agents how: build-plan asks for user-behaviour AC and proof tags; build-verify defines V9 per proof kind (throwaway data, recipe, redaction, `not captured`, FAIL conditions) and allows evidence artefacts in scope; build-review commits the evidence directory and builds/refreshes the PR's Proof block; the `build-verifier` agent may write evidence but never code. [proof: none — skill text, asserted by tests]
- [x] AC-6: A new django-drf area ships its evidence recipe and a working session helper: `codeangel add django-drf backend` creates `backend/docs/ai/evidence.md`, `backend/core/seed_evidence.py` (idempotent staff user, unusable password, one JSON line with a `sessionid`, refuses when DEBUG is off) and its tests, routes the recipe from `backend/AGENTS.md`, and the generated project's own gates (tests, ruff) pass. [proof: cli]
- [x] AC-7: A new expo area ships an evidence recipe that states its web-target prerequisite, routed from its `AGENTS.md`. [proof: cli]
- [x] AC-8: (implied) This repo's own installed copy of the harness is current (`codeangel update` ran: `.codeangel/`, shims, lock), and managed files stay project-agnostic. [proof: cli]

## Out of scope
- Consuming-project work (flipfather's recipes, seeding helper, tests, `codeangel update`): the second PR.
- A `codeangel` command that installs evidence recipes into existing areas (`update` never touches project-owned files; older areas copy the preset file by hand).
- Hosting screenshots outside the PR branch, video/GIF capture, or driving native devices; a browser dependency in codeangel itself (recipes call Playwright via `npx`).
- Token / JWT auth recipes (session cookies only; the recipe notes where to swap).
- Rewriting past tickets' specs for the new sections; bumping `codeangel.__version__`.

## Affected files
| path | change | why |
|---|---|---|
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/scripts/transition.py | modify | `ac_proof_planned`, `evidence_recorded`, `T proof` |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/stages.toml | modify | new checks on PLAN / VERIFY exits, §Evidence artefact |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/assets/spec-template.md | modify | `## Evidence`, AC proof tags, V9 line |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/references/contract.md | modify | Evidence rules, `T proof` row |
| src/codeangel/payload/managed/dot_codeangel/skills/build-loop/SKILL.md | modify | final report line for proof |
| src/codeangel/payload/managed/dot_codeangel/skills/build-plan/SKILL.md | modify | user-behaviour AC, proof tags |
| src/codeangel/payload/managed/dot_codeangel/skills/build-verify/SKILL.md | modify | V9 procedure, scope/hygiene |
| src/codeangel/payload/managed/dot_codeangel/skills/build-review/SKILL.md | modify | commit evidence, PR Proof block |
| src/codeangel/payload/managed/dot_claude/agents/build-verifier.md | modify | evidence writes allowed |
| src/codeangel/payload/managed/docs/ai/agent-docs.md | modify | evidence flow in the build-loop summary |
| src/codeangel/payload/presets/django-drf/docs/ai/evidence.md | create | backend recipe |
| src/codeangel/payload/presets/django-drf/core/seed_evidence.py | create | session helper |
| src/codeangel/payload/presets/django-drf/core/tests/test_seed_evidence.py | create | helper tests |
| src/codeangel/payload/presets/django-drf/AGENTS.md | modify | router row |
| src/codeangel/payload/presets/django-drf/_doc-map.toml | modify | rules keep the recipe current |
| src/codeangel/payload/presets/django-drf/docs/ai/architecture.md | modify | core/ layout mentions the helper |
| src/codeangel/payload/presets/django-drf/docs/ai/commands.md | modify | evidence-session command row |
| src/codeangel/payload/presets/expo/docs/ai/evidence.md | create | frontend recipe + web prerequisite |
| src/codeangel/payload/presets/expo/AGENTS.md | modify | router row |
| src/codeangel/payload/presets/expo/_doc-map.toml | modify | package.json rule also covers the recipe |
| tests/support/evidence.py | create | spec / artefact builder for the tests |
| tests/cli/test_build_loop_evidence.py | create | AC-1…AC-3 |
| tests/cli/test_build_loop_proof.py | create | AC-4 |
| tests/harness/test_evidence_payload.py | create | AC-5…AC-7 |
| .codeangel/ , .claude/ , docs/ai/agent-docs.md | modify | this repo's installed copy, refreshed by `codeangel update` (AC-8) |
| README.md | modify | build-loop bullet mentions proof in the PR |
| docs/ai/repo-map.md | modify | `docs/specs/evidence/<TICKET>/` row |
| docs/specs/CAM-13.md | modify | this spec |
| docs/learnings/tooling.md | modify | lessons filed by LEARN |

## Test plan
| test id | covers | asserts |
|---|---|---|
| tests/cli/test_build_loop_evidence.py::TestProofPlanning::test_untagged_criterion_is_named | AC-1 | one problem naming the untagged AC |
| tests/cli/test_build_loop_evidence.py::TestProofPlanning::test_every_tag_form_is_accepted | AC-1 | api, ui+api, cli, none with reason all pass |
| tests/cli/test_build_loop_evidence.py::TestProofPlanning::test_none_needs_a_reason | AC-1 | bare `none` refused |
| tests/cli/test_build_loop_evidence.py::TestProofPlanning::test_template_placeholder_is_not_a_tag | AC-1 | the template's literal tag is refused |
| tests/cli/test_build_loop_evidence.py::TestProofPlanning::test_planned_exits_list_the_check | AC-1 | `T show PLAN` lists `ac_proof_planned` on both planned exits |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_missing_row_names_the_criterion | AC-2 | `AC-2 has no row in §Evidence` |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_proof_file_not_captured_and_n_a_rows_pass | AC-2 | file, `not captured:` and `n/a:` rows give no problem |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_missing_empty_and_foreign_artefacts_are_refused | AC-2 | missing, empty and out-of-directory artefacts each refused |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_planned_kind_cannot_be_downgraded_to_none | AC-2 | planned api recorded as none refused |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_every_planned_kind_needs_a_row | AC-2 | ui+api with only a ui row names the missing api row |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_verify_pass_exit_lists_the_check | AC-2 | `T show VERIFY` lists `evidence_recorded` |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_credentials_in_artefacts_and_section_are_refused | AC-3 | cookie in a text artefact and a bearer header in the section both flagged |
| tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_redacted_values_are_accepted | AC-3 | `<redacted>` and short prose like `password: required` pass |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_shows_images_text_and_warnings | AC-4 | commit-pinned `?raw=true` image, fenced transcript, warning, `2 of 3` summary, no raw proof tag |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_splicing_replaces_only_the_marked_block | AC-4 | second render replaces the first block, surrounding text intact |
| tests/cli/test_build_loop_proof.py::TestProofRendering::test_proof_command_writes_into_a_body_file | AC-4 | `T proof … --into` appends the block to an existing body file |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_verify_defines_v9_for_every_proof_kind | AC-5 | V9, kinds, evidence dir, throwaway data, redaction, not captured present |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_verifier_may_write_evidence_but_never_code | AC-5 | agent tools include Write; code edits still forbidden |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_plan_requires_user_behaviour_and_proof_tags | AC-5 | plan skill text |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_review_commits_evidence_and_renders_the_proof_section | AC-5 | review skill commits the dir, runs `T proof`, markers, `gh pr edit` fallback |
| tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_state_machine_and_template_carry_the_evidence_flow | AC-5 | stages.toml, template, contract updated |
| tests/harness/test_evidence_payload.py::TestEvidencePresets::test_django_preset_ships_recipe_seed_helper_and_tests | AC-6 | files generated with the project's settings module, router row |
| tests/harness/test_evidence_payload.py::TestEvidencePresets::test_doc_map_points_auth_changes_at_the_recipe | AC-6 | doc map rule for settings / urls / permissions |
| tests/harness/test_evidence_payload.py::TestEvidencePresets::test_expo_preset_ships_a_recipe_with_its_web_prerequisite | AC-7 | recipe mentions react-native-web, routed |
| tests/harness/test_payload.py::TestPayload::test_managed_files_are_project_agnostic | AC-8 | no banned stack words in managed files |
| tests/harness/test_payload.py::TestPayload::test_repo_uses_codeangel_folder_not_agents | AC-8 | repo's own `.codeangel` layout and lock keys intact |

Run: `uv run pytest`. AC-6's generated-project gates (tests + ruff of the generated backend) are run by VERIFY in a scratch project and recorded in the report.

## Docs impact
| doc | status | note |
|---|---|---|
| README.md | updated | build-loop bullet mentions the Proof section |
| docs/ai/repo-map.md | updated | evidence directory row |
| AGENTS.md | unchanged | layout, payload rules and commands are unchanged by new payload files; the project-agnostic rule still holds |
| docs/ai/code-standards.md | unchanged | no new standard; new Python in `src/` is payload (outside the OO and size rules), tests follow the two-class limit |

## Risks / open questions
- [non-blocking] Second repo: flipfather's PR consumes this one through `codeangel update`; it must be re-run against the merged `origin/main` before flipfather merges.
- [non-blocking] The plan was written after the harness change had been prototyped against the flipfather ticket; tests were added alongside, then checked to fail without the behaviour only by construction (new functions). Declared here rather than hidden.
- [non-blocking] Existing projects get the new skills / checks through `update`, but their older specs lack proof tags and `## Evidence`; the checks only run on new PLAN/VERIFY exits, so in-flight tickets must add tags before `planned` or rows before `pass`.
- [non-blocking] Existing areas do not get `evidence.md` or the seed helper from `update` (project-owned files); documented in agent-docs and the README.
- [non-blocking] Browser capture uses Playwright via `npx` and a system browser channel; not exercised in CI here. The django-drf recipe commands are verified in the flipfather PR against a real project.
- [non-blocking] Commit-pinned `?raw=true` links render in PR descriptions for signed-in viewers of private repos; unverified for public-without-login views.

## Baseline
- base_sha: 2ef7d3d4f7d6e1b28fb554607711a015a63a5c61 (origin/main, CAM-8 merged)
- gates: `uv run pytest` → 87 passed, 0 failed · `uv run ruff check src tests` → clean · `uv run ruff format --check src tests` → clean (measured in a scratch worktree of origin/main)
- known failures: none
- lint debt: none
- schema drift: n/a (no schema)

## Plan amendments
<!-- - <UTC time> <what changed> — <why> -->

## Verify reports
### Attempt 1 — PASS
- Independence: run by the implementing agent, not a separate subagent (the cross-repo ticket has no installed verifier for this working tree); the flipfather ticket's VERIFY, which consumes this payload, is the independent run.
- V1 lint/format: PASS `uv run ruff check src tests` clean, `ruff format --check` 74 files clean
- V2 migrations: PASS n/a (no schema)
- V3 full suite: PASS 111 passed, 0 failed (baseline 87 passed; +24 new tests)
- V4 planned tests: PASS all Test plan ids exist and pass (34 passed across the four files)
- V5 AC audit: PASS
  - AC-1: tests/cli/test_build_loop_evidence.py::TestProofPlanning::test_untagged_criterion_is_named; tests/cli/test_build_loop_evidence.py:17
  - AC-2: tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_missing_row_names_the_criterion; tests/cli/test_build_loop_evidence.py:63
  - AC-3: tests/cli/test_build_loop_evidence.py::TestEvidenceGate::test_credentials_in_artefacts_and_section_are_refused; tests/cli/test_build_loop_evidence.py:127
  - AC-4: tests/cli/test_build_loop_proof.py::TestProofRendering::test_section_shows_images_text_and_warnings; tests/cli/test_build_loop_proof.py:34
  - AC-5: tests/harness/test_evidence_payload.py::TestEvidenceProcedure::test_review_commits_evidence_and_renders_the_proof_section; tests/harness/test_evidence_payload.py:42
  - AC-6: tests/harness/test_evidence_payload.py::TestEvidencePresets::test_django_preset_ships_recipe_seed_helper_and_tests; tests/harness/test_evidence_payload.py:70
  - AC-7: tests/harness/test_evidence_payload.py::TestEvidencePresets::test_expo_preset_ships_a_recipe_with_its_web_prerequisite; tests/harness/test_evidence_payload.py:82
  - AC-8: tests/harness/test_payload.py::TestPayload::test_managed_files_are_project_agnostic; tests/harness/test_payload.py:17
- V6 scope audit: PASS changed files are all in Affected files, the spec, or docs/specs/evidence/CAM-13/
- V7 hygiene: PASS no comments or docstrings in new tests; payload scripts are outside the standards; no secrets or machine paths in the evidence (paths replaced by placeholders)
- V8 docs in sync: PASS `T docs CAM-13` ✓ ready (README, repo-map updated; AGENTS.md, code-standards unchanged with reasons)
- V9 evidence: PASS 7 rows with transcripts captured from a scratch project and a generated django-drf project; AC-5 is n/a (skill text). Found by the generated-project run: re-issuing a session reset the user's password hash and invalidated earlier sessions → fixed (password set only on creation) and covered by test_second_run_reuses_the_user.

## Evidence
| AC | kind | proof | note |
|---|---|---|---|
| AC-1 | cli | docs/specs/evidence/CAM-13/ac-1-cli.txt | `go planned` refused naming AC-2, then accepted once tagged |
| AC-2 | cli | docs/specs/evidence/CAM-13/ac-2-cli.txt | `go pass` refused for a missing AC row, accepted once the ui row's screenshot exists |
| AC-3 | cli | docs/specs/evidence/CAM-13/ac-3-cli.txt | a session cookie in an artefact refused (value not echoed), accepted once redacted |
| AC-4 | cli | docs/specs/evidence/CAM-13/ac-4-cli.txt | `T proof` output spliced into a PR body; second run replaced only the marked block |
| AC-5 | none | n/a: skill and agent text, asserted by tests | - |
| AC-6 | cli | docs/specs/evidence/CAM-13/ac-6-cli.txt | `add django-drf` files + router row; generated project: 5 tests pass, ruff clean |
| AC-7 | cli | docs/specs/evidence/CAM-13/ac-7-cli.txt | `add expo` recipe with the react-native-web prerequisite and router row |
| AC-8 | cli | docs/specs/evidence/CAM-13/ac-8-cli.txt | `update` reports up to date, payload tests and shim check pass |

## Review
- PR: https://github.com/camalpha-lgtm/codeangel/pull/5
- CI runs: 39066449141 e29109980178200c49c3ca55650ef4b64fc024d6 success
- Ready for review: marked ready after CI green (2026-10-17)

## Learnings
- docs/learnings/tooling.md: added two entries (ruff format touches managed payload scripts → rerun update; test preset Python in a generated project, session-hash finding)
- doc map: no change — every doc that went stale was already mapped

## Log
- 2026-10-17T20:17Z STARTUP → PLAN [init] attempt=0/5 — mode=immediate, branch=camerondhobbs/cam-13-show-proof-in-pr-description, base=2ef7d3d4f7
- 2026-10-17T20:21Z PLAN → IMPLEMENT [planned] attempt=0/5
- 2026-10-17T20:21Z IMPLEMENT → VERIFY [implemented] attempt=0/5
- 2026-10-17T20:22Z VERIFY → REVIEW [pass] attempt=0/5
- 2026-10-17T20:23Z REVIEW → LEARN [ci_green] attempt=0/5
- 2026-10-17T20:23Z LEARN → DONE [learned] attempt=0/5
