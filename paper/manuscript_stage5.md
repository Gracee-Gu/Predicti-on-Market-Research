# Prediction Markets as Manufactured Public Signals: Media Framing, Market Quality, and Representational Overreach

## Abstract

Prediction markets are increasingly presented as public signals about elections, policy, and social outcomes. This study examines when media descriptions of market probabilities exceed what market participation and quality can substantiate. We combine a structured media corpus, article–market matching, coded framing constructs, and publication-aligned market evidence. The current empirical status is inserted automatically from the Stage 4 audit. Results are reported at the strongest level allowed by the claim gates. The study contributes a framework for distinguishing numerical market signals from claims about public opinion, collective belief, or democratic representation.

**Empirical status:** `exploratory_only`.

## Introduction

Prediction-market probabilities are numerical outputs of trading systems, but they increasingly circulate as statements about what “the public,” “voters,” or “people” believe. This paper investigates the representational work required to turn a market price into a public signal and the conditions under which media framing exceeds what participation and market quality can support.

## Theory and Hypotheses

The project distinguishes a market probability from a claim about collective representation. Framing becomes representationally consequential when it suppresses information about who may trade, how liquid the market is, how prices are formed, and whether the observed market can plausibly stand in for a broader public. The hypotheses and construct definitions remain those established in Stage 1 and operationalized in Stage 3.

## Data and Methods

The study uses a governed corpus of prediction-market media mentions linked to market records. Corpus construction, platform and source-type classification, article–market matching, coding rules, reliability procedures, and publication-aligned market-quality joins are documented in the Stage 2–4 protocols. Historical price evidence is distinguished from prospective order-book evidence, and current snapshots are not treated as historical market quality.

## Results

**Interpretation boundary:** The corpus did not pass all confirmatory gates. All empirical statements below are restricted to exploratory within-corpus associations.

# Stage 4 Analysis Report

**Claim status:** `exploratory_only`

## Corpus diagnostics

- N: 116
- Source types: {'platform_owned': 116}
- Market-quality coverage: 0.0
- Human adjudication evidence: False

## Bivariate associations

- probability_as_public_opinion: mean difference 0.827333545715196 (95% CI 0.6252676896058407, 1.0293994018245514)
- representativeness_caveat: mean difference  (95% CI , )
- market_quality_caveat: mean difference -0.08452380952380945 (95% CI -0.36013629021686855, 0.19108867116924966)
- certainty_language: mean difference 0.4709595959595958 (95% CI 0.2329082711633628, 0.7090109207558288)
- democratic_language: mean difference 1.5132743362831858 (95% CI 1.3780625379749232, 1.6484861345914483)
- horse_race_frame: mean difference 1.4432560903149139 (95% CI 1.0275603252172985, 1.8589518554125293)

## Multivariable models

Model registry output: `{'M1': {'status': 'completed', 'n': 116, 'coefficients': {'const': 0.20960160397932126, 'probability_as_public_opinion': 0.7153142464649207, 'representativeness_caveat': 7.635413586927512e-16, 'market_quality_caveat': -0.623563671334881, 'certainty_language': -0.033069852611080086, 'democratic_language': 0.5379573356265391, 'horse_race_frame': 1.5610356131694294}, 'standard_errors': {'const': 0.09426541638340903, 'probability_as_public_opinion': 0.08624966586734832, 'representativeness_caveat': 5.640697769685092e-16, 'market_quality_caveat': 0.07321542997590959, 'certainty_language': 0.06195983534947999, 'democratic_language': 0.39778923726376725, 'horse_race_frame': 0.11317405360293296}, 'pvalues': {'const': 0.026180352368139814, 'probability_as_public_opinion': 1.099356045621084e-16, 'representativeness_caveat': 0.17585468483559052, 'market_quality_caveat': 1.639741183225244e-17, 'certainty_language': 0.5935280185891113, 'democratic_language': 0.17625770101027527, 'horse_race_frame': 2.799444366984717e-43}, 'r_squared': 0.8270136270300448}, 'M2': {'status': 'completed', 'n': 116, 'coefficients': {'probability_as_public_opinion': 58.98901388311027, 'representativeness_caveat': 0.0, 'market_quality_caveat': -57.529706203075406, 'certainty_language': 17.03317065867918, 'democratic_language': 49.55435450206959, 'horse_race_frame': 62.38679330418438, '0/1': 2.8203731310096316, '1/2': 4.046003526960788, '2/3': 4.547411594783209}, 'standard_errors': {'probability_as_public_opinion': nan, 'representativeness_caveat': nan, 'market_quality_caveat': nan, 'certainty_language': nan, 'democratic_language': nan, 'horse_race_frame': nan, '0/1': nan, '1/2': nan, '2/3': nan}, 'pvalues': {'probability_as_public_opinion': nan, 'representativeness_caveat': nan, 'market_quality_caveat': nan, 'certainty_language': nan, 'democratic_language': nan, 'horse_race_frame': nan, '0/1': nan, '1/2': nan, '2/3': nan}}}`

## Interpretation boundary

Results may be described only at the claim level permitted by the input audit. Failed gates must be reported alongside estimates.


## Discussion

The central interpretation is not that prediction-market prices are meaningless. Rather, their public meaning is produced through a chain of market design, participant composition, liquidity, platform presentation, and journalistic framing. Any observed relationship between framing and representational overreach should therefore be read as evidence about the sampled communication environment, and does not establish public misunderstanding attributable to framing.

The strongest contribution of the study is conceptual and methodological: it makes the representational leap from traded probability to public judgment measurable and ties that leap to observable caveats and market-quality evidence.

## Limitations

The design is observational and cannot establish causal effects of framing. Generalizability depends on source-type diversity and corpus construction. Article–market matching may be uncertain; publication-aligned quality measures may be missing; platform-owned coverage may differ systematically from independent journalism; and coding provenance constrains the strongest available claims. Failed Stage 4 gates must remain visible in any publication.

## Conclusion

Prediction markets can function as manufactured public signals when market probabilities are circulated with representational meanings that the underlying market cannot independently warrant. The framework developed here separates numerical prediction, market quality, media framing, and claims about collective belief, providing an auditable basis for evaluating representational overreach.

## Reproducibility Statement

The repository contains collection protocols, matching rules, codebooks, analysis scripts, claim gates, tests, and generated audit artifacts. Raw copyrighted article text is excluded by default. Stage 5 records file hashes and a claim–evidence ledger so that manuscript statements can be traced to design records or empirical outputs.
