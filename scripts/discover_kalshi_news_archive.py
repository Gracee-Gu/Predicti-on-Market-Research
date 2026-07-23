from __future__ import annotations

import argparse
import csv
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.http import HttpClient
from pmresearch.io import ensure_parent


ARCHIVE_URL = "https://news.kalshi.com/archive"


def fetch_archive_posts(client: HttpClient, limit: int, max_pages: int) -> list[dict]:
    posts: list[dict] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        url = ARCHIVE_URL if page == 1 else f"{ARCHIVE_URL}?page={page}"
        html, _ = client.get_text(url)
        soup = BeautifulSoup(html, "html.parser")
        page_added = 0
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "").strip()
            if not href or href.startswith("#"):
                continue
            absolute = urljoin(url, href)
            if "/p/" not in absolute:
                continue
            if absolute in seen:
                continue
            seen.add(absolute)
            title = " ".join(tag.get_text(" ", strip=True).split())
            posts.append(
                {
                    "source_name": "Kalshi News",
                    "source_type": "platform_owned",
                    "formal_partnership": "0",
                    "platform": "kalshi",
                    "url": absolute,
                    "published_at": "",
                    "article_genre": "",
                    "market_category": "",
                    "notes": f"Discovered from Kalshi News archive page {page}",
                    "partnership_evidence_url": "",
                    "page_title_seed": title,
                }
            )
            page_added += 1
            if len(posts) >= limit:
                return posts
        if page_added == 0:
            break
    return posts


def write_seed_csv(path: Path, rows: list[dict], id_prefix: str = "kalshi_archive") -> None:
    ensure_parent(path)
    fieldnames = [
        "source_id",
        "source_name",
        "source_type",
        "formal_partnership",
        "platform",
        "url",
        "published_at",
        "article_genre",
        "market_category",
        "notes",
        "partnership_evidence_url",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, row in enumerate(rows, start=1):
            payload = dict(row)
            payload["source_id"] = f"{id_prefix}_{index:03d}"
            payload.pop("page_title_seed", None)
            writer.writerow(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="config/media_sources_kalshi_archive.csv")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--max-pages", type=int, default=10)
    args = parser.parse_args()

    client = HttpClient(
        user_agent="PredictionMarketResearch/0.2",
        timeout_seconds=10.0,
        max_retries=2,
        sleep_seconds=0.2,
    )
    rows = fetch_archive_posts(client, limit=args.limit, max_pages=args.max_pages)
    output = Path(args.output)
    write_seed_csv(output, rows)
    print(f"Wrote {len(rows)} Kalshi News archive seeds to {output}")


if __name__ == "__main__":
    main()
