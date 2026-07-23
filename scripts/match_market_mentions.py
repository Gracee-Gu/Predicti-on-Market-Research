from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.collectors.kalshi import KalshiCollector
from pmresearch.http import HttpClient
from pmresearch.io import read_jsonl, write_jsonl
from pmresearch.market_utils import (
    choose_polymarket_yes_token,
    extract_kalshi_event_ticker,
    extract_kalshi_fragment,
    extract_kalshi_market_ticker,
    extract_kalshi_tickers,
    extract_polymarket_slug,
    infer_kalshi_event_ticker,
    loose_normalize_identifier,
    normalize_text,
)


PRICE_RE = re.compile(r"(?P<value>\d{1,3}(?:\.\d+)?)\s*(?P<unit>%|percent|cents?|¢)")


def has_price_token(value: str) -> bool:
    return bool(PRICE_RE.search(value or ""))


def build_catalog(kalshi_paths: list[Path], polymarket_paths: list[Path]) -> list[dict]:
    catalog: list[dict] = []
    for path in kalshi_paths:
        for row in read_jsonl(path):
            catalog.append(
                {
                    "platform": "kalshi",
                    "market_id": row.get("ticker", ""),
                    "title": row.get("title", ""),
                    "normalized_title": normalize_text(row.get("title", "")),
                    "slug": "",
                    "yes_token_id": "",
                    "event_ticker": row.get("event_ticker", ""),
                    "series_ticker": row.get("series_ticker", ""),
                    "status": row.get("status", ""),
                }
            )
    for path in polymarket_paths:
        for row in read_jsonl(path):
            catalog.append(
                {
                    "platform": "polymarket",
                    "market_id": str(row.get("id", "")),
                    "title": row.get("question", ""),
                    "normalized_title": normalize_text(row.get("question", "")),
                    "slug": str(row.get("slug", "")).strip().lower(),
                    "yes_token_id": choose_polymarket_yes_token(row),
                    "event_ticker": "",
                    "series_ticker": "",
                    "status": "closed" if row.get("closed") else "active",
                }
            )
    return catalog


def kalshi_catalog_by_ticker(catalog: list[dict]) -> dict[str, dict]:
    return {
        row["market_id"]: row
        for row in catalog
        if row["platform"] == "kalshi" and row["market_id"]
    }


def polymarket_catalog_by_slug(catalog: list[dict]) -> dict[str, dict]:
    return {
        row["slug"]: row
        for row in catalog
        if row["platform"] == "polymarket" and row["slug"]
    }


def resolve_fragment_market(fragment: str, markets: list[dict]) -> dict | None:
    if not fragment:
        return None
    normalized_fragment = loose_normalize_identifier(fragment)
    for market in markets:
        if market.get("ticker", "").upper() == fragment:
            return market
    for market in markets:
        ticker = market.get("ticker", "")
        normalized_ticker = loose_normalize_identifier(ticker)
        if normalized_fragment == normalized_ticker or normalized_ticker.endswith(normalized_fragment):
            return market
    return None


def resolve_market_from_event_payload(
    event_payload: dict,
    link_label: str,
    fragment: str,
) -> dict | None:
    markets = event_payload.get("markets", []) or event_payload.get("event", {}).get("markets", []) or []
    if not markets:
        return None

    exact = resolve_fragment_market(fragment, markets)
    if exact:
        return exact
    if len(markets) == 1:
        return markets[0]

    normalized_label = normalize_text(link_label)
    if not normalized_label or len(normalized_label) < 6:
        return None

    scored: list[tuple[int, dict]] = []
    label_tokens = set(normalized_label.split())
    for market in markets:
        candidate_text = " ".join(
            [
                market.get("title", ""),
                market.get("yes_sub_title", ""),
                market.get("no_sub_title", ""),
            ]
        )
        normalized_candidate = normalize_text(candidate_text)
        candidate_tokens = set(normalized_candidate.split())
        overlap = len(label_tokens & candidate_tokens)
        if normalized_label in normalized_candidate:
            overlap += 5
        scored.append((overlap, market))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored or scored[0][0] <= 0:
        return None
    if len(scored) == 1 or scored[0][0] > scored[1][0]:
        return scored[0][1]
    return None


