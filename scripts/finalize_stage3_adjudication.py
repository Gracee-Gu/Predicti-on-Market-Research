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


def all_equal(rows: list[dict]) -> bool:
    if len(rows) < 2:
        return True
    left, right = rows[0], rows[1]
    return all(left.get(field, "") == right.get(field, "") for field in CODING_FIELDS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--completed", required=True)
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--output", default="data/annotations/adjudicated_annotations.csv")
    args = parser.parse_args()

    completed = read_csv(args.completed)
    adjudication_rows = read_csv(args.adjudication)
    adjudication_by_pair = {row["pair_id"]: row for row in adjudication_rows}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in completed:
        grouped[row["pair_id"]].append(row)

    output_rows: list[dict] = []
    output_fields = list(completed[0].keys()) if completed else []

    for pair_id, pair_rows in grouped.items():
        base = dict(pair_rows[0])
        base["coder_id"] = ""
        if len(pair_rows) == 1 or all_equal(pair_rows):
            reference = pair_rows[0]
            for field in CODING_FIELDS:
                base[field] = reference.get(field, "")
            output_rows.append(base)
            continue

        adjudication = adjudication_by_pair.get(pair_id)
        if not adjudication:
            raise SystemExit(f"Missing adjudication row for pair_id={pair_id}")
        for field in CODING_FIELDS:
            value = adjudication.get(f"{field}_adjudicated", "")
            if value == "":
                raise SystemExit(f"Missing adjudicated value for {field} on pair_id={pair_id}")
            base[field] = value
        base["notes"] = adjudication.get("adjudication_notes", base.get("notes", ""))
        output_rows.append(base)

    write_csv(args.output, output_rows, output_fields)
    print(json.dumps({"rows": len(output_rows), "output": args.output}))


if __name__ == "__main__":
    main()
