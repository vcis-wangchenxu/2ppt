"""Verify argument fidelity and child exit codes in the host's launcher."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/ppt-master/scripts"


class LauncherTests(unittest.TestCase):
    def launcher(self):
        if os.name == "nt":
            shell = shutil.which("pwsh") or shutil.which("powershell")
            self.assertIsNotNone(shell, "Windows CI must provide PowerShell")
            return [shell, "-NoProfile", "-NonInteractive", "-File", str(SCRIPTS / "run-python.ps1")]
        return ["sh", str(SCRIPTS / "run-python.sh")]

    def test_unicode_paths_arguments_and_exit_code(self):
        with tempfile.TemporaryDirectory(prefix="runner test ") as directory:
            script = Path(directory) / "参数 test.py"
            script.write_text(
                'import json, sys\nprint(json.dumps(sys.argv[1:], ensure_ascii=False))\nraise SystemExit(7)\n',
                encoding="utf-8",
            )
            args = ["中文 and spaces", "--literal", "a&b", "value=hello world"]
            result = subprocess.run(
                [*self.launcher(), str(script), *args], cwd=directory,
                capture_output=True, encoding="utf-8", timeout=30,
                env={**os.environ, "PPT_MASTER_PYTHON": sys.executable},
            )
            self.assertEqual(result.returncode, 7, result.stderr)
            self.assertEqual(json.loads(result.stdout), args)

    def test_invalid_explicit_interpreter_fails(self):
        result = subprocess.run(
            [*self.launcher(), "-c", "raise SystemExit(0)"],
            capture_output=True, encoding="utf-8", timeout=30,
            env={**os.environ, "PPT_MASTER_PYTHON": str(SCRIPTS / "missing-python")},
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