def resolve_kalshi_link_markets(
    source: dict,
    collector: KalshiCollector | None,
    event_cache: dict[str, dict],
) -> list[dict]:
    if collector is None:
        return []
    resolved: list[dict] = []
    seen: set[str] = set()
    for link in source.get("market_links", []) or []:
        url = link.get("url", "")
        event_ticker = extract_kalshi_event_ticker(url)
        if not event_ticker:
            continue
        if event_ticker not in event_cache:
            try:
                event_cache[event_ticker] = collector.event(event_ticker, with_nested_markets=True)
            except Exception:
                event_cache[event_ticker] = {}
        payload = event_cache.get(event_ticker, {})
        market = resolve_market_from_event_payload(
            payload,
            link.get("label", ""),
            extract_kalshi_fragment(url),
        )
        if not market:
            continue
        ticker = market.get("ticker", "")
        if not ticker or ticker in seen:
            continue
        seen.add(ticker)
        resolved.append(
            {
                "platform": "kalshi",
                "market_id": ticker,
                "title": market.get("title", ""),
                "slug": "",
                "yes_token_id": "",
                "event_ticker": market.get("event_ticker", event_ticker),
                "status": market.get("status", ""),
                "series_ticker": payload.get("event", {}).get("series_ticker", ""),
            }
        )
    return resolved


def combined_text(row: dict) -> str:
    pieces = [
        row.get("page_title", ""),
        row.get("excerpt", ""),
        row.get("notes", ""),
        row.get("url", ""),
    ]
    for link in row.get("market_links", []) or []:
        pieces.append(link.get("url", ""))
        pieces.append(link.get("label", ""))
    return " ".join(piece for piece in pieces if piece)


def find_quoted_price(text: str, anchor: int) -> tuple[str, str]:
    left = max(0, anchor - 160)
    right = min(len(text), anchor + 240)
    window = text[left:right]
    match = PRICE_RE.search(window)
    if not match:
        return "", ""
    return match.group("value"), match.group("unit")


def mention_record(
    source: dict,
    market: dict,
    method: str,
    search_text: str,
    matched_text: str,
) -> dict:
    lower_text = search_text.lower()
    anchor = lower_text.find(matched_text.lower()) if matched_text else -1
    price, price_unit = find_quoted_price(search_text, anchor if anchor >= 0 else 0)
    publication_time = source.get("published_at_resolved") or source.get("published_at", "")
    event_ticker = market.get("event_ticker", "")
    if not event_ticker and market.get("platform") == "kalshi":
        event_ticker = infer_kalshi_event_ticker(market.get("market_id", ""))
    return {
        "mention_id": f"{source.get('source_id', '')}:{market['platform']}:{market['market_id']}",
        "source_id": source.get("source_id", ""),
        "source_name": source.get("source_name", ""),
        "source_type": source.get("source_type", ""),
        "formal_partnership": source.get("formal_partnership", ""),
        "source_url": source.get("url", ""),
        "publication_time": publication_time,
        "platform": market["platform"],
        "market_id": market["market_id"],
        "market_title": market.get("title", ""),
        "market_slug": market.get("slug", ""),
        "event_ticker": event_ticker,
        "series_ticker": market.get("series_ticker", ""),
        "token_id": market.get("yes_token_id", ""),
        "match_method": method,
        "match_confidence": 1.0 if method == "exact_identifier" else 0.95,
        "mention_start_char": anchor,
        "mention_end_char": anchor + len(matched_text) if anchor >= 0 else -1,
        "quoted_price": price,
        "quoted_price_unit": price_unit,
        "evidence_text": matched_text[:240],
        "notes": source.get("notes", ""),
    }


