from __future__ import annotations

from pathlib import Path

import pytest

from codeangel.io.errors import CodeangelError
from codeangel.project.model import Project


class TestProject:
    def test_find_root_walks_up_to_the_config(self, tmp_path: Path):
        root = tmp_path / "app"
        nested = root / "a" / "b"
        nested.mkdir(parents=True)
        (root / ".codeangel").mkdir()
        (root / ".codeangel" / "codeangel.toml").write_text(
            '[project]\nname = "app"\n', encoding="utf-8"
        )

        assert Project.discover(nested).root == root

    def test_missing_config_is_a_codeangel_error(self, tmp_path: Path):
        with pytest.raises(CodeangelError, match="codeangel init"):
            Project.discover(tmp_path)

    def test_package_name_is_a_valid_identifier(self):
        assert Project.package_name("9 My-App") == "p_9_my_app"
