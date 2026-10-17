import json
import tomllib
from pathlib import Path, PurePosixPath

from codeangel.install.presets import Preset, PresetCatalog
from codeangel.install.rows import RowInserter
from codeangel.install.tree import PAYLOAD, PayloadTree
from codeangel.io.errors import CodeangelError
from codeangel.io.files import TextFile
from codeangel.io.templating import TemplateRenderer
from codeangel.project.model import Paths, Project


class PresetInstaller:
    ROW_MARKER = "<!-- codeangel:areas"
    CI_MARKER = "<!-- codeangel:ci"
    ADOPT_GUARD = "Loaded for any work under"

    def __init__(self) -> None:
        self._renderer = TemplateRenderer()
        self._rows = RowInserter()
        self._files = TextFile()
        self._catalog = PresetCatalog(PAYLOAD.presets, self._renderer)

    def install(
        self,
        directory: str,
        preset_name: str,
        area_path: str,
        name: str | None,
        overrides: list[str] | None,
    ) -> int:
        project = Project.discover(Path(directory).resolve())
        preset = self._catalog.get(preset_name)
        area = PurePosixPath(area_path.replace("\\", "/").strip("/")).as_posix()
        variables = preset.variables(project.variables() | self._area_vars(area, name), overrides)
        self._require(project.root, preset, area, variables)
        self._adopt(project.root, preset, area, variables)
        created, kept = self._copy(project.root, preset, area, variables)
        self._announce(preset_name, area, created, kept)
        self._doc_map(project, preset, area, variables)
        self._router_rows(project.root, preset, area, variables)
        self._config(project, preset, area, variables, preset_name)
        self._next(preset, variables)
        return 0

    def _area_vars(self, area: str, name: str | None) -> dict[str, str]:
        return {"area": area, "area_name": name or PurePosixPath(area).name}

    def _require(self, root: Path, preset: Preset, area: str, variables: dict[str, str]) -> None:
        missing = [
            filename
            for filename in preset.meta.get("area", {}).get("requires_files", [])
            if not (root / area / filename).exists()
        ]
        if missing:
            detail = preset.field("requires", variables)
            raise CodeangelError(f"{area}/ has no {', '.join(missing)} — {detail}")

    def _adopt(self, root: Path, preset: Preset, area: str, variables: dict[str, str]) -> None:
        for rule in preset.meta.get("area", {}).get("adopt", []):
            self._adopt_one(root, area, variables, rule)

    def _adopt_one(
        self, root: Path, area: str, variables: dict[str, str], rule: dict[str, str]
    ) -> None:
        source, target = root / area / rule["from"], root / area / rule["to"]
        if not source.is_file() or target.exists():
            return
        body = source.read_text(encoding="utf-8")
        if self.ADOPT_GUARD in body:
            return
        title = self._renderer.render(rule["title"], variables, "adopt title")
        when = self._renderer.render(rule["when"], variables, "adopt when")
        self._files.write(target, self._adopted_text(title, when, area, body))
        source.unlink()
        print(f"  adopted {area}/{rule['from']} → {area}/{rule['to']}")

    def _adopted_text(self, title: str, when: str, area: str, body: str) -> str:
        header = (
            f"# {title}\n\n<!-- When: {when}. Adopted unchanged from the area's generator; "
            f"routed to from {area}/AGENTS.md. -->\n\n"
        )
        return header + body.lstrip("\n")

    def _copy(
        self, root: Path, preset: Preset, area: str, variables: dict[str, str]
    ) -> tuple[list[str], list[str]]:
        created: list[str] = []
        kept: list[str] = []
        for rel in preset.tree.files():
            placed = self._place(root, preset, area, variables, rel)
            if placed is None:
                continue
            kind, shown = placed.split(":", 1)
            (created if kind == "created" else kept).append(shown)
        return created, kept

    def _place(
        self, root: Path, preset: Preset, area: str, variables: dict[str, str], rel: PurePosixPath
    ) -> str | None:
        if len(rel.parts) == 1 and rel.name.startswith("_"):
            return None
        base, sub = self._base(root, area, rel)
        rendered = self._renderer.render(
            PayloadTree.install_path(sub).as_posix(), variables, rel.as_posix()
        )
        dest = base / rendered
        shown = dest.relative_to(root).as_posix()
        if dest.exists():
            return f"kept:{shown}"
        text = self._renderer.render(preset.tree.read(rel), variables, rel.as_posix())
        self._files.write(dest, text)
        return f"created:{shown}"

    def _base(self, root: Path, area: str, rel: PurePosixPath) -> tuple[Path, PurePosixPath]:
        if rel.parts[0] == "_root":
            return root, PurePosixPath(*rel.parts[1:])
        return root / area, rel

    def _announce(self, preset_name: str, area: str, created: list[str], kept: list[str]) -> None:
        print(f"preset {preset_name} → {area}/  (files created: {len(created)}, kept: {len(kept)})")
        if kept:
            print(f"  kept (already existed, not overwritten): {', '.join(kept)}")

    def _doc_map(
        self, project: Project, preset: Preset, area: str, variables: dict[str, str]
    ) -> None:
        doc_map = project.root / project.config.get("project", {}).get(
            "doc_map", "docs/ai/doc-map.toml"
        )
        fragment = preset.directory / "_doc-map.toml"
        if not fragment.is_file() or not doc_map.is_file():
            return
        text = doc_map.read_text(encoding="utf-8")
        tag = f"# codeangel:preset {preset.name} {area}"
        if tag in text:
            print(f"  kept {doc_map.name}: rules for {area}/ present")
            return
        rules = self._renderer.render(
            fragment.read_text(encoding="utf-8"), variables, "_doc-map.toml"
        )
        updated = text.rstrip("\n") + f"\n\n{tag}{rules}"
        tomllib.loads(updated)
        if not updated.endswith("\n"):
            updated += "\n"
        self._files.write(doc_map, updated)
        print(f"  rules added to {doc_map.name}")

    def _router_rows(
        self, root: Path, preset: Preset, area: str, variables: dict[str, str]
    ) -> None:
        for rel, row in self._row_table(root, preset, area, variables).items():
            print(f"  {self._rows.insert(root, rel, row, self.ROW_MARKER)}")
        if preset.meta.get("ci"):
            inserted = self._rows.insert(
                root, "docs/ai/git-workflow.md", preset.field("ci", variables), self.CI_MARKER
            )
            print(f"  {inserted}")

    def _row_table(
        self, root: Path, preset: Preset, area: str, variables: dict[str, str]
    ) -> dict[str, str]:
        name = variables["area_name"]
        summary = preset.field("summary", variables)
        rows = {
            "AGENTS.md": f"| {name} | `{area}/` | `{area}/AGENTS.md` |",
            "docs/ai/repo-map.md": f"| `{area}/` | {summary} | `{area}/AGENTS.md` |",
            "README.md": f"| `{area}/` | {summary} | {preset.field('quick_start', variables)} |",
        }
        learnings = root / area / "docs/learnings/README.md"
        if learnings.is_file():
            rows["docs/learnings/README.md"] = (
                f"| `{area}/docs/learnings/README.md` | {name} gotchas (index) |"
            )
        return rows

    def _config(
        self,
        project: Project,
        preset: Preset,
        area: str,
        variables: dict[str, str],
        preset_name: str,
    ) -> None:
        if any(entry.get("path") == area for entry in project.config.get("areas", [])):
            print(f"  kept {Paths.CONFIG}: area {area} present")
            return
        commands = [
            self._renderer.render(command, variables, "pre_remove")
            for command in preset.meta.get("area", {}).get("pre_remove", [])
        ]
        rendered = ", ".join(json.dumps(command) for command in commands)
        name = variables["area_name"]
        block = (
            f'\n[[areas]]\nname = "{name}"\npath = "{area}"\npreset = "{preset_name}"\n'
            f"pre_remove = [{rendered}]\n"
        )
        path = project.root / Paths.CONFIG
        text = path.read_text(encoding="utf-8").rstrip("\n") + "\n" + block
        tomllib.loads(text)
        self._files.write(path, text)
        print(f"  area added to {Paths.CONFIG}")

    def _next(self, preset: Preset, variables: dict[str, str]) -> None:
        if preset.meta.get("next"):
            print(f"next: {preset.field('next', variables)}")
