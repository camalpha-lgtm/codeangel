from __future__ import annotations

from pathlib import Path

from codeangel.install.managed import ManagedInstaller
from codeangel.io.files import ContentDigest


class TestManagedInstaller:
    def test_creates_missing_file(self, tmp_path: Path):
        dest = tmp_path / "file.txt"
        status, digest = ManagedInstaller().install(dest, "new\n", None, False)

        assert status == "created"
        assert digest == ContentDigest().hexdigest(b"new\n")
        assert dest.read_text(encoding="utf-8") == "new\n"

    def test_locally_edited_file_becomes_a_new_proposal(self, tmp_path: Path):
        dest = tmp_path / "file.txt"
        dest.write_text("local\n", encoding="utf-8")
        locked = ContentDigest().hexdigest(b"old\n")

        status, digest = ManagedInstaller().install(dest, "new\n", locked, False)

        assert status == "conflict"
        assert digest == locked
        assert dest.read_text(encoding="utf-8") == "local\n"
        proposal = tmp_path / "file.txt.codeangel-new"
        assert proposal.read_text(encoding="utf-8") == "new\n"

    def test_force_overwrites_a_conflict(self, tmp_path: Path):
        dest = tmp_path / "file.txt"
        dest.write_text("local\n", encoding="utf-8")
        locked = ContentDigest().hexdigest(b"old\n")

        status, _digest = ManagedInstaller().install(dest, "new\n", locked, True)

        assert status == "updated"
        assert dest.read_text(encoding="utf-8") == "new\n"
