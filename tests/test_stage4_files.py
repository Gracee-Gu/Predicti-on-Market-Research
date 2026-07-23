from pathlib import Path
import csv
ROOT=Path(__file__).resolve().parents[1]
def test_model_registry_has_unique_ids():
    with (ROOT/"config/stage4_model_registry.csv").open(newline="") as f: rows=list(csv.DictReader(f))
    ids=[r["model_id"] for r in rows]; assert len(ids)==len(set(ids)) and "M1" in ids
