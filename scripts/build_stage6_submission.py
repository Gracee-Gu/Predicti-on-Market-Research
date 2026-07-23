from __future__ import annotations

import json
import re
from pathlib import Path

from _stage6_common import ROOT, OUT, FINAL_PAPER, resolve_claim_status, section_missing, sha256_file, write_json

REQUIRED = [
    "Abstract", "Introduction", "Theory and Hypotheses", "Data and Methods",
    "Results", "Discussion", "Limitations", "Conclusion", "Reproducibility Statement"
]
ANON_PATTERNS = ["Gracee Gu", "Yingzi Gu", "顾英子", "Cornell Tech"]

def anonymize(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    result = text
    for value in ANON_PATTERNS:
        count = len(re.findall(re.escape(value), result, flags=re.I))
        counts[value] = count
        result = re.sub(re.escape(value), "[ANONYMIZED]", result, flags=re.I)
    result = re.sub(
        r"https?://github\.com/Gracee-Gu/[^\s)]+",
        "[ANONYMIZED REPOSITORY]",
        result,
        flags=re.I,
    )
    return result, counts

def main() -> None:
    source = ROOT / "paper/manuscript_stage5.md"
    if not source.exists():
        raise SystemExit("Missing paper/manuscript_stage5.md. Run Stage 5 first.")

    OUT.mkdir(parents=True, exist_ok=True)
    FINAL_PAPER.mkdir(parents=True, exist_ok=True)
    claim_status, claim_source = resolve_claim_status()
    text = source.read_text(encoding="utf-8").strip() + "\n"

    banner = (
        f"> **Evidence classification:** `{claim_status}`. "
        "This classification is inherited from the Stage 4/5 claim audit and is not upgraded by Stage 6.\n\n"
    )
    if "Evidence classification:" not in text:
        first_break = text.find("\n")
        text = text[: first_break + 1] + "\n" + banner + text[first_break + 1 :]

    clean_path = FINAL_PAPER / "manuscript_clean.md"
    clean_path.write_text(text, encoding="utf-8")
    blinded, replacements = anonymize(text)
    blinded_path = FINAL_PAPER / "manuscript_blinded.md"
    blinded_path.write_text(blinded, encoding="utf-8")

    availability = f"""# Data and Code Availability Statement

The code, configuration files, construct definitions, collection protocols, annotation schema, analysis scripts, tests, and audit records for this study are maintained in the project repository.

The empirical claim classification for this release is `{claim_status}`.

Raw copyrighted article text is excluded from the public reproducibility package by default. The repository retains source metadata, hashes, excerpts where permitted, and documented retrieval and matching procedures. Credentials, private keys, access tokens, and local environment files are excluded.

The current corpus and analysis limitations—including source concentration, market-quality coverage, and coding provenance—must be evaluated using the Stage 3–5 audit outputs before interpreting the results.

A machine-readable Stage 6 capsule manifest records the relative path, size, and SHA-256 digest of each included file.
"""
    availability_path = FINAL_PAPER / "data_and_code_availability.md"
    availability_path.write_text(availability, encoding="utf-8")

    metadata = {
        "stage": 6,
        "title": "Prediction Markets as Manufactured Public Signals: Media Framing, Market Quality, and Representational Overreach",
        "claim_status": claim_status,
        "claim_status_source": claim_source,
        "source_manuscript": str(source.relative_to(ROOT)),
        "clean_manuscript": str(clean_path.relative_to(ROOT)),
        "blinded_manuscript": str(blinded_path.relative_to(ROOT)),
        "data_availability_statement": str(availability_path.relative_to(ROOT)),
        "required_sections_missing": section_missing(text, REQUIRED),
        "anonymization_replacements": replacements,
        "sha256": {
            "clean_manuscript": sha256_file(clean_path),
            "blinded_manuscript": sha256_file(blinded_path),
        },
        "human_prechecks_required": [
            "Review automated anonymization, including self-citations and file metadata.",
            "Replace template or placeholder language.",
            "Verify every numerical result against Stage 4 outputs.",
            "Confirm bibliography completeness and citation formatting.",
            "Confirm venue-specific length, formatting, and disclosure requirements.",
        ],
    }
    write_json(OUT / "submission_metadata.json", metadata)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
