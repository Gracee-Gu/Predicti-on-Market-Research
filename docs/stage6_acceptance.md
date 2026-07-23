# Stage 6 Acceptance Criteria

Stage 6 implementation passes when:

1. the Stage 5 manuscript is found;
2. the inherited claim status is resolved;
3. clean and blinded manuscripts are generated;
4. all required manuscript sections are present;
5. a data/code availability statement is generated;
6. a reproducibility capsule and hash manifest are generated;
7. a defense brief and supervisor handoff memo are generated;
8. no credential patterns are found in included release files;
9. non-confirmatory manuscripts contain no configured prohibited claims;
10. tests pass.

Possible final statuses:

- `ready_for_submission_precheck`: implementation complete and automated checks pass;
- `ready_for_supervisor_review`: package is coherent but human decisions or known evidence limitations remain;
- `not_ready`: required artifacts are missing or critical checks fail.

For an `exploratory_only` study, the expected successful outcome is normally `ready_for_supervisor_review`, not an assertion that the paper is publication-ready.
