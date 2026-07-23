#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pmresearch.stage3.io import read_csv, write_csv


def load_with_default_coder(path: str, coder_id: str) -> list[dict]:
    rows = read_csv(path)
    for row in rows:
        if not row.get("coder_id"):
            row["coder_id"] = coder_id
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coder-a", required=True)
    parser.add_argument("--coder-b", required=True)
    parser.add_argument("--coder-a-id", default="coder_a")
    parser.add_argument("--coder-b-id", default="coder_b")
    parser.add_argument("--output", default="data/annotations/coding_sheet_completed.csv")
    args = parser.parse_args()

    a_rows = load_with_default_coder(args.coder_a, args.coder_a_id)
    b_rows = load_with_default_coder(args.coder_b, args.coder_b_id)
    rows = a_rows + b_rows
    if not rows:
        raise SystemExit("No coder rows found to merge.")

    fieldnames = list(rows[0].keys())
    write_csv(args.output, rows, fieldnames)
    print(
        json.dumps(
            {
                "coder_a_rows": len(a_rows),
                "coder_b_rows": len(b_rows),
                "merged_rows": len(rows),
                "output": args.output,
            }
        )
    )


if __name__ == "__main__":
    main()
