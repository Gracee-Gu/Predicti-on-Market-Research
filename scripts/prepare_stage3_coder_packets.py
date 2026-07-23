#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pmresearch.stage3.io import read_csv, write_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/annotations/coding_sheet.csv")
    parser.add_argument("--output-a", default="data/annotations/coder_a_sheet.csv")
    parser.add_argument("--output-b", default="data/annotations/coder_b_sheet.csv")
    parser.add_argument("--coder-a-id", default="coder_a")
    parser.add_argument("--coder-b-id", default="coder_b")
    parser.add_argument("--seed", type=int, default=20260723)
    args = parser.parse_args()

    rows = read_csv(args.input)
    if not rows:
        raise SystemExit(f"No rows found in {args.input}")

    fieldnames = list(rows[0].keys())
    rng = random.Random(args.seed)
    single_rows = [row for row in rows if str(row.get("double_code", "0")) != "1"]
    double_rows = [row for row in rows if str(row.get("double_code", "0")) == "1"]
    rng.shuffle(single_rows)

    a_rows: list[dict] = []
    b_rows: list[dict] = []

    for index, row in enumerate(single_rows):
        payload = dict(row)
        if index % 2 == 0:
            payload["coder_id"] = args.coder_a_id
            a_rows.append(payload)
        else:
            payload["coder_id"] = args.coder_b_id
            b_rows.append(payload)

    for row in double_rows:
        a_payload = dict(row)
        a_payload["coder_id"] = args.coder_a_id
        a_rows.append(a_payload)

        b_payload = dict(row)
        b_payload["coder_id"] = args.coder_b_id
        b_rows.append(b_payload)

    write_csv(args.output_a, a_rows, fieldnames)
    write_csv(args.output_b, b_rows, fieldnames)
    print(
        json.dumps(
            {
                "input_rows": len(rows),
                "double_coded_pairs": len(double_rows),
                "coder_a_rows": len(a_rows),
                "coder_b_rows": len(b_rows),
                "output_a": args.output_a,
                "output_b": args.output_b,
            }
        )
    )


if __name__ == "__main__":
    main()
