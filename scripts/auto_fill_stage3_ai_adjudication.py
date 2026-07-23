#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from auto_fill_stage3_ai_coders import code_row


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


def read_csv(path: str) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: str, rows: list[dict]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows = read_csv(args.input)
    completed: list[dict] = []
    for row in rows:
        payload = dict(row)
        codes = code_row(payload, "adjudicator")
        for field in CODING_FIELDS:
            payload[f"{field}_adjudicated"] = codes[field]
        payload["adjudication_notes"] = "AI adjudication based on rubric heuristics."
        completed.append(payload)
    write_csv(args.output, completed)
    print(json.dumps({"rows": len(completed), "output": args.output}))


if __name__ == "__main__":
    main()
