# Prediction Markets as Manufactured Public Signals: Exploratory Progress Paper

> Stage 7 status: `empirical_recovery_required`. This manuscript is a progress-paper / methods-and-measurement deliverable, not a final empirical test of the original two-part claim.

## Abstract

Prediction-market probabilities increasingly circulate as if they were measures of collective belief rather than outputs of specific trading mechanisms. This project asks how platforms and media institutions translate market prices into public signals, and when that translation outruns what representativeness and market quality can support. As of July 23, 2026, the repository contains a full collection, matching, coding, analysis, and reproducibility pipeline; a cross-source corpus of 164 media records; and an audited analytic layer of 116 article-market pairs. The present submission supports a theory-and-measurement contribution plus an exploratory empirical demonstration, but it does not yet complete the original final empirical design. The remaining blocking issue is publication-aligned market-quality coverage beyond a small minority of matched cases.

## Introduction

Prediction markets are often discussed as though they reveal what "the public" believes about elections, policy, or social outcomes. Yet a market probability is produced by a particular institutional arrangement: a platform, a set of trading rules, a population of eligible participants, and a pattern of liquidity and information flow. The fact that a price exists does not by itself make that price a representative statement about collective belief.

This project develops a framework for studying that representational leap. The core claim is that platforms and media institutions do not merely report prediction-market prices; they actively translate those prices into authoritative public signals. That translation may or may not disclose the conditions under which a market deserves public epistemic weight. The research question is therefore not only whether prediction markets can be informative, but also how communicators frame them and whether those frames outrun the available evidence about market quality and representativeness.

## Research Design

The original design required two empirical components. First, the project needed a comparative content-analysis layer spanning substantively different source types so that framing differences could be studied across institutional contexts. Second, it needed publication-aligned market-quality evidence for the markets cited in those texts so that claims about public meaning could be evaluated against activity, liquidity, and related indicators at the time of publication. Stage 7 therefore audits the repository against the original design rather than treating a successful software workflow as equivalent to a completed empirical study.

At the corpus level, the project now contains 164 traceable media records distributed across platform owned (49), partner media (31), independent media (47), regulatory critical (37). This means the document collection problem is substantially solved. At the analytic level, however, the audited article-market table remains narrower than the corpus from which it was built: the current audited analytic layer contains 116 rows and is concentrated in platform owned (116). That asymmetry is central to the interpretation of every downstream result.

## Coding and Reliability

The coding workflow now includes documented audited rows in the repository state read by Stage 7: 139 coding rows are detected as human-audited by the current audit logic. Reliability reporting is also present for the core framing constructs. In the double-coded subset (`n = 23`), agreement is high for several binary framing variables and remains substantial for the more interpretive constructs. In particular, Cohen's kappa is approximately 0.82 for `probability_as_public_opinion`, 0.75 for `market_quality_caveat`, and 0.73 for `overreach_severity`. These values are strong enough to support exploratory use of the coding layer, even though they do not solve the separate problem of sparse market-quality evidence.

## Data and Measures

The current analytic table contains 116 audited article-market pairs. Publication timestamps and match traceability are effectively complete in the present audited dataset, and publication-time price observations are available for 52 rows. The major shortfall lies in the narrower class of publication-aligned market-quality indicators: only 3 rows currently include trade-count, volume, or spread evidence aligned to publication time, which corresponds to roughly 2.6% coverage. This matters because the original market-quality question cannot be answered using quoted prices alone, nor can current prospective order-book snapshots be substituted for historical publication-time quality.

## Exploratory Findings

The exploratory empirical layer should be read as a within-corpus demonstration rather than a completed hypothesis test. The Stage 4 claim status remains `exploratory_only`, and the audited analytic subset is entirely platform-owned. Within that narrow subset, the descriptive models nevertheless identify interpretable co-occurrence patterns. In the main linear model, overreach severity increases alongside `probability_as_public_opinion` framing (coefficient approximately 0.72) and `horse_race_frame` (approximately 1.56), while `market_quality_caveat` moves in the opposite direction (approximately -0.62). The model fit is high (`R² ≈ 0.83`), but that fit should not be mistaken for generalizability: it reflects a single institutional subset and a coding-and-text environment in which several frame variables move together.

The most defensible reading of these exploratory results is therefore conceptual rather than confirmatory. They suggest that representational overreach is empirically legible in text and that the coding framework can detect patterned variation in how prediction-market language is used. They do not yet establish the comparative cross-institutional findings or the market-quality moderation evidence that the original design sought.

## Limits on Inference

The Stage 7 audit now indicates that only one original-design gate remains unpassed:

- `market_quality_coverage`

That single remaining failure is substantively decisive. Without publication-aligned market-quality evidence for a substantial share of article–market pairs, the project cannot honestly claim to have completed the planned comparative test of representational overreach and market quality. In practical terms, this means the project can describe how the framework operates, how the corpus was constructed, how coding behaves under audit, and what the exploratory platform-owned subset looks like. It cannot yet claim to have completed the intended linkage between public framing and market-quality conditions across the broader cross-source corpus.

## Contribution of the Present Submission

Seen in that light, the current submission is still a serious course-paper outcome. It offers a theory of prediction markets as manufactured public signals, a governed corpus-construction and matching workflow, a coding and reliability system, a claim-gated analysis pipeline, a reproducibility package, and an explicit design-level realignment audit. Those are meaningful research contributions even though the final planned empirical claim remains incomplete.

The right framing is therefore neither "finished final empirical paper" nor "failed project." It is a methods-and-measurement paper with an exploratory empirical demonstration and a transparent account of what remains to be done for the original final claim. That is a much stronger course-paper position than either overclaiming or pretending the project has no substantive result until every planned data layer is complete.

## Conclusion

The analysis can responsibly stop here. The repository has reached a point where it can support a polished, reviewable course-paper submission centered on theory, measurement, and exploratory evidence. What it cannot yet support is the stronger claim that the original two-part empirical design has been fully carried through. The remaining work is no longer primarily conceptual or infrastructural; it is the empirical recovery of publication-aligned market-quality evidence.

## Reproducibility Statement

The repository contains code, configuration, codebooks, tests, audit outputs, and derived analytic artifacts sufficient to reproduce the current exploratory deliverable. Raw copyrighted article text remains excluded. Future empirical completion requires new evidence, not merely additional packaging.

