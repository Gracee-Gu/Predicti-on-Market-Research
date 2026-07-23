from __future__ import annotations

import json
import shutil
import subprocess

from _stage7_common import ROOT, OUT, read_json, write_json


def main() -> None:
    audit = read_json(OUT / "alignment_audit.json")
    status = audit.get("status", "design_revision_required")
    if status == "finalization_ready":
        manuscript = ROOT / "paper/final/manuscript_stage7.md"
        pdf = ROOT / "paper/final/manuscript_stage7.pdf"
    else:
        manuscript = ROOT / "paper/final/manuscript_stage7_progress.md"
        pdf = ROOT / "paper/final/manuscript_stage7_progress.pdf"

    if not manuscript.exists():
        payload = {
            "stage": 7,
            "status": "missing_input",
            "alignment_status": status,
            "reason": f"Missing manuscript source: {manuscript.relative_to(ROOT)}",
            "pdf_path": str(pdf.relative_to(ROOT)) if pdf.exists() else None,
        }
        write_json(OUT / "pdf_render_status.json", payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    if shutil.which("pandoc") is None:
        payload = {
            "stage": 7,
            "status": "unavailable",
            "alignment_status": status,
            "returncode": None,
            "stdout": "",
            "stderr": "Pandoc is not installed.",
            "pdf_path": str(pdf.relative_to(ROOT)) if pdf.exists() else None,
        }
        write_json(OUT / "pdf_render_status.json", payload)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    proc = subprocess.run(
        [
            "pandoc",
            str(manuscript),
            "--from",
            "markdown",
            "--pdf-engine=xelatex",
            "--metadata",
            "title=Prediction Markets as Manufactured Public Signals",
            "-o",
            str(pdf),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    payload = {
        "stage": 7,
        "status": "completed" if proc.returncode == 0 else "unavailable",
        "alignment_status": status,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "pdf_path": str(pdf.relative_to(ROOT)) if pdf.exists() else None,
    }
    write_json(OUT / "pdf_render_status.json", payload)
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
