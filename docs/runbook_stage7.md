# Stage 7 Runbook

Run from the repository root.

## 1. Audit alignment with the original design

```bash
python scripts/audit_stage7_alignment.py
```

## 2. Build the research-question evidence map

```bash
python scripts/build_stage7_evidence_map.py
```

## 3. Generate either the empirical recovery plan or final manuscript

```bash
python scripts/run_stage7_delivery.py
```

The script reads `outputs/stage7/alignment_audit.json`.

- If the status is `empirical_recovery_required`, it generates a detailed recovery plan and does not represent the manuscript as final.
- If the status is `finalization_ready`, it assembles the final manuscript and appendix from audited evidence.
- If core schema or provenance is missing, it returns `design_revision_required`.

## 4. Build PDF when finalization is permitted

```bash
bash scripts/build_stage7_pdf.sh
```

The script uses Pandoc if available. It refuses to create a misleading final PDF when the alignment status is not `finalization_ready`.

## 5. Final audit

```bash
python scripts/audit_stage7_delivery.py
python -m pytest
```

## Recommended current workflow

If the audit returns `empirical_recovery_required`, follow the generated:

```text
outputs/stage7/empirical_recovery_plan.md
```

Then rerun Stages 2–5 using the expanded corpus and publication-aligned market evidence before rerunning Stage 7.
