import re
import subprocess
from pathlib import Path

from codeangel import __version__
from codeangel.install.lockfile import Lockfile
from codeangel.install.shims import ShimSynchroniser
from codeangel.io.files import ContentDigest
from codeangel.project.model import Paths, Project
from codeangel.project.runtime import PythonRuntime


class DoctorReport:
    def __init__(self) -> None:
        self.results: list[tuple[str, str]] = []

    def add(self, level: str, message: str) -> None:
        self.results.append((level, message))

    def emit(self) -> int:
        for level, message in self.results:
            print(f"[{level}] {message}")
        failed = sum(level == "FAIL" for level, _ in self.results)
        warns = sum(level == "warn" for level, _ in self.results)
        print(f"doctor: {failed} problem(s), {warns} warning(s)")
        return 1 if failed else 0


class DoctorCheck:
    def run(self, project: Project, report: DoctorReport) -> None:
        return None


class VersionCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        installed = project.config.get("codeangel", {}).get("version")
        if installed != __version__:
            report.add(
                "warn",
                f"project at codeangel {installed}, CLI is {__version__} → `codeangel update`",
            )


class PythonCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        python = project.config.get("runtime", {}).get("python", "")
        if PythonRuntime().ok(python):
            report.add("ok", f"runtime python `{python}` is >= 3.11")
            return
        report.add(
            "FAIL",
            f"runtime python `{python}` missing or < 3.11 → fix [runtime] python in {Paths.CONFIG}",
        )


class LockCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        lock = Lockfile(project.root).load()
        if not lock:
            report.add("FAIL", f"{Paths.LOCK} missing or empty → `codeangel update`")
        digest = ContentDigest()
        for dest_rel, locked in lock.items():
            self._one(project.root, report, digest, dest_rel, locked)

    def _one(
        self, root: Path, report: DoctorReport, digest: ContentDigest, dest_rel: str, locked: str
    ) -> None:
        dest = root / dest_rel
        if not dest.exists():
            report.add("FAIL", f"managed file missing: {dest_rel} → `codeangel update`")
            return
        if digest.hexdigest(dest.read_bytes()) != locked:
            report.add(
                "warn", f"managed file edited locally: {dest_rel} (update won't overwrite it)"
            )


class ProposalCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        suffix = ".codeangel-new"
        for stray in project.root.rglob(f"*{suffix}"):
            report.add("warn", f"unmerged update: {stray.relative_to(project.root).as_posix()}")


class ShimCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        code = ShimSynchroniser().check_quiet(project.root)
        if code == 0:
            report.add("ok", "Claude skill shims in sync")
            return
        report.add("FAIL", "Claude skill shims out of sync or skill invalid → `codeangel sync`")


class MachineCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        python = project.config.get("runtime", {}).get("python", "")
        if not PythonRuntime().ok(python):
            return
        command = f'{python} "{project.root / Paths.TRANSITION}" show'
        machine = subprocess.run(command, shell=True, capture_output=True)
        if machine.returncode == 0:
            report.add("ok", "build-loop state machine valid")
            return
        report.add("FAIL", "build-loop state machine invalid → run transition.py show")


class DocMapCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        import tomllib

        doc_map = project.root / project.config.get("project", {}).get(
            "doc_map", "docs/ai/doc-map.toml"
        )
        try:
            rules = tomllib.loads(doc_map.read_text(encoding="utf-8")).get("rule", [])
            missing = sorted(
                {doc for rule in rules for doc in rule["docs"] if not (project.root / doc).exists()}
            )
        except (OSError, tomllib.TOMLDecodeError, KeyError) as error:
            report.add("FAIL", f"doc map unreadable: {error}")
            return
        if missing:
            report.add("FAIL", f"doc map names missing docs: {', '.join(missing)}")
            return
        report.add("ok", f"doc map: {len(rules)} rules")


class AreaAgentsCheck(DoctorCheck):
    def run(self, project: Project, report: DoctorReport) -> None:
        for entry in project.config.get("areas", []):
            agents = project.root / entry["path"] / "AGENTS.md"
            if not agents.is_file():
                report.add("FAIL", f"area {entry['path']}: no AGENTS.md")


class AgentsBudgetCheck(DoctorCheck):
    BUDGET = 50

    def run(self, project: Project, report: DoctorReport) -> None:
        for path in self._agents(project):
            lines = len(path.read_text(encoding="utf-8").splitlines())
            if lines > self.BUDGET:
                shown = path.relative_to(project.root).as_posix()
                report.add("warn", f"{shown}: {lines} lines > {self.BUDGET}")

    def _agents(self, project: Project) -> list[Path]:
        files = [project.root / "AGENTS.md"]
        for entry in project.config.get("areas", []):
            agents = project.root / entry["path"] / "AGENTS.md"
            if agents.is_file():
                files.append(agents)
        return files


class DocLinkCheck(DoctorCheck):
    _paths = re.compile(r"`((?:\.?[\w-]+/)+[\w.-]+\.(?:md|toml|py|ya?ml|json))`")

    def run(self, project: Project, report: DoctorReport) -> None:
        for path in self._docs(project):
            self._scan(project.root, path, report)

    def _scan(self, root: Path, path: Path, report: DoctorReport) -> None:
        if not path.is_file():
            return
        for ref in self._paths.findall(path.read_text(encoding="utf-8")):
            head = root / ref.split("/")[0]
            if head.exists() and not (root / ref).exists():
                report.add("warn", f"{path.relative_to(root).as_posix()} → missing {ref}")

    def _docs(self, project: Project) -> list[Path]:
        agents = AgentsBudgetCheck()._agents(project)
        docs = agents + sorted((project.root / "docs/ai").glob("*.md"))
        for entry in project.config.get("areas", []):
            docs += sorted((project.root / entry["path"] / "docs/ai").glob("*.md"))
        return docs


class Doctor:
    def __init__(self, project: Project) -> None:
        self.project = project
        self.report = DoctorReport()
        self.checks: list[DoctorCheck] = [
            VersionCheck(),
            PythonCheck(),
            LockCheck(),
            ProposalCheck(),
            ShimCheck(),
            MachineCheck(),
            DocMapCheck(),
            AreaAgentsCheck(),
            AgentsBudgetCheck(),
            DocLinkCheck(),
        ]

    def run(self) -> int:
        for check in self.checks:
            check.run(self.project, self.report)
        return self.report.emit()
