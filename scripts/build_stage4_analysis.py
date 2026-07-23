from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path
import _stage4_bootstrap  # noqa
from pmresearch.stage4.core import as_float, find_input, mean, mean_difference, read_csv, write_json
ROOT = Path(__file__).resolve().parents[1]
PREDICTORS = ["probability_as_public_opinion", "representativeness_caveat", "market_quality_caveat", "certainty_language", "democratic_language", "horse_race_frame"]

def main() -> None:
    source = find_input(ROOT, ["data/analysis/article_market_dataset.csv", "data/stage3/article_market_dataset.csv"])
    rows = read_csv(source)
    out = ROOT / "outputs/stage4"; (out / "tables").mkdir(parents=True, exist_ok=True)
    profile = {"n": len(rows), "source_type": dict(Counter(r.get("source_type", "missing") for r in rows)),
               "platform": dict(Counter(r.get("platform", "missing") for r in rows)),
               "outcome_mean": mean(x for r in rows if (x := as_float(r.get("overreach_severity"))) is not None)}
    write_json(out / "corpus_profile.json", profile)
    effects = [mean_difference(rows, p, "overreach_severity") for p in PREDICTORS]
    with (out / "tables/bivariate_effects.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(effects[0])); w.writeheader(); w.writerows(effects)
    write_json(out / "analysis_build.json", {"input": str(source.relative_to(ROOT)), "rows": len(rows), "effects": len(effects)})
    print(json.dumps(profile, indent=2))
if __name__ == "__main__": main()
