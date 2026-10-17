"""build-loop merge watch (codeangel). Polls GitHub until a pull request is merged; no model calls.

  <runtime.python> .codeangel/skills/build-loop/scripts/await_merge.py <pr> [--interval 300] [--timeout 7200]

<pr> is whatever `gh pr view` accepts: a number, a URL or a branch. Run it from the repository.
Stdlib only, Python >= 3.11. Prints one result line.

Exit codes: 0 merged, 1 closed without merging, 2 gh failed 3 polls in a row (or bad usage), 3 timeout.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections.abc import Callable
from typing import Any

MERGED = 0
CLOSED = 1
FAILED = 2
TIMED_OUT = 3


class GhFailure(Exception):
    pass


class MergeWatcher:
    def __init__(
        self,
        pr: str,
        interval: float = 300,
        timeout: float = 7200,
        max_failures: int = 3,
        run: Callable[..., Any] = subprocess.run,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.pr = pr
        self.interval = interval
        self.timeout = timeout
        self.max_failures = max_failures
        self.run = run
        self.sleep = sleep
        self.clock = clock

    def fetch_state(self) -> str:
        command = ["gh", "pr", "view", self.pr, "--json", "state"]
        try:
            result = self.run(command, capture_output=True, text=True, encoding="utf-8")
        except OSError as error:
            raise GhFailure(str(error)) from error
        if result.returncode != 0:
            raise GhFailure((result.stderr or "gh exited non-zero").strip())
        try:
            return json.loads(result.stdout)["state"]
        except (ValueError, KeyError) as error:
            raise GhFailure(f"unexpected gh output: {result.stdout.strip()[:200]}") from error

    def watch(self) -> int:
        deadline = self.clock() + self.timeout
        failures = 0
        while True:
            try:
                state = self.fetch_state()
                failures = 0
            except GhFailure as error:
                failures += 1
                if failures >= self.max_failures:
                    return self.report(FAILED, f"gh failed {failures} polls in a row: {error}")
            else:
                if state == "MERGED":
                    return self.report(MERGED, "merged")
                if state == "CLOSED":
                    return self.report(CLOSED, "closed without merging")
            remaining = deadline - self.clock()
            if remaining <= 0:
                return self.report(TIMED_OUT, f"still open after {self.timeout:g} s")
            self.sleep(min(self.interval, remaining))

    def report(self, code: int, message: str) -> int:
        print(f"merge-watch {self.pr}: {message} (exit {code})")
        return code


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait until a pull request is merged.")
    parser.add_argument("pr")
    parser.add_argument("--interval", type=float, default=300)
    parser.add_argument("--timeout", type=float, default=7200)
    args = parser.parse_args()
    if args.interval <= 0 or args.timeout <= 0:
        print("merge-watch: --interval and --timeout must be positive", file=sys.stderr)
        return FAILED
    return MergeWatcher(args.pr, args.interval, args.timeout).watch()


if __name__ == "__main__":
    sys.exit(main())
