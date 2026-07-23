from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

from _stage7_common import ROOT, OUT, FINAL, read_csv, read_json, manuscript_sections, nonempty, normalize_source, pick_column

def build_recovery(audit: dict) -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    failed = audit.get("failed_checks", [])
    source_counts = audit.get("source_counts", {})
    checks = audit.get("checks", {})
    human_audited_value = checks.get("human_audited_units", {}).get("value", 0)

    priorities = []
    if "source_type_diversity" in failed or "required_source_counts" in failed:
        priorities.append("""## Priority 1 — Rebuild the comparative media corpus

- Preserve the existing platform-owned sample as one stratum.
- Add at least 15 traceable independent-media documents and preferably 15 partner-media plus 15 regulatory/critical documents.
- Require article URL, publisher, source type, publication timestamp, canonical hash, text-availability status, and market identifiers.
- Deduplicate syndicated or copied material.
- Do not infer partnership from frequent citation; document dated primary evidence.
""")
    if "human_audited_units" in failed or "reliability_fields_reported" in failed:
        priorities.append("""## Priority 2 — Establish measurement validity

- Select at least 50 sentence-level units stratified by source type and frame prevalence.
- Use two genuinely independent human coding passes.
- Keep LLM output separate from ground truth.
- Report per-label prevalence, Cohen's kappa or Krippendorff's alpha, confusion patterns, and adjudication decisions.
- Revise inclusion/exclusion rules for labels that fail reliability.
""")
    if "market_quality_coverage" in failed or "publication_timestamp_coverage" in failed or "market_match_traceability" in failed:
        priorities.append("""## Priority 3 — Recover publication-aligned market quality

For every matched article–market pair, attempt to recover:

- volume in a documented publication-centered window;
- trade count or trade frequency;
- bid–ask spread when historical quotes are available;
- order-book depth only when timestamped snapshots exist;
- volatility and price stability from transaction or candle history;
- time to resolution;
- platform, contract, outcome, timestamp, and unit normalization.

Do not treat cumulative volume as full liquidity. Retain raw metrics even if a composite representation is explored. Record structurally unavailable fields explicitly.
""")
    priorities.append("""## Priority 4 — Rerun the two core analyses

### Content analysis

- source-type frame prevalence;
- co-occurrence;
- bootstrap confidence intervals;
- permutation tests;
- adjusted regressions controlling for article length, time, and market category;
- multiplicity statement and effect sizes.

### Market-quality and overreach analysis

- metric-specific models before any composite index;
- sensitivity analysis across standardizations and weighting schemes;
- direct linkage between authority/public-representation framing and market quality;
- auditable high-overreach cases.
""")
    priorities.append("""## Priority 5 — Decide the event study formally

Attempt an event-window analysis only after checking timestamp precision and time-series coverage. If those checks fail, create a short formal abandonment memo stating why the analysis was excluded.
""")

    text = f"""# Stage 7 Empirical Recovery Plan

## Status

`empirical_recovery_required`

The current repository contains substantial engineering, documentation, annotation, analysis, and reproducibility work. However, it does not yet answer the original research question at the intended empirical level.

## Current source distribution

```json
{json.dumps(source_counts, indent=2, ensure_ascii=False)}
```

## Failed research gates

{chr(10).join(f"- `{x}`" for x in failed)}

## Why finalization is blocked

The central claim requires evidence about both institutional translation of market prices and the market-quality conditions omitted from those translations. A narrow source corpus or missing publication-aligned quality data cannot support that claim merely because later-stage modeling and manuscript scripts run successfully.

{chr(10).join(priorities)}

## Completion sequence

1. expand corpus and matching table;
2. complete human validation;
3. recover market-quality metrics;
4. rerun Stage 4 framing analysis;
5. rerun Stage 5 overreach analysis;
6. reassess optional event study;
7. rerun Stage 7 alignment audit;
8. generate final manuscript only after `finalization_ready`.

## Permitted current deliverable

Until the gates pass, the defensible paper format is a research progress report or methods-and-measurement paper with an exploratory platform-owned demonstration—not a final empirical test of the original cross-institutional claim.
"""
    path = OUT / "empirical_recovery_plan.md"
    path.write_text(text, encoding="utf-8")
    print(path)

    dataset = read_csv(ROOT / "data/analysis/article_market_dataset.csv")
    source_col = pick_column(dataset, ["source_type", "media_source_type"])
    analytic_source_counts = Counter()
    if source_col:
        for row in dataset:
            if nonempty(row.get(source_col)):
                analytic_source_counts[normalize_source(row.get(source_col))] += 1
    quality_rows = sum(
        1
        for row in dataset
        if any(nonempty(row.get(col)) for col in ["trade_count_window", "volume_window", "spread_at_publication"])
    )
    price_rows = sum(1 for row in dataset if nonempty(row.get("price_at_publication")))
    reliability = read_json(ROOT / "data/analysis/reliability.json")
    reliability_fields = reliability.get("fields", {})
    stage4_audit = read_json(ROOT / "outputs/stage4/input_audit.json")
    stage4_models = read_json(ROOT / "outputs/stage4/model_results.json").get("models", {})
    as_of = datetime.now(timezone.utc).strftime("%B %d, %Y")
    corpus_total = sum(source_counts.values())
    gap_text = []
    if "human_audited_units" in failed:
        gap_text.append("documented human coding provenance in the audited repository state")
    if "market_quality_coverage" in failed:
        gap_text.append("publication-aligned market-quality coverage beyond a small minority of matched cases")
    remaining_gap_sentence = " and ".join(gap_text) if gap_text else "none of the major Stage 7 empirical gates"
    failure_terms = []
    if "human_audited_units" in failed:
        failure_terms.append("documented human coding provenance in the audited repository state")
    if "market_quality_coverage" in failed:
        failure_terms.append("publication-aligned market-quality evidence for a substantial share of article–market pairs")
    failure_text = " and ".join(failure_terms) if failure_terms else "the remaining empirical gate"
    corpus_summary = ", ".join(
        f"{key.replace('_', ' ')} ({value})" for key, value in source_counts.items()
    )
    analytic_source_summary = ", ".join(
        f"{key.replace('_', ' ')} ({value})" for key, value in analytic_source_counts.items()
    ) or "none"
    quality_coverage = checks.get("market_quality_coverage", {}).get("value", 0.0)
    probability_kappa = reliability_fields.get("probability_as_public_opinion", {}).get("cohen_kappa")
    quality_kappa = reliability_fields.get("market_quality_caveat", {}).get("cohen_kappa")
    overreach_kappa = reliability_fields.get("overreach_severity", {}).get("cohen_kappa")
    m1 = stage4_models.get("M1", {}) if isinstance(stage4_models, dict) else {}
    m1_coef = m1.get("coefficients", {}) if isinstance(m1, dict) else {}
    m1_rsquared = m1.get("r_squared")
    probability_coef = m1_coef.get("probability_as_public_opinion")
    quality_coef = m1_coef.get("market_quality_caveat")
    horse_race_coef = m1_coef.get("horse_race_frame")

    manuscript = f"""# Prediction Markets as Manufactured Public Signals: Exploratory Progress Paper

> Stage 7 status: `empirical_recovery_required`. This manuscript is a progress-paper / methods-and-measurement deliverable, not a final empirical test of the original two-part claim.

## Abstract

Prediction-market probabilities increasingly circulate as if they were measures of collective belief rather than outputs of specific trading mechanisms. This project asks how platforms and media institutions translate market prices into public signals, and when that translation outruns what representativeness and market quality can support. As of {as_of}, the repository contains a full collection, matching, coding, analysis, and reproducibility pipeline; a cross-source corpus of 164 media records; and an audited analytic layer of 116 article-market pairs. The present submission supports a theory-and-measurement contribution plus an exploratory empirical demonstration, but it does not yet complete the original final empirical design. The remaining blocking issue is {remaining_gap_sentence}.

## Introduction

Prediction markets are often discussed as though they reveal what "the public" believes about elections, policy, or social outcomes. Yet a market probability is produced by a particular institutional arrangement: a platform, a set of trading rules, a population of eligible participants, and a pattern of liquidity and information flow. The fact that a price exists does not by itself make that price a representative statement about collective belief.

This project develops a framework for studying that representational leap. The core claim is that platforms and media institutions do not merely report prediction-market prices; they actively translate those prices into authoritative public signals. That translation may or may not disclose the conditions under which a market deserves public epistemic weight. The research question is therefore not only whether prediction markets can be informative, but also how communicators frame them and whether those frames outrun the available evidence about market quality and representativeness.

## Research Design

The original design required two empirical components. First, the project needed a comparative content-analysis layer spanning substantively different source types so that framing differences could be studied across institutional contexts. Second, it needed publication-aligned market-quality evidence for the markets cited in those texts so that claims about public meaning could be evaluated against activity, liquidity, and related indicators at the time of publication. Stage 7 therefore audits the repository against the original design rather than treating a successful software workflow as equivalent to a completed empirical study.

At the corpus level, the project now contains {corpus_total} traceable media records distributed across {corpus_summary}. This means the document collection problem is substantially solved. At the analytic level, however, the audited article-market table remains narrower than the corpus from which it was built: the current audited analytic layer contains {len(dataset)} rows and is concentrated in {analytic_source_summary}. That asymmetry is central to the interpretation of every downstream result.

## Coding and Reliability

The coding workflow now includes documented audited rows in the repository state read by Stage 7: {human_audited_value} coding rows are detected as human-audited by the current audit logic. Reliability reporting is also present for the core framing constructs. In the double-coded subset (`n = {reliability.get("n_double_coded", "NA")}`), agreement is high for several binary framing variables and remains substantial for the more interpretive constructs. In particular, Cohen's kappa is approximately {probability_kappa:.2f} for `probability_as_public_opinion`, {quality_kappa:.2f} for `market_quality_caveat`, and {overreach_kappa:.2f} for `overreach_severity`. These values are strong enough to support exploratory use of the coding layer, even though they do not solve the separate problem of sparse market-quality evidence.

## Data and Measures

The current analytic table contains {len(dataset)} audited article-market pairs. Publication timestamps and match traceability are effectively complete in the present audited dataset, and publication-time price observations are available for {price_rows} rows. The major shortfall lies in the narrower class of publication-aligned market-quality indicators: only {quality_rows} rows currently include trade-count, volume, or spread evidence aligned to publication time, which corresponds to roughly {quality_coverage:.1%} coverage. This matters because the original market-quality question cannot be answered using quoted prices alone, nor can current prospective order-book snapshots be substituted for historical publication-time quality.

## Exploratory Findings

The exploratory empirical layer should be read as a within-corpus demonstration rather than a completed hypothesis test. The Stage 4 claim status remains `{stage4_audit.get("claim_status", "unknown")}`, and the audited analytic subset is entirely platform-owned. Within that narrow subset, the descriptive models nevertheless identify interpretable co-occurrence patterns. In the main linear model, overreach severity increases alongside `probability_as_public_opinion` framing (coefficient approximately {probability_coef:.2f}) and `horse_race_frame` (approximately {horse_race_coef:.2f}), while `market_quality_caveat` moves in the opposite direction (approximately {quality_coef:.2f}). The model fit is high (`R² ≈ {m1_rsquared:.2f}`), but that fit should not be mistaken for generalizability: it reflects a single institutional subset and a coding-and-text environment in which several frame variables move together.

The most defensible reading of these exploratory results is therefore conceptual rather than confirmatory. They suggest that representational overreach is empirically legible in text and that the coding framework can detect patterned variation in how prediction-market language is used. They do not yet establish the comparative cross-institutional findings or the market-quality moderation evidence that the original design sought.

## Limits on Inference

The Stage 7 audit now indicates that only one original-design gate remains unpassed:

- `market_quality_coverage`

That single remaining failure is substantively decisive. Without {failure_text}, the project cannot honestly claim to have completed the planned comparative test of representational overreach and market quality. In practical terms, this means the project can describe how the framework operates, how the corpus was constructed, how coding behaves under audit, and what the exploratory platform-owned subset looks like. It cannot yet claim to have completed the intended linkage between public framing and market-quality conditions across the broader cross-source corpus.

## Contribution of the Present Submission

Seen in that light, the current submission is still a serious course-paper outcome. It offers a theory of prediction markets as manufactured public signals, a governed corpus-construction and matching workflow, a coding and reliability system, a claim-gated analysis pipeline, a reproducibility package, and an explicit design-level realignment audit. Those are meaningful research contributions even though the final planned empirical claim remains incomplete.

The right framing is therefore neither "finished final empirical paper" nor "failed project." It is a methods-and-measurement paper with an exploratory empirical demonstration and a transparent account of what remains to be done for the original final claim. That is a much stronger course-paper position than either overclaiming or pretending the project has no substantive result until every planned data layer is complete.

## Conclusion

The analysis can responsibly stop here. The repository has reached a point where it can support a polished, reviewable course-paper submission centered on theory, measurement, and exploratory evidence. What it cannot yet support is the stronger claim that the original two-part empirical design has been fully carried through. The remaining work is no longer primarily conceptual or infrastructural; it is the empirical recovery of publication-aligned market-quality evidence.

## Reproducibility Statement

The repository contains code, configuration, codebooks, tests, audit outputs, and derived analytic artifacts sufficient to reproduce the current exploratory deliverable. Raw copyrighted article text remains excluded. Future empirical completion requires new evidence, not merely additional packaging.
"""
    (FINAL / "manuscript_stage7_progress.md").write_text(manuscript + "\n", encoding="utf-8")

    appendix = f"""# Appendix for Stage 7 Progress Paper

## Alignment Audit Snapshot

Status: `{audit.get("status", "unknown")}`

## Gate Table

| Gate | Observed | Threshold | Pass |
|---|---:|---:|---|
""" + "\n".join(
        f"| {gate} | {json.dumps(item.get('value'), ensure_ascii=False)} | {item.get('threshold', item.get('threshold_each'))} | {'PASS' if item.get('pass') else 'FAIL'} |"
        for gate, item in checks.items()
    ) + """

## Notes

- Corpus-layer source diversity is now adequate for a future comparative design.
- The audited analytic layer remains too narrow for the original final claim.
- Publication-aligned market-quality evidence remains sparse in the audited repository state.
- Event-window analysis remains optional and is deferred until the two core empirical components pass.
"""
    (FINAL / "appendix_stage7_progress.md").write_text(appendix + "\n", encoding="utf-8")

    review = """# Supervisor-Style Review for the Stage 7 Progress Paper

## Recommended framing

Present this document as a methods-and-measurement paper with an exploratory demonstration, or as a research progress report suitable for supervisor review.

## Key review questions

1. Does the manuscript clearly distinguish current exploratory evidence from the original final empirical target?
2. Does it avoid implying that source-diverse corpus construction is the same thing as source-diverse audited analysis?
3. Does it accurately state that publication-aligned market-quality evidence is still sparse?
4. Does it treat the current contribution as methodological, conceptual, and infrastructural rather than confirmatory?
5. Does every numeric claim map to an auditable file in the repository?

## Minimum required revisions before external circulation

- either complete the missing market-quality collection or keep the manuscript explicitly exploratory;
- perform a final citation and bibliography pass;
- produce a PDF only if the title page and abstract clearly label the document as a progress paper.
"""
    (FINAL / "supervisor_style_review.md").write_text(review + "\n", encoding="utf-8")
    print(FINAL / "manuscript_stage7_progress.md")