def match_media_row(
    source: dict,
    catalog: list[dict],
    kalshi_collector: KalshiCollector | None = None,
    event_cache: dict[str, dict] | None = None,
    max_title_matches: int = 50,
) -> list[dict]:
    event_cache = event_cache or {}
    kalshi_by_ticker = kalshi_catalog_by_ticker(catalog)
    polymarket_by_slug = polymarket_catalog_by_slug(catalog)
    search_text = combined_text(source)
    normalized_search = normalize_text(search_text)
    source_lower = search_text.lower()

    identifier_hits: set[tuple[str, str]] = set()
    mentions: list[dict] = []
    ticker_event_hints: dict[str, str] = {}
    ticker_link_labels: dict[str, str] = {}

    tickers = set(source.get("candidate_tickers") or [])
    tickers.update(
        extract_kalshi_tickers(
            source.get("page_title", ""),
            source.get("excerpt", ""),
            source.get("notes", ""),
        )
    )
    source_url_ticker = extract_kalshi_market_ticker(source.get("url", ""))
    if source_url_ticker:
        tickers.add(source_url_ticker)
    for link in source.get("market_links", []) or []:
        event_hint = extract_kalshi_event_ticker(link.get("url", ""))
        ticker = extract_kalshi_market_ticker(link.get("url", ""))
        if ticker:
            tickers.add(ticker)
            if event_hint:
                ticker_event_hints[ticker] = event_hint
            label = link.get("label", "")
            if label and (
                ticker not in ticker_link_labels
                or (has_price_token(label) and not has_price_token(ticker_link_labels[ticker]))
            ):
                ticker_link_labels[ticker] = label
        fragment_tickers = extract_kalshi_tickers(extract_kalshi_fragment(link.get("url", "")))
        for fragment_ticker in fragment_tickers:
            tickers.add(fragment_ticker)
            if event_hint:
                ticker_event_hints[fragment_ticker] = event_hint
            label = link.get("label", "")
            if label and (
                fragment_ticker not in ticker_link_labels
                or (
                    has_price_token(label)
                    and not has_price_token(ticker_link_labels[fragment_ticker])
                )
            ):
                ticker_link_labels[fragment_ticker] = label
    polymarket_slugs = {
        extract_polymarket_slug(source.get("url", "")),
        *(
            extract_polymarket_slug(link.get("url", ""))
            for link in (source.get("market_links", []) or [])
        ),
    }
    polymarket_slugs.discard("")

    for ticker in sorted(tickers):
        market = kalshi_by_ticker.get(
            ticker,
            {
                "platform": "kalshi",
                "market_id": ticker,
                "title": "",
                "slug": "",
                "yes_token_id": "",
                "event_ticker": ticker_event_hints.get(ticker, ""),
                "series_ticker": "",
                "status": "",
            },
        )
        if ticker_event_hints.get(ticker) and not market.get("event_ticker"):
            market = dict(market)
            market["event_ticker"] = ticker_event_hints[ticker]
        key = (market["platform"], market["market_id"])
        if key in identifier_hits:
            continue
        identifier_hits.add(key)
        mentions.append(
            mention_record(
                source,
                market,
                "exact_identifier",
                search_text,
                ticker_link_labels.get(ticker, ticker),
            )
        )

    for market in resolve_kalshi_link_markets(source, kalshi_collector, event_cache):
        key = (market["platform"], market["market_id"])
        if key in identifier_hits:
            continue
        identifier_hits.add(key)
        mentions.append(
            mention_record(
                source,
                market,
                "exact_identifier",
                search_text,
                market["market_id"],
            )
        )

    for slug in sorted(polymarket_slugs):
        market = polymarket_by_slug.get(
            slug,
            {
                "platform": "polymarket",
                "market_id": slug,
                "title": "",
                "slug": slug,
                "yes_token_id": "",
                "event_ticker": "",
                "series_ticker": "",
                "status": "",
            },
        )
        key = (market["platform"], market["market_id"])
        if key in identifier_hits:
            continue
        identifier_hits.add(key)
        mentions.append(
            mention_record(
                source,
                market,
                "exact_identifier",
                search_text,
                slug,
            )
        )

    title_matches = 0
    for market in catalog:
        if title_matches >= max_title_matches:
            break
        normalized_title = market["normalized_title"]
        if len(normalized_title) < 24:
            continue
        if normalized_title not in normalized_search:
            continue
        key = (market["platform"], market["market_id"])
        if key in identifier_hits:
            continue
        title_matches += 1
        matched_text = market["title"]
        if matched_text.lower() not in source_lower:
            matched_text = market["title"][:240]
        mentions.append(
            mention_record(
                source,
                market,
                "exact_title",
                search_text,
                matched_text,
            )
        )
        identifier_hits.add(key)
    return mentions


def default_output_path() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(f"data/processed/market_mentions_{timestamp}.jsonl")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--media", action="append", default=[])
    parser.add_argument("--kalshi", action="append", default=[])
    parser.add_argument("--polymarket", action="append", default=[])
    parser.add_argument("--output", default=None)
    parser.add_argument("--max-title-matches", type=int, default=50)
    parser.add_argument("--resolve-kalshi-events", action="store_true")
    parser.add_argument("--event-timeout-seconds", type=float, default=8.0)
    parser.add_argument("--event-max-retries", type=int, default=1)
    args = parser.parse_args()

    media_paths = [Path(value) for value in args.media]
    kalshi_paths = [Path(value) for value in args.kalshi]
    polymarket_paths = [Path(value) for value in args.polymarket]

    catalog = build_catalog(kalshi_paths, polymarket_paths)
    kalshi_collector = None
    event_cache: dict[str, dict] = {}
    if args.resolve_kalshi_events:
        kalshi_collector = KalshiCollector(
            HttpClient(
                user_agent="PredictionMarketResearch/0.2",
                timeout_seconds=args.event_timeout_seconds,
                max_retries=args.event_max_retries,
                sleep_seconds=0.1,
            )
        )
    mentions: list[dict] = []
    for path in media_paths:
        for row in read_jsonl(path):
            mentions.extend(
                match_media_row(
                    row,
                    catalog,
                    kalshi_collector=kalshi_collector,
                    event_cache=event_cache,
                    max_title_matches=args.max_title_matches,
                )
            )

    output = Path(args.output) if args.output else default_output_path()
    count = write_jsonl(output, mentions)
    print(f"Wrote {count} market mentions to {output}")


if __name__ == "__main__":
    main()
