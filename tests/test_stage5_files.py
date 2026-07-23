from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_stage5_required_files():
    for p in ['config/stage5.yaml','docs/runbook_stage5.md','scripts/audit_stage5_inputs.py','scripts/assemble_stage5_manuscript.py','scripts/audit_stage5_release.py']:
        assert (ROOT/p).exists(), p
