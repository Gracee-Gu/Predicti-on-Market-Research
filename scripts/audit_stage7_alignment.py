from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from _stage7_common import (
    ROOT, OUT, first_existing, read_csv, read_json, read_jsonl, normalize_source,
    pick_column, proportion, count_metric_columns, nonempty, write_json,
    dedupe_media_records
)

GATES = {
    "minimum_total_documents": 80,
    "minimum_source_types": 3,
    "minimum_documents_per_required_source_type": 15,
    "minimum_human_audited_units": 50,
    "minimum_reliability_fields_reported": 3,
    "minimum_market_quality_coverage": 0.50,
    "minimum_publication_timestamp_coverage": 0.80,
    "minimum_match_traceability": 0.90,
    "minimum_case_evidence_rows": 10,
}

def load_corpus_records() -> tuple[list[dict[str, str]], Path | None]:
    csv_candidates = [
        ROOT / "data/processed/media_corpus.csv",
        ROOT / "data/processed/articles.csv",
    ]
    for path in csv_candidates:
        rows = read_csv(path)
        if rows:
            return rows, path

    media_dir = ROOT / "data/raw/media"
    if media_dir.exists():
        rows: list[dict[str, str]] = []
        for path in sorted(media_dir.glob("*.jsonl")):
            for row in read_jsonl(path):
                rows.append({k: "" if v is None else str(v) for k, v in row.items()})
        deduped = dedupe_media_records(rows)
        if deduped:
            return deduped, media_dir

    inventory = ROOT / "data/inventory/corpus_inventory.csv"
    rows = read_csv(inventory)
    if rows:
        record_type = pick_column(rows, ["record_type"])
        if record_type:
            media_rows = [
                row for row in rows
                if (row.get(record_type) or "").strip().lower() in {"media", "article", "document"}
            ]
            if media_rows:
                return media_rows, inventory
        return rows, inventory

    return [], None

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    corpus, corpus_path = load_corpus_records()
    dataset_path = first_existing([
        ROOT / "data/analysis/article_market_dataset.csv",
        ROOT / "data/stage3/article_market_dataset.csv",
        ROOT / "data/processed/article_market_matches.csv",
    ])
    annotations_path = first_existing([
        ROOT / "data/annotations/adjudicated_annotations.csv",
        ROOT / "data/annotations/coding_sheet_completed.csv",
    ])
    coding_provenance_path = first_existing([
        ROOT / "data/annotations/coding_sheet_completed.csv",
        ROOT / "data/annotations/adjudicated_annotations.csv",
    ])
    reliability_path = first_existing([
        ROOT / "data/analysis/reliability.json",
        ROOT / "outputs/stage3/reliability_report.json",
        ROOT / "outputs/stage3/reliability.json",
    ])

    dataset = read_csv(dataset_path)
    annotations = read_csv(annotations_path)
    coding_provenance = read_csv(coding_provenance_path)
    reliability = read_json(reliability_path)

    source_col = pick_column(corpus or dataset, [
        "source_type", "media_source_type", "source_category", "corpus_type"
    ])
    source_rows = [
        row for row in (corpus or dataset)
        if source_col and nonempty(row.get(source_col))
    ] or (corpus or dataset)
    source_counts = Counter()
    if source_col:
        for row in source_rows:
            source_counts[normalize_source(row.get(source_col))] += 1
        source_counts.pop("", None)

    timestamp_cols = count_metric_columns(dataset, [
        "publication_time", "published_at", "publication_timestamp", "article_date"
    ])
    id_cols = count_metric_columns(dataset, [
        "market_id", "ticker", "condition_id", "token_id", "matched_market"
    ])
    quality_cols = count_metric_columns(dataset, [
        "volume", "trade_frequency", "trade_count", "spread", "depth",
        "volatility", "stability", "time_to_resolution"
    ])
    non_volume_quality = [c for c in quality_cols if "volume" not in c.lower()]

    timestamp_coverage = proportion(dataset, timestamp_cols)
    traceability = proportion(dataset, id_cols)
    market_quality_coverage = proportion(dataset, quality_cols)
    non_volume_quality_coverage = proportion(dataset, non_volume_quality)

    coder_col = pick_column(coding_provenance, ["coder_id", "coder", "annotator", "adjudicator"])
    double_code_col = pick_column(coding_provenance, ["double_code", "double_coded", "is_double_coded"])
    human_audited = 0
    if coding_provenance and coder_col:
        for row in coding_provenance:
            coder_value = (row.get(coder_col) or "").strip().lower()
            if not coder_value:
                continue
            if any(term in coder_value for term in ("ai", "llm", "gpt", "auto")):
                continue
            if double_code_col is None or nonempty(row.get(double_code_col)):
                human_audited += 1

    reliability_fields = 0
    def walk(obj):
        nonlocal reliability_fields
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(term in k.lower() for term in ("kappa", "alpha", "reliability")) and isinstance(v, (int, float)):
                    reliability_fields += 1
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    walk(reliability)

    required_sources = {
        "platform_owned": source_counts.get("platform_owned", 0),
        "independent_media": source_counts.get("independent_media", 0),
    }

    checks = {
        "total_documents": {
            "value": len(corpus or dataset),
            "threshold": GATES["minimum_total_documents"],
            "pass": len(corpus or dataset) >= GATES["minimum_total_documents"],
        },
        "source_type_diversity": {
            "value": len([k for k,v in source_counts.items() if v > 0]),
            "threshold": GATES["minimum_source_types"],
            "pass": len([k for k,v in source_counts.items() if v > 0]) >= GATES["minimum_source_types"],
        },
        "required_source_counts": {
            "value": required_sources,
            "threshold_each": GATES["minimum_documents_per_required_source_type"],
            "pass": all(v >= GATES["minimum_documents_per_required_source_type"] for v in required_sources.values()),
        },
        "human_audited_units": {
            "value": human_audited,
            "threshold": GATES["minimum_human_audited_units"],
            "pass": human_audited >= GATES["minimum_human_audited_units"],
        },
        "reliability_fields_reported": {
            "value": reliability_fields,
            "threshold": GATES["minimum_reliability_fields_reported"],
            "pass": reliability_fields >= GATES["minimum_reliability_fields_reported"],
        },
        "publication_timestamp_coverage": {
            "value": timestamp_coverage,
            "threshold": GATES["minimum_publication_timestamp_coverage"],
            "pass": timestamp_coverage >= GATES["minimum_publication_timestamp_coverage"],
        },
        "market_match_traceability": {
            "value": traceability,
            "threshold": GATES["minimum_match_traceability"],
            "pass": traceability >= GATES["minimum_match_traceability"],
        },
        "market_quality_coverage": {
            "value": market_quality_coverage,
            "non_volume_value": non_volume_quality_coverage,
            "threshold": GATES["minimum_market_quality_coverage"],
            "pass": (
                market_quality_coverage >= GATES["minimum_market_quality_coverage"]
                and non_volume_quality_coverage >= GATES["minimum_market_quality_coverage"] / 2
            ),
        },
        "case_level_rows": {
            "value": sum(1 for r in dataset if any(nonempty(r.get(c)) for c in id_cols)),
            "threshold": GATES["minimum_case_evidence_rows"],
            "pass": sum(1 for r in dataset if any(nonempty(r.get(c)) for c in id_cols)) >= GATES["minimum_case_evidence_rows"],
        },
    }

    critical_missing = not dataset_path or not source_col
    passed = all(item["pass"] for item in checks.values())
    if critical_missing:
        status = "design_revision_required"
    elif passed:
        status = "finalization_ready"
    else:
        status = "empirical_recovery_required"

    report = {
        "stage": 7,
        "status": status,
        "inputs": {
            "corpus": str(corpus_path.relative_to(ROOT)) if corpus_path else None,
            "article_market_dataset": str(dataset_path.relative_to(ROOT)) if dataset_path else None,
            "annotations": str(annotations_path.relative_to(ROOT)) if annotations_path else None,
            "reliability": str(reliability_path.relative_to(ROOT)) if reliability_path else None,
        },
        "source_counts": dict(source_counts),
        "detected_market_quality_columns": quality_cols,
        "detected_non_volume_quality_columns": non_volume_quality,
        "checks": checks,
        "failed_checks": [k for k,v in checks.items() if not v["pass"]],
        "interpretation": (
            "Both original empirical components meet the configured minimum gates."
            if status == "finalization_ready"
            else "The repository is technically developed but does not yet support the original two-part empirical claim."
            if status == "empirical_recovery_required"
            else "Core data schema or provenance is missing; revise the design implementation before empirical recovery."
        ),
    }
    write_json(OUT / "alignment_audit.json", report)

    with (OUT / "evidence_gap_matrix.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["gate", "observed", "threshold", "status", "research_consequence"])
        writer.writeheader()
        consequences = {
            "total_documents": "Insufficient corpus breadth and precision.",
            "source_type_diversity": "Cannot compare institutional framing types.",
            "required_source_counts": "Cannot estimate platform-versus-independent differences.",
            "human_audited_units": "Annotation validity is not independently established.",
            "reliability_fields_reported": "Measurement reliability is undocumented.",
            "publication_timestamp_coverage": "Publication-aligned market matching is unreliable.",
            "market_match_traceability": "Case-level claims cannot be traced to markets.",
            "market_quality_coverage": "Core market-quality and overreach analysis cannot be executed.",
            "case_level_rows": "High-overreach examples cannot be audited.",
        }
        for gate, item in checks.items():
            writer.writerow({
                "gate": gate,
                "observed": json.dumps(item.get("value"), ensure_ascii=False),
                "threshold": item.get("threshold", item.get("threshold_each")),
                "status": "PASS" if item["pass"] else "FAIL",
                "research_consequence": consequences[gate],
            })

    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
