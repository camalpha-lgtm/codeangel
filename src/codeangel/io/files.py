import hashlib
from pathlib import Path


class ContentDigest:
    def hexdigest(self, data: bytes) -> str:
        return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


class TextFile:
    def write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
