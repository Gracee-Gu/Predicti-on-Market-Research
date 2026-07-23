# Corpus Construction Protocol

## Target period

January 1, 2025 through the frozen collection cutoff.

## Source strata

1. platform-owned;
2. documented partner media;
3. independent media;
4. regulatory/critical institutional sources.

The design targets balance across strata and market categories rather than claiming a census of all coverage.

## Discovery log

For every search session record:

- query;
- search engine or database;
- execution date;
- date filters;
- source domain filter;
- result pages reviewed;
- inclusion/exclusion decision.

Search-result rankings are unstable; the log is part of the evidence.

## Inclusion

- directly mentions a prediction-market platform, contract, price, odds, or displayed probability;
- public-facing English-language text;
- publication time can be established to at least a calendar day;
- source identity can be established;
- within the research period.

## Exclusion

- duplicated syndication, retaining the earliest or canonical version;
- pure market listings without public-facing narrative, except platform-owned framing pages;
- inaccessible source with no auditable metadata;
- social post with no stable archive, unless sampled in a separately defined sub-study;
- article that mentions generic betting without a prediction-market signal.

## Copyright-safe storage

Commit:

- URLs;
- titles and publication metadata;
- source classifications;
- hashes;
- short excerpts;
- derived labels and features.

Do not commit:

- full copyrighted article text;
- paywalled HTML;
- credentials;
- private API responses.

## Deduplication

Primary key: canonicalized URL.
Secondary checks:

- title similarity;
- text hash;
- same wire copy across domains.

Syndicated copies remain in an audit table but only one canonical text enters framing prevalence estimates unless outlet-level dissemination is itself analyzed.
