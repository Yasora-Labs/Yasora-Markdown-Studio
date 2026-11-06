"""Compare pinned engine and latest stable PyPI without modifying artifacts."""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

root = Path(__file__).resolve().parents[1]
pin = re.search(r"markitdown\[all\]==([\d.]+)", (root / "requirements-desktop.txt").read_text())
if not pin:
    raise SystemExit("Missing pinned engine version")
installed = pin.group(1)
req = Request("https://pypi.org/pypi/markitdown/json", headers={"User-Agent": "YasoraStudio-EngineWatch/1.0"})
with urlopen(req, timeout=15) as response:
    latest = json.load(response)["info"]["version"]
def triple(s):
    return tuple(int(x) for x in s.split(".") if x.isdigit())
print(f"PINNED={installed}")
print(f"LATEST={latest}")
if triple(latest) > triple(installed):
    print(f"ENGINE_UPDATE_AVAILABLE={latest}")
