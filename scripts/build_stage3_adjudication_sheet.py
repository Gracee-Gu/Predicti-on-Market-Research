#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pmresearch.stage3.io import read_csv, write_csv


CODING_FIELDS = [
    "market_probability_present",
    "probability_as_public_opinion",
    "representativeness_caveat",
    "market_quality_caveat",
    "certainty_language",
    "democratic_language",
    "horse_race_frame",
    "overreach_severity",
]

BASE_FIELDS = [
    "pair_id",
    "article_id",
    "market_id",
    "article_url",
    "article_title",
    "context_excerpt",
    "evidence_text",
    "quoted_price",
    "quoted_price_unit",
    "source_notes",
    "publication_time",
    "source_type",
    "platform",
    "topic",
    "match_status",
    "snapshot_status",
]


def has_disagreement(rows: list[dict]) -> bool:
    if len(rows) < 2:
        return False
    left, right = rows[0], rows[1]
    for field in CODING_FIELDS:
        if left.get(field, "") != right.get(field, ""):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/annotations/adjudication_sheet.csv")
    args = parser.parse_args()

    rows = read_csv(args.input)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["pair_id"]].append(row)

    output_rows: list[dict] = []
    fieldnames = BASE_FIELDS + ["coder_a_id", "coder_b_id"]
    for field in CODING_FIELDS:
        fieldnames.extend([f"{field}_coder_a", f"{field}_coder_b", f"{field}_adjudicated"])
    fieldnames.extend(["adjudication_notes"])

    for pair_rows in grouped.values():
        if len(pair_rows) < 2 or not has_disagreement(pair_rows):
            continue
        left, right = pair_rows[0], pair_rows[1]
        payload = {field: left.get(field, "") for field in BASE_FIELDS}
        payload["coder_a_id"] = left.get("coder_id", "")
        payload["coder_b_id"] = right.get("coder_id", "")
        for field in CODING_FIELDS:
            payload[f"{field}_coder_a"] = left.get(field, "")
            payload[f"{field}_coder_b"] = right.get(field, "")
            payload[f"{field}_adjudicated"] = ""
        payload["adjudication_notes"] = ""
        output_rows.append(payload)

    write_csv(args.output, output_rows, fieldnames)
    print(
        json.dumps(
            {
                "input_rows": len(rows),
                "disagreement_pairs": len(output_rows),
                "output": args.output,
            }
        )
    )


if __name__ == "__main__":
    main()
