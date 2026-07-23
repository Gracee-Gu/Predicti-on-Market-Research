#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT="$ROOT/outputs/stage7/alignment_audit.json"
MANUSCRIPT="$ROOT/paper/final/manuscript_stage7.md"
OUTPUT="$ROOT/paper/final/manuscript_stage7.pdf"

if [[ ! -f "$AUDIT" ]]; then
  echo "Missing Stage 7 alignment audit." >&2
  exit 2
fi

STATUS="$(python - "$AUDIT" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8")).get("status", ""))
PY
)"

if [[ "$STATUS" != "finalization_ready" ]]; then
  echo "Refusing to build a final PDF because Stage 7 status is: $STATUS" >&2
  echo "Complete the empirical recovery plan and rerun the alignment audit." >&2
  exit 3
fi

if [[ ! -f "$MANUSCRIPT" ]]; then
  echo "Missing $MANUSCRIPT. Run scripts/run_stage7_delivery.py." >&2
  exit 4
fi

if ! command -v pandoc >/dev/null 2>&1; then
  echo "Pandoc is required to build the final PDF." >&2
  echo "Install pandoc and a compatible LaTeX engine, then rerun." >&2
  exit 5
fi

pandoc "$MANUSCRIPT" \
  --from markdown \
  --pdf-engine=xelatex \
  --metadata title="Prediction Markets as Manufactured Public Signals" \
  -o "$OUTPUT"

echo "Generated $OUTPUT"
