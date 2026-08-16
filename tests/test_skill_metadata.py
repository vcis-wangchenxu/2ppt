from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY / "skills" / "ppt-master"


class SkillMetadataTestCase(unittest.TestCase):
    def test_skill_frontmatter_matches_codex_contract(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", content, flags=re.DOTALL)
        self.assertIsNotNone(match, "SKILL.md 缺少完整 YAML frontmatter")
        assert match is not None
        fields: dict[str, str] = {}
        for line in match.group(1).splitlines():
            key, separator, value = line.partition(":")
            self.assertEqual(separator, ":", f"frontmatter 行格式错误：{line}")
            fields[key.strip()] = value.strip()
        self.assertEqual(set(fields), {"name", "description"})
        self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertEqual(fields["name"], "ppt-master")
        description = json.loads(fields["description"])
        self.assertIsInstance(description, str)
        self.assertTrue(description.strip())
        self.assertLessEqual(len(description), 1024)
        self.assertNotRegex(description, r"[<>]")
        self.assertIn("$ppt-master", description)

    def test_openai_metadata_requires_explicit_invocation(self) -> None:
        content = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(content, r"(?m)^interface:\s*$")
        self.assertRegex(content, r"(?m)^policy:\s*$")
        self.assertRegex(content, r"(?m)^\s+allow_implicit_invocation:\s+false\s*$")
        prompt_match = re.search(r'(?m)^\s+default_prompt:\s+(".*")\s*$', content)
        self.assertIsNotNone(prompt_match)
        assert prompt_match is not None
        self.assertIn("$ppt-master", json.loads(prompt_match.group(1)))

    def test_local_markdown_links_resolve(self) -> None:
        failures: list[str] = []
        markdown_files = [
            *REPOSITORY.glob("*.md"),
            *SKILL_ROOT.rglob("*.md"),
        ]
        for markdown in markdown_files:
            content = markdown.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                clean = target.split("#", 1)[0]
                if not clean or re.match(r"^[a-z]+://", clean):
                    continue
                if not (markdown.parent / clean).resolve().exists():
                    failures.append(f"{markdown.relative_to(REPOSITORY)} -> {target}")
        self.assertEqual(failures, [])


if __name__ == "__main__":
    unittest.main()
