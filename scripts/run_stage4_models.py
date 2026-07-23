from __future__ import annotations
import json
from pathlib import Path
import _stage4_bootstrap  # noqa
from pmresearch.stage4.core import find_input, read_csv, write_json
ROOT = Path(__file__).resolve().parents[1]
PREDICTORS = ["probability_as_public_opinion", "representativeness_caveat", "market_quality_caveat", "certainty_language", "democratic_language", "horse_race_frame"]

def main() -> None:
    source = find_input(ROOT, ["data/analysis/article_market_dataset.csv", "data/stage3/article_market_dataset.csv"])
    rows = read_csv(source); result = {"input": str(source.relative_to(ROOT)), "n": len(rows), "models": {}}
    try:
        import pandas as pd
        import statsmodels.api as sm
        df = pd.DataFrame(rows)
        cols = ["overreach_severity"] + PREDICTORS
        for c in cols: df[c] = pd.to_numeric(df[c], errors="coerce")
        use = df[cols].dropna()
        X = sm.add_constant(use[PREDICTORS], has_constant="add")
        fit = sm.OLS(use["overreach_severity"], X).fit(cov_type="HC1")
        result["models"]["M1"] = {"status": "completed", "n": int(fit.nobs), "coefficients": fit.params.to_dict(), "standard_errors": fit.bse.to_dict(), "pvalues": fit.pvalues.to_dict(), "r_squared": float(fit.rsquared)}
        try:
            from statsmodels.miscmodels.ordinal_model import OrderedModel
            od = OrderedModel(use["overreach_severity"].astype(int), use[PREDICTORS], distr="logit").fit(method="bfgs", disp=False)
            result["models"]["M2"] = {"status": "completed", "n": int(od.nobs), "coefficients": od.params.to_dict(), "standard_errors": od.bse.to_dict(), "pvalues": od.pvalues.to_dict()}
        except Exception as e:
            result["models"]["M2"] = {"status": "unavailable", "reason": f"{type(e).__name__}: {e}"}
    except Exception as e:
        result["models"]["M1"] = {"status": "unavailable", "reason": f"{type(e).__name__}: {e}", "install": "pip install pandas statsmodels"}
        result["models"]["M2"] = {"status": "unavailable", "reason": "M1 dependencies unavailable"}
    write_json(ROOT / "outputs/stage4/model_results.json", result)
    print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
