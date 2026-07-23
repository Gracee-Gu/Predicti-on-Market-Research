from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    required=["input_audit.json","corpus_profile.json","analysis_build.json","tables/bivariate_effects.csv","model_results.json","stage4_report.md"]
    missing=[x for x in required if not (ROOT/"outputs/stage4"/x).exists()]
    report={"stage":4,"implementation_status":"PASS" if not missing else "INCOMPLETE","missing_outputs":missing}
    audit=ROOT/"outputs/stage4/input_audit.json"
    if audit.exists(): report["empirical_status"]=json.loads(audit.read_text()).get("claim_status")
    (ROOT/"outputs/stage4/stage4_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
