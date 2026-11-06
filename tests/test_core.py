from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from yasora_studio.paths import source_items
from yasora_studio.converter import convert_one
from yasora_studio.updates import installed_engine_version


class FakeEngine:
    def convert_local(self, path):
        return SimpleNamespace(markdown="# Test\n\n" + Path(path).read_text(encoding="utf-8"))


class ConversionTests(unittest.TestCase):
    def test_folder_output_exclusion_and_collision(self):
        with TemporaryDirectory() as root:
            base = Path(root)
            source = base / "source"
            source.mkdir()
            (source / "report.html").write_text("report", encoding="utf-8")
            (source / "report.txt").write_text("report", encoding="utf-8")
            sub = source / "sub"
            sub.mkdir()
            (sub / "a.json").write_text("{}", encoding="utf-8")
            output = source / "output"
            output.mkdir()
            (output / "previous.md").write_text("previous", encoding="utf-8")
            pairs = source_items([source], output)
            self.assertEqual(len(pairs), 3)
            paths = [str(r) for _, r in pairs]
            self.assertIn("source/report.html.md", paths)
            self.assertIn("source/report.txt.md", paths)
            self.assertIn("source/sub/a.json.md", paths)

    def test_atomic_conversion_skip_overwrite(self):
        with TemporaryDirectory() as root:
            base = Path(root)
            src = base / "in.html"
            dst = base / "out.md"
            src.write_text("hello", encoding="utf-8")
            self.assertEqual(convert_one(src, dst, factory=FakeEngine), "converted")
            self.assertEqual(convert_one(src, dst, factory=FakeEngine), "skipped")
            self.assertEqual(dst.read_text(encoding="utf-8"), "# Test\n\nhello")
            src.write_text("changed", encoding="utf-8")
            self.assertEqual(convert_one(src, dst, overwrite=True, factory=FakeEngine), "converted")
            self.assertIn("changed", dst.read_text(encoding="utf-8"))
            self.assertFalse(list(base.glob(".*.tmp")))

    def test_empty_output_and_bad_input(self):
        with TemporaryDirectory() as root:
            self.assertRaises(ValueError, convert_one, Path(root) / "missing.pdf", Path(root) / "out.md", factory=FakeEngine)

    def test_engine_info_offline(self):
        self.assertIsInstance(installed_engine_version(), str)


if __name__ == "__main__":
    unittest.main()
