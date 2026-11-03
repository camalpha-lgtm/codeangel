from __future__ import annotations

from pathlib import Path

import pytest
from support import transition
from support.repo import Repo, read


@pytest.fixture
def repo(project: Path) -> Repo:
    return Repo(project)


class TestScopeCheck:
    def test_a_file_outside_affected_files_is_named(self, repo: Repo):
        repo.write("src/a.py")
        repo.write("src/b.py")

        problems = repo.scope(["src/a.py"])

        assert problems == ["src/b.py: changed but not in §Affected files or §Plan amendments"]

    def test_comma_separated_paths_in_one_cell_each_count(self, repo: Repo):
        repo.write("src/a.py")
        repo.write("src/b.py")

        assert repo.scope(["src/a.py, src/b.py"]) == []

    def test_a_directory_or_glob_entry_covers_what_is_below_it(self, repo: Repo):
        repo.write("src/pkg/a.py")
        repo.write("docs/one.md")

        assert repo.scope(["src/pkg/", "docs/*.md"]) == []

    def test_a_plan_amendment_can_name_the_extra_file(self, repo: Repo):
        repo.write("src/a.py")
        repo.write("src/b.py")

        assert repo.scope(["src/a.py"], "- 2026-01-01 added src/b.py: shared helper") == []

    def test_an_affected_file_that_gitignore_swallows_is_refused(self, repo: Repo):
        repo.write("ignored/models.py")

        problems = repo.scope(["ignored/models.py"])

        assert len(problems) == 1
        assert "git-ignored" in problems[0]

    def test_spec_files_are_not_scope(self, repo: Repo):
        repo.write("docs/specs/ABC-1.md")

        assert repo.scope([]) == []

    def test_scope_command_names_a_stray_file(self, repo: Repo):
        result = transition(
            repo.root,
            "init",
            "ABC-1",
            "--mode",
            "immediate",
            "--title",
            "t",
            "--branch",
            "b",
            "--base-sha",
            repo.base,
        )
        assert result.returncode == 0, result.stdout
        repo.write("src/stray.py")

        stray = transition(repo.root, "scope", "ABC-1")

        assert "scope: ✗" in stray.stdout
        assert "src/stray.py" in stray.stdout

    def test_implemented_exit_requires_scope_and_docs(self):
        stages = read("build-loop/references/stages.toml")
        block = stages.split("[[stages.IMPLEMENT.exits]]", 1)[1].split("[stages.VERIFY]", 1)[0]

        assert '"scope_within_affected"' in block
        assert '"docs_synced"' in block


class TestSpecParsing:
    def test_a_reason_after_a_proof_kind_is_accepted(self, repo: Repo):
        loaded = repo.loaded

        assert loaded.planned_kinds(" a [proof: ui — home page]") == {"ui"}
        assert loaded.planned_kinds(" a [proof: api+ui - list and screen]") == {"api", "ui"}
        assert loaded.planned_kinds(" a [proof: none — docs only]") == {"none"}
        assert loaded.planned_kinds(" a [proof: none]") == set()

    def test_a_test_name_may_end_in_a_symbol(self, repo: Repo):
        repo.write("tests/test_x.py", "it('says \"No people found\"', () => {})\n")
        spec = repo.loaded.Spec(
            "---\nticket: A-1\n---\n\n## Test plan\n| id | covers | asserts |\n|---|---|---|\n"
            '| tests/test_x.py::says "No people found" | AC-1 | x |\n'
        )

        assert repo.loaded.check_planned_tests_exist(spec, "") == []
