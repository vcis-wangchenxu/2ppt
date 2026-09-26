#!/usr/bin/env python3
"""Diagnose the Codex-native PPT Master runtime."""
from __future__ import annotations
import argparse,importlib,importlib.metadata,json,platform,shutil,sys
from pathlib import Path
from typing import Any
MINIMUM_PYTHON=(3,10)
CORE=[("python-pptx","pptx"),("Pillow","PIL"),("PyYAML","yaml")]
CAPABILITIES={"native_drawingml":[("XlsxWriter","xlsxwriter"),("skia-pathops","pathops"),("uharfbuzz","uharfbuzz")],"source_conversion":[("PyMuPDF","fitz"),("mammoth","mammoth"),("markdownify","markdownify"),("ebooklib","ebooklib"),("nbconvert","nbconvert"),("openpyxl","openpyxl"),("requests","requests"),("beautifulsoup4","bs4"),("curl_cffi","curl_cffi")],"image_processing":[("numpy","numpy"),("google-genai","google.genai")],"narration":[("edge-tts","edge_tts")],"live_preview":[("flask","flask")]}
def dep(dist:str,mod:str)->dict[str,Any]:
    try: version=importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError: version=None
    error=None; ok=False
    try: importlib.import_module(mod); ok=True
    except Exception as exc: error=f"{type(exc).__name__}: {exc}"
    return {"name":dist,"import":mod,"version":version,"available":bool(version and ok),"error":error}
def collect_diagnostics()->dict[str,Any]:
    pyok=sys.version_info>=MINIMUM_PYTHON; core=[dep(*x) for x in CORE]; caps={k:[dep(*x) for x in v] for k,v in CAPABILITIES.items()}
    tools=[]
    for name,purpose in (("libreoffice","PPTX render/compat"),("soffice","LibreOffice CLI"),("pdftoppm","PDF render"),("ffmpeg","audio/video"),("pandoc","fallback conversion")):
        loc=shutil.which(name); tools.append({"name":name,"available":loc is not None,"path":str(Path(loc).resolve()) if loc else None,"required":False,"purpose":purpose})
    return {"ok":pyok and all(x["available"] for x in core),"python":{"version":platform.python_version(),"minimum":".".join(map(str,MINIMUM_PYTHON)),"ok":pyok,"executable":str(Path(sys.executable).resolve()),"implementation":platform.python_implementation()},"required_dependencies":core,"capabilities":{k:{"available":all(x["available"] for x in v),"dependencies":v} for k,v in caps.items()},"optional_tools":tools,"platform":{"system":platform.system(),"release":platform.release(),"machine":platform.machine()}}
def main(argv:list[str]|None=None)->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--json",action="store_true"); a=ap.parse_args(); r=collect_diagnostics()
    if a.json: print(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True))
    else:
        print(f"ppt-master core: {'OK' if r['ok'] else 'NOT READY'}")
        for x in r["required_dependencies"]: print(f"{'OK' if x['available'] else 'MISS'} {x['name']} {x['version'] or ''}")
        for k,v in r["capabilities"].items(): print(f"{'OK' if v['available'] else 'PARTIAL'} capability:{k}")
    return 0 if r["ok"] else 1
if __name__=="__main__": raise SystemExit(main())
