from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))

import install as installer  # noqa: E402


class InstallerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="ppt-master-install-test-")
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(REPOSITORY / "install.py"), *args],
            cwd=REPOSITORY,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_copy_replace_and_recoverable_uninstall(self) -> None:
        target = self.root / "installed" / "ppt-master"
        first = self.run_installer("--target", str(target))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue((target / "SKILL.md").is_file())

        refused = self.run_installer("--target", str(target))
        self.assertEqual(refused.returncode, 2)
        self.assertTrue((target / "SKILL.md").is_file())

        replaced = self.run_installer("--target", str(target), "--force")
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        backups = sorted(target.parent.glob("ppt-master.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue((backups[0] / "SKILL.md").is_file())

        removed = self.run_installer("--target", str(target), "--uninstall")
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertFalse(target.exists())
        self.assertEqual(len(list(target.parent.glob("ppt-master.backup-*"))), 2)

    def test_rejects_destinations_that_overlap_source(self) -> None:
        source = installer.SOURCE_DIR.resolve()
        with self.assertRaises(installer.InstallError):
            installer.validate_source(source / "nested")
        with self.assertRaises(installer.InstallError):
            installer.validate_source(source.parent)
        with self.assertRaises(installer.InstallError):
            installer.uninstall(source)
        self.assertTrue((source / "SKILL.md").is_file())

        linked_parent = self.root / "linked-source"
        try:
            linked_parent.symlink_to(source, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"当前平台无法创建测试符号链接：{exc}")
        with self.assertRaises(installer.InstallError):
            installer.validate_source(linked_parent / "nested")

        case_alias = source.parent / source.name.upper()
        try:
            aliases_source = case_alias.exists() and case_alias.samefile(source)
        except OSError:
            aliases_source = False
        if aliases_source:
            with self.assertRaises(installer.InstallError):
                installer.validate_source(case_alias / "nested")

    def test_rejects_unsafe_target_name_and_unrelated_uninstall(self) -> None:
        wrong_name = self.root / "whole-project"
        refused_name = self.run_installer("--target", str(wrong_name))
        self.assertEqual(refused_name.returncode, 2)
        self.assertFalse(wrong_name.exists())

        unrelated = self.root / "unrelated" / "ppt-master"
        unrelated.mkdir(parents=True)
        sentinel = unrelated / "keep.txt"
        sentinel.write_text("do not move", encoding="utf-8")
        refused_uninstall = self.run_installer(
            "--target", str(unrelated), "--uninstall"
        )
        self.assertEqual(refused_uninstall.returncode, 2)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not move")
        self.assertEqual(list(unrelated.parent.glob("ppt-master.backup-*")), [])


if __name__ == "__main__":
    unittest.main()
