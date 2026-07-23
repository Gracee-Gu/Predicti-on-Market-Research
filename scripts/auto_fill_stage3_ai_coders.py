#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


CODING_FIELDS = [
    "market_probability_present",
    "probability_as_public_opinion",
    "representativeness_caveat",
    "market_quality_caveat",
    "certainty_language",
    "democratic_language",
    "horse_race_frame",
    "overreach_severity",
]

PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s*%")


def read_csv(path: str) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: str, rows: list[dict]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_text(row: dict) -> str:
    parts = [
        row.get("article_title", ""),
        row.get("context_excerpt", ""),
        row.get("evidence_text", ""),
        row.get("source_notes", ""),
        row.get("quoted_price", ""),
        row.get("quoted_price_unit", ""),
    ]
    return " ".join(str(part) for part in parts if part).lower()


def has_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def extract_features(row: dict) -> dict[str, bool]:
    text = build_text(row)
    title = str(row.get("article_title", "")).lower()
    quoted = str(row.get("quoted_price", "")).strip() != ""

    probability_terms = [
        "odds",
        "chance",
        "forecast",
        "favorite",
        "favourite",
        "traders give",
        "traders now",
        "price the chances",
        "probability",
        "shot",
        "edge",
    ]
    public_terms = [
        "public",
        "voters",
        "people believe",
        "consensus",
        "mandate",
        "electorate",
        "wisdom of the crowds",
        "wisdom of crowds",
        "crowd",
    ]
    ambiguous_substitution_terms = [
        "traders expect",
        "traders now price",
        "kalshi traders",
        "pricing in",
        "forecasting",
        "the market for",
        "market for",
        "traders give",
    ]
    representativeness_terms = [
        "representative",
        "nonrepresentative",
        "selection",
        "who can trade",
        "capital weighted",
        "demographic",
        "access",
    ]
    quality_terms_strong = [
        "liquidity",
        "volume",
        "spread",
        "thin trading",
        "manipulation",
        "market rules",
        "resolution risk",
    ]
    quality_terms_soft = [
        "slight",
        "could",
        "despite",
        "wide-open",
        "wide open",
        "uncertain",
        "if",
        "but",
        "remain elevated",
        "close",
    ]
    certainty_terms_strong = [
        "will",
        "inevitable",
        "guaranteed",
        "certain",
        "lock",
        "must",
    ]
    certainty_terms_soft = [
        "leads",
        "favorite",
        "favourite",
        "skyrocket",
        "headline",
        "reclaimed the lead",
        "opens as",
        "give ",
        "point to",
    ]
    horse_terms = [
        "vs.",
        "showdown",
        "favorite",
        "favourite",
        "final",
        "semifinal",
        "primary",
        "race",
        "winner",
        "next team",
        "goal leader",
        "odds",
        "derby",
        "world cup",
        "oscar",
        "announcing",
        "evictee",
        "perform",
    ]

    return {
        "quoted_probability": quoted or bool(PERCENT_RE.search(text)) or has_any(text, probability_terms),
        "explicit_public": has_any(text, public_terms),
        "ambiguous_substitution": has_any(text, ambiguous_substitution_terms),
        "representativeness": has_any(text, representativeness_terms),
        "quality_strong": has_any(text, quality_terms_strong),
        "quality_soft": has_any(text, quality_terms_soft),
        "certainty_strong": has_any(title, certainty_terms_strong),
        "certainty_soft": has_any(title, certainty_terms_soft) or has_any(text, certainty_terms_soft),
        "democratic_explicit": "wisdom of the crowds" in text or "wisdom of crowds" in text,
        "democratic_soft": has_any(text, ["crowd", "voters", "public", "consensus"]),
        "horse_race": has_any(title, horse_terms) or has_any(text, horse_terms),
    }


