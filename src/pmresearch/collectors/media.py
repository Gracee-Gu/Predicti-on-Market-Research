from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from pmresearch.http import HttpClient
from pmresearch.io import sha256_text


@dataclass
class MediaCollector:
    client: HttpClient
    store_full_text: bool = False
    excerpt_character_limit: int = 500

    def collect_seed_file(self, seed_path: Path) -> list[dict]:
        with seed_path.open(encoding="utf-8", newline="") as handle:
            seeds = list(csv.DictReader(handle))
        return [self.collect_one(seed) for seed in seeds]

    def collect_one(self, seed: dict) -> dict:
        html, content_type = self.client.get_text(seed["url"])
        soup = BeautifulSoup(html, "html.parser")
        title = self._meta(soup, "og:title") or (soup.title.string.strip() if soup.title and soup.title.string else "")
        published = (
            seed.get("published_at")
            or self._meta(soup, "article:published_time")
            or self._meta_name(soup, "date")
            or ""
        )
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
        record = dict(seed)
        record.update(
            {
                "resolved_domain": urlparse(seed["url"]).netloc.lower(),
                "page_title": title,
                "published_at_resolved": published,
                "content_type": content_type,
                "fetch_ok": True,
                "text_sha256": sha256_text(text),
                "text_length_chars": len(text),
                "excerpt": text[: self.excerpt_character_limit],
            }
        )
        if self.store_full_text:
            record["full_text"] = text
        return record

    @staticmethod
    def _meta(soup: BeautifulSoup, prop: str) -> str:
        tag = soup.find("meta", attrs={"property": prop})
        return tag.get("content", "").strip() if tag else ""

    @staticmethod
    def _meta_name(soup: BeautifulSoup, name: str) -> str:
        tag = soup.find("meta", attrs={"name": name})
        return tag.get("content", "").strip() if tag else ""
