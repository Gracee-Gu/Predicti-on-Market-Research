import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import build_stage3_analytic_dataset
import build_stage3_sampling_frame
import build_stage3_adjudication_sheet
import finalize_stage3_adjudication
import merge_stage3_coder_files
import prepare_stage3_coder_packets


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_build_stage3_sampling_frame_reads_stage2_mentions_and_snapshots(
    tmp_path: Path, monkeypatch
):
    mention_path = tmp_path / "market_mentions_sample_v3.jsonl"
    snapshot_path = tmp_path / "market_snapshots_sample_v3.jsonl"
    media_path = tmp_path / "media_sample.jsonl"
    output_path = tmp_path / "coding_sheet.csv"

    mention_path.write_text(
        json.dumps(
            {
                "mention_id": "source_1:kalshi:KXTEST-26",
                "source_id": "source_1",
                "source_url": "https://example.com/story",
                "market_id": "KXTEST-26",
                "publication_time": "2026-07-23T12:00:00Z",
                "source_type": "independent_media",
                "platform": "kalshi",
                "match_method": "exact_identifier",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    snapshot_path.write_text(
        json.dumps(
            {
                "snapshot_id": "source_1:kalshi:KXTEST-26",
                "market_id": "KXTEST-26",
                "snapshot_status": "historical_price_matched",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    media_path.write_text(
        json.dumps(
            {
                "source_id": "source_1",
                "page_title": "Example Title",
                "excerpt": "Example excerpt for coders.",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_stage3_sampling_frame.py",
            "--input-glob",
            str(mention_path),
            "--snapshots-glob",
            str(snapshot_path),
            "--media-glob",
            str(media_path),
            "--output",
            str(output_path),
            "--seed",
            "1",
            "--double-fraction",
            "1.0",
        ],
    )
    build_stage3_sampling_frame.main()

    rows = read_csv_rows(output_path)
    assert len(rows) == 1
    assert rows[0]["article_id"] == "source_1"
    assert rows[0]["article_url"] == "https://example.com/story"
    assert rows[0]["article_title"] == "Example Title"
    assert rows[0]["context_excerpt"] == "Example excerpt for coders."
    assert rows[0]["market_id"] == "KXTEST-26"
    assert rows[0]["match_status"] == "exact_identifier"
    assert rows[0]["snapshot_status"] == "historical_price_matched"
    assert rows[0]["double_code"] == "1"


def test_build_stage3_analytic_dataset_joins_snapshot_id_to_pair_id(
    tmp_path: Path, monkeypatch
):
    annotations_path = tmp_path / "annotations.csv"
    snapshot_path = tmp_path / "market_snapshots_sample_v3.jsonl"
    output_path = tmp_path / "analytic.csv"
    pid = build_stage3_sampling_frame.make_pair_id("source_1", "KXTEST-26")

    annotations_path.write_text(
        "\n".join(
            [
                "pair_id,article_id,market_id,coder_id,market_probability_present,probability_as_public_opinion,representativeness_caveat,market_quality_caveat,certainty_language,democratic_language,horse_race_frame,overreach_severity,notes",
                f"{pid},source_1,KXTEST-26,,1,0,0,1,2,1,0,2,ok",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    snapshot_path.write_text(
        json.dumps(
            {
                "snapshot_id": "source_1:kalshi:KXTEST-26",
                "market_id": "KXTEST-26",
                "snapshot_status": "historical_price_matched",
                "price_at_publication": "0.5200",
                "trade_count_window": "4",
                "volume_window": "1200",
                "spread_at_publication": "0.04",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_stage3_analytic_dataset.py",
            "--annotations",
            str(annotations_path),
            "--snapshots-glob",
            str(snapshot_path),
            "--output",
            str(output_path),
        ],
    )
    build_stage3_analytic_dataset.main()

    rows = read_csv_rows(output_path)
    assert len(rows) == 1
    assert rows[0]["quality_evidence_class"] == "historical_price_matched"
    assert rows[0]["price_at_publication"] == "0.5200"
    assert rows[0]["trade_count_window"] == "4"
    assert rows[0]["volume_window"] == "1200"
    assert rows[0]["spread_at_publication"] == "0.04"


def test_prepare_merge_and_finalize_stage3_annotation_workflow(
    tmp_path: Path, monkeypatch
):
    coding_sheet = tmp_path / "coding_sheet.csv"
    coder_a = tmp_path / "coder_a.csv"
    coder_b = tmp_path / "coder_b.csv"
    merged = tmp_path / "coding_sheet_completed.csv"
    adjudication = tmp_path / "adjudication_sheet.csv"
    adjudication_completed = tmp_path / "adjudication_sheet_completed.csv"
    final_output = tmp_path / "adjudicated_annotations.csv"

    coding_sheet.write_text(
        "\n".join(
            [
                "pair_id,article_id,market_id,article_url,article_title,context_excerpt,evidence_text,quoted_price,quoted_price_unit,source_notes,publication_time,source_type,platform,topic,match_status,snapshot_status,double_code,coder_id,market_probability_present,probability_as_public_opinion,representativeness_caveat,market_quality_caveat,certainty_language,democratic_language,horse_race_frame,overreach_severity,notes",
                "pair1,a1,m1,https://example.com/1,t1,e1,ev1,50,%,sn1,2026-07-01,platform_owned,kalshi,,exact_identifier,historical_price_matched,1,,,,,,,,,,",
                "pair2,a2,m2,https://example.com/2,t2,e2,ev2,,,sn2,2026-07-02,independent_media,kalshi,,exact_identifier,unavailable,0,,,,,,,,,,",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prepare_stage3_coder_packets.py",
            "--input",
            str(coding_sheet),
            "--output-a",
            str(coder_a),
            "--output-b",
            str(coder_b),
            "--seed",
            "1",
        ],
    )
    prepare_stage3_coder_packets.main()

    a_rows = read_csv_rows(coder_a)
    b_rows = read_csv_rows(coder_b)
    assert len(a_rows) == 2
    assert len(b_rows) == 1

    for row in a_rows:
        if row["pair_id"] == "pair1":
            row["market_probability_present"] = "1"
            row["probability_as_public_opinion"] = "2"
            row["representativeness_caveat"] = "0"
            row["market_quality_caveat"] = "0"
            row["certainty_language"] = "2"
            row["democratic_language"] = "1"
            row["horse_race_frame"] = "1"
            row["overreach_severity"] = "3"
        if row["pair_id"] == "pair2":
            row["market_probability_present"] = "0"
            row["probability_as_public_opinion"] = "0"
            row["representativeness_caveat"] = "1"
            row["market_quality_caveat"] = "1"
            row["certainty_language"] = "0"
            row["democratic_language"] = "0"
            row["horse_race_frame"] = "0"
            row["overreach_severity"] = "1"
    for row in b_rows:
        row["market_probability_present"] = "1"
        row["probability_as_public_opinion"] = "1"
        row["representativeness_caveat"] = "0"
        row["market_quality_caveat"] = "1"
        row["certainty_language"] = "1"
        row["democratic_language"] = "0"
        row["horse_race_frame"] = "1"
        row["overreach_severity"] = "2"

    with coder_a.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(a_rows[0].keys()))
        writer.writeheader()
        writer.writerows(a_rows)
    with coder_b.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(b_rows[0].keys()))
        writer.writeheader()
        writer.writerows(b_rows)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "merge_stage3_coder_files.py",
            "--coder-a",
            str(coder_a),
            "--coder-b",
            str(coder_b),
            "--output",
            str(merged),
        ],
    )
    merge_stage3_coder_files.main()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "build_stage3_adjudication_sheet.py",
            "--input",
            str(merged),
            "--output",
            str(adjudication),
        ],
    )
    build_stage3_adjudication_sheet.main()

    adjudication_rows = read_csv_rows(adjudication)
    assert len(adjudication_rows) == 1
    assert adjudication_rows[0]["pair_id"] == "pair1"

    adjudication_rows[0]["market_probability_present_adjudicated"] = "1"
    adjudication_rows[0]["probability_as_public_opinion_adjudicated"] = "2"
    adjudication_rows[0]["representativeness_caveat_adjudicated"] = "0"
    adjudication_rows[0]["market_quality_caveat_adjudicated"] = "1"
    adjudication_rows[0]["certainty_language_adjudicated"] = "1"
    adjudication_rows[0]["democratic_language_adjudicated"] = "1"
    adjudication_rows[0]["horse_race_frame_adjudicated"] = "1"
    adjudication_rows[0]["overreach_severity_adjudicated"] = "2"
    adjudication_rows[0]["adjudication_notes"] = "Resolved disagreement."

    with adjudication_completed.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(adjudication_rows[0].keys()))
        writer.writeheader()
        writer.writerows(adjudication_rows)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "finalize_stage3_adjudication.py",
            "--completed",
            str(merged),
            "--adjudication",
            str(adjudication_completed),
            "--output",
            str(final_output),
        ],
    )
    finalize_stage3_adjudication.main()

    final_rows = read_csv_rows(final_output)
    assert len(final_rows) == 2
    pair1 = next(row for row in final_rows if row["pair_id"] == "pair1")
    pair2 = next(row for row in final_rows if row["pair_id"] == "pair2")
    assert pair1["overreach_severity"] == "2"
    assert pair1["notes"] == "Resolved disagreement."
    assert pair2["overreach_severity"] == "1"
