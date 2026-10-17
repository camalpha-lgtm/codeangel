from __future__ import annotations

from pathlib import Path

from support import load_transition, transition


class TestBuildLoopScript:
    def init_ticket(self, root: Path, ticket: str = "ABC-1"):
        return transition(
            root,
            "init",
            ticket,
            "--mode",
            "plan",
            "--title",
            "t",
            "--branch",
            "b",
            "--base-sha",
            "abc",
        )

    def test_map_loads_in_an_installed_project(self, project: Path):
        result = transition(project, "show")

        assert result.returncode == 0, result.stdout

    def test_specs_land_in_the_configured_spec_dir(self, project: Path):
        config = project / ".codeangel/codeangel.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                'spec_dir = "docs/specs"', 'spec_dir = "work/specs"'
            ),
            encoding="utf-8",
        )

        result = self.init_ticket(project)

        assert result.returncode == 0, result.stdout
        assert (project / "work/specs/ABC-1.md").is_file()

    def test_ticket_pattern_comes_from_config(self, project: Path):
        config = project / ".codeangel/codeangel.toml"
        config.write_text(
            config.read_text(encoding="utf-8").replace("'^[A-Z][A-Z0-9]+-\\d+$'", "'^FF-\\d+$'"),
            encoding="utf-8",
        )

        assert self.init_ticket(project, "ABC-1").returncode == 2
        assert self.init_ticket(project, "FF-1").returncode == 0

    def test_planned_tests_resolve_under_area_paths(self, backend_project: Path):
        tests = backend_project / "backend/orders/tests"
        tests.mkdir(parents=True)
        (tests / "test_orders_api.py").write_text(
            "class TestOrderList:\n    def test_returns_orders(self):\n        pass\n",
            encoding="utf-8",
        )
        loaded = load_transition(backend_project)

        def problems(node_id: str) -> list[str]:
            spec = loaded.Spec(
                "---\nticket: ABC-1\n---\n\n## Test plan\n| id | covers | asserts |\n|---|---|---|\n"
                f"| {node_id} | AC-1 | x |\n"
            )
            return loaded.check_planned_tests_exist(spec, "")

        assert problems("orders/tests/test_orders_api.py::TestOrderList::test_returns_orders") == []
        assert problems("orders/tests/test_orders_api.py::TestOrderList::test_missing")
        assert problems("orders/tests/test_nope.py::TestX::test_y")
