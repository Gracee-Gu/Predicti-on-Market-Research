from __future__ import annotations

import json
from pathlib import Path

from _stage6_common import ROOT, OUT, first_existing, read_json, resolve_claim_status, write_json

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manuscript = first_existing([ROOT / "paper/manuscript_stage5.md"])
    stage5_audit = first_existing([
        ROOT / "outputs/stage5/stage5_release_audit.json",
        ROOT / "outputs/stage5/stage5_input_audit.json",
    ])
    ledger = first_existing([ROOT / "outputs/stage5/claim_evidence_ledger.csv"])
    manifest = first_existing([ROOT / "outputs/stage5/reproducibility_manifest.json"])
    claim_status, claim_source = resolve_claim_status()

    stage5_payload = read_json(stage5_audit) if stage5_audit else {}
    report = {
        "stage": 6,
        "manuscript": str(manuscript.relative_to(ROOT)) if manuscript else None,
        "stage5_audit": str(stage5_audit.relative_to(ROOT)) if stage5_audit else None,
        "claim_ledger": str(ledger.relative_to(ROOT)) if ledger else None,
        "stage5_manifest": str(manifest.relative_to(ROOT)) if manifest else None,
        "claim_status": claim_status,
        "claim_status_source": claim_source,
        "stage5_publication_status": stage5_payload.get("publication_status"),
        "required_input_failures": [] if manuscript else ["paper/manuscript_stage5.md"],
        "warnings": [
            warning for warning, condition in [
                ("Stage 5 claim ledger was not found.", ledger is None),
                ("Stage 5 reproducibility manifest was not found.", manifest is None),
                ("Claim status is blocked or could not be resolved.", claim_status == "blocked"),
            ] if condition
        ],
    }
    report["implementation_status"] = "PASS" if manuscript else "INCOMPLETE"
    write_json(OUT / "stage6_input_audit.json", report)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
