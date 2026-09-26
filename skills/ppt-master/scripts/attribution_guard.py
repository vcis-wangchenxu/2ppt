#!/usr/bin/env python3
"""Integrity guard for the Codex-native PPT Master adaptation."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

_ERROR_MESSAGE = (
    "PPT Master Codex adaptation integrity check failed. "
    "Reinstall from https://github.com/vcis-wangchenxu/2ppt."
)
_SKILL_DIR = Path(__file__).resolve().parent.parent
_UPSTREAM_URL = "https://github.com/hugohe3/ppt-master"
_ADAPTATION_URL = "https://github.com/vcis-wangchenxu/2ppt"
_BASELINE_COMMIT = "a50758ac29ec027e85966db33e2ae80031446756"
_REQUIRED_FILES = (
    "SKILL.md",
    "LICENSE",
    "agents/openai.yaml",
    "references/upstream.md",
    "scripts/console_encoding.py",
    "scripts/pptx_to_svg.py",
    "scripts/svg_to_pptx.py",
    "scripts/svg_quality_checker.py",
)

def _read(relative: str) -> str:
    return (_SKILL_DIR / relative).read_text(encoding="utf-8")

def _metadata_is_valid() -> bool:
    text = _read("SKILL.md")
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---\n", 4)
    if end < 0:
        return False
    meta = text[4:end]
    return (
        re.search(r"(?m)^name:\s*ppt-master\s*$", meta) is not None
        and "$ppt-master" in meta
    )

def _license_is_valid() -> bool:
    text = _read("LICENSE")
    return "MIT License" in text and "Hugo He" in text

def _upstream_identity_is_valid() -> bool:
    text = _read("references/upstream.md")
    return (
        _UPSTREAM_URL in text
        and _ADAPTATION_URL in text
        and _BASELINE_COMMIT in text
        and "MIT" in text
        and "Hugo He" in text
    )

def _files_are_present() -> bool:
    return all((_SKILL_DIR / relative).is_file() for relative in _REQUIRED_FILES)

def _integrity_is_valid() -> bool:
    return (
        _files_are_present()
        and _metadata_is_valid()
        and _license_is_valid()
        and _upstream_identity_is_valid()
    )

def require_skill_integrity() -> None:
    try:
        valid = _integrity_is_valid()
    except (OSError, UnicodeError, ValueError):
        valid = False
    if valid:
        return
    print(_ERROR_MESSAGE, file=sys.stderr)
    raise SystemExit(78)

def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Validate the Codex-native PPT Master adaptation identity."
    )

def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    require_skill_integrity()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
