from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.collectors.kalshi import KalshiCollector
from pmresearch.http import HttpClient
from pmresearch.io import write_jsonl


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be a positive integer")
    return parsed


def load_tickers(raw_value: str | None, path_value: str | None) -> list[str]:
    tickers: list[str] = []
    if raw_value:
        tickers.extend(part.strip() for part in raw_value.split(","))
    if path_value:
        path = Path(path_value)
        tickers.extend(line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [ticker for ticker in tickers if ticker]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/stage2.yaml")
    parser.add_argument("--historical", action="store_true")
    parser.add_argument("--status", default=None)
    parser.add_argument("--tickers", default=None)
    parser.add_argument("--tickers-file", default=None)
    parser.add_argument("--event-ticker", default=None)
    parser.add_argument("--series-ticker", default=None)
    parser.add_argument("--exclude-mve", action="store_true")
    parser.add_argument("--max-pages", type=positive_int, default=None)
    parser.add_argument("--allow-unbounded-historical", action="store_true")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    tickers = load_tickers(args.tickers, args.tickers_file)
    if args.historical and args.status:
        parser.error("--status is only supported for live /markets collection")
    if args.historical:
        if sum([bool(tickers), bool(args.event_ticker), bool(args.series_ticker), bool(args.exclude_mve)]) > 1:
            parser.error(
                "Historical market filters are mutually exclusive; choose only one of "
                "--tickers/--tickers-file, --event-ticker, --series-ticker, or --exclude-mve."
            )
        bounded_historical = bool(
            tickers or args.event_ticker or args.series_ticker or args.exclude_mve or args.max_pages
        )
        if not bounded_historical and not args.allow_unbounded_historical:
            parser.error(
                "Refusing unbounded Kalshi historical collection. "
                "Use a historical filter, set --max-pages for a bounded probe, "
                "or pass --allow-unbounded-historical if you really want the full archive."
            )

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    c = config["kalshi"]
    client = HttpClient(
        user_agent=config["project"]["user_agent"],
        sleep_seconds=c["request_sleep_seconds"],
    )
    collector = KalshiCollector(client, c["base_url"], c["page_limit"])
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(args.output or f"data/raw/kalshi/markets_{timestamp}.jsonl")
    count = write_jsonl(
        output,
        collector.markets(
            status=args.status,
            historical=args.historical,
            tickers=tickers,
            event_ticker=args.event_ticker,
            series_ticker=args.series_ticker,
            exclude_mve=args.exclude_mve,
            max_pages=args.max_pages,
        ),
    )
    print(f"Wrote {count} Kalshi markets to {output}")


if __name__ == "__main__":
    main()
