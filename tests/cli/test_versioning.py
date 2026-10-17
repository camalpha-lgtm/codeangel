from __future__ import annotations

import re
from pathlib import Path

from support import run

from codeangel import __version__

ROOT = Path(__file__).resolve().parents[2]


class TestVersioning:
    def test_version_is_semver(self):
        assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)

    def test_pyproject_derives_version_from_package(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert 'dynamic = ["version"]' in text
        assert "version = " not in text.split("[project]", 1)[1].split("[", 1)[0]
        assert 'attr = "codeangel.__version__"' in text

    def test_version_command_prints_package_version(self, capsys):
        assert run(ROOT, "version") == 0
        assert capsys.readouterr().out.strip() == f"codeangel {__version__}"

    def test_project_config_records_the_installed_version(self, project, backend_project):
        import json

        del backend_project
        config = (project / ".codeangel/codeangel.toml").read_text(encoding="utf-8")
        lock = json.loads((project / ".codeangel/codeangel.lock.json").read_text(encoding="utf-8"))
        assert f'version = "{__version__}"' in config
        assert lock["codeangel"] == __version__
        assert run(project, "update") == 0
        config = (project / ".codeangel/codeangel.toml").read_text(encoding="utf-8")
        lock = json.loads((project / ".codeangel/codeangel.lock.json").read_text(encoding="utf-8"))
        assert f'version = "{__version__}"' in config
        assert lock["codeangel"] == __version__

    def test_readme_documents_pinning_to_a_release_tag(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        assert "uv tool install git+https://github.com/camalpha-lgtm/codeangel@v" in readme
        assert "[codeangel] version" in readme
        assert ".codeangel/codeangel.toml" in readme
        assert "codeangel doctor" in readme
        assert "warns" in readme
        assert "vX.Y.Z" in agents
