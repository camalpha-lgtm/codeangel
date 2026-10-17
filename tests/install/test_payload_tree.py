from __future__ import annotations

from pathlib import Path, PurePosixPath

from codeangel.install.tree import PayloadTree


class TestPayloadTree:
    def test_dot_prefixed_parts_install_as_hidden_paths(self):
        assert PayloadTree.install_path(PurePosixPath("dot_agents/x")).as_posix() == ".agents/x"

    def test_files_skip_bytecode_caches(self, tmp_path: Path):
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "a.pyc").write_text("x", encoding="utf-8")
        (tmp_path / "b.txt").write_text("y", encoding="utf-8")
        nested = tmp_path / "sub"
        nested.mkdir()
        (nested / "c.txt").write_text("z", encoding="utf-8")

        assert [path.as_posix() for path in PayloadTree(tmp_path).files()] == ["b.txt", "sub/c.txt"]
