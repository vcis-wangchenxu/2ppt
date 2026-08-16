#!/usr/bin/env python3
"""Shared helpers for the small, deterministic ppt-master runtime."""

from __future__ import annotations

import json
import math
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = 1
HEX_COLOR_RE = re.compile(r"^#?([0-9A-Fa-f]{6})$")
MAX_JSON_BYTES = 32 * 1024 * 1024
INVALID_XML_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")


class UserInputError(ValueError):
    """An actionable error caused by a command-line argument or input file."""


def load_json_object(path: Path) -> dict[str, Any]:
    try:
        size = path.stat().st_size
        if size > MAX_JSON_BYTES:
            raise UserInputError(f"JSON 文件超过安全上限 {MAX_JSON_BYTES} 字节：{path}")
        raw = path.read_text(encoding="utf-8")
    except UserInputError:
        raise
    except OSError as exc:
        raise UserInputError(f"无法读取 JSON：{path}（{exc}）") from exc
    def reject_constant(value: str) -> None:
        raise ValueError(f"不允许非有限数字 {value}")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, item in pairs:
            if key in result:
                raise ValueError(f"对象字段重复：{key}")
            result[key] = item
        return result

    try:
        value = json.loads(
            raw,
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
    except json.JSONDecodeError as exc:
        raise UserInputError(
            f"JSON 语法错误：{path}:{exc.lineno}:{exc.colno}：{exc.msg}"
        ) from exc
    except ValueError as exc:
        raise UserInputError(f"JSON 内容错误：{path}：{exc}") from exc
    if not isinstance(value, dict):
        raise UserInputError("JSON 顶层必须是对象")
    return value


def write_json_atomic(path: Path, value: Any, *, overwrite: bool = True) -> None:
    """Write UTF-8 JSON without ever exposing a partially written file."""
    if path.exists() and not overwrite:
        raise UserInputError(f"为避免覆盖已有文件，已停止：{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def safe_relative_file(base: Path, value: Any, *, field: str, must_exist: bool = True) -> Path:
    """Resolve an untrusted spec path while preventing absolute/traversal escapes."""
    if not isinstance(value, str) or not value.strip():
        raise UserInputError(f"{field} 必须是非空相对路径")
    candidate = Path(value)
    if candidate.is_absolute() or candidate.anchor or ".." in candidate.parts:
        raise UserInputError(f"{field} 只能是 spec 目录内的相对路径：{value!r}")
    root = base.resolve()
    resolved = (root / candidate).resolve()
    if not is_relative_to(resolved, root):
        raise UserInputError(f"{field} 越过了 spec 目录边界：{value!r}")
    if must_exist and not resolved.is_file():
        raise UserInputError(f"{field} 指向的文件不存在：{value!r}")
    return resolved


def require_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise UserInputError(f"{field} 必须是对象")
    return value


def require_list(value: Any, field: str, *, nonempty: bool = False) -> list[Any]:
    if not isinstance(value, list):
        raise UserInputError(f"{field} 必须是数组")
    if nonempty and not value:
        raise UserInputError(f"{field} 不能为空")
    return value


def number(
    value: Any,
    field: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
    positive: bool = False,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UserInputError(f"{field} 必须是数字")
    result = float(value)
    if not math.isfinite(result):
        raise UserInputError(f"{field} 必须是有限数字")
    if positive and result <= 0:
        raise UserInputError(f"{field} 必须大于 0")
    if minimum is not None and result < minimum:
        raise UserInputError(f"{field} 不得小于 {minimum}")
    if maximum is not None and result > maximum:
        raise UserInputError(f"{field} 不得大于 {maximum}")
    return result


def integer(value: Any, field: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise UserInputError(f"{field} 必须是整数")
    if minimum is not None and value < minimum:
        raise UserInputError(f"{field} 不得小于 {minimum}")
    return value


def boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise UserInputError(f"{field} 必须是布尔值")
    return value


def choice(value: Any, field: str, choices: Iterable[str]) -> str:
    allowed = tuple(choices)
    if not isinstance(value, str) or value not in allowed:
        raise UserInputError(f"{field} 必须是以下值之一：{', '.join(allowed)}")
    return value


def color(value: Any, field: str, palette: Mapping[str, str] | None = None) -> str:
    """Return an uppercase six-digit RGB value, resolving theme color names."""
    if not isinstance(value, str):
        raise UserInputError(f"{field} 必须是颜色字符串")
    candidate = value.strip()
    if palette and candidate in palette:
        candidate = palette[candidate]
    match = HEX_COLOR_RE.fullmatch(candidate)
    if not match:
        raise UserInputError(f"{field} 必须是 RRGGBB/#RRGGBB 或主题颜色名")
    return match.group(1).upper()


def optional_string(value: Any, field: str, *, maximum: int = 10000) -> str:
    if not isinstance(value, str):
        raise UserInputError(f"{field} 必须是字符串")
    if len(value) > maximum:
        raise UserInputError(f"{field} 过长（上限 {maximum} 个字符）")
    if INVALID_XML_CHAR_RE.search(value):
        raise UserInputError(f"{field} 包含 OOXML 不允许的控制字符")
    return value


def emit_result(payload: Mapping[str, Any], *, as_json: bool, lines: list[str]) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("\n".join(lines))
