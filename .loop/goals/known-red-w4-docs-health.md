# Main-red docs and health rows pass again or are removed with evidence, so the v2.0 release gate's full suite has no FAIL outside the known list (TOP-DECISION 52-54, o195 no waivers, o212)

- Slug: known-red-w4-docs-health
- Touches: not declared
- ETA: 225 active minutes (estimate 177m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: no-usage-passes docs-guide-page-issue-125 prd-readers stale-groups-defect stale-code-page-reviewed entry-stale health-file-no-milestone health-findings-table hlt6-cannot-fire no-milestone-issue-ok runbook-registry
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

1. Open the pull request's regression run (the full-suite shards) and look up each of the eleven rows named in done line 1.
   Expect: each shows PASS, none shows FAIL.
2. Open .loop/regression-known.tsv and compare the row count of .loop/regression.tsv with main.
   Expect: regression-known.tsv gained no row, and regression.tsv has no more rows than main.
