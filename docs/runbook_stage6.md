# Stage 6 Runbook

Run all commands from the repository root.

```bash
python scripts/audit_stage6_inputs.py
python scripts/build_stage6_submission.py
python scripts/build_stage6_capsule.py
python scripts/build_stage6_defense_brief.py
python scripts/audit_stage6_final.py
python -m pytest
```

Generated outputs:

```text
outputs/stage6/stage6_input_audit.json
outputs/stage6/submission_metadata.json
outputs/stage6/reproducibility_capsule_manifest.json
outputs/stage6/final_audit.json

paper/final/manuscript_clean.md
paper/final/manuscript_blinded.md
paper/final/data_and_code_availability.md
paper/final/defense_brief.md
paper/final/supervisor_handoff.md

release/stage6_reproducibility_capsule.zip
```

## Interpretation rule

A successful Stage 6 build means the research package is structurally ready for review. It does not change the empirical status inherited from Stage 4 and Stage 5.

For the current repository, `exploratory_only` should remain visible in the manuscript, defense brief, supervisor memo, and release audit unless the underlying corpus and evidence gates are genuinely changed and rerun.

## Installation

After extracting `stage6_overlay/` in the repository root:

```bash
bash stage6_overlay/install_stage6.sh .
```

The installer copies files into their repository-relative destinations. Existing different files are reported as conflicts and are not overwritten unless `--force` is explicitly supplied.
