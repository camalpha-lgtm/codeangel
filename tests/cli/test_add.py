from __future__ import annotations

import tomllib
from pathlib import Path

from support import VAR_RE, run, text_files


class TestAdd:
    def test_django_drf_creates_a_runnable_skeleton_and_wires_docs(self, backend_project: Path):
        root = backend_project

        for expected in [
            "backend/manage.py",
            "backend/my_app/settings.py",
            "backend/my_app/urls.py",
            "backend/core/base_test.py",
            "backend/AGENTS.md",
            "backend/docs/ai/architecture.md",
            "backend/.pre-commit-config.yaml",
            ".github/workflows/backend.yml",
        ]:
            assert (root / expected).is_file(), expected
        assert "my_app.urls" in (root / "backend/my_app/settings.py").read_text(encoding="utf-8")
        assert "| backend |" in (root / "AGENTS.md").read_text(encoding="utf-8")
        assert "`backend/`" in (root / "README.md").read_text(encoding="utf-8")
        assert "`backend/`" in (root / "docs/ai/repo-map.md").read_text(encoding="utf-8")
        assert "backend.yml" in (root / "docs/ai/git-workflow.md").read_text(encoding="utf-8")
        assert "codeangel:preset django-drf backend" in (root / "docs/ai/doc-map.toml").read_text(
            encoding="utf-8"
        )
        assert 'path = "backend"' in (root / ".codeangel/codeangel.toml").read_text(
            encoding="utf-8"
        )

    def test_no_unresolved_template_variables(self, backend_project: Path):
        leftovers = [
            path.relative_to(backend_project).as_posix()
            for path in text_files(backend_project)
            if VAR_RE.search(path.read_text(encoding="utf-8"))
        ]

        assert leftovers == []

    def test_is_idempotent(self, backend_project: Path):
        tracked = [
            "AGENTS.md",
            "README.md",
            "docs/ai/repo-map.md",
            "docs/ai/doc-map.toml",
            "docs/ai/git-workflow.md",
            ".codeangel/codeangel.toml",
        ]
        before = {name: (backend_project / name).read_text(encoding="utf-8") for name in tracked}

        assert run(backend_project, "add", "django-drf", "backend") == 0

        after = {name: (backend_project / name).read_text(encoding="utf-8") for name in tracked}
        assert after == before

    def test_never_overwrites_existing_area_files(self, project: Path):
        (project / "backend").mkdir()
        (project / "backend/AGENTS.md").write_text("custom\n", encoding="utf-8")

        assert run(project, "add", "django-drf", "backend") == 0

        assert (project / "backend/AGENTS.md").read_text(encoding="utf-8") == "custom\n"

    def test_unknown_preset_is_an_error(self, project: Path):
        assert run(project, "add", "no-such-preset", "x") == 2

    def test_expo_requires_an_existing_app(self, project: Path):
        assert run(project, "add", "expo", "frontend") == 2

        (project / "frontend").mkdir()
        (project / "frontend/package.json").write_text("{}\n", encoding="utf-8")
        assert run(project, "add", "expo", "frontend") == 0
        assert (project / "frontend/AGENTS.md").is_file()
        assert (project / ".github/workflows/frontend.yml").is_file()

    def test_expo_adopts_the_generators_agents_md(self, project: Path):
        (project / "frontend").mkdir()
        (project / "frontend/package.json").write_text("{}\n", encoding="utf-8")
        vendor = "This is an Expo app.\n\n## Expo has changed\n\nRead the docs.\n"
        (project / "frontend/AGENTS.md").write_text(vendor, encoding="utf-8")

        assert run(project, "add", "expo", "frontend") == 0

        adopted = (project / "frontend/docs/ai/expo-official.md").read_text(encoding="utf-8")
        assert adopted.startswith("# Expo official agent guidance")
        assert "<!-- When:" in adopted
        assert vendor.strip() in adopted
        router = (project / "frontend/AGENTS.md").read_text(encoding="utf-8")
        assert "Loaded for any work under" in router
        assert "frontend/docs/ai/expo-official.md" in router
        assert run(project, "add", "expo", "frontend") == 0
        assert (project / "frontend/docs/ai/expo-official.md").read_text(
            encoding="utf-8"
        ) == adopted
        assert run(project, "doctor") == 0

    def test_requires_an_initialised_project(self, tmp_path: Path):
        assert run(tmp_path, "add", "django-drf", "backend") == 2

    def test_doc_map_stays_valid_toml_with_two_areas(self, backend_project: Path):
        (backend_project / "frontend").mkdir()
        (backend_project / "frontend/package.json").write_text("{}\n", encoding="utf-8")
        assert run(backend_project, "add", "expo", "frontend") == 0

        rules = tomllib.loads(
            (backend_project / "docs/ai/doc-map.toml").read_text(encoding="utf-8")
        )["rule"]
        assert any("backend/" in rule["paths"][0] for rule in rules)
        assert any("frontend/" in rule["paths"][0] for rule in rules)
