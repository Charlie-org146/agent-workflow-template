# Test levels G3 (LVL-1.2; owner o980, o985; split TD1749): L2 full runs every row and a skipped row is red

- Slug: v110-lvl-l2
- Touches: skills/workflow-regression, .github/workflows, dev/toy, .loop/regression.tsv, skills/loop-files.md, .loop/regression-relevel.tsv
- ETA: 385 active minutes (estimate 306m plus a 25% margin)

## Done lines

Frozen. A wrong done line needs a new goal.

1. Given a row that no change has reached for 30 days, when L2 runs, then the row runs and its result is recorded.
2. Given a shard that runs out of job time with rows left, when L2 ends, then the run is red and one issue names each skipped row.
3. Given a row that fails at L2, when the run ends, then one issue is open for it, the main-red goal names it, and main has no revert commit.
4. Given the package, when the goal's checks run, then every script stays under 20,480 bytes, no test is loosened, no row turns red, and committed text never names the service repo.

## Verify by hand

<!-- Numbered steps for a person, each with an Expect: line. A release needs this. -->
