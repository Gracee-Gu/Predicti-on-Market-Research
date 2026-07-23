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
from pmresearch.snapshots import summarize_kalshi_orderbook, summarize_polymarket_orderbook

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - dependency fallback
    yaml = None


def default_output_path() -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(f"data/processed/prospective_snapshots_{timestamp}.jsonl")


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


def unique_targets(mentions_path: Path) -> list[dict]:
    seen: set[tuple[str, str, str]] = set()
    targets: list[dict] = []
    for row in read_jsonl(mentions_path):
        key = (row.get("platform", ""), row.get("market_id", ""), row.get("token_id", ""))
        if key in seen:
            continue
        seen.add(key)
        targets.append(row)
    return targets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mentions", required=True)
    parser.add_argument("--config", default="config/stage2.yaml")
    parser.add_argument("--output", default=None)
    parser.add_argument("--kalshi-depth", type=int, default=5)
    parser.add_argument("--depth-band", type=float, default=0.05)
    args = parser.parse_args()

    user_agent, sleep_seconds = load_runtime_settings(Path(args.config))
    client = HttpClient(
        user_agent=user_agent,
        sleep_seconds=sleep_seconds,
    )
    kalshi = KalshiCollector(client)
    polymarket = PolymarketCollector(client)

    observed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    rows: list[dict] = []
    for target in unique_targets(Path(args.mentions)):
        row = {
            "snapshot_id": f"{target['platform']}:{target['market_id']}:{observed_at}",
            "platform": target["platform"],
            "market_id": target["market_id"],
            "token_id": target.get("token_id", ""),
            "observed_at": observed_at,
            "target_time": "",
            "alignment_seconds": 0,
            "snapshot_status": "unavailable",
            "source_endpoint": "",
        }
        try:
            if target["platform"] == "kalshi":
                payload = kalshi.orderbook(target["market_id"], depth=args.kalshi_depth)
                row.update(
                    summarize_kalshi_orderbook(payload, depth_band=args.depth_band)
                )
                row["snapshot_status"] = "prospective_orderbook_matched"
                row["source_endpoint"] = "kalshi_orderbook"
            else:
                token_id = target.get("token_id", "")
                if not token_id:
                    row["source_endpoint"] = "missing_token_id"
                else:
                    payload = polymarket.orderbook(token_id)
                    row.update(
                        summarize_polymarket_orderbook(payload, depth_band=args.depth_band)
                    )
                    row["snapshot_status"] = "prospective_orderbook_matched"
                    row["source_endpoint"] = "polymarket_orderbook"
        except Exception as exc:  # pragma: no cover - network behavior
            row["error"] = str(exc)
        rows.append(row)

    output = Path(args.output) if args.output else default_output_path()
    count = write_jsonl(output, rows)
    print(f"Wrote {count} prospective snapshots to {output}")


if __name__ == "__main__":
    main()
