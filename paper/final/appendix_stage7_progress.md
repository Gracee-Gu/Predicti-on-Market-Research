# Appendix for Stage 7 Progress Paper

## Alignment Audit Snapshot

Status: `empirical_recovery_required`

## Gate Table

| Gate | Observed | Threshold | Pass |
|---|---:|---:|---|
| total_documents | 164 | 80 | PASS |
| source_type_diversity | 4 | 3 | PASS |
| required_source_counts | {"platform_owned": 49, "independent_media": 47} | 15 | PASS |
| human_audited_units | 139 | 50 | PASS |
| reliability_fields_reported | 16 | 3 | PASS |
| publication_timestamp_coverage | 1.0 | 0.8 | PASS |
| market_match_traceability | 1.0 | 0.9 | PASS |
| market_quality_coverage | 0.02586206896551724 | 0.5 | FAIL |
| case_level_rows | 116 | 10 | PASS |

## Notes

- Corpus-layer source diversity is now adequate for a future comparative design.
- The audited analytic layer remains too narrow for the original final claim.
- Publication-aligned market-quality evidence remains sparse in the audited repository state.
- Event-window analysis remains optional and is deferred until the two core empirical components pass.