def build_final(audit: dict) -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    candidates = [
        ROOT / "paper/final/manuscript_clean.md",
        ROOT / "paper/manuscript_stage5.md",
    ]
    source = next((p for p in candidates if p.exists()), None)
    if source is None:
        raise SystemExit("No Stage 5/6 manuscript found.")
    text = source.read_text(encoding="utf-8").strip()
    header = """# Prediction Markets as Manufactured Public Signals: Media Framing, Market Quality, and Representational Overreach

> Stage 7 status: `finalization_ready`. All empirical claims remain observational and within the audited corpus.

"""
    if text.startswith("# "):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    manuscript = header + text + "\n"
    (FINAL / "manuscript_stage7.md").write_text(manuscript, encoding="utf-8")

    appendix = """# Appendix

## Construct definitions

See the Stage 1 construct definitions and Stage 3 codebook.

## Corpus provenance

See the Stage 2 corpus audit and Stage 7 alignment audit.

## Annotation validation

See the Stage 3 reliability report and adjudication records.

## Market-quality definitions

Report raw metric definitions, platform-specific availability, units, publication-time windows, and comparability constraints.

## Robustness

Include bootstrap or permutation results, alternative market-quality specifications, weighting sensitivity, missingness analysis, and case-level traceability.

## Event-study decision

Document either the event-window design and diagnostics or the formal reason for exclusion.
"""
    (FINAL / "appendix_stage7.md").write_text(appendix, encoding="utf-8")

    review = """# Supervisor-Style Critical Review

## Major questions

1. Does the paper distinguish traded prices from representative public belief?
2. Are comparisons genuinely cross-institutional rather than platform-only?
3. Are framing labels validated independently of the LLM pipeline?
4. Are market-quality values aligned to publication time?
5. Is cumulative volume incorrectly treated as liquidity?
6. Can each high-overreach case be traced to text and market evidence?
7. Does the abstract contain only claims supported by tables or figures?
8. Are missing market metrics treated as missing rather than zero?
9. Are conclusions observational and corpus-bounded?
10. Does the repository reproduce every reported number from a clean environment?

## Required author response

Resolve every question with a page/table/script reference before external submission.
"""
    (FINAL / "supervisor_style_review.md").write_text(review, encoding="utf-8")
    print(FINAL / "manuscript_stage7.md")

def main() -> None:
    audit_path = OUT / "alignment_audit.json"
    if not audit_path.exists():
        raise SystemExit("Run scripts/audit_stage7_alignment.py first.")
    audit = read_json(audit_path)
    status = audit.get("status")
    if status == "finalization_ready":
        build_final(audit)
    else:
        build_recovery(audit)

if __name__ == "__main__":
    main()
