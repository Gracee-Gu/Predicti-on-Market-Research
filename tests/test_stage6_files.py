from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_stage6_required_implementation_files_exist():
    required = [
        "README_STAGE6.md",
        "config/stage6.yaml",
        "docs/runbook_stage6.md",
        "docs/stage6_submission_protocol.md",
        "docs/stage6_acceptance.md",
        "scripts/audit_stage6_inputs.py",
        "scripts/build_stage6_submission.py",
        "scripts/build_stage6_capsule.py",
        "scripts/build_stage6_defense_brief.py",
        "scripts/audit_stage6_final.py",
    ]
    assert all((ROOT / path).exists() for path in required)
