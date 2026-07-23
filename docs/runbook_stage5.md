# Stage 5 Runbook

Run from the repository root:

```bash
python scripts/audit_stage5_inputs.py
python scripts/build_stage5_claim_ledger.py
python scripts/assemble_stage5_manuscript.py
python scripts/build_stage5_reproducibility_manifest.py
python scripts/audit_stage5_release.py
python -m pytest
```

Outputs are written to `outputs/stage5/`. The manuscript draft is written to `paper/manuscript_stage5.md`. Stage 5 reads but does not overwrite Stage 1–4 source files.

Before interpreting the manuscript, inspect:

```text
outputs/stage5/stage5_input_audit.json
outputs/stage5/claim_evidence_ledger.csv
outputs/stage5/stage5_release_audit.json
```

A successful build means the manuscript is structurally reproducible. It does not mean the empirical claim gates passed.
