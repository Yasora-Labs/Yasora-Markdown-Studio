"""Path selection, recursive file discovery and output collision avoidance."""
from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Iterable

SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".xls", ".html", ".htm", ".csv", ".json", ".xml", ".txt", ".md", ".msg", ".epub", ".jpg", ".jpeg", ".png", ".wav", ".mp3", ".zip"}


def default_output() -> Path:
    # Do not use the redirected Desktop or system-wide installer directories.
    home = Path.home()
    if sys.platform == "win32":
        documents = Path(os.environ.get("USERPROFILE", str(home))) / "Documents"
    else:
        documents = home / "Documents"
        if sys.platform.startswith("linux"):
            user_dirs = home / ".config" / "user-dirs.dirs"
            if user_dirs.is_file():
                try:
                    import re
                    m = re.search(r'^XDG_DOCUMENTS_DIR="([^"\n]+)"', user_dirs.read_text(encoding="utf-8"), re.M)
                    if m:
                        candidate = m.group(1).replace("$HOME", str(home))
                        documents = Path(candidate)
                except OSError:
                    pass
    return documents / "Yasora Markdown Studio"


def source_items(paths: Iterable[Path], output: Path) -> list[tuple[Path, Path]]:
    """Return (input file, relative output path) without following symlinked dirs/files.

    The source filename's original extension is retained, e.g. `report.pdf.md`.
    This prevents PDF/DOCX name collisions. Duplicate inputs are removed.
    """
    out = output.resolve(strict=False)
    seen: set[str] = set()
    results: list[tuple[Path, Path]] = []
    for source in paths:
        path = Path(source).expanduser().absolute()
        if path.is_symlink() or not path.exists():
            continue
        if path.is_file():
            candidates = [(path, Path(path.name + ".md"))]
        elif path.is_dir():
            candidates = []
            for root, dirs, filenames in os.walk(path, followlinks=False):
                root_p = Path(root)
                dirs[:] = [d for d in dirs if not (root_p / d).is_symlink() and (root_p / d).resolve(strict=False) != out and out not in (root_p / d).resolve(strict=False).parents]
                for filename in sorted(filenames):
                    file = root_p / filename
                    if file.is_symlink():
                        continue
                    rel = file.relative_to(path)
                    candidates.append((file, Path(path.name) / rel.parent / (rel.name + ".md")))
        else:
            continue
        for file, rel in candidates:
            if file.suffix.lower() not in SUPPORTED:
                continue
            # Prevent recursive conversion of Markdown outputs when output resides inside source.
            resolved = file.resolve(strict=False)
            if resolved == out or out in resolved.parents:
                continue
            key = os.path.normcase(str(resolved))
            if key in seen:
                continue
            seen.add(key)
            results.append((file, rel))
    # Explicitly selected duplicate basenames are isolated in flat mode via suffix.
    used: set[str] = set()
    normalized: list[tuple[Path, Path]] = []
    for src, rel in results:
        original = rel
        index = 2
        while os.path.normcase(str(rel)) in used:
            rel = original.with_name(f"{original.stem}-{index}{original.suffix}")
            index += 1
        used.add(os.path.normcase(str(rel)))
        normalized.append((src, rel))
    return normalized
