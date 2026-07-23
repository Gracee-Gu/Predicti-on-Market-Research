#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pmresearch.stage3.io import read_jsonl, write_csv


FIELDS = [
    "pair_id",
    "article_id",
    "market_id",
    "article_url",
    "article_title",
    "context_excerpt",
    "evidence_text",
    "quoted_price",
    "quoted_price_unit",
    "source_notes",
    "publication_time",
    "source_type",
    "platform",
    "topic",
    "match_status",
    "snapshot_status",
    "double_code",
    "coder_id",
    "market_probability_present",
    "probability_as_public_opinion",
    "representativeness_caveat",
    "market_quality_caveat",
    "certainty_language",
    "democratic_language",
    "horse_race_frame",
    "overreach_severity",
    "notes",
]


def first(row: dict, *names: str) -> str:
    for name in names:
        value = row.get(name)
        if value not in (None, ""):
            return str(value)
    return ""


def make_pair_id(article_id: str, market_id: str) -> str:
    return hashlib.sha256(f"{article_id}|{market_id}".encode()).hexdigest()[:16]


def load_snapshots(snapshot_glob: str) -> tuple[dict[str, dict], list[str]]:
    snapshots: dict[str, dict] = {}
    matched_files = sorted(glob.glob(snapshot_glob))
    for path in matched_files:
        for row in read_jsonl(path):
            snapshot_id = first(row, "snapshot_id", "mention_id", "pair_id")
            if snapshot_id:
                snapshots[snapshot_id] = row
    return snapshots, matched_files


def load_media(media_glob: str) -> tuple[dict[str, dict], list[str]]:
    media_by_source: dict[str, dict] = {}
    matched_files = sorted(glob.glob(media_glob))
    for path in matched_files:
        for row in read_jsonl(path):
            source_id = first(row, "source_id")
            if source_id and source_id not in media_by_source:
                media_by_source[source_id] = row
    return media_by_source, matched_files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-glob", default="data/processed/market_mentions*_v3.jsonl")
    parser.add_argument("--snapshots-glob", default="data/processed/market_snapshots*_v3.jsonl")
    parser.add_argument("--media-glob", default="data/raw/media/*.jsonl")
    parser.add_argument("--output", default="data/annotations/coding_sheet.csv")
    parser.add_argument("--seed", type=int, default=20260723)
    parser.add_argument("--double-fraction", type=float, default=0.2)
    args = parser.parse_args()

    mention_files = sorted(glob.glob(args.input_glob))
    snapshots, snapshot_files = load_snapshots(args.snapshots_glob)
    media_by_source, media_files = load_media(args.media_glob)

    rows: list[dict[str, str | int]] = []
    seen: set[tuple[str, str]] = set()
    skipped_missing_ids = 0

    for path in mention_files:
        for row in read_jsonl(path):
            article_id = first(row, "article_id", "source_id", "media_id", "url_hash")
            market_id = first(row, "market_id", "ticker", "condition_id")
            if not article_id or not market_id:
                skipped_missing_ids += 1
                continue

            key = (article_id, market_id)
            if key in seen:
                continue
            seen.add(key)

            pair_id = make_pair_id(article_id, market_id)
            mention_id = first(row, "mention_id")
            snapshot = snapshots.get(mention_id, {})
            media = media_by_source.get(article_id, {})

            rows.append(
                {
                    "pair_id": pair_id,
                    "article_id": article_id,
                    "market_id": market_id,
                    "article_url": first(row, "article_url", "source_url", "url"),
                    "article_title": first(media, "page_title"),
                    "context_excerpt": first(media, "excerpt"),
                    "evidence_text": first(row, "evidence_text"),
                    "quoted_price": first(row, "quoted_price"),
                    "quoted_price_unit": first(row, "quoted_price_unit"),
                    "source_notes": first(row, "notes"),
                    "publication_time": first(row, "publication_time", "published_at"),
                    "source_type": first(row, "source_type"),
                    "platform": first(row, "platform"),
                    "topic": first(row, "topic", "category", "market_category"),
                    "match_status": first(row, "match_status", "match_method"),
                    "snapshot_status": first(snapshot, "snapshot_status")
                    or first(row, "snapshot_status"),
                    "double_code": 0,
                    "coder_id": "",
                    "market_probability_present": "",
                    "probability_as_public_opinion": "",
                    "representativeness_caveat": "",
                    "market_quality_caveat": "",
                    "certainty_language": "",
                    "democratic_language": "",
                    "horse_race_frame": "",
                    "overreach_severity": "",
                    "notes": "",
                }
            )

    rng = random.Random(args.seed)
    ids = list(range(len(rows)))
    rng.shuffle(ids)
    for index in ids[: round(len(rows) * args.double_fraction)]:
        rows[index]["double_code"] = 1

    write_csv(args.output, rows, FIELDS)
    print(
        json.dumps(
            {
                "mention_files": len(mention_files),
                "snapshot_files": len(snapshot_files),
                "media_files": len(media_files),
                "pairs": len(rows),
                "double_code": sum(int(row["double_code"]) for row in rows),
                "skipped_missing_ids": skipped_missing_ids,
                "output": args.output,
            }
        )
    )


if __name__ == "__main__":
    main()
