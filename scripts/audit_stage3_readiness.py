from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.io import read_jsonl


PASSING_MENTION_METHODS = {"exact_identifier", "exact_title", "fuzzy_reviewed"}
PASSING_SNAPSHOT_STATUSES = {
    "historical_price_matched",
    "historical_trade_matched",
}


def load_rows(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for value in paths:
        rows.extend(read_jsonl(Path(value)))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", action="append", default=[])
    parser.add_argument("--mentions", action="append", default=[])
    parser.add_argument("--snapshots", action="append", default=[])
    parser.add_argument("--target-per-stratum", type=int, default=30)
    args = parser.parse_args()

    media_rows = load_rows(args.media)
    mention_rows = load_rows(args.mentions)
    snapshot_rows = load_rows(args.snapshots)

    docs_by_stratum = Counter(
        row.get("source_type", "")
        for row in media_rows
        if row.get("fetch_ok", True)
    )
    passing_mentions = [
        row for row in mention_rows if row.get("match_method", "") in PASSING_MENTION_METHODS
    ]
    passing_snapshots = [
        row for row in snapshot_rows if row.get("snapshot_status", "") in PASSING_SNAPSHOT_STATUSES
    ]
    prospective_count = sum(
        1
        for row in snapshot_rows
        if row.get("snapshot_status") == "prospective_orderbook_matched"
    )

    report = {
        "documents_by_stratum": dict(docs_by_stratum),
        "documents_target_per_stratum": args.target_per_stratum,
        "documents_gap_by_stratum": {
            stratum: max(0, args.target_per_stratum - docs_by_stratum.get(stratum, 0))
            for stratum in [
                "platform_owned",
                "partner_media",
                "independent_media",
                "regulatory_critical",
            ]
        },
        "documents_gate_pass": all(
            docs_by_stratum.get(stratum, 0) >= args.target_per_stratum
            for stratum in [
                "platform_owned",
                "partner_media",
                "independent_media",
                "regulatory_critical",
            ]
        ),
        "unambiguous_mentions": len(passing_mentions),
        "unambiguous_mentions_gate_pass": len(passing_mentions) >= 100,
        "publication_time_matches": len(passing_snapshots),
        "publication_time_matches_gate_pass": len(passing_snapshots) >= 50,
        "prospective_snapshot_matches": prospective_count,
        "prospective_snapshot_plan_ready": prospective_count > 0,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
