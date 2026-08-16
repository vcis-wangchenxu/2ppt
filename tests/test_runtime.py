from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY / "skills" / "ppt-master"
SCRIPT_DIR = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import build_deck  # noqa: E402
import doctor  # noqa: E402
import init_project  # noqa: E402
import inspect_pptx  # noqa: E402
import runtime_common  # noqa: E402
import smoke_test  # noqa: E402
import validate_pptx  # noqa: E402
import verify_attribution  # noqa: E402
from runtime_common import UserInputError, write_json_atomic  # noqa: E402


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


class RuntimeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="ppt-master-test-")
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_spec(self, value: dict, name: str = "deck.json") -> Path:
        path = self.root / name
        write_json_atomic(path, value, overwrite=False)
        return path

    @staticmethod
    def minimal_spec(text: str = "Hello, Codex") -> dict:
        return {
            "schema_version": 1,
            "slides": [
                {
                    "elements": [
                        {
                            "type": "text",
                            "x": 1,
                            "y": 1,
                            "w": 8,
                            "h": 1,
                            "text": text,
                        }
                    ]
                }
            ],
        }

    def test_init_project_creates_safe_skeleton(self) -> None:
        project = init_project.initialize("季度复盘", self.root)
        self.assertEqual(project, (self.root / "季度复盘").resolve())
        self.assertTrue((project / "ppt-master.json").is_file())
        self.assertTrue((project / "deck.json").is_file())
        self.assertTrue((project / "assets" / "images").is_dir())
        self.assertTrue((project / "assets" / "data").is_dir())
        self.assertTrue((project / "output").is_dir())
        manifest = json.loads((project / "ppt-master.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(manifest["project_id"], "季度复盘")
        self.assertEqual(manifest["route"], "generate")
        self.assertEqual(manifest["profile"], "ordinary")
        with self.assertRaises(UserInputError):
            init_project.initialize("季度复盘", self.root)

    def test_init_project_rejects_unsafe_name(self) -> None:
        for name in (
            "../escape",
            "a/b",
            "..",
            ".",
            "a\\b",
            "\x00",
            "a:b",
            "x?y",
            "CON",
            "nul.txt",
            "COM1",
            "LPT9.log",
            "name.",
            "name ",
            " leading",
        ):
            with self.subTest(name=repr(name)), self.assertRaises(UserInputError):
                init_project.initialize(name, self.root)

    def test_init_project_rejects_broken_symlink(self) -> None:
        destination = self.root / "broken-project"
        try:
            destination.symlink_to(self.root / "missing-target", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"当前平台无法创建测试符号链接：{exc}")
        with self.assertRaises(UserInputError):
            init_project.initialize("broken-project", self.root)

    def test_build_minimal_inspect_validate_and_reproduce(self) -> None:
        spec_path = self.write_spec(self.minimal_spec())
        first = self.root / "first.pptx"
        second = self.root / "second.pptx"
        result = build_deck.build_from_file(spec_path, first)
        build_deck.build_from_file(spec_path, second)
        self.assertEqual(result["slides"], 1)
        self.assertEqual(result["elements"]["text"], 1)
        self.assertTrue(zipfile.is_zipfile(first))
        self.assertEqual(
            hashlib.sha256(first.read_bytes()).digest(),
            hashlib.sha256(second.read_bytes()).digest(),
        )

        validation = validate_pptx.validate(first)
        self.assertTrue(validation["ok"], validation["errors"])
        self.assertEqual(validation["slide_count"], 1)
        inspection = inspect_pptx.inspect(first)
        self.assertEqual(inspection["slide_count"], 1)
        self.assertEqual(inspection["elements"]["text"], 1)
        self.assertEqual(inspection["slides"][0]["title"], "Hello, Codex")

    def test_build_all_native_element_types(self) -> None:
        (self.root / "pixel.png").write_bytes(PNG_1X1)
        spec = {
            "schema_version": 1,
            "route": "generate",
            "profile": "ordinary",
            "meta": {"title": "Native elements", "author": "Tests"},
            "theme": {
                "fonts": {"heading": "Aptos Display", "body": "Aptos"},
                "colors": {"brand": "7C3AED"},
            },
            "slides": [
                {
                    "background": "background",
                    "notes": "[Sources]\n- test fixture",
                    "elements": [
                        {
                            "type": "text",
                            "x": 0.5,
                            "y": 0.2,
                            "w": 4,
                            "h": 0.6,
                            "paragraphs": [
                                {
                                    "runs": [
                                        {"text": "Native ", "bold": True},
                                        {"text": "elements", "color": "brand"},
                                    ]
                                }
                            ],
                        },
                        {
                            "type": "shape",
                            "shape_type": "rounded_rect",
                            "x": 0.5,
                            "y": 1.0,
                            "w": 2.0,
                            "h": 0.8,
                            "fill": "brand",
                            "text": "Editable",
                        },
                        {
                            "type": "line",
                            "x1": 0.5,
                            "y1": 2.1,
                            "x2": 2.5,
                            "y2": 2.1,
                            "color": "accent",
                            "dash": "dash",
                            "end_arrow": "triangle",
                        },
                        {
                            "type": "image",
                            "path": "pixel.png",
                            "x": 2.8,
                            "y": 1.0,
                            "w": 1.0,
                            "h": 1.0,
                            "fit": "cover",
                            "alt": "one-pixel fixture",
                        },
                        {
                            "type": "table",
                            "x": 4.0,
                            "y": 0.9,
                            "w": 4.0,
                            "h": 1.5,
                            "rows": [["Metric", "Value"], ["ARR", 42]],
                            "header_rows": 1,
                            "column_widths": [2.5, 1.5],
                        },
                        {
                            "type": "chart",
                            "chart": "column",
                            "x": 8.25,
                            "y": 0.8,
                            "w": 4.5,
                            "h": 3.2,
                            "categories": ["A", "B", "C"],
                            "series": [
                                {"name": "Current", "values": [1, 3, 2]},
                                {"name": "Plan", "values": [2, 2, 4]},
                            ],
                            "title": "Editable chart",
                            "legend": "bottom",
                            "colors": ["brand", "accent"],
                            "data_labels": True,
                        },
                    ],
                },
                {
                    "elements": [
                        {
                            "type": "chart",
                            "chart": "line",
                            "x": 1,
                            "y": 1,
                            "w": 5,
                            "h": 3,
                            "categories": ["Q1", "Q2"],
                            "series": [{"name": "Trend", "values": [2, None]}],
                        },
                        {
                            "type": "chart",
                            "chart": "pie",
                            "x": 7,
                            "y": 1,
                            "w": 5,
                            "h": 3,
                            "categories": ["Yes", "No"],
                            "series": [{"name": "Share", "values": [7, 3]}],
                        },
                    ]
                },
            ],
        }
        output = self.root / "native.pptx"
        spec_path = self.write_spec(spec)
        build_deck.build_from_file(spec_path, output)
        repeated = self.root / "native-repeated.pptx"
        build_deck.build_from_file(spec_path, repeated)
        self.assertEqual(
            hashlib.sha256(output.read_bytes()).digest(),
            hashlib.sha256(repeated.read_bytes()).digest(),
        )
        validation = validate_pptx.validate(output)
        self.assertTrue(validation["ok"], validation["errors"])
        inspection = inspect_pptx.inspect(output)
        self.assertEqual(inspection["slide_count"], 2)
        self.assertEqual(inspection["elements"]["image"], 1)
        self.assertEqual(inspection["elements"]["table"], 1)
        self.assertEqual(inspection["elements"]["chart"], 3)
        self.assertIn("[Sources]", inspection["slides"][0]["notes"])
        with zipfile.ZipFile(output, "r") as archive:
            chart_xml = b"\n".join(
                archive.read(name)
                for name in archive.namelist()
                if name.startswith("ppt/charts/chart") and name.endswith(".xml")
            )
        self.assertNotRegex(chart_xml, rb'<c:(?:axId|crossAx)\b[^>]*\bval="-')

    def test_rejects_asset_escape_and_absolute_path(self) -> None:
        for unsafe in ("../outside.png", str((self.root / "absolute.png").resolve())):
            spec = self.minimal_spec()
            spec["slides"][0]["elements"] = [
                {"type": "image", "path": unsafe, "x": 1, "y": 1, "w": 2, "h": 2}
            ]
            spec_path = self.root / f"unsafe-{len(unsafe)}.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            with self.subTest(path=unsafe), self.assertRaises(UserInputError):
                build_deck.build_from_file(spec_path, self.root / "unsafe.pptx")

    def test_rejects_invalid_specs_without_overwriting_output(self) -> None:
        output = self.root / "existing.pptx"
        output.write_bytes(b"keep")
        invalid_specs = [
            {"slides": [{"elements": []}]},
            {"schema_version": 1, "slides": []},
            {
                "schema_version": 1,
                "route": "generate",
                "profile": "standard",
                "slides": [{"elements": []}],
            },
            {
                "schema_version": 1,
                "route": "enhance",
                "profile": "ordinary",
                "slides": [{"elements": []}],
            },
            {
                "schema_version": 1,
                "route": "fill-template",
                "slides": [{"elements": []}],
            },
            {
                "schema_version": 1,
                "meta": {"title": "x" * 256},
                "slides": [{"elements": []}],
            },
            {
                "schema_version": 1,
                "slides": [{"elements": [{"type": "video", "x": 0, "y": 0, "w": 1, "h": 1}]}],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "text",
                                "x": 1,
                                "y": 1,
                                "w": 4,
                                "h": 1,
                                "paragraphs": [{"text": "too deep", "level": 9}],
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "text",
                                "x": 1,
                                "y": 1,
                                "w": 4,
                                "h": 2,
                                "paragraphs": ["x"] * (build_deck.MAX_PARAGRAPHS + 1),
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "chart",
                                "chart": "column",
                                "x": 1,
                                "y": 1,
                                "w": 5,
                                "h": 3,
                                "categories": ["A"],
                                "series": [
                                    {"name": f"S{index}", "values": [1]}
                                    for index in range(build_deck.MAX_CHART_SERIES + 1)
                                ],
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [{"elements": [{"type": "text", "x": 13, "y": 1, "w": 2, "h": 1, "text": "overflow"}]}],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "text",
                                "x": 1,
                                "y": 1,
                                "w": 4,
                                "h": 1,
                                "text": "typo",
                                "font_szie": 48,
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "shape",
                                "x": 1,
                                "y": 1,
                                "w": 2,
                                "h": 1,
                                "line": {"color": "000000", "widht": 8},
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "chart",
                                "chart": "column",
                                "x": 1,
                                "y": 1,
                                "w": 5,
                                "h": 3,
                                "categories": ["A"],
                                "series": [{"name": "S", "values": [1]}],
                                "style": 49,
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "chart",
                                "chart": "column",
                                "x": 1,
                                "y": 1,
                                "w": 5,
                                "h": 3,
                                "categories": ["A"],
                                "series": [{"name": "S", "values": [1], "valuez": [1]}],
                            }
                        ]
                    }
                ],
            },
            {
                "schema_version": 1,
                "slides": [
                    {
                        "elements": [
                            {
                                "type": "chart",
                                "chart": "bar",
                                "x": 1,
                                "y": 1,
                                "w": 5,
                                "h": 3,
                                "categories": ["A", "B"],
                                "series": [{"name": "S", "values": [1]}],
                            }
                        ]
                    }
                ],
            },
        ]
        for index, spec in enumerate(invalid_specs):
            spec_path = self.root / f"invalid-{index}.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            with self.subTest(index=index), self.assertRaises(UserInputError):
                build_deck.build_from_file(spec_path, output, force=True)
            self.assertEqual(output.read_bytes(), b"keep")

    def test_existing_output_requires_force_and_spec_cannot_be_output(self) -> None:
        spec_path = self.write_spec(self.minimal_spec())
        output = self.root / "deck.pptx"
        build_deck.build_from_file(spec_path, output)
        before = output.read_bytes()
        with self.assertRaises(UserInputError):
            build_deck.build_from_file(spec_path, output)
        self.assertEqual(output.read_bytes(), before)
        forced = build_deck.build_from_file(spec_path, output, force=True)
        self.assertTrue(forced["ok"])

        disguised_spec = self.root / "spec.pptx"
        disguised_spec.write_text(json.dumps(self.minimal_spec()), encoding="utf-8")
        original = disguised_spec.read_bytes()
        with self.assertRaises(UserInputError):
            build_deck.build_from_file(disguised_spec, disguised_spec, force=True)
        self.assertEqual(disguised_spec.read_bytes(), original)

        linked_output = self.root / "same-inode.pptx"
        try:
            linked_output.hardlink_to(spec_path)
        except OSError as exc:
            self.skipTest(f"当前平台无法创建测试硬链接：{exc}")
        spec_before = spec_path.read_bytes()
        with self.assertRaises(UserInputError):
            build_deck.build_from_file(spec_path, linked_output, force=True)
        self.assertEqual(spec_path.read_bytes(), spec_before)

    def test_rejects_spec_and_image_size_limits(self) -> None:
        oversized_spec = self.root / "oversized.json"
        oversized_spec.write_text(json.dumps(self.minimal_spec()), encoding="utf-8")
        original_json_limit = runtime_common.MAX_JSON_BYTES
        try:
            runtime_common.MAX_JSON_BYTES = 1
            with self.assertRaises(UserInputError):
                build_deck.build_from_file(oversized_spec, self.root / "oversized.pptx")
        finally:
            runtime_common.MAX_JSON_BYTES = original_json_limit

        image_path = self.root / "pixel.png"
        image_path.write_bytes(PNG_1X1)
        spec = self.minimal_spec()
        spec["slides"][0]["elements"] = [
            {"type": "image", "path": "pixel.png", "x": 1, "y": 1, "w": 1, "h": 1}
        ]
        image_spec = self.write_spec(spec, "image.json")
        original_image_limit = build_deck.MAX_IMAGE_BYTES
        try:
            build_deck.MAX_IMAGE_BYTES = 1
            with self.assertRaises(UserInputError):
                build_deck.build_from_file(image_spec, self.root / "image.pptx")
        finally:
            build_deck.MAX_IMAGE_BYTES = original_image_limit

    def test_rejects_symlink_output_without_touching_target(self) -> None:
        victim = self.root / "victim.txt"
        victim.write_bytes(b"keep")
        output = self.root / "linked.pptx"
        try:
            output.symlink_to(victim)
        except OSError as exc:
            self.skipTest(f"当前平台无法创建测试符号链接：{exc}")
        with self.assertRaises(UserInputError):
            build_deck.build_from_file(self.write_spec(self.minimal_spec()), output)
        self.assertEqual(victim.read_bytes(), b"keep")
        self.assertTrue(output.is_symlink())

    def test_validate_reports_bad_zip_and_bad_opc(self) -> None:
        plain = self.root / "plain.pptx"
        plain.write_bytes(b"not a zip")
        report = validate_pptx.validate(plain)
        self.assertFalse(report["ok"])
        self.assertTrue(any("ZIP" in error for error in report["errors"]))

        malformed = self.root / "malformed.pptx"
        with zipfile.ZipFile(malformed, "w") as archive:
            archive.writestr("[Content_Types].xml", b"<broken>")
        report = validate_pptx.validate(malformed)
        self.assertFalse(report["ok"])
        self.assertTrue(any("XML" in error for error in report["errors"]))
        self.assertTrue(any("presentation.xml" in error for error in report["errors"]))

    def test_validator_resource_limit_also_protects_inspector(self) -> None:
        crowded = self.root / "crowded.pptx"
        with zipfile.ZipFile(crowded, "w") as archive:
            for index in range(4):
                archive.writestr(f"part-{index}.txt", b"x")
        original_limit = validate_pptx.MAX_MEMBERS
        try:
            validate_pptx.MAX_MEMBERS = 3
            report = validate_pptx.validate(crowded)
            self.assertFalse(report["ok"])
            self.assertTrue(any("成员数" in error for error in report["errors"]))
            with self.assertRaises(UserInputError):
                inspect_pptx.inspect(crowded)
        finally:
            validate_pptx.MAX_MEMBERS = original_limit

    def test_inspector_turns_unsupported_chart_into_user_error(self) -> None:
        spec = self.minimal_spec()
        spec["slides"][0]["elements"] = [
            {
                "type": "chart",
                "chart": "column",
                "x": 1,
                "y": 1,
                "w": 5,
                "h": 3,
                "categories": ["A"],
                "series": [{"name": "S", "values": [1]}],
            }
        ]
        output = self.root / "unsupported-chart.pptx"
        build_deck.build_from_file(self.write_spec(spec), output)
        mutated = self.root / "mutated.pptx"
        with zipfile.ZipFile(output, "r") as source, zipfile.ZipFile(mutated, "w") as target:
            for info in source.infolist():
                data = source.read(info)
                if info.filename.startswith("ppt/charts/chart") and info.filename.endswith(".xml"):
                    data = data.replace(b"<c:barChart>", b"<c:unknownChart>")
                    data = data.replace(b"</c:barChart>", b"</c:unknownChart>")
                target.writestr(info, data)
        self.assertTrue(validate_pptx.validate(mutated)["ok"])
        with self.assertRaises(UserInputError):
            inspect_pptx.inspect(mutated)

    def test_attribution_and_doctor(self) -> None:
        attribution = verify_attribution.verify(SKILL_ROOT)
        self.assertTrue(attribution["ok"], attribution)
        missing = verify_attribution.verify(self.root / "missing-skill")
        self.assertFalse(missing["ok"])
        diagnostics = doctor.collect_diagnostics()
        self.assertTrue(diagnostics["python"]["ok"])
        self.assertTrue(diagnostics["required_dependencies"][0]["available"])

    def test_cli_json_and_smoke(self) -> None:
        doctor_run = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "doctor.py"), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(doctor_run.returncode, 0, doctor_run.stderr)
        self.assertTrue(json.loads(doctor_run.stdout)["ok"])
        self.assertEqual(smoke_test.main(), 0)


if __name__ == "__main__":
    unittest.main()
