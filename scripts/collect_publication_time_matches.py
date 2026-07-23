from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from _bootstrap import add_src_to_path

add_src_to_path()

from pmresearch.collectors.kalshi import KalshiCollector
from pmresearch.collectors.polymarket import PolymarketCollector
from pmresearch.http import HttpClient
from pmresearch.io import read_jsonl, write_jsonl
from pmresearch.market_utils import parse_publication_datetime, to_unix_seconds

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - dependency fallback
    yaml = None


def nearest_kalshi_trade(trades: list[dict], target_ts: int) -> dict | None:
    if not trades:
        return None
    return min(
        trades,
        key=lambda row: abs(
            int(parse_publication_datetime(row.get("created_time", "")).timestamp()) - target_ts
        ),
    )


def nearest_kalshi_candlestick(candlesticks: list[dict], target_ts: int) -> dict | None:
    if not candlesticks:
        return None
    return min(candlesticks, key=lambda row: abs(int(row.get("end_period_ts", target_ts)) - target_ts))


def candlestick_price(row: dict) -> str:
    price = row.get("price", {}) or {}
    for field in ("mean_dollars", "close_dollars", "mean", "close", "previous"):
        value = price.get(field)
        if value not in (None, ""):
            return str(value)
    yes_bid = row.get("yes_bid", {}) or {}
    yes_ask = row.get("yes_ask", {}) or {}
    bid_close = yes_bid.get("close_dollars", yes_bid.get("close"))
    ask_close = yes_ask.get("close_dollars", yes_ask.get("close"))
    try:
        if bid_close not in (None, "") and ask_close not in (None, ""):
            return f"{(float(bid_close) + float(ask_close)) / 2:.4f}"
    except ValueError:
        pass
    if bid_close not in (None, ""):
        return str(bid_close)
    return str(ask_close or "")


def source_quoted_price(mention: dict) -> str:
    raw_value = str(mention.get("quoted_price", "")).strip()
    unit = str(mention.get("quoted_price_unit", "")).strip().lower()
    if not raw_value:
        return ""
    try:
        numeric = float(raw_value)
    except ValueError:
        return raw_value
    if unit in {"%", "percent"}:
        return f"{numeric / 100:.4f}"
    if unit in {"cent", "cents", "¢"}:
        return f"{numeric / 100:.4f}"
    return raw_value


