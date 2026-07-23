# Stage 6 Submission Protocol

## Purpose

Stage 6 freezes a reviewable research state without overstating the evidence.

## Required package components

- clean manuscript;
- blinded manuscript;
- claim and evidence provenance;
- data and code availability statement;
- reproducibility capsule;
- defense brief;
- supervisor handoff memo;
- final automated audit.

## Claim discipline

The authoritative claim status is inherited from Stage 4/5. A manuscript may be structurally complete while remaining exploratory or blocked.

When the status is `exploratory_only`:

- results must be described as within-corpus associations;
- single-source concentration must be disclosed;
- missing market-quality evidence must be disclosed;
- AI coding/adjudication provenance must be disclosed;
- causal and population-generalizing language is prohibited.

## Blind review

The blinded copy replaces configured author and institutional identifiers. Automated anonymization is a precheck, not a substitute for human review. File metadata, acknowledgements, repository links, self-citations, and filenames must still be inspected manually.

## Reproducibility capsule

The capsule includes code, configuration, documentation, tests, nonrestricted data products, and audit outputs. It excludes:

- raw copyrighted article text;
- credentials and secret files;
- `.git`;
- virtual environments and caches;
- oversized files above the configured threshold.

## Freeze rule

A release is not final until the capsule manifest records SHA-256 hashes and the final audit reports no unresolved critical failures.
