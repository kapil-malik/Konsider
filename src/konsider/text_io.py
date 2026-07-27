"""Platform-independent UTF-8 text output helpers."""

from __future__ import annotations

from pathlib import Path


def write_text_lf(path: Path, value: str) -> None:
    """Write final UTF-8 bytes without operating-system newline translation."""

    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(value)
