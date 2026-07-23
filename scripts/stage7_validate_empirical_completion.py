from __future__ import annotations

import json

from _stage7_common import OUT, read_json, write_json
from audit_stage7_alignment import main as alignment_main


def main() -> None:
    alignment_main()
    audit = read_json(OUT / "alignment_audit.json")
    status = audit.get("status", "design_revision_required")
    payload = {
        "stage": 7,
        "validation_status": status,
        "ready_for_final_empirical_paper": status == "finalization_ready",
        "requires_empirical_recovery": status == "empirical_recovery_required",
        "requires_design_revision": status == "design_revision_required",
        "failed_checks": audit.get("failed_checks", []),
        "interpretation": audit.get("interpretation"),
    }
    write_json(OUT / "empirical_completion_validation.json", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
