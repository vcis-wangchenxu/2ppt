#!/usr/bin/env python3
"""Verify retained upstream attribution for the Codex adaptation."""
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path
from typing import Any
UPSTREAM_URL="https://github.com/hugohe3/ppt-master"; ADAPTATION_URL="https://github.com/vcis-wangchenxu/2ppt"; BASELINE_COMMIT="ce92fb43e4ade9c701f4c869e286f13fce743c72"
def verify(skill_root:Path)->dict[str,Any]:
    root=skill_root.expanduser().resolve(); checks=[]
    def add(i,ok,msg,p): checks.append({"id":i,"ok":bool(ok),"message":msg,"path":str(p)})
    lp=root/"LICENSE"; up=root/"references"/"upstream.md"; lt=lp.read_text(encoding="utf-8") if lp.is_file() else ""; ut=up.read_text(encoding="utf-8") if up.is_file() else ""
    add("license.exists",lp.is_file(),"Skill contains LICENSE",lp); add("license.mit","MIT License" in lt and "Permission is hereby granted" in lt,"MIT license retained",lp); add("license.hugo",re.search(r"Copyright[^\n]*Hugo He",lt,re.I) is not None,"Hugo He copyright retained",lp); add("upstream.exists",up.is_file(),"upstream note exists",up); add("upstream.repo",UPSTREAM_URL in ut,"upstream URL retained",up); add("upstream.commit",BASELINE_COMMIT in ut,"v6.9.0 audited commit pinned",up); add("upstream.author","Hugo He" in ut,"upstream author retained",up); add("upstream.license",re.search(r"(?:许可证|license)[^\n]*MIT",ut,re.I) is not None,"upstream MIT noted",up); add("adaptation.repo",ADAPTATION_URL in ut,"adaptation repo noted",up)
    mp = root / "UPSTREAM_MANIFEST.json"
    try:
        manifest = json.loads(mp.read_text(encoding="utf-8"))
        add("manifest.commit", manifest["upstream_commit"] == BASELINE_COMMIT, "Manifest matches audited commit", mp)
        add("manifest.version", manifest["upstream_version"] == "v6.9.0", "Manifest matches audited release", mp)
        paths = manifest["files"]
        hashes = manifest["sha256"]
        valid = len(paths) == manifest["file_count"] and set(paths) == set(hashes)
        mismatches = []
        for rel in paths:
            path = (root / rel).resolve()
            if not path.is_relative_to(root) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != hashes[rel]:
                mismatches.append(rel)
        add("manifest.files", valid and not mismatches, f"Vendored file hashes verified ({len(paths)} files); mismatches: {mismatches[:5]}", mp)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        add("manifest.readable", False, f"Invalid upstream manifest: {exc}", mp)
    failures=[x for x in checks if not x["ok"]]; return {"ok":not failures,"skill_root":str(root),"checks":checks,"failures":len(failures)}
def main(argv:list[str]|None=None)->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--skill-root",type=Path,default=Path(__file__).resolve().parent.parent); ap.add_argument("--json",action="store_true"); a=ap.parse_args(); r=verify(a.skill_root)
    if a.json: print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True))
    else:
        print(f"attribution: {'OK' if r['ok'] else 'FAIL'}")
        for x in r["checks"]: print(f"{'OK' if x['ok'] else 'FAIL'} {x['message']}")
    return 0 if r["ok"] else 1
if __name__=="__main__": raise SystemExit(main())
