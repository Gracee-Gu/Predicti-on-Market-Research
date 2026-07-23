from __future__ import annotations

import csv
import json

from _stage7_common import OUT, read_json, write_json
from audit_stage7_alignment import main as alignment_main
from build_stage7_evidence_map import main as evidence_map_main


ACTION_MAP = {
    "source_type_diversity": {
        "priority": 1,
        "research_question": "RQ1",
        "action": "Expand the corpus to at least three substantively different source types.",
    },
    "required_source_counts": {
        "priority": 1,
        "research_question": "RQ1",
        "action": "Increase platform-owned and independent-media counts to the configured minimum.",
    },
    "human_audited_units": {
        "priority": 2,
        "research_question": "RQ1",
        "action": "Complete at least 50 genuinely human-audited, double-coded units.",
    },
    "reliability_fields_reported": {
        "priority": 2,
        "research_question": "RQ1",
        "action": "Report reliability metrics for the core framing labels and adjudication output.",
    },
    "publication_timestamp_coverage": {
        "priority": 3,
        "research_question": "RQ2",
        "action": "Recover or verify publication timestamps for matched article-market pairs.",
    },
    "market_match_traceability": {
        "priority": 3,
        "research_question": "RQ2",
        "action": "Preserve traceable identifiers linking each text unit to a specific market record.",
    },
    "market_quality_coverage": {
        "priority": 3,
        "research_question": "RQ2",
        "action": "Recover publication-aligned raw market-quality metrics beyond cumulative volume.",
    },
    "case_level_rows": {
        "priority": 4,
        "research_question": "RQ2",
        "action": "Preserve auditable case-level rows for high-overreach text–market pairs.",
    },
}


def main() -> None:
    alignment_main()
    evidence_map_main()
    audit = read_json(OUT / "alignment_audit.json")
    checks = audit.get("checks", {})
    failed = audit.get("failed_checks", [])

    rows = []
    for gate in failed:
        item = checks.get(gate, {})
        action = ACTION_MAP.get(gate, {})
        rows.append(
            {
                "priority": action.get("priority", 9),
                "gate": gate,
                "research_question": action.get("research_question", "cross_cutting"),
                "observed": json.dumps(item.get("value"), ensure_ascii=False),
                "threshold": item.get("threshold", item.get("threshold_each")),
                "required_action": action.get("action", "Resolve this failed empirical gate."),
            }
        )
    rows.sort(key=lambda row: (row["priority"], row["gate"]))

    csv_path = OUT / "recovery_queue.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["priority", "gate", "research_question", "observed", "threshold", "required_action"],
        )
        writer.writeheader()
        writer.writerows(rows)

    payload = {
        "stage": 7,
        "research_status": audit.get("status"),
        "queue_items": len(rows),
        "queue_path": str(csv_path.relative_to(csv_path.parents[2])),
    }
    write_json(OUT / "recovery_queue_summary.json", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
