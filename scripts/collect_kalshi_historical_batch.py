from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.collectors.kalshi import KalshiCollector
from pmresearch.http import HttpClient
from pmresearch.io import ensure_parent


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer")
    return parsed


def load_tickers(path: Path) -> list[str]:
    seen: set[str] = set()
    tickers: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        ticker = line.strip()
        if ticker and ticker not in seen:
            seen.add(ticker)
            tickers.append(ticker)
    return tickers


def chunked(values: list[str], chunk_size: int) -> Iterable[list[str]]:
    for index in range(0, len(values), chunk_size):
        yield values[index : index + chunk_size]


def existing_tickers(path: Path) -> set[str]:
    if not path.exists():
        return set()
    tickers: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            ticker = json.loads(line).get("ticker")
            if ticker:
                tickers.add(ticker)
    return tickers


def default_output_path() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"data/raw/kalshi/historical_markets_{timestamp}.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/stage2.yaml")
    parser.add_argument("--tickers-file", required=True)
    parser.add_argument("--chunk-size", type=positive_int, default=25)
    parser.add_argument("--output", default=default_output_path())
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    c = config["kalshi"]
    client = HttpClient(
        user_agent=config["project"]["user_agent"],
        sleep_seconds=c["request_sleep_seconds"],
    )
    collector = KalshiCollector(client, c["base_url"], c["page_limit"])

    tickers = load_tickers(Path(args.tickers_file))
    output = Path(args.output)
    already_written = existing_tickers(output) if args.resume else set()
    pending = [ticker for ticker in tickers if ticker not in already_written]

    if output.exists() and not args.resume:
        parser.error(f"{output} already exists. Use --resume or choose a new --output path.")

    ensure_parent(output)
    total_chunks = (len(pending) + args.chunk_size - 1) // args.chunk_size if pending else 0
    written = 0
    mode = "a" if args.resume else "w"
    with output.open(mode, encoding="utf-8") as handle:
        for index, ticker_chunk in enumerate(chunked(pending, args.chunk_size), start=1):
            rows = list(collector.markets(historical=True, tickers=ticker_chunk))
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                written += 1
            missing = sorted(set(ticker_chunk) - {row.get("ticker") for row in rows})
            print(
                f"Chunk {index}/{total_chunks}: requested {len(ticker_chunk)} tickers, "
                f"wrote {len(rows)} records"
            )
            if missing:
                print(f"Missing tickers in chunk {index}: {', '.join(missing)}")

    print(
        f"Wrote {written} historical Kalshi market records for {len(pending)} requested tickers to {output}"
    )


if __name__ == "__main__":
    main()
