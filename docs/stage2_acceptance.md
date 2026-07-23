# Stage 2 Acceptance Report

## Delivered

- API collectors for Kalshi and Polymarket market metadata;
- support for Kalshi live and historical tiers;
- Polymarket token parsing and CLOB quality endpoints;
- seed-driven media collector;
- copyright-safe storage defaults;
- inventory builder;
- source-type rules;
- data dictionary;
- corpus inclusion/exclusion protocol;
- fixtures and unit tests;
- runbook.

## Automated checks

The package must pass:

```bash
pytest -q
ruff check .
```

## Acceptance criteria

| Criterion | Result |
|---|---|
| Stage 1 constructs preserved | Pass |
| Public API paths grounded in official documentation | Pass |
| Historical/live Kalshi split handled | Pass |
| Polymarket market metadata and CLOB endpoints separated | Pass |
| Raw full text excluded from Git by default | Pass |
| Inventory schema defined | Pass |
| Timestamp-alignment status explicit | Pass |
| Historical order-book limitation acknowledged | Pass |
| Full real-data collection executed in this environment | Not run: network unavailable in artifact runtime |
| Minimum matched corpus size established | Pending actual collection |

## Stage verdict

**PASS FOR IMPLEMENTATION; CONDITIONAL PASS FOR EMPIRICAL COVERAGE.**

The code and protocol are ready to upload and run locally. Stage 3 should not begin until the real collection produces:

- at least 30 audited documents per main source stratum where feasible;
- at least 100 unambiguous market mentions overall;
- at least 50 publication-time price/activity matches;
- a documented prospective snapshot plan if spread/depth is central.

These are design targets, not grounds for hiding lower coverage. If coverage is lower, the paper must narrow its inferential scope.
