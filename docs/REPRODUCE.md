# Reproducing the Analysis

All commands run from the repository root with the project virtual environment active
(`source .venv/bin/activate`) and `PYTHONPATH=.` set, since one collector module imports
absolutely (`from pmresearch...`).

## 1. Collect raw data (optional — raw data is git-ignored, not required to reproduce the paper)

```bash
python scripts/collect_kalshi.py
python scripts/collect_polymarket.py
python scripts/collect_media.py --config config/media_sources.csv
python scripts/match_market_mentions.py --media data/raw/media/<file>.jsonl \
  --kalshi data/raw/kalshi/<file>.jsonl --polymarket data/raw/polymarket/<file>.jsonl
python scripts/collect_publication_time_matches.py --mentions data/processed/<mentions>.jsonl
```

Raw article text is never committed (see `docs/corpus_protocol.md`); only URLs, hashes, short
excerpts, and derived labels are retained.

## 2. Classification

The seven framing constructs are scored by a disclosed, deterministic keyword classifier, not by
human coders (see the paper's §3.3 and Appendix C for the full disclosure and exact rules):

```bash
python scripts/build_stage3_sampling_frame.py
python scripts/auto_fill_stage3_ai_coders.py \
  --coder-a-input data/annotations/coder_a_sheet.csv \
  --coder-b-input data/annotations/coder_b_sheet.csv \
  --coder-a-output data/annotations/coder_a_sheet_completed.csv \
  --coder-b-output data/annotations/coder_b_sheet_completed.csv
python scripts/merge_stage3_coder_files.py \
  --coder-a data/annotations/coder_a_sheet_completed.csv \
  --coder-b data/annotations/coder_b_sheet_completed.csv \
  --output data/annotations/coding_sheet_completed.csv
python scripts/build_stage3_adjudication_sheet.py \
  --input data/annotations/coding_sheet_completed.csv \
  --output data/annotations/adjudication_sheet.csv
python scripts/finalize_stage3_adjudication.py \
  --completed data/annotations/coding_sheet_completed.csv \
  --adjudication data/annotations/adjudication_sheet_completed.csv \
  --output data/annotations/adjudicated_annotations.csv
```

The annotation files retain `coder_id`/`double_code` fields from an earlier human-double-coding
design; as run above, both "coders" are the same classifier, and no inter-coder reliability
statistic is computed or reported in the paper.

## 3. Build the analytic dataset

```bash
python scripts/build_stage3_analytic_dataset.py \
  --annotations data/annotations/adjudicated_annotations.csv \
  --snapshots-glob "data/processed/market_snapshots_kalshi_archive_45_v4.jsonl" \
  --output data/analysis/article_market_dataset.csv
```

The paper does not report a regression of overreach severity on the other constructs, because
severity is deterministically composed from them (§3.3); the scripts that once produced that
regression have been removed from the repository since their output was never part of the paper.

## 4. Independent market-quality verification and figures

```bash
python scripts/make_figures.py
```

This reads `data/analysis/article_market_dataset.csv` and the verification artifacts in
`outputs/verification/` (ticker-liveness audit, real Kalshi candlestick pulls, cross-source frame
tags), and writes seven PNG figures to `outputs/verification/figures/` (copy them into
`paper/final/figures/` to rebuild the manuscript).

## 5. Render the manuscript

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="paper/final/manuscript.pdf" \
  "file://$(pwd)/paper/final/manuscript.html"
```

Any recent Chromium build works; the manuscript is plain HTML/CSS (two-column print layout,
`@page` page numbering) with no external dependencies, so no LaTeX or pandoc installation is
required.

## 6. Tests

```bash
uv run pytest
```
