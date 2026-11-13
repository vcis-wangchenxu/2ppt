#!/usr/bin/env python3
"""Vendor the pinned PPT Master core without replacing the Codex control layer."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

UPSTREAM_VERSION = "v6.9.0"
UPSTREAM_COMMIT = "ce92fb43e4ade9c701f4c869e286f13fce743c72"
RELEASE_SHA256 = "5ac7bf511b1bbaf3809b9fb3d8465918f79ca39b5451203c9eb9e08763acd873"
SKILL_REL = Path("skills/ppt-master")
PROTECTED = {
    "SKILL.md", "agents/openai.yaml", "references/codex-runtime.md",
    "references/deck-spec.md", "references/project-contract.md",
    "references/quality-gates.md", "references/routing.md", "references/upstream.md",
    "scripts/attribution_guard.py", "scripts/build_deck.py", "scripts/console_encoding.py",
    "scripts/doctor.py", "scripts/init_project.py", "scripts/inspect_pptx.py",
    "scripts/run-python.sh", "scripts/run-python.ps1", "scripts/runtime_common.py",
    "scripts/smoke_test.py", "scripts/validate_pptx.py", "scripts/verify_attribution.py",
    "LICENSE",
}
TEMPLATE_DIRS = {"schemas", "scaffolds", "charts", "tables", "styles", "layouts", "decks"}
TEMPLATE_ROOT_FILES = {
    "README.md", "VISUALIZATION_TEMPLATE_AUTHORING.md",
    "design_spec_reference.md", "spec_lock_reference.md",
}


def selected(rel: Path) -> bool:
    if rel.is_absolute() or any(p in {"..", ".git", ".venv", "__pycache__"} for p in rel.parts):
        return False
    p = rel.as_posix()
    if p in PROTECTED or rel.suffix in {".pyc", ".pyo"}:
        return False
    if p == "requirements.txt" or p.startswith("workflows/"):
        return True
    if p.startswith("references/"):
        return not p.startswith("references/ai-image-comparison/")
    if p.startswith("scripts/"):
        return not p.startswith("scripts/tests/") and p != "scripts/update_repo.py"
    if p.startswith("templates/"):
        return (len(rel.parts) == 2 and rel.name in TEMPLATE_ROOT_FILES) or rel.parts[1] in TEMPLATE_DIRS
    return False


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_target(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts:
        raise ValueError(f"Unsafe manifest path: {relative}")
    path = root / rel
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Manifest path escapes skill: {relative}")
    return path


def sync(source: Path, target: Path) -> dict:
    if not (source / "SKILL.md").is_file() or not (target / "SKILL.md").is_file():
        raise ValueError("Both source and target must contain SKILL.md")
    if source.resolve() == target.resolve():
        raise ValueError("Source and target must be different")
    files = sorted(
        (p.relative_to(source) for p in source.rglob("*") if p.is_file() and selected(p.relative_to(source))),
        key=lambda p: p.as_posix(),
    )
    keep = {p.as_posix() for p in files}
    manifest_path = target / "UPSTREAM_MANIFEST.json"
    old_files = json.loads(manifest_path.read_text(encoding="utf-8"))["files"] if manifest_path.exists() else []
    # Validate the entire deletion plan before changing the installed subset.
    stale = [checked_target(target, p) for p in old_files if p not in keep and p not in PROTECTED]
    destinations = [checked_target(target, p.as_posix()) for p in files]
    for path in stale:
        if path.is_file():
            path.unlink()
    hashes = {}
    total = 0
    for rel, destination in zip(files, destinations):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / rel, destination)
        hashes[rel.as_posix()] = sha256(destination)
        total += destination.stat().st_size
    manifest = {
        "schema": "2ppt.upstream-manifest.v1",
        "upstream_repository": "https://github.com/hugohe3/ppt-master",
        "upstream_version": UPSTREAM_VERSION,
        "upstream_commit": UPSTREAM_COMMIT,
        "files": sorted(keep), "file_count": len(files), "bytes": total,
        "sha256": hashes,
        "omitted": ["references/ai-image-comparison", "templates/brands", "templates/icons", "templates/sounds", "scripts/tests"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return manifest


def extract_release(archive: Path, destination: Path) -> Path:
    if sha256(archive) != RELEASE_SHA256:
        raise ValueError("Release archive SHA-256 does not match the audited release")
    prefix = "ppt-master/skills/ppt-master/"
    with zipfile.ZipFile(archive) as bundle:
        for info in bundle.infolist():
            if not info.filename.startswith(prefix) or info.is_dir():
                continue
            rel = Path(info.filename[len(prefix):])
            if rel.as_posix() != "SKILL.md" and not selected(rel):
                continue
            output = checked_target(destination, rel.as_posix())
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(bundle.read(info))
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--upstream-root", type=Path)
    source.add_argument("--upstream-archive", type=Path, help="Official release ZIP; verified by SHA-256")
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--version", choices=[UPSTREAM_VERSION], default=UPSTREAM_VERSION)
    args = parser.parse_args()
    target = args.repo_root.resolve() / SKILL_REL
    try:
        if args.upstream_archive:
            with tempfile.TemporaryDirectory(prefix="ppt-master-sync-") as temporary:
                root = extract_release(args.upstream_archive, Path(temporary))
                manifest = sync(root, target)
        else:
            root = args.upstream_root.resolve()
            commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            if commit != UPSTREAM_COMMIT:
                raise ValueError(f"Expected upstream {UPSTREAM_COMMIT}, got {commit}")
            dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--", str(SKILL_REL)], text=True)
            if dirty.strip():
                raise ValueError("Upstream skill checkout has local changes")
            manifest = sync(root / SKILL_REL, target)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(2, f"Sync failed: {exc}\n")
    print(json.dumps({k: manifest[k] for k in ("upstream_version", "upstream_commit", "file_count", "bytes")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
