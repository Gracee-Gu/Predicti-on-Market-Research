# Stage 4 Runbook

From the repository root:

```bash
python scripts/audit_stage4_inputs.py
python scripts/build_stage4_analysis.py
python scripts/run_stage4_models.py
python scripts/render_stage4_report.py
python scripts/audit_stage4.py
python -m pytest
```

Outputs are written under `outputs/stage4/` and never overwrite Stage 3 data.

The first command creates `outputs/stage4/input_audit.json`. Read its `claim_status` before interpreting any model. The model runner uses standard-library calculations for descriptive and bivariate estimates. If `pandas`, `statsmodels`, and `matplotlib` are installed, it additionally emits multivariable models and figures; otherwise it records those components as unavailable.
