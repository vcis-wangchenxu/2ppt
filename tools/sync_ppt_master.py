#!/usr/bin/env python3
"""Vendor the audited PPT Master core into the Codex-native 2ppt skill."""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

UPSTREAM_VERSION="v6.6.0"
SKILL_REL=Path("skills/ppt-master")
PROTECTED={"SKILL.md","agents/openai.yaml","references/codex-runtime.md","references/deck-spec.md","references/project-contract.md","references/quality-gates.md","references/routing.md","references/upstream.md","scripts/attribution_guard.py","scripts/build_deck.py","scripts/console_encoding.py","scripts/doctor.py","scripts/init_project.py","scripts/inspect_pptx.py","scripts/run-python.sh","scripts/runtime_common.py","scripts/smoke_test.py","scripts/validate_pptx.py","scripts/verify_attribution.py","LICENSE"}
TEMPLATE_DIRS={"schemas","scaffolds","charts","tables","styles","layouts","decks"}
TEMPLATE_ROOT_FILES={"README.md","VISUALIZATION_TEMPLATE_AUTHORING.md","design_spec_reference.md","spec_lock_reference.md"}

def selected(rel:Path)->bool:
    p=rel.as_posix()
    if p in PROTECTED: return False
    if p=="requirements.txt": return True
    if p.startswith("workflows/"): return True
    if p.startswith("references/"): return not p.startswith("references/ai-image-comparison/")
    if p.startswith("scripts/"):
        if p.startswith("scripts/tests/"): return False
        return p != "scripts/update_repo.py"
    if p.startswith("templates/"):
        parts=rel.parts
        if len(parts)==2 and parts[1] in TEMPLATE_ROOT_FILES: return True
        return len(parts)>=2 and parts[1] in TEMPLATE_DIRS
    return False

def head(root:Path)->str:
    try: return subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()
    except Exception: return "unknown"

def old_manifest(target:Path)->list[str]:
    p=target/"UPSTREAM_MANIFEST.json"
    if not p.is_file(): return []
    try: return [x for x in json.loads(p.read_text(encoding="utf-8")).get("files",[]) if isinstance(x,str)]
    except Exception: return []

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream-root",type=Path,required=True)
    ap.add_argument("--repo-root",type=Path,required=True)
    ap.add_argument("--version",default=UPSTREAM_VERSION)
    a=ap.parse_args()
    source=a.upstream_root.resolve()/SKILL_REL; target=a.repo_root.resolve()/SKILL_REL
    if not (source/"SKILL.md").is_file(): raise SystemExit(f"invalid upstream skill root: {source}")
    if not (target/"SKILL.md").is_file(): raise SystemExit(f"invalid target skill root: {target}")
    files=sorted((p.relative_to(source) for p in source.rglob("*") if p.is_file() and selected(p.relative_to(source))),key=lambda p:p.as_posix())
    keep={p.as_posix() for p in files}
    for old in old_manifest(target):
        if old in keep or old in PROTECTED: continue
        v=target/old
        if v.is_file() or v.is_symlink(): v.unlink()
    total=0
    for rel in files:
        s,d=source/rel,target/rel
        d.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(s,d); total+=s.stat().st_size
    manifest={"schema":"2ppt.upstream-manifest.v1","upstream_repository":"https://github.com/hugohe3/ppt-master","upstream_version":a.version,"upstream_commit":head(a.upstream_root.resolve()),"files":[p.as_posix() for p in files],"file_count":len(files),"bytes":total,"omitted":["references/ai-image-comparison","templates/brands","templates/icons","templates/sounds","scripts/tests"]}
    (target/"UPSTREAM_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__": raise SystemExit(main())
