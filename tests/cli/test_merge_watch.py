from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from support import AWAIT_MERGE, load_script

from codeangel.install.tree import PAYLOAD

SKILL = PAYLOAD.managed.base / "dot_codeangel/skills/build-loop/SKILL.md"
SOURCE = PAYLOAD.managed.base / "dot_codeangel"
SCRIPT = "skills/build-loop/scripts/await_merge.py"


def load_source_script():
    return load_script(SOURCE, SCRIPT)


class FakeGh:
    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        self.commands.append(command)
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if reply == "FAIL":
            return subprocess.CompletedProcess(command, 1, stdout="", stderr="gh: network down")
        return subprocess.CompletedProcess(command, 0, stdout=json.dumps({"state": reply}))


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


class TestMergeWatcher:
    def watcher(self, replies: list[str], **options):
        module = load_source_script()
        gh = FakeGh(replies)
        clock = FakeClock()
        watcher = module.MergeWatcher(
            "https://github.com/o/r/pull/7",
            run=gh,
            sleep=clock.sleep,
            clock=clock.monotonic,
            **options,
        )
        return watcher, gh, clock

    def test_defaults_poll_every_five_minutes_for_two_hours(self):
        module = load_source_script()

        watcher = module.MergeWatcher("7")

        assert watcher.interval == 300
        assert watcher.timeout == 7200

    def test_asks_github_cli_for_the_pr_state(self):
        watcher, gh, _ = self.watcher(["MERGED"])

        watcher.watch()

        assert gh.commands == [
            ["gh", "pr", "view", "https://github.com/o/r/pull/7", "--json", "state"]
        ]

    def test_exits_zero_as_soon_as_the_pr_is_merged(self):
        watcher, gh, clock = self.watcher(["OPEN", "OPEN", "MERGED"])

        assert watcher.watch() == 0
        assert clock.sleeps == [300, 300]
        assert len(gh.commands) == 3

    def test_exits_three_when_still_open_at_the_timeout(self):
        watcher, gh, clock = self.watcher(["OPEN"])

        assert watcher.watch() == 3
        assert sum(clock.sleeps) == 7200
        assert len(gh.commands) == 25

    def test_exits_one_when_the_pr_is_closed_unmerged(self):
        watcher, gh, clock = self.watcher(["CLOSED"])

        assert watcher.watch() == 1
        assert clock.sleeps == []
        assert len(gh.commands) == 1

    def test_exits_two_after_three_consecutive_gh_failures(self):
        recovered, _, _ = self.watcher(["FAIL", "FAIL", "OPEN", "FAIL", "FAIL", "MERGED"])
        failing, gh, _ = self.watcher(["FAIL"])

        assert recovered.watch() == 0
        assert failing.watch() == 2
        assert len(gh.commands) == 3

    def test_script_is_installed_into_projects(self, project: Path):
        installed = project / AWAIT_MERGE

        assert installed.is_file()
        assert hasattr(load_script(project, AWAIT_MERGE), "MergeWatcher")


class TestBuildLoopInstructions:
    def section(self, start: str, end: str) -> str:
        text = SKILL.read_text(encoding="utf-8")
        match = re.search(re.escape(start) + r".*?(?=" + re.escape(end) + r")", text, re.S)
        assert match, start
        return match.group(0)

    def test_startup_sets_in_progress_before_planning(self):
        startup = self.section("## STARTUP", "## Dispatch")

        assert "save_issue" in startup
        assert "In Progress" in startup
        assert "started" in startup
        assert "Never blocks" in startup

    def test_merge_watch_runs_the_script_and_never_recalls_the_skill(self):
        watch = self.section("## MERGE WATCH", "## Final report")

        assert "scripts/await_merge.py" in watch
        assert "no model call" in watch
        assert "DONE" in watch
        assert "draft" in watch
        assert "background" in watch

    def test_merge_outcomes_map_to_linear_status(self):
        watch = self.section("## MERGE WATCH", "## Final report")
        rows = {
            match.group(1): match.group(2)
            for match in re.finditer(r"^\s*\| (\d) \| (.*)$", watch, re.M)
        }

        assert "Done" in rows["0"]
        for code in ("1", "2", "3"):
            assert "unchanged" in rows[code]
