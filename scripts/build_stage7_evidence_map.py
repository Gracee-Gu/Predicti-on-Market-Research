from __future__ import annotations

import csv
import json
from pathlib import Path

from _stage7_common import ROOT, OUT, read_json

ROWS = [
    {
        "research_question": "RQ1",
        "question": "How do platforms and media translate market prices into probability, public sentiment, or objective information?",
        "required_evidence": "Multi-source computational content analysis with validated framing measures.",
        "minimum_comparison": "platform_owned vs independent_media; preferably partner_media and regulatory_critical.",
        "result_family": "frame prevalence, co-occurrence, effect sizes, adjusted source comparisons.",
    },
    {
        "research_question": "RQ2",
        "question": "Does authoritative representation match underlying market quality?",
        "required_evidence": "Publication-aligned volume, trade frequency, spread, volatility/stability, and available depth.",
        "minimum_comparison": "authority/representation framing linked to raw market-quality metrics.",
        "result_family": "metric-specific associations, sensitivity analysis, case-level evidence.",
    },
    {
        "research_question": "RQ3_optional",
        "question": "Do media citations coincide with changes in trading activity or prices?",
        "required_evidence": "Verified publication timestamps and sufficiently granular market time series.",
        "minimum_comparison": "pre/post windows with justified baselines and controls.",
        "result_family": "associational event-window estimates only.",
    },
]

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    audit = read_json(OUT / "alignment_audit.json")
    failed = set(audit.get("failed_checks", []))

    with (OUT / "research_question_evidence_map.csv").open("w", encoding="utf-8", newline="") as f:
        fields = list(ROWS[0]) + ["current_status", "blocking_gates"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in ROWS:
            if row["research_question"] == "RQ1":
                blockers = sorted(failed & {"source_type_diversity", "required_source_counts", "human_audited_units", "reliability_fields_reported"})
            elif row["research_question"] == "RQ2":
                blockers = sorted(failed & {"publication_timestamp_coverage", "market_match_traceability", "market_quality_coverage", "case_level_rows"})
            else:
                blockers = ["optional_not_assessed_unless_RQ1_RQ2_pass"]
            writer.writerow({
                **row,
                "current_status": "SUPPORTED" if not blockers else "NOT_YET_SUPPORTED",
                "blocking_gates": ";".join(blockers),
            })
    print(OUT / "research_question_evidence_map.csv")

if __name__ == "__main__":
    main()
