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
