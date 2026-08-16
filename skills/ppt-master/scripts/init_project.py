#!/usr/bin/env python3
"""Create a minimal, safe and reproducible ppt-master project."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from runtime_common import SCHEMA_VERSION, UserInputError, write_json_atomic


SAFE_NAME = re.compile(r'^[^<>:"/\\|?*\x00-\x1f]+$')
WINDOWS_DEVICE_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def validate_project_name(name: str) -> str:
    value = name.strip()
    device_stem = value.split(".", 1)[0].upper()
    if (
        not value
        or value != name
        or value in {".", ".."}
        or value.endswith((".", " "))
        or not SAFE_NAME.fullmatch(value)
        or device_stem in WINDOWS_DEVICE_NAMES
    ):
        raise UserInputError(
            "项目名必须是跨平台安全的单级目录名：不得含控制字符或 <>:\"/\\|?*，"
            "不得使用 Windows 设备名，也不得以点或空格结尾"
        )
    if len(value) > 120:
        raise UserInputError("项目名过长（上限 120 个字符）")
    return value


def starter_spec(name: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "route": "generate",
        "profile": "ordinary",
        "meta": {"title": name, "author": ""},
        "slide_size": "wide",
        "theme": {
            "fonts": {"heading": "Aptos Display", "body": "Aptos"},
            "colors": {
                "background": "F7F8FA",
                "text": "172033",
                "primary": "2563EB",
                "secondary": "0F766E",
                "accent": "F59E0B",
                "muted": "667085",
                "white": "FFFFFF",
            },
        },
        "slides": [
            {
                "background": "background",
                "notes": "在这里添加演讲者备注；如引用外部资料，请记录来源。",
                "elements": [
                    {
                        "type": "text",
                        "x": 1.0,
                        "y": 1.45,
                        "w": 11.33,
                        "h": 1.0,
                        "text": name,
                        "font_size": 34,
                        "font_face": "Aptos Display",
                        "bold": True,
                        "color": "text",
                        "align": "center",
                        "valign": "middle",
                    },
                    {
                        "type": "text",
                        "x": 2.0,
                        "y": 2.7,
                        "w": 9.33,
                        "h": 0.65,
                        "text": "用清晰的受众语言填写副标题",
                        "font_size": 20,
                        "color": "muted",
                        "align": "center",
                    },
                ],
            }
        ],
    }


def initialize(name: str, root: Path) -> Path:
    clean_name = validate_project_name(name)
    root = root.expanduser().resolve()
    destination = root / clean_name
    if destination.is_symlink():
        raise UserInputError(f"目标是符号链接，已停止：{destination}")
    if destination.exists():
        if not destination.is_dir():
            raise UserInputError(f"目标已存在且不是目录：{destination}")
        try:
            next(destination.iterdir())
        except StopIteration:
            pass
        else:
            raise UserInputError(f"目标目录非空，为避免覆盖已停止：{destination}")

    destination.mkdir(parents=True, exist_ok=True)
    for relative in ("assets/images", "assets/data", "output"):
        (destination / relative).mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "project_id": clean_name,
        "route": "generate",
        "profile": "ordinary",
        "mode": "default",
        "goal": "",
        "audience": "",
        "language": "zh-CN",
        "slide_size": "wide",
        "slide_plan": [],
        "visual_system": {"spec": "deck.json#theme"},
        "editability": {
            "native": ["text", "shape", "line", "table", "chart"],
            "raster": ["image"],
        },
        "preserve": [],
        "sources": [],
        "assumptions": ["未指定页面比例时使用 16:9"],
        "runtime": {"builder": "ppt-master/bundled-json-v1", "spec": "deck.json"},
        "deliverables": {"pptx": "output/deck.pptx"},
        "acceptance": ["validate_pptx.py 通过", "完成逐页视觉 QA"],
        "paths": {"spec": "deck.json", "assets": "assets", "output": "output"},
    }
    write_json_atomic(destination / "ppt-master.json", manifest, overwrite=False)
    write_json_atomic(destination / "deck.json", starter_spec(clean_name), overwrite=False)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="创建 ppt-master 项目骨架")
    parser.add_argument("name", help="项目名（单级目录名）")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="父目录，默认当前目录")
    args = parser.parse_args(argv)
    try:
        destination = initialize(args.name, args.root)
    except UserInputError as exc:
        parser.exit(2, f"错误：{exc}\n")
    except OSError as exc:
        parser.exit(1, f"初始化失败：{exc}\n")
    print(json.dumps({"ok": True, "project": str(destination)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
