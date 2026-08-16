#!/usr/bin/env python3
"""Run an end-to-end JSON -> PPTX -> OPC validation smoke test."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_deck import build_from_file
from runtime_common import write_json_atomic
from validate_pptx import validate


def main() -> int:
    spec = {
        "schema_version": 1,
        "route": "generate",
        "meta": {"title": "ppt-master smoke test", "author": "ppt-master"},
        "slides": [
            {
                "notes": "本页由 smoke_test.py 生成。",
                "elements": [
                    {
                        "type": "text",
                        "x": 1,
                        "y": 1,
                        "w": 8,
                        "h": 1,
                        "text": "ppt-master smoke test",
                        "font_size": 32,
                        "bold": True,
                    }
                ],
            }
        ],
    }
    with tempfile.TemporaryDirectory(prefix="ppt-master-smoke-") as temporary:
        root = Path(temporary)
        spec_path = root / "deck.json"
        output_path = root / "deck.pptx"
        write_json_atomic(spec_path, spec, overwrite=False)
        build = build_from_file(spec_path, output_path)
        validation = validate(output_path)
        report = {
            "ok": bool(build["ok"] and validation["ok"]),
            "slides": build["slides"],
            "elements": build["elements"],
            "validation_errors": validation["errors"],
        }
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
