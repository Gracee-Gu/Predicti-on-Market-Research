from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

from _stage6_common import ROOT, OUT, FINAL_PAPER, read_json, resolve_claim_status, section_missing, secret_hits, write_json

REQUIRED_SECTIONS = [
    "Abstract", "Introduction", "Theory and Hypotheses", "Data and Methods",
    "Results", "Discussion", "Limitations", "Conclusion", "Reproducibility Statement"
]
FORBIDDEN = [
    "proves that", "demonstrates that", " causal effect ",
    "representative of the public", "generalizes to all media"
]
REQUIRED_FILES = [
    ROOT / "paper/final/manuscript_clean.md",
    ROOT / "paper/final/manuscript_blinded.md",
    ROOT / "paper/final/data_and_code_availability.md",
    ROOT / "paper/final/defense_brief.md",
    ROOT / "paper/final/supervisor_handoff.md",
    ROOT / "outputs/stage6/submission_metadata.json",
    ROOT / "outputs/stage6/reproducibility_capsule_manifest.json",
    ROOT / "release/stage6_reproducibility_capsule.zip",
]

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    claim_status, claim_source = resolve_claim_status()
    clean = ROOT / "paper/final/manuscript_clean.md"
    text = clean.read_text(encoding="utf-8") if clean.exists() else ""
    missing_files = [str(p.relative_to(ROOT)) for p in REQUIRED_FILES if not p.exists()]
    missing_sections = section_missing(text, REQUIRED_SECTIONS)

    forbidden_hits = []
    if claim_status != "confirmatory_ready":
        low = " " + re.sub(r"\s+", " ", text.lower()) + " "
        forbidden_hits = [term.strip() for term in FORBIDDEN if term in low]

    secret_findings = {}
    for path in REQUIRED_FILES:
        if path.exists() and path.is_file() and path.suffix.lower() != ".zip":
            hits = secret_hits(path)
            if hits:
                secret_findings[str(path.relative_to(ROOT))] = hits

    capsule_error = None
    capsule = ROOT / "release/stage6_reproducibility_capsule.zip"
    if capsule.exists():
        try:
            with zipfile.ZipFile(capsule) as archive:
                bad = archive.testzip()
                if bad:
                    capsule_error = f"Corrupt member: {bad}"
        except Exception as exc:
            capsule_error = str(exc)

    critical = bool(missing_files or missing_sections or forbidden_hits or secret_findings or capsule_error)
    warnings = []
    if claim_status == "exploratory_only":
        warnings.append("Evidence remains exploratory; supervisor review is required before external submission.")
    if claim_status == "blocked":
        warnings.append("Inferential claims remain blocked.")
    if "[ANONYMIZED]" not in (ROOT / "paper/final/manuscript_blinded.md").read_text(encoding="utf-8") if (ROOT / "paper/final/manuscript_blinded.md").exists() else False:
        warnings.append("No configured identity strings were found; manually verify blind-review compliance.")

    if critical:
        final_status = "not_ready"
    elif claim_status == "confirmatory_ready":
        final_status = "ready_for_submission_precheck"
    else:
        final_status = "ready_for_supervisor_review"

    report = {
        "stage": 6,
        "claim_status": claim_status,
        "claim_status_source": claim_source,
        "implementation_status": "PASS" if not critical else "INCOMPLETE",
        "final_status": final_status,
        "missing_files": missing_files,
        "missing_sections": missing_sections,
        "forbidden_claim_hits": forbidden_hits,
        "secret_findings": secret_findings,
        "capsule_integrity_error": capsule_error,
        "warnings": warnings,
        "human_review_required": True,
    }
    write_json(OUT / "final_audit.json", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
