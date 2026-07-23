from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.io import read_jsonl, write_csv


FIELDS = [
    "record_type", "platform", "source_file", "record_id", "title",
    "status", "category", "start_time", "end_time", "raw_url_or_ticker",
    "matched_market_id", "publication_time", "source_type", "formal_partnership",
    "quality_snapshot_status", "notes"
]


def market_row(platform: str, source_file: Path, item: dict) -> dict:
    if platform == "kalshi":
        return {
            "record_type": "market",
            "platform": platform,
            "source_file": str(source_file),
            "record_id": item.get("ticker", ""),
            "title": item.get("title", ""),
            "status": item.get("status", ""),
            "category": item.get("category", ""),
            "start_time": item.get("open_time", ""),
            "end_time": item.get("close_time", ""),
            "raw_url_or_ticker": item.get("ticker", ""),
        }
    return {
        "record_type": "market",
        "platform": platform,
        "source_file": str(source_file),
        "record_id": item.get("id", ""),
        "title": item.get("question", ""),
        "status": "closed" if item.get("closed") else "active",
        "category": item.get("category", ""),
        "start_time": item.get("startDate", ""),
        "end_time": item.get("endDate", ""),
        "raw_url_or_ticker": item.get("slug", ""),
    }


def media_row(source_file: Path, item: dict) -> dict:
    return {
        "record_type": "media",
        "platform": item.get("platform", ""),
        "source_file": str(source_file),
        "record_id": item.get("source_id", ""),
        "title": item.get("page_title", ""),
        "raw_url_or_ticker": item.get("url", ""),
        "publication_time": item.get("published_at_resolved", ""),
        "source_type": item.get("source_type", ""),
        "formal_partnership": item.get("formal_partnership", ""),
        "matched_market_id": item.get("matched_market_id", ""),
        "quality_snapshot_status": item.get("quality_snapshot_status", "unmatched"),
        "notes": item.get("notes", ""),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kalshi", action="append", default=[])
    parser.add_argument("--polymarket", action="append", default=[])
    parser.add_argument("--media", action="append", default=[])
    parser.add_argument("--output", default="data/inventory/corpus_inventory.csv")
    args = parser.parse_args()

    rows = []
    for value in args.kalshi:
        path = Path(value)
        rows.extend(market_row("kalshi", path, row) for row in read_jsonl(path))
    for value in args.polymarket:
        path = Path(value)
        rows.extend(market_row("polymarket", path, row) for row in read_jsonl(path))
    for value in args.media:
        path = Path(value)
        rows.extend(media_row(path, row) for row in read_jsonl(path))

    write_csv(Path(args.output), rows, FIELDS)
    print(f"Wrote {len(rows)} inventory rows to {args.output}")


if __name__ == "__main__":
    main()
