"""Exercise the vendored engine through its public CLIs, without provider calls."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from openpyxl import Workbook
from pptx import Presentation
from pptx.util import Inches

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/ppt-master/scripts"


class NativePipelineTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ppt-native-测试 ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def run_script(self, name, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / name), *map(str, args)],
            cwd=self.root, capture_output=True, encoding="utf-8", timeout=60,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def make_source(self):
        source = self.root / "原始 deck.pptx"
        deck = Presentation()
        for number in (1, 2):
            slide = deck.slides.add_slide(deck.slide_layouts[6])
            slide.shapes.add_textbox(Inches(1), Inches(1), Inches(5), Inches(1)).text = f"原生标题 {number}"
            slide.notes_slide.notes_text_frame.text = f"Original notes {number}"
        deck.save(source)
        return source

    def test_roundtrip_edits_notes_preserves_slides_and_rejects_source_overwrite(self):
        source = self.make_source()
        original = source.read_bytes()
        workspace = self.root / "编辑 workspace"
        self.run_script("pptx_to_svg.py", source, "-o", workspace, "--inheritance-mode", "both", "--roundtrip")
        backing = workspace / "sources/source.pptx"
        notes = sorted((workspace / "notes").glob("*.md"))
        self.assertEqual(len(notes), 2)
        notes[0].write_text("更新后的讲稿。\n", encoding="utf-8")
        self.run_script("svg_quality_checker.py", workspace, "--roundtrip", "--json")
        for output in (source, backing):
            self.run_script("svg_to_pptx.py", workspace, "-o", output, "--roundtrip", success=False)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(backing.read_bytes(), original)
        output = self.root / "result.pptx"
        self.run_script("svg_to_pptx.py", workspace, "-o", output, "--roundtrip")
        self.run_script("validate_pptx.py", output, "--json")
        result = Presentation(output)
        self.assertEqual(len(result.slides), 2)
        self.assertIn("更新后的讲稿", result.slides[0].notes_slide.notes_text_frame.text)
        with zipfile.ZipFile(source) as before, zipfile.ZipFile(output) as after:
            for i in (1, 2):
                path = f"ppt/slides/slide{i}.xml"
                self.assertEqual(before.read(path), after.read(path))
        self.assertEqual(source.read_bytes(), original)

    def test_svg_exports_as_native_editable_text(self):
        project = self.root / "native generate"
        svg_dir = project / "svg_output"
        svg_dir.mkdir(parents=True)
        (svg_dir / "slide_01.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">'
            '<rect x="0" y="0" width="1280" height="720" fill="#FFFFFF"/>'
            '<text x="80" y="100" font-family="Arial" font-size="32" fill="#112233">Editable native text</text>'
            '</svg>', encoding="utf-8",
        )
        output = self.root / "native.pptx"
        self.run_script("svg_to_pptx.py", project, "-s", "svg_output", "-o", output)
        self.run_script("validate_pptx.py", output, "--json")
        deck = Presentation(output)
        texts = [shape.text for shape in deck.slides[0].shapes if shape.has_text_frame]
        self.assertIn("Editable native text", texts)

    def test_xlsx_conversion_and_source_alias_protection(self):
        source = self.root / "资料.xlsx"
        book = Workbook()
        book.active.append(["季度", "收入"])
        book.active.append(["Q1", 123])
        book.save(source)
        original = source.read_bytes()
        output = self.root / "资料.md"
        self.run_script("source_to_md.py", source, "-o", output)
        self.assertIn("123", output.read_text(encoding="utf-8"))
        self.run_script("source_to_md.py", source, "-o", source, success=False)
        self.assertEqual(source.read_bytes(), original)
        alias = self.root / "alias.md"
        os.link(source, alias)
        self.run_script("source_to_md.py", source, "-o", alias, success=False)
        self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
