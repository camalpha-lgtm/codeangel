from __future__ import annotations

from pathlib import Path

import pytest
from support import PYTHON, run


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "my-app"
    root.mkdir()
    assert run(root, "init", "--name", "my-app", "--python", PYTHON) == 0
    return root


@pytest.fixture
def backend_project(project: Path) -> Path:
    assert run(project, "add", "django-drf", "backend") == 0
    return project
