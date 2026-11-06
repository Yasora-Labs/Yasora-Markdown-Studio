"""Build on the TARGET OS; PyInstaller does not cross-compile."""
from __future__ import annotations
import os
import sys
from pathlib import Path
import PyInstaller.__main__

root = Path(__file__).resolve().parents[1]
icon = root / "src" / "yasora_studio" / "assets" / ("studio.ico" if sys.platform == "win32" else "studio.icns")
args = [
    str(root / "run_studio.py"), "--noconfirm", "--clean", "--onedir", "--windowed",
    "--name", "YasoraMarkdownStudio", "--paths", str(root / "src"),
    "--distpath", str(root / "dist"), "--workpath", str(root / "build"),
    "--specpath", str(root / "build"),
    "--add-data", str(root / "src/yasora_studio/assets") + os.pathsep + "yasora_studio/assets",
    "--collect-all", "markitdown", "--copy-metadata", "markitdown",
    "--collect-all", "magika", "--collect-all", "onnxruntime",
    "--collect-all", "pdfplumber", "--collect-all", "pandas",
    "--collect-all", "numpy", "--collect-all", "mammoth",
    "--collect-all", "pptx", "--collect-all", "openpyxl",
    "--collect-all", "azure.ai", "--collect-all", "azure.identity",
    "--collect-submodules", "win32com" if sys.platform == "win32" else "lxml",
]
if sys.platform in {"win32", "darwin"}:
    if not icon.is_file():
        raise SystemExit(f"Missing app icon {icon}")
    args += ["--icon", str(icon)]
PyInstaller.__main__.run(args)
