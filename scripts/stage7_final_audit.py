from __future__ import annotations

import json

from _stage7_common import OUT, read_json, write_json
from audit_stage7_delivery import main as delivery_audit_main


def main() -> None:
    delivery_audit_main()
    report = read_json(OUT / "final_delivery_audit.json")
    write_json(OUT / "stage7_final_audit.json", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
