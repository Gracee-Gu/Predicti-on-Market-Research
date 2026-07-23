from __future__ import annotations
import json
from pathlib import Path
import _stage4_bootstrap  # noqa: F401
from pmresearch.stage4.core import audit_rows, find_input, read_csv, write_json

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ["data/analysis/article_market_dataset.csv", "data/stage3/article_market_dataset.csv"]
GATES = {"minimum_n": 80, "minimum_source_types": 2, "maximum_single_source_share": .85,
         "minimum_quality_coverage": .50, "require_human_adjudication_for_confirmatory": True}

def main() -> None:
    source = find_input(ROOT, CANDIDATES)
    report = audit_rows(read_csv(source), GATES)
    report["input_path"] = str(source.relative_to(ROOT))
    write_json(ROOT / "outputs/stage4/input_audit.json", report)
    print(json.dumps(report, indent=2))
if __name__ == "__main__": main()
