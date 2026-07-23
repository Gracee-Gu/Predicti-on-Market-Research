# Stage 3 Runbook

From repo root:

```bash
.venv/bin/python scripts/build_stage3_sampling_frame.py
.venv/bin/python scripts/prepare_stage3_coder_packets.py \
  --input data/annotations/coding_sheet.csv \
  --output-a data/annotations/coder_a_sheet.csv \
  --output-b data/annotations/coder_b_sheet.csv
# two coders independently fill data/annotations/coder_a_sheet.csv and data/annotations/coder_b_sheet.csv
.venv/bin/python scripts/merge_stage3_coder_files.py \
  --coder-a data/annotations/coder_a_sheet_completed.csv \
  --coder-b data/annotations/coder_b_sheet_completed.csv \
  --output data/annotations/coding_sheet_completed.csv
.venv/bin/python scripts/check_stage3_reliability.py \
  --input data/annotations/coding_sheet_completed.csv
.venv/bin/python scripts/build_stage3_adjudication_sheet.py \
  --input data/annotations/coding_sheet_completed.csv \
  --output data/annotations/adjudication_sheet.csv
# fill adjudicated values only for disagreement rows
.venv/bin/python scripts/finalize_stage3_adjudication.py \
  --completed data/annotations/coding_sheet_completed.csv \
  --adjudication data/annotations/adjudication_sheet_completed.csv \
  --output data/annotations/adjudicated_annotations.csv
.venv/bin/python scripts/build_stage3_analytic_dataset.py \
  --annotations data/annotations/adjudicated_annotations.csv
.venv/bin/python scripts/analyze_stage3.py
.venv/bin/python scripts/audit_stage3.py
uv run pytest
```

Do not commit copyrighted full article text. Store stable identifiers, excerpts permitted by the corpus protocol, hashes, and coder judgments. Never backfill historical spread/depth with a current snapshot.
