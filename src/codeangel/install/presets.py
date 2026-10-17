import tomllib
from pathlib import Path

from codeangel.install.tree import PayloadTree
from codeangel.io.errors import CodeangelError
from codeangel.io.templating import TemplateRenderer


class Preset:
    def __init__(self, directory: Path, renderer: TemplateRenderer) -> None:
        self.directory = directory
        self.name = directory.name
        self.meta = tomllib.loads((directory / "_preset.toml").read_text(encoding="utf-8"))
        self.tree = PayloadTree(directory)
        self._renderer = renderer

    def field(self, key: str, variables: dict[str, str]) -> str:
        return self._renderer.render(
            self.meta.get(key, ""), variables, f"{self.name}/_preset.toml {key}"
        )

    def variables(self, base: dict[str, str], overrides: list[str] | None) -> dict[str, str]:
        variables = dict(base)
        for key, value in self.meta.get("vars", {}).items():
            variables[key] = self._renderer.render(value, variables, f"{self.name}/_preset.toml")
        for override in overrides or []:
            self._apply(variables, override)
        return variables

    def _apply(self, variables: dict[str, str], override: str) -> None:
        key, sep, value = override.partition("=")
        if not sep:
            raise CodeangelError(f"--var {override!r}: expected key=value")
        variables[key] = value


class PresetCatalog:
    def __init__(self, root: Path, renderer: TemplateRenderer | None = None) -> None:
        self.root = root
        self._renderer = renderer or TemplateRenderer()

    def get(self, name: str) -> Preset:
        directory = self.root / name
        if not (directory / "_preset.toml").is_file():
            raise CodeangelError(f"unknown preset {name!r} — see `codeangel presets`")
        return Preset(directory, self._renderer)

    def listed(self) -> list[Preset]:
        found = [path for path in self.root.iterdir() if (path / "_preset.toml").is_file()]
        return [Preset(path, self._renderer) for path in sorted(found)]
