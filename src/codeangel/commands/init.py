import argparse
import json
from pathlib import Path, PurePosixPath

from codeangel import __version__
from codeangel.commands.base import Command
from codeangel.install.lockfile import Lockfile
from codeangel.install.managed import ManagedInstaller
from codeangel.install.shims import ShimSynchroniser
from codeangel.install.tree import PAYLOAD, PayloadTree
from codeangel.io.errors import CodeangelError
from codeangel.io.files import TextFile
from codeangel.io.templating import TemplateRenderer
from codeangel.project.model import Paths, Project
from codeangel.project.runtime import PythonRuntime


class InitCommand(Command):
    name = "init"
    help = "install codeangel into a repo"

    def configure(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--name", help="project name (default: directory name)")
        parser.add_argument("--base-branch", default="main")
        parser.add_argument(
            "--python", help="Python >= 3.11 command for .agents scripts (default: detect)"
        )
        parser.add_argument(
            "--force", action="store_true", help="overwrite differing managed files"
        )

    def execute(self, args: argparse.Namespace) -> int:
        root = Path(args.directory).resolve()
        self._refuse(root, args.force)
        variables = self._variables(root, args)
        counts, lock = self._managed(root, args.force)
        self._scaffold(root, variables, counts)
        Lockfile(root).save(lock)
        Project.read_config(root)
        return self._finish(root, variables["python"], counts)

    def _refuse(self, root: Path, force: bool) -> None:
        if (root / Paths.CONFIG).exists() and not force:
            raise CodeangelError(f"{root} is already initialised — use `codeangel update`")

    def _variables(self, root: Path, args: argparse.Namespace) -> dict[str, str]:
        python = args.python or PythonRuntime().detect()
        name = args.name or root.name
        return {
            "project_name": name,
            "project_package": Project.package_name(name),
            "base_branch": args.base_branch,
            "python": python,
            "python_toml": json.dumps(python),
            "codeangel_version": __version__,
        }

    def _managed(self, root: Path, force: bool) -> tuple[dict[str, int], dict[str, str]]:
        counts: dict[str, int] = {}
        lock: dict[str, str] = {}
        installer = ManagedInstaller()
        for rel in PAYLOAD.managed.files():
            self._one_managed(root, rel, installer, force, counts, lock)
        return counts, lock

    def _one_managed(
        self,
        root: Path,
        rel: PurePosixPath,
        installer: ManagedInstaller,
        force: bool,
        counts: dict[str, int],
        lock: dict[str, str],
    ) -> None:
        dest_rel = PayloadTree.install_path(rel).as_posix()
        status, locked = installer.install(root / dest_rel, PAYLOAD.managed.read(rel), None, force)
        key = f"managed {status}"
        counts[key] = counts.get(key, 0) + 1
        if locked:
            lock[dest_rel] = locked
        if status == "conflict":
            suffix = installer.NEW_SUFFIX
            print(f"  conflict  {dest_rel} exists and differs → new version at {dest_rel}{suffix}")

    def _scaffold(self, root: Path, variables: dict[str, str], counts: dict[str, int]) -> None:
        renderer = TemplateRenderer()
        for rel in PAYLOAD.scaffold.files():
            self._one_scaffold(root, rel, renderer, variables, counts)

    def _one_scaffold(
        self,
        root: Path,
        rel: PurePosixPath,
        renderer: TemplateRenderer,
        variables: dict[str, str],
        counts: dict[str, int],
    ) -> None:
        dest_rel = renderer.render(
            PayloadTree.install_path(rel).as_posix(), variables, rel.as_posix()
        )
        dest = root / dest_rel
        if dest.exists():
            counts["scaffold kept"] = counts.get("scaffold kept", 0) + 1
            return
        text = renderer.render(PAYLOAD.scaffold.read(rel), variables, rel.as_posix())
        TextFile().write(dest, text)
        counts["scaffold created"] = counts.get("scaffold created", 0) + 1

    def _finish(self, root: Path, python: str, counts: dict[str, int]) -> int:
        print(f"codeangel {__version__} → {root}  (runtime python: {python})")
        summary = " · ".join(f"{key}: {value}" for key, value in sorted(counts.items()))
        print(f"  {summary}")
        code = ShimSynchroniser().run(root, check=False)
        print(
            "next: fill the TODOs in AGENTS.md + docs/ai/product.md · add areas: `codeangel add"
            " <preset> <path>` (list: `codeangel presets`) · then `codeangel doctor`"
        )
        return code
