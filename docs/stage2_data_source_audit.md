# Stage 2 Data-Source Audit

## Decision

Stage 2 is technically feasible with a two-tier design:

1. **Retrospective evidence:** market metadata, trades, candlesticks/price history, settlement, and publication-time matching.
2. **Prospective evidence:** scheduled order-book snapshots for spread and depth from the date collection begins.

Historical order-book depth is generally not reconstructible from candles or trade prints. Therefore, depth is confirmatory only for prospective observations with actual snapshots. Retrospective analyses must not impute historical depth.

## Kalshi

Official production base:

`https://external-api.kalshi.com/trade-api/v2`

Public market-data endpoints do not require authentication. Kalshi partitions older data into live and historical tiers. The historical cutoff is dynamic and must be retrieved at collection time.

Supported research inputs:

- live/recent markets;
- historical markets;
- live/recent trades;
- historical trades;
- market candlesticks;
- historical-market candlesticks;
- current order book;
- market/event/series metadata.

Implication: an article published in the retrospective window can often be aligned to hourly candles and trades. A historical spread or depth measure is unavailable unless a contemporaneous archive exists.

## Polymarket

Official metadata base:

`https://gamma-api.polymarket.com`

Official CLOB base:

`https://clob.polymarket.com`

Supported research inputs:

- market and event metadata;
- outcome token IDs;
- current order book;
- current midpoint and spread;
- last trade price;
- price history;
- volume/liquidity metadata.

Implication: price histories support publication-time price alignment, while current order books support prospective depth snapshots. Gamma liquidity fields are useful metadata but must not be treated as a directly comparable substitute for Kalshi depth.

## Media corpus

Media collection is seed-driven, not an unrestricted web scrape. Every source row records:

- URL;
- source type;
- platform;
- publication time;
- genre;
- category;
- partnership evidence;
- notes.

Full article text is local-only by default. The repository stores URLs, metadata, hashes, character counts, and short excerpts. This reduces copyright and reproducibility risk.

## Matching strategy

A market mention is matched using:

1. exact ticker, slug, token, or embedded URL;
2. quoted market question/title;
3. publication-time eligibility;
4. manual adjudication for ambiguous cases.

Every match receives a status:

- `exact_identifier`;
- `exact_title`;
- `fuzzy_reviewed`;
- `ambiguous`;
- `unmatched`.

Ambiguous and unmatched mentions are excluded from confirmatory market-quality analysis.

## Snapshot statuses

- `historical_price_matched`;
- `historical_trade_matched`;
- `prospective_orderbook_matched`;
- `current_only_not_aligned`;
- `unavailable`.

`current_only_not_aligned` must not be used as evidence of quality at the article publication date.

## Feasibility verdict

**PASS, with a required distinction between retrospective price/activity quality and prospective spread/depth quality.**
