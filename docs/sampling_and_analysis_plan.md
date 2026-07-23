# Sampling and Analysis Plan (Original)

> **Status.** This was the original sampling and coding plan, including "blind double coding" by
> two human coders. It was not run that way: both "coders" ended up being the same automated
> keyword classifier (see the paper's §3.3 and `docs/codebook.md`). Kept as a record of the
> original design.

The sampling frame is the union of valid Stage 2 article–market matches. Exclude unmatched, ambiguous, current-only-not-aligned, duplicate URL–market pairs, and rows lacking publication time. Retain unavailable historical quality as missing rather than imputing current order-book conditions.

Stratify by source type, platform, topic, and month. Include all eligible platform-owned and partner-media pairs when small; sample independent media within strata. Reserve at least 30 pairs for the pilot and randomly select at least 20% for blind double coding.

Primary outcome: `overreach_severity`. Secondary outcomes: public-opinion substitution, democratic language, certainty, and caveat presence. Market-quality predictors should be computed from publication-aligned evidence only: recent trade count/volume, price movement, and available spread/depth snapshots. Models are descriptive/associational, not causal.

Primary tests:
1. Source type differences in overreach.
2. Association between lower publication-aligned market quality and stronger representational claims.
3. Whether caveats attenuate the relationship between market probability foregrounding and overreach.
4. Robustness excluding platform-owned media and ambiguous matches.
