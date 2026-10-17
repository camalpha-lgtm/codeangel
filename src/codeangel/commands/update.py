import argparse
import re
from pathlib import Path

from codeangel import __version__
from codeangel.commands.base import Command
from codeangel.install.lockfile import Lockfile
from codeangel.install.managed import ManagedInstaller
from codeangel.install.shims import ShimSynchroniser
from codeangel.install.tree import PAYLOAD, PayloadTree
from codeangel.io.files import ContentDigest, TextFile
from codeangel.project.model import Paths, Project


class UpdateCommand(Command):
    name = "update"
    help = "refresh managed files; never clobbers local edits"

    def configure(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--force", action="store_true", help="overwrite locally edited managed files"
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = Project.discover(Path(args.directory).resolve()).root
        self._refresh(root, args.force)
        self._stamp_version(root)
        print(f"codeangel {__version__}: managed files up to date")
        return ShimSynchroniser().run(root, check=False)

    def _refresh(self, root: Path, force: bool) -> None:
        old = Lockfile(root).load()
        new, shipped = self._install(root, old, force)
        self._retire(root, old, shipped)
        Lockfile(root).save(new)

    def _install(
        self, root: Path, old: dict[str, str], force: bool
    ) -> tuple[dict[str, str], set[str]]:
        installer = ManagedInstaller()
        new: dict[str, str] = {}
        shipped: set[str] = set()
        for rel in PAYLOAD.managed.files():
            dest_rel = PayloadTree.install_path(rel).as_posix()
            shipped.add(dest_rel)
            status, locked = installer.install(
                root / dest_rel, PAYLOAD.managed.read(rel), old.get(dest_rel), force
            )
            if locked:
                new[dest_rel] = locked
            self._report(root, dest_rel, status, installer.NEW_SUFFIX)
        return new, shipped

    def _report(self, root: Path, dest_rel: str, status: str, suffix: str) -> None:
        proposal = (root / dest_rel).with_name(Path(dest_rel).name + suffix)
        if status in ("updated", "unchanged"):
            proposal.unlink(missing_ok=True)
        if status == "unchanged":
            return
        hint = f" (yours kept; new version → {dest_rel}{suffix})" if status == "conflict" else ""
        print(f"  {status:<9} {dest_rel}{hint}")

    def _retire(self, root: Path, old: dict[str, str], shipped: set[str]) -> None:
        digest = ContentDigest()
        for dest_rel, locked in old.items():
            dest = root / dest_rel
            if dest_rel in shipped or not dest.exists():
                continue
            if digest.hexdigest(dest.read_bytes()) == locked:
                dest.unlink()
                print(f"  removed   {dest_rel} (no longer shipped)")
                continue
            print(f"  orphaned  {dest_rel} (no longer shipped, locally modified — left in place)")

    def _stamp_version(self, root: Path) -> None:
        path = root / Paths.CONFIG
        text = path.read_text(encoding="utf-8")
        stamped = re.sub(r'(?m)^(version\s*=\s*)"[^"]*"', rf'\g<1>"{__version__}"', text, count=1)
        TextFile().write(path, stamped)
