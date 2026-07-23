from __future__ import annotations
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'outputs/stage5'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    audit=json.loads((OUT/'stage5_input_audit.json').read_text()) if (OUT/'stage5_input_audit.json').exists() else {}
    status=audit.get('stage4_claim_status','blocked')
    rows=[
      ['Introduction','Prediction-market prices acquire public meaning through platform and media presentation.','theory_source','paper/literature_review.md',status,'review_required'],
      ['Methods','Articles are linked to markets using explicit matching statuses and publication-time rules.','design_record','docs/corpus_protocol.md',status,'ready'],
      ['Methods','Framing and overreach constructs follow the Stage 3 codebook.','design_record','docs/stage3_codebook.md',status,'ready'],
      ['Results','Corpus diagnostics and associations are reproduced from Stage 4 outputs.','empirical_output','outputs/stage4/stage4_report.md',status,'ready' if status!='blocked' else 'descriptive_only'],
      ['Discussion','Observed associations do not establish causal effects.','interpretive_inference','docs/stage4_claim_policy.md',status,'ready'],
    ]
    p=OUT/'claim_evidence_ledger.csv'
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['section','claim','support_type','support_path','claim_status','publication_status']); w.writerows(rows)
    print(p)
if __name__=='__main__': main()
