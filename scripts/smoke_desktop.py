"""Verify the FROZEN executable contains working format-specific converters."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
if sys.platform == "darwin":
    binary = root / "dist/YasoraMarkdownStudio.app/Contents/MacOS/YasoraMarkdownStudio"
elif os.name == "nt":
    binary = root / "dist/YasoraMarkdownStudio/YasoraMarkdownStudio.exe"
else:
    binary = root / "dist/YasoraMarkdownStudio/YasoraMarkdownStudio"
if not binary.is_file():
    raise RuntimeError(f"Frozen executable was not built: {binary}")


def test_one(source: Path, token: str) -> None:
    target = source.with_name(source.name + ".md")
    run = subprocess.run([str(binary), "--smoke-test", str(source), str(target)], text=True, capture_output=True, timeout=150)
    if run.returncode != 0:
        raise RuntimeError(f"Frozen engine failed for {source.suffix}: stdout={run.stdout!r}, stderr={run.stderr!r}")
    result = target.read_text(encoding="utf-8")
    if token not in result:
        raise RuntimeError(f"Unexpected {source.suffix} output, missing {token!r}: {result[:400]!r}")
    print(f"PASS: {source.suffix} bundled converter")


with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    from docx import Document
    from pptx import Presentation
    from openpyxl import Workbook
    from reportlab.pdfgen import canvas

    html = folder / "sample.html"
    html.write_text("<h1>Yasora HTML Sample</h1><p>Local extraction</p>", encoding="utf-8")
    docx = folder / "sample.docx"
    doc = Document()
    doc.add_heading("Yasora Word Sample", level=1)
    doc.save(str(docx))
    pptx = folder / "sample.pptx"
    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[5])
    slide.shapes.title.text = "Yasora Slide Sample"
    presentation.save(str(pptx))
    xlsx = folder / "sample.xlsx"
    book = Workbook()
    book.active["A1"] = "Yasora Spreadsheet Sample"
    book.save(str(xlsx))
    pdf = folder / "sample.pdf"
    c = canvas.Canvas(str(pdf))
    c.drawString(90, 680, "Yasora PDF Sample")
    c.save()
    for source, token in [(html,"Yasora HTML Sample"), (docx,"Yasora Word Sample"), (pptx,"Yasora Slide Sample"), (xlsx,"Yasora Spreadsheet Sample"), (pdf,"Yasora PDF Sample")]:
        test_one(source, token)
print("PASS: all five bundled conversion smoke tests completed")
