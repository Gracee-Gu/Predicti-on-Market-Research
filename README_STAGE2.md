# Stage 2 — Corpus and Data Sources

This stage adds reproducible collectors and governance for the media–market corpus.

Start with `docs/runbook_stage2.md`.

Important: historical prices/trades and prospective order-book snapshots are different evidence classes. Never use a current order book as a proxy for quality at an earlier publication date.

Kalshi historical markets should be collected with explicit bounds. The API supports ticker, event, and series filters, but not date-range filters for historical market metadata.
