from __future__ import annotations

from pathlib import Path

import pytest
from support import run

from codeangel.install.tree import PAYLOAD

SKILLS = "dot_codeangel/skills"
ROOT = Path(__file__).resolve().parents[2]


def managed(relative: str) -> str:
    return (PAYLOAD.managed.base / relative).read_text(encoding="utf-8")


class TestEvidenceProcedure:
    def test_verify_defines_v9_for_every_proof_kind(self):
        verify = managed(f"{SKILLS}/build-verify/SKILL.md")

        assert "V9" in verify
        for kind in ("`api`", "`ui`", "`cli`", "`none`"):
            assert kind in verify
        assert "<project.spec_dir>/evidence/<TICKET>/" in verify
        assert "T evidence <TICKET>" in verify
        assert "text capture" in verify
        assert "never committed" in verify
        assert "throwaway data" in verify
        assert "<redacted>" in verify
        assert "not captured:" in verify

    def test_verifier_may_write_evidence_but_never_code(self):
        agent = managed("dot_claude/agents/build-verifier.md")

        assert "Write" in agent.splitlines()[3]
        assert "evidence artefacts" in agent
        assert "Never modify code" in agent

    def test_plan_requires_user_behaviour_and_proof_tags(self):
        plan = managed(f"{SKILLS}/build-plan/SKILL.md")

        assert "user behaviour" in plan
        assert "[proof: api|ui|cli|none — reason]" in plan

    def test_review_does_not_commit_evidence_and_renders_the_proof_section(self):
        review = managed(f"{SKILLS}/build-review/SKILL.md")
        commit = next(line for line in review.splitlines() if line.startswith("1. **Commit**"))

        assert "evidence" not in commit
        assert "T proof <TICKET> --into" in review
        assert "--sha" not in review
        assert "--repo" not in review
        assert "<!-- proof:start -->" in review
        assert "gh pr edit" in review

    def test_skills_ask_for_a_minimal_proof(self):
        verify = managed(f"{SKILLS}/build-verify/SKILL.md")
        review = managed(f"{SKILLS}/build-review/SKILL.md")

        assert "≤ 6" in verify
        assert "one short sentence" in verify
        assert "≤ 6 lines" in review
        assert "one small paragraph" in review

    def test_worktree_cleanup_treats_evidence_as_disposable(self):
        scaffold = (PAYLOAD.scaffold.base / "dot_codeangel/codeangel.toml").read_text(
            encoding="utf-8"
        )
        own = (ROOT / ".codeangel/codeangel.toml").read_text(encoding="utf-8")

        assert '"evidence/"' in scaffold
        assert '"evidence/"' in own

    def test_repo_installed_copy_is_current(self):
        for relative in (
            "skills/build-loop/scripts/transition.py",
            "skills/build-loop/references/contract.md",
            "skills/build-verify/SKILL.md",
            "skills/build-review/SKILL.md",
        ):
            installed = (ROOT / ".codeangel" / relative).read_text(encoding="utf-8")
            assert installed == managed(f"dot_codeangel/{relative}"), relative

    def test_state_machine_and_template_carry_the_evidence_flow(self):
        stages = managed(f"{SKILLS}/build-loop/references/stages.toml")
        template = managed(f"{SKILLS}/build-loop/assets/spec-template.md")
        contract = managed(f"{SKILLS}/build-loop/references/contract.md")

        assert "evidence_recorded" in stages
        assert "ac_proof_planned" in stages
        assert "## Evidence" in template
        assert "V9 evidence" in template
        assert "## Evidence" in contract
        assert "T proof" in contract


class TestEvidencePresets:
    @pytest.fixture
    def stack(self, project: Path) -> Path:
        assert run(project, "add", "django-drf", "backend") == 0
        return project

    def test_django_preset_ships_recipe_seed_helper_and_tests(self, stack: Path):
        recipe = (stack / "backend/docs/ai/evidence.md").read_text(encoding="utf-8")
        seed = (stack / "backend/core/seed_evidence.py").read_text(encoding="utf-8")

        assert "core.seed_evidence" in recipe
        assert "sessionid" in recipe
        assert "playwright" in recipe
        assert 'SETTINGS_MODULE = "my_app.settings"' in seed
        assert (stack / "backend/core/tests/test_seed_evidence.py").is_file()
        agents = (stack / "backend/AGENTS.md").read_text(encoding="utf-8")
        assert "backend/docs/ai/evidence.md" in agents

    def test_expo_preset_ships_a_recipe_with_its_web_prerequisite(self, project: Path):
        (project / "app").mkdir()
        (project / "app/package.json").write_text("{}", encoding="utf-8")

        assert run(project, "add", "expo", "app") == 0

        recipe = (project / "app/docs/ai/evidence.md").read_text(encoding="utf-8")
        assert "react-native-web" in recipe
        assert "app/docs/ai/evidence.md" in (project / "app/AGENTS.md").read_text(encoding="utf-8")

    def test_doc_map_points_auth_changes_at_the_recipe(self, stack: Path):
        doc_map = (stack / "docs/ai/doc-map.toml").read_text(encoding="utf-8")

        assert "backend/docs/ai/evidence.md" in doc_map
        assert "backend/my_app/settings.py" in doc_map
