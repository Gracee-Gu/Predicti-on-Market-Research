# Analysis Plan (Original)

> **Status.** This was the original plan for a regression linking framing constructs to
> `overreach_severity`. It was not run: `overreach_severity` turned out to be a deterministic
> function of the other constructs (see the paper's §3.3 and Appendix C), which would make any
> such regression circular. The published paper reports construct prevalence and its association
> with independently-verified market-quality evidence instead. This document is kept as a record
> of the original design, not as a description of the final methodology.

## Objective

Estimate associations between media framing constructs and representational overreach while preserving the distinction between exploratory evidence and confirmatory inference.

## Unit of analysis

One adjudicated media article–market pair (`pair_id`). Repeated articles or markets must be diagnosed and reported. Standard errors should be clustered by article or market once either cluster contains repeated observations and the required statistical package is available.

## Primary outcome

`overreach_severity` on the Stage 3 ordinal scale 0–3.

## Primary predictors

`probability_as_public_opinion`, `representativeness_caveat`, `market_quality_caveat`, `certainty_language`, `democratic_language`, and `horse_race_frame`.

## Claim gates

Confirmatory language is prohibited unless all configured gates pass: sufficient sample size, at least two source types, no source type above the concentration threshold, adequate market-quality coverage, and human adjudication provenance.

## Estimands

1. Mean difference in overreach by framing indicator.
2. Partial association from a linear model with heteroskedasticity-robust uncertainty.
3. Ordinal-logit direction and magnitude as a robustness check.
4. Source-type contrasts only when more than one source type is observed.

## Missingness

No complete-case deletion may silently remove records. Market-quality absence is represented by an explicit missingness indicator. Models using market-quality measures must report the effective sample size.

## Multiplicity

The six primary framing coefficients form one family. Report raw p-values and Benjamini–Hochberg adjusted q-values. Emphasize effect sizes and uncertainty rather than binary significance.

## Robustness

Run: leave-one-topic-out, leave-one-market-out where feasible, binary high-overreach outcome (`>=2`), ordinal model, and analyses excluding AI-only adjudication. Any unavailable check must be recorded as unavailable rather than omitted.
