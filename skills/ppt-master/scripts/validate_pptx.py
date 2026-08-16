#!/usr/bin/env python3
"""Validate ZIP, OPC, XML and slide structure without requiring PowerPoint."""

from __future__ import annotations

import argparse
import json
import posixpath
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET

from runtime_common import UserInputError


NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

MAX_MEMBERS = 20_000
MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024
MAX_XML_TOTAL_BYTES = 128 * 1024 * 1024
MAX_XML_PART_BYTES = 32 * 1024 * 1024
MAX_SUSPICIOUS_RATIO = 1_000
MIN_RATIO_CHECK_BYTES = 10 * 1024 * 1024


def _safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and "\\" not in name and not path.is_absolute() and ".." not in path.parts


def _source_for_rels(name: str) -> str | None:
    if name == "_rels/.rels":
        return None
    path = PurePosixPath(name)
    if path.parent.name != "_rels" or not path.name.endswith(".rels"):
        return ""
    source_name = path.name[: -len(".rels")]
    return str(path.parent.parent / source_name)


def _resolve_target(source: str | None, target: str) -> str:
    target = target.split("#", 1)[0]
    if "\\" in target:
        raise ValueError("关系目标包含反斜杠")
    if target.startswith("/"):
        normalized = posixpath.normpath(target.lstrip("/"))
    else:
        base = "" if source is None else posixpath.dirname(source)
        normalized = posixpath.normpath(posixpath.join(base, target))
    if normalized in {"", ".", ".."} or normalized.startswith("../") or normalized.startswith("/"):
        raise ValueError("关系目标越过包边界")
    return normalized


def _xml(archive: zipfile.ZipFile, name: str, errors: list[str]) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(name))
    except (KeyError, ET.ParseError, ValueError) as exc:
        errors.append(f"XML 无法解析：{name}（{exc}）")
        return None


