#!/usr/bin/env python3
"""Diagnose the required Python runtime and useful optional PPT tools."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


MINIMUM_PYTHON = (3, 10)


def _distribution(name: str) -> dict[str, Any]:
    try:
        version = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return {"name": name, "available": False, "version": None}
    return {"name": name, "available": True, "version": version}


def _dependency(distribution: str, import_name: str) -> dict[str, Any]:
    item = _distribution(distribution)
    item["import"] = import_name
    item["importable"] = False
    item["error"] = None
    try:
        importlib.import_module(import_name)
    except Exception as exc:  # an installed but broken dependency must fail doctor
        item["error"] = f"{type(exc).__name__}: {exc}"
    else:
        item["importable"] = True
    item["available"] = bool(item["available"] and item["importable"])
    return item


def collect_diagnostics() -> dict[str, Any]:
    python_ok = sys.version_info >= MINIMUM_PYTHON
    dependencies = [
        _dependency("python-pptx", "pptx"),
        _dependency("Pillow", "PIL"),
    ]
    tools = []
    for name, purpose in (
        ("libreoffice", "PPTX 渲染与格式兼容检查"),
        ("soffice", "LibreOffice 命令行入口"),
        ("pdftoppm", "PDF 页面转图片"),
        ("ffmpeg", "音视频素材检查"),
    ):
        located = shutil.which(name)
        tools.append(
            {
                "name": name,
                "available": located is not None,
                "path": str(Path(located).resolve()) if located else None,
                "required": False,
                "purpose": purpose,
            }
        )
    required_ok = python_ok and all(item["available"] for item in dependencies)
    return {
        "ok": required_ok,
        "python": {
            "available": True,
            "executable": str(Path(sys.executable).resolve()),
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "minimum": ".".join(map(str, MINIMUM_PYTHON)),
            "ok": python_ok,
        },
        "required_dependencies": dependencies,
        "optional_tools": tools,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查 ppt-master 的运行环境")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args(argv)
    report = collect_diagnostics()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        status = "通过" if report["ok"] else "未通过"
        print(f"ppt-master 环境检查：{status}")
        py = report["python"]
        marker = "✓" if py["ok"] else "✗"
        print(f"{marker} Python {py['version']}（要求 >= {py['minimum']}）")
        for item in report["required_dependencies"]:
            marker = "✓" if item["available"] else "✗"
            version = item["version"] or "未安装"
            print(f"{marker} {item['name']} {version}（必需）")
            if item.get("error"):
                print(f"  导入失败：{item['error']}")
        for item in report["optional_tools"]:
            marker = "✓" if item["available"] else "-"
            detail = item["path"] or "未找到"
            print(f"{marker} {item['name']}: {detail}（可选：{item['purpose']}）")
        if not report["ok"]:
            print("修复建议：使用 Python 3.10+ 并运行 pip install -r requirements.txt")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
