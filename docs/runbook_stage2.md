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
