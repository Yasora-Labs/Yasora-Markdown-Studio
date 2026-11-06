"""Read-only update checks. Frozen binaries must be replaced by signed app releases.

Never pip-install into a frozen application's bundled runtime. New MarkItDown
versions are incorporated by rebuilding, testing and releasing the full app.
"""
from __future__ import annotations
import importlib.metadata
import json
import re
from urllib.request import Request, urlopen
from . import VERSION

RELEASES = "https://github.com/Yasora-Labs/Yasora-Markdown-Studio/releases"
ENGINE_UPSTREAM = "https://pypi.org/project/markitdown/"


def installed_engine_version() -> str:
    try:
        return importlib.metadata.version("markitdown")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def latest_versions(timeout: float = 7) -> dict[str, str]:
    urls = {
        "engine_latest": "https://pypi.org/pypi/markitdown/json",
        "app_latest": "https://api.github.com/repos/Yasora-Labs/Yasora-Markdown-Studio/releases/latest",
    }
    result = {"app_installed": VERSION, "engine_installed": installed_engine_version(), "engine_latest": "unavailable", "app_latest": "unavailable"}
    for key, url in urls.items():
        try:
            req = Request(url, headers={"User-Agent": "Yasora-Markdown-Studio/0.4 (+https://github.com/Yasora-Labs/Yasora-Markdown-Studio)", "Accept": "application/json"})
            with urlopen(req, timeout=timeout) as response:
                data = json.load(response)
            candidate = data["info"]["version"] if key == "engine_latest" else data["tag_name"].lstrip("v")
            if isinstance(candidate, str) and re.fullmatch(r"[0-9A-Za-z.+_\-]{1,50}", candidate):
                result[key] = candidate
        except Exception:
            # Offline machines and not-yet-created GitHub repositories are normal.
            continue
    return result