def collect_kalshi_match(
    collector: KalshiCollector,
    mention: dict,
    target_ts: int,
    window_seconds: int,
    historical_cutoff_ts: int | None,
) -> dict:
    market_id = mention["market_id"]
    quoted_price = source_quoted_price(mention)
    if quoted_price:
        return {
            "snapshot_status": "historical_price_matched",
            "observed_at": mention.get("publication_time", ""),
            "alignment_seconds": 0,
            "price": quoted_price,
            "trailing_volume": "",
            "trade_count": "",
            "source_endpoint": "source_quoted_price",
        }
    trade_historical = historical_cutoff_ts is not None and target_ts < historical_cutoff_ts
    trade_errors: list[str] = []
    trades: list[dict] = []
    source_endpoint = "historical_trades" if trade_historical else "live_trades"
    try:
        trades = list(
            collector.trades(
                ticker=market_id,
                min_ts=target_ts - window_seconds,
                max_ts=target_ts + window_seconds,
                historical=trade_historical,
            )
        )
    except Exception as exc:  # pragma: no cover - network behavior
        trade_errors.append(str(exc))
        trades = []

    nearest = nearest_kalshi_trade(trades, target_ts)
    if nearest:
        observed_at = parse_publication_datetime(nearest.get("created_time", ""))
        observed_ts = to_unix_seconds(observed_at)
        return {
            "snapshot_status": "historical_trade_matched",
            "observed_at": nearest.get("created_time", ""),
            "alignment_seconds": abs((observed_ts or target_ts) - target_ts),
            "price": nearest.get("yes_price_dollars", ""),
            "trailing_volume": sum(float(row.get("count_fp", 0.0) or 0.0) for row in trades),
            "trade_count": len(trades),
            "source_endpoint": source_endpoint,
        }

    series_ticker = mention.get("series_ticker", "")
    event_ticker = mention.get("event_ticker", "")
    if not event_ticker or not series_ticker:
        try:
            market_payload = (
                collector.historical_market(market_id)
                if trade_historical
                else collector.market(market_id)
            )
        except Exception as exc:  # pragma: no cover - network behavior
            trade_errors.append(str(exc))
            market_payload = {}
        event_ticker = event_ticker or market_payload.get("event_ticker", "")
        series_ticker = series_ticker or market_payload.get("series_ticker", "")
    if not series_ticker and event_ticker:
        try:
            event_payload = collector.event(event_ticker, with_nested_markets=False)
            series_ticker = event_payload.get("event", {}).get("series_ticker", "")
        except Exception as exc:  # pragma: no cover - network behavior
            trade_errors.append(str(exc))
            series_ticker = ""
    if series_ticker and event_ticker:
        try:
            candlesticks = collector.candlesticks(
                series_ticker=series_ticker,
                ticker=market_id,
                start_ts=target_ts - window_seconds,
                end_ts=target_ts + window_seconds,
                period_interval=60,
                historical=trade_historical,
            )
        except Exception as exc:  # pragma: no cover - network behavior
            trade_errors.append(str(exc))
            candlesticks = []
        nearest_candle = nearest_kalshi_candlestick(candlesticks, target_ts)
        if nearest_candle:
            observed_ts = int(nearest_candle.get("end_period_ts", target_ts))
            observed_at = datetime.fromtimestamp(observed_ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
            return {
                "snapshot_status": "historical_price_matched",
                "observed_at": observed_at,
                "alignment_seconds": abs(observed_ts - target_ts),
                "price": candlestick_price(nearest_candle),
                "trailing_volume": nearest_candle.get("volume_fp", nearest_candle.get("volume", "")),
                "trade_count": "",
                "source_endpoint": "historical_candlesticks" if trade_historical else "live_candlesticks",
            }

    payload = {
        "snapshot_status": "unavailable",
        "source_endpoint": source_endpoint if trades or not trade_errors else "kalshi_trades_error",
    }
    if trade_errors:
        payload["error"] = trade_errors[0]
    return payload


def collect_polymarket_match(
    collector: PolymarketCollector,
    mention: dict,
    target_ts: int,
    window_seconds: int,
    fidelity: int,
) -> dict:
    token_id = mention.get("token_id", "")
    if not token_id:
        return {"snapshot_status": "unavailable", "source_endpoint": "missing_token_id"}
    try:
        payload = collector.price_history(
            token_id=token_id,
            start_ts=target_ts - window_seconds,
            end_ts=target_ts + window_seconds,
            fidelity=fidelity,
        )
        history = payload.get("history", []) if isinstance(payload, dict) else []
        if not history:
            return {
                "snapshot_status": "unavailable",
                "source_endpoint": "polymarket_price_history",
            }
        nearest = min(history, key=lambda row: abs(int(row.get("t", target_ts)) - target_ts))
        observed_ts = int(nearest.get("t", target_ts))
        observed_at = datetime.fromtimestamp(observed_ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        return {
            "snapshot_status": "historical_price_matched",
            "observed_at": observed_at,
            "alignment_seconds": abs(observed_ts - target_ts),
            "price": nearest.get("p", ""),
            "source_endpoint": "polymarket_price_history",
        }
    except Exception as exc:  # pragma: no cover - network behavior
        return {
            "snapshot_status": "unavailable",
            "source_endpoint": "polymarket_price_history_error",
            "error": str(exc),
        }


def default_output_path() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(f"data/processed/market_snapshots_{timestamp}.jsonl")


def load_runtime_settings(config_path: Path) -> tuple[str, float]:
    default_user_agent = "PredictionMarketResearch/0.2"
    default_sleep = 1.0
    if yaml is None:
        return default_user_agent, default_sleep
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return (
        config["project"]["user_agent"],
        float(config["media"]["request_sleep_seconds"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mentions", required=True)
    parser.add_argument("--config", default="config/stage2.yaml")
    parser.add_argument("--output", default=None)
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--polymarket-fidelity", type=int, default=60)
    args = parser.parse_args()

    user_agent, sleep_seconds = load_runtime_settings(Path(args.config))
    client = HttpClient(
        user_agent=user_agent,
        sleep_seconds=sleep_seconds,
    )
    kalshi = KalshiCollector(client)
    polymarket = PolymarketCollector(client)
    window_seconds = args.window_hours * 3600
    cutoff = kalshi.historical_cutoff()
    historical_cutoff_ts = to_unix_seconds(parse_publication_datetime(cutoff.get("trades_created_ts", "")))

    rows: list[dict] = []
    for mention in read_jsonl(Path(args.mentions)):
        publication_dt = parse_publication_datetime(mention.get("publication_time", ""))
        target_ts = to_unix_seconds(publication_dt)
        if target_ts is None:
            rows.append(
                {
                    "snapshot_id": mention["mention_id"],
                    "platform": mention["platform"],
                    "market_id": mention["market_id"],
                    "token_id": mention.get("token_id", ""),
                    "target_time": mention.get("publication_time", ""),
                    "snapshot_status": "unavailable",
                    "source_endpoint": "missing_publication_time",
                }
            )
            continue

        if mention["platform"] == "kalshi":
            payload = collect_kalshi_match(
                kalshi,
                mention,
                target_ts,
                window_seconds,
                historical_cutoff_ts,
            )
        else:
            payload = collect_polymarket_match(
                polymarket,
                mention,
                target_ts,
                window_seconds,
                args.polymarket_fidelity,
            )
        row = {
            "snapshot_id": mention["mention_id"],
            "platform": mention["platform"],
            "market_id": mention["market_id"],
            "token_id": mention.get("token_id", ""),
            "target_time": mention.get("publication_time", ""),
        }
        row.update(payload)
        rows.append(row)

    output = Path(args.output) if args.output else default_output_path()
    count = write_jsonl(output, rows)
    print(f"Wrote {count} publication-time matches to {output}")


if __name__ == "__main__":
    main()
