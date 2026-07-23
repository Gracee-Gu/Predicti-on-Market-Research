# Stage 2 Runbook

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Tests

```bash
pytest -q
ruff check .
```

## Collect market metadata

```bash
python scripts/collect_kalshi.py --status open
python scripts/collect_kalshi.py --status closed
python scripts/collect_kalshi.py --historical --max-pages 5
python scripts/collect_kalshi.py --historical --tickers KXEXAMPLE-25,KXEXAMPLE2-25
python scripts/export_kalshi_tickers.py --input data/inventory/corpus_inventory.csv
python scripts/collect_kalshi_historical_batch.py --tickers-file data/interim/kalshi_tickers.txt

python scripts/collect_polymarket.py --active true --closed false
python scripts/collect_polymarket.py --active false --closed true
```

Kalshi historical market collection is intentionally guarded. The historical endpoint does not support date-range filters, so the safe workflow is:

- collect and audit the media seed corpus first;
- identify matched Kalshi tickers, event tickers, or series tickers;
- export matched Kalshi tickers to `data/interim/kalshi_tickers.txt`;
- fetch historical markets by `--tickers`, `--event-ticker`, or `--series-ticker`;
- use `collect_kalshi_historical_batch.py` for larger matched-ticker lists;
- use `--max-pages` only for bounded probes;
- use `--allow-unbounded-historical` only if you explicitly want the full archive and have the disk budget.

Raw outputs are gitignored.

## Collect media seeds

`config/media_sources.csv` now ships with a small starter seed corpus of verified URLs.
Add, replace, or prune rows there before collection as needed.

```bash
python scripts/collect_media.py
```

Full text is disabled by default. Keep local raw outputs private.

## Build safe inventory

```bash
python scripts/build_inventory.py \
  --kalshi data/raw/kalshi/markets_<timestamp>.jsonl \
  --polymarket data/raw/polymarket/markets_<timestamp>.jsonl \
  --media data/raw/media/media_<timestamp>.jsonl \
  --output data/inventory/corpus_inventory.csv
```

## Required manual checks

- verify partnership evidence;
- resolve ambiguous market matches;
- confirm UTC conversions;
- distinguish current-only order book from historical quality;
- inspect extraction failures;
- ensure no copyrighted full text is staged for Git.

## Advance Stage 3 readiness

Use the enriched media collector output to extract exact-identifier market mentions:

```bash
python scripts/match_market_mentions.py \
  --media data/raw/media/media_<timestamp>.jsonl \
  --kalshi data/raw/kalshi/markets_<timestamp>.jsonl \
  --polymarket data/raw/polymarket/markets_<timestamp>.jsonl
```

Use those mentions to collect publication-time price and activity matches:

```bash
python scripts/collect_publication_time_matches.py \
  --mentions data/processed/market_mentions_<timestamp>.jsonl
```

If spread or depth is central, start a prospective snapshot series for the matched markets:

```bash
python scripts/collect_prospective_snapshots.py \
  --mentions data/processed/market_mentions_<timestamp>.jsonl
```

Audit the current readiness thresholds at any point:

```bash
python scripts/audit_stage3_readiness.py \
  --media data/raw/media/media_<timestamp>.jsonl \
  --mentions data/processed/market_mentions_<timestamp>.jsonl \
  --snapshots data/processed/market_snapshots_<timestamp>.jsonl \
  --snapshots data/processed/prospective_snapshots_<timestamp>.jsonl
```

Current passing processed file set as of 2026-07-23:

- mentions: `data/processed/market_mentions_probe_v3.jsonl`
- mentions: `data/processed/market_mentions_kalshi_archive_45_v3.jsonl`
- snapshots: `data/processed/market_snapshots_probe_v3.jsonl`
- snapshots: `data/processed/market_snapshots_kalshi_archive_45_v3.jsonl`
- snapshots: `data/processed/prospective_snapshots_kalshi_archive_30.jsonl`

Current passing readiness audit command:

```bash
python scripts/audit_stage3_readiness.py \
  --media data/raw/media/media_enriched_probe_v2.jsonl \
  --media data/raw/media/media_kalshi_archive_45.jsonl \
  --media data/raw/media/media_partner_cnn.jsonl \
  --media data/raw/media/media_independent_extra.jsonl \
  --media data/raw/media/media_independent_ap_supplement.jsonl \
  --media data/raw/media/media_independent_ap_supplement_2.jsonl \
  --media data/raw/media/media_regulatory_extra.jsonl \
  --media data/raw/media/media_regulatory_supplement.jsonl \
  --media data/raw/media/media_regulatory_supplement_2.jsonl \
  --mentions data/processed/market_mentions_probe_v3.jsonl \
  --mentions data/processed/market_mentions_kalshi_archive_45_v3.jsonl \
  --snapshots data/processed/market_snapshots_probe_v3.jsonl \
  --snapshots data/processed/market_snapshots_kalshi_archive_45_v3.jsonl \
  --snapshots data/processed/prospective_snapshots_kalshi_archive_30.jsonl
```

Suggested final staging command for the current Stage 3-ready deliverables:

```bash
git add \
  README_STAGE2.md \
  docs/runbook_stage2.md \
  config/media_sources_kalshi_archive.csv \
  config/media_sources_kalshi_archive_45.csv \
  config/media_sources_partner_cnn.csv \
  config/media_sources_independent_extra.csv \
  config/media_sources_independent_ap_supplement.csv \
  config/media_sources_independent_ap_supplement_2.csv \
  config/media_sources_regulatory_extra.csv \
  config/media_sources_regulatory_supplement.csv \
  config/media_sources_regulatory_supplement_2.csv \
  scripts/collect_media.py \
  scripts/match_market_mentions.py \
  scripts/collect_publication_time_matches.py \
  scripts/collect_prospective_snapshots.py \
  scripts/audit_stage3_readiness.py \
  scripts/discover_kalshi_news_archive.py \
  src/pmresearch/collectors/kalshi.py \
  src/pmresearch/collectors/media.py \
  src/pmresearch/http.py \
  src/pmresearch/market_utils.py \
  src/pmresearch/snapshots.py \
  tests/test_collectors.py \
  tests/test_stage3_scripts.py \
  data/interim/kalshi_publication_tickers.txt \
  data/processed/market_mentions_probe_v3.jsonl \
  data/processed/market_mentions_kalshi_archive_45_v3.jsonl \
  data/processed/market_snapshots_probe_v3.jsonl \
  data/processed/market_snapshots_kalshi_archive_45_v3.jsonl \
  data/processed/prospective_snapshots_kalshi_archive_30.jsonl
```
