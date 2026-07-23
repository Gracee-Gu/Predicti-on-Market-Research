#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pmresearch.stage3.io import read_csv
from pmresearch.stage3.reliability import cohen_kappa, krippendorff_alpha_ordinal


FIELDS = [
    "market_probability_present",
    "probability_as_public_opinion",
    "representativeness_caveat",
    "market_quality_caveat",
    "certainty_language",
    "democratic_language",
    "horse_race_frame",
    "overreach_severity",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/analysis/reliability.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(
            f"Input file not found: {args.input}. "
            "Create a merged coder file first, for example "
            "`data/annotations/coding_sheet_completed.csv`."
        )

    rows = read_csv(args.input)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["pair_id"]].append(row)

    report = {
        "n_rows": len(rows),
        "n_double_coded": sum(len(value) >= 2 for value in grouped.values()),
        "fields": {},
    }
    for field in FIELDS:
        pairs = [
            value
            for value in grouped.values()
            if len(value) >= 2 and value[0].get(field, "") != "" and value[1].get(field, "") != ""
        ]
        report["fields"][field] = {
            "cohen_kappa": cohen_kappa([value[0][field] for value in pairs], [value[1][field] for value in pairs]),
            "ordinal_alpha": krippendorff_alpha_ordinal([[row[field] for row in value] for value in pairs]),
            "n": len(pairs),
        }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
