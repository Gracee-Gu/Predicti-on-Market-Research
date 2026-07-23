from __future__ import annotations

import json

from _stage7_common import OUT, read_json, write_json
from run_stage7_delivery import main as delivery_main


def main() -> None:
    delivery_main()
    audit = read_json(OUT / "alignment_audit.json")
    status = audit.get("status", "design_revision_required")
    if status == "finalization_ready":
        generated = "paper/final/manuscript_stage7.md"
    else:
        generated = "paper/final/manuscript_stage7_progress.md"
    payload = {
        "stage": 7,
        "alignment_status": status,
        "generated_primary_output": generated,
    }
    write_json(OUT / "final_paper_build.json", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
