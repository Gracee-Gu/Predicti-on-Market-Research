from __future__ import annotations

from typing import Any


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize_polymarket_orderbook(book: dict[str, Any], depth_band: float = 0.05) -> dict[str, float | None]:
    bids = book.get("bids") or []
    asks = book.get("asks") or []
    best_bid = _to_float(bids[0].get("price")) if bids else None
    best_ask = _to_float(asks[0].get("price")) if asks else None
    midpoint = (best_bid + best_ask) / 2 if best_bid is not None and best_ask is not None else None
    spread = best_ask - best_bid if best_bid is not None and best_ask is not None else None
    relative_spread = spread / midpoint if spread is not None and midpoint not in (None, 0.0) else None

    bid_depth = 0.0
    if best_bid is not None:
        bid_depth = sum(
            _to_float(level.get("size")) or 0.0
            for level in bids
            if (_to_float(level.get("price")) or -1.0) >= best_bid - depth_band
        )
    ask_depth = 0.0
    if best_ask is not None:
        ask_depth = sum(
            _to_float(level.get("size")) or 0.0
            for level in asks
            if (_to_float(level.get("price")) or 2.0) <= best_ask + depth_band
        )
    return {
        "bid": best_bid,
        "ask": best_ask,
        "price": midpoint,
        "relative_spread": relative_spread,
        "depth_band": bid_depth + ask_depth if (bid_depth or ask_depth) else None,
    }


def summarize_kalshi_orderbook(
    payload: dict[str, Any],
    depth_band: float = 0.05,
) -> dict[str, float | None]:
    orderbook = payload.get("orderbook_fp") or {}
    yes_bids = orderbook.get("yes_dollars") or []
    no_bids = orderbook.get("no_dollars") or []
    best_yes_bid = _to_float(yes_bids[0][0]) if yes_bids else None
    best_no_bid = _to_float(no_bids[0][0]) if no_bids else None
    best_yes_ask = 1.0 - best_no_bid if best_no_bid is not None else None
    midpoint = (
        (best_yes_bid + best_yes_ask) / 2
        if best_yes_bid is not None and best_yes_ask is not None
        else None
    )
    spread = (
        best_yes_ask - best_yes_bid
        if best_yes_bid is not None and best_yes_ask is not None
        else None
    )
    relative_spread = spread / midpoint if spread is not None and midpoint not in (None, 0.0) else None

    bid_depth = 0.0
    if best_yes_bid is not None:
        bid_depth = sum(
            _to_float(level[1]) or 0.0
            for level in yes_bids
            if (_to_float(level[0]) or -1.0) >= best_yes_bid - depth_band
        )
    ask_depth = 0.0
    if best_no_bid is not None:
        ask_depth = sum(
            _to_float(level[1]) or 0.0
            for level in no_bids
            if (_to_float(level[0]) or -1.0) >= best_no_bid - depth_band
        )
    return {
        "bid": best_yes_bid,
        "ask": best_yes_ask,
        "price": midpoint,
        "relative_spread": relative_spread,
        "depth_band": bid_depth + ask_depth if (bid_depth or ask_depth) else None,
    }
