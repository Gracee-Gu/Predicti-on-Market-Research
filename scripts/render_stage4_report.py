from __future__ import annotations
import csv, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load_json(p): return json.loads(p.read_text()) if p.exists() else {}
def main():
    out=ROOT/"outputs/stage4"; audit=load_json(out/"input_audit.json"); profile=load_json(out/"corpus_profile.json"); models=load_json(out/"model_results.json")
    effects=[]
    p=out/"tables/bivariate_effects.csv"
    if p.exists():
        with p.open(newline="",encoding="utf-8") as f: effects=list(csv.DictReader(f))
    lines=["# Stage 4 Analysis Report", "", f"**Claim status:** `{audit.get('claim_status','not audited')}`", "", "## Corpus diagnostics", "", f"- N: {profile.get('n','NA')}", f"- Source types: {profile.get('source_type',{})}", f"- Market-quality coverage: {audit.get('quality_coverage','NA')}", f"- Human adjudication evidence: {audit.get('human_adjudication_evidence','NA')}", "", "## Bivariate associations", ""]
    for r in effects: lines.append(f"- {r['predictor']}: mean difference {r['difference']} (95% CI {r['ci95_low']}, {r['ci95_high']})")
    lines += ["", "## Multivariable models", "", f"Model registry output: `{models.get('models',{})}`", "", "## Interpretation boundary", "", "Results may be described only at the claim level permitted by the input audit. Failed gates must be reported alongside estimates."]
    (out/"stage4_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(out/"stage4_report.md")
if __name__=="__main__": main()
