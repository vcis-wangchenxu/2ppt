"""Check that repeatable upstream updates preserve the Codex control layer."""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))
from tools import sync_ppt_master as syncer


class SyncTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ppt-sync-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        for path in (self.source, self.target):
            path.mkdir()
            (path / "SKILL.md").write_text("control", encoding="utf-8")

    def test_repeatable_sync_preserves_control_and_removes_only_stale_files(self):
        for rel in ("scripts/new.py", "scripts/run-python.ps1", "scripts/tests/omit.py", "templates/icons/omit.svg"):
            path = self.source / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("upstream", encoding="utf-8")
        (self.target / "scripts").mkdir()
        (self.target / "scripts/run-python.ps1").write_text("local", encoding="utf-8")
        stale = self.target / "scripts/old.py"
        stale.write_text("old", encoding="utf-8")
        marker = self.target / "UPSTREAM_MANIFEST.json"
        marker.write_text(json.dumps({"files": ["scripts/old.py"]}), encoding="utf-8")
        first = syncer.sync(self.source, self.target)
        self.assertFalse(stale.exists())
        self.assertEqual(first["files"], ["scripts/new.py"])
        self.assertEqual((self.target / "scripts/run-python.ps1").read_text(), "local")
        self.assertEqual((self.target / "SKILL.md").read_text(), "control")
        self.assertEqual(first["sha256"]["scripts/new.py"], hashlib.sha256(b"upstream").hexdigest())
        serialized = marker.read_bytes()
        self.assertEqual(syncer.sync(self.source, self.target), first)
        self.assertEqual(marker.read_bytes(), serialized)

    def test_manifest_escape_is_rejected_without_deleting_files(self):
        sentinel = self.root / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        (self.target / "UPSTREAM_MANIFEST.json").write_text(json.dumps({"files": ["../keep.txt"]}), encoding="utf-8")
        with self.assertRaises(ValueError):
            syncer.sync(self.source, self.target)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_unverified_archive_is_rejected_before_extraction(self):
        archive = self.root / "release.zip"
        archive.write_bytes(b"not the pinned release")
        output = self.root / "extracted"
        with self.assertRaises(ValueError):
            syncer.extract_release(archive, output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
