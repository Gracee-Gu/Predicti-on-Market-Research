# Research Design

> **Status.** This is the original research design, written before data collection. One part of it
> was not carried out as planned: §&thinsp;"human-coded audit set" below describes a two-human
> double-coding process that, in the executed project, was instead a disclosed automated keyword
> classifier applied twice (see the paper's §3.3 and `docs/codebook.md`). The theory, constructs,
> and overall design below otherwise reflect what was actually studied.

## Project title

**Prediction Markets as Manufactured Public Signals: Media Framing, Market Quality, and Representational Overreach**

## 1. Purpose and scope

This project studies how prediction-market prices are translated into public-facing information by prediction-market platforms and news organizations. It does not ask only whether prediction markets forecast accurately. Instead, it asks when a market price is represented as an objective probability, collective belief, or measure of public sentiment, and whether the evidentiary quality of the underlying market is disclosed or otherwise commensurate with that representation.

The empirical unit is a **market mention**: a bounded instance in which a platform-owned text, news article, broadcast transcript, partnership announcement, or institutional document refers to a specific prediction-market contract or to prediction-market prices as a class of information.

The project combines:

1. a computational content analysis of platform, partner-media, independent-media, and regulatory/critical texts;
2. human-validated sentence-level framing annotation;
3. contract-level market-quality measurement for the markets cited in those texts; and
4. a linkage analysis testing whether stronger informational authority claims are accompanied by stronger market quality or adequate quality disclosure.

The design is observational and primarily descriptive-associational. It does not identify the causal effect of commercial partnerships on editorial language or the causal effect of framing on audience beliefs.

## 2. Research problem

Prediction-market scholarship has established that markets can aggregate dispersed information and sometimes generate useful forecasts (Wolfers and Zitzewitz 2004). However, a binary-contract price is interpretable as a probability only under substantive assumptions concerning beliefs, preferences, wealth, and market structure (Manski 2006; Wolfers and Zitzewitz 2006). Market prices also need not represent a population's attitudes or preferences. A price reflects the marginal terms at which participating traders exchange risk; it is not a survey statistic.

Meanwhile, contemporary platforms and media organizations increasingly present prediction-market prices as “probabilities,” “public sentiment,” “what people think,” or real-time objective data. The media-framing literature explains how selective emphasis makes some interpretations more salient than others (Entman 1993), but existing prediction-market work has rarely linked public representation to contract-level liquidity, spread, depth, and trading activity.

The resulting empirical gap is not simply whether prediction markets are accurate. It is whether the **strength and breadth of public claims made about a market price are matched by the quality and disclosed limitations of the market that generated it**.

## 3. Theoretical model

The project distinguishes four stages:

1. **Market production** — a contract is designed, traded, and resolved under platform-specific rules.
2. **Signal extraction** — a price, midpoint, or displayed percentage is selected as the salient market signal.
3. **Institutional translation** — platforms and media attach meanings such as probability, consensus, intelligence, or public sentiment.
4. **Public representation** — the translated signal is presented to an audience, often without full information about participation, liquidity, spread, uncertainty, or contract design.

A manufactured public signal is not necessarily false. “Manufactured” means institutionally selected, formatted, labeled, and circulated rather than naturally self-interpreting.

The principal theoretical mechanism is **representational expansion**: movement from a narrow, technically supportable statement to a broader public claim.

Example hierarchy:

- Narrow: “The contract last traded at 0.63.”
- Market interpretation: “Traders price the event at roughly 63%.”
- Epistemic expansion: “The probability is 63%.”
- Representational expansion: “The public believes there is a 63% chance.”

Each step adds assumptions. The study measures these additions rather than presuming they are valid.

## 4. Research questions

**RQ1. Framing distribution.** How do platform-owned, partner-media, independent-media, and regulatory/critical sources differ in their use of epistemic-authority, public-representation, financial-market, gambling, uncertainty-disclosure, and participation frames?

**RQ2. Partnership association.** Are commercially affiliated or formal partner-media texts more likely than independent-media texts to use epistemic-authority and public-representation frames, after accounting for article date, market category, article genre, and text length?

**RQ3. Disclosure.** When a prediction-market price is presented as probability-like or representative of collective belief, how often are liquidity, spread, volume, participant-selection, manipulation, resolution, or other limitations disclosed?

**RQ4. Quality alignment.** Are stronger epistemic-authority and public-representation claims associated with objectively higher contract-level market quality?

**RQ5. Representational overreach.** Which market mentions combine broad authority/representativeness claims with low market quality and weak quality disclosure, and how robust is that classification to alternative measurement choices?

**RQ6. Platform and category heterogeneity.** Does the relationship between framing and market quality vary by platform, market category, time to resolution, and article genre?

## 5. Hypotheses

The confirmatory hypotheses are deliberately limited to comparisons supportable by the observational design.

**H1 (Authority framing).** Partner-media and platform-owned texts will have higher epistemic-authority framing scores than independent-media and regulatory/critical texts.

**H2 (Public representation).** Partner-media and platform-owned texts will be more likely to describe prediction-market prices as public sentiment, collective belief, consensus, or what people think.

**H3 (Risk asymmetry).** Partner-media and platform-owned texts will have lower uncertainty-disclosure and gambling/risk framing scores than regulatory/critical texts.

**H4 (Disclosure gap).** Conditional on making an epistemic-authority or public-representation claim, partner-media and platform-owned texts will be less likely than independent or regulatory/critical texts to disclose at least one market-quality limitation.

**H5 (Weak quality alignment).** The association between authority framing and contract-level market quality will be weak or inconsistent across reasonable market-quality specifications.

**H6 (Overreach concentration).** High representational-overreach cases will be disproportionately concentrated in partner-media and platform-owned source types.

H5 and H6 are preregisterable directional hypotheses but should be treated cautiously until data availability is audited. The analysis will report null and contrary results without revising the construct post hoc.

## 6. Units of analysis and sampling

### 6.1 Text document

A news article, broadcast transcript, platform page, press release, help-center page, partnership announcement, or regulatory/critical institutional document.

### 6.2 Sentence

The primary unit for framing annotation. Sentence-level coding reduces the ambiguity produced by assigning a single label to an entire article.

### 6.3 Market mention

A document-market pair. One document may produce several market mentions. Each mention contains the quoted/displayed price, surrounding text, source metadata, and matched platform contract ID where possible.

### 6.4 Market snapshot

Contract-level market data aligned as closely as possible to the publication or broadcast timestamp. Snapshot fields may include midpoint, last trade, best bid, best ask, spread, depth, recent volume, trade count, volatility, and time to resolution.

### 6.5 Sampling frame

Target period: **January 1, 2025 through the data-collection cutoff**.

Target platforms:
- Kalshi, primary;
- Polymarket, comparative;
- additional platforms only if a cited market can be matched reliably.

Target source strata:
- platform-owned;
- formal or documented media partners;
- independent mainstream media;
- regulatory, academic, ethics, or public-interest criticism.

The corpus should be stratified rather than represented as a census. Inclusion and exclusion rules must be documented before outcome analysis.

## 7. Variable operationalization

### 7.1 Source-type variables

- `source_type`: platform_owned, partner_media, independent_media, regulatory_critical.
- `formal_partnership`: documented commercial/data/content relationship, 0/1.
- `article_genre`: news, analysis, opinion, explainer, press_release, help_page, transcript.
- `platform`: Kalshi, Polymarket, other, multiple.
- `market_category`: politics, economics, sports, entertainment, weather, technology, geopolitics, other.

Partnership coding requires a dated public source. Mere frequent citation does not establish partnership.

### 7.2 Framing constructs

All framing variables are coded at sentence level and aggregated to mention and document level.

**Epistemic authority**
Language that presents the market or price as knowledge-producing, accurate, objective, truth-seeking, data-driven, predictive, or intelligence-bearing.

Indicators: probability, forecast, signal, accurate, objective, data, intelligence, price discovery, truth, wisdom of crowds.

Exclusions: purely mechanical descriptions of payout or price with no knowledge claim.

**Public representation**
Language extending market prices to a broader collectivity.

Indicators: public sentiment, what Americans think, collective belief, consensus, public mood, voters believe, people expect.

Exclusions: “traders believe,” when explicitly limited to traders.

**Financial-market frame**
Language aligning the activity with exchanges, contracts, trading, hedging, liquidity, investment, or price discovery.

**Gambling/risk frame**
Language aligning the activity with bets, wagers, casinos, addiction, losses, speculation, or gambling harms.

**Uncertainty/quality disclosure**
Explicit qualification of the evidentiary strength or operation of the signal.

Indicators: low volume, wide spread, thin market, participant selection, manipulation, insider information, uncertainty interval, small number of traders, resolution ambiguity, price volatility, contract-rule limitations.

**Participation/conversion frame**
Language encouraging clicking, viewing, following, signing up, trading, or taking a position.

### 7.3 Claim breadth

A four-level ordinal variable:

0. **Transaction report** — reports price, odds, or trade without epistemic interpretation.
1. **Trader-belief claim** — attributes belief specifically to traders or the market.
2. **Objective-probability claim** — treats the displayed number as the event probability without qualification.
3. **Public-representation claim** — treats it as public sentiment, consensus, or what a broader population believes.

Primary operationalization: maximum level within the mention window.
Robustness operationalization: mean sentence-level level and binary indicators for levels 2–3.

### 7.4 Market-quality variables

No single measure is treated as “true quality.” The primary analysis reports a vector:

- quoted relative bid–ask spread;
- top-of-book depth or depth within a defined price band;
- trailing trading volume over fixed windows;
- trailing trade count;
- zero-trade share or intertrade duration;
- short-window realized price volatility;
- price staleness;
- time to resolution;
- contract age;
- resolution-rule clarity, separately coded.

Because cumulative volume is mechanically increasing and category-dependent, it will not be used alone as liquidity.

A standardized market-quality index may be added only after reporting components. Candidate construction:
- equal-weight index after direction alignment;
- first principal component;
- rank-based index.

All substantive conclusions must survive at least two constructions or be labeled specification-sensitive.

### 7.5 Disclosure adequacy

`disclosure_any = 1` if the mention includes at least one relevant limitation.
`disclosure_count` counts distinct limitation classes.
`quality_metric_disclosed = 1` if volume, spread, depth, trade count, or comparable market-quality evidence is reported.

Adequacy is not equivalent to a legal disclosure standard; it is an empirical measure of whether the audience receives information relevant to interpreting the signal.

### 7.6 Representational overreach

**Definition:** Representational overreach is a document-market configuration in which the breadth and authority of a public claim exceeds the evidentiary support made visible by the underlying market quality and accompanying disclosure.

It has three separately measured components:

- `claim_breadth`;
- `market_quality`;
- `disclosure_adequacy`.

Primary case classification:

- high claim: objective-probability or public-representation claim;
- low quality: bottom tercile within platform × category × time-to-resolution stratum, or failure on at least two prespecified quality thresholds;
- weak disclosure: no relevant market-quality or representativeness limitation.

A mention is a high-overreach case only when all three conditions hold.

Continuous robustness score:

`Overreach = z(claim breadth) - z(market quality) - z(disclosure adequacy)`

The continuous score is descriptive, not a naturally scaled latent variable. Results will be reported alongside the transparent rule-based classification.

## 8. Analysis plan

### 8.1 Descriptive analysis

- corpus flow and exclusions;
- source-type and category composition;
- framing prevalence with bootstrap confidence intervals;
- co-occurrence of frames;
- claim-breadth distribution;
- disclosure rates conditional on high claims;
- market-quality distributions by platform and category.

### 8.2 Hypothesis tests

For binary sentence/mention outcomes:
- multilevel logistic regression with document random intercepts where sample size permits;
- otherwise cluster-robust logistic regression or permutation tests.

For count/proportion outcomes:
- negative-binomial, beta-binomial, or fractional models selected according to distribution;
- bootstrap contrasts as a model-light robustness check.

Core specification:

`Outcome_i = β0 + β1 PartnerMedia_i + β2 PlatformOwned_i + β3 RegulatoryCritical_i + controls + ε_i`

Controls:
- publication month;
- platform;
- market category;
- article genre;
- standardized text length;
- days to resolution where applicable.

The independent-media group is the principal reference category. Estimates will be presented as average marginal effects or predicted probabilities, not only log-odds.

### 8.3 Quality alignment

- rank correlations between claim breadth/authority score and each quality measure;
- partial correlations or regression with platform/category/time-to-resolution controls;
- binned scatterplots with uncertainty;
- sensitivity to snapshot timing and alternative quality definitions.

### 8.4 Overreach analysis

- prevalence by source type;
- Fisher exact/permutation comparisons for small cells;
- case-level audit table;
- leave-one-category-out sensitivity;
- alternative threshold grid;
- specification curve across quality-index and disclosure definitions.

### 8.5 Annotation validation

A human-coded audit set will be drawn before final model estimation. At least two coding passes are required for a subset. Agreement will be reported using Cohen's kappa for binary labels and weighted kappa or Krippendorff's alpha for ordinal claim breadth. LLM annotations are model-generated measurements, not ground truth.

## 9. Threats to validity and mitigation

**Selection bias.** Publicly discoverable articles may overrepresent prominent markets. Mitigation: define search procedures, source strata, and coverage dates; avoid population-wide prevalence claims.

**Partnership endogeneity.** Media partners may choose prediction markets because they already prefer data-oriented language. Mitigation: use associational language and avoid causal claims.

**Temporal mismatch.** Current market data may not represent quality at publication. Mitigation: require timestamp-aligned historical snapshots for confirmatory quality analysis; otherwise classify the observation as unmatched.

**Platform comparability.** Kalshi and Polymarket differ in contract structure, access, fees, and data. Mitigation: platform-specific standardization and within-platform analyses.

**LLM measurement error.** Model labels may reproduce prompt assumptions. Mitigation: fixed codebook, versioned prompts, human validation, model/rule robustness, error taxonomy.

**Construct contamination.** “Probability” may be used mechanically rather than rhetorically. Mitigation: sentence-level coding and explicit inclusion/exclusion rules.

**Post-treatment controls.** Some controls could be influenced by source choice or editorial framing. Mitigation: maintain minimal and expanded specifications and interpret controls descriptively.

## 10. Falsifiability and decision rules

The research thesis will be weakened if:

- partner-media texts are not more authority-oriented than independent media;
- high authority claims consistently occur in higher-quality markets;
- high claims commonly include clear limitations and market-quality metrics;
- overreach classifications disappear under reasonable alternative definitions.

The paper will report these outcomes rather than redefining overreach to preserve a preferred conclusion.

## 11. Deliverables

- versioned corpus and source inventory;
- reproducible collection and preprocessing code;
- codebook and validated annotation sample;
- framing-analysis tables and figures;
- market-quality feature table;
- overreach case audit;
- full academic paper and reproducibility appendix.

## 12. Stage-1 freeze

Frozen for Stage 2:
- observational, noncausal design;
- four source strata;
- sentence, document, market-mention, and market-snapshot units;
- claim-breadth hierarchy;
- component-based market-quality analysis;
- transparent three-condition overreach classification;
- Kalshi primary and Polymarket comparative scope.

May change only after a documented data-availability audit:
- exact date cutoff;
- final media-source list;
- snapshot windows;
- minimum sample size for multilevel models;
- exact quality thresholds.
