# Main-red size and caps rows pass again or are removed with evidence, so the v2.0 release gate's full suite has no FAIL outside the known list (TOP-DECISION 52-54, o195 no waivers, o212)

- Slug: known-red-w8-size
- Touches: not declared
- ETA: 225 active minutes (estimate 177m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Each of these rows passes on the PR head in the CI full-suite shards, or is removed from .loop/regression.tsv with evidence in the PR that the behaviour it tests no longer exists: size-141 skill-kept skill-size-116 skill-lines-release-4172 scripts-c-health-under-19000 scripts-c-regression-under-19000 docs-release-scripts-under-19000 trim-monitoring-4-size trim-setup-under-19000
2. No row is added to .loop/regression-known.tsv, and net regression rows are 0 or fewer against main

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
