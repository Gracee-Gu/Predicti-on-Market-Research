from __future__ import annotations

import json

from _stage7_common import OUT, ROOT, count_metric_columns, proportion, read_csv, read_json, write_json
from audit_stage7_alignment import main as alignment_main


EVENT_PATTERNS = [
    "window", "spread", "price", "return", "trade_count", "volume", "depth", "volatility", "stability"
]


def main() -> None:
    alignment_main()
    audit = read_json(OUT / "alignment_audit.json")
    dataset_path = ROOT / "data/analysis/article_market_dataset.csv"
    dataset = read_csv(dataset_path)
    event_columns = count_metric_columns(dataset, EVENT_PATTERNS)
    event_coverage = proportion(dataset, event_columns)

    timestamp_check = audit.get("checks", {}).get("publication_timestamp_coverage", {})
    market_quality_check = audit.get("checks", {}).get("market_quality_coverage", {})
    status = audit.get("status", "design_revision_required")

    if status != "finalization_ready":
        decision = "defer_until_empirical_recovery"
        rationale = (
            "The optional event study is deferred because the two core empirical components are not yet complete."
        )
    elif timestamp_check.get("value", 0.0) < 0.80:
        decision = "not_feasible"
        rationale = "Publication timestamps are too incomplete for an auditable event-window design."
    elif event_coverage < 0.50 or market_quality_check.get("value", 0.0) < 0.50:
        decision = "not_feasible"
        rationale = "Market time-series coverage is too sparse to support publication-centered event windows."
    else:
        decision = "proceed_optional"
        rationale = "Timestamp and time-series coverage are sufficient for an optional associational event study."

    payload = {
        "stage": 7,
        "decision": decision,
        "alignment_status": status,
        "timestamp_coverage": timestamp_check.get("value", 0.0),
        "event_metric_columns": event_columns,
        "event_metric_coverage": event_coverage,
        "market_quality_coverage": market_quality_check.get("value", 0.0),
        "rationale": rationale,
    }
    write_json(OUT / "event_study_decision.json", payload)

    memo = f"""# Stage 7 Event Study Decision

## Decision

`{decision}`

## Rationale

{rationale}

## Diagnostics

- Alignment status: `{status}`
- Publication timestamp coverage: `{timestamp_check.get("value", 0.0):.3f}`
- Event-metric coverage: `{event_coverage:.3f}`
- Market-quality coverage: `{market_quality_check.get("value", 0.0):.3f}`
- Detected event-related columns: `{", ".join(event_columns) if event_columns else "none"}`
"""
    (OUT / "event_study_decision.md").write_text(memo, encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
