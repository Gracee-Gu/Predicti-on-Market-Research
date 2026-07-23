from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_stage7_files_exist():
    required = [
        "README_STAGE7.md",
        "config/stage7.yaml",
        "docs/stage7_reconciliation.md",
        "docs/runbook_stage7.md",
        "docs/stage7_acceptance.md",
        "scripts/stage7_repo_audit.py",
        "scripts/stage7_build_recovery_queue.py",
        "scripts/stage7_validate_empirical_completion.py",
        "scripts/stage7_decide_event_study.py",
        "scripts/stage7_build_final_paper.py",
        "scripts/stage7_render_pdf.py",
        "scripts/stage7_final_audit.py",
        "scripts/audit_stage7_alignment.py",
        "scripts/build_stage7_evidence_map.py",
        "scripts/run_stage7_delivery.py",
        "scripts/build_stage7_pdf.sh",
        "scripts/audit_stage7_delivery.py",
    ]
    assert all((ROOT / p).exists() for p in required)
