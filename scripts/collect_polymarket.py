from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.collectors.polymarket import PolymarketCollector
from pmresearch.http import HttpClient
from pmresearch.io import write_jsonl


def optional_bool(value: str | None):
    if value is None or value.lower() == "all":
        return None
    if value.lower() in {"true", "1", "yes"}:
        return True
    if value.lower() in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("Use true, false, or all")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/stage2.yaml")
    parser.add_argument("--active", type=optional_bool, default=None)
    parser.add_argument("--closed", type=optional_bool, default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    c = config["polymarket"]
    client = HttpClient(
        user_agent=config["project"]["user_agent"],
        sleep_seconds=c["request_sleep_seconds"],
    )
    collector = PolymarketCollector(
        client, c["gamma_base_url"], c["clob_base_url"], c["page_limit"]
    )
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(args.output or f"data/raw/polymarket/markets_{timestamp}.jsonl")
    count = write_jsonl(output, collector.markets(args.active, args.closed))
    print(f"Wrote {count} Polymarket markets to {output}")


if __name__ == "__main__":
    main()
