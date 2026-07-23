# Stage 7 Empirical Recovery Plan

## Status

`empirical_recovery_required`

The current repository contains substantial engineering, documentation, annotation, analysis, and reproducibility work. However, it does not yet answer the original research question at the intended empirical level.

## Current source distribution

```json
{
  "platform_owned": 49,
  "partner_media": 31,
  "independent_media": 47,
  "regulatory_critical": 37
}
```

## Failed research gates

- `market_quality_coverage`

## Why finalization is blocked

The central claim requires evidence about both institutional translation of market prices and the market-quality conditions omitted from those translations. A narrow source corpus or missing publication-aligned quality data cannot support that claim merely because later-stage modeling and manuscript scripts run successfully.

## Priority 3 — Recover publication-aligned market quality

For every matched article–market pair, attempt to recover:

- volume in a documented publication-centered window;
- trade count or trade frequency;
- bid–ask spread when historical quotes are available;
- order-book depth only when timestamped snapshots exist;
- volatility and price stability from transaction or candle history;
- time to resolution;
- platform, contract, outcome, timestamp, and unit normalization.

Do not treat cumulative volume as full liquidity. Retain raw metrics even if a composite representation is explored. Record structurally unavailable fields explicitly.

## Priority 4 — Rerun the two core analyses

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

## Priority 5 — Decide the event study formally

Attempt an event-window analysis only after checking timestamp precision and time-series coverage. If those checks fail, create a short formal abandonment memo stating why the analysis was excluded.


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
