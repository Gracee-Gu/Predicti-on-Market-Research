from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.io import ensure_parent


DEFAULT_TICKER_FIELDS = ["matched_market_id", "market_id", "ticker"]


def iter_csv_rows(path: Path) -> Iterable[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def iter_jsonl_rows(path: Path) -> Iterable[dict]:
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def iter_rows(path: Path) -> Iterable[dict]:
    if path.suffix.lower() == ".csv":
        yield from iter_csv_rows(path)
        return
    if path.suffix.lower() == ".jsonl":
        yield from iter_jsonl_rows(path)
        return
    raise ValueError(f"Unsupported input format for {path}. Use .csv or .jsonl")


def parse_ticker_value(value: str) -> list[str]:
    return [part for part in re.split(r"[\s,]+", value.strip()) if part]


def choose_tickers(row: dict, ticker_fields: list[str]) -> list[str]:
    for field in ticker_fields:
        value = str(row.get(field, "")).strip()
        if value:
            return parse_ticker_value(value)
    return []


def export_tickers(
    inputs: list[Path],
    output: Path,
    ticker_fields: list[str],
    platform_field: str,
    platform_value: str,
) -> tuple[int, int]:
    seen: set[str] = set()
    ordered: list[str] = []
    scanned = 0

    for path in inputs:
        for row in iter_rows(path):
            scanned += 1
            platform = str(row.get(platform_field, "")).strip().lower()
            if platform and platform != platform_value.lower():
                continue
            for ticker in choose_tickers(row, ticker_fields):
                if ticker not in seen:
                    seen.add(ticker)
                    ordered.append(ticker)

    ensure_parent(output)
    output.write_text("\n".join(ordered) + ("\n" if ordered else ""), encoding="utf-8")
    return scanned, len(ordered)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--output", default="data/interim/kalshi_tickers.txt")
    parser.add_argument("--ticker-field", action="append", default=[])
    parser.add_argument("--platform-field", default="platform")
    parser.add_argument("--platform-value", default="kalshi")
    args = parser.parse_args()

    ticker_fields = args.ticker_field or DEFAULT_TICKER_FIELDS
    inputs = [Path(value) for value in args.input]
    scanned, exported = export_tickers(
        inputs=inputs,
        output=Path(args.output),
        ticker_fields=ticker_fields,
        platform_field=args.platform_field,
        platform_value=args.platform_value,
    )
    print(f"Scanned {scanned} rows and wrote {exported} unique Kalshi tickers to {args.output}")


if __name__ == "__main__":
    main()
