from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

REQUIRED = {
    "pair_id", "article_id", "market_id", "source_type", "platform",
    "overreach_severity", "probability_as_public_opinion",
    "representativeness_caveat", "market_quality_caveat",
    "certainty_language", "democratic_language", "horse_race_frame",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def find_input(root: Path, candidates: Sequence[str]) -> Path:
    for rel in candidates:
        p = root / rel
        if p.exists():
            return p
    raise FileNotFoundError("No Stage 3 analytic dataset found: " + ", ".join(candidates))


def as_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    try:
        x = float(text)
    except ValueError:
        return None
    return x if math.isfinite(x) else None


def mean(xs: Iterable[float]) -> float | None:
    vals = list(xs)
    return sum(vals) / len(vals) if vals else None


def sample_variance(xs: Sequence[float]) -> float | None:
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def mean_difference(rows: list[dict[str, str]], predictor: str, outcome: str) -> dict:
    groups: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        x, y = as_float(row.get(predictor)), as_float(row.get(outcome))
        if x is not None and y is not None:
            groups[int(x > 0)].append(y)
    a, b = groups[1], groups[0]
    ma, mb = mean(a), mean(b)
    diff = None if ma is None or mb is None else ma - mb
    se = None
    va, vb = sample_variance(a), sample_variance(b)
    if va is not None and vb is not None and a and b:
        se = math.sqrt(va / len(a) + vb / len(b))
    return {"predictor": predictor, "n_positive": len(a), "n_zero": len(b),
            "mean_positive": ma, "mean_zero": mb, "difference": diff,
            "standard_error": se,
            "ci95_low": None if diff is None or se is None else diff - 1.96 * se,
            "ci95_high": None if diff is None or se is None else diff + 1.96 * se}


def bh_adjust(pvalues: Sequence[float | None]) -> list[float | None]:
    valid = [(i, p) for i, p in enumerate(pvalues) if p is not None and 0 <= p <= 1]
    out: list[float | None] = [None] * len(pvalues)
    m = len(valid)
    if not m:
        return out
    ranked = sorted(valid, key=lambda z: z[1])
    running = 1.0
    for rank_from_end, (idx, p) in enumerate(reversed(ranked), start=1):
        rank = m - rank_from_end + 1
        running = min(running, p * m / rank)
        out[idx] = min(1.0, running)
    return out


def audit_rows(rows: list[dict[str, str]], gates: dict) -> dict:
    columns = set(rows[0]) if rows else set()
    missing_columns = sorted(REQUIRED - columns)
    source_counts = Counter(r.get("source_type", "") or "missing" for r in rows)
    n = len(rows)
    largest_share = max(source_counts.values(), default=0) / n if n else 1.0
    quality_fields = ["spread", "depth", "volume", "liquidity", "market_quality_available"]
    observed_quality = 0
    for r in rows:
        if any(str(r.get(k, "")).strip() not in {"", "0", "False", "false", "NA", "nan"} for k in quality_fields):
            observed_quality += 1
    quality_coverage = observed_quality / n if n else 0.0
    provenance_fields = ["adjudication_provenance", "human_adjudicated", "adjudicator_id"]
    human_evidence = any(str(r.get(k, "")).strip().lower() in {"1", "true", "human", "yes"} for r in rows for k in provenance_fields)
    checks = {
        "schema_complete": not missing_columns,
        "minimum_n": n >= int(gates.get("minimum_n", 80)),
        "source_type_count": len([k for k in source_counts if k != "missing"]) >= int(gates.get("minimum_source_types", 2)),
        "source_concentration": largest_share <= float(gates.get("maximum_single_source_share", .85)),
        "quality_coverage": quality_coverage >= float(gates.get("minimum_quality_coverage", .5)),
        "human_adjudication": human_evidence if gates.get("require_human_adjudication_for_confirmatory", True) else True,
    }
    status = "blocked" if not checks["schema_complete"] or not checks["minimum_n"] else ("confirmatory_ready" if all(checks.values()) else "exploratory_only")
    return {"n": n, "missing_columns": missing_columns, "source_type_counts": dict(source_counts),
            "largest_source_share": largest_share, "quality_coverage": quality_coverage,
            "human_adjudication_evidence": human_evidence, "checks": checks, "claim_status": status}


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
