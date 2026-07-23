# Constructs, Hypotheses, and Operationalization

## Construct table

| Construct | Conceptual definition | Unit | Primary measure | Key exclusions | Validity risk |
|---|---|---|---|---|---|
| Epistemic authority | Representation of a market or price as knowledge-producing, objective, accurate, predictive, or intelligence-bearing | Sentence; aggregated to mention/document | Human-validated multilabel classifier; proportion of sentences labeled | Mechanical payout/price descriptions | “Probability” may be technical rather than rhetorical |
| Public representation | Extension of a market signal to a public, electorate, population, consensus, or collective belief | Sentence/mention | Binary label plus ordinal claim breadth | Explicitly trader-limited claims | “Market consensus” may be ambiguous |
| Financial-market framing | Alignment with exchange, contract, trading, liquidity, hedging, investing, or price discovery | Sentence/document | Frame proportion | Generic use of “market” meaning topic/domain | Polysemy |
| Gambling/risk framing | Alignment with betting, wagering, casino activity, addiction, loss, or gambling harms | Sentence/document | Frame proportion | Metaphorical “bet” unrelated to transaction | Editorial genre confounding |
| Uncertainty/quality disclosure | Explicit qualification relevant to interpreting signal quality or representativeness | Mention | Any-disclosure indicator; class count | Generic disclaimer with no interpretive content | Legal boilerplate may inflate counts |
| Participation/conversion framing | Prompt or affordance encouraging viewing, signup, following, trading, or taking a position | Sentence/document | Frame proportion; call-to-action flag | Neutral navigation | Platform pages structurally differ from news |
| Claim breadth | Degree to which a market price is generalized from transaction to trader belief, objective probability, or public belief | Mention | Ordinal 0–3 | None; hierarchy is exhaustive for matched mentions | Borderline probability language |
| Market quality | Current capacity of a contract market to support trading and informative price formation | Market snapshot | Vector of spread, depth, activity, staleness, volatility, time | Cumulative volume alone | Cross-platform comparability |
| Disclosure adequacy | Visibility of information needed to interpret the signal responsibly | Mention | Any disclosure, count, quality metric disclosed | Legal sufficiency is not claimed | Normative threshold |
| Representational overreach | Configuration where broad authoritative claims exceed visible evidentiary support | Mention | Transparent conjunction plus continuous robustness score | Not synonymous with inaccuracy or deception | Threshold sensitivity |

## Claim-breadth coding

| Level | Name | Example form | Added assumption |
|---|---|---|---|
| 0 | Transaction report | “The contract traded at 63 cents.” | None beyond accurate reporting |
| 1 | Trader belief | “Traders assign a 63% chance.” | Price summarizes participating traders |
| 2 | Objective probability | “There is a 63% chance.” | Price maps to event probability |
| 3 | Public representation | “The public thinks the chance is 63%.” | Traders represent a broader population |

## Hypothesis-to-variable map

### H1: Authority framing

- Outcome: `epistemic_authority_share`
- Main predictors: `partner_media`, `platform_owned`, `regulatory_critical`
- Reference: `independent_media`
- Controls: month, platform, category, genre, text length
- Expected signs: partner > 0; platform-owned > 0; regulatory/critical < 0
- Inference level: association, not causal partnership effect

### H2: Public representation

- Outcome: `public_representation_any` or maximum `claim_breadth == 3`
- Model: logistic or permutation comparison
- Expected signs: partner and platform-owned positive

### H3: Risk asymmetry

- Outcomes: `uncertainty_disclosure_share`, `gambling_risk_share`
- Expected: partner/platform-owned lower than regulatory/critical
- Important control: article genre
- Robustness: compare news/explainer genres separately

### H4: Disclosure gap

- Sample: mentions with claim breadth >= 2
- Outcome: `disclosure_any`
- Expected: lower in partner/platform-owned than independent/regulatory
- Secondary: `quality_metric_disclosed`

### H5: Weak quality alignment

- Outcomes: component quality metrics and quality index
- Predictors: authority score and claim breadth
- Expected: small, unstable, or null positive association
- Interpretation: failure to reject a strong positive alignment is not proof of overreach; overreach is established at case/configuration level

### H6: Overreach concentration

- Outcome: `high_overreach_case`
- Predictor: source type
- Test: permutation/Fisher exact plus adjusted logistic if sample permits
- Expected: higher prevalence in partner/platform-owned texts

## Prespecified controls and prohibited controls

### Allowed controls

- publication month;
- article genre;
- platform;
- market category;
- standardized text length;
- days to resolution;
- contract age.

### Avoid or separate as robustness controls

- article engagement;
- article placement;
- trading volume after publication;
- post-publication volatility.

These may be consequences of publication or framing and should not be included as ordinary pre-treatment controls.

## Minimum reporting requirements

Every hypothesis result must include:

- sample size and number of clusters;
- effect estimate in interpretable units;
- uncertainty interval;
- unadjusted and adjusted specification;
- source and category composition;
- annotation reliability;
- missing-data pattern;
- sensitivity to alternative frame classifier;
- sensitivity to alternative market-quality measure where applicable.

## No-go interpretation rules

The final paper must not state:

- that a market price is “wrong” solely because liquidity is low;
- that a media organization caused trust without audience data;
- that partnership caused framing from cross-sectional comparison;
- that prediction markets measure public sentiment;
- that a lack of disclosure proves intentional deception;
- that a high overreach score proves legal or ethical wrongdoing.

Permitted language:

- “is associated with”;
- “is represented as”;
- “provides an authority cue”;
- “omits information relevant to interpretation”;
- “is classified as high overreach under the prespecified rule”;
- “is inconsistent with a simple quality-alignment account.”
