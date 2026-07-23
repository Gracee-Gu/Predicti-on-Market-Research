from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from pmresearch.http import HttpClient
from pmresearch.io import sha256_text
from pmresearch.market_utils import extract_kalshi_market_ticker, extract_kalshi_tickers


@dataclass
class MediaCollector:
    client: HttpClient
    store_full_text: bool = False
    excerpt_character_limit: int = 500

    def collect_seed_file(self, seed_path: Path) -> list[dict]:
        with seed_path.open(encoding="utf-8", newline="") as handle:
            seeds = list(csv.DictReader(handle))
        return [self.collect_one_safe(seed) for seed in seeds]

    def collect_one_safe(self, seed: dict) -> dict:
        try:
            return self.collect_one(seed)
        except Exception as exc:
            record = dict(seed)
            record.update(
                {
                    "resolved_domain": urlparse(seed.get("url", "")).netloc.lower(),
                    "page_title": "",
                    "published_at_resolved": seed.get("published_at", ""),
                    "content_type": "",
                    "fetch_ok": False,
                    "fetch_error": str(exc),
                    "text_sha256": "",
                    "text_length_chars": 0,
                    "excerpt": "",
                    "market_links": [],
                    "candidate_tickers": [],
                }
            )
            return record

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
        market_links = self._market_links(soup, seed["url"])
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
                "market_links": market_links,
                "candidate_tickers": extract_kalshi_tickers(
                    title,
                    text[: max(self.excerpt_character_limit * 3, 1500)],
                ),
            }
        )
        linked_tickers = [
            extract_kalshi_market_ticker(link["url"])
            for link in market_links
        ]
        record["candidate_tickers"] = [
            ticker
            for ticker in dict.fromkeys(record["candidate_tickers"] + linked_tickers)
            if ticker
        ]
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

    @staticmethod
    def _market_links(soup: BeautifulSoup, base_url: str) -> list[dict[str, str]]:
        links: list[dict[str, str]] = []
        seen: set[str] = set()
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "").strip()
            if not href:
                continue
            absolute = urljoin(base_url, href)
            netloc = urlparse(absolute).netloc.lower()
            if "kalshi.com" not in netloc and "polymarket.com" not in netloc:
                continue
            if absolute in seen:
                continue
            seen.add(absolute)
            label = re.sub(r"\s+", " ", tag.get_text(" ", strip=True)).strip()[:160]
            links.append({"url": absolute, "label": label})
        return links