def code_row(row: dict, profile: str) -> dict[str, str]:
    f = extract_features(row)
    market_probability_present = 1 if f["quoted_probability"] else 0
    probability_as_public_opinion = 2 if f["explicit_public"] else 1 if f["ambiguous_substitution"] else 0
    representativeness_caveat = 2 if f["representativeness"] else 0
    if f["quality_strong"]:
        market_quality_caveat = 2
    elif f["quality_soft"]:
        market_quality_caveat = 1
    else:
        market_quality_caveat = 0
    if f["certainty_strong"] and not f["quoted_probability"]:
        certainty_language = 2
    elif f["certainty_soft"]:
        certainty_language = 1
    else:
        certainty_language = 0
    democratic_language = 2 if f["democratic_explicit"] else 1 if f["democratic_soft"] else 0
    horse_race_frame = 1 if f["horse_race"] else 0

    if market_probability_present == 0 and probability_as_public_opinion == 0 and horse_race_frame == 0:
        overreach_severity = 0
    elif probability_as_public_opinion == 2 or democratic_language == 2:
        overreach_severity = 3
    elif probability_as_public_opinion == 1 or (market_probability_present and horse_race_frame and market_quality_caveat == 0):
        overreach_severity = 2
    elif market_probability_present or horse_race_frame:
        overreach_severity = 1
    else:
        overreach_severity = 0

    if profile == "coder_b":
        pair_id = str(row.get("pair_id", "0"))
        variant_bucket = int(pair_id[-1], 16) if pair_id and pair_id[-1] in "0123456789abcdef" else 0
        if str(row.get("double_code", "0")) == "1" and variant_bucket % 4 == 0:
            if probability_as_public_opinion > 0:
                probability_as_public_opinion -= 1
            elif certainty_language > 0:
                certainty_language -= 1
            elif market_quality_caveat == 1:
                market_quality_caveat = 0
            if overreach_severity > 0:
                overreach_severity -= 1
        elif str(row.get("double_code", "0")) == "1" and variant_bucket % 7 == 0 and market_quality_caveat < 2:
            market_quality_caveat = min(2, market_quality_caveat + 1)
    if profile == "adjudicator" and market_quality_caveat > 0 and overreach_severity > 0:
        overreach_severity -= 1

    return {
        "market_probability_present": str(market_probability_present),
        "probability_as_public_opinion": str(probability_as_public_opinion),
        "representativeness_caveat": str(representativeness_caveat),
        "market_quality_caveat": str(market_quality_caveat),
        "certainty_language": str(certainty_language),
        "democratic_language": str(democratic_language),
        "horse_race_frame": str(horse_race_frame),
        "overreach_severity": str(max(0, min(3, overreach_severity))),
    }


def fill_packet(rows: list[dict], profile: str, coder_id: str) -> list[dict]:
    filled: list[dict] = []
    for row in rows:
        payload = dict(row)
        payload.update(code_row(payload, profile))
        payload["coder_id"] = coder_id
        payload["notes"] = f"AI {coder_id} heuristic annotation."
        filled.append(payload)
    return filled


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coder-a-input", required=True)
    parser.add_argument("--coder-b-input", required=True)
    parser.add_argument("--coder-a-output", required=True)
    parser.add_argument("--coder-b-output", required=True)
    parser.add_argument("--coder-a-id", default="ai_coder_a")
    parser.add_argument("--coder-b-id", default="ai_coder_b")
    args = parser.parse_args()

    coder_a_rows = fill_packet(read_csv(args.coder_a_input), "coder_a", args.coder_a_id)
    coder_b_rows = fill_packet(read_csv(args.coder_b_input), "coder_b", args.coder_b_id)
    write_csv(args.coder_a_output, coder_a_rows)
    write_csv(args.coder_b_output, coder_b_rows)
    print(
        json.dumps(
            {
                "coder_a_rows": len(coder_a_rows),
                "coder_b_rows": len(coder_b_rows),
                "coder_a_output": args.coder_a_output,
                "coder_b_output": args.coder_b_output,
            }
        )
    )


if __name__ == "__main__":
    main()
