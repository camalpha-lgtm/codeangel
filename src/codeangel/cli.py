"""codeangel — install and maintain an agent-agnostic AI software factory in any repo.

  codeangel init    [--name N] [--base-branch B] [--python CMD] [--force]
  codeangel add     <preset> <area-path> [--name N] [--var key=value ...]
  codeangel update  [--force]
  codeangel sync    [--check]
  codeangel doctor
  codeangel presets
  codeangel version

Global: -C <dir> runs as if started in <dir>. Exit codes: 0 ok, 1 problems found, 2 usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

from codeangel import __version__

PAYLOAD = Path(__file__).resolve().parent / "payload"
MANAGED = PAYLOAD / "managed"
SCAFFOLD = PAYLOAD / "scaffold"
PRESETS = PAYLOAD / "presets"
CONFIG = ".agents/codeangel.toml"
LOCK = ".agents/codeangel.lock.json"
SYNC = ".agents/sync-shims.py"
TRANSITION = ".agents/skills/build-loop/scripts/transition.py"
ROW_MARKER = "<!-- codeangel:areas"
CI_MARKER = "<!-- codeangel:ci"
DOC_MAP_MARKER = "# codeangel:areas"
NEW_SUFFIX = ".codeangel-new"
VAR_RE = re.compile(r"\{\{([a-z_]+)\}\}")
PATH_RE = re.compile(r"`((?:\.?[\w-]+/)+[\w.-]+\.(?:md|toml|py|ya?ml|json))`")
AGENTS_MD_BUDGET = 50


class CodeangelError(Exception):
    pass


# ── payload helpers ───────────────────────────────────────────────────────────


def target_path(rel: PurePosixPath) -> PurePosixPath:
    """`dot_x` → `.x`: setuptools can't ship dot-directories as package data."""
    return PurePosixPath(
        *(f".{part[4:]}" if part.startswith("dot_") else part for part in rel.parts)
    )


def payload_files(base: Path) -> list[PurePosixPath]:
    return sorted(
        PurePosixPath(path.relative_to(base).as_posix())
        for path in base.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )


def render(text: str, variables: dict[str, str], where: str) -> str:
    def substitute(match: re.Match[str]) -> str:
        if match[1] not in variables:
            raise CodeangelError(f"{where}: no value for {{{{{match[1]}}}}}")
        return variables[match[1]]

    return VAR_RE.sub(substitute, text)


