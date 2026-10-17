from pathlib import Path

from codeangel.io.files import ContentDigest, TextFile


class ManagedInstaller:
    NEW_SUFFIX = ".codeangel-new"

    def __init__(self) -> None:
        self._digest = ContentDigest()
        self._files = TextFile()

    def install(
        self, dest: Path, text: str, locked: str | None, force: bool
    ) -> tuple[str, str | None]:
        new = self._digest.hexdigest(text.encode("utf-8"))
        if not dest.exists():
            self._files.write(dest, text)
            return "created", new
        return self._existing(dest, text, new, locked, force)

    def _existing(
        self, dest: Path, text: str, new: str, locked: str | None, force: bool
    ) -> tuple[str, str | None]:
        current = self._digest.hexdigest(dest.read_bytes())
        if current == new:
            return "unchanged", new
        if force or current == locked:
            self._files.write(dest, text)
            return "updated", new
        self._files.write(dest.with_name(dest.name + self.NEW_SUFFIX), text)
        return "conflict", locked
