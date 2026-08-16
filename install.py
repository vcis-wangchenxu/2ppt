#!/usr/bin/env python3
"""Install this repository's PPT Master skill for Codex.

The default is a user-level copy at ``~/.agents/skills/ppt-master``. Use
``--project PATH`` for a repository-local installation, or ``--symlink`` while
developing. Existing destinations are never overwritten unless ``--force`` is
provided; forced replacement first moves the old destination to a timestamped
backup next to it.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


SKILL_NAME = "ppt-master"
REPOSITORY_ROOT = Path(__file__).resolve().parent
SOURCE_DIR = REPOSITORY_ROOT / "skills" / SKILL_NAME


class InstallError(RuntimeError):
    """A user-actionable installation error."""


def path_exists(path: Path) -> bool:
    """Return True for regular paths, symlinks, and broken symlinks."""

    return path.exists() or path.is_symlink()


def remove_path(path: Path) -> None:
    """Remove one known installation or temporary path."""

    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def backup_path_for(destination: Path) -> Path:
    """Choose a non-existing timestamped backup path beside destination."""

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    base = destination.with_name(f"{destination.name}.backup-{stamp}")
    candidate = base
    counter = 1
    while path_exists(candidate):
        candidate = destination.with_name(f"{base.name}-{counter}")
        counter += 1
    return candidate


def resolve_destination(args: argparse.Namespace) -> Path:
    """Resolve the requested user, project, or explicit installation path."""

    if args.target is not None:
        destination = args.target.expanduser()
    elif args.project is not None:
        project_root = args.project.expanduser().resolve()
        if not project_root.is_dir():
            raise InstallError(f"项目目录不存在或不是目录：{project_root}")
        destination = project_root / ".agents" / "skills" / SKILL_NAME
    else:
        destination = Path.home() / ".agents" / "skills" / SKILL_NAME
    # Normalize ``..`` and make the path absolute without dereferencing an
    # existing final symlink. Dereferencing here would make a linked install
    # look identical to SOURCE_DIR and prevent safe upgrade/uninstall.
    return Path(os.path.abspath(os.fspath(destination)))


def validate_source(destination: Path) -> None:
    """Validate repository layout and guard against self-overwrite."""

    if not (SOURCE_DIR / "SKILL.md").is_file():
        raise InstallError(
            f"未找到 {SOURCE_DIR / 'SKILL.md'}；请从完整仓库根目录运行 install.py。"
        )
    if destination.name != SKILL_NAME:
        raise InstallError(
            f"安装目标目录名必须是 {SKILL_NAME!r}，当前为 {destination.name!r}。"
        )
    source = SOURCE_DIR.resolve()
    # Resolve parent symlinks without dereferencing an existing destination
    # symlink. This keeps ``--force --symlink`` upgrades safe while still
    # detecting a target routed into the repository through a linked parent.
    effective_destination = destination.parent.resolve(strict=False) / destination.name

    def same_existing(left: Path, right: Path) -> bool:
        try:
            return os.path.samefile(left, right)
        except OSError:
            return False

    # ``Path.relative_to`` is lexical and can be bypassed by a case alias on
    # default macOS filesystems. Compare existing ancestors by inode too. Do
    # not dereference the final destination symlink: an external development
    # install intentionally pointing at SOURCE_DIR must remain upgradeable.
    if not destination.is_symlink() and effective_destination.exists():
        if same_existing(effective_destination, source):
            raise InstallError("安装目标不能与仓库中的 Skill 源目录相同。")
        for source_ancestor in source.parents:
            if same_existing(effective_destination, source_ancestor):
                raise InstallError("安装目标不能包含仓库中的 Skill 源目录。")
    for destination_ancestor in (
        effective_destination.parent,
        *effective_destination.parent.parents,
    ):
        if destination_ancestor.exists() and same_existing(destination_ancestor, source):
            raise InstallError("安装目标不能位于仓库中的 Skill 源目录内。")

    try:
        effective_destination.relative_to(source)
    except ValueError:
        pass
    else:
        raise InstallError("安装目标不能位于仓库中的 Skill 源目录内。")
    try:
        source.relative_to(effective_destination)
    except ValueError:
        pass
    else:
        raise InstallError("安装目标不能包含仓库中的 Skill 源目录。")


def install_copy(destination: Path) -> None:
    """Copy the Skill through a sibling temporary directory."""

    temporary = destination.with_name(
        f".{destination.name}.installing-{uuid.uuid4().hex[:8]}"
    )
    try:
        shutil.copytree(
            SOURCE_DIR,
            temporary,
            symlinks=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
        )
        temporary.replace(destination)
    finally:
        if path_exists(temporary):
            remove_path(temporary)


def install_symlink(destination: Path) -> None:
    """Create a directory symlink to the repository Skill source."""

    try:
        destination.symlink_to(SOURCE_DIR.resolve(), target_is_directory=True)
    except OSError as exc:
        if os.name == "nt":
            raise InstallError(
                "Windows 创建符号链接失败。请启用开发者模式/管理员权限，"
                "或去掉 --symlink 使用默认复制安装。"
            ) from exc
        raise


def install(destination: Path, *, symlink: bool, force: bool) -> Path | None:
    """Install to destination and return the backup path, if one was made."""

    validate_source(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    backup: Path | None = None
    if path_exists(destination):
        if not force:
            raise InstallError(
                f"目标已存在：{destination}\n"
                "为保护现有安装，本次未做任何修改。确认替换时请加 --force。"
            )
        backup = backup_path_for(destination)
        destination.replace(backup)

    try:
        if symlink:
            install_symlink(destination)
        else:
            install_copy(destination)
    except Exception:
        if path_exists(destination):
            remove_path(destination)
        if backup is not None and path_exists(backup):
            backup.replace(destination)
        raise

    return backup


def uninstall(destination: Path) -> Path:
    """Move an installation to a recoverable timestamped backup."""

    validate_source(destination)
    if not path_exists(destination):
        raise InstallError(f"未找到安装：{destination}")
    # A broken development symlink is still safe to move because only the link
    # itself is renamed. For a real directory, require the Codex Skill marker
    # so a mistyped --target cannot relocate an unrelated folder.
    if not destination.is_symlink():
        marker = destination / "SKILL.md"
        if not marker.is_file():
            raise InstallError(
                f"拒绝卸载非 Skill 目录：{destination}（缺少 SKILL.md）。"
            )
        try:
            marker_text = marker.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise InstallError(f"无法读取 Skill 标记：{marker}") from exc
        if not any(
            line.strip() == f"name: {SKILL_NAME}"
            for line in marker_text.splitlines()[:20]
        ):
            raise InstallError(
                f"拒绝卸载非 {SKILL_NAME} Skill 目录：{destination}。"
            )
    backup = backup_path_for(destination)
    destination.replace(backup)
    return backup


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="安装本仓库的 Codex PPT Master Skill。"
    )
    location = parser.add_mutually_exclusive_group()
    location.add_argument(
        "--project",
        type=Path,
        metavar="REPO",
        help="安装到 REPO/.agents/skills/ppt-master。",
    )
    location.add_argument(
        "--target",
        type=Path,
        metavar="DIR",
        help="安装到明确指定、且名称为 ppt-master 的目录；高级用法。",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--copy",
        action="store_true",
        help="复制安装（默认，适合日常使用）。",
    )
    mode.add_argument(
        "--symlink",
        action="store_true",
        help="符号链接安装（适合开发，仓库改动会立即生效）。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="替换已有目标；替换前自动创建同级时间戳备份。",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="卸载并把当前安装移动到同级时间戳备份。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        destination = resolve_destination(args)
        if args.uninstall:
            backup = uninstall(destination)
            print(f"已卸载：{destination}")
            print(f"可恢复备份：{backup}")
            return 0

        backup = install(destination, symlink=args.symlink, force=args.force)
    except InstallError as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"安装失败：{exc}", file=sys.stderr)
        return 1

    mode = "符号链接" if args.symlink else "复制"
    print(f"安装成功（{mode}）：{destination}")
    if backup is not None:
        print(f"原安装备份：{backup}")
    print("请重新加载 Codex，然后在请求中显式写出 $ppt-master。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
