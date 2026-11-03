from __future__ import annotations

from support.repo import read


class TestPlanAndImplementAreCheap:
    def test_plan_reads_the_baseline_and_runs_nothing(self):
        plan = read("build-plan/SKILL.md")

        assert "READ, never measured" in plan
        assert "Run no tests, linters, builds or installs in PLAN" in plan
        assert "run each touched area's `## Done` gates" not in plan

    def test_plan_names_the_spec_format_rules_that_used_to_refuse_the_exit(self):
        plan = read("build-plan/SKILL.md")

        assert "one path per row" in plan
        assert "Demote any `## ` heading" in plan
        assert "`file::describe::it name`" in plan

    def test_baseline_template_has_no_gate_results_to_measure(self):
        template = read("build-loop/assets/spec-template.md")

        assert "- gates:" not in template
        assert "Read, never measured" in template

    def test_environment_setup_moves_from_startup_to_implement(self):
        loop = read("build-loop/SKILL.md")
        implement = read("build-implement/SKILL.md")

        assert "each touched area's setup" not in loop
        assert "PLAN only reads" in loop
        assert "1b. **Environment**" in implement

    def test_implement_runs_the_scope_gate_before_handing_over(self):
        implement = read("build-implement/SKILL.md")

        assert "`T scope <TICKET>`" in implement
        assert implement.index("`T scope <TICKET>`") < implement.index(
            "`T go <TICKET> implemented`"
        )


class TestVerifyAndReviewAreCheapFirst:
    def test_verify_runs_cheap_checks_before_the_suite_and_the_app(self):
        verify = read("build-verify/SKILL.md")

        assert "Tier 1" in verify
        assert "ONLY when every Tier 1 check passed" in verify
        assert "not run: fix Tier 1 first" in verify
        assert "V3 | full suite (Tier 2)" in verify
        assert "V9 | evidence (Tier 2)" in verify

    def test_verify_re_attempts_audit_only_the_delta(self):
        verify = read("build-verify/SKILL.md")

        assert "`T delta <TICKET>`" in verify
        assert "carried from attempt" in verify

    def test_verify_proves_baseline_failures_lazily(self):
        verify = read("build-verify/SKILL.md")

        assert "proven lazily" in verify
        assert "Unproven → it is this ticket's failure" in verify

    def test_capture_tooling_is_built_once_and_filed_back(self):
        verify = read("build-verify/SKILL.md")
        learn = read("build-learn/SKILL.md")

        assert "EVIDENCE/tools/" in verify
        assert "recipe gaps" in verify
        assert "recipe gaps" in learn
        assert "docs/ai/evidence.md" in learn

    def test_review_merges_the_base_before_pushing(self):
        review = read("build-review/SKILL.md")

        assert "`T base <TICKET>`" in review
        assert review.index("2b.") < review.index("3. **Push**")
        assert "never rebase" in review

    def test_contract_lists_the_new_commands(self):
        contract = read("build-loop/references/contract.md")

        for command in ("`T scope <TICKET>`", "`T delta <TICKET>`", "`T base <TICKET>`"):
            assert command in contract
