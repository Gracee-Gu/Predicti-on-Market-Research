from __future__ import annotations

import json
import re
from pathlib import Path

from _stage7_common import ROOT, OUT, FINAL, read_json, write_json

FORBIDDEN = [
    "confirms the main hypothesis",
    "demonstrates that media institutions",
    "proves that prediction markets",
    "generalizes to all media",
    "causal effect",
]
SECRET_PATTERNS = [
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
]

def main() -> None:
    audit = read_json(OUT / "alignment_audit.json")
    status = audit.get("status", "design_revision_required")
    recovery = OUT / "empirical_recovery_plan.md"
    manuscript = FINAL / "manuscript_stage7.md"
    appendix = FINAL / "appendix_stage7.md"
    progress_manuscript = FINAL / "manuscript_stage7_progress.md"
    progress_appendix = FINAL / "appendix_stage7_progress.md"
    review = FINAL / "supervisor_style_review.md"
    pdf = FINAL / "manuscript_stage7.pdf"
    progress_pdf = FINAL / "manuscript_stage7_progress.pdf"

    forbidden_hits = []
    target_manuscript = manuscript if status == "finalization_ready" else progress_manuscript
    if target_manuscript.exists():
        low = target_manuscript.read_text(encoding="utf-8").lower()
        forbidden_hits = [x for x in FORBIDDEN if x in low]

    secret_hits = []
    for root_name in ["config", "docs", "scripts", "src", "paper"]:
        root = ROOT / root_name
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file() or p.stat().st_size > 2_000_000:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                secret_hits.append(str(p.relative_to(ROOT)))

    if status == "finalization_ready":
        missing = [
            str(p.relative_to(ROOT)) for p in [manuscript, appendix, review]
            if not p.exists()
        ]
        warnings = [] if pdf.exists() else ["Final PDF has not yet been generated."]
        implementation = "PASS" if not missing and not forbidden_hits and not secret_hits else "INCOMPLETE"
        delivery_status = "ready_for_final_human_review" if implementation == "PASS" else "not_ready"
    else:
        required = [recovery, progress_manuscript, progress_appendix, review]
        missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
        warnings = [
            "The original empirical research question is not yet fully answered.",
            "Do not treat Stage 5/6 packaging as evidence of empirical completion.",
        ]
        implementation = "PASS" if not missing and not secret_hits else "INCOMPLETE"
        delivery_status = "ready_for_progress_paper_review" if implementation == "PASS" else status

    report = {
        "stage": 7,
        "research_status": status,
        "implementation_status": implementation,
        "delivery_status": delivery_status,
        "missing_required_outputs": missing,
        "forbidden_claim_hits": forbidden_hits,
        "secret_hits": secret_hits,
        "warnings": warnings,
        "final_pdf_present": pdf.exists() if status == "finalization_ready" else progress_pdf.exists(),
        "research_question_answered": status == "finalization_ready",
    }
    write_json(OUT / "final_delivery_audit.json", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
