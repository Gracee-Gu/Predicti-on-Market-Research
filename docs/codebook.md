# Codebook

> **Note on how this was actually executed.** This codebook was originally written for the
> two-human double-coding procedure described below. In the version of the corpus used in the
> final paper, all seven constructs are instead scored by a disclosed, deterministic keyword
> classifier (`scripts/auto_fill_stage3_ai_coders.py`), not by trained human coders. The
> annotation files still carry `coder_id` and `double_code` fields from the original design; they
> do not reflect independent human judgments, and no inter-coder reliability statistic should be
> inferred from them. See the paper's §3.3 and Appendix C
> (`paper/final/manuscript.pdf`/`manuscript.html`) for the full disclosure and the classifier's
> exact keyword rules. The construct definitions below still describe what each variable is
> intended to measure; the "Coding procedure" section describes a human protocol that was not
> the one actually run.

## Unit of analysis
One media article–prediction market pair. Code only language attributable to the article, not platform copy embedded in widgets unless the article endorses it.

## Core variables

- `market_probability_present`: 1 when a market price/probability is stated or visually foregrounded.
- `probability_as_public_opinion`: 0 none; 1 suggestive/ambiguous; 2 explicitly treats traders, odds, or price as what voters/the public/people believe or want.
- `representativeness_caveat`: 0 none; 1 generic limitation; 2 specifically notes trader selection, capital weighting, access, demographics, or nonrepresentativeness.
- `market_quality_caveat`: 0 none; 1 generic uncertainty; 2 mentions liquidity, volume, spread, manipulation, thin trading, market rules, or resolution risk.
- `certainty_language`: 0 calibrated; 1 mildly categorical; 2 strongly deterministic or inevitability language.
- `democratic_language`: 0 none; 1 metaphorical public voice; 2 market framed as electorate, mandate, consensus, or democratic signal.
- `horse_race_frame`: 1 when the article emphasizes movement, winners/losers, momentum, or contest standings over substantive policy.
- `overreach_severity`: holistic ordinal judgment: 0 absent, 1 mild, 2 material, 3 severe.

## Decision rule
Representational overreach requires more than merely reporting odds. It occurs when market prices are generalized beyond the population and mechanism that produced them, especially when framed as public sentiment without representativeness or market-quality qualification.

## Coding procedure
Pilot 30 pairs independently. Discuss disagreements only after blind coding. Revise examples, not variable meanings. Double-code at least 20% of the final sample. Adjudicated values must preserve both original coder rows.