def validate(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {
        "path": str(resolved),
        "members": 0,
        "compressed_bytes": 0,
        "uncompressed_bytes": 0,
        "xml_bytes": 0,
        "xml_parts": 0,
        "slide_count": 0,
        "external_relationships": 0,
    }
    if not resolved.is_file():
        return {"ok": False, "errors": [f"文件不存在：{resolved}"], "warnings": [], **details}
    if resolved.suffix.lower() != ".pptx":
        warnings.append("文件扩展名不是 .pptx")
    if not zipfile.is_zipfile(resolved):
        return {"ok": False, "errors": ["文件不是有效 ZIP/OPC 包"], "warnings": warnings, **details}

    try:
        with zipfile.ZipFile(resolved, "r") as archive:
            infos = [item for item in archive.infolist() if not item.is_dir()]
            names = [item.filename for item in infos]
            name_set = set(names)
            details["members"] = len(names)
            details["compressed_bytes"] = sum(item.compress_size for item in infos)
            details["uncompressed_bytes"] = sum(item.file_size for item in infos)
            xml_infos = [
                item
                for item in infos
                if item.filename.endswith((".xml", ".rels"))
                or item.filename == "[Content_Types].xml"
            ]
            details["xml_bytes"] = sum(item.file_size for item in xml_infos)

            duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
            if duplicates:
                errors.append("ZIP 包含重复成员：" + ", ".join(duplicates[:10]))
            unsafe = sorted(name for name in names if not _safe_member(name))
            if unsafe:
                errors.append("ZIP 包含不安全成员路径：" + ", ".join(unsafe[:10]))
            encrypted = [item.filename for item in infos if item.flag_bits & 0x1]
            if encrypted:
                errors.append("ZIP 包含加密成员，无法安全验证：" + ", ".join(encrypted[:10]))

            resource_error = False
            if len(infos) > MAX_MEMBERS:
                errors.append(f"ZIP 成员数超过安全上限 {MAX_MEMBERS}")
                resource_error = True
            if details["uncompressed_bytes"] > MAX_UNCOMPRESSED_BYTES:
                errors.append(
                    f"ZIP 解压后总大小超过安全上限 {MAX_UNCOMPRESSED_BYTES} 字节"
                )
                resource_error = True
            if details["xml_bytes"] > MAX_XML_TOTAL_BYTES:
                errors.append(f"XML 总大小超过安全上限 {MAX_XML_TOTAL_BYTES} 字节")
                resource_error = True
            oversized_xml = [
                item.filename for item in xml_infos if item.file_size > MAX_XML_PART_BYTES
            ]
            if oversized_xml:
                errors.append("XML 单件超过安全上限：" + ", ".join(oversized_xml[:10]))
                resource_error = True
            suspicious_ratio = [
                item.filename
                for item in infos
                if item.file_size >= MIN_RATIO_CHECK_BYTES
                and item.file_size / max(item.compress_size, 1) > MAX_SUSPICIOUS_RATIO
            ]
            if suspicious_ratio:
                errors.append("ZIP 成员压缩比异常：" + ", ".join(suspicious_ratio[:10]))
                resource_error = True

            if resource_error or encrypted:
                return {
                    "ok": False,
                    "errors": errors,
                    "warnings": warnings,
                    **details,
                }

            corrupt = archive.testzip()
            if corrupt:
                errors.append(f"ZIP CRC 校验失败：{corrupt}")

            required = {
                "[Content_Types].xml",
                "_rels/.rels",
                "ppt/presentation.xml",
                "ppt/_rels/presentation.xml.rels",
            }
            for missing in sorted(required - name_set):
                errors.append(f"缺少必需 OPC 部件：{missing}")

            roots: dict[str, ET.Element] = {}
            for name in names:
                if name.endswith(".xml") or name.endswith(".rels") or name == "[Content_Types].xml":
                    root = _xml(archive, name, errors)
                    if root is not None:
                        roots[name] = root
            details["xml_parts"] = len(roots)

            content_root = roots.get("[Content_Types].xml")
            defaults: set[str] = set()
            overrides: dict[str, str] = {}
            if content_root is not None:
                if content_root.tag != f"{{{NS_CT}}}Types":
                    errors.append("[Content_Types].xml 根元素不是 Types")
                for item in content_root:
                    if item.tag == f"{{{NS_CT}}}Default":
                        extension = item.get("Extension")
                        if extension:
                            defaults.add(extension.lower())
                    elif item.tag == f"{{{NS_CT}}}Override":
                        part = item.get("PartName", "").lstrip("/")
                        if part:
                            overrides[part] = item.get("ContentType", "")
                presentation_type = overrides.get("ppt/presentation.xml", "")
                if "presentationml.presentation.main+xml" not in presentation_type:
                    errors.append("presentation.xml 缺少正确的 presentation 内容类型")
                for name in names:
                    if name == "[Content_Types].xml":
                        continue
                    extension = (
                        "rels"
                        if name.endswith(".rels")
                        else PurePosixPath(name).suffix.lstrip(".").lower()
                    )
                    if name not in overrides and extension not in defaults:
                        errors.append(f"OPC 部件没有 Content Type 映射：{name}")

            relationships: dict[str, dict[str, tuple[str, str, str]]] = {}
            for rels_name, root in roots.items():
                if not rels_name.endswith(".rels"):
                    continue
                source = _source_for_rels(rels_name)
                if source == "":
                    errors.append(f"关系部件路径无效：{rels_name}")
                    continue
                if root.tag != f"{{{NS_REL}}}Relationships":
                    errors.append(f"关系部件根元素错误：{rels_name}")
                    continue
                entries: dict[str, tuple[str, str, str]] = {}
                for relationship in root.findall(f"{{{NS_REL}}}Relationship"):
                    rel_id = relationship.get("Id", "")
                    target = relationship.get("Target", "")
                    rel_type = relationship.get("Type", "")
                    target_mode = relationship.get("TargetMode", "Internal")
                    if not rel_id or not target or not rel_type:
                        errors.append(f"关系缺少 Id/Target/Type：{rels_name}")
                        continue
                    if rel_id in entries:
                        errors.append(f"关系 Id 重复：{rels_name}#{rel_id}")
                        continue
                    if target_mode == "External":
                        details["external_relationships"] += 1
                        warnings.append(f"存在外部关系：{rels_name}#{rel_id} -> {target}")
                        entries[rel_id] = (target, rel_type, target_mode)
                        continue
                    if target_mode != "Internal":
                        errors.append(f"未知 TargetMode：{rels_name}#{rel_id}={target_mode}")
                        continue
                    try:
                        resolved_target = _resolve_target(source, target)
                    except ValueError as exc:
                        errors.append(f"不安全关系：{rels_name}#{rel_id}（{exc}）")
                        continue
                    if resolved_target not in name_set:
                        errors.append(f"关系目标不存在：{rels_name}#{rel_id} -> {resolved_target}")
                    entries[rel_id] = (resolved_target, rel_type, target_mode)
                relationships["" if source is None else source] = entries

            root_rels = relationships.get("", {})
            office_targets = [
                target
                for target, rel_type, mode in root_rels.values()
                if mode == "Internal" and rel_type.endswith("/officeDocument")
            ]
            if office_targets != ["ppt/presentation.xml"]:
                errors.append("根关系必须唯一指向 ppt/presentation.xml")

            presentation = roots.get("ppt/presentation.xml")
            slide_targets: list[str] = []
            if presentation is not None:
                if presentation.tag != f"{{{NS_P}}}presentation":
                    errors.append("presentation.xml 根元素不是 p:presentation")
                slide_ids = presentation.findall(f".//{{{NS_P}}}sldId")
                details["slide_count"] = len(slide_ids)
                if not slide_ids:
                    errors.append("演示文稿不包含幻灯片")
                seen_numeric_ids: set[str] = set()
                presentation_rels = relationships.get("ppt/presentation.xml", {})
                for slide_id in slide_ids:
                    numeric_id = slide_id.get("id", "")
                    rel_id = slide_id.get(f"{{{NS_R}}}id", "")
                    if not numeric_id or numeric_id in seen_numeric_ids:
                        errors.append("presentation.xml 中 slide id 缺失或重复")
                    seen_numeric_ids.add(numeric_id)
                    relationship = presentation_rels.get(rel_id)
                    if relationship is None:
                        errors.append(f"幻灯片关系不存在：{rel_id or '(empty)'}")
                        continue
                    target, rel_type, mode = relationship
                    if mode != "Internal" or not rel_type.endswith("/slide"):
                        errors.append(f"{rel_id} 不是内部 slide 关系")
                        continue
                    slide_targets.append(target)
                if len(slide_targets) != len(set(slide_targets)):
                    errors.append("多条 slide id 关系指向同一幻灯片部件")

            for slide_name in slide_targets:
                root = roots.get(slide_name)
                if root is None:
                    errors.append(f"幻灯片 XML 缺失或损坏：{slide_name}")
                    continue
                if root.tag != f"{{{NS_P}}}sld":
                    errors.append(f"幻灯片根元素不是 p:sld：{slide_name}")
                shape_tree = root.find(f"./{{{NS_P}}}cSld/{{{NS_P}}}spTree")
                if shape_tree is None:
                    errors.append(f"幻灯片缺少 p:cSld/p:spTree：{slide_name}")

            if any(name.lower().endswith("vbaproject.bin") for name in names):
                warnings.append("PPTX 包含 VBA 宏部件")
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        errors.append(f"无法读取 PPTX：{exc}")

    return {"ok": not errors, "errors": errors, "warnings": warnings, **details}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="验证 PPTX 的 ZIP、OPC、XML 与幻灯片结构")
    parser.add_argument("file", type=Path, help="要验证的 .pptx 文件")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args(argv)
    report = validate(args.file)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"PPTX 验证：{'通过' if report['ok'] else '失败'}")
        print(f"文件：{report['path']}")
        print(f"幻灯片：{report['slide_count']}；包成员：{report['members']}；XML：{report['xml_parts']}")
        for warning in report["warnings"]:
            print(f"警告：{warning}")
        for error in report["errors"]:
            print(f"错误：{error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
