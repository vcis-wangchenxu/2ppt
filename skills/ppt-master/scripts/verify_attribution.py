#!/usr/bin/env python3
"""Verify that the redistributed skill retains its required attribution files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


UPSTREAM_URL = "https://github.com/hugohe3/ppt-master"
ADAPTATION_URL = "https://github.com/vcis-wangchenxu/2ppt"
BASELINE_COMMIT = "090a133040d9bf41dca887dab78386c553af5dc6"


def verify(skill_root: Path) -> dict[str, Any]:
    root = skill_root.expanduser().resolve()
    checks: list[dict[str, Any]] = []

    def add(identifier: str, ok: bool, message: str, path: Path) -> None:
        checks.append(
            {"id": identifier, "ok": bool(ok), "message": message, "path": str(path)}
        )

    license_path = root / "LICENSE"
    upstream_path = root / "references" / "upstream.md"
    try:
        license_text = license_path.read_text(encoding="utf-8")
    except OSError:
        license_text = ""
    try:
        upstream_text = upstream_path.read_text(encoding="utf-8")
    except OSError:
        upstream_text = ""

    add("license.exists", license_path.is_file(), "Skill 目录包含 LICENSE", license_path)
    add(
        "license.mit",
        "MIT License" in license_text and "Permission is hereby granted" in license_text,
        "LICENSE 保留 MIT 许可正文",
        license_path,
    )
    add(
        "license.hugo-he",
        re.search(r"Copyright[^\n]*Hugo He", license_text, flags=re.IGNORECASE) is not None,
        "LICENSE 保留 Hugo He 版权声明",
        license_path,
    )
    add(
        "upstream.exists",
        upstream_path.is_file(),
        "references/upstream.md 存在",
        upstream_path,
    )
    add(
        "upstream.repository",
        UPSTREAM_URL in upstream_text,
        "上游说明包含原仓库地址",
        upstream_path,
    )
    add(
        "upstream.baseline",
        BASELINE_COMMIT in upstream_text,
        "上游说明固定了审计基线提交",
        upstream_path,
    )
    add(
        "upstream.author",
        "Hugo He" in upstream_text,
        "上游说明标明原作者",
        upstream_path,
    )
    add(
        "upstream.license",
        re.search(r"(?:许可证|license)[^\n]*MIT", upstream_text, flags=re.IGNORECASE) is not None,
        "上游说明标明 MIT 许可证",
        upstream_path,
    )
    add(
        "adaptation.repository",
        ADAPTATION_URL in upstream_text,
        "上游说明包含 Codex 适配仓库地址",
        upstream_path,
    )
    failures = [item for item in checks if not item["ok"]]
    return {
        "ok": not failures,
        "skill_root": str(root),
        "checks": checks,
        "failures": len(failures),
    }


def main(argv: list[str] | None = None) -> int:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="验证 ppt-master 上游署名和许可证文件")
    parser.add_argument("--skill-root", type=Path, default=default_root, help="Skill 根目录")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args(argv)
    report = verify(args.skill_root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"署名检查：{'通过' if report['ok'] else '失败'}")
        for item in report["checks"]:
            marker = "✓" if item["ok"] else "✗"
            print(f"{marker} {item['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
