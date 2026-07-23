from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "stage7"
FINAL = ROOT / "paper" / "final"

SOURCE_ALIASES = {
    "platform": "platform_owned",
    "platform-owned": "platform_owned",
    "platform_owned": "platform_owned",
    "independent": "independent_media",
    "independent-media": "independent_media",
    "independent_media": "independent_media",
    "partner": "partner_media",
    "partner-media": "partner_media",
    "partner_media": "partner_media",
    "regulatory": "regulatory_critical",
    "critical": "regulatory_critical",
    "regulatory/critical": "regulatory_critical",
    "regulatory_critical": "regulatory_critical",
}

def first_existing(paths: Iterable[Path]) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None

def read_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}

def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def read_csv(path: Path | None) -> list[dict[str, str]]:
    if path is None:
        return []
    try:
        with path.open(encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception:
        return []

def read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    rows = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                value = json.loads(line)
                if isinstance(value, dict):
                    rows.append(value)
    except Exception:
        return []
    return rows

def normalize_source(value: str | None) -> str:
    raw = (value or "").strip().lower().replace(" ", "_")
    return SOURCE_ALIASES.get(raw, raw)

def pick_column(rows: list[dict[str, str]], candidates: list[str]) -> str | None:
    if not rows:
        return None
    names = {k.lower(): k for k in rows[0].keys()}
    for c in candidates:
        if c.lower() in names:
            return names[c.lower()]
    return None

def nonempty(value: Any) -> bool:
    return value is not None and str(value).strip().lower() not in {"", "na", "nan", "none", "null"}

def proportion(rows: list[dict[str, str]], columns: list[str]) -> float:
    if not rows:
        return 0.0
    present = 0
    for row in rows:
        if any(nonempty(row.get(c)) for c in columns if c in row):
            present += 1
    return present / len(rows)

def count_metric_columns(rows: list[dict[str, str]], patterns: list[str]) -> list[str]:
    if not rows:
        return []
    cols = list(rows[0].keys())
    found = []
    for col in cols:
        low = col.lower()
        if any(p in low for p in patterns):
            found.append(col)
    return found

def manuscript_sections(text: str) -> list[str]:
    return re.findall(r"(?m)^##\s+(.+?)\s*$", text)

def row_nonempty_count(row: dict[str, Any]) -> int:
    return sum(1 for value in row.values() if nonempty(value))

def media_record_key(row: dict[str, Any]) -> tuple[Any, ...]:
    url = (row.get("url") or row.get("article_url") or "").strip()
    if url:
        return ("url", url)
    source_id = (row.get("source_id") or row.get("article_id") or "").strip()
    if source_id:
        return ("source_id", source_id)
    text_hash = (row.get("text_sha256") or "").strip()
    if text_hash:
        return ("text_sha256", text_hash)
    title = (row.get("title") or row.get("page_title") or row.get("article_title") or "").strip().lower()
    published = (row.get("published_at") or row.get("publication_time") or "").strip()
    return ("fallback", title, published)

def dedupe_media_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = media_record_key(row)
        existing = selected.get(key)
        if existing is None or row_nonempty_count(row) > row_nonempty_count(existing):
            selected[key] = row
    return list(selected.values())
