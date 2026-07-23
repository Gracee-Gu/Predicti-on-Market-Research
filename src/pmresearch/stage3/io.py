import csv, json
from pathlib import Path

def read_jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def write_csv(path, rows, fieldnames):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(rows)

def read_csv(path):
    with Path(path).open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))
