from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs/stage5'
EXCLUDED={'.git','.venv','venv','__pycache__'}

def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    records=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or any(x in EXCLUDED for x in p.parts): continue
        rel=p.relative_to(ROOT)
        if str(rel).startswith('outputs/stage5/reproducibility_manifest'): continue
        records.append({'path':str(rel),'bytes':p.stat().st_size,'sha256':digest(p)})
    obj={'stage':5,'algorithm':'sha256','file_count':len(records),'files':records}
    (OUT/'reproducibility_manifest.json').write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
    print(OUT/'reproducibility_manifest.json')
if __name__=='__main__': main()
