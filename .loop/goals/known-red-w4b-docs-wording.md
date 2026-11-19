# Two main-red docs-wording rows pass again or are removed with evidence, so the v2.0 gate's full suite has no FAIL outside the known list (TOP-DECISION 57, o195 no waivers, o213)

- Slug: known-red-w4b-docs-wording
- Touches: dev/toy/test-milestone-wording.sh, .loop/regression.tsv, docs/wiki/Documentation.md, docs/wiki/Tests.md
- ETA: 220 active minutes (estimate 176m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: doc1-sync-pointer milestone-wording-unreviewed
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
