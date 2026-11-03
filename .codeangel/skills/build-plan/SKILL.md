---
name: build-plan
description: Stage PLAN of build-loop for a ticket — creates or revises the ticket's spec file — baseline read from CI (no test runs), research, acceptance criteria, out of scope, affected files, test plan, docs impact, risks. Run by the build-loop coordinator, or directly to (re)plan a ticket whose spec is at PLAN.
metadata:
  claude-argument-hint: "<TICKET>"
---

# build-plan — stage PLAN

Read first: `.codeangel/skills/build-loop/references/contract.md`. Stage block: `T show PLAN`.
Guard: new ticket (no spec) or `T status <TICKET>` = PLAN; else return per contract.
From the coordinator (new ticket): MODE, verbatim original ticket text, title, TARGET branch, url, source, STARTUP risks, and — when the coordinator refined the ticket — a draft of AC, out of scope and open questions.

1. **Init** (new spec only): `T init <TICKET> --mode <MODE> --title "<title>" --branch <TARGET> --base-sha $(git merge-base HEAD origin/<BASE>) --url <url> --source <linear-mcp|user-paste>`. Paste the original ticket verbatim under `## Ticket`.
2. **Research**: root `AGENTS.md` → each touched area's `AGENTS.md` → its `docs/ai` + `docs/learnings` files (incl. `docs/ai/evidence.md`, if present: how proof is gathered there); read every file you'll change plus its tests.
3. **Baseline** → `## Baseline`, READ, never measured. Run no tests, linters, builds or installs in PLAN: a full-suite baseline costs minutes to hours, repeats what CI already did, and needs every area's environment set up before a line is planned.
   - `source`: CI on the base — the conclusion of the latest workflow run for `base_sha` (GitHub MCP, or `gh run list --commit <base_sha>`). Green → `known failures: none`. Red → list the failed checks / test ids from the run's log (last ~80 lines). No run → also look for known issues in `docs/learnings`; none → `source: none found`, `known failures: none`.
   - VERIFY proves a failure belongs to the base lazily, only when one shows up (`proven lazily`). Nothing here is a `[blocking]` risk: a red base is VERIFY's concern, and a broken environment surfaces at IMPLEMENT.
4. **Fill the spec** (artefacts: `T show PLAN` → produces):
   - Start from the coordinator's refined draft (if any): keep each AC / out-of-scope item that holds up against the code, fix or add the rest. Open questions → Risks.
   - Acceptance criteria: `- [ ] AC-n: …` written as user behaviour — what a person or client does and what they see or receive (screen / endpoint / command + input → observable result or state change), never an implementation detail. Necessary-but-unstated (auth failures, missing objects, invalid input, isolation between users) → include, tag `(implied)`.
   - Proof plan: end every AC with `[proof: api|ui|cli|none — reason]` — the kind of evidence VERIFY will gather from the running system (`api` request + response, `ui` screenshot, `cli` command + output; combine with `+`, e.g. `[proof: api+ui]`). `none` needs a reason (e.g. documentation only, nothing runnable). What the proof needs (seed data, auth, a browser, a dev server — see the area's `docs/ai/evidence.md`) → Affected files, or Risks when it does not exist yet.
   - Out of scope: ≥ 1 item; name tempting adjacent work (known issues in learnings, baseline failures, refactors).
   - Affected files: every file to create / modify incl. tests, migrations, registrations, generated tables in docs — `create|modify` + why. Repo-relative paths.
   - Test plan: one row per test = `<file>::<test name>` as the area's test runner accepts it (file relative to the area dir) → AC ids → what it asserts. Every AC ≥ 1 test; every test ≥ 1 AC.
   - Docs impact: run `T docs <TICKET>` after filling Affected files → one row per mapped doc (`updated` if the change will alter what it says, else `unchanged` + why), plus any other doc the change will make stale (README.md, AGENTS.md files, `docs/ai/*`). Add every `updated` doc to Affected files too. Nothing maps → `- none: <why>`.
   - Risks / open questions: tag `[blocking]` / `[non-blocking]`, or `- none`. Include STARTUP risks.
   - Spec format, so `T go <TICKET> planned` and `implemented` accept it first time:
     - Proof tag: `[proof: ui]`, `[proof: api+ui]`, or `[proof: none — reason]`; a reason after a kind (`[proof: ui — home page]`) is fine.
     - Affected files: one path per row (a directory ending in `/` or a glob also works); every file the change touches, incl. lock files and generated output, and none that `.gitignore` swallows (`git check-ignore -v <path>` on the first file of any new top-level directory).
     - Test ids: `file::Class::test_name` for class-based runners; `file::it name` or `file::describe::it name` for describe / it runners (`::` between levels, never a joined `describe it`). Each name must appear verbatim in the file.
     - Every AC needs a test row, a documentation-only AC too (a small docs test, never a weaker AC).
     - Demote any `## ` heading inside the pasted ticket to `###`.
   - Revising (entered via `revise`): apply the feedback from the last `[revise]` log note; record it under `## Plan amendments`.
   - Refined ticket (description contains `<!-- codeangel:refined -->`) and the final AC / out of scope differ from its `## Acceptance criteria` / `## Out of scope` → update those two sections in the tracker ticket (`save_issue`, replace only those sections; same rules as build-loop STARTUP 3b; best-effort, never blocks). The spec stays the source of truth.
5. **Exit**: `T go <TICKET> planned` (checks: plan complete, AC↔test mapping, a proof tag on every AC, no blocking risk). Unresolvable blocking item → `T go <TICKET> blocked --note …`. Then commit the spec locally: `git add <spec> && git commit -m "<TICKET>: Plan"`.
6. Return per contract (→ AWAITING_APPROVAL in plan mode, → IMPLEMENT in immediate mode).
