from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/stage5'

def load_json(path: Path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    candidates=[ROOT/'outputs/stage4/input_audit.json',ROOT/'outputs/stage4/stage4_audit.json']
    selected=next((p for p in candidates if p.exists()),None)
    status='blocked'; source=None
    if selected:
        obj=load_json(selected)
        status=obj.get('claim_status') or obj.get('empirical_status') or 'blocked'
        source=str(selected.relative_to(ROOT))
    required=[
        ROOT/'outputs/stage4/stage4_report.md',
        ROOT/'outputs/stage4/model_results.json',
        ROOT/'outputs/stage4/tables/bivariate_effects.csv',
    ]
    report={'stage':5,'stage4_claim_status':status,'claim_status_source':source,
            'missing_stage4_outputs':[str(p.relative_to(ROOT)) for p in required if not p.exists()],
            'implementation_ready': selected is not None}
    (OUT/'stage5_input_audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
