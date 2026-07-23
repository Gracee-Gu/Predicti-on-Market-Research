from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.collectors.media import MediaCollector
from pmresearch.http import HttpClient
from pmresearch.io import write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/stage2.yaml")
    parser.add_argument("--seed-file", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    c = config["media"]
    client = HttpClient(
        user_agent=config["project"]["user_agent"],
        sleep_seconds=c["request_sleep_seconds"],
    )
    collector = MediaCollector(
        client,
        store_full_text=c["store_full_text"],
        excerpt_character_limit=c["excerpt_character_limit"],
    )
    seed_file = Path(args.seed_file or c["seed_file"])
    rows = collector.collect_seed_file(seed_file)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(args.output or f"data/raw/media/media_{timestamp}.jsonl")
    count = write_jsonl(output, rows)
    print(f"Wrote {count} media records to {output}")


if __name__ == "__main__":
    main()
