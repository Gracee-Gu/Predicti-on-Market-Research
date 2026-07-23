from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse


KALSHI_TICKER_RE = re.compile(r"\b[A-Za-z]{2,}[A-Za-z0-9]*(?:-[A-Za-z0-9.]+)+\b")


def normalize_text(value: str) -> str:
    lowered = value.lower()
    cleaned = re.sub(r"[^a-z0-9%$¢]+", " ", lowered)
    return re.sub(r"\s+", " ", cleaned).strip()


def extract_kalshi_tickers(*values: str) -> list[str]:
    seen: set[str] = set()
    tickers: list[str] = []
    for value in values:
        for match in KALSHI_TICKER_RE.findall(value or ""):
            candidate = match.upper()
            if not candidate.startswith("KX"):
                continue
            if candidate not in seen:
                seen.add(candidate)
                tickers.append(candidate)
    return tickers


def extract_kalshi_market_ticker(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if "kalshi.com" not in parsed.netloc.lower():
        return ""
    query_ticker = parse_qs(parsed.query).get("op_market_ticker", [""])[0].strip().upper()
    if query_ticker.startswith("KX"):
        return query_ticker
    parts = [part for part in parsed.path.split("/") if part]
    if "markets" not in parts or not parts:
        return ""
    candidate = parts[-1].strip().upper()
    return candidate if candidate.startswith("KX") else ""


def extract_kalshi_event_ticker(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if "kalshi.com" not in parsed.netloc.lower():
        return ""
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0] != "markets":
        return ""
    candidate = parts[1].strip().upper()
    return candidate if candidate.startswith("KX") or candidate.isalpha() else candidate


def extract_kalshi_fragment(url: str) -> str:
    if not url:
        return ""
    fragment = urlparse(url).fragment.strip().upper()
    return fragment


def loose_normalize_identifier(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", value.upper())


def infer_kalshi_event_ticker(market_ticker: str) -> str:
    if not market_ticker or "-" not in market_ticker:
        return ""
    return market_ticker.rsplit("-", 1)[0].upper()


def extract_polymarket_slug(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if "polymarket.com" not in parsed.netloc.lower():
        return ""
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return ""
    return parts[-1].strip().lower()


def choose_polymarket_yes_token(market: dict[str, Any]) -> str:
    outcomes = market.get("_parsed_outcomes") or []
    token_ids = market.get("_parsed_clob_token_ids") or []
    for outcome, token_id in zip(outcomes, token_ids):
        if isinstance(outcome, str) and outcome.strip().lower() == "yes":
            return str(token_id)
    return str(token_ids[0]) if token_ids else ""


def parse_publication_datetime(value: str) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        try:
            parsed = datetime.fromisoformat(raw + "T00:00:00+00:00")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def to_unix_seconds(value: datetime | None) -> int | None:
    if value is None:
        return None
    return int(value.timestamp())
