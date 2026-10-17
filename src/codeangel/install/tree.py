from pathlib import Path, PurePosixPath


class PayloadTree:
    def __init__(self, base: Path) -> None:
        self.base = base

    def files(self) -> list[PurePosixPath]:
        return sorted(
            PurePosixPath(path.relative_to(self.base).as_posix())
            for path in self.base.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )

    def read(self, rel: PurePosixPath) -> str:
        return (self.base / rel).read_text(encoding="utf-8")

    @staticmethod
    def install_path(rel: PurePosixPath) -> PurePosixPath:
        return PurePosixPath(
            *(f".{part[4:]}" if part.startswith("dot_") else part for part in rel.parts)
        )


class Payload:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1] / "payload"
        self.managed = PayloadTree(self.root / "managed")
        self.scaffold = PayloadTree(self.root / "scaffold")
        self.presets = self.root / "presets"


PAYLOAD = Payload()
