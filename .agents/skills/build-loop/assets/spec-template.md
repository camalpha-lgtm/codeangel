---
ticket: <TICKET>
title: <ticket title>
mode: plan   # plan | immediate — approval of a plan sets immediate
source: <linear-mcp | linear-api | user-paste | other>
url: <linear issue url | none>
branch: <Linear suggested branch name>
base_sha: <sha>
pr: <pr url | empty until REVIEW>
stage: PLAN  # managed by transition.py — see stages.toml
last_status: init  # exit status that entered the current stage
attempt: 0   # failed VERIFY / CI cycles; forced BLOCKED at max_attempts
blocked_stage:
blocked_reason:
created: <UTC ISO time>
updated: <UTC ISO time>
---

# <TICKET>: <title>

## Ticket
<verbatim ticket title, description, relevant comments>

## Acceptance criteria
- [ ] AC-1: <method + path + input → status + body / DB effect, or concrete behaviour>
- [ ] AC-2: <...> (implied)

## Out of scope
- <tempting adjacent work explicitly not done here>

## Affected files
| path | change | why |
|---|---|---|
| <repo-relative path> | <create or modify> | <reason> |

## Test plan
| test id | covers | asserts |
|---|---|---|
| <file>::<test name> | AC-1 | <observable outcome> |

## Docs impact
<!-- `T docs <TICKET>` lists docs mapped from the change (docs/ai/doc-map.toml). One row per doc; status updated or unchanged; unchanged needs a reason. Nothing maps → "- none: <why>". -->
| doc | status | note |
|---|---|---|
| <repo-relative doc path> | <updated or unchanged> | <what changed / why it is still accurate> |

## Risks / open questions
- [non-blocking] <risk or question>

## Baseline
- base_sha: <sha>
- gates: <per area: command → exit code; n passed, m failed; collection / build errors>
- known failures: <test ids | none>
- lint debt: <file: codes | none>
- schema drift: <area / app | none>

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
- Failure excerpt / root cause / next action: <...>
-->

## Review
- PR: <url>
- CI runs: <!-- <run id> <sha> <conclusion> -->
- Ready for review: <UTC time | not marked: reason>

## Learnings
<!-- - <area>/docs/learnings/<file>.md or <area>/docs/ai/<file>.md: <entry added/updated/deleted> | none: <why> -->

## Log
<!-- written only by transition.py (go / log / init) -->
