"""MarkItDown-powered local file converter (not a reimplementation of Microsoft code)."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Callable
import uuid


def convert_one(source: Path, destination: Path, *, overwrite: bool = False, factory: Callable | None = None) -> str:
    """Convert one local file safely and atomically; return 'converted' or 'skipped'."""
    source, destination = Path(source), Path(destination)
    if not source.is_file() or source.is_symlink():
        raise ValueError(f"Not a regular local file: {source}")
    if source.resolve() == destination.resolve(strict=False):
        raise ValueError("Source and output must be different")
    if destination.exists() and not overwrite:
        return "skipped"
    if factory is None:
        from markitdown import MarkItDown
        factory = MarkItDown
    engine = factory()
    # convert_local avoids accepting remote URLs from the user-facing app.
    result = engine.convert_local(str(source))
    markdown = result.markdown
    if not isinstance(markdown, str):
        raise TypeError("The conversion engine returned no Markdown string")
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_name("." + destination.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(markdown)
            handle.flush()
            os.fsync(handle.fileno())
        if destination.exists() and not overwrite:
            return "skipped"
        os.replace(tmp, destination)
        return "converted"
    finally:
        if tmp.exists():
            tmp.unlink()
