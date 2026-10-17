# product

<!-- When: deciding what to build, judging scope, interpreting a vague ticket. -->

- codeangel is a stdlib-only Python CLI (≥ 3.11), installed with uv, that copies an agent-agnostic AI setup into other repos: Agent Skills, an enforced build-loop state machine, and self-maintaining agent docs. It is a package manager for that setup, not a runtime dependency of the projects.
- Users: developers who run `codeangel init` / `add <preset>` / `update` / `doctor` in their repos. Presets exist for `django-drf` and `expo`.
- This repo uses its own build loop (installed with `codeangel init`). The source of truth for skills is `src/codeangel/payload/managed/`; the root `.agents/` is an installed copy refreshed with `codeangel update`.
- Requirements come from the ticket. Unclear scope, or a ticket conflicting with the code → ask; don't infer features.
