# The regression workflow's full nightly-level run finishes every row inside its job budget (UNRUN 0), through more shards (12-16) and/or a longer job timeout, so the release gate's --suite-from can accept a main CI run (TOP-DECISION 58)

- Slug: ci-shards-unrun0
- Touches: .github/workflows/regression.yml, .github/workflows/regression-pr.yml, skills/workflow-regression/scripts/regression.py, skills/workflow-regression/scripts/actions.py, dev/toy/test-regression.sh, docs/wiki/Regression.md
- ETA: 225 active minutes (estimate 177m plus a 25% margin, rough)

## Done lines

Frozen. A wrong done line needs a new goal.

1. A full nightly-level run of .github/workflows/regression.yml on the PR head finishes with UNRUN 0, through more shards (12-16) and/or a longer job timeout
2. A negative control proves a deliberately slow shard still reports UNRUN greater than 0 and review.py gate --suite-from still refuses that run
3. Net regression rows are 0 against main, and the goal touches only .github/workflows/regression.yml and the shard split

## Verify by hand

1. Open the run summary of `gh workflow run regression.yml --ref loop/ci-shards-unrun0`.
   Expect: its last line reads `SHARDS 16 of 16 reported. UNRUN 0`.
2. Run `python3 dev/toy/test-gate-ci-suite.py`.
   Expect: `passed all`, including the runs with UNRUN 3 and 7 of 8 shards refused.
