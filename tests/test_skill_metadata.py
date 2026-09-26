from __future__ import annotations
import json,re,unittest
from pathlib import Path
REPOSITORY=Path(__file__).resolve().parents[1]
SKILL_ROOT=REPOSITORY/"skills"/"ppt-master"
class SkillMetadataTestCase(unittest.TestCase):
    def test_skill_frontmatter_matches_codex_contract(self):
        content=(SKILL_ROOT/"SKILL.md").read_text(encoding="utf-8")
        match=re.match(r"^---\n(.*?)\n---\n",content,flags=re.DOTALL); self.assertIsNotNone(match)
        fields={}
        for line in match.group(1).splitlines():
            key,sep,value=line.partition(":"); self.assertEqual(sep,":"); fields[key.strip()]=value.strip()
        self.assertEqual(set(fields),{"name","description"}); self.assertEqual(fields["name"],"ppt-master")
        description=json.loads(fields["description"]); self.assertIn("$ppt-master",description); self.assertLessEqual(len(description),1024)
    def test_openai_metadata_requires_explicit_invocation(self):
        content=(SKILL_ROOT/"agents"/"openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(content,r"(?m)^policy:\s*$"); self.assertRegex(content,r"(?m)^\s+allow_implicit_invocation:\s+false\s*$"); self.assertIn("$ppt-master",content)
    def test_three_route_contract(self):
        content=(SKILL_ROOT/"SKILL.md").read_text(encoding="utf-8")
        for term in ("Generate PPTX","Create Template","Edit Native PPTX"): self.assertIn(term,content)
    def test_local_runtime_links_resolve(self):
        ignored=("references/ai-image-comparison/","templates/brands/","templates/icons/","templates/sounds/","scripts/tests/")
        failures=[]
        for mdfile in [*REPOSITORY.glob("*.md"),*SKILL_ROOT.rglob("*.md")]:
            content=mdfile.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)",content):
                clean=target.split("#",1)[0]
                if not clean or re.match(r"^[a-z]+://",clean): continue
                resolved=(mdfile.parent/clean).resolve()
                try: rel=resolved.relative_to(SKILL_ROOT.resolve()).as_posix()
                except ValueError:
                    if str(mdfile.resolve()).startswith(str(SKILL_ROOT.resolve())): continue
                    rel=""
                normalized_target=(Path(rel).as_posix() if rel else clean).lstrip("./")
                if any(normalized_target.startswith(x) or f"/{x}" in normalized_target for x in ignored): continue
                if any(part in {"brands","icons","sounds","ai-image-comparison"} for part in Path(clean).parts): continue
                if not resolved.exists(): failures.append(f"{mdfile.relative_to(REPOSITORY)} -> {target}")
        self.assertEqual(failures,[])
if __name__=="__main__": unittest.main()
