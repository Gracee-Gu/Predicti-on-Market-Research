from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterator

from pmresearch.http import HttpClient


def parse_jsonish_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


@dataclass
class PolymarketCollector:
    client: HttpClient
    gamma_base_url: str = "https://gamma-api.polymarket.com"
    clob_base_url: str = "https://clob.polymarket.com"
    page_limit: int = 500

    def markets(
        self, active: bool | None = None, closed: bool | None = None
    ) -> Iterator[dict]:
        offset = 0
        while True:
            params: dict[str, Any] = {"limit": self.page_limit, "offset": offset}
            if active is not None:
                params["active"] = str(active).lower()
            if closed is not None:
                params["closed"] = str(closed).lower()
            payload = self.client.get_json(f"{self.gamma_base_url}/markets", params)
            if not isinstance(payload, list):
                raise RuntimeError("Unexpected Polymarket markets response")
            for item in payload:
                item = dict(item)
                item["_parsed_clob_token_ids"] = parse_jsonish_list(item.get("clobTokenIds"))
                item["_parsed_outcomes"] = parse_jsonish_list(item.get("outcomes"))
                item["_parsed_outcome_prices"] = parse_jsonish_list(item.get("outcomePrices"))
                yield item
            if len(payload) < self.page_limit:
                break
            offset += self.page_limit

    def orderbook(self, token_id: str) -> dict:
        return self.client.get_json(f"{self.clob_base_url}/book", {"token_id": token_id})

    def midpoint(self, token_id: str) -> dict:
        return self.client.get_json(f"{self.clob_base_url}/midpoint", {"token_id": token_id})

    def spread(self, token_id: str) -> dict:
        return self.client.get_json(f"{self.clob_base_url}/spread", {"token_id": token_id})

    def last_trade_price(self, token_id: str) -> dict:
        return self.client.get_json(f"{self.clob_base_url}/last-trade-price", {"token_id": token_id})

    def price_history(
        self,
        token_id: str,
        start_ts: int | None = None,
        end_ts: int | None = None,
        fidelity: int = 60,
    ) -> dict:
        params: dict[str, Any] = {"market": token_id, "fidelity": fidelity}
        if start_ts is not None:
            params["startTs"] = start_ts
        if end_ts is not None:
            params["endTs"] = end_ts
        return self.client.get_json(f"{self.clob_base_url}/prices-history", params)
