# The regression workflow's full nightly-level run finishes every row inside its job budget (UNRUN 0), through more shards (12-16) and/or a longer job timeout, so the release gate's --suite-from can accept a main CI run (TOP-DECISION 58)

- Slug: ci-shards-unrun0
- Touches: not declared
- ETA: 225 active minutes (estimate 177m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A full nightly-level run of .github/workflows/regression.yml on the PR head finishes with UNRUN 0, through more shards (12-16) and/or a longer job timeout
2. A negative control proves a deliberately slow shard still reports UNRUN greater than 0 and review.py gate --suite-from still refuses that run
3. Net regression rows are 0 against main, and the goal touches only .github/workflows/regression.yml and the shard split

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
