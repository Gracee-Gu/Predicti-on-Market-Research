from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Iterator

from pmresearch.http import HttpClient


@dataclass
class KalshiCollector:
    client: HttpClient
    base_url: str = "https://external-api.kalshi.com/trade-api/v2"
    page_limit: int = 1000

    def _paginate(
        self,
        path: str,
        root_key: str,
        params: dict[str, Any] | None = None,
        max_pages: int | None = None,
    ) -> Iterator[dict]:
        query = dict(params or {})
        query.setdefault("limit", self.page_limit)
        cursor = None
        pages_fetched = 0
        while True:
            if cursor:
                query["cursor"] = cursor
            elif "cursor" in query:
                query.pop("cursor")
            payload = self.client.get_json(f"{self.base_url}{path}", query)
            pages_fetched += 1
            for item in payload.get(root_key, []):
                yield item
            if max_pages is not None and pages_fetched >= max_pages:
                break
            cursor = payload.get("cursor")
            if not cursor:
                break

    @staticmethod
    def _historical_market_params(
        tickers: Sequence[str] | None = None,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        exclude_mve: bool = False,
    ) -> dict[str, Any]:
        filters_selected = sum(
            [
                bool(tickers),
                bool(event_ticker),
                bool(series_ticker),
                bool(exclude_mve),
            ]
        )
        if filters_selected > 1:
            raise ValueError(
                "Historical market filters are mutually exclusive; choose only one of "
                "tickers, event_ticker, series_ticker, or exclude_mve."
            )

        params: dict[str, Any] = {}
        if tickers:
            params["tickers"] = ",".join(tickers)
        elif event_ticker:
            params["event_ticker"] = event_ticker
        elif series_ticker:
            params["series_ticker"] = series_ticker
        elif exclude_mve:
            params["mve_filter"] = "exclude"
        return params

    def historical_cutoff(self) -> dict:
        return self.client.get_json(f"{self.base_url}/historical/cutoff")

    def event(self, event_ticker: str, with_nested_markets: bool = False) -> dict:
        return self.client.get_json(
            f"{self.base_url}/events/{event_ticker}",
            {"with_nested_markets": str(with_nested_markets).lower()},
        )

    def markets(
        self,
        status: str | None = None,
        historical: bool = False,
        tickers: Sequence[str] | None = None,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        exclude_mve: bool = False,
        max_pages: int | None = None,
    ) -> Iterator[dict]:
        path = "/historical/markets" if historical else "/markets"
        params = {"status": status} if status and not historical else {}
        if not historical:
            if tickers:
                params["tickers"] = ",".join(tickers)
            if event_ticker:
                params["event_ticker"] = event_ticker
            if series_ticker:
                params["series_ticker"] = series_ticker
            if exclude_mve:
                params["mve_filter"] = "exclude"
        if historical:
            params.update(
                self._historical_market_params(
                    tickers=tickers,
                    event_ticker=event_ticker,
                    series_ticker=series_ticker,
                    exclude_mve=exclude_mve,
                )
            )
        yield from self._paginate(path, "markets", params, max_pages=max_pages)

    def market(self, ticker: str) -> dict:
        payload = self.client.get_json(f"{self.base_url}/markets/{ticker}")
        return payload.get("market", {})

    def historical_market(self, ticker: str) -> dict:
        payload = self.client.get_json(f"{self.base_url}/historical/markets/{ticker}")
        return payload.get("market", {})

    def trades(
        self,
        ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        historical: bool = False,
    ) -> Iterator[dict]:
        path = "/historical/trades" if historical else "/markets/trades"
        params = {}
        if ticker:
            params["ticker"] = ticker
        if min_ts is not None:
            params["min_ts"] = min_ts
        if max_ts is not None:
            params["max_ts"] = max_ts
        yield from self._paginate(path, "trades", params)

    def candlesticks(
        self,
        series_ticker: str,
        ticker: str,
        start_ts: int,
        end_ts: int,
        period_interval: int = 60,
        historical: bool = False,
    ) -> list[dict]:
        if historical:
            path = f"/historical/markets/{ticker}/candlesticks"
        else:
            path = f"/series/{series_ticker}/markets/{ticker}/candlesticks"
        payload = self.client.get_json(
            f"{self.base_url}{path}",
            {
                "start_ts": start_ts,
                "end_ts": end_ts,
                "period_interval": period_interval,
            },
        )
        return payload.get("candlesticks", [])

    def orderbook(self, ticker: str, depth: int = 0) -> dict:
        return self.client.get_json(
            f"{self.base_url}/markets/{ticker}/orderbook",
            {"depth": depth},
        )
