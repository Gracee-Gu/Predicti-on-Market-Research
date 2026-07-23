from __future__ import annotations
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs/stage5'; PAPER=ROOT/'paper/manuscript_stage5.md'
SECRETS=[re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
CAUSAL=[' causes ',' caused ',' leads to ',' produces ',' effect of ',' demonstrates that ',' proves that ']
REQ=['Abstract','Introduction','Theory and Hypotheses','Data and Methods','Results','Discussion','Limitations','Conclusion','Reproducibility Statement']
EXCLUDED_PARTS={'.git','.venv','venv','__pycache__','.pytest_cache','.ruff_cache','.mypy_cache'}

def find_secret_hits(root: Path):
    hits=[]
    for p in root.rglob('*'):
        if not p.is_file() or any(part in EXCLUDED_PARTS for part in p.parts): continue
        if p.stat().st_size>2_000_000: continue
        try: s=p.read_text(encoding='utf-8')
        except Exception: continue
        if any(r.search(s) for r in SECRETS): hits.append(str(p.relative_to(root)))
    return hits

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    audit=json.loads((OUT/'stage5_input_audit.json').read_text()) if (OUT/'stage5_input_audit.json').exists() else {}
    status=audit.get('stage4_claim_status','blocked')
    text=PAPER.read_text(encoding='utf-8') if PAPER.exists() else ''
    missing=[s for s in REQ if f'## {s}' not in text]
    causal=[]
    if status!='confirmatory_ready':
        low=' '+text.lower()+' '
        causal=[t.strip() for t in CAUSAL if t in low]
    secret_hits=find_secret_hits(ROOT)
    required=[OUT/'claim_evidence_ledger.csv',OUT/'reproducibility_manifest.json',OUT/'manuscript_build.json',PAPER]
    missing_files=[str(p.relative_to(ROOT)) for p in required if not p.exists()]
    report={'stage':5,'claim_status':status,'implementation_status':'PASS' if not (missing or missing_files or causal or secret_hits) else 'INCOMPLETE',
            'missing_sections':missing,'missing_files':missing_files,'causal_language_violations':causal,'secret_hits':secret_hits,
            'publication_status':'ready_for_human_review' if not (missing or missing_files or causal or secret_hits) else 'not_ready'}
    (OUT/'stage5_release_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
