"""build-loop state machine (codeangel). Enforces references/stages.toml on <spec_dir>/<TICKET>.md.

Run from anywhere in the repo (stdlib only, Python >= 3.11):
  <runtime.python> .codeangel/skills/build-loop/scripts/transition.py <command> ...
Project settings (spec dir, doc map, ticket pattern, areas) come from .codeangel/codeangel.toml.

  init   <TICKET> --mode plan|immediate --title T --branch B --base-sha SHA [--url U] [--source S]
  status <TICKET>                  stage, attempt, every legal exit with its check results
  go     <TICKET> <exit-status> [--note TEXT]
  log    <TICKET> TEXT             log line without a stage change
  docs   <TICKET>                  docs the change must update (docs/ai/doc-map.toml) vs §Docs impact
  evidence <TICKET>                create the git-ignored evidence dir and print it
  publish <TICKET>                 push the evidence screenshots / videos to branch evidence/<TICKET>; print its sha
  proof  <TICKET> [--repo OWNER/REPO --sha SHA] [--into FILE]   render §Evidence as the PR's '## Proof' section
  show   [STAGE]                   print the map

Exit codes: 0 ok, 1 refused (reasons printed), 2 usage error / missing spec / broken map.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = SKILL_DIR.parent
ROOT = SKILL_DIR.parents[2]
CONFIG_PATH = ROOT / ".codeangel" / "codeangel.toml"
CONFIG: dict[str, Any] = (
    tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8")) if CONFIG_PATH.is_file() else {}
)
PROJECT: dict[str, Any] = CONFIG.get("project", {})
SPEC_DIR = ROOT / PROJECT.get("spec_dir", "docs/specs")
DOC_MAP = ROOT / PROJECT.get("doc_map", "docs/ai/doc-map.toml")
TEST_ROOTS = [ROOT / area["path"] for area in CONFIG.get("areas", [])] + [ROOT]
TEMPLATE = SKILL_DIR / "assets" / "spec-template.md"
SHIM_SYNC = ROOT / ".codeangel" / "sync-shims.py"
DOC_STATUSES = ("updated", "unchanged")
MAP: dict[str, Any] = tomllib.loads(
    (SKILL_DIR / "references" / "stages.toml").read_text(encoding="utf-8")
)

TICKET_RE = re.compile(PROJECT.get("ticket_pattern", r"^[A-Z][A-Z0-9]+-\d+$"))
FM_LINE_RE = re.compile(r"^(?P<key>[a-z_]+):[ \t]*(?P<value>.*?)(?P<comment>[ \t]+#.*)?$")
SECTION_RE = re.compile(r"^## (.+)$", re.M)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
SEPARATOR_RE = re.compile(r"^\|[\s:|-]+\|?$")
AC_RE = re.compile(r"^- \[([ xX])\] (AC-\d+)\b", re.M)
ATTEMPT_RE = re.compile(r"^### Attempt (\d+) [—-] (PASS|FAIL)\b", re.M)
REVIEW_ENTRY_RE = re.compile(r"(\S+) → REVIEW \[")
AC_LINE_RE = re.compile(r"^- \[[ xX]\] (?P<id>AC-\d+)\b(?P<rest>.*)$", re.M)
PROOF_RE = re.compile(
    r"\[proof: (?P<kinds>(?:api|ui|cli)(?:\s*\+\s*(?:api|ui|cli))*|none\s*[—-]\s*[^\]]+)\]"
)
EVIDENCE_KINDS = ("api", "ui", "cli", "none")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".webm", ".mov"}
MEDIA_SUFFIXES = IMAGE_SUFFIXES | VIDEO_SUFFIXES
MEDIA_MAX_BYTES = 50 * 1024 * 1024
TEXT_SUFFIXES = {".txt", ".md", ".json", ".log", ".http", ".html", ".xml", ".yaml", ".yml", ".csv"}
SECRET_RE = re.compile(
    r"\b(?:sessionid|session_id|csrftoken|password|passwd|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|token)\b[\"']?\s*[=:]\s*[\"']?(?!<?redacted)[A-Za-z0-9._~+/=-]{12,}",
    re.I,
)
AUTH_HEADER_RE = re.compile(
    r"\bauthorization\b[\"']?\s*[=:]\s*[\"']?(?:bearer|basic|token)\s+(?!<?redacted)[A-Za-z0-9._~+/=-]{12,}",
    re.I,
)
PROOF_BEGIN = "<!-- proof:start -->"
PROOF_END = "<!-- proof:end -->"
PROOF_MAX_LINES = 6
PROOF_TITLE_CHARS = 100


def _commented_keys() -> set[str]:
    """Frontmatter keys that carry an inline `# comment` in the template; free-text keys never do."""
    front = TEMPLATE.read_text(encoding="utf-8").split("---\n", 2)[1]
    matches = (FM_LINE_RE.match(line) for line in front.splitlines())
    return {match["key"] for match in matches if match and match["comment"]}


COMMENTED_KEYS = _commented_keys()


class Refused(Exception):
    pass


class UsageError(Exception):
    pass


def now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%MZ")


class Spec:
    def __init__(self, text: str) -> None:
        text = text.replace("\r\n", "\n")
        if not text.startswith("---\n"):
            raise UsageError("spec has no frontmatter")
        _, self.front, self.body = text.split("---\n", 2)

    def text(self) -> str:
        return f"---\n{self.front}---\n{self.body}"

    @staticmethod
    def _split(match: re.Match[str]) -> tuple[str, str]:
        """(value, comment); only template-commented keys have comments, so '#' in notes survives."""
        if match["key"] in COMMENTED_KEYS:
            return match["value"].strip(), match["comment"] or ""
        return f"{match['value']}{match['comment'] or ''}".strip(), ""

    def get(self, key: str) -> str:
        for line in self.front.splitlines():
            match = FM_LINE_RE.match(line)
            if match and match["key"] == key:
                return self._split(match)[0]
        return ""

    def set(self, key: str, value: str) -> None:
        lines = self.front.splitlines()
        for i, line in enumerate(lines):
            match = FM_LINE_RE.match(line)
            if match and match["key"] == key:
                lines[i] = f"{key}:{' ' if value else ''}{value}{self._split(match)[1]}"
                break
        else:
            lines.append(f"{key}: {value}")
        self.front = "\n".join(lines) + "\n"

    def sections(self) -> dict[str, str]:
        parts = SECTION_RE.split(self.body)
        return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}

    def section(self, name: str) -> str:
        return COMMENT_RE.sub("", self.sections().get(name, ""))

    def append_log(self, line: str) -> None:
        heading = re.search(r"^## Log\n", self.body, re.M)
        if heading is None:
            self.body = self.body.rstrip("\n") + "\n\n## Log\n"
            heading = re.search(r"^## Log\n", self.body, re.M)
        following = SECTION_RE.search(self.body, heading.end())
        end = following.start() if following else len(self.body)
        head, tail = self.body[:end].rstrip("\n"), self.body[end:]
        self.body = f"{head}\n{line}\n" + (f"\n{tail}" if tail else "")


def content_lines(section: str) -> list[str]:
    """Meaningful lines: no blanks, comments, table headers or separator rows."""
    raw = [line.strip() for line in COMMENT_RE.sub("", section).splitlines()]
    lines = []
    for i, line in enumerate(raw):
        if not line or SEPARATOR_RE.match(line):
            continue
        if line.startswith("|") and i + 1 < len(raw) and SEPARATOR_RE.match(raw[i + 1]):
            continue
        lines.append(line)
    return lines


def table_rows(section: str) -> list[list[str]]:
    return [
        [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        for line in content_lines(section)
        if line.startswith("|")
    ]


def template_lines(name: str) -> set[str]:
    template = Spec(TEMPLATE.read_text(encoding="utf-8"))
    return set(content_lines(template.sections().get(name, "")))


# ── checks: (spec, note) -> problems; empty list = pass ──────────────────────


def check_plan_complete(spec: Spec, note: str) -> list[str]:
    problems = []
    sections = spec.sections()
    for name in MAP["plan_sections"]:
        if name not in sections:
            problems.append(f"§{name} missing")
            continue
        lines = content_lines(sections[name])
        stale = [line for line in lines if line in template_lines(name)]
        if stale:
            problems.append(f"§{name} still has template line: {stale[0]}")
        elif not lines:
            problems.append(f"§{name} has no content")
    return problems


def check_ac_test_mapping(spec: Spec, note: str) -> list[str]:
    acs = [ac for _, ac in AC_RE.findall(spec.section("Acceptance criteria"))]
    if not acs:
        return ["§Acceptance criteria has no '- [ ] AC-n: …' lines"]
    rows = table_rows(spec.section("Test plan"))
    if not rows:
        return ["§Test plan has no rows"]
    problems, covered = [], set()
    for row in rows:
        ids = re.findall(r"AC-\d+", row[1] if len(row) > 1 else "")
        if not ids:
            problems.append(f"test {row[0]} covers no AC")
        unknown = [ac for ac in ids if ac not in acs]
        if unknown:
            problems.append(f"test {row[0]} covers unknown {', '.join(unknown)}")
        covered.update(ids)
    return problems + [f"{ac} has no test" for ac in acs if ac not in covered]


def check_no_blocking_risks(spec: Spec, note: str) -> list[str]:
    risks = content_lines(spec.section("Risks / open questions"))
    return [f"blocking: {line}" for line in risks if re.search(r"\[blocking\]", line, re.I)]


def planned_kinds(rest: str) -> set[str]:
    match = PROOF_RE.search(rest)
    if match is None:
        return set()
    kinds = match["kinds"]
    if kinds.startswith("none"):
        return {"none"}
    return {kind.strip() for kind in kinds.split("+")}


def acceptance_criteria(spec: Spec) -> dict[str, str]:
    return {
        m["id"]: m["rest"].strip() for m in AC_LINE_RE.finditer(spec.section("Acceptance criteria"))
    }


def check_ac_proof_planned(spec: Spec, note: str) -> list[str]:
    return [
        f"{ac} has no [proof: api|ui|cli|none — reason] tag"
        for ac, rest in acceptance_criteria(spec).items()
        if not planned_kinds(rest)
    ]


def evidence_rows(spec: Spec) -> list[list[str]]:
    stale = template_lines("Evidence")
    lines = [
        line
        for line in content_lines(spec.section("Evidence"))
        if line.startswith("|") and line not in stale
    ]
    return [
        [
            cell.strip().strip("`") if index < 3 else cell.strip()
            for index, cell in enumerate(line.strip("|").split("|"))
        ]
        for line in lines
    ]


def evidence_dir(ticket: str) -> Path:
    return SPEC_DIR / "evidence" / ticket


def prepare_evidence(ticket: str) -> Path:
    home = evidence_dir(ticket)
    home.mkdir(parents=True, exist_ok=True)
    marker = home / ".gitignore"
    if not marker.is_file():
        marker.write_text("*\n", encoding="utf-8", newline="\n")
    return home


def tracked_evidence(ticket: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=off",
            "ls-files",
            "--",
            evidence_dir(ticket).relative_to(ROOT).as_posix(),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return [line for line in result.stdout.splitlines() if line] if result.returncode == 0 else []


def evidence_tracking_problems(ticket: str) -> list[str]:
    home = evidence_dir(ticket)
    if not home.is_dir():
        return []
    where = home.relative_to(ROOT).as_posix()
    marker = home / ".gitignore"
    problems = []
    if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != "*":
        problems.append(f"{where}/ is not git-ignored → run `T evidence {ticket}`")
    problems += [
        f"{path} is tracked by git → `git rm --cached -r {where}`; evidence is shown in the PR, never committed"
        for path in tracked_evidence(ticket)
    ]
    return problems


def reason_after(proof: str, prefix: str) -> str | None:
    if proof.lower().startswith(prefix):
        return proof[len(prefix) :].strip()
    return None


def artefact_problems(ac: str, proof: str, ticket: str) -> list[str]:
    home = evidence_dir(ticket).resolve()
    problems = []
    items = list(filter(None, (part.strip() for part in proof.split(","))))
    for item in items:
        file = (ROOT / item).resolve()
        if home not in file.parents:
            problems.append(f"{ac}: {item} is not under {home.relative_to(ROOT).as_posix()}/")
        elif not file.is_file() or file.stat().st_size == 0:
            problems.append(f"{ac}: {item} is missing or empty")
    if not items:
        return [f"{ac}: proof cell is empty"]
    return problems


def evidence_row_problems(row: list[str], acs: dict[str, str], ticket: str) -> list[str]:
    if len(row) < 3 or row[0] not in acs:
        return [
            f"§Evidence row {row[0] if row else '?'}: expected '| AC-n | kind | proof | note |' for a known AC"
        ]
    ac, kind, proof = row[0], row[1].lower(), row[2]
    planned = planned_kinds(acs[ac])
    if kind not in EVIDENCE_KINDS:
        return [f"{ac}: kind {row[1]!r} must be api, ui, cli or none"]
    if reason_after(proof, "not captured:"):
        return []
    if reason_after(proof, "n/a:"):
        return (
            []
            if kind == "none" and planned == {"none"}
            else [f"{ac}: n/a is only for kind none planned none"]
        )
    if kind == "none" and planned != {"none"}:
        return [
            f"{ac}: planned {'+'.join(sorted(planned))} but kind is none → capture it or write 'not captured: <reason>'"
        ]
    return artefact_problems(ac, proof, ticket)


def credential_problems(where: str, text: str) -> list[str]:
    hit = SECRET_RE.search(text) or AUTH_HEADER_RE.search(text)
    if hit is None:
        return []
    name = re.split(r"[=:]", hit[0], maxsplit=1)[0].strip(" \"'")
    return [f"{where}: credential-looking value for '{name}' → replace it with <redacted>"]


def evidence_secret_problems(spec: Spec, ticket: str) -> list[str]:
    problems = credential_problems("§Evidence", spec.section("Evidence"))
    home = evidence_dir(ticket)
    files = sorted(home.rglob("*")) if home.is_dir() else []
    for file in files:
        if file.is_file() and file.suffix.lower() in TEXT_SUFFIXES:
            where = file.relative_to(ROOT).as_posix()
            problems += credential_problems(
                where, file.read_text(encoding="utf-8", errors="ignore")
            )
    return problems


def missing_kind_problems(rows: list[list[str]], acs: dict[str, str]) -> list[str]:
    problems = []
    for ac, rest in acs.items():
        mine = [row for row in rows if row and row[0] == ac]
        if not mine:
            problems.append(f"{ac} has no row in §Evidence")
            continue
        kinds = {row[1].lower() for row in mine if len(row) > 1}
        problems += [
            f"{ac}: planned {kind} but §Evidence has no {kind} row"
            for kind in sorted(planned_kinds(rest) - {"none"} - kinds)
        ]
    return problems


def check_evidence_recorded(spec: Spec, note: str) -> list[str]:
    acs = acceptance_criteria(spec)
    if not acs:
        return ["§Acceptance criteria has no '- [ ] AC-n: …' lines"]
    rows = evidence_rows(spec)
    ticket = spec.get("ticket")
    problems = [p for row in rows for p in evidence_row_problems(row, acs, ticket)]
    return (
        problems
        + missing_kind_problems(rows, acs)
        + evidence_secret_problems(spec, ticket)
        + evidence_tracking_problems(ticket)
    )


def check_planned_tests_exist(spec: Spec, note: str) -> list[str]:
    rows = table_rows(spec.section("Test plan"))
    if not rows:
        return ["§Test plan has no rows"]
    problems = []
    for row in rows:
        path, _, rest = row[0].partition("::")
        file = next((root / path for root in TEST_ROOTS if (root / path).is_file()), None)
        if file is None:
            roots = ", ".join(root.relative_to(ROOT).as_posix() for root in TEST_ROOTS)
            problems.append(f"{row[0]}: {path} not found under any test root ({roots})")
            continue
        source = file.read_text(encoding="utf-8")
        where = file.relative_to(ROOT).as_posix()
        for name in filter(None, rest.split("::")):
            name = re.sub(r"\[.*\]$", "", name)
            if not re.search(rf"\b{re.escape(name)}\b", source):
                problems.append(f"{row[0]}: '{name}' not found in {where}")
    return problems


def _latest_attempt(spec: Spec, expected: str) -> list[str]:
    reports = ATTEMPT_RE.findall(spec.section("Verify reports"))
    if not reports:
        return ["§Verify reports has no '### Attempt N — PASS|FAIL' heading"]
    number, status = reports[-1]
    want = int(spec.get("attempt") or 0) + 1
    problems = []
    if int(number) != want:
        problems.append(f"latest report is Attempt {number}; expected Attempt {want}")
    if status != expected:
        problems.append(f"latest report says {status}, not {expected}")
    return problems


def check_latest_attempt_pass(spec: Spec, note: str) -> list[str]:
    return _latest_attempt(spec, "PASS")


def check_latest_attempt_fail(spec: Spec, note: str) -> list[str]:
    return _latest_attempt(spec, "FAIL")


def check_all_ac_ticked(spec: Spec, note: str) -> list[str]:
    acs = AC_RE.findall(spec.section("Acceptance criteria"))
    return [f"{ac} not ticked" for box, ac in acs if box == " "]


def check_pr_recorded(spec: Spec, note: str) -> list[str]:
    return [] if spec.get("pr").startswith(("http://", "https://")) else ["frontmatter pr is empty"]


def check_learnings_recorded(spec: Spec, note: str) -> list[str]:
    stale = template_lines("Learnings")
    lines = [line for line in content_lines(spec.section("Learnings")) if line not in stale]
    return [] if lines else ["§Learnings is empty (write 'none: <why>' if nothing was learned)"]


def check_note_required(spec: Spec, note: str) -> list[str]:
    return [] if note else ["--note is required for this exit"]


def check_ci_flaky_once(spec: Spec, note: str) -> list[str]:
    lines = spec.section("Log").splitlines()
    entries = [
        i
        for i, line in enumerate(lines)
        if (match := REVIEW_ENTRY_RE.search(line)) and match[1] != "REVIEW"
    ]
    since = lines[entries[-1] :] if entries else lines
    if any("[ci_flaky]" in line for line in since):
        return ["ci_flaky already used since entering REVIEW → use ci_red_code"]
    return []


# ── docs move with code ───────────────────────────────────────────────────────


def git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-c", "core.quotepath=off", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise UsageError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line]


def changed_files(base_sha: str) -> list[str]:
    """Repo-relative paths changed since base_sha (committed, staged, unstaged, untracked)."""
    paths = set(git_lines("diff", "--name-only", base_sha))
    paths |= set(git_lines("ls-files", "--others", "--exclude-standard"))
    return sorted(path for path in paths if not path.startswith("docs/specs/"))


def required_docs(paths: list[str]) -> dict[str, list[str]]:
    """doc → reasons, for every doc-map rule whose globs match one of `paths`."""
    if not DOC_MAP.is_file():
        return {}
    needed: dict[str, list[str]] = {}
    for rule in tomllib.loads(DOC_MAP.read_text(encoding="utf-8")).get("rule", []):
        hits = [p for p in paths if any(fnmatch.fnmatchcase(p, g) for g in rule["paths"])]
        if hits:
            more = f" +{len(hits) - 1}" if len(hits) > 1 else ""
            for doc in rule["docs"]:
                needed.setdefault(doc, []).append(f"{rule['why']} [{hits[0]}{more}]")
    return needed


def docs_impact(spec: Spec) -> dict[str, tuple[str, str]]:
    """§Docs impact rows: doc → (status, note)."""
    rows = table_rows(spec.section("Docs impact"))
    return {
        row[0]: (row[1].lower() if len(row) > 1 else "", row[2] if len(row) > 2 else "")
        for row in rows
    }


def doc_hygiene(changed: list[str]) -> list[str]:
    """What area linters may miss: whitespace in changed docs, generated skill shims."""
    problems = []
    for path in changed:
        file = ROOT / path
        if file.suffix not in {".md", ".toml"} or not file.is_file():
            continue
        text = file.read_text(encoding="utf-8")
        if text and not text.endswith("\n"):
            problems.append(f"{path}: no final newline")
        if re.search(r"[ \t]+\r?$", text, re.M):
            problems.append(f"{path}: trailing whitespace")
    if any(fnmatch.fnmatchcase(p, ".codeangel/skills/*/SKILL.md") for p in changed):
        result = subprocess.run(
            [sys.executable, str(SHIM_SYNC), "--check"], cwd=ROOT, capture_output=True, text=True
        )
        if result.returncode != 0:
            problems.append("Claude skill shims out of sync → run: python .codeangel/sync-shims.py")
    return problems


def check_docs_synced(spec: Spec, note: str) -> list[str]:
    try:
        changed = changed_files(spec.get("base_sha"))
    except UsageError as error:
        return [str(error)]
    impact = docs_impact(spec)
    problems = [
        f"{doc} missing from §Docs impact — {reasons[0]}"
        for doc, reasons in required_docs(changed).items()
        if doc not in impact
    ]
    for doc, (status, why) in impact.items():
        if status not in DOC_STATUSES:
            problems.append(f"§Docs impact {doc}: status must be updated or unchanged")
        elif status == "updated" and doc not in changed:
            problems.append(f"§Docs impact {doc}: marked updated but unchanged since base_sha")
        elif status == "unchanged" and not why:
            problems.append(f"§Docs impact {doc}: unchanged needs a reason")
    return problems + doc_hygiene(changed)


CHECKS: dict[str, Callable[[Spec, str], list[str]]] = {
    "plan_complete": check_plan_complete,
    "ac_test_mapping": check_ac_test_mapping,
    "ac_proof_planned": check_ac_proof_planned,
    "no_blocking_risks": check_no_blocking_risks,
    "planned_tests_exist": check_planned_tests_exist,
    "latest_attempt_pass": check_latest_attempt_pass,
    "latest_attempt_fail": check_latest_attempt_fail,
    "all_ac_ticked": check_all_ac_ticked,
    "pr_recorded": check_pr_recorded,
    "learnings_recorded": check_learnings_recorded,
    "note_required": check_note_required,
    "ci_flaky_once": check_ci_flaky_once,
    "docs_synced": check_docs_synced,
    "evidence_recorded": check_evidence_recorded,
}
EFFECTS = {"increment_attempt", "set_blocked", "clear_blocked", "set_mode_immediate"}


def validate_map() -> None:
    stages = MAP["stages"]
    errors = []
    if set(MAP["checks"]) != set(CHECKS):
        errors.append(f"[checks] {sorted(MAP['checks'])} != implemented {sorted(CHECKS)}")
    if set(MAP["effects"]) != EFFECTS:
        errors.append(f"[effects] {sorted(MAP['effects'])} != implemented {sorted(EFFECTS)}")
    exits = [(name, e) for name, st in stages.items() for e in st.get("exits", [])]
    exits += [("*", e) for e in MAP["global_exits"]]
    for name, e in exits:
        where = f"{name}.{e.get('status')}"
        if e.get("to") not in stages and e.get("to") != "@blocked_stage":
            errors.append(f"{where}: unknown target {e.get('to')!r}")
        errors += [f"{where}: unknown check {c!r}" for c in e.get("checks", []) if c not in CHECKS]
        errors += [
            f"{where}: unknown effect {f!r}" for f in e.get("effects", []) if f not in EFFECTS
        ]
        if not e.get("when"):
            errors.append(f"{where}: missing 'when'")
    for name in MAP["terminal"]:
        if stages.get(name, {}).get("exits"):
            errors.append(f"terminal stage {name} has exits")
    for name, st in stages.items():
        if not (SKILLS_DIR / st.get("owner", "") / "SKILL.md").is_file():
            errors.append(f"{name}: owner skill {st.get('owner')!r} has no SKILL.md")
    if errors:
        raise UsageError("stages.toml is inconsistent:\n  " + "\n  ".join(errors))


def exits_for(stage: str, mode: str) -> list[dict[str, Any]]:
    exits = [e for e in MAP["stages"][stage].get("exits", []) if e.get("mode", mode) == mode]
    if stage not in MAP["terminal"]:
        exits += [e for e in MAP["global_exits"] if e["to"] != stage]
    return exits


def run_checks(exit_: dict[str, Any], spec: Spec, note: str, skip_note: bool = False) -> list[str]:
    names = [c for c in exit_.get("checks", []) if not (skip_note and c == "note_required")]
    return [problem for name in names for problem in CHECKS[name](spec, note)]


def spec_path(ticket: str) -> Path:
    if not TICKET_RE.match(ticket):
        raise UsageError(f"ticket {ticket!r} is not a Linear ID like ABC-123")
    return SPEC_DIR / f"{ticket}.md"


def load(ticket: str) -> tuple[Path, Spec]:
    path = spec_path(ticket)
    if not path.is_file():
        raise UsageError(f"{path.relative_to(ROOT).as_posix()} not found — run `init` first")
    spec = Spec(path.read_text(encoding="utf-8"))
    if spec.get("stage") not in MAP["stages"]:
        raise UsageError(f"frontmatter stage {spec.get('stage')!r} is not a known stage")
    return path, spec


def save(path: Path, spec: Spec) -> None:
    path.write_text(spec.text(), encoding="utf-8", newline="\n")


def owner_ref(stage: dict[str, Any]) -> str:
    return f"{stage['owner']} (.codeangel/skills/{stage['owner']}/SKILL.md)"


def target_label(exit_: dict[str, Any], spec: Spec | None) -> str:
    if exit_["to"] == "@blocked_stage" and spec is not None:
        return f"{spec.get('blocked_stage')} (blocked_stage)"
    return exit_["to"]


def describe_exits(stage: str, mode: str, spec: Spec | None = None) -> str:
    exits = exits_for(stage, mode)
    return " | ".join(f"{e['status']} → {target_label(e, spec)}" for e in exits) or "none"


def print_next(spec: Spec) -> None:
    stage = MAP["stages"][spec.get("stage")]
    print(f"next: run skill {owner_ref(stage)} — {stage['does']}")
    print(f"exits: {describe_exits(spec.get('stage'), spec.get('mode'), spec)}")


# ── commands ──────────────────────────────────────────────────────────────────


def cmd_init(args: argparse.Namespace) -> None:
    path = spec_path(args.ticket)
    if path.exists():
        raise Refused(
            f"{path.relative_to(ROOT).as_posix()} exists — resume it (status / go), don't re-init"
        )
    spec = Spec(TEMPLATE.read_text(encoding="utf-8"))
    stamp = now()
    values = {
        "ticket": args.ticket,
        "title": args.title,
        "mode": args.mode,
        "source": args.source,
        "url": args.url,
        "branch": args.branch,
        "base_sha": args.base_sha,
        "pr": "",
        "stage": "PLAN",
        "last_status": "init",
        "attempt": "0",
        "blocked_stage": "",
        "blocked_reason": "",
        "created": stamp,
        "updated": stamp,
    }
    for key, value in values.items():
        spec.set(key, value)
    spec.body = spec.body.replace("# <TICKET>: <title>", f"# {args.ticket}: {args.title}", 1)
    spec.body = re.sub(r"^## Log\n[\s\S]*\Z", "## Log\n", spec.body, flags=re.M)
    spec.append_log(
        f"- {stamp} STARTUP → PLAN [init] attempt=0/{MAP['max_attempts']} — "
        f"mode={args.mode}, branch={args.branch}, base={args.base_sha[:10]}"
    )
    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    save(path, spec)
    print(
        f"{args.ticket}: created {path.relative_to(ROOT).as_posix()} · stage PLAN · mode {args.mode}"
    )
    print_next(spec)


def cmd_go(args: argparse.Namespace) -> None:
    path, spec = load(args.ticket)
    note = " ".join((args.note or "").split())
    stage, mode = spec.get("stage"), spec.get("mode")
    exits = exits_for(stage, mode)
    exit_ = next((e for e in exits if e["status"] == args.status), None)
    if exit_ is None:
        raise Refused(
            f"'{args.status}' is not an exit of {stage} (mode={mode}). "
            f"Legal: {describe_exits(stage, mode)}"
        )
    problems = run_checks(exit_, spec, note)
    if problems:
        lines = "\n".join(f"  ✗ {p}" for p in problems)
        raise Refused(f"{stage} → {target_label(exit_, spec)} [{args.status}] refused:\n{lines}")

    target, effects = exit_["to"], exit_.get("effects", [])
    attempt = int(spec.get("attempt") or 0)
    if target == "@blocked_stage":
        target = spec.get("blocked_stage")
        if target not in MAP["stages"]:
            raise Refused(f"blocked_stage {target!r} is not a stage; fix the frontmatter by hand")
    if "clear_blocked" in effects:
        if spec.get("blocked_reason").startswith("attempt cap"):
            attempt = 0
        spec.set("blocked_stage", "")
        spec.set("blocked_reason", "")
    if "set_blocked" in effects:
        spec.set("blocked_stage", stage)
        spec.set("blocked_reason", note)
    if "set_mode_immediate" in effects:
        spec.set("mode", "immediate")
    if "increment_attempt" in effects:
        attempt += 1
        if attempt >= MAP["max_attempts"]:
            spec.set("blocked_stage", target)
            spec.set("blocked_reason", f"attempt cap {MAP['max_attempts']} reached; last: {note}")
            target = "BLOCKED"

    spec.set("stage", target)
    spec.set("last_status", args.status)
    spec.set("attempt", str(attempt))
    spec.set("updated", now())
    detail = f" — {note}" if note else ""
    spec.append_log(
        f"- {now()} {stage} → {target} [{args.status}] "
        f"attempt={attempt}/{MAP['max_attempts']}{detail}"
    )
    save(path, spec)
    print(
        f"{args.ticket}: {stage} → {target} [{args.status}] · attempt {attempt}/{MAP['max_attempts']}"
    )
    if target == "BLOCKED":
        print(f"blocked: {spec.get('blocked_reason')} (resumes at {spec.get('blocked_stage')})")
    print_next(spec)


def cmd_status(args: argparse.Namespace) -> None:
    _, spec = load(args.ticket)
    stage, mode = spec.get("stage"), spec.get("mode")
    print(
        f"{args.ticket} · stage {stage} · mode {mode} · "
        f"attempt {spec.get('attempt') or 0}/{MAP['max_attempts']} · last {spec.get('last_status') or '-'}"
    )
    if stage == "BLOCKED":
        print(f"blocked at {spec.get('blocked_stage')}: {spec.get('blocked_reason')}")
    info = MAP["stages"][stage]
    print(f"does: {info['does']}\nowner: {owner_ref(info)}")
    for item in info.get("produces", []):
        print(f"  produces  {item}")
    for exit_ in exits_for(stage, mode):
        problems = run_checks(exit_, spec, "", skip_note=True)
        note = " (needs --note)" if "note_required" in exit_.get("checks", []) else ""
        state = "✓ ready" if not problems else f"✗ {len(problems)} unmet"
        print(f"  exit {exit_['status']:<16} → {target_label(exit_, spec):<17} {state}{note}")
        for problem in problems:
            print(f"       ✗ {problem}")


def cmd_log(args: argparse.Namespace) -> None:
    path, spec = load(args.ticket)
    spec.set("updated", now())
    spec.append_log(f"- {now()} {spec.get('stage')} · {' '.join(args.text.split())}")
    save(path, spec)
    print(f"{args.ticket}: logged at {spec.get('stage')}")


def cmd_docs(args: argparse.Namespace) -> None:
    _, spec = load(args.ticket)
    base = spec.get("base_sha")
    changed = changed_files(base) if base else []
    planned = [row[0] for row in table_rows(spec.section("Affected files")) if "/" in row[0]]
    impact = docs_impact(spec)
    needed = required_docs(sorted(set(changed) | set(planned)))
    print(f"{args.ticket}: {len(changed)} changed since {base[:10] or '-'}, {len(planned)} planned")
    if not needed:
        print("  no doc-map rule matches → §Docs impact may be '- none: <why>'")
    for doc, reasons in sorted(needed.items()):
        status, why = impact.get(doc, ("missing", ""))
        done = (status == "updated" and doc in changed) or (status == "unchanged" and why)
        print(f"  {'✓' if done else '✗'} {doc:<46} {status or 'missing':<9} {reasons[0]}")
    problems = check_docs_synced(spec, "") if base else ["frontmatter base_sha is empty"]
    print("docs_synced: ✓ ready" if not problems else f"docs_synced: ✗ {len(problems)} unmet")
    for problem in problems:
        print(f"  ✗ {problem}")


# ── proof for the pull request ────────────────────────────────────────────────


def fence_for(text: str) -> str:
    return "````" if "```" in text else "```"


def captured_artefacts(spec: Spec) -> list[str]:
    return [
        item
        for row in evidence_rows(spec)
        if len(row) > 2 and is_captured(row) and not reason_after(row[2], "n/a:")
        for item in (part.strip() for part in row[2].split(","))
        if item
    ]


def missing_artefacts(spec: Spec, published: bool) -> list[str]:
    return [
        item
        for item in captured_artefacts(spec)
        if not (ROOT / item).is_file()
        and not (published and Path(item).suffix.lower() in MEDIA_SUFFIXES)
    ]


def evidence_branch(ticket: str) -> str:
    return f"evidence/{ticket}"


def git_run(*args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    if result.returncode != 0:
        raise UsageError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def media_files(ticket: str) -> list[Path]:
    home = evidence_dir(ticket)
    if not home.is_dir():
        return []
    return sorted(
        file for file in home.iterdir() if file.is_file() and file.suffix.lower() in MEDIA_SUFFIXES
    )


def evidence_branch_tip(ticket: str) -> str | None:
    branch = evidence_branch(ticket)
    listed = git_run("ls-remote", "origin", f"refs/heads/{branch}")
    if not listed:
        return None
    tip = listed.split()[0]
    known = subprocess.run(["git", "cat-file", "-e", tip], cwd=ROOT, capture_output=True)
    if known.returncode != 0:
        git_run("fetch", "-q", "origin", f"refs/heads/{branch}")
    return tip


def evidence_tree(ticket: str, files: list[Path]) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(scratch) / "index")}
        for file in files:
            blob = git_run("hash-object", "-w", str(file))
            git_run(
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{blob},{ticket}/{file.name}",
                env=env,
            )
        return git_run("write-tree", env=env)


def publish_evidence(ticket: str) -> str | None:
    files = media_files(ticket)
    if not files:
        return None
    for file in files:
        if file.stat().st_size > MEDIA_MAX_BYTES:
            raise Refused(
                f"{file.relative_to(ROOT).as_posix()} is {file.stat().st_size // (1024 * 1024)} MB, over the "
                f"{MEDIA_MAX_BYTES // (1024 * 1024)} MB limit → record a shorter clip or compress it"
            )
    tree = evidence_tree(ticket, files)
    parent = evidence_branch_tip(ticket)
    identity = {
        "GIT_AUTHOR_NAME": "codeangel",
        "GIT_AUTHOR_EMAIL": "codeangel@users.noreply.github.com",
        "GIT_COMMITTER_NAME": "codeangel",
        "GIT_COMMITTER_EMAIL": "codeangel@users.noreply.github.com",
    }
    parents = ["-p", parent] if parent else []
    commit = git_run(
        "commit-tree",
        tree,
        *parents,
        "-m",
        f"{ticket}: proof media",
        env={**os.environ, **identity},
    )
    git_run("push", "-q", "origin", f"{commit}:refs/heads/{evidence_branch(ticket)}")
    return commit


def media_url(repo: str, sha: str, ticket: str, name: str) -> str:
    return f"https://github.com/{repo}/blob/{sha}/{ticket}/{name}?raw=true"


def media_markdown(path: str, ticket: str, repo: str, sha: str) -> str:
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    video = suffix in VIDEO_SUFFIXES
    if repo and sha:
        url = media_url(repo, sha, ticket, name)
        return f"[▶ {name}]({url})" if video else f"![{name}]({url})"
    if not (ROOT / path).is_file():
        return f"> ⚠ `{name}` is no longer available"
    return f"`{name}` — {'video' if video else 'screenshot'} kept locally, not committed"


def artefact_markdown(path: str) -> str:
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    file = ROOT / path
    if not file.is_file():
        return f"> ⚠ `{name}` is no longer available"
    if suffix not in TEXT_SUFFIXES:
        return f"`{name}` — kept locally, not committed"
    lines = file.read_text(encoding="utf-8", errors="ignore").splitlines()
    shown = "\n".join(lines[:PROOF_MAX_LINES])
    more = (
        f"\n… {len(lines) - PROOF_MAX_LINES} more lines in the local file"
        if len(lines) > PROOF_MAX_LINES
        else ""
    )
    fence = fence_for(shown)
    return f"`{name}`\n{fence}text\n{shown}{more}\n{fence}"


def row_summary(ac: str, title: str, row: list[str]) -> str:
    kind, proof = row[1].lower(), row[2]
    note = f" — {row[3]}" if len(row) > 3 and row[3] else ""
    missing = reason_after(proof, "not captured:")
    if missing is not None:
        return f"- ⚠ **{ac}** — {title} — not captured ({kind}): {missing}"
    na = reason_after(proof, "n/a:")
    if na is not None:
        return f"- ➖ **{ac}** — {title} — n/a: {na}"
    return f"- ✅ **{ac}** — {title}{note}"


def row_excerpts(ac: str, row: list[str]) -> list[str]:
    proof = row[2]
    if reason_after(proof, "not captured:") is not None or reason_after(proof, "n/a:") is not None:
        return []
    return [
        f"**{ac}** {artefact_markdown(item)}"
        for item in (part.strip() for part in proof.split(","))
        if item and Path(item).suffix.lower() not in MEDIA_SUFFIXES
    ]


def row_media(row: list[str], ticket: str, repo: str, sha: str) -> list[str]:
    proof = row[2]
    if reason_after(proof, "not captured:") is not None or reason_after(proof, "n/a:") is not None:
        return []
    return [
        "  " + media_markdown(item, ticket, repo, sha)
        for item in (part.strip() for part in proof.split(","))
        if item and Path(item).suffix.lower() in MEDIA_SUFFIXES
    ]


def short_title(rest: str) -> str:
    title = PROOF_RE.sub("", rest).lstrip(": ").strip()
    title = re.sub(r"^\(implied\)\s*", "", title).replace("`", "").replace("<", "&lt;")
    sentence = re.split(r"(?<=[.!?])\s", title, maxsplit=1)[0]
    if len(sentence) <= PROOF_TITLE_CHARS:
        return sentence
    return sentence[: PROOF_TITLE_CHARS - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def is_captured(row: list[str]) -> bool:
    return len(row) > 2 and not reason_after(row[2], "not captured:")


def render_proof(spec: Spec, repo: str = "", sha: str = "") -> str:
    acs = acceptance_criteria(spec)
    rows = evidence_rows(spec)
    ticket = spec.get("ticket")
    captured = sum(1 for ac in acs if any(r[0] == ac and is_captured(r) for r in rows))
    summary, excerpts = [], []
    for ac, rest in acs.items():
        title = short_title(rest)
        mine = [row for row in rows if row[0] == ac and len(row) > 2]
        if not mine:
            summary.append(f"- ⚠ **{ac}** — {title} — no evidence recorded")
        for row in mine:
            summary.append(row_summary(ac, title, row))
            summary += row_media(row, ticket, repo, sha)
            excerpts += row_excerpts(ac, row)
    where = (
        "screenshots and videos are on the evidence branch"
        if repo and sha
        else "evidence stays local"
    )
    out = [
        PROOF_BEGIN,
        "## Proof",
        f"{captured} of {len(acs)} criteria have captured proof ({where}, not part of this diff).",
        "\n".join(summary),
    ]
    if excerpts:
        body = "\n\n".join(excerpts)
        out.append(f"<details><summary>Output excerpts</summary>\n\n{body}\n\n</details>")
    out.append(PROOF_END)
    return "\n\n".join(out) + "\n"


def splice_proof(body: str, section: str) -> str:
    start, end = body.find(PROOF_BEGIN), body.find(PROOF_END)
    if start != -1 and end > start:
        return body[:start] + section.rstrip("\n") + body[end + len(PROOF_END) :]
    return body.rstrip("\n") + ("\n\n" if body.strip() else "") + section


def cmd_proof(args: argparse.Namespace) -> None:
    _, spec = load(args.ticket)
    if bool(args.repo) != bool(args.sha):
        raise UsageError("--repo and --sha go together")
    section = render_proof(spec, args.repo or "", args.sha or "")
    if not args.into:
        print(section, end="")
        return
    target = Path(args.into)
    body = target.read_text(encoding="utf-8") if target.is_file() else ""
    gone = missing_artefacts(spec, bool(args.repo))
    if gone and PROOF_BEGIN in body:
        print(
            f"{args.ticket}: kept the existing Proof block in {args.into}; artefacts not found here: {', '.join(gone)}"
        )
        return
    target.write_text(splice_proof(body, section), encoding="utf-8", newline="\n")
    print(f"{args.ticket}: proof section written to {args.into}")


def cmd_evidence(args: argparse.Namespace) -> None:
    print(prepare_evidence(args.ticket).relative_to(ROOT).as_posix())


def cmd_publish(args: argparse.Namespace) -> None:
    sha = publish_evidence(args.ticket)
    if sha:
        print(sha)


def cmd_show(args: argparse.Namespace) -> None:
    names = [args.stage] if args.stage else list(MAP["stages"])
    for name in names:
        if name not in MAP["stages"]:
            raise UsageError(f"unknown stage {name!r}; stages: {', '.join(MAP['stages'])}")
        info = MAP["stages"][name]
        print(f"{name} — {info['does']} [owner: {info['owner']}]")
        for item in info.get("entry", []):
            print(f"  entry     {item}")
        for item in info.get("produces", []):
            print(f"  produces  {item}")
        exits = info.get("exits", [])
        if name not in MAP["terminal"]:
            exits = exits + [e for e in MAP["global_exits"] if e["to"] != name]
        for e in exits:
            mode = f" [mode={e['mode']}]" if "mode" in e else ""
            checks = ",".join(e.get("checks", [])) or "-"
            effects = ",".join(e.get("effects", [])) or "-"
            print(
                f"  exit      {e['status']}{mode} → {e['to']}  checks={checks}  effects={effects}"
            )
            print(f"            {e['when']}")
        print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("ticket")
    init.add_argument("--mode", choices=["plan", "immediate"], required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--branch", required=True)
    init.add_argument("--base-sha", required=True)
    init.add_argument("--url", default="none")
    init.add_argument(
        "--source",
        choices=["linear-mcp", "user-paste", "other"],
        default="user-paste",
    )
    init.set_defaults(handler=cmd_init)

    go = commands.add_parser("go")
    go.add_argument("ticket")
    go.add_argument("status")
    go.add_argument("--note", default="")
    go.set_defaults(handler=cmd_go)

    status = commands.add_parser("status")
    status.add_argument("ticket")
    status.set_defaults(handler=cmd_status)

    log = commands.add_parser("log")
    log.add_argument("ticket")
    log.add_argument("text")
    log.set_defaults(handler=cmd_log)

    docs = commands.add_parser("docs")
    docs.add_argument("ticket")
    docs.set_defaults(handler=cmd_docs)

    proof_cmd = commands.add_parser("proof")
    proof_cmd.add_argument("ticket")
    proof_cmd.add_argument("--repo")
    proof_cmd.add_argument("--sha")
    proof_cmd.add_argument("--into")
    proof_cmd.set_defaults(handler=cmd_proof)

    evidence = commands.add_parser("evidence")
    evidence.add_argument("ticket")
    evidence.set_defaults(handler=cmd_evidence)

    publish = commands.add_parser("publish")
    publish.add_argument("ticket")
    publish.set_defaults(handler=cmd_publish)

    show = commands.add_parser("show")
    show.add_argument("stage", nargs="?")
    show.set_defaults(handler=cmd_show)
    return parser


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    try:
        validate_map()
        args.handler(args)
    except Refused as error:
        print(f"REFUSED: {error}")
        return 1
    except UsageError as error:
        print(f"ERROR: {error}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