def digest(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def package_name(name: str) -> str:
    package = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "project"
    return f"p_{package}" if package[0].isdigit() else package


def python_ok(command: str) -> bool:
    check = '-c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"'
    try:
        result = subprocess.run(f"{command} {check}", shell=True, capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def detect_python() -> str:
    candidates = ["py -3.13", "py -3.12", "py -3.11"] if os.name == "nt" else []
    for command in candidates + ["python3", "python"]:
        if python_ok(command):
            return command
    return f'"{sys.executable}"' if " " in sys.executable else sys.executable


# ── project state ─────────────────────────────────────────────────────────────


def find_root(start: Path) -> Path:
    for directory in [start, *start.parents]:
        if (directory / CONFIG).is_file():
            return directory
    raise CodeangelError(f"no {CONFIG} in {start} or its parents — run `codeangel init` first")


def load_config(root: Path) -> dict[str, Any]:
    try:
        return tomllib.loads((root / CONFIG).read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise CodeangelError(f"{CONFIG}: {error}") from error


def load_lock(root: Path) -> dict[str, str]:
    path = root / LOCK
    return json.loads(path.read_text(encoding="utf-8"))["files"] if path.is_file() else {}


def save_lock(root: Path, files: dict[str, str]) -> None:
    data = {"codeangel": __version__, "files": dict(sorted(files.items()))}
    write(root / LOCK, json.dumps(data, indent=2) + "\n")


def project_vars(config: dict[str, Any]) -> dict[str, str]:
    project = config.get("project", {})
    name = project.get("name", "project")
    return {
        "project_name": name,
        "project_package": package_name(name),
        "base_branch": project.get("base_branch", "main"),
        "python": config.get("runtime", {}).get("python", "python3"),
        "python_toml": json.dumps(config.get("runtime", {}).get("python", "python3")),
        "codeangel_version": __version__,
    }


def install_managed(
    dest: Path, text: str, locked: str | None, force: bool
) -> tuple[str, str | None]:
    """→ (status, hash to lock). Never overwrites a locally modified file unless forced."""
    new = digest(text.encode("utf-8"))
    if not dest.exists():
        write(dest, text)
        return "created", new
    current = digest(dest.read_bytes())
    if current == new:
        return "unchanged", new
    if force or current == locked:
        write(dest, text)
        return "updated", new
    write(dest.with_name(dest.name + NEW_SUFFIX), text)
    return "conflict", locked


def sync_shims(root: Path, check: bool) -> int:
    command = [sys.executable, str(root / SYNC)] + (["--check"] if check else [])
    return subprocess.run(command, cwd=root).returncode


def insert_row(root: Path, rel: str, row: str, marker: str = ROW_MARKER) -> str:
    path = root / rel
    if not path.is_file():
        return f"skipped {rel}: missing"
    text = path.read_text(encoding="utf-8")
    if row in text:
        return f"kept {rel}: row present"
    lines = text.splitlines(keepends=True)
    index = next((i for i, line in enumerate(lines) if line.startswith(marker)), None)
    if index is None:
        return f"MANUAL {rel}: no `{marker}` marker — add: {row}"
    lines.insert(index, row + "\n")
    write(path, "".join(lines))
    return f"row added to {rel}"


# ── commands ──────────────────────────────────────────────────────────────────


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.directory).resolve()
    if (root / CONFIG).exists() and not args.force:
        raise CodeangelError(f"{root} is already initialised — use `codeangel update`")
    python = args.python or detect_python()
    variables = {
        "project_name": args.name or root.name,
        "project_package": package_name(args.name or root.name),
        "base_branch": args.base_branch,
        "python": python,
        "python_toml": json.dumps(python),  # valid TOML basic string (escapes Windows backslashes)
        "codeangel_version": __version__,
    }
    counts: dict[str, int] = {}
    lock: dict[str, str] = {}
    for rel in payload_files(MANAGED):
        dest_rel = target_path(rel).as_posix()
        status, locked = install_managed(
            root / dest_rel, (MANAGED / rel).read_text(encoding="utf-8"), None, args.force
        )
        counts[f"managed {status}"] = counts.get(f"managed {status}", 0) + 1
        if locked:
            lock[dest_rel] = locked
        if status == "conflict":
            print(
                f"  conflict  {dest_rel} exists and differs → new version at {dest_rel}{NEW_SUFFIX}"
            )
    for rel in payload_files(SCAFFOLD):
        dest_rel = render(target_path(rel).as_posix(), variables, rel.as_posix())
        dest = root / dest_rel
        if dest.exists():
            counts["scaffold kept"] = counts.get("scaffold kept", 0) + 1
            continue
        write(dest, render((SCAFFOLD / rel).read_text(encoding="utf-8"), variables, rel.as_posix()))
        counts["scaffold created"] = counts.get("scaffold created", 0) + 1
    save_lock(root, lock)
    load_config(root)  # fail now, not later, if the generated config is not valid TOML
    print(f"codeangel {__version__} → {root}  (runtime python: {python})")
    print("  " + " · ".join(f"{key}: {value}" for key, value in sorted(counts.items())))
    code = sync_shims(root, check=False)
    print(
        "next: fill the TODOs in AGENTS.md + docs/ai/product.md · add areas: `codeangel add"
        " <preset> <path>` (list: `codeangel presets`) · then `codeangel doctor`"
    )
    return code


def cmd_add(args: argparse.Namespace) -> int:
    root = find_root(Path(args.directory).resolve())
    config = load_config(root)
    preset_dir = PRESETS / args.preset
    if not (preset_dir / "_preset.toml").is_file():
        raise CodeangelError(f"unknown preset {args.preset!r} — see `codeangel presets`")
    area = PurePosixPath(args.path.replace("\\", "/").strip("/")).as_posix()
    variables = project_vars(config) | {
        "area": area,
        "area_name": args.name or PurePosixPath(area).name,
    }
    meta = tomllib.loads((preset_dir / "_preset.toml").read_text(encoding="utf-8"))
    for key, value in meta.get("vars", {}).items():
        variables[key] = render(value, variables, f"{args.preset}/_preset.toml")
    for override in args.var or []:
        key, sep, value = override.partition("=")
        if not sep:
            raise CodeangelError(f"--var {override!r}: expected key=value")
        variables[key] = value

    def field(key: str) -> str:
        return render(meta.get(key, ""), variables, f"{args.preset}/_preset.toml {key}")

    missing = [
        name
        for name in meta.get("area", {}).get("requires_files", [])
        if not (root / area / name).exists()
    ]
    if missing:
        raise CodeangelError(f"{area}/ has no {', '.join(missing)} — {field('requires')}")

    created: list[str] = []
    kept: list[str] = []
    for rel in payload_files(preset_dir):
        if len(rel.parts) == 1 and rel.name.startswith("_"):
            continue
        # `_root/…` files land at the repo root (e.g. CI workflows); everything else inside the area.
        base, sub = (
            (root, PurePosixPath(*rel.parts[1:])) if rel.parts[0] == "_root" else (root / area, rel)
        )
        dest = base / render(target_path(sub).as_posix(), variables, rel.as_posix())
        shown = dest.relative_to(root).as_posix()
        if dest.exists():
            kept.append(shown)
            continue
        write(
            dest, render((preset_dir / rel).read_text(encoding="utf-8"), variables, rel.as_posix())
        )
        created.append(shown)
    print(f"preset {args.preset} → {area}/  (files created: {len(created)}, kept: {len(kept)})")
    if kept:
        print(f"  kept (already existed, not overwritten): {', '.join(kept)}")

    doc_map = root / config.get("project", {}).get("doc_map", "docs/ai/doc-map.toml")
    tag = f"# codeangel:preset {args.preset} {area}"
    fragment = preset_dir / "_doc-map.toml"
    if fragment.is_file() and doc_map.is_file():
        text = doc_map.read_text(encoding="utf-8")
        if tag in text:
            print(f"  kept {doc_map.name}: rules for {area}/ present")
        else:
            rules = render(fragment.read_text(encoding="utf-8"), variables, "_doc-map.toml")
            updated = text.rstrip("\n") + f"\n\n{tag}{rules}"
            tomllib.loads(updated)
            write(doc_map, updated if updated.endswith("\n") else updated + "\n")
            print(f"  rules added to {doc_map.name}")

    name = variables["area_name"]
    rows = {
        "AGENTS.md": f"| {name} | `{area}/` | `{area}/AGENTS.md` |",
        "docs/ai/repo-map.md": f"| `{area}/` | {field('summary')} | `{area}/AGENTS.md` |",
        "README.md": f"| `{area}/` | {field('summary')} | {field('quick_start')} |",
    }
    if (root / area / "docs/learnings/README.md").is_file():
        rows["docs/learnings/README.md"] = (
            f"| `{area}/docs/learnings/README.md` | {name} gotchas (index) |"
        )
    for rel, row in rows.items():
        print(f"  {insert_row(root, rel, row)}")
    if meta.get("ci"):
        print(f"  {insert_row(root, 'docs/ai/git-workflow.md', field('ci'), CI_MARKER)}")

    if any(entry.get("path") == area for entry in config.get("areas", [])):
        print(f"  kept {CONFIG}: area {area} present")
    else:
        pre_remove = [
            render(c, variables, "pre_remove") for c in meta.get("area", {}).get("pre_remove", [])
        ]
        block = (
            f'\n[[areas]]\nname = "{name}"\npath = "{area}"\npreset = "{args.preset}"\n'
            f"pre_remove = [{', '.join(json.dumps(c) for c in pre_remove)}]\n"
        )
        text = (root / CONFIG).read_text(encoding="utf-8").rstrip("\n") + "\n" + block
        tomllib.loads(text)
        write(root / CONFIG, text)
        print(f"  area added to {CONFIG}")
    if meta.get("next"):
        print(f"next: {field('next')}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    root = find_root(Path(args.directory).resolve())
    old = load_lock(root)
    new: dict[str, str] = {}
    shipped = set()
    for rel in payload_files(MANAGED):
        dest_rel = target_path(rel).as_posix()
        shipped.add(dest_rel)
        status, locked = install_managed(
            root / dest_rel,
            (MANAGED / rel).read_text(encoding="utf-8"),
            old.get(dest_rel),
            args.force,
        )
        if locked:
            new[dest_rel] = locked
        if status in ("updated", "unchanged"):
            (root / dest_rel).with_name(Path(dest_rel).name + NEW_SUFFIX).unlink(missing_ok=True)
        if status != "unchanged":
            hint = (
                f" (yours kept; new version → {dest_rel}{NEW_SUFFIX})"
                if status == "conflict"
                else ""
            )
            print(f"  {status:<9} {dest_rel}{hint}")
    for dest_rel, locked in old.items():
        dest = root / dest_rel
        if dest_rel in shipped or not dest.exists():
            continue
        if digest(dest.read_bytes()) == locked:
            dest.unlink()
            print(f"  removed   {dest_rel} (no longer shipped)")
        else:
            print(f"  orphaned  {dest_rel} (no longer shipped, locally modified — left in place)")
    save_lock(root, new)
    config_path = root / CONFIG
    text = config_path.read_text(encoding="utf-8")
    write(
        config_path,
        re.sub(r'(?m)^(version\s*=\s*)"[^"]*"', rf'\g<1>"{__version__}"', text, count=1),
    )
    print(f"codeangel {__version__}: managed files up to date")
    return sync_shims(root, check=False)


def cmd_sync(args: argparse.Namespace) -> int:
    return sync_shims(find_root(Path(args.directory).resolve()), check=args.check)


def cmd_doctor(args: argparse.Namespace) -> int:
    root = find_root(Path(args.directory).resolve())
    config = load_config(root)
    results: list[tuple[str, str]] = []

    def report(level: str, message: str) -> None:
        results.append((level, message))

    installed = config.get("codeangel", {}).get("version")
    if installed != __version__:
        report(
            "warn", f"project at codeangel {installed}, CLI is {__version__} → `codeangel update`"
        )
    python = config.get("runtime", {}).get("python", "")
    if python_ok(python):
        report("ok", f"runtime python `{python}` is >= 3.11")
    else:
        report(
            "FAIL",
            f"runtime python `{python}` missing or < 3.11 → fix [runtime] python in {CONFIG}",
        )
    lock = load_lock(root)
    if not lock:
        report("FAIL", f"{LOCK} missing or empty → `codeangel update`")
    for dest_rel, locked in lock.items():
        dest = root / dest_rel
        if not dest.exists():
            report("FAIL", f"managed file missing: {dest_rel} → `codeangel update`")
        elif digest(dest.read_bytes()) != locked:
            report("warn", f"managed file edited locally: {dest_rel} (update won't overwrite it)")
    for stray in root.rglob(f"*{NEW_SUFFIX}"):
        report("warn", f"unmerged update: {stray.relative_to(root).as_posix()}")
    shims = subprocess.run(
        [sys.executable, str(root / SYNC), "--check"], cwd=root, capture_output=True
    )
    report(
        "ok" if shims.returncode == 0 else "FAIL",
        "Claude skill shims in sync"
        if shims.returncode == 0
        else "Claude skill shims out of sync or skill invalid → `codeangel sync`",
    )
    if python_ok(python):
        machine = subprocess.run(
            f'{python} "{root / TRANSITION}" show', shell=True, capture_output=True
        )
        report(
            "ok" if machine.returncode == 0 else "FAIL",
            "build-loop state machine valid"
            if machine.returncode == 0
            else "build-loop state machine invalid → run transition.py show",
        )
    doc_map = root / config.get("project", {}).get("doc_map", "docs/ai/doc-map.toml")
    try:
        rules = tomllib.loads(doc_map.read_text(encoding="utf-8")).get("rule", [])
        missing = sorted(
            {doc for rule in rules for doc in rule["docs"] if not (root / doc).exists()}
        )
        report(
            "FAIL" if missing else "ok",
            f"doc map names missing docs: {', '.join(missing)}"
            if missing
            else f"doc map: {len(rules)} rules",
        )
    except (OSError, tomllib.TOMLDecodeError, KeyError) as error:
        report("FAIL", f"doc map unreadable: {error}")
    agents_files = [root / "AGENTS.md"]
    for entry in config.get("areas", []):
        area_agents = root / entry["path"] / "AGENTS.md"
        if area_agents.is_file():
            agents_files.append(area_agents)
        else:
            report("FAIL", f"area {entry['path']}: no AGENTS.md")
    docs = agents_files + sorted((root / "docs/ai").glob("*.md"))
    for entry in config.get("areas", []):
        docs += sorted((root / entry["path"] / "docs/ai").glob("*.md"))
    for path in agents_files:
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > AGENTS_MD_BUDGET:
            report(
                "warn", f"{path.relative_to(root).as_posix()}: {lines} lines > {AGENTS_MD_BUDGET}"
            )
    for path in docs:
        if not path.is_file():
            continue
        for ref in PATH_RE.findall(path.read_text(encoding="utf-8")):
            # Only repo-relative references: the first segment must exist at the repo root.
            if (root / ref.split("/")[0]).exists() and not (root / ref).exists():
                report("warn", f"{path.relative_to(root).as_posix()} → missing {ref}")
    for level, message in results:
        print(f"[{level}] {message}")
    failed = sum(level == "FAIL" for level, _ in results)
    print(f"doctor: {failed} problem(s), {sum(level == 'warn' for level, _ in results)} warning(s)")
    return 1 if failed else 0


def cmd_presets(args: argparse.Namespace) -> int:
    for preset in sorted(p for p in PRESETS.iterdir() if (p / "_preset.toml").is_file()):
        meta = tomllib.loads((preset / "_preset.toml").read_text(encoding="utf-8"))
        print(f"{preset.name:<14} {meta.get('description', '')}")
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    print(f"codeangel {__version__}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        prog="codeangel", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-C", dest="directory", default=".", help="run as if started in this dir")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="install codeangel into a repo")
    init.add_argument("--name", help="project name (default: directory name)")
    init.add_argument("--base-branch", default="main")
    init.add_argument(
        "--python", help="Python >= 3.11 command for .agents scripts (default: detect)"
    )
    init.add_argument("--force", action="store_true", help="overwrite differing managed files")
    init.set_defaults(handler=cmd_init)

    add = commands.add_parser("add", help="add an area from a preset")
    add.add_argument("preset")
    add.add_argument("path", help="area directory, repo-relative (e.g. backend)")
    add.add_argument("--name", help="area name (default: last path segment)")
    add.add_argument("--var", action="append", help="template variable override key=value")
    add.set_defaults(handler=cmd_add)

    update = commands.add_parser("update", help="refresh managed files; never clobbers local edits")
    update.add_argument(
        "--force", action="store_true", help="overwrite locally edited managed files"
    )
    update.set_defaults(handler=cmd_update)

    sync = commands.add_parser("sync", help="regenerate Claude Code skill shims")
    sync.add_argument("--check", action="store_true", help="report drift, change nothing")
    sync.set_defaults(handler=cmd_sync)

    for name, handler, text in [
        ("doctor", cmd_doctor, "validate the whole setup"),
        ("presets", cmd_presets, "list area presets"),
        ("version", cmd_version, "print the version"),
    ]:
        commands.add_parser(name, help=text).set_defaults(handler=handler)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except CodeangelError as error:
        print(f"error: {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
